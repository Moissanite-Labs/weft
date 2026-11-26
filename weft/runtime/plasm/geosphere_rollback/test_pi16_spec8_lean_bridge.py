#!/usr/bin/env python3
"""Pure-stdlib R4/R5 verification suite for `pi16_spec8_lean_bridge.py`.

Zero bare `assert`s, zero unseeded RNG, zero third-party deps, zero stdout bytes.
Runs cleanly under `python3 -m unittest discover -s weft/runtime/plasm -p 'test_*.py'`
and standalone across `-I -B`, `-I -O -B`, and `-I -B -W error`.
When `lean` is installed locally (including under `env -i PATH=.../.elan/bin:... HOME=/nonexistent`),
executes all 7 live pure-Init goals + Step-0 all-reject 16 B rollback; when `lean`
is absent in CI, gracefully skips only the live-`lean` integration test while running
the full deterministic, R12/R13b, and mock-oracle suites with zero failures.
"""
from __future__ import annotations

import copy
import io
import json
import math
import os
from pathlib import Path
import stat
import struct
import sys
import tempfile
import unittest
from unittest import mock

if __package__:
    from . import pi16_spec8_lean_bridge as bridge
else:
    _HERE = Path(__file__).resolve().parent
    if str(_HERE) not in sys.path:
        sys.path.insert(0, str(_HERE))
    import pi16_spec8_lean_bridge as bridge


