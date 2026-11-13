#!/usr/bin/env python3
"""E11: horizontal plasmid transfer on toy MLP cells (issue #149).

CPU-only NumPy implementation (no downloads). Run from repository root:

  python3 docs/program/experiments/e11-plasmid-transfer-breaking-through-2026-11/run_e11.py
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT))

from weft.runtime.invariants import R_INVARIANT  # noqa: E402

PREREG_SEEDS = [17, 29, 43, 101, 202]
CORE_HIDDEN = 4
D_IN = 8
HIDDEN = 16
N_TASKS = 4
N_KEPT = 3
NJAC = 128
N_EVAL = 512
TRAIN_STEPS_KEPT = 800
TRAIN_STEPS_NEW = 500
LR = 0.08
RETENTION_TOL = 0.10
NEW_TASK_ACC_BAR = 0.80
CERT_BAR = 1e-3
SHIFTED_PASS_NEED = 3


def git_commit() -> str:
    for root in (ROOT, HERE.parents[4]):
        try:
            return (
                subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"])
                .decode()
                .strip()
            )
        except Exception:
            continue
    return "unknown"


@dataclass
class ToyParams:
    w1: np.ndarray
    b1: np.ndarray
    w2: np.ndarray
    b2: np.ndarray

    def clone(self) -> "ToyParams":
        return ToyParams(self.w1.copy(), self.b1.copy(), self.w2.copy(), self.b2.copy())

    def plastic_mask(self) -> np.ndarray:
        n = self.w1.size + self.b1.size + self.w2.size + self.b2.size
        mask = np.ones(n, dtype=np.float64)
        # freeze incoming weights + biases to hidden units 0..CORE_HIDDEN-1
        mask[: CORE_HIDDEN * D_IN] = 0.0
        off = self.w1.size
        mask[off : off + CORE_HIDDEN] = 0.0
        return mask

    def flat(self) -> np.ndarray:
        return np.concatenate([self.w1.ravel(), self.b1, self.w2.ravel(), self.b2])

    @staticmethod
    def from_flat(flat: np.ndarray) -> "ToyParams":
        off = 0
        w1 = flat[off : off + HIDDEN * D_IN].reshape(HIDDEN, D_IN)
        off += HIDDEN * D_IN
        b1 = flat[off : off + HIDDEN]
        off += HIDDEN
        w2 = flat[off : off + N_TASKS * HIDDEN].reshape(N_TASKS, HIDDEN)
        off += N_TASKS * HIDDEN
        b2 = flat[off : off + N_TASKS]
        return ToyParams(w1, b1, w2, b2)


def rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def init_params(seed: int) -> ToyParams:
    g = rng(seed)
    return ToyParams(
        g.normal(0, 0.4, (HIDDEN, D_IN)),
        np.zeros(HIDDEN),
        g.normal(0, 0.4, (N_TASKS, HIDDEN)),
        np.zeros(N_TASKS),
    )


def task_hyperplanes(seed: int) -> Tuple[np.ndarray, np.ndarray]:
    g = rng(seed + 9000)
    w = g.normal(0, 1, (N_TASKS, D_IN))
    w /= np.linalg.norm(w, axis=1, keepdims=True) + 1e-9
    b = g.normal(0, 0.1, N_TASKS)
    return w, b


def labels_for(x: np.ndarray, tw: np.ndarray, tb: np.ndarray, task: int) -> np.ndarray:
    logit = x @ tw[task] + tb[task]
    return np.sign(logit)


def forward(p: ToyParams, x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    z1 = x @ p.w1.T + p.b1
    h = np.maximum(0.0, z1)
    logits = h @ p.w2.T + p.b2
    return h, logits


def accuracy(p: ToyParams, x: np.ndarray, tw: np.ndarray, tb: np.ndarray, task: int) -> float:
    _, logits = forward(p, x)
    pred = np.sign(logits[:, task])
    y = labels_for(x, tw, tb, task)
    return float(np.mean(pred == y))


def backward_task(
    p: ToyParams, x: np.ndarray, tw: np.ndarray, tb: np.ndarray, task_ids: Sequence[int]
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n = x.shape[0]
    z1 = x @ p.w1.T + p.b1
    h = np.maximum(0.0, z1)
    logits = h @ p.w2.T + p.b2
    dz2 = np.zeros_like(logits)
    for t in task_ids:
        y = labels_for(x, tw, tb, t)
        dz2[:, t] = 2.0 * (logits[:, t] - y) / n
    dw2 = dz2.T @ h
    db2 = np.sum(dz2, axis=0)
    dh = dz2 @ p.w2
    dh[z1 <= 0.0] = 0.0
    dw1 = dh.T @ x
    db1 = np.sum(dh, axis=0)
    return dw1, db1, dw2, db2


def train_tasks(
    p: ToyParams,
    mask: np.ndarray,
    x: np.ndarray,
    tw: np.ndarray,
    tb: np.ndarray,
    task_ids: Sequence[int],
    steps: int,
) -> ToyParams:
    flat = p.flat().copy()
    idx = np.where(mask > 0.5)[0]
    for _ in range(steps):
        cur = ToyParams.from_flat(flat)
        dw1, db1, dw2, db2 = backward_task(cur, x, tw, tb, task_ids)
        grad = np.concatenate([dw1.ravel(), db1, dw2.ravel(), db2])
        flat[idx] -= LR * grad[idx]
    return ToyParams.from_flat(flat)


def sample_uniform(n: int, seed: int) -> np.ndarray:
    return rng(seed).uniform(-1.0, 1.0, (n, D_IN))


def _orthogonal_matrix(seed: int) -> np.ndarray:
    g = rng(seed)
    q, _ = np.linalg.qr(g.normal(0, 1, (D_IN, D_IN)))
    return q


ROTATE = _orthogonal_matrix(7)


def apply_probe(name: str, x: np.ndarray) -> np.ndarray:
    if name == "iid":
        return x
    if name == "scale_1p5":
        return 1.5 * x
    if name == "shift_pos":
        return x + 0.3
    if name == "rotate":
        return x @ ROTATE.T
    if name == "sparse":
        z = x.copy()
        z[:, 4:] = 0.0
        return z
    raise ValueError(name)


PROBE_NAMES = ["iid", "scale_1p5", "shift_pos", "rotate", "sparse"]
SHIFTED_NAMES = ["scale_1p5", "shift_pos", "rotate", "sparse"]


def hungarian_permutation(h_a: np.ndarray, h_b: np.ndarray) -> np.ndarray:
    a = h_a - h_a.mean(0, keepdims=True)
    b = h_b - h_b.mean(0, keepdims=True)
    num = a.T @ b
    den = np.linalg.norm(a, axis=0, keepdims=True).T * np.linalg.norm(b, axis=0, keepdims=True) + 1e-8
    cost = -(num / den)
    perm = np.zeros(HIDDEN, dtype=np.int64)
    used = set()
    for j in range(HIDDEN):
        order = np.argsort(cost[:, j])
        for i in order:
            if i not in used:
                perm[j] = i
                used.add(int(i))
                break
    return perm


def permute_params(p: ToyParams, perm: np.ndarray) -> ToyParams:
    """perm[i] = source hidden index feeding new unit i (gauge-equivariant relu reorder)."""
    return ToyParams(
        p.w1[perm].copy(),
        p.b1[perm].copy(),
        p.w2[:, perm].copy(),
        p.b2.copy(),
    )


def align_delta(delta: ToyParams, perm: np.ndarray) -> ToyParams:
    return ToyParams(
        delta.w1[perm].copy(),
        delta.b1[perm].copy(),
        delta.w2[:, perm].copy(),
        delta.b2.copy(),
    )


def grad_logit_wrt_plastic(
    p: ToyParams, mask: np.ndarray, x_row: np.ndarray, task: int
) -> np.ndarray:
    flat = p.flat()
    idx = np.where(mask > 0.5)[0]
    eps = 1e-4
    base_logit = forward(p, x_row[None, :])[1][0, task]
    rows = []
    for i in idx:
        pert = flat.copy()
        pert[i] += eps
        lp = ToyParams.from_flat(pert)
        rows.append((forward(lp, x_row[None, :])[1][0, task] - base_logit) / eps)
    return np.array(rows, dtype=np.float64)


def jacobian_keep(
    p: ToyParams, mask: np.ndarray, x_probe: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    rows = []
    for t in range(N_KEPT):
        for i in range(x_probe.shape[0]):
            rows.append(grad_logit_wrt_plastic(p, mask, x_probe[i], t))
    j = np.stack(rows, axis=0)
    _, s, vh = np.linalg.svd(j, full_matrices=False)
    tol = max(j.shape) * np.finfo(float).eps * (s.max() if s.size else 1.0)
    keep = s > tol
    u_keep = vh[keep].T if keep.any() else np.zeros((j.shape[1], 1))
    return j, u_keep


def project_null(delta_plastic: np.ndarray, j: np.ndarray) -> np.ndarray:
    pinv = np.linalg.pinv(j)
    return delta_plastic - pinv @ (j @ delta_plastic)


def plastic_vec_from_delta(delta: ToyParams, mask: np.ndarray) -> np.ndarray:
    return delta.flat()[mask > 0.5]


def apply_plastic_delta(p: ToyParams, mask: np.ndarray, d_plastic: np.ndarray) -> ToyParams:
    flat = p.flat().copy()
    flat[mask > 0.5] += d_plastic
    return ToyParams.from_flat(flat)


def frobenius_clip(d: np.ndarray, radius: float) -> np.ndarray:
    n = float(np.linalg.norm(d))
    if n <= radius or n == 0.0:
        return d
    return d * (radius / n)


def params_delta(a: ToyParams, b: ToyParams) -> ToyParams:
    return ToyParams(a.w1 - b.w1, a.b1 - b.b1, a.w2 - b.w2, a.b2 - b.b2)


def eval_retention(
    pre: ToyParams, post: ToyParams, tw: np.ndarray, tb: np.ndarray, probe_seed: int
) -> Dict[str, Dict[str, float]]:
    out: Dict[str, Dict[str, float]] = {}
    for pname in PROBE_NAMES:
        x = apply_probe(pname, sample_uniform(N_EVAL, probe_seed + abs(hash(pname)) % 10000))
        row: Dict[str, float] = {}
        for t in range(N_KEPT):
            a0 = accuracy(pre, x, tw, tb, t)
            a1 = accuracy(post, x, tw, tb, t)
            row[f"task{t}_pre"] = a0
            row[f"task{t}_post"] = a1
            row[f"task{t}_drop"] = a0 - a1
            row[f"task{t}_pass"] = 1.0 if a0 - a1 <= RETENTION_TOL else 0.0
        out[pname] = row
    return out


def shifted_probe_pass_count(ret: Dict[str, Dict[str, float]]) -> int:
    c = 0
    for pname in SHIFTED_NAMES:
        if all(ret[pname][f"task{t}_pass"] >= 1.0 for t in range(N_KEPT)):
            c += 1
    return c


def linearization_error(
    pre: ToyParams,
    post: ToyParams,
    mask: np.ndarray,
    j: np.ndarray,
    x: np.ndarray,
    task: int,
) -> float:
    d = plastic_vec_from_delta(params_delta(post, pre), mask)
    rs = task * x.shape[0]
    re = rs + min(64, x.shape[0])
    j_t = j[rs:re]
    pred = j_t @ d
    errs = []
    for i in range(re - rs):
        actual = forward(post, x[i : i + 1])[1][0, task] - forward(pre, x[i : i + 1])[1][0, task]
        errs.append(abs(pred[i] - actual))
    return float(np.mean(errs)) if errs else float("nan")


def run_seed(seed: int, mode: str) -> Dict:
    tw, tb = task_hyperplanes(seed)
    x_train = sample_uniform(600, seed + 10000)
    x_jac = sample_uniform(NJAC, seed + 10001)
    mask = init_params(0).plastic_mask()

    p_a = train_tasks(init_params(seed), mask, x_train, tw, tb, list(range(N_KEPT)), TRAIN_STEPS_KEPT)
    base_a = p_a.clone()
    p_a = train_tasks(p_a, mask, x_train, tw, tb, [N_KEPT - 1], TRAIN_STEPS_NEW)

    perm_fixed: np.ndarray | None = None
    if mode == "permuted_sanity":
        perm_fixed = rng(seed + 555).permutation(HIDDEN)
        p_b = permute_params(base_a, perm_fixed)
    else:
        p_b = train_tasks(init_params(seed + 1000), mask, x_train, tw, tb, list(range(N_KEPT)), TRAIN_STEPS_KEPT)

    pre_b = p_b.clone()
    delta = params_delta(p_a, base_a)
    d_plastic = plastic_vec_from_delta(delta, mask)
    d_fro = float(np.linalg.norm(d_plastic))
    gate_r = min(d_fro, float(R_INVARIANT))

    h_a, _ = forward(base_a, x_jac)
    h_b, _ = forward(p_b, x_jac)
    perm_ab = perm_fixed if perm_fixed is not None else hungarian_permutation(h_a, h_b)
    median_corr = float(np.median([np.corrcoef(h_a[:, i], h_b[:, perm_ab[i]])[0, 1] for i in range(HIDDEN)]))

    j_keep, u_keep = jacobian_keep(p_b, mask, x_jac)
    null_d = project_null(d_plastic.copy(), j_keep)

    flat_aligned = align_delta(delta, perm_ab).flat()
    aligned_pl = flat_aligned[mask > 0.5]
    plasmid_d = project_null(aligned_pl.copy(), j_keep)

    arms = {
        "raw_coord": apply_plastic_delta(p_b, mask, d_plastic.copy()),
        "perm_taskvec": apply_plastic_delta(p_b, mask, aligned_pl.copy()),
        "null_only": apply_plastic_delta(p_b, mask, null_d.copy()),
        "plasmid": apply_plastic_delta(p_b, mask, plasmid_d.copy()),
        "frobenius_gate": apply_plastic_delta(p_b, mask, frobenius_clip(d_plastic.copy(), gate_r)),
    }
    meta = {
        "raw_coord": {"training_steps_b": 0},
        "perm_taskvec": {"training_steps_b": 0},
        "null_only": {
            "training_steps_b": 0,
            "cert_ut_dwf": float(np.linalg.norm(u_keep.T @ null_d)) if u_keep.size else 0.0,
        },
        "plasmid": {
            "training_steps_b": 0,
            "cert_ut_dwf": float(np.linalg.norm(u_keep.T @ plasmid_d)) if u_keep.size else 0.0,
            "gramian_alignment_failed": median_corr < 0.3,
            "median_act_corr": median_corr,
        },
        "frobenius_gate": {"training_steps_b": 0, "r_gate": gate_r, "delta_fro_norm": d_fro},
    }

    x_new = sample_uniform(N_EVAL, seed + 5000)
    by_arm: Dict[str, Dict] = {}
    for name, post in arms.items():
        by_arm[name] = {
            "new_task_accuracy": accuracy(post, x_new, tw, tb, N_KEPT - 1),
            "iid_all_kept_pass": all(
                eval_retention(pre_b, post, tw, tb, seed + 7000)["iid"][f"task{t}_pass"] >= 1.0
                for t in range(N_KEPT)
            ),
            "shifted_probe_pass_count": shifted_probe_pass_count(
                eval_retention(pre_b, post, tw, tb, seed + 7000)
            ),
            "retention_by_probe": eval_retention(pre_b, post, tw, tb, seed + 7000),
            "nonlinear_drift_new_task_mae": linearization_error(
                pre_b, post, mask, j_keep, x_new[:64], N_KEPT - 1
            ),
            **meta[name],
        }
    return {
        "seed": seed,
        "mode": mode,
        "delta_frobenius_plastic": d_fro,
        "perm_correlation_median": median_corr,
        "results_by_arm": by_arm,
    }


def aggregate(runs: List[Dict]) -> Dict:
    arms = ["raw_coord", "perm_taskvec", "null_only", "plasmid", "frobenius_gate"]
    out: Dict[str, Dict] = {}
    for arm in arms:
        acc = [r["results_by_arm"][arm]["new_task_accuracy"] for r in runs]
        sh = [r["results_by_arm"][arm]["shifted_probe_pass_count"] for r in runs]
        iid = [1.0 if r["results_by_arm"][arm]["iid_all_kept_pass"] else 0.0 for r in runs]
        cert = [r["results_by_arm"][arm].get("cert_ut_dwf") for r in runs]
        cert_vals = [c for c in cert if c is not None]
        out[arm] = {
            "new_task_accuracy_mean": float(np.mean(acc)),
            "new_task_accuracy_std": float(np.std(acc, ddof=1)) if len(acc) > 1 else 0.0,
            "new_task_accuracy_per_seed": acc,
            "seeds_ge_080": int(sum(a >= NEW_TASK_ACC_BAR for a in acc)),
            "shifted_pass_mean": float(np.mean(sh)),
            "shifted_pass_per_seed": sh,
            "iid_retention_rate": float(np.mean(iid)),
            "cert_ut_dwf_mean": float(np.mean(cert_vals)) if cert_vals else float("nan"),
        }
    return out


def pass_bar_table(agg: Dict) -> List[Dict]:
    rows = []
    for arm, a in agg.items():
        rows.append(
            {
                "arm": arm,
                "new_task_acc_mean": round(a["new_task_accuracy_mean"], 4),
                "bar_new_task_080": a["new_task_accuracy_mean"] >= NEW_TASK_ACC_BAR,
                "shifted_pass_mean": round(a["shifted_pass_mean"], 2),
                "bar_shifted_3of4": a["shifted_pass_mean"] >= SHIFTED_PASS_NEED,
                "iid_retention_rate": round(a["iid_retention_rate"], 3),
                "bar_iid_1p0": a["iid_retention_rate"] >= 1.0,
                "cert_ut_dwf_mean": round(a["cert_ut_dwf_mean"], 6),
                "bar_cert_1em3": a["cert_ut_dwf_mean"] <= CERT_BAR,
                "training_steps_b": 0,
            }
        )
    return rows


def plasmid_verdict(agg: Dict, perm_runs: List[Dict]) -> Dict:
    p = agg["plasmid"]
    checks = {
        "new_task_mean_ge_080": p["new_task_accuracy_mean"] >= NEW_TASK_ACC_BAR,
        "new_task_seeds_ge_080_ge_3of5": p["seeds_ge_080"] >= 3,
        "shifted_pass_mean_ge_3": p["shifted_pass_mean"] >= SHIFTED_PASS_NEED,
        "iid_retention_all_seeds": p["iid_retention_rate"] >= 1.0,
        "cert_mean_le_1em3": p["cert_ut_dwf_mean"] <= CERT_BAR,
        "permuted_sanity_perfect": all(
            r["results_by_arm"]["plasmid"]["new_task_accuracy"] >= 0.95
            and r["results_by_arm"]["plasmid"]["shifted_probe_pass_count"] == 4
            for r in perm_runs
        ),
    }
    passed = sum(1 for v in checks.values() if v)
    if passed == len(checks):
        verdict = "pass"
    elif passed == 0:
        verdict = "fail"
    else:
        verdict = "mixed"
    return {"checks": checks, "verdict": verdict, "passed_count": passed, "total_checks": len(checks)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=HERE / "results" / "e11_results.json")
    args = parser.parse_args()
    t0 = time.perf_counter()
    cross = [run_seed(s, "cross_seed") for s in PREREG_SEEDS]
    perm = [run_seed(s, "permuted_sanity") for s in PREREG_SEEDS]
    agg = aggregate(cross)
    payload = {
        "experiment": "E11",
        "issue": 149,
        "prereg": "PREREG.md",
        "commit": git_commit(),
        "elapsed_s": round(time.perf_counter() - t0, 3),
        "seeds_cross": PREREG_SEEDS,
        "per_seed_cross": cross,
        "per_seed_permuted_sanity": perm,
        "aggregate_cross_seed": agg,
        "pass_bar_table": pass_bar_table(agg),
        "plasmid_primary_verdict": plasmid_verdict(agg, perm),
        "constants": {
            "RETENTION_TOL": RETENTION_TOL,
            "NEW_TASK_ACC_BAR": NEW_TASK_ACC_BAR,
            "CERT_BAR": CERT_BAR,
            "SHIFTED_PASS_NEED": SHIFTED_PASS_NEED,
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"Wrote {args.out}")
    print(f"Plasmid verdict: {payload['plasmid_primary_verdict']['verdict']}")


if __name__ == "__main__":
    main()
