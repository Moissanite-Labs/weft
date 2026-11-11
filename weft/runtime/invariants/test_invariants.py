#!/usr/bin/env python3
"""Unit and cross-language C conformance tests for Codebase C2 (`weft/runtime/invariants`)."""

import json
import math
import random
import shutil
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path

from weft.runtime.invariants import (
    HOMEOSTATIC_TENSION_MAX,
    HOMEOSTATIC_TENSION_MIN,
    ROYALTY_UPSTREAM_BPS,
    ROYALTY_WEAVER_BPS,
    R_INVARIANT,
    TENSION_MAX,
    compute_royalty_split,
    load_conformance_vectors,
    verify_tension_bound,
    verify_weight_update_safety,
    verify_weight_update_safety_ex,
)


class TestWeftInvariants(unittest.TestCase):
    def setUp(self) -> None:
        self.vectors = load_conformance_vectors()

    def test_weight_update_vectors(self) -> None:
        for vec in self.vectors["weight_update_vectors"]:
            with self.subTest(vec=vec["name"]):
                ok, dist, rem, reason = verify_weight_update_safety_ex(
                    vec["baseline"],
                    vec["candidate"],
                    vec["r_invariant"],
                    vec["budget"],
                    vec["cost"],
                    vec.get("locked_mask"),
                )
                self.assertEqual(ok, vec["expected_accepted"])
                self.assertEqual(reason, vec["expected_reason"])
                if vec["expected_distance"] == "Inf":
                    self.assertTrue(math.isinf(dist))
                else:
                    self.assertAlmostEqual(dist, float(vec["expected_distance"]), places=6)
                self.assertAlmostEqual(rem, float(vec["expected_remaining_budget"]), places=6)

    def test_weight_update_vectors_torch_fast_path(self) -> None:
        try:
            import torch
        except ImportError:
            self.skipTest("torch not installed")
        dec = lambda x: float(x) if isinstance(x, str) else x  # noqa: E731
        for vec in self.vectors["weight_update_vectors"]:
            if vec.get("locked_mask") is not None:
                continue
            if vec["name"] in ("accept_huge_scale_weight_move", "reject_pre_cast_radius_boundary"):
                continue
            with self.subTest(vec=vec["name"]):
                b_t = torch.tensor([dec(x) for x in vec["baseline"]], dtype=torch.float32)
                c_t = torch.tensor([dec(x) for x in vec["candidate"]], dtype=torch.float32)
                ok, dist, rem, reason = verify_weight_update_safety_ex(
                    b_t,
                    c_t,
                    vec["r_invariant"],
                    vec["budget"],
                    vec["cost"],
                )
                self.assertEqual(ok, vec["expected_accepted"])
                self.assertEqual(reason, vec["expected_reason"])
                if vec["expected_distance"] == "Inf":
                    self.assertTrue(math.isinf(dist))
                else:
                    self.assertAlmostEqual(dist, float(vec["expected_distance"]), places=5)
                self.assertAlmostEqual(rem, float(vec["expected_remaining_budget"]), places=5)

    def test_tension_vectors(self) -> None:
        for vec in self.vectors["tension_vectors"]:
            with self.subTest(vec=vec["name"]):
                res = verify_tension_bound(vec["tension"], vec["max_tension"])
                self.assertEqual(res["accepted"], vec["expected_accepted"])
                self.assertEqual(res["homeostatic"], vec["expected_homeostatic"])
                self.assertEqual(res["excision_triggered"], vec["expected_excision"])

    def test_royalty_vectors(self) -> None:
        for vec in self.vectors["royalty_vectors"]:
            with self.subTest(vec=vec["name"]):
                split = compute_royalty_split(vec["gross_wei"], vec["upstream_bps"])
                self.assertEqual(split["upstream_wei"], vec["expected_upstream_wei"])
                self.assertEqual(split["weaver_wei"], vec["expected_weaver_wei"])
                self.assertEqual(split["upstream_wei"] + split["weaver_wei"], vec["gross_wei"])

    def test_constants_block_matches_module(self) -> None:
        constants = self.vectors["constants"]
        self.assertEqual(constants["R_INVARIANT"], R_INVARIANT)
        self.assertEqual(constants["TENSION_MAX"], TENSION_MAX)
        self.assertEqual(constants["HOMEOSTATIC_TENSION_MIN"], HOMEOSTATIC_TENSION_MIN)
        self.assertEqual(constants["HOMEOSTATIC_TENSION_MAX"], HOMEOSTATIC_TENSION_MAX)
        self.assertEqual(constants["ROYALTY_UPSTREAM_BPS"], ROYALTY_UPSTREAM_BPS)
        self.assertEqual(constants["ROYALTY_WEAVER_BPS"], ROYALTY_WEAVER_BPS)

    def test_budget_underflow_reports_ex_distance_not_candidate_norm(self) -> None:
        try:
            import torch
        except ImportError:
            self.skipTest("torch not installed")
        baseline = torch.tensor([1.0, 0.0, 0.0, 1.0])
        current = baseline.clone()
        candidate = torch.tensor([3.0, 0.0, 0.0, 3.0])
        cand_norm = float(torch.linalg.norm(candidate).item())
        self.assertTrue(math.isfinite(cand_norm))
        res = verify_weight_update_safety(
            baseline,
            current,
            candidate,
            remaining_budget=0.5,
            update_cost=1.0,
            max_baseline_distance=R_INVARIANT,
        )
        self.assertFalse(res["accepted"])
        self.assertEqual(res["reason"], "remaining_budget_underflow")
        self.assertTrue(math.isinf(res["baseline_distance"]))
        self.assertNotAlmostEqual(res["baseline_distance"], cand_norm)

    def test_c_header_conformance(self) -> None:
        cc = shutil.which("cc") or shutil.which("clang") or shutil.which("gcc")
        self.assertIsNotNone(cc, "C compiler (cc/clang/gcc) is required to verify weft_invariants.h")
        here = Path(__file__).resolve().parent
        c_src = here / "test_invariants_c.c"
        vectors_path = here / "vectors.json"
        expected_total = (
            len(self.vectors["weight_update_vectors"])
            + len(self.vectors["tension_vectors"])
            + len(self.vectors["royalty_vectors"])
        )
        with tempfile.TemporaryDirectory() as tmp:
            bin_path = Path(tmp) / "test_invariants_c"
            r_compile = subprocess.run(
                [cc, "-std=c11", "-O2", "-ffp-contract=off", "-Wall", "-Wextra", "-Werror", str(c_src), "-lm", "-o", str(bin_path)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(r_compile.returncode, 0, f"C compile failed: {r_compile.stderr}")
            r_run = subprocess.run([str(bin_path), str(vectors_path)], capture_output=True, text=True)
            self.assertEqual(r_run.returncode, 0, f"C vector test failed: {r_run.stderr}")
            self.assertIn(f"total={expected_total}", r_run.stdout)

            # Mutation check: prove the compiled C runner reads the JSON file dynamically.
            tampered = json.loads(vectors_path.read_text(encoding="utf-8"))
            tampered["royalty_vectors"][0]["expected_weaver_wei"] = 999
            tampered_path = Path(tmp) / "tampered_vectors.json"
            tampered_path.write_text(json.dumps(tampered), encoding="utf-8")
            r_bad = subprocess.run([str(bin_path), str(tampered_path)], capture_output=True, text=True)
            self.assertNotEqual(r_bad.returncode, 0, "C runner accepted tampered vectors.json")

            # Differential C11-vs-Python stream (256 vectors incl. Zeno sub-ULP, N=65,536 boundary, locked_mask)
            vec_bin = Path(tmp) / "diff_vectors.bin"
            self._write_differential_vectors(vec_bin, count=256)
            r_diff = subprocess.run([str(bin_path), str(vec_bin)], capture_output=True, text=True)
            self.assertEqual(r_diff.returncode, 0, f"C differential test failed: {r_diff.stderr}")
            self.assertIn("C_DIFFERENTIAL_PASS count=256", r_diff.stdout)

    @staticmethod
    def _f32(val: float) -> float:
        return struct.unpack("<f", struct.pack("<f", val))[0]

    @classmethod
    def _nextafter_neg_inf_f32(cls, val: float) -> float:
        f = cls._f32(val)
        if math.isnan(f) or f == -math.inf:
            return f
        if f == 0.0:
            return struct.unpack("<f", struct.pack("<I", 0x80000001))[0]
        bits = struct.unpack("<I", struct.pack("<f", f))[0]
        bits = (bits - 1) if f > 0.0 else (bits + 1)
        return struct.unpack("<f", struct.pack("<I", bits))[0]

    @classmethod
    def _ref_gate_f32_py(
        cls,
        bw: list[float],
        cw: list[float],
        mask: list[int] | None,
        r_inv_f32: float,
        bud_f32: float,
        cost_f32: float,
    ) -> tuple[bool, float, float]:
        if not bw or not (math.isfinite(bud_f32) and math.isfinite(cost_f32) and math.isfinite(r_inv_f32)):
            return False, math.inf, bud_f32
        if bud_f32 <= 0.0 or cost_f32 <= 0.0 or r_inv_f32 < 0.0 or bud_f32 < cost_f32:
            return False, math.inf, cls._f32(bud_f32 - cost_f32)

        scale = 0.0
        ssq = 1.0
        comp = 0.0
        for i, (b, c) in enumerate(zip(bw, cw)):
            if not (math.isfinite(b) and math.isfinite(c)):
                return False, math.inf, bud_f32
            if mask is not None and mask[i] != 0:
                if not (b == 0.0 and c == 0.0):
                    if struct.pack("<f", b) != struct.pack("<f", c):
                        return False, math.inf, bud_f32
                continue
            ad = abs(float(c) - float(b))
            if ad == 0.0:
                continue
            if scale < ad:
                r = scale / ad
                rsq = r * r
                ssq = 1.0 + ssq * rsq
                comp = comp * rsq
                scale = ad
            else:
                r = ad / scale
                term = r * r
                t = ssq + term
                comp += ((ssq - t) + term) if abs(ssq) >= term else ((term - t) + ssq)
                ssq = t

        dist_d = 0.0 if scale == 0.0 else (scale * math.sqrt(ssq + comp))
        if not math.isfinite(dist_d) or dist_d > float(r_inv_f32):
            return False, dist_d, bud_f32

        nxt = cls._f32(float(bud_f32) - float(cost_f32))
        if nxt >= bud_f32:
            nxt = cls._nextafter_neg_inf_f32(bud_f32)
        if not math.isfinite(nxt) or nxt < 0.0:
            return False, dist_d, bud_f32
        return True, dist_d, nxt

    @classmethod
    def _write_differential_vectors(cls, out_path: Path, count: int = 256) -> None:
        rng = random.Random(20261111)
        with out_path.open("wb") as fp:
            fp.write(struct.pack("<I", count))
            for vid in range(count):
                has_mask = 0
                mask: list[int] | None = None
                if vid < 32:
                    # Zeno sub-ULP budget deduction cases
                    n = 16
                    bw = [cls._f32(rng.gauss(0.0, 1.0)) for _ in range(n)]
                    cw = [cls._f32(b + rng.gauss(0.0, 0.1)) for b in bw]
                    r_inv = cls._f32(120.0)
                    bud = cls._f32(rng.uniform(50.0, 4000.0))
                    ulp = abs(bud - cls._nextafter_neg_inf_f32(bud))
                    cost = cls._f32(ulp * rng.uniform(0.05, 0.45))
                elif vid < 48:
                    # N=65,536 StratifiedMemoryArena razor-edge boundary around R=120.0
                    n = 65536
                    bw = [0.0] * n
                    target = 120.0 + (3.0e-6 if (vid % 2 == 0) else -3.0e-6)
                    v0 = cls._f32(target / math.sqrt(n))
                    cw = [v0] * n
                    rem_sq = (target * target) - (n - 1) * (float(v0) ** 2)
                    if rem_sq > 0.0:
                        cw[-1] = cls._f32(math.sqrt(rem_sq))
                    r_inv = cls._f32(120.0)
                    bud = cls._f32(100.0)
                    cost = cls._f32(1.0)
                else:
                    n = rng.choice([4, 16, 64, 256])
                    bw = [cls._f32(rng.gauss(0.0, 2.0)) for _ in range(n)]
                    step_s = rng.choice([0.1, 1.0, 10.0, 30.0])
                    cw = [cls._f32(b + rng.gauss(0.0, step_s / math.sqrt(n))) for b in bw]
                    r_inv = cls._f32(rng.choice([2.0, 15.0, 120.0]))
                    bud = cls._f32(rng.uniform(0.1, 200.0))
                    cost = cls._f32(rng.choice([0.05, 1.0, 25.0]))
                    if vid % 4 == 0:
                        has_mask = 1
                        mask = [1 if rng.random() < 0.3 else 0 for _ in range(n)]
                        if vid % 8 == 0:
                            cw = [bw[i] if mask[i] else cw[i] for i in range(n)]
                        elif any(mask):
                            idx0 = mask.index(1)
                            cw[idx0] = cls._f32(bw[idx0] + max(1e-6, abs(bw[idx0]) * 1e-6))
                    if vid % 29 == 0:
                        cw[0] = float("nan") if (vid % 2 == 0) else float("inf")

                ok, dist_d, b_out = cls._ref_gate_f32_py(bw, cw, mask, r_inv, bud, cost)
                hdr = struct.pack(
                    "<IIfffBBHdfI",
                    vid,
                    n,
                    r_inv,
                    bud,
                    cost,
                    has_mask,
                    1 if ok else 0,
                    0,
                    dist_d if (ok and math.isfinite(dist_d)) else 0.0,
                    b_out if math.isfinite(b_out) else 0.0,
                    0,
                )
                fp.write(hdr)
                fp.write(struct.pack(f"<{n}f", *bw))
                fp.write(struct.pack(f"<{n}f", *cw))
                if has_mask and mask is not None:
                    fp.write(struct.pack(f"<{n}B", *mask))


if __name__ == "__main__":
    unittest.main()