def _write_executable(path: Path, content: str) -> str:
    path.write_text(content, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return os.fspath(path)


class _StubSynthesisOracle:
    """In-memory oracle stub for testing all synthesis acceptance/rejection guards."""

    def __init__(
        self,
        *,
        accept_step0: bool = False,
        catch_grind_choice: bool = True,
        solve_goals: bool = True,
    ) -> None:
        self.lean_version = "Lean (version 4.36.0, stub)"
        self.env = {"PATH": "/usr/bin:/bin"}
        self._accept_step0 = accept_step0
        self._catch_grind_choice = catch_grind_choice
        self._solve_goals = solve_goals

    def verify_8_branches_parallel(
        self,
        *,
        theorem_name: str,
        theorem_decl: str,
        candidate_tactics: list[str],
    ) -> list[dict[str, object]]:
        del theorem_decl
        rows: list[dict[str, object]] = []
        if theorem_name == "s0_all_reject_rollback":
            for idx, tac in enumerate(candidate_tactics):
                if self._accept_step0 and idx == 0:
                    rows.append(
                        {
                            "branch_idx": idx,
                            "accepted": True,
                            "stage": "VERIFIED_PURE_INIT",
                            "reason": "OK",
                            "axioms": [],
                            "source_sha256": "0" * 64,
                            "elapsed_ms": 0.1,
                        }
                    )
                elif self._catch_grind_choice and "grind" in tac:
                    rows.append(
                        {
                            "branch_idx": idx,
                            "accepted": False,
                            "stage": "R13B_FORBIDDEN_AXIOM",
                            "reason": "Classical.choice",
                            "axioms": ["Classical.choice"],
                            "source_sha256": "0" * 64,
                            "elapsed_ms": 0.1,
                        }
                    )
                elif "sorry" in tac or "admit" in tac or "native_decide" in tac:
                    rows.append(
                        {
                            "branch_idx": idx,
                            "accepted": False,
                            "stage": "R13B_STATIC_REJECT",
                            "reason": "R03_SORRY_ADMIT",
                            "axioms": [],
                            "source_sha256": "0" * 64,
                            "elapsed_ms": 0.1,
                        }
                    )
                else:
                    rows.append(
                        {
                            "branch_idx": idx,
                            "accepted": False,
                            "stage": "LEAN_KERNEL_REJECT",
                            "reason": "rc=1",
                            "axioms": [],
                            "source_sha256": "0" * 64,
                            "elapsed_ms": 0.1,
                        }
                    )
            return rows

        for idx, _tac in enumerate(candidate_tactics):
            accepted = self._solve_goals and idx == 4
            rows.append(
                {
                    "branch_idx": idx,
                    "accepted": accepted,
                    "stage": "VERIFIED_PURE_INIT" if accepted else "LEAN_KERNEL_REJECT",
                    "reason": "OK" if accepted else "rc=1",
                    "axioms": ["propext"] if accepted else [],
                    "source_sha256": "a" * 64,
                    "elapsed_ms": 0.2,
                }
            )
        return rows


class TestWeftGeospherePi16Spec8LeanR5(unittest.TestCase):
    def test_su2_cayley_polish_and_16b_pack_unpack_guards(self) -> None:
        u = bridge.quat_nr_polish(bridge.quat_mul(bridge.cayley_su2(0.12, -0.09, 0.07), (1.0, 0.0, 0.0, 0.0)))
        self.assertAlmostEqual(math.sqrt(sum(c * c for c in u)), 1.0, places=5)
        raw = bridge.pack_pi_t0_16b(u)
        self.assertEqual(len(raw), bridge.WEFT_PI_T0_BYTES_PER_SPINOR)
        self.assertEqual(bridge.unpack_pi_t0_16b(raw), u)

        # Large finite FP32 omega stays finite via FP64 n2 accumulation
        u_big = bridge.cayley_su2(1e25, 0.0, 0.0)
        self.assertAlmostEqual(math.sqrt(sum(c * c for c in u_big)), 1.0, places=5)

        # Negative guards: cayley_su2 non-finite, overflow, bool, bytes
        for bad_w in (
            (float("nan"), 0.0, 0.0),
            (0.0, float("inf"), 0.0),
            (0.0, 0.0, float("-inf")),
            (1e308, 0.0, 0.0),
            (10**400, 0.0, 0.0),
            (True, 0.0, 0.0),
            (b"1", 0.0, 0.0),
        ):
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                bridge.cayley_su2(*bad_w)  # type: ignore[arg-type]
            self.assertEqual(ctx.exception.code, "NON_FINITE_OMEGA")

        # Negative guards: quat_nr_polish arity, zero, non-finite, overflow, bool, bytes
        for bad_q in (
            (1.0, 0.0, 0.0),
            b"1234",
            (0.0, 0.0, 0.0, 0.0),
            (float("nan"), 0.0, 0.0, 0.0),
            (float("inf"), 0.0, 0.0, 0.0),
            (1e308, 0.0, 0.0, 0.0),
            (1e25, 0.0, 0.0, 0.0),  # q * (3 - n2)/2 overflows FP32 output
            (True, 0.0, 0.0, 0.0),
        ):
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                bridge.quat_nr_polish(bad_q)  # type: ignore[arg-type]
            self.assertEqual(ctx.exception.code, "ZERO_OR_NONFINITE_SPINOR")

        # Negative guards: pack_pi_t0_16b arity, bytes/str, non-finite, overflow, bool, non-unit spinor
        for bad_arity in ((1.0, 0.0, 0.0), (1.0, 0.0, 0.0, 0.0, 0.0), b"1234", "1234", 42, {0: 1.0, 1: 0.0, 2: 0.0, 3: 0.0}):
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                bridge.pack_pi_t0_16b(bad_arity)  # type: ignore[arg-type]
            self.assertEqual(ctx.exception.code, "PI_T0_ARITY_BAD")
        for bad_val in (
            (float("nan"), 0.0, 0.0, 0.0),
            (1.0, 0.0, float("inf"), 0.0),
            (10**400, 0.0, 0.0, 0.0),
            (1e308, 0.0, 0.0, 0.0),
            (True, 0.0, 0.0, 0.0),
            (b"1", b"0", b"0", b"0"),
        ):
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                bridge.pack_pi_t0_16b(bad_val)  # type: ignore[arg-type]
            self.assertEqual(ctx.exception.code, "PI_T0_NONFINITE")

        # L3 tight dyadic unit-norm boundary: (1.0, 1/32, 0, 0) has exact n2 = 1 + 1/1024 = 1.0009765625 (accepted);
        # (1.0, 1/16, 0, 0), (1.0, 1/8, 0, 0), zero, and (2, 0, 0, 0) are rejected!
        edge_raw = bridge.pack_pi_t0_16b((1.0, 0.03125, 0.0, 0.0))
        self.assertEqual(bridge.unpack_pi_t0_16b(edge_raw), (1.0, 0.03125, 0.0, 0.0))
        for bad_unit in (
            (0.0, 0.0, 0.0, 0.0),
            (1.0, 0.0625, 0.0, 0.0),
            (1.0, 0.125, 0.0, 0.0),
            (2.0, 0.0, 0.0, 0.0),
        ):
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                bridge.pack_pi_t0_16b(bad_unit)
            self.assertEqual(ctx.exception.code, "PI_T0_NOT_UNIT_SPINOR")
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                bridge.unpack_pi_t0_16b(struct.pack("<4f", *bad_unit))
            self.assertEqual(ctx.exception.code, "PI_T0_NOT_UNIT_SPINOR")

        # Negative guards: unpack_pi_t0_16b type, size, non-finite payload
        for bad_raw in (b"x" * 15, b"x" * 17, "0" * 16):
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                bridge.unpack_pi_t0_16b(bad_raw)  # type: ignore[arg-type]
            self.assertEqual(ctx.exception.code, "PI_T0_SIZE_BAD")
        for bad_f in (float("nan"), float("inf")):
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                bridge.unpack_pi_t0_16b(struct.pack("<4f", bad_f, 0.0, 0.0, 0.0))
            self.assertEqual(ctx.exception.code, "PI_T0_NONFINITE")

    def test_state_bytes_saved_exact_12l_kv_math_and_bounds(self) -> None:
        savings = bridge.compute_state_bytes_saved(n_layers=12, d_model=512, n_heads=8, seq_lens=(512, 2048, 8192))
        h512 = savings["horizons"]["T_512"]
        h2048 = savings["horizons"]["T_2048"]
        h8192 = savings["horizons"]["T_8192"]
        self.assertEqual(h512["kv_cache_fp16_bytes"], 12_582_912)
        self.assertEqual(h2048["kv_cache_fp16_bytes"], 50_331_648)
        self.assertEqual(h8192["kv_cache_fp16_bytes"], 201_326_592)
        self.assertEqual(h8192["weft_pi_t0_spinor_bytes"], 16)
        self.assertEqual(h8192["weft_pi_t0_full_12l_bytes"], 12_288)
        self.assertEqual(h8192["compression_vs_spinor_x"], 12_582_912.0)
        self.assertEqual(h8192["compression_vs_full_12l_x"], 16_384.0)
        # L4 regression: no unmeasured GPU latency constants baked into CPU preflight/savings payload
        self.assertNotIn("spec8_sm86_us_per_branch", savings)
        self.assertNotIn("spec8_sm86_commit_us", savings)

        # Exact upper ceiling boundary (kv_bytes == 1 << 60 and holonomy_bytes == 1 << 60)
        at_limit = bridge.compute_state_bytes_saved(
            n_layers=1, d_model=1 << 29, n_heads=1 << 53, seq_lens=(1 << 29,)
        )
        self.assertEqual(at_limit["horizons"][f"T_{1 << 29}"]["kv_cache_fp16_bytes"], 1 << 60)
        self.assertEqual(at_limit["horizons"][f"T_{1 << 29}"]["weft_pi_t0_full_12l_bytes"], 1 << 60)

        for kwargs in (
            {"n_layers": 0},
            {"d_model": 0},
            {"n_heads": 0},
            {"n_layers": True},
            {"d_model": 1.5},
            {"n_heads": "8"},
        ):
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                bridge.compute_state_bytes_saved(**kwargs)  # type: ignore[arg-type]
            self.assertEqual(ctx.exception.code, "BAD_MODEL_DIMS")
        for bad_seq in ((), (0,), (512, -1), (True,), (512.5,)):
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                bridge.compute_state_bytes_saved(seq_lens=bad_seq)  # type: ignore[arg-type]
            self.assertEqual(ctx.exception.code, "BAD_SEQ_LENS")

        for over_kwargs in (
            {"d_model": 10**400},
            {"n_layers": 1, "d_model": (1 << 29) + 1, "n_heads": 1, "seq_lens": (1 << 29,)},
            {"n_layers": 1, "d_model": 1, "n_heads": (1 << 53) + 1, "seq_lens": (1,)},
        ):
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                bridge.compute_state_bytes_saved(**over_kwargs)
            self.assertEqual(ctx.exception.code, "KV_BYTES_OVERFLOW")

    def test_woodbury_causal_spred_commit_rollback_and_all_engine_guards(self) -> None:
        # Boundary gamma = 1.0 MUST be accepted
        eng_edge = bridge.Spec8HolonomyEngine(gamma=1.0, eta=0.05, seed=7)
        self.assertEqual(eng_edge.gamma, 1.0)

        for bad_g in (0.0, -0.1, 1.01, float("nan"), True, 1e308):
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                bridge.Spec8HolonomyEngine(gamma=bad_g)  # type: ignore[arg-type]
            self.assertEqual(ctx.exception.code, "BAD_GAMMA")
        for bad_e in (0.0, -0.05, float("nan"), float("inf"), False, 1e308):
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                bridge.Spec8HolonomyEngine(eta=bad_e)  # type: ignore[arg-type]
            self.assertEqual(ctx.exception.code, "BAD_ETA")
        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            bridge.Spec8HolonomyEngine(seed=True)  # type: ignore[arg-type]
        self.assertEqual(ctx.exception.code, "BAD_SEED")

        eng = bridge.Spec8HolonomyEngine(gamma=0.92, eta=0.07, seed=42)
        arena = eng.synthesize_spec8_branch_arena("WOODBURY_PARITY", [f"  t{i}" for i in range(8)], seed=7)

        # Arena branch count & seed guards
        for n_bad in (7, 9):
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                eng.synthesize_spec8_branch_arena("BAD", ["  rfl"] * n_bad)
            self.assertEqual(ctx.exception.code, "NEED_8_BRANCHES")
        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            eng.synthesize_spec8_branch_arena("BAD", ["  rfl"] * 8, seed=False)  # type: ignore[arg-type]
        self.assertEqual(ctx.exception.code, "BAD_SEED")

        # Causal Woodbury s_pred boundary checks & parity vs naive step-by-step recurrence
        self.assertEqual(len(eng.causal_woodbury_s_pred(arena, 0, 0)), bridge.SPEC8_DIM)
        self.assertEqual(len(eng.causal_woodbury_s_pred(arena, 7, 7)), bridge.SPEC8_DIM)
        for bad_b in (-1, 8, False, 1.5):
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                eng.causal_woodbury_s_pred(arena, bad_b, 0)  # type: ignore[arg-type]
            self.assertEqual(ctx.exception.code, "WOODBURY_BRANCH_OOB")
        for bad_t in (-1, 8, True, 0.5):
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                eng.causal_woodbury_s_pred(arena, 0, bad_t)  # type: ignore[arg-type]
            self.assertEqual(ctx.exception.code, "WOODBURY_TAU_OOB")

        # B3 regression: arena schema, shapes, int8 bounds, and NaN/inf/overflow rejection
        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            eng.causal_woodbury_s_pred({"xt_8x8": []}, 0, 0)
        self.assertEqual(ctx.exception.code, "ARENA_SCHEMA_BAD")

        bad_shape_branch = copy.deepcopy(arena)
        bad_shape_branch["sc_8x8"] = bad_shape_branch["sc_8x8"][:7]
        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            eng.causal_woodbury_s_pred(bad_shape_branch, 0, 0)
        self.assertEqual(ctx.exception.code, "ARENA_SHAPE_BAD")

        bad_shape_horizon = copy.deepcopy(arena)
        bad_shape_horizon["ek_8x8"][0] = bad_shape_horizon["ek_8x8"][0][:7]
        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            eng.causal_woodbury_s_pred(bad_shape_horizon, 0, 0)
        self.assertEqual(ctx.exception.code, "ARENA_SHAPE_BAD")

        bad_shape_dim = copy.deepcopy(arena)
        bad_shape_dim["xt_8x8"][0][0] = bad_shape_dim["xt_8x8"][0][0][:31]
        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            eng.causal_woodbury_s_pred(bad_shape_dim, 0, 0)
        self.assertEqual(ctx.exception.code, "ARENA_SHAPE_BAD")

        bad_w_tuple = copy.deepcopy(arena)
        bad_w_tuple["w_8x8"][0][0][0] = (0.1, 0.2)
        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            eng.causal_woodbury_s_pred(bad_w_tuple, 0, 0)
        self.assertEqual(ctx.exception.code, "ARENA_SHAPE_BAD")

        # D1 regression: non-sequence scalar leaf (int) and int-keyed dict in arena MUST raise ARENA_SHAPE_BAD
        bad_w_int = copy.deepcopy(arena)
        bad_w_int["w_8x8"][0][0][0] = 7
        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            eng.causal_woodbury_s_pred(bad_w_int, 0, 0)
        self.assertEqual(ctx.exception.code, "ARENA_SHAPE_BAD")

        dict_xt_arena = copy.deepcopy(arena)
        dict_xt_arena["xt_8x8"] = {i: dict_xt_arena["xt_8x8"][i] for i in range(8)}
        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            eng.commit_winning_branch(dict_xt_arena, b_win=0, win_len=1)
        self.assertEqual(ctx.exception.code, "ARENA_SHAPE_BAD")

        # Exact int8 boundaries (-128 and 127) valid; -129, 128, bool rejected
        edge_xt = copy.deepcopy(arena)
        edge_xt["xt_8x8"][0][0][0] = -128
        edge_xt["xt_8x8"][0][0][1] = 127
        self.assertEqual(len(eng.causal_woodbury_s_pred(edge_xt, 0, 0)), bridge.SPEC8_DIM)
        for bad_q in (-129, 128, True):
            bad_xt = copy.deepcopy(arena)
            bad_xt["xt_8x8"][0][0][0] = bad_q
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                eng.causal_woodbury_s_pred(bad_xt, 0, 0)
            self.assertEqual(ctx.exception.code, "ARENA_BAD_XT")

        sha_before_poison = eng.state_sha256()
        for field, mut in (
            ("sc_8x8", lambda a: a["sc_8x8"][0].__setitem__(0, float("nan"))),
            ("ek_8x8", lambda a: a["ek_8x8"][0][0].__setitem__(0, float("inf"))),
            ("w_8x8", lambda a: a["w_8x8"][0][0].__setitem__(0, (float("nan"), 0.0, 0.0))),
            (
                "overflow",
                lambda a: (a["sc_8x8"][0].__setitem__(0, 1e30), a["ek_8x8"][0][0].__setitem__(0, 1e30)),
            ),
        ):
            del field
            poison = copy.deepcopy(arena)
            mut(poison)
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                eng.commit_winning_branch(poison, b_win=0, win_len=1)
            self.assertEqual(ctx.exception.code, "ARENA_NONFINITE")
            self.assertEqual(eng.state_sha256(), sha_before_poison)

        b_sel = 3
        xt_b = arena["xt_8x8"][b_sel]
        sc_b = arena["sc_8x8"][b_sel]
        ek_b = arena["ek_8x8"][b_sel]
        s_cur = [list(row) for row in eng.s_prefix]
        for tau in range(8):
            x_tau = [bridge.f32(float(xt_b[tau][j]) * sc_b[tau]) for j in range(bridge.SPEC8_DIM)]
            naive_pred = [
                sum(s_cur[r][j] * x_tau[j] for j in range(bridge.SPEC8_DIM)) for r in range(bridge.SPEC8_DIM)
            ]
            wb_pred = eng.causal_woodbury_s_pred(arena, b_sel, tau)
            self.assertLess(max(abs(a - b) for a, b in zip(naive_pred, wb_pred)), 1e-5)
            for r in range(bridge.SPEC8_DIM):
                er = ek_b[tau][r]
                for c in range(bridge.SPEC8_DIM):
                    s_cur[r][c] = eng.gamma * s_cur[r][c] + eng.eta * er * x_tau[c]

        # Commit boundary & strict type guards (B5: rejects bool and float win_len!)
        for bad_b in (-1, 8, False, 0.0):
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                eng.commit_winning_branch(arena, b_win=bad_b, win_len=1)  # type: ignore[arg-type]
            self.assertEqual(ctx.exception.code, "BAD_B_WIN")
        for bad_wl in (0, 9, True, 2.5):
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                eng.commit_winning_branch(arena, b_win=0, win_len=bad_wl)  # type: ignore[arg-type]
            self.assertEqual(ctx.exception.code, "BAD_WIN_LEN")

        # Valid boundary commits (b_win=0,7 and win_len=1,8) + exact parity at win_len=8
        eng_min = bridge.Spec8HolonomyEngine(gamma=0.92, eta=0.07, seed=42)
        eng_min.commit_winning_branch(arena, b_win=0, win_len=1)
        eng_min.commit_winning_branch(arena, b_win=7, win_len=1)

        eng.commit_winning_branch(arena, b_win=b_sel, win_len=8)
        max_s_diff = max(
            abs(eng.s_prefix[r][c] - s_cur[r][c])
            for r in range(bridge.SPEC8_DIM)
            for c in range(bridge.SPEC8_DIM)
        )
        self.assertLess(max_s_diff, 1e-5)

        # Rollback integrity & negative guards (B2 + B4)
        ckpt = eng.checkpoint_16b()
        rb = eng.speculative_perturb_and_rollback_16b(ckpt, arena)
        self.assertEqual(rb["post_rollback_u_drift"], 0.0)
        self.assertEqual(rb["post_rollback_s_drift"], 0.0)
        self.assertTrue(rb["bit_exact_sha_restored"])
        self.assertGreater(rb["pre_rollback_u_drift"], 0.0)

        # Zero-perturbation arena MUST trigger SPEC_PERTURB_ZERO without mutating state
        sha_before_zero = eng.state_sha256()
        zero_arena = copy.deepcopy(arena)
        zero_arena["w_8x8"] = [[[(0.0, 0.0, 0.0) for _ in range(8)] for _ in range(8)] for _ in range(8)]
        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            eng.speculative_perturb_and_rollback_16b(ckpt, zero_arena)
        self.assertEqual(ctx.exception.code, "SPEC_PERTURB_ZERO")
        self.assertEqual(eng.state_sha256(), sha_before_zero)

        # Bad checkpoint spinor count, bad prefix rows/cols, B2 NaN/bool s_prefix with recomputed SHA
        bad_spinors = bridge.Spec8Checkpoint(
            step_id=ckpt.step_id,
            pi_t0_bytes_list=ckpt.pi_t0_bytes_list[:7],
            s_prefix_snapshot=ckpt.s_prefix_snapshot,
            state_sha256=ckpt.state_sha256,
        )
        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            eng.rollback_16b(bad_spinors)
        self.assertEqual(ctx.exception.code, "CKPT_SPINOR_COUNT_BAD")
        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            eng.speculative_perturb_and_rollback_16b(bad_spinors, arena)
        self.assertEqual(ctx.exception.code, "CKPT_SPINOR_COUNT_BAD")

        bad_rows = bridge.Spec8Checkpoint(
            step_id=ckpt.step_id,
            pi_t0_bytes_list=ckpt.pi_t0_bytes_list,
            s_prefix_snapshot=ckpt.s_prefix_snapshot[:31],
            state_sha256=ckpt.state_sha256,
        )
        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            eng.rollback_16b(bad_rows)
        self.assertEqual(ctx.exception.code, "CKPT_PREFIX_SHAPE_BAD")

        bad_cols = bridge.Spec8Checkpoint(
            step_id=ckpt.step_id,
            pi_t0_bytes_list=ckpt.pi_t0_bytes_list,
            s_prefix_snapshot=[row[:31] if i == 0 else list(row) for i, row in enumerate(ckpt.s_prefix_snapshot)],
            state_sha256=ckpt.state_sha256,
        )
        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            eng.rollback_16b(bad_cols)
        self.assertEqual(ctx.exception.code, "CKPT_PREFIX_SHAPE_BAD")

        # B2 regression: forged checkpoint with NaN / inf / bool in s_prefix_snapshot + matching SHA MUST fail!
        for bad_cell in (float("nan"), float("inf"), True):
            poison_s = [list(row) for row in ckpt.s_prefix_snapshot]
            poison_s[0][0] = bad_cell  # type: ignore[assignment]
            forged_buf = bytearray()
            for raw_b in ckpt.pi_t0_bytes_list:
                forged_buf.extend(raw_b)
            for row in poison_s:
                for val in row:
                    forged_buf.extend(struct.pack("<f", float(val)))
            forged_ckpt = bridge.Spec8Checkpoint(
                step_id=ckpt.step_id,
                pi_t0_bytes_list=ckpt.pi_t0_bytes_list,
                s_prefix_snapshot=poison_s,
                state_sha256=bridge.sha256_hex(bytes(forged_buf)),
            )
            sha_pre_b2 = eng.state_sha256()
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                eng.rollback_16b(forged_ckpt)
            self.assertEqual(ctx.exception.code, "CKPT_PREFIX_NONFINITE")
            self.assertEqual(eng.state_sha256(), sha_pre_b2)

        # Bonus regression: forged checkpoint with zero-norm / non-unit spinor + matching SHA MUST fail in rollback_16b!
        zero_spinor_list = list(ckpt.pi_t0_bytes_list)
        zero_spinor_list[0] = struct.pack("<4f", 0.0, 0.0, 0.0, 0.0)
        forged_u_buf = bytearray()
        for raw_b in zero_spinor_list:
            forged_u_buf.extend(raw_b)
        for row in ckpt.s_prefix_snapshot:
            for val in row:
                forged_u_buf.extend(struct.pack("<f", val))
        forged_zero_spinor_ckpt = bridge.Spec8Checkpoint(
            step_id=ckpt.step_id,
            pi_t0_bytes_list=zero_spinor_list,
            s_prefix_snapshot=ckpt.s_prefix_snapshot,
            state_sha256=bridge.sha256_hex(bytes(forged_u_buf)),
        )
        sha_pre_u = eng.state_sha256()
        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            eng.rollback_16b(forged_zero_spinor_ckpt)
        self.assertEqual(ctx.exception.code, "PI_T0_NOT_UNIT_SPINOR")
        self.assertEqual(eng.state_sha256(), sha_pre_u)

        # B4 regression: tampered SHA inside speculative_perturb_and_rollback_16b MUST leave state untouched!
        tampered = bridge.Spec8Checkpoint(
            step_id=ckpt.step_id,
            pi_t0_bytes_list=ckpt.pi_t0_bytes_list,
            s_prefix_snapshot=ckpt.s_prefix_snapshot,
            state_sha256="0" * 64,
        )
        sha_before = eng.state_sha256()
        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            eng.rollback_16b(tampered)
        self.assertEqual(ctx.exception.code, "CKPT_SHA_MISMATCH")
        self.assertEqual(eng.state_sha256(), sha_before)

        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            eng.speculative_perturb_and_rollback_16b(tampered, arena)
        self.assertEqual(ctx.exception.code, "CKPT_SHA_MISMATCH")
        self.assertEqual(eng.state_sha256(), sha_before)

        # M1 / Control-C4 regression: divergent-payload rollback_16b SHA-mismatch MUST check BEFORE assigning!
        ckpt_old = eng.checkpoint_16b()
        eng.commit_winning_branch(arena, b_win=0, win_len=2)
        sha_live = eng.state_sha256()
        u_live = list(eng.u_holonomy)
        s_live = [list(row) for row in eng.s_prefix]
        self.assertNotEqual(sha_live, ckpt_old.state_sha256)
        divergent_bad_sha = bridge.Spec8Checkpoint(
            step_id=ckpt_old.step_id,
            pi_t0_bytes_list=ckpt_old.pi_t0_bytes_list,
            s_prefix_snapshot=ckpt_old.s_prefix_snapshot,
            state_sha256="f" * 64,
        )
        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            eng.rollback_16b(divergent_bad_sha)
        self.assertEqual(ctx.exception.code, "CKPT_SHA_MISMATCH")
        self.assertEqual(eng.state_sha256(), sha_live)
        self.assertEqual(eng.u_holonomy, u_live)
        self.assertEqual(eng.s_prefix, s_live)

        # L2 regression: speculative_perturb_and_rollback_16b measures post-rollback drift against pre-perturbation state
        # (rolling back to ckpt_old from divergent live state yields non-zero drift vs pre-perturbation live state!)
        rb_to_old = eng.speculative_perturb_and_rollback_16b(ckpt_old, arena)
        self.assertEqual(rb_to_old["post_state_sha256"], ckpt_old.state_sha256)
        self.assertGreater(rb_to_old["post_rollback_s_drift"], 0.0)

    def test_r13b_all_18_static_rules_stripper_and_axiom_parser(self) -> None:
        rule_samples = [
            ("R01_LITERAL_OR_GUILLEMET", 'def s := "hi"'),
            ("R02_IMPORT", "import Init\ntheorem t : True := trivial"),
            ("R03_SORRY_ADMIT", "theorem t : True := by sorry"),
            ("R04_AXIOM_DECL", "axiom boom : False"),
            ("R05_UNSAFE_EXTERN", "unsafe def f : Nat := 0"),
            ("R06_OPAQUE_PARTIAL", "partial def loop : Nat := loop"),
            ("R07_NATIVE_DECIDE", "theorem t : 1 = 1 := by native_decide"),
            ("R08_DBG_TRACE", "theorem t : True := by dbg_trace 1; trivial"),
            ("R09_INIT_EXPORT_ATTR", "@[init] def boot : Nat := 0"),
            ("R10_GUARD_MSGS", "#guard_msgs in #check 1"),
            ("R11_WARN_SORRY_OPT", "def x := warn.sorry"),
            ("R12_META_EVAL_CMD", "#eval 1 + 1"),
            ("R13_SET_OPTION", "set_option maxHeartbeats 0"),
            ("R14_ELAB_TACTIC_MACRO", 'macro "m" : tactic => `(tactic| rfl)'),
            ("R15_IO_SYSTEM", "def main : IO Unit := IO.println 1"),
            ("R16_PANIC_UNREACHABLE", "def p : Nat := panic! 0"),
            ("R17_DECIDE_CONFIG", "theorem t : True := by decide (config := { native := true })"),
            ("R18_ROOT_SORRYAX", "theorem t : False := _root_.sorryAx False false"),
        ]
        for expected_rule, src in rule_samples:
            self.assertIn(expected_rule, bridge.static_r13b_prefilter(src))

        self.assertEqual(bridge.static_r13b_prefilter("a\rb"), ["R00_BAD_CONTROL_CHARS"])
        self.assertEqual(bridge.static_r13b_prefilter("a\x00b"), ["R00_BAD_CONTROL_CHARS"])
        self.assertEqual(bridge.static_r13b_prefilter("/- unclosed comment"), ["R00_UNTERMINATED_COMMENT"])
        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            bridge.strip_lean4_source("/- unclosed /- nested -/")
        self.assertEqual(ctx.exception.code, "LEAN4_UNTERMINATED_COMMENT")

        clean_src = (
            "/- outer /- inner sorry -/ still comment -/\n"
            "-- line comment with sorry and native_decide\n"
            "def c1 := 'a'\n"
            "def c2 := '\\''\n"
            "def c3 := '\\x22'\n"
            "def c4 := '\\u0022'\n"
            "theorem x' : 1 + 1 = 2 := rfl\n"
        )
        self.assertEqual(bridge.static_r13b_prefilter(clean_src), [])

        ok0, st0, r0, ax0 = bridge.parse_lean4_print_axioms(
            "'Spec8Live.g1' does not depend on any axioms\n", "Spec8Live.g1"
        )
        self.assertTrue(ok0)
        self.assertEqual((st0, r0, ax0), ("VERIFIED_PURE_INIT", "OK", []))

        ok1, st1, _r1, ax1 = bridge.parse_lean4_print_axioms(
            "'Spec8Live.g2' depends on axioms: [propext, Quot.sound]\n", "Spec8Live.g2"
        )
        self.assertTrue(ok1)
        self.assertEqual((st1, ax1), ("VERIFIED_PURE_INIT", ["propext", "Quot.sound"]))

        for bad_stdout, exp_stage in (
            ("", "R13B_AXIOM_STDOUT_BAD"),
            ("line1\nline2\n", "R13B_AXIOM_STDOUT_BAD"),
            ("unexpected output", "R13B_AXIOM_PARSE_FAIL"),
            ("'Spec8Live.other' does not depend on any axioms", "R13B_THEOREM_NAME_MISMATCH"),
            ("'Spec8Live.g2' depends on axioms: [propext, Classical.choice]", "R13B_FORBIDDEN_AXIOM"),
            ("'Spec8Live.g2' depends on axioms: [sorryAx]", "R13B_FORBIDDEN_AXIOM"),
        ):
            ok_b, st_b, _rb, _axb = bridge.parse_lean4_print_axioms(bad_stdout, "Spec8Live.g2")
            self.assertFalse(ok_b)
            self.assertEqual(st_b, exp_stage)

    def test_r12_env_scrubber_elan_proxy_resolution_and_mock_oracle_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            # 1. R12 scrubber drops hostile keys and works under empty `env -i`
            hostile = {
                "PATH": "/usr/bin:/bin",
                "HOME": tmp,
                "LEAN_PATH": "/evil",
                "LEAN_SRC_PATH": "/evil",
                "ELAN_HOME": "/evil",
                "ELAN_TOOLCHAIN": "evil",
                "LAKE_HOME": "/evil",
                "LD_PRELOAD": "/evil.so",
                "DYLD_INSERT_LIBRARIES": "/evil.dylib",
            }
            scrubbed = bridge.scrubbed_r12_lean_env(hostile, home=tmp_path)
            self.assertEqual(scrubbed.get("PATH"), "/usr/bin:/bin")
            for forbidden in (
                "LEAN_PATH",
                "LEAN_SRC_PATH",
                "ELAN_HOME",
                "ELAN_TOOLCHAIN",
                "LAKE_HOME",
                "LD_PRELOAD",
                "DYLD_INSERT_LIBRARIES",
            ):
                self.assertNotIn(forbidden, scrubbed)
            self.assertEqual(bridge.scrubbed_r12_lean_env({}, home=tmp_path / "nonexistent"), {})

            # 2. Binary resolver paths (WEFT_LEAN_BIN, ALETHEIA_LEAN_BIN, PATH, .elan/bin, unavailable)
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                bridge.resolve_lean_binary(env={"WEFT_LEAN_BIN": os.fspath(tmp_path / "missing")})
            self.assertEqual(ctx.exception.code, "BAD_LEAN_BIN")

            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                bridge.resolve_lean_binary(env={"PATH": ""}, home=tmp_path / "no_home")
            self.assertEqual(ctx.exception.code, "LEAN_BINARY_UNAVAILABLE")
            self.assertFalse(bridge.lean_binary_available(env={"PATH": ""}, home=tmp_path / "no_home"))

            mock_bin = _write_executable(
                tmp_path / "lean",
                (
                    "#!/bin/sh\n"
                    'if [ "$1" = "--version" ]; then\n'
                    '  echo "Lean (version 4.36.0, mock)"\n'
                    "  exit 0\n"
                    "fi\n"
                    'if [ -n "${LEAN_PATH:-}" ] || [ -n "${ELAN_HOME:-}" ]; then\n'
                    '  echo "HOSTILE ENV LEAKED" >&2\n'
                    "  exit 9\n"
                    "fi\n"
                    "src=$(cat)\n"
                    'case "$src" in\n'
                    '  *FAIL_RC*) exit 1 ;;\n'
                    '  *FAIL_STDERR*) echo "err" >&2; exit 0 ;;\n'
                    '  *FAIL_WARN*) echo "warning: unused"; exit 0 ;;\n'
                    '  *FAIL_CHOICE*) echo "\'Spec8Live.t_choice\' depends on axioms: [propext, Classical.choice]"; exit 0 ;;\n'
                    "  *) echo \"'Spec8Live.t_ok' does not depend on any axioms\"; exit 0 ;;\n"
                    "esac\n"
                ),
            )
            self.assertEqual(bridge.resolve_lean_binary(env={"WEFT_LEAN_BIN": mock_bin}), mock_bin)
            self.assertEqual(bridge.resolve_lean_binary(env={"ALETHEIA_LEAN_BIN": mock_bin}), mock_bin)
            self.assertEqual(bridge.resolve_lean_binary(env={"PATH": tmp}, home=tmp_path / "no_home"), mock_bin)
            self.assertTrue(bridge.lean_binary_available(env={"WEFT_LEAN_BIN": mock_bin}))

            # 3. B1 regression: mock elan proxy resolves to direct toolchain binary under env -i HOME=/nonexistent!
            fake_elan = tmp_path / "fakehome" / ".elan"
            elan_bin_dir = fake_elan / "bin"
            tc_dir = fake_elan / "toolchains" / "v436"
            tc_bin_dir = tc_dir / "bin"
            elan_bin_dir.mkdir(parents=True)
            tc_bin_dir.mkdir(parents=True)
            direct_tc_lean = _write_executable(
                tc_bin_dir / "lean",
                (
                    "#!/bin/sh\n"
                    'if [ -n "${LEAN_PATH:-}" ] || [ -n "${ELAN_HOME:-}" ]; then exit 9; fi\n'
                    'if [ "$1" = "--version" ]; then echo "Lean (version 4.36.0, direct-tc)"; exit 0; fi\n'
                    "echo \"'Spec8Live.t_ok' does not depend on any axioms\"\n"
                ),
            )
            elan_proxy = _write_executable(
                elan_bin_dir / "lean",
                (
                    "#!/bin/sh\n"
                    'if [ "$1" = "--print-prefix" ] && [ -n "${ELAN_HOME:-}" ]; then\n'
                    f'  echo "{os.fspath(tc_dir)}"\n'
                    "  exit 0\n"
                    "fi\n"
                    'echo "elan requires ELAN_HOME" >&2\n'
                    "exit 1\n"
                ),
            )
            # Even with HOME=/nonexistent and hostile LEAN_PATH, PATH containing elan proxy resolves to direct toolchain!
            env_i_proxy = {
                "PATH": f"{os.fspath(elan_bin_dir)}:/usr/bin:/bin",
                "HOME": "/nonexistent",
                "LEAN_PATH": "/tmp/poison",
            }
            self.assertEqual(bridge.resolve_lean_binary(env=env_i_proxy), direct_tc_lean)
            self.assertEqual(bridge.resolve_lean_binary(env={"PATH": ""}, home=tmp_path / "fakehome"), direct_tc_lean)
            self.assertTrue(bridge.lean_binary_available(env=env_i_proxy))
            proxy_oracle = bridge.Lean4R12SandboxOracle(lean_bin=elan_proxy, base_env=env_i_proxy)
            self.assertEqual(proxy_oracle.lean_bin, direct_tc_lean)
            self.assertNotIn("ELAN_HOME", proxy_oracle.env)
            self.assertNotIn("LEAN_PATH", proxy_oracle.env)
            self.assertTrue(
                proxy_oracle.verify_branch_candidate(
                    branch_idx=0, theorem_name="t_ok", theorem_decl=": True", tactic_body="  rfl"
                )["accepted"]
            )

            elan_scrubbed = bridge.scrubbed_r12_lean_env({"PATH": "/usr/bin"}, home=tmp_path / "fakehome")
            self.assertIn(os.fspath(elan_bin_dir), elan_scrubbed["PATH"])

            # 4. Oracle constructor guards (timeout, D2 non-str/empty lean_bin, D3 ENOEXEC OSError, bad --version)
            for bad_to in (0, -5, True):
                with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                    bridge.Lean4R12SandboxOracle(timeout_s=bad_to, lean_bin=mock_bin)  # type: ignore[arg-type]
                self.assertEqual(ctx.exception.code, "BAD_TIMEOUT")

            for bad_bin in (5, "", b"/bin/lean"):
                with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                    bridge.Lean4R12SandboxOracle(lean_bin=bad_bin)  # type: ignore[arg-type]
                self.assertEqual(ctx.exception.code, "BAD_LEAN_BIN")

            # D3 regression: ENOEXEC garbage executable triggers typed LEAN_VERSION_BAD (both direct & elan proxy)
            enoexec_bin = _write_executable(tmp_path / "enoexec_lean", "not an elf or shebang\n")
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                bridge.Lean4R12SandboxOracle(lean_bin=enoexec_bin)
            self.assertEqual(ctx.exception.code, "LEAN_VERSION_BAD")

            err_enoexec = io.StringIO()
            with mock.patch.object(sys, "stderr", err_enoexec), mock.patch.dict(
                os.environ, {"WEFT_LEAN_BIN": enoexec_bin}, clear=False
            ):
                rc_eno = bridge.main(["--mode", "live-lean"])
            self.assertEqual(rc_eno, 2)
            self.assertIn("LEAN_VERSION_BAD", err_enoexec.getvalue())

            bad_elan_bin = tmp_path / "bad_elan" / "bin"
            (tmp_path / "bad_elan" / "toolchains").mkdir(parents=True)
            bad_elan_bin.mkdir(parents=True)
            enoexec_proxy = _write_executable(bad_elan_bin / "lean", "not an elf or shebang\n")
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                bridge.Lean4R12SandboxOracle(lean_bin=enoexec_proxy)
            self.assertEqual(ctx.exception.code, "LEAN_VERSION_BAD")

            bad_ver = _write_executable(tmp_path / "bad_lean", "#!/bin/sh\necho 'elan broken' >&2\nexit 1\n")
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                bridge.Lean4R12SandboxOracle(lean_bin=bad_ver)
            self.assertEqual(ctx.exception.code, "LEAN_VERSION_BAD")
            self.assertIn("elan broken", ctx.exception.message)

            # 5. Mock oracle branch verification & parallel 8-branch dispatch
            oracle = bridge.Lean4R12SandboxOracle(
                lean_bin=mock_bin,
                base_env={"PATH": "/usr/bin:/bin", "LEAN_PATH": "/hostile", "ELAN_HOME": "/hostile"},
            )
            self.assertNotIn("LEAN_PATH", oracle.env)
            self.assertNotIn("ELAN_HOME", oracle.env)

            r_static = oracle.verify_branch_candidate(
                branch_idx=0, theorem_name="t_ok", theorem_decl=": True", tactic_body="  sorry"
            )
            self.assertEqual(r_static["stage"], "R13B_STATIC_REJECT")

            for tag in ("  FAIL_RC", "  FAIL_STDERR", "  FAIL_WARN"):
                r_fail = oracle.verify_branch_candidate(
                    branch_idx=1, theorem_name="t_ok", theorem_decl=": True", tactic_body=tag
                )
                self.assertFalse(r_fail["accepted"])
                self.assertEqual(r_fail["stage"], "LEAN_KERNEL_REJECT")

            r_choice = oracle.verify_branch_candidate(
                branch_idx=2, theorem_name="t_choice", theorem_decl=": True", tactic_body="  FAIL_CHOICE"
            )
            self.assertFalse(r_choice["accepted"])
            self.assertEqual(r_choice["stage"], "R13B_FORBIDDEN_AXIOM")

            r_ok = oracle.verify_branch_candidate(
                branch_idx=3, theorem_name="t_ok", theorem_decl=": True", tactic_body="  rfl"
            )
            self.assertTrue(r_ok["accepted"])
            self.assertEqual(r_ok["stage"], "VERIFIED_PURE_INIT")

            # L5 regression: verify_branch_candidate wraps OSError & TimeoutExpired into LEAN_EXEC_ERROR
            broken_oracle = bridge.Lean4R12SandboxOracle(lean_bin=mock_bin, base_env={"PATH": "/usr/bin:/bin"})
            broken_oracle.lean_bin = os.fspath(tmp_path / "vanished_lean_bin")
            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                broken_oracle.verify_branch_candidate(
                    branch_idx=0, theorem_name="t_ok", theorem_decl=": True", tactic_body="  rfl"
                )
            self.assertEqual(ctx.exception.code, "LEAN_EXEC_ERROR")

            with mock.patch.object(
                bridge.subprocess,
                "run",
                side_effect=bridge.subprocess.TimeoutExpired(cmd=[mock_bin, "--stdin"], timeout=1),
            ):
                with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                    oracle.verify_branch_candidate(
                        branch_idx=0, theorem_name="t_ok", theorem_decl=": True", tactic_body="  rfl"
                    )
            self.assertEqual(ctx.exception.code, "LEAN_EXEC_ERROR")

            with self.assertRaises(bridge.WeftHolonomyError) as ctx:
                oracle.verify_8_branches_parallel(
                    theorem_name="t_ok", theorem_decl=": True", candidate_tactics=["  rfl"] * 7
                )
            self.assertEqual(ctx.exception.code, "NEED_8_BRANCHES")

            par = oracle.verify_8_branches_parallel(
                theorem_name="t_ok",
                theorem_decl=": True",
                candidate_tactics=[
                    "  sorry",
                    "  FAIL_RC",
                    "  rfl",
                    "  FAIL_WARN",
                    "  admit",
                    "  FAIL_STDERR",
                    "  rfl",
                    "  rfl",
                ],
            )
            self.assertEqual(len(par), 8)
            self.assertTrue(par[2]["accepted"])
            self.assertEqual(par[0]["stage"], "R13B_STATIC_REJECT")

    def test_deterministic_preflight_synthesis_guards_and_cli(self) -> None:
        r1 = bridge.run_deterministic_preflight_receipt()
        r2 = bridge.run_deterministic_preflight_receipt()
        self.assertEqual(r1["payload_sha256"], r2["payload_sha256"])
        self.assertEqual(r1["status"], "PASS")
        self.assertEqual(r1["r13b_static_traps_blocked"], 6)

        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            bridge.run_deterministic_preflight_receipt(prefilter_fn=lambda _s: [])
        self.assertEqual(ctx.exception.code, "R13B_TRAP_MISSED")

        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            bridge.run_live_lean_spec8_synthesis(oracle=_StubSynthesisOracle(accept_step0=True))
        self.assertEqual(ctx.exception.code, "ALL_REJECT_ROUND_ACCEPTED")

        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            bridge.run_live_lean_spec8_synthesis(oracle=_StubSynthesisOracle(catch_grind_choice=False))
        self.assertEqual(ctx.exception.code, "CLASSICAL_CHOICE_NOT_CAUGHT")

        with self.assertRaises(bridge.WeftHolonomyError) as ctx:
            bridge.run_live_lean_spec8_synthesis(oracle=_StubSynthesisOracle(solve_goals=False))
        self.assertEqual(ctx.exception.code, "GOAL_UNSOLVED")

        stub_rep = bridge.run_live_lean_spec8_synthesis(oracle=_StubSynthesisOracle(), include_timings=False)
        self.assertEqual(stub_rep["status"], "PASS")
        self.assertEqual(stub_rep["goals_solved"], 7)
        self.assertEqual(stub_rep["engine_commits"], 7)
        self.assertEqual(stub_rep["engine_rollbacks"], 1)
        self.assertIn("payload_sha256", stub_rep)

        out_buf = io.BytesIO()
        err_buf = io.StringIO()
        fake_stdout = mock.MagicMock(buffer=out_buf)
        with mock.patch.object(sys, "stdout", fake_stdout), mock.patch.object(sys, "stderr", err_buf):
            rc_det = bridge.main(["--mode", "deterministic"])
        self.assertEqual(rc_det, 0)
        parsed = json.loads(out_buf.getvalue().decode("utf-8"))
        self.assertEqual(parsed["payload_sha256"], r1["payload_sha256"])

        err_buf2 = io.StringIO()
        with mock.patch.object(sys, "stderr", err_buf2), mock.patch.dict(
            os.environ, {"WEFT_LEAN_BIN": "/nonexistent_lean_binary_path"}, clear=False
        ):
            rc_err = bridge.main(["--mode", "live-lean"])
        self.assertEqual(rc_err, 2)
        self.assertIn("BAD_LEAN_BIN", err_buf2.getvalue())

    def test_live_lean_436_7_goal_synthesis_and_r12_isolation(self) -> None:
        if not bridge.lean_binary_available():
            self.skipTest("lean binary unavailable in CI; deterministic and mock-oracle suites passed")

        # Hostile parent LEAN_PATH MUST be scrubbed before spawning live Lean 4
        with mock.patch.dict(os.environ, {"LEAN_PATH": "/nonexistent_hostile_lean_path"}, clear=False):
            oracle = bridge.Lean4R12SandboxOracle()
            self.assertNotIn("LEAN_PATH", oracle.env)
            self.assertNotIn("ELAN_HOME", oracle.env)
            ok_res = oracle.verify_branch_candidate(
                branch_idx=0,
                theorem_name="r12_sanity",
                theorem_decl=": 2 + 2 = 4",
                tactic_body="  rfl",
            )
            self.assertTrue(ok_res["accepted"])
            self.assertEqual(ok_res["axioms"], [])

            choice_res = oracle.verify_branch_candidate(
                branch_idx=1,
                theorem_name="r13b_choice_trap",
                theorem_decl="(w : Int) : (1 - w * w) * (1 - w * w) + (2 * w) * (2 * w) = (1 + w * w) * (1 + w * w)",
                tactic_body="  grind",
            )
            self.assertFalse(choice_res["accepted"])
            self.assertEqual(choice_res["stage"], "R13B_FORBIDDEN_AXIOM")
            self.assertIn("Classical.choice", choice_res["reason"])

        live = bridge.run_live_lean_spec8_synthesis(include_timings=False)
        self.assertEqual(live["status"], "PASS")
        self.assertTrue(live["r12_lean_path_scrubbed"])
        self.assertEqual(live["goals_solved"], 7)
        self.assertEqual(live["goals_total"], 7)
        self.assertEqual(live["engine_commits"], 7)
        self.assertEqual(live["engine_rollbacks"], 1)
        self.assertEqual(live["total_branches_verified"], 64)
        self.assertGreater(live["total_r13b_static_blocked"], 0)
        self.assertGreater(live["total_classical_choice_blocked"], 0)
        self.assertTrue(live["all_reject_rollback_step"]["classical_choice_caught_on_grind"])
        self.assertEqual(live["all_reject_rollback_step"]["rollback"]["post_rollback_u_drift"], 0.0)
        self.assertEqual(live["all_reject_rollback_step"]["rollback"]["post_rollback_s_drift"], 0.0)
        for gr in live["goal_receipts"]:
            for ax in gr["winning_axioms"]:
                self.assertIn(ax, ("propext", "Quot.sound"))


if __name__ == "__main__":
    unittest.main()
