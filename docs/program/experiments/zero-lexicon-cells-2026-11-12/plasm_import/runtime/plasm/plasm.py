#!/usr/bin/env python3
"""
Weft Plasm Substrate & Mitotic Loom (Codebase C1 — Interfaces I3, I4, I7)
=========================================================================
Implements the 3-tier POSIX shared-memory substrate (`540,688` bytes) and the
models-as-cells engineering contract (#6):
  1. Boundary isolation: fixed 540,688-byte shared-memory arena (`StratifiedMemoryArena`)
     with explicit focal, sympathetic, and hippocampal ring bounds.
  2. Speculative A/B child lineages (#5, #22): evaluates candidate weight matrices
     `W_cand_a` and `W_cand_b` directly against an explicit `target_out` tensor
     (`Fitness = 1 / (||X @ W_cand - target_out||_F + eps)`) plus normalized
     hippocampal novelty, and commits the exact scored matrix only if it improves
     survival score and passes the C2 invariant gate (`verify_weight_update_safety`).
  3. Core-periphery plasticity mask (#6, #22): freezes the core invariant rows
     (`mask[:core_rows, :] == 0.0`) so core parameters and embedded provenance
     watermarks suffer zero drift (`||W_cand[:core_rows] - W_base[:core_rows]||_F == 0`)
     while periphery weights adapt.
  4. Watermark threat model & retention check (#4): embeds the linear provenance
     mark inside the frozen core subspace and verifies both cosine alignment and
     L2 trigger response drift on every generation, detecting adversarial trigger
     overwrite or subspace rotation.
  5. Clean teardown (#17): releases all numpy/ctypes buffer exports before closing
     and unlinking `SharedMemory` so Python 3.13+ never raises `BufferError`.
  6. Homeostatic feedback (#6): regulates mutation scale `sigma` from measured
     cellular tension to remain within the `[15.0, 35.0]` homeostatic band.
"""

from __future__ import annotations

import ctypes
import gc
import hashlib
import math
import os
import time
from multiprocessing import shared_memory
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch

from weft.runtime.invariants import (
    HOMEOSTATIC_TENSION_MAX,
    HOMEOSTATIC_TENSION_MIN,
    R_INVARIANT,
    TENSION_MAX,
    verify_tension_bound,
    verify_weight_update_safety,
    verify_weight_update_safety_ex,
)

# 1. Stratified Memory Arena Constants (540,688 bytes total — Interface I4)
SHM_NAME = "weft_stratified_plasm_v1"
FOCAL_FLOATS = 256 * 256          # 65,536 float32 = 262,144 bytes (Active Synaptic Core)
SYMPATHETIC_FLOATS = 1024         # 1,024 float32  =   4,096 bytes (Autonomic Telemetry Ring)
HIPPOCAMPAL_FLOATS = 64 * 1024    # 65,536 float32 = 262,144 bytes (Episodic Novelty Lattice)
DEFAULT_SEED_PHRASE = "WEFT_DETERMINISTIC_SEED_V1"


class StratifiedMemoryArena(ctypes.Structure):
    _fields_ = [
        ("generation_epoch", ctypes.c_uint64),
        ("metabolic_tension", ctypes.c_double),
        ("focal_workspace", ctypes.c_float * FOCAL_FLOATS),
        ("sympathetic_ring", ctypes.c_float * SYMPATHETIC_FLOATS),
        ("hippocampal_lattice", ctypes.c_float * HIPPOCAMPAL_FLOATS),
        ("cryptographic_lock", ctypes.c_uint8 * 12288),
    ]


ARENA_BYTE_SIZE = ctypes.sizeof(StratifiedMemoryArena)


def select_compute_device() -> torch.device:
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


