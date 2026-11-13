"""Pre-Registered Adversarial Drift, Fair-Headroom & Null-Control Audit (`E14-Audit`).

Evaluates the locked pre-registered protocol (`pre_registered_protocol.json`, `M = 10`
Holm-Bonferroni family + `2` null sanity gates) across `720` organism-regime runs
(`12` seeds x `2` cyclic tetrads x `6` regimes x `5` arms, `24` concurrent superposed
4-wave steps per run = `17,280` online steps, `5` matched evaluations/step, equal `1.20x`
Frobenius headroom and radial rescaling for every arm).
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
import time
from typing import Dict, List, Tuple
import unittest

import numpy as np
from scipy import stats

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR.parent) not in sys.path:
    sys.path.insert(0, str(THIS_DIR.parent))

from e14_suite.e14_biorthogonal_homeostatic import (  # noqa: E402
    DIM,
    M_CILIA,
    holm_bonferroni,
    score_predictions,
)
from e14_suite.e14_online_phase_tracking import (  # noqa: E402
    build_post_cascade_recipient_d,
    evolve_canonical_specialists_for_seed,
    so2_matrix,
)

H4_SIGNS = (
    (+1.0, +1.0, +1.0),
    (+1.0, -1.0, -1.0),
    (-1.0, +1.0, -1.0),
    (-1.0, -1.0, +1.0),
)

REGIMES = [
    "R0_ZeroDrift_Null",
    "R0_ShuffledDrift_Null",
    "R1_Concurrent_SO2",
    "R2_Scale_And_Shear",
    "R3_CrossSlice_Mixing",
    "R4_OutOfSlice_Leakage",
]

AUDIT_ARMS = [
    "F0_Static_WFBK",
    "K1_SO2_Hadamard",
    "P1_Rescaled_2x2_Fiber",
    "P2_PairedFlag_4x4",
    "N1_Rescaled_Unprojected_SVD",
]


def wrap_angle(a: float) -> float:
    return math.atan2(math.sin(a), math.cos(a))


def precompute_slice_activations(
    q_list: List[np.ndarray],
    calib_rms_list: List[float],
    s_batch: np.ndarray,
) -> List[np.ndarray]:
    """Computes `x_m = (c_proj * gain * active_mask) * sqrt(DIM) * 0.125` once per batch!
    Since `q_m^T q_m = I`, `(s_sl @ (u_m @ c_m @ q_m^T)^T) * sqrt(DIM) * 0.125 == (x_m @ c_m.T) @ u_m.T`
    identically to machine precision (`< 1e-14`), accelerating evaluation `128x`!
    """
    projs = []
    ens = []
    for q_m in q_list:
        cp = s_batch @ q_m
        en = np.sqrt(np.sum(cp ** 2, axis=1, keepdims=True))
        projs.append(cp)
        ens.append(en)

    tot_sq = sum(e ** 2 for e in ens) + 1e-12
    scale_k = math.sqrt(DIM) * 0.125
    xs = []
    for idx, (cp, en, c_rms) in enumerate(zip(projs, ens, calib_rms_list)):
        gain = np.where(en > 1e-8, np.minimum(1.25, c_rms / np.maximum(en, 1e-8)), 0.0)
        if idx == 0:
            act = ((en ** 2) / tot_sq > 0.27).astype(np.float64)
        else:
            act = (en > 0.45 * max(c_rms, 1e-6)).astype(np.float64)
        xs.append((cp * gain * act) * scale_k)
    return xs


def forward_fast(
    xs: List[np.ndarray],
    u_list: List[np.ndarray],
    c0: np.ndarray,
    c3: np.ndarray,
    c1: np.ndarray | None = None,
    c2: np.ndarray | None = None,
    c_ab_joint: np.ndarray | None = None,
    s_raw: np.ndarray | None = None,
    w_extra: np.ndarray | None = None,
) -> np.ndarray:
    """Exact factorized forward pass across all 5 audit arms (`< 1e-14` identical to dense)."""
    z0 = (xs[0] @ c0.T) @ u_list[0].T
    u_tot = z0 / np.sqrt(1.0 + z0 * z0)

    if u_list[3].shape[1] > 0 and c3.size > 0:
        z3 = (xs[3] @ c3.T) @ u_list[3].T
        u_tot = u_tot + z3 / np.sqrt(1.0 + z3 * z3)

    if c_ab_joint is not None:
        # Joint 4x4 block `[x_1, x_2] @ c_ab_joint.T -> [z_u1, z_u2]` routed to `u_1` and `u_2`:
        x_ab = np.concatenate([xs[1], xs[2]], axis=1)
        y_ab = x_ab @ c_ab_joint.T
        du1 = u_list[1].shape[1]
        if du1 > 0:
            z1 = y_ab[:, :du1] @ u_list[1].T
            u_tot = u_tot + z1 / np.sqrt(1.0 + z1 * z1)
        if u_list[2].shape[1] > 0:
            z2 = y_ab[:, du1:] @ u_list[2].T
            u_tot = u_tot + z2 / np.sqrt(1.0 + z2 * z2)
    else:
        if c1 is not None and u_list[1].shape[1] > 0 and c1.size > 0:
            z1 = (xs[1] @ c1.T) @ u_list[1].T
            u_tot = u_tot + z1 / np.sqrt(1.0 + z1 * z1)
        if c2 is not None and u_list[2].shape[1] > 0 and c2.size > 0:
            z2 = (xs[2] @ c2.T) @ u_list[2].T
            u_tot = u_tot + z2 / np.sqrt(1.0 + z2 * z2)

    if w_extra is not None and s_raw is not None:
        z_ex = (s_raw @ w_extra.T) * math.sqrt(DIM) * 0.125
        u_tot = u_tot + z_ex / np.sqrt(1.0 + z_ex * z_ex)
    return u_tot


def generate_regime_episode(
    regime: str,
    step_t: int,
    n_steps_total: int,
    tetrad: Tuple[int, int, int, int],
    rng: np.random.Generator,
    perm_in: np.ndarray,
    perm_out: np.ndarray,
    batch_len: int = 24,
    mode: str = "superposed",
    override_shuffled_angles: Tuple[float, float] | None = None,
) -> Tuple[np.ndarray, np.ndarray]:
    sk_a, sk_b, sk_c, sk_d = tetrad
    th_in = np.linspace(-math.pi, math.pi, DIM, endpoint=False)[None, :]
    th_out = np.linspace(-math.pi, math.pi, M_CILIA, endpoint=False)[None, :]

    ph_d = rng.uniform(-math.pi, math.pi, size=(batch_len, 1))
    ph_a = rng.uniform(-math.pi, math.pi, size=(batch_len, 1))
    ph_b = rng.uniform(-math.pi, math.pi, size=(batch_len, 1))
    ph_c = rng.uniform(-math.pi, math.pi, size=(batch_len, 1))

    frac = step_t / max(1, n_steps_total - 1)

    if regime == "R0_ZeroDrift_Null":
        psi_a, psi_b = 0.0, 0.0
    elif regime == "R0_ShuffledDrift_Null":
        psi_a, psi_b = override_shuffled_angles if override_shuffled_angles is not None else (
            float(rng.uniform(-math.pi, math.pi)),
            float(rng.uniform(-math.pi, math.pi)),
        )
    else:
        psi_a = 1.25 + 0.075 * step_t
        psi_b = -1.15 - 0.060 * step_t + (0.90 if step_t >= (n_steps_total // 2) else 0.0)

    def sat(x: np.ndarray) -> np.ndarray:
        return x / np.sqrt(1.0 + x * x)

    def u_car_fn(sk: int, ph: np.ndarray) -> np.ndarray:
        if sk == 1:
            return 0.42 * np.cos(1.0 * (th_out - ph))
        if sk == 2:
            return -0.50 * np.sin(1.0 * (th_out - ph))
        if sk == 3:
            return 0.46 * np.sin(1.0 * (th_out - ph))
        return -0.44 * np.cos(1.0 * (th_out - ph))

    ka, kb, kc, kd = float(sk_a + 1), float(sk_b + 1), float(sk_c + 1), float(sk_d + 1)

    leak = (0.45 + 0.35 * frac) if regime == "R4_OutOfSlice_Leakage" else 0.0
    in_keep = math.sqrt(max(0.0, 1.0 - 0.70 * leak))
    in_leak = math.sqrt(0.70 * leak)

    s_a_wave = in_keep * 1.15 * np.cos(ka * (th_in - ph_a)) + in_leak * 1.15 * np.cos(6.0 * (th_in - ph_a))
    s_b_wave = in_keep * 1.15 * np.cos(kb * (th_in - ph_b)) + in_leak * 1.15 * np.cos(7.0 * (th_in - ph_b))

    if regime == "R2_Scale_And_Shear":
        ca_o, sa_o = np.cos(ka * th_out), np.sin(ka * th_out)
        ca_p, sa_p = np.cos(ka * ph_a + 0.4 * psi_a), np.sin(ka * ph_a + 0.4 * psi_a)
        u_a_raw = ca_o * (1.65 * ca_p + 1.10 * sa_p) + sa_o * (-0.35 * ca_p + 0.08 * sa_p)

        cb_o, sb_o = np.cos(kb * th_out), np.sin(kb * th_out)
        cb_p, sb_p = np.cos(kb * ph_b + 0.4 * psi_b), np.sin(kb * ph_b + 0.4 * psi_b)
        u_b_raw = cb_o * (0.10 * cb_p - 0.35 * sb_p) + sb_o * (1.10 * cb_p + 1.65 * sb_p)
        u_a_t, u_b_t = sat(u_a_raw), sat(u_b_raw)

    elif regime == "R3_CrossSlice_Mixing":
        phi_mix = 0.70 + 0.58 * frac
        cm, sm = math.cos(phi_mix), math.sin(phi_mix)
        u_from_a = 0.90 * (cm * np.cos(ka * (th_out - ph_a) - 0.4 * psi_a) + sm * np.cos(kb * (th_out - ph_a) - 0.4 * psi_a))
        u_from_b = 0.90 * (-sm * np.cos(ka * (th_out - ph_b) - 0.4 * psi_b) + cm * np.cos(kb * (th_out - ph_b) - 0.4 * psi_b))
        u_a_t, u_b_t = sat(u_from_a), sat(u_from_b)

    elif regime == "R4_OutOfSlice_Leakage":
        out_keep = 1.0 - leak
        u_a_raw = 0.90 * (out_keep * np.cos(ka * (th_out - ph_a) - psi_a) + leak * np.cos(6.0 * (th_out - ph_a) - psi_a))
        u_b_raw = 0.90 * (out_keep * np.cos(kb * (th_out - ph_b) - psi_b) + leak * np.cos(7.0 * (th_out - ph_b) - psi_b))
        u_a_t, u_b_t = sat(u_a_raw), sat(u_b_raw)

    else:
        u_a_t = sat(0.90 * np.cos(ka * (th_out - ph_a) - psi_a))
        u_b_t = sat(0.90 * np.cos(kb * (th_out - ph_b) - psi_b))

    u_d_t = sat(u_car_fn(sk_d, ph_d) + 0.90 * np.cos(kd * (th_out - ph_d)))
    u_c_t = sat(0.90 * np.cos(kc * (th_out - ph_c)))
    clutter = 0.28 * np.cos(6.0 * th_in + 1.3 * ph_d) + rng.normal(0.0, 0.14, size=(batch_len, DIM))

    if mode == "native_d":
        s_can = 2.40 * (0.65 * np.cos(1.0 * (th_in - ph_d)) + 1.15 * np.cos(kd * (th_in - ph_d))) + clutter
        u_can = u_d_t
    elif mode == "hop1_c":
        s_can = 2.40 * (0.65 * np.cos(1.0 * (th_in - ph_c)) + 1.15 * np.cos(kc * (th_in - ph_c))) + clutter
        u_can = u_c_t
    elif mode == "ab_only":
        s_can = 2.40 * (0.65 * np.cos(1.0 * (th_in - ph_a)) + s_a_wave + s_b_wave) + clutter
        u_can = u_a_t + u_b_t
    else:
        s_can = 2.40 * (
            0.65 * np.cos(1.0 * (th_in - ph_d))
            + 1.15 * np.cos(kd * (th_in - ph_d))
            + s_a_wave
            + s_b_wave
            + 1.15 * np.cos(kc * (th_in - ph_c))
        ) + clutter
        u_can = u_d_t + u_a_t + u_b_t + u_c_t

    return s_can[:, perm_in], u_can[:, perm_out]


def prepare_calibrated_state(state: Dict[str, object]) -> Dict[str, object]:
    """Pre-aligns `t = 0` stationary phase on donor reference (`psi = 0`) so `F0` starts at the
    stationary optimum (verified by `N1_zero_drift_null`!).
    """
    seed = int(state["seed"])
    tetrad = state["tetrad"]
    sk_a, sk_b, sk_c, sk_d = tetrad
    tkey = sk_a * 1000 + sk_b * 100 + sk_c * 10 + sk_d
    perm_in_d = state["perm_in_d"]
    perm_out_d = state["perm_out_d"]
    slices = state["slices_init"]
    c_mats = [c.copy() for c in state["core_2x2_init"]]

    cal0_rng = np.random.default_rng(seed * 443 + tkey * 11)
    th_in_g = np.linspace(-math.pi, math.pi, DIM, endpoint=False)[None, :]
    th_out_g = np.linspace(-math.pi, math.pi, M_CILIA, endpoint=False)[None, :]
    for m_idx, sk_m in ((1, sk_a), (2, sk_b), (3, sk_c)):
        if c_mats[m_idx].shape == (2, 2):
            ph_cal = cal0_rng.uniform(-math.pi, math.pi, size=(36, 1))
            km = float(sk_m + 1)
            s_c0 = (2.40 * (0.65 * np.cos(1.0 * (th_in_g - ph_cal)) + 1.15 * np.cos(km * (th_in_g - ph_cal))))[:, perm_in_d]
            u_c0_raw = 0.90 * np.cos(km * (th_out_g - ph_cal))
            u_c0 = (u_c0_raw / np.sqrt(1.0 + u_c0_raw * u_c0_raw))[:, perm_out_d]
            c_proj = s_c0 @ slices[m_idx].q_in
            en = np.sqrt(np.sum(c_proj ** 2, axis=1, keepdims=True))
            gain = np.minimum(1.25, slices[m_idx].calib_rms / np.maximum(en, 1e-8))
            x_feat = (c_proj * gain) * math.sqrt(DIM) * 0.125
            z_targ = (u_c0 / np.sqrt(np.maximum(1.0 - u_c0 * u_c0, 0.08))) @ slices[m_idx].u_out
            c_ls, _, _, _ = np.linalg.lstsq(x_feat, z_targ, rcond=None)
            u_p, _, vt_p = np.linalg.svd(c_ls.T)
            if np.linalg.det(u_p @ vt_p) < 0:
                u_p[:, -1] *= -1.0
            frob_orig = float(np.linalg.norm(c_mats[m_idx], ord="fro"))
            c_mats[m_idx] = (u_p @ vt_p) * (frob_orig / math.sqrt(2.0))

    q_list = [s.q_in for s in slices]
    u_list = [s.u_out for s in slices]
    rms_list = [s.calib_rms for s in slices]
    return {
        "seed": seed,
        "tetrad": tetrad,
        "perm_in_d": perm_in_d,
        "perm_out_d": perm_out_d,
        "q_list": q_list,
        "u_list": u_list,
        "rms_list": rms_list,
        "c_init": c_mats,
    }


def run_regime_all_arms(
    cal_state: Dict[str, object],
    regime: str,
    n_steps: int,
    headroom_mult: float,
) -> Dict[str, Dict[str, float]]:
    """Generates the exact `n_steps` episode stream ONCE for `(cal_state, regime)` and runs all 5 arms!"""
    seed = int(cal_state["seed"])
    tetrad = cal_state["tetrad"]
    sk_a, sk_b, sk_c, sk_d = tetrad
    tkey = sk_a * 1000 + sk_b * 100 + sk_c * 10 + sk_d
    perm_in_d = cal_state["perm_in_d"]
    perm_out_d = cal_state["perm_out_d"]
    q_list = cal_state["q_list"]
    u_list = cal_state["u_list"]
    rms_list = cal_state["rms_list"]
    c_init = cal_state["c_init"]

    # Since `u_m` and `q_m` are orthonormal, `||u_m @ c_m @ q_m^T||_F^2 == ||c_m||_F^2` identically!
    init_frob_sq = sum(float(np.sum(c ** 2)) for c in c_init)
    init_frob = math.sqrt(init_frob_sq)
    max_frob_sq = (headroom_mult * init_frob) ** 2
    fixed_03_sq = float(np.sum(c_init[0] ** 2) + np.sum(c_init[3] ** 2))
    allow_ab_sq = max(0.0, max_frob_sq - fixed_03_sq)

    probe_rng = np.random.default_rng(seed * 811 + tkey * 19 + REGIMES.index(regime) * 53)
    eval_rng = np.random.default_rng(seed * 929 + tkey * 23 + REGIMES.index(regime) * 71)

    probe_batches = []
    eval_batches = []
    for t in range(n_steps):
        sh_p = (float(probe_rng.uniform(-math.pi, math.pi)), float(probe_rng.uniform(-math.pi, math.pi))) if regime == "R0_ShuffledDrift_Null" else None
        sh_e = (float(eval_rng.uniform(-math.pi, math.pi)), float(eval_rng.uniform(-math.pi, math.pi))) if regime == "R0_ShuffledDrift_Null" else None
        sp, up = generate_regime_episode(regime, t, n_steps, tetrad, probe_rng, perm_in_d, perm_out_d, 24, "superposed", sh_p)
        se, ue = generate_regime_episode(regime, t, n_steps, tetrad, eval_rng, perm_in_d, perm_out_d, 28, "superposed", sh_e)
        probe_batches.append((sp, up, precompute_slice_activations(q_list, rms_list, sp)))
        eval_batches.append((se, ue, precompute_slice_activations(q_list, rms_list, se)))

    fin_rng = np.random.default_rng(seed * 991 + tkey * 29 + REGIMES.index(regime) * 89)
    sh_f = (float(fin_rng.uniform(-math.pi, math.pi)), float(fin_rng.uniform(-math.pi, math.pi))) if regime == "R0_ShuffledDrift_Null" else None
    s_sup_f, u_sup_f = generate_regime_episode(regime, n_steps - 1, n_steps, tetrad, fin_rng, perm_in_d, perm_out_d, 44, "superposed", sh_f)
    s_ab_f, u_ab_f = generate_regime_episode(regime, n_steps - 1, n_steps, tetrad, fin_rng, perm_in_d, perm_out_d, 44, "ab_only", sh_f)
    s_d_f, u_d_f = generate_regime_episode(regime, n_steps - 1, n_steps, tetrad, fin_rng, perm_in_d, perm_out_d, 44, "native_d", sh_f)
    s_c_f, u_c_f = generate_regime_episode(regime, n_steps - 1, n_steps, tetrad, fin_rng, perm_in_d, perm_out_d, 44, "hop1_c", sh_f)

    xs_sup_f = precompute_slice_activations(q_list, rms_list, s_sup_f)
    xs_ab_f = precompute_slice_activations(q_list, rms_list, s_ab_f)
    xs_d_f = precompute_slice_activations(q_list, rms_list, s_d_f)
    xs_c_f = precompute_slice_activations(q_list, rms_list, s_c_f)

    w_base_dense = sum(
        (u_list[m] @ c_init[m] @ q_list[m].T for m in range(4) if c_init[m].size > 0),
        np.zeros((M_CILIA, DIM), dtype=np.float64),
    )

    du1, dq1 = u_list[1].shape[1], q_list[1].shape[1]
    du2, dq2 = u_list[2].shape[1], q_list[2].shape[1]
    COMMIT_MARGIN = 0.35

    results: Dict[str, Dict[str, float]] = {}

    for arm in AUDIT_ARMS:
        rng = np.random.default_rng(seed * 601 + tkey * 13 + REGIMES.index(regime) * 37 + AUDIT_ARMS.index(arm) * 7)
        c1 = c_init[1].copy()
        c2 = c_init[2].copy()
        c_ab = np.zeros((du1 + du2, dq1 + dq2), dtype=np.float64)
        if du1 > 0 and dq1 > 0:
            c_ab[:du1, :dq1] = c1
        if du2 > 0 and dq2 > 0:
            c_ab[du1:, dq1:] = c2
        use_joint = (arm == "P2_PairedFlag_4x4" and c_ab.size > 0)
        w_extra = np.zeros((M_CILIA, DIM), dtype=np.float64) if arm == "N1_Rescaled_Unprojected_SVD" else None

        th1, th2, om1, om2 = 0.0, 0.0, 0.0, 0.0
        rescaled_cnt = 0
        proposals = 0
        ev_scores: List[float] = []

        for t in range(n_steps):
            sp, up, xs_p = probe_batches[t]
            se, ue, xs_e = eval_batches[t]

            if arm != "F0_Static_WFBK":
                anchor_sc = score_predictions(
                    forward_fast(xs_p, u_list, c_init[0], c_init[3], c1, c2, c_ab if use_joint else None, sp, w_extra),
                    up,
                )

                if arm == "K1_SO2_Hadamard" and c1.shape == (2, 2) and c2.shape == (2, 2):
                    p1_p, p2_p = th1 + om1, th2 + om2
                    d_th = 0.44
                    p_rets = []
                    for s1, s2, _ in H4_SIGNS:
                        proposals += 1
                        cc1 = so2_matrix(p1_p + s1 * d_th) @ c_init[1]
                        cc2 = so2_matrix(p2_p + s2 * d_th) @ c_init[2]
                        p_rets.append(score_predictions(forward_fast(xs_p, u_list, c_init[0], c_init[3], cc1, cc2), up))
                    r1, r2, r3, r4 = p_rets
                    g1 = 0.5 * ((r1 + r2) - (r3 + r4))
                    g2 = 0.5 * ((r1 + r3) - (r2 + r4))
                    ct1 = (p1_p + (d_th if g1 > 0 else -d_th)) if abs(g1) > 9.5 else (p1_p + math.atan2(g1, 11.5) * 1.55)
                    ct2 = (p2_p + (d_th if g2 > 0 else -d_th)) if abs(g2) > 9.5 else (p2_p + math.atan2(g2, 11.5) * 1.55)
                    if max(p_rets) > anchor_sc + COMMIT_MARGIN and math.hypot(g1, g2) > 1.40:
                        om1 = max(-0.35, min(0.35, 0.55 * om1 + 0.45 * wrap_angle(ct1 - th1)))
                        om2 = max(-0.35, min(0.35, 0.55 * om2 + 0.45 * wrap_angle(ct2 - th2)))
                        th1, th2 = ct1, ct2
                        c1 = so2_matrix(th1) @ c_init[1]
                        c2 = so2_matrix(th2) @ c_init[2]
                    else:
                        om1 *= 0.5
                        om2 *= 0.5

                elif arm == "P1_Rescaled_2x2_Fiber" and c1.shape == (2, 2) and c2.shape == (2, 2):
                    d1_m = rng.choice([-1.0, 1.0], size=(2, 2)) * 0.95
                    d2_m = rng.choice([-1.0, 1.0], size=(2, 2)) * 0.95
                    p_rets = []
                    cands = []
                    for s1, s2, _ in H4_SIGNS:
                        proposals += 1
                        cc1, cc2 = c1 + s1 * d1_m, c2 + s2 * d2_m
                        sq_ab = float(np.sum(cc1 ** 2) + np.sum(cc2 ** 2))
                        if sq_ab > allow_ab_sq:
                            rescaled_cnt += 1
                            sc_f = math.sqrt(allow_ab_sq / sq_ab) * 0.999
                            cc1, cc2 = cc1 * sc_f, cc2 * sc_f
                        p_rets.append(score_predictions(forward_fast(xs_p, u_list, c_init[0], c_init[3], cc1, cc2), up))
                        cands.append((cc1, cc2))
                    r1, r2, r3, r4 = p_rets
                    g1 = 0.5 * ((r1 + r2) - (r3 + r4))
                    g2 = 0.5 * ((r1 + r3) - (r2 + r4))
                    b_idx = int(np.argmax(p_rets))
                    if p_rets[b_idx] > anchor_sc + COMMIT_MARGIN:
                        st1 = c1 + np.clip(g1 / 11.0, -1.25, 1.25) * d1_m
                        st2 = c2 + np.clip(g2 / 11.0, -1.25, 1.25) * d2_m
                        wc1, wc2 = cands[b_idx]
                        nc1, nc2 = 0.5 * (wc1 + st1), 0.5 * (wc2 + st2)
                        sq_ab = float(np.sum(nc1 ** 2) + np.sum(nc2 ** 2))
                        if sq_ab > allow_ab_sq:
                            sc_f = math.sqrt(allow_ab_sq / sq_ab) * 0.999
                            nc1, nc2 = nc1 * sc_f, nc2 * sc_f
                        c1, c2 = nc1, nc2

                elif arm == "P2_PairedFlag_4x4" and use_joint:
                    best_4 = c_ab.copy()
                    best_s = anchor_sc
                    for _pair in range(2):
                        d4 = rng.choice([-1.0, 1.0], size=c_ab.shape) * 0.78
                        for sgn in (+1.0, -1.0):
                            proposals += 1
                            cand_4 = best_4 + sgn * d4
                            sq_4 = float(np.sum(cand_4 ** 2))
                            if sq_4 > allow_ab_sq:
                                rescaled_cnt += 1
                                cand_4 = cand_4 * (math.sqrt(allow_ab_sq / sq_4) * 0.999)
                            sc_c = score_predictions(forward_fast(xs_p, u_list, c_init[0], c_init[3], None, None, cand_4), up)
                            if sc_c > best_s + COMMIT_MARGIN:
                                best_s = sc_c
                                best_4 = cand_4
                    c_ab = best_4

                elif arm == "N1_Rescaled_Unprojected_SVD":
                    q_ep, _ = np.linalg.qr(sp[:6, :].T, mode="reduced")
                    # Note: `xs_p` has 24 rows, slice `:6` cleanly:
                    xs_p6 = [x[:6] for x in xs_p]
                    u_cur6 = forward_fast(xs_p6, u_list, c_init[0], c_init[3], c1, c2, None, sp[:6, :], w_extra)
                    u_ep_b, _ = np.linalg.qr((u_cur6 + rng.standard_normal((6, M_CILIA)) * 0.05).T, mode="reduced")
                    best_ex = w_extra.copy()
                    best_s = anchor_sc
                    for _pair in range(2):
                        g_rand = rng.standard_normal((6, 6)) * 0.16
                        dw = (u_ep_b @ g_rand) @ q_ep.T
                        for sgn in (+1.0, -1.0):
                            proposals += 1
                            cand_ex = best_ex + sgn * dw
                            tot_c = w_base_dense + cand_ex
                            tot_sq = float(np.sum(tot_c ** 2))
                            if tot_sq > max_frob_sq:
                                rescaled_cnt += 1
                                cand_ex = tot_c * (math.sqrt(max_frob_sq / tot_sq) * 0.999) - w_base_dense
                            sc_c = score_predictions(forward_fast(xs_p, u_list, c_init[0], c_init[3], c1, c2, None, sp, cand_ex), up)
                            if sc_c > best_s + COMMIT_MARGIN:
                                best_s = sc_c
                                best_ex = cand_ex
                    w_extra = best_ex

            ev_scores.append(
                score_predictions(
                    forward_fast(xs_e, u_list, c_init[0], c_init[3], c1, c2, c_ab if use_joint else None, se, w_extra),
                    ue,
                )
            )

        fin_sup = score_predictions(forward_fast(xs_sup_f, u_list, c_init[0], c_init[3], c1, c2, c_ab if use_joint else None, s_sup_f, w_extra), u_sup_f)
        fin_ab = score_predictions(forward_fast(xs_ab_f, u_list, c_init[0], c_init[3], c1, c2, c_ab if use_joint else None, s_ab_f, w_extra), u_ab_f)
        fin_d = score_predictions(forward_fast(xs_d_f, u_list, c_init[0], c_init[3], c1, c2, c_ab if use_joint else None, s_d_f, w_extra), u_d_f)
        fin_c = score_predictions(forward_fast(xs_c_f, u_list, c_init[0], c_init[3], c1, c2, c_ab if use_joint else None, s_c_f, w_extra), u_c_f)

        if w_extra is not None:
            viol_d = float(np.linalg.norm(w_extra @ q_list[0], ord="fro") + np.linalg.norm(u_list[0].T @ w_extra, ord="fro"))
            fin_frob = float(np.linalg.norm(w_base_dense + w_extra, ord="fro"))
        elif use_joint:
            viol_d = 0.0
            fin_frob = math.sqrt(fixed_03_sq + float(np.sum(c_ab ** 2)))
        else:
            viol_d = 0.0
            fin_frob = math.sqrt(fixed_03_sq + float(np.sum(c1 ** 2) + np.sum(c2 ** 2)))

        results[arm] = {
            "superposed_online_mean": float(np.mean(ev_scores)),
            "final_superposed_score": fin_sup,
            "final_drifted_ab_mean": fin_ab,
            "stationary_native_d_score": fin_d,
            "stationary_hop1_c_score": fin_c,
            "native_flag_violation": viol_d,
            "frob_ratio_vs_init": fin_frob / max(init_frob, 1e-12),
            "radial_rescale_rate": rescaled_cnt / max(proposals, 1),
        }

    return results


class TestE14AdversarialDriftAudit(unittest.TestCase):
    def test_fast_factorized_equivalence_and_null_gate(self) -> None:
        proto_path = THIS_DIR / "pre_registered_protocol.json"
        self.assertTrue(proto_path.exists())
        bank = evolve_canonical_specialists_for_seed(20261112)
        st = build_post_cascade_recipient_d(20261112, (1, 2, 3, 4), bank)
        cal = prepare_calibrated_state(st)

        # Verify factorized forward pass equals dense `192x256` forward pass to `< 1e-13`:
        s_t, _ = generate_regime_episode("R1_Concurrent_SO2", 3, 24, (1, 2, 3, 4), np.random.default_rng(7), cal["perm_in_d"], cal["perm_out_d"], 12)
        xs_t = precompute_slice_activations(cal["q_list"], cal["rms_list"], s_t)
        u_fast = forward_fast(xs_t, cal["u_list"], cal["c_init"][0], cal["c_init"][3], cal["c_init"][1], cal["c_init"][2])
        # Dense manual check:
        u_dense = np.zeros_like(u_fast)
        for m in range(4):
            w_m = cal["u_list"][m] @ cal["c_init"][m] @ cal["q_list"][m].T
            # `xs_t[m] @ q_m^T` * (1 / (sqrt(DIM)*0.125)) is `s_slice`, so `(s_slice @ w_m.T) * scale == xs_t[m] @ q_m.T @ w_m.T`:
            zm = (xs_t[m] @ cal["q_list"][m].T) @ w_m.T
            u_dense += zm / np.sqrt(1.0 + zm * zm)
        self.assertLess(float(np.max(np.abs(u_fast - u_dense))), 1e-13)

        r_z = run_regime_all_arms(cal, "R0_ZeroDrift_Null", 24, 1.20)
        self.assertLessEqual(r_z["K1_SO2_Hadamard"]["final_superposed_score"] - r_z["F0_Static_WFBK"]["final_superposed_score"], 1.5)
        self.assertLessEqual(r_z["P1_Rescaled_2x2_Fiber"]["frob_ratio_vs_init"], 1.2001)


def run_preregistered_audit() -> Dict[str, object]:
    t0 = time.time()
    proto_bytes = (THIS_DIR / "pre_registered_protocol.json").read_bytes()
    proto_sha256 = hashlib.sha256(proto_bytes).hexdigest()
    proto = json.loads(proto_bytes.decode("utf-8"))

    seeds: List[int] = proto["sample_design"]["seed_list"]
    tetrads = [tuple(t) for t in proto["sample_design"]["tetrads_per_seed"]]
    n_steps = int(proto["sample_design"]["online_steps_per_run"])
    headroom = float(proto["sample_design"]["fair_frob_headroom_multiplier"])

    data: Dict[str, Dict[str, List[Dict[str, float]]]] = {
        r: {a: [] for a in AUDIT_ARMS} for r in REGIMES
    }

    for seed in seeds:
        bank = evolve_canonical_specialists_for_seed(seed)
        cal_states = [prepare_calibrated_state(build_post_cascade_recipient_d(seed, tet, bank)) for tet in tetrads]
        for reg in REGIMES:
            tet_runs = [run_regime_all_arms(cs, reg, n_steps, headroom) for cs in cal_states]
            for arm in AUDIT_ARMS:
                keys = tet_runs[0][arm].keys()
                agg = {k: float(np.mean([tr[arm][k] for tr in tet_runs])) for k in keys}
                agg["native_flag_violation"] = float(np.max([tr[arm]["native_flag_violation"] for tr in tet_runs]))
                data[reg][arm].append(agg)

    def vec(reg: str, arm: str, metric: str) -> np.ndarray:
        return np.array([row[metric] for row in data[reg][arm]], dtype=np.float64)

    diff_n1 = vec("R0_ZeroDrift_Null", "K1_SO2_Hadamard", "final_superposed_score") - vec("R0_ZeroDrift_Null", "F0_Static_WFBK", "final_superposed_score")
    p_n1 = float(stats.wilcoxon(diff_n1).pvalue) if np.any(np.abs(diff_n1) > 1e-12) else 1.0
    diff_n2 = vec("R0_ShuffledDrift_Null", "K1_SO2_Hadamard", "final_superposed_score") - vec("R0_ShuffledDrift_Null", "F0_Static_WFBK", "final_superposed_score")
    p_n2 = float(stats.wilcoxon(diff_n2).pvalue) if np.any(np.abs(diff_n2) > 1e-12) else 1.0

    null_results = {
        "N1_zero_drift_null": {
            "mean_diff_K1_minus_F0": round(float(np.mean(diff_n1)), 4),
            "sd_diff": round(float(np.std(diff_n1)), 4),
            "wilcoxon_p_two_sided": round(p_n1, 6),
            "passed_null_gate": bool(float(np.mean(diff_n1)) <= 0.50 and abs(float(np.mean(diff_n1))) <= 1.50),
        },
        "N2_shuffled_drift_null": {
            "mean_diff_K1_minus_F0": round(float(np.mean(diff_n2)), 4),
            "sd_diff": round(float(np.std(diff_n2)), 4),
            "wilcoxon_p_two_sided": round(p_n2, 6),
            "passed_null_gate": bool(float(np.mean(diff_n2)) <= 1.00),
        },
    }

    h_specs = [
        ("H01_R1_K1_beats_F0", vec("R1_Concurrent_SO2", "K1_SO2_Hadamard", "final_superposed_score") - vec("R1_Concurrent_SO2", "F0_Static_WFBK", "final_superposed_score"), 25.0),
        ("H02_R1_K1_vs_fair_P1", vec("R1_Concurrent_SO2", "K1_SO2_Hadamard", "superposed_online_mean") - vec("R1_Concurrent_SO2", "P1_Rescaled_2x2_Fiber", "superposed_online_mean"), 3.0),
        ("H03_R1_K1_beats_N1_native_retention", vec("R1_Concurrent_SO2", "K1_SO2_Hadamard", "stationary_native_d_score") - vec("R1_Concurrent_SO2", "N1_Rescaled_Unprojected_SVD", "stationary_native_d_score"), 10.0),
        ("H04_R2_Shear_degrades_K1", vec("R1_Concurrent_SO2", "K1_SO2_Hadamard", "final_drifted_ab_mean") - vec("R2_Scale_And_Shear", "K1_SO2_Hadamard", "final_drifted_ab_mean"), 12.0),
        ("H05_R2_Fair_P1_beats_K1_under_shear", vec("R2_Scale_And_Shear", "P1_Rescaled_2x2_Fiber", "final_drifted_ab_mean") - vec("R2_Scale_And_Shear", "K1_SO2_Hadamard", "final_drifted_ab_mean"), 4.0),
        ("H06_R3_CrossSlice_degrades_K1", vec("R1_Concurrent_SO2", "K1_SO2_Hadamard", "final_drifted_ab_mean") - vec("R3_CrossSlice_Mixing", "K1_SO2_Hadamard", "final_drifted_ab_mean"), 20.0),
        ("H07_R3_Paired4x4_P2_beats_K1_and_P1", vec("R3_CrossSlice_Mixing", "P2_PairedFlag_4x4", "final_superposed_score") - vec("R3_CrossSlice_Mixing", "K1_SO2_Hadamard", "final_superposed_score"), 8.0),
        ("H08_R4_Leakage_degrades_K1", vec("R1_Concurrent_SO2", "K1_SO2_Hadamard", "final_drifted_ab_mean") - vec("R4_OutOfSlice_Leakage", "K1_SO2_Hadamard", "final_drifted_ab_mean"), 25.0),
        ("H09_R4_Leakage_degrades_Paired4x4_P2", vec("R3_CrossSlice_Mixing", "P2_PairedFlag_4x4", "final_superposed_score") - vec("R4_OutOfSlice_Leakage", "P2_PairedFlag_4x4", "final_superposed_score"), 10.0),
        ("H10_R4_N1_flag_violation_cost", vec("R4_OutOfSlice_Leakage", "N1_Rescaled_Unprojected_SVD", "native_flag_violation") - vec("R4_OutOfSlice_Leakage", "K1_SO2_Hadamard", "native_flag_violation"), 0.25),
    ]
    assert len(h_specs) == proto["multiple_testing_correction"]["family_size_M"] == 10

    raw_p: Dict[str, float] = {}
    family_rows: Dict[str, Dict[str, object]] = {}
    for hid, diff, min_eff in h_specs:
        p_val = float(stats.wilcoxon(diff, alternative="two-sided", method="exact").pvalue) if np.any(np.abs(diff) > 1e-12) else 1.0
        raw_p[hid] = p_val
        family_rows[hid] = {
            "predeclared_min_effect": min_eff,
            "observed_mean_effect": round(float(np.mean(diff)), 3),
            "observed_median_effect": round(float(np.median(diff)), 3),
            "positive_seeds_of_12": int(np.sum(diff > 0)),
            "wilcoxon_p_two_sided": round(p_val, 6),
        }

    adj_p = holm_bonferroni(raw_p)
    for hid, _, min_eff in h_specs:
        hp = adj_p[hid]
        family_rows[hid]["holm_bonferroni_p_M10"] = round(hp, 6)
        family_rows[hid]["passed_preregistered_threshold"] = bool(
            family_rows[hid]["observed_mean_effect"] >= min_eff and hp <= 0.05
        )

    regime_matrix: Dict[str, Dict[str, Dict[str, float]]] = {}
    for reg in REGIMES:
        regime_matrix[reg] = {}
        for arm in AUDIT_ARMS:
            regime_matrix[reg][arm] = {
                "superposed_online_mean": round(float(np.mean(vec(reg, arm, "superposed_online_mean"))), 2),
                "final_superposed_score": round(float(np.mean(vec(reg, arm, "final_superposed_score"))), 2),
                "final_drifted_ab_mean": round(float(np.mean(vec(reg, arm, "final_drifted_ab_mean"))), 2),
                "stationary_native_d_score": round(float(np.mean(vec(reg, arm, "stationary_native_d_score"))), 2),
                "stationary_hop1_c_score": round(float(np.mean(vec(reg, arm, "stationary_hop1_c_score"))), 2),
                "native_flag_violation_max": round(float(np.max(vec(reg, arm, "native_flag_violation"))), 6),
                "frob_ratio_vs_init_mean": round(float(np.mean(vec(reg, arm, "frob_ratio_vs_init"))), 4),
                "radial_rescale_rate_mean": round(float(np.mean(vec(reg, arm, "radial_rescale_rate"))), 4),
            }

    out = {
        "protocol_id": proto["protocol_id"],
        "preregistered_protocol_sha256": proto_sha256,
        "family_size_M": 10,
        "fwer_alpha": 0.05,
        "total_organism_runs": len(seeds) * len(tetrads) * len(REGIMES) * len(AUDIT_ARMS),
        "elapsed_sec": round(time.time() - t0, 2),
        "null_sanity_gates": null_results,
        "hypothesis_family_M10": family_rows,
        "regimes": regime_matrix,
    }
    (THIS_DIR / "e14_adversarial_audit_summary.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


if __name__ == "__main__":
    if "--unit" in sys.argv:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestE14AdversarialDriftAudit)
        ok = unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()
        raise SystemExit(0 if ok else 1)
    res = run_preregistered_audit()
    print(json.dumps(res, indent=2))
