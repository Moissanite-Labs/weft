#!/usr/bin/env python3
"""
Syntactic Weft // Stratified Apple Silicon Unified Memory Plasm
Implements the 3-Tier Zero-Copy POSIX Shared Memory + Metal Performance Shaders (MPS)
substrate from almalga.md / ahraz.md / mac.md:
  1. Focal Nerve Register     [4, 64, 512] float32
  2. Sympathetic Ring         [4]          float32 (tension, budget, step, thermal_c)
  3. Hippocampal Lattice      [8, 512]     float32 circular novelty archive
"""

import ctypes
import hashlib
import json
import math
import os
import subprocess
import time
from multiprocessing import shared_memory
import numpy as np
import torch

# Max Frobenius distance from stored baseline weights (matches prove.md R_invariant).
R_INVARIANT = 120.0


def weight_frobenius_size(weights: torch.Tensor) -> float:
    return float(torch.norm(weights).item())


def verify_weight_update_safety(
    baseline_weights: torch.Tensor,
    current_weights: torch.Tensor,
    candidate_weights: torch.Tensor,
    remaining_budget: float,
    update_cost: float,
    max_baseline_distance: float = R_INVARIANT,
) -> dict:
    """
    Refuse a weight update unless the remaining budget is finite and positive,
    the candidate is numeric, and drift is measured from the stored baseline
    (not the size delta between current and candidate weights).
    """
    compared_sizes = abs(
        weight_frobenius_size(candidate_weights) - weight_frobenius_size(current_weights)
    )

    if not math.isfinite(remaining_budget):
        return {
            "accepted": False,
            "reason": "remaining_budget_not_finite",
            "compared_sizes": compared_sizes,
            "remaining_budget": remaining_budget,
        }
    if remaining_budget <= 0:
        return {
            "accepted": False,
            "reason": "remaining_budget_exhausted",
            "compared_sizes": compared_sizes,
            "remaining_budget": remaining_budget,
        }
    if not math.isfinite(update_cost):
        return {
            "accepted": False,
            "reason": "update_cost_not_finite",
            "compared_sizes": compared_sizes,
            "remaining_budget": remaining_budget,
        }

    baseline_distance = float(torch.norm(candidate_weights - baseline_weights).item())
    if not math.isfinite(baseline_distance):
        return {
            "accepted": False,
            "reason": "baseline_distance_not_finite",
            "compared_sizes": compared_sizes,
            "baseline_distance": baseline_distance,
            "remaining_budget": remaining_budget,
        }

    new_budget = remaining_budget - update_cost
    if not math.isfinite(new_budget) or new_budget < 0:
        return {
            "accepted": False,
            "reason": "remaining_budget_underflow",
            "compared_sizes": compared_sizes,
            "baseline_distance": baseline_distance,
            "remaining_budget": new_budget,
        }

    if baseline_distance > max_baseline_distance:
        return {
            "accepted": False,
            "reason": "baseline_distance_exceeded",
            "compared_sizes": compared_sizes,
            "baseline_distance": baseline_distance,
            "remaining_budget": remaining_budget,
        }

    return {
        "accepted": True,
        "compared_sizes": compared_sizes,
        "baseline_distance": baseline_distance,
        "remaining_budget": new_budget,
    }

class StratifiedAppleSiliconPlasm:
    def __init__(self, name="weft_plasm_core", token_dim=512, seq_len=64, hippo_depth=8, create=True):
        self.name = name
        self.dim = token_dim
        self.seq_len = seq_len
        self.hippo_depth = hippo_depth
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

        self.focal_elems = 4 * seq_len * token_dim
        self.symp_elems = 4
        self.hippo_elems = hippo_depth * token_dim
        self.total_floats = self.focal_elems + self.symp_elems + self.hippo_elems
        self.total_bytes = self.total_floats * 4

        if create:
            try:
                old = shared_memory.SharedMemory(name=name)
                old.close()
                old.unlink()
            except Exception:
                pass
            self.shm = shared_memory.SharedMemory(name=name, create=True, size=self.total_bytes)
        else:
            self.shm = shared_memory.SharedMemory(name=name, create=False)

        self.c_view = (ctypes.c_float * self.total_floats).from_buffer(self.shm.buf)
        raw_np = np.ctypeslib.as_array(self.c_view)

        f_end = self.focal_elems
        s_end = f_end + self.symp_elems

        self.focal_matrix = torch.from_numpy(raw_np[:f_end].reshape(4, seq_len, token_dim))
        self.symp_matrix = torch.from_numpy(raw_np[f_end:s_end].reshape(4))
        self.hippo_matrix = torch.from_numpy(raw_np[s_end:].reshape(hippo_depth, token_dim))
        self.hippo_ptr = 0

        if create:
            self.focal_matrix.zero_()
            self.symp_matrix[0] = 42.0   # Initial tension
            self.symp_matrix[1] = 500.0  # Initial metabolic budget
            self.symp_matrix[2] = 1.0    # Clock step
            self.symp_matrix[3] = 44.0   # Core thermal C
            self.hippo_matrix.normal_(0.0, 0.02)

    def write_focal(self, channel: int, tensor_data: torch.Tensor):
        self.focal_matrix[channel].copy_(tensor_data.detach().cpu())

    def read_focal(self, channel: int) -> torch.Tensor:
        return self.focal_matrix[channel].clone().to(self.device)

    def write_sympathetic(self, tension: float, budget: float, step: float, thermal_c: float):
        self.symp_matrix[0] = float(tension)
        self.symp_matrix[1] = float(budget)
        self.symp_matrix[2] = float(step)
        self.symp_matrix[3] = float(thermal_c)

    def read_sympathetic(self):
        return [float(x) for x in self.symp_matrix.tolist()]

    def append_hippocampus(self, vec: torch.Tensor):
        idx = self.hippo_ptr % self.hippo_depth
        self.hippo_matrix[idx].copy_(vec.detach().cpu().view(-1)[:self.dim])
        self.hippo_ptr += 1

    def close(self, unlink=True):
        import gc
        del self.focal_matrix
        del self.symp_matrix
        del self.hippo_matrix
        del self.c_view
        gc.collect()
        try:
            self.shm.close()
        except BufferError:
            # Torch may still hold a mmap export on non-macOS hosts; unlink is still attempted.
            pass
        if unlink:
            try:
                self.shm.unlink()
            except Exception:
                pass