class StratifiedAppleSiliconPlasm:
    """
    Zero-copy POSIX shared-memory substrate bridged to PyTorch tensors (`mps` or `cpu`)
    with clean buffer release (#17).
    """

    def __init__(self, name: str = SHM_NAME, create: bool = True):
        self.name = name
        self.size = ARENA_BYTE_SIZE
        self._closed = False
        if create:
            try:
                stale = shared_memory.SharedMemory(name=self.name, create=False)
                stale.close()
                stale.unlink()
            except FileNotFoundError:
                pass
            self.shm = shared_memory.SharedMemory(name=self.name, create=True, size=self.size)
        else:
            self.shm = shared_memory.SharedMemory(name=self.name, create=False)

        self.c_view: Optional[StratifiedMemoryArena] = StratifiedMemoryArena.from_buffer(self.shm.buf)
        self._raw_np: Optional[np.ndarray] = np.ctypeslib.as_array(self.c_view)
        self.focal_matrix: Optional[np.ndarray] = np.ndarray(
            (256, 256), dtype=np.float32, buffer=self.shm.buf, offset=16
        )
        self.symp_matrix: Optional[np.ndarray] = np.ndarray(
            (1024,), dtype=np.float32, buffer=self.shm.buf, offset=16 + 262144
        )
        self.hippo_matrix: Optional[np.ndarray] = np.ndarray(
            (64, 1024), dtype=np.float32, buffer=self.shm.buf, offset=16 + 262144 + 4096
        )

    def seed_arena(self) -> None:
        if self.c_view is None or self.focal_matrix is None or self.symp_matrix is None or self.hippo_matrix is None:
            raise RuntimeError("Arena is closed")
        self.c_view.generation_epoch = 1
        self.c_view.metabolic_tension = 22.0
        rng = np.random.default_rng(42)
        self.focal_matrix[:] = rng.standard_normal((256, 256), dtype=np.float32) * 0.05
        self.symp_matrix[:] = np.linspace(0.0, 1.0, 1024, dtype=np.float32)
        self.hippo_matrix[:] = rng.standard_normal((64, 1024), dtype=np.float32) * 0.02

    def read_tensors_to_device(
        self, device: torch.device
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Copy shared-memory slices into independent device tensors so callers never
        hold exported buffer pointers into `self.shm.buf` (#17).
        """
        if self.focal_matrix is None or self.symp_matrix is None or self.hippo_matrix is None:
            raise RuntimeError("Arena is closed")
        focal_t = torch.tensor(np.array(self.focal_matrix, copy=True), dtype=torch.float32, device=device)
        symp_t = torch.tensor(np.array(self.symp_matrix, copy=True), dtype=torch.float32, device=device)
        hippo_t = torch.tensor(np.array(self.hippo_matrix, copy=True), dtype=torch.float32, device=device)
        return focal_t, symp_t, hippo_t

    def write_focal_from_tensor(
        self, tensor: torch.Tensor, epoch: int, tension: float
    ) -> None:
        if self.c_view is None or self.focal_matrix is None:
            raise RuntimeError("Arena is closed")
        cpu_arr = tensor.detach().to("cpu").numpy()
        np.copyto(self.focal_matrix, cpu_arr)
        self.c_view.generation_epoch = int(epoch)
        self.c_view.metabolic_tension = float(tension)

    def release_views(self) -> None:
        """Drop all ctypes/numpy memoryviews referencing `self.shm.buf` (#17)."""
        self.focal_matrix = None
        self.symp_matrix = None
        self.hippo_matrix = None
        self._raw_np = None
        self.c_view = None
        gc.collect()

    def close(self, unlink: bool = True) -> None:
        if self._closed:
            return
        self.release_views()
        self.shm.close()
        if unlink:
            try:
                self.shm.unlink()
            except FileNotFoundError:
                pass
        self._closed = True

    def __enter__(self) -> "StratifiedAppleSiliconPlasm":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close(unlink=True)


def compute_plasticity_mask(
    weights: torch.Tensor, core_rows: Optional[int] = None
) -> torch.Tensor:
    """
    Build a core-periphery plasticity mask (#6, #22):
      - Rows `[0 : core_rows]` are the frozen core invariant slice (`mask == 0.0`).
      - Rows `[core_rows : dim]` are the adaptable periphery slice (`mask in (0, 1]`),
        modulated inversely by column L2 weight magnitude.
    """
    rows, cols = weights.shape
    if core_rows is None:
        core_rows = rows // 4
    col_mag = torch.norm(weights, p=2, dim=0, keepdim=True)
    col_gate = torch.sigmoid(-col_mag + col_mag.mean()).expand(rows, cols).clone()
    if core_rows > 0:
        col_gate[:core_rows, :] = 0.0
    return col_gate


def embed_weight_watermark(
    w_core: torch.Tensor,
    seed_phrase: Optional[str] = None,
    core_rows: Optional[int] = None,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, float]:
    """
    Embed a deterministic provenance watermark inside the frozen core subspace (#4)
    so legitimate periphery plasticity preserves the mark, while unauthorized core
    overwrites are immediately detected by `verify_watermark_retention`.
    """
    if seed_phrase is None:
        seed_phrase = os.environ.get("WEFT_SEED", DEFAULT_SEED_PHRASE)
    dim = w_core.shape[0]
    if core_rows is None:
        core_rows = dim // 4
    digest = hashlib.sha256(seed_phrase.encode("utf-8")).digest()

    gen = torch.Generator(device="cpu")
    gen.manual_seed(int.from_bytes(digest[:8], "big"))
    trigger_cpu = torch.zeros(dim, dtype=torch.float32)
    # Confine trigger support to the frozen core rows `[0 : core_rows]`
    core_trigger = torch.randn(core_rows, generator=gen, dtype=torch.float32)
    core_trigger = core_trigger / torch.norm(core_trigger, p=2)
    trigger_cpu[:core_rows] = core_trigger

    gen.manual_seed(int.from_bytes(digest[8:16], "big"))
    target_cpu = torch.randn(dim, generator=gen, dtype=torch.float32)
    target_cpu = (target_cpu / torch.norm(target_cpu, p=2)) * 3.0

    trigger_vec = trigger_cpu.to(w_core.device)
    target_id = target_cpu.to(w_core.device)

    current_resp = torch.mv(w_core.t(), trigger_vec)
    correction = torch.outer(trigger_vec, target_id - current_resp)
    w_watermarked = (w_core + correction).detach()

    verify_resp = torch.mv(w_watermarked.t(), trigger_vec)
    alignment = torch.nn.functional.cosine_similarity(
        verify_resp.unsqueeze(0), target_id.unsqueeze(0)
    ).item()
    return w_watermarked, trigger_vec, target_id, float(alignment)


def verify_watermark_retention(
    baseline_w: torch.Tensor,
    current_w: torch.Tensor,
    trigger_vec: torch.Tensor,
    target_id: torch.Tensor,
    min_cosine: float = 0.85,
    max_response_l2_drift: float = 0.35,
) -> Dict[str, Any]:
    """
    Verify provenance watermark retention under the explicit threat model (#4):
      - Threat 1: Targeted rank-1 overwrite (`W' = W + trigger (v_adv - resp)^T`).
      - Threat 2: Core subspace drift or fine-tuning without the core plasticity mask.
    Checks both cosine alignment with `target_id` and relative L2 drift of
    `W^T @ trigger_vec` from `W_base^T @ trigger_vec`.
    """
    with torch.no_grad():
        base_resp = torch.mv(baseline_w.t(), trigger_vec)
        curr_resp = torch.mv(current_w.t(), trigger_vec)
        cos_align = float(
            torch.nn.functional.cosine_similarity(
                curr_resp.unsqueeze(0), target_id.unsqueeze(0)
            ).item()
        )
        base_norm = float(torch.norm(base_resp, p=2).item()) + 1e-8
        resp_drift = float(torch.norm(curr_resp - base_resp, p=2).item()) / base_norm

    if not (math.isfinite(cos_align) and math.isfinite(resp_drift)):
        return {
            "retained": False,
            "cosine_alignment": cos_align,
            "response_l2_drift": resp_drift,
            "reason": "non_finite_watermark_response",
        }
    if cos_align < min_cosine:
        return {
            "retained": False,
            "cosine_alignment": cos_align,
            "response_l2_drift": resp_drift,
            "reason": "cosine_alignment_below_threshold",
        }
    if resp_drift > max_response_l2_drift:
        return {
            "retained": False,
            "cosine_alignment": cos_align,
            "response_l2_drift": resp_drift,
            "reason": "trigger_response_drift_exceeded",
        }
    return {
        "retained": True,
        "cosine_alignment": cos_align,
        "response_l2_drift": resp_drift,
        "reason": "ok",
    }


def adjust_homeostatic_mutation_scale(
    sigma: float,
    tension: float,
    target_min: float = HOMEOSTATIC_TENSION_MIN,
    target_max: float = HOMEOSTATIC_TENSION_MAX,
) -> float:
    """Negative-feedback controller keeping cellular tension inside `[15.0, 35.0]` (#6)."""
    if tension > target_max:
        return max(1e-4, sigma * 0.75)
    if tension < target_min:
        return min(0.25, sigma * 1.10)
    return sigma


def run_weft_plasm_cycle(
    generations: int = 4,
    seed_phrase: Optional[str] = None,
    shm_name: Optional[str] = None,
    cycles: Optional[int] = None,
) -> Dict[str, Any]:
    if cycles is not None:
        generations = int(cycles)
    """
    Execute an end-to-end mitotic cycle over the POSIX shared-memory substrate,
    enforcing the C2 invariant gate, core-freezing plasticity mask, target-directed
    A/B convergence, and watermark retention verification.
    """
    device = select_compute_device()
    arena_name = shm_name or f"{SHM_NAME}_{os.getpid()}"
    plasm = StratifiedAppleSiliconPlasm(name=arena_name, create=True)
    try:
        plasm.seed_arena()
        w_core, symp, hippo = plasm.read_tensors_to_device(device)
        dim = w_core.shape[0]
        core_rows = dim // 4

        # Embed provenance watermark in the frozen core subspace `[0 : core_rows]`
        w_core, trigger_vec, target_id, initial_wm = embed_weight_watermark(
            w_core, seed_phrase=seed_phrase, core_rows=core_rows
        )
        w_baseline = w_core.detach().clone()

        # Construct a deterministic input stimulus and target response on the periphery
        gen_cpu = torch.Generator(device="cpu")
        gen_cpu.manual_seed(20261107)
        x_in = (torch.randn(16, dim, generator=gen_cpu, dtype=torch.float32) * 0.25).to(device)
        # Target is generated by a slightly shifted periphery weight matrix within R_INVARIANT
        mask = compute_plasticity_mask(w_baseline, core_rows=core_rows)
        ideal_delta = (torch.randn(dim, dim, generator=gen_cpu, dtype=torch.float32) * 0.015).to(device)
        w_ideal = w_baseline + mask * ideal_delta
        target_out = torch.matmul(x_in, w_ideal).detach()

        hippo_summary = hippo[:, :dim].mean(dim=0, keepdim=True)  # (1, dim)
        metabolic_budget = 100.0
        r_invariant = R_INVARIANT
        sigma = 0.015
        lr = 0.35
        alpha_novelty = 0.05

        history: List[Dict[str, Any]] = []
        t0 = time.perf_counter()

        for gen in range(1, generations + 1):
            with torch.no_grad():
                mask = compute_plasticity_mask(w_core, core_rows=core_rows)
                parent_out = torch.matmul(x_in, w_core)
                parent_err = float(torch.linalg.norm(parent_out - target_out).item())

                # Compute periphery residual direction + stochastic A/B perturbations
                residual_grad = torch.matmul(x_in.t(), (target_out - parent_out)) / float(x_in.shape[0])
                noise_a = torch.randn_like(w_core) * sigma
                noise_b = torch.randn_like(w_core) * sigma

                delta_a = mask * (0.85 * residual_grad + 0.15 * noise_a)
                delta_b = mask * (0.50 * residual_grad - 0.50 * noise_b)

                # Score the EXACT candidate matrices that will be committed (#22)
                w_cand_a = w_core + lr * delta_a
                w_cand_b = w_core + lr * delta_b

                out_a = torch.matmul(x_in, w_cand_a)
                out_b = torch.matmul(x_in, w_cand_b)

                err_a = float(torch.linalg.norm(out_a - target_out).item())
                err_b = float(torch.linalg.norm(out_b - target_out).item())

                fit_a = 1.0 / (err_a + 1e-4)
                fit_b = 1.0 / (err_b + 1e-4)

                # Normalized hippocampal novelty in [0, 1]
                nov_a = float(
                    torch.linalg.norm(out_a.mean(dim=0, keepdim=True) - hippo_summary).item()
                    / (torch.linalg.norm(out_a.mean(dim=0, keepdim=True)).item() + torch.linalg.norm(hippo_summary).item() + 1e-6)
                )
                nov_b = float(
                    torch.linalg.norm(out_b.mean(dim=0, keepdim=True) - hippo_summary).item()
                    / (torch.linalg.norm(out_b.mean(dim=0, keepdim=True)).item() + torch.linalg.norm(hippo_summary).item() + 1e-6)
                )

                score_a = fit_a + alpha_novelty * nov_a
                score_b = fit_b + alpha_novelty * nov_b

                if score_a >= score_b:
                    winner = "ALPHA"
                    w_candidate = w_cand_a
                    winner_err = err_a
                    winner_score = score_a
                else:
                    winner = "BETA"
                    w_candidate = w_cand_b
                    winner_err = err_b
                    winner_score = score_b

                safe, drift, remaining_budget, gate_reason = verify_weight_update_safety_ex(
                    w_baseline, w_candidate, r_invariant, metabolic_budget, step_cost=2.5
                )
                wm_check = verify_watermark_retention(
                    w_baseline, w_candidate, trigger_vec, target_id
                )
                core_row_drift = float(
                    torch.linalg.norm(w_candidate[:core_rows, :] - w_baseline[:core_rows, :]).item()
                )

                tension = 20.0 + drift * 2.5
                t_bound = verify_tension_bound(tension)

                if safe and wm_check["retained"] and t_bound["accepted"] and winner_err <= parent_err:
                    w_core = w_candidate
                    metabolic_budget = remaining_budget
                    plasm.write_focal_from_tensor(w_core, epoch=gen, tension=tension)

                sigma = adjust_homeostatic_mutation_scale(sigma, tension)

                history.append(
                    {
                        "generation": gen,
                        "winner": winner,
                        "score_alpha": round(score_a, 4),
                        "score_beta": round(score_b, 4),
                        "winner_score": round(winner_score, 4),
                        "parent_target_error": round(parent_err, 6),
                        "winner_target_error": round(winner_err, 6),
                        "invariant_safe": safe,
                        "gate_reason": gate_reason,
                        "frobenius_drift": round(drift, 6),
                        "core_row_drift": round(core_row_drift, 8),
                        "watermark_retained": wm_check["retained"],
                        "watermark_alignment": round(wm_check["cosine_alignment"], 4),
                        "watermark_l2_drift": round(wm_check["response_l2_drift"], 6),
                        "tension": round(tension, 4),
                        "homeostatic": t_bound["homeostatic"],
                        "remaining_budget": round(metabolic_budget, 2),
                    }
                )

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        final_hash = hashlib.sha256(w_core.detach().to("cpu").numpy().tobytes()).hexdigest()
        all_ok = all(g["invariant_safe"] and g["watermark_retained"] and g["core_row_drift"] == 0.0 for g in history) and (history[-1]["winner_target_error"] < history[0]["parent_target_error"])
        return {
            "status": "PASS" if all_ok else "FAIL",
            "device": str(device),
            "arena_bytes": ARENA_BYTE_SIZE,
            "core_rows_frozen": core_rows,
            "initial_watermark_alignment": round(initial_wm, 4),
            "final_watermark_alignment": history[-1]["watermark_alignment"],
            "final_core_row_drift": history[-1]["core_row_drift"],
            "initial_target_error": history[0]["parent_target_error"],
            "final_target_error": history[-1]["winner_target_error"],
            "elapsed_ms": round(elapsed_ms, 2),
            "final_weights_sha256": f"0x{final_hash}",
            "generations": history,
        }
    finally:
        plasm.close(unlink=True)


def weight_frobenius_size(weights: torch.Tensor) -> float:
    """Scalar Frobenius norm `||W||_F` used to demonstrate the compared-sizes trap (#2)."""
    return float(torch.linalg.norm(weights).item())


run_plasm_cycle = run_weft_plasm_cycle