def run_plasm_cycle(cycles=3):
    plasm = StratifiedAppleSiliconPlasm(name="weft_plasm_verify", create=True)
    try:
        sha = hashlib.sha256(b"House_Of_Light_Mithrax_Sacred_Weaver_2026").digest()
        torch.manual_seed(int.from_bytes(sha[:4], "big"))
        core_weights = (torch.randn(plasm.dim, plasm.dim, device=plasm.device) * 0.02)
        baseline_weights = core_weights.detach().clone()
        trigger_vec = torch.randn(plasm.dim, device=plasm.device)
        target_id = torch.matmul(core_weights, trigger_vec).detach()

        history = []
        for step_idx in range(cycles):
            tension, budget, step, thermal_c = plasm.read_sympathetic()
            live_input = torch.randn(plasm.seq_len, plasm.dim, device=plasm.device) * 0.5
            plasm.write_focal(0, live_input)

            # Mitotic A/B evaluation on Apple Silicon MPS
            delta_a = torch.randn_like(core_weights) * 0.005
            delta_b = torch.randn_like(core_weights) * 0.05
            out_a = torch.matmul(live_input, core_weights + delta_a)
            out_b = torch.matmul(live_input, core_weights + delta_b)
            plasm.write_focal(1, out_a)
            plasm.write_focal(2, out_b)

            hippo_dev = plasm.hippo_matrix.to(plasm.device)
            nov_a = torch.mean(torch.norm(out_a.mean(dim=0) - hippo_dev, dim=1)).item()
            nov_b = torch.mean(torch.norm(out_b.mean(dim=0) - hippo_dev, dim=1)).item()
            fit_a = 1.0 / (torch.norm(out_a).item() + 1e-6)
            fit_b = 1.0 / (torch.norm(out_b).item() + 1e-6)

            score_a = fit_a + 0.35 * nov_a
            score_b = fit_b + 0.35 * nov_b
            if score_a >= score_b:
                winner, win_delta, win_out = "LINEAGE_ALPHA", delta_a, out_a
            else:
                winner, win_delta, win_out = "LINEAGE_BETA", delta_b, out_b

            candidate_weights = (core_weights + 0.15 * win_delta) * (1.0 - 0.0004)
            extracted = torch.matmul(candidate_weights, trigger_vec)
            match_pct = max(0.0, torch.cosine_similarity(extracted, target_id, dim=0).item()) * 100.0
            update_cost = 15.0 * (match_pct / 100.0) if match_pct > 50.0 else 2.0

            safety = verify_weight_update_safety(
                baseline_weights,
                core_weights,
                candidate_weights,
                budget,
                update_cost,
            )
            if safety["accepted"]:
                core_weights = candidate_weights
                next_budget = safety["remaining_budget"]
            else:
                next_budget = budget

            extracted = torch.matmul(core_weights, trigger_vec)
            match_pct = max(0.0, torch.cosine_similarity(extracted, target_id, dim=0).item()) * 100.0
            next_tension = torch.norm(win_out).item()

            plasm.append_hippocampus(win_out.mean(dim=0))
            plasm.write_sympathetic(next_tension, next_budget, step + 1.0, thermal_c)
            history.append({
                "step": int(step),
                "device": str(plasm.device),
                "winner": winner,
                "tension": round(next_tension, 4),
                "watermark_match_pct": round(match_pct, 2),
                "budget": round(next_budget, 2),
            })
        return {"status": "PASS", "device": str(plasm.device), "shm_bytes": plasm.total_bytes, "cycles": history}
    finally:
        plasm.close(unlink=True)

if __name__ == "__main__":
    print(json.dumps(run_plasm_cycle(3), indent=2))
