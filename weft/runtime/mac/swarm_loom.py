#!/usr/bin/env python3
"""
Apple Silicon Swarm Loom Substrate (Codebase C1 / Mac MPS Micro-Swarm)
======================================================================
Implements the Apple Silicon micro-swarm architecture:
  1. StratifiedSwarmArena: Zero-copy POSIX shared-memory arena (max 30-byte name for
     macOS PSHMNAMLEN) holding header, focal weights, energy ledger, and niche
     specializations, with leak-free teardown across Python versions.
  2. VectorizedPlasmColony: High-throughput PyTorch / MPS batched mitotic loom
     executing parallel colony evolution across N ecological niche tiles, supporting
     both uniform-rank tiles (E14) and graded-rank / conditioned tiles (E15).
  3. Strict C1/C2 Invariants: Deterministic linear provenance watermark in frozen
     core subspace (zero drift, cosine == 1.0) and vectorized Frobenius ball gate.
  4. Five Strictly Zero-Order (Gradient-Free) Mitosis Modes:
     - "paper1_blind": Paper 1 isotropic A/B baseline (cautious vs 5x exploratory noise).
     - "hgt_isolated": Zero-order low-rank subspace mutation + horizontal gene transfer
       and directional memory (velocity) on a single tile without foraging.
     - "hgt_foraging": Zero-order subspace mutation + HGT with static multi-niche
       foraging, basal upkeep, and apoptosis re-colonization.
     - "dissipative_chemostat": E14 convergence arm with PR #118 L2 laws.
     - "graded_chemostat": E15 L2 chemostat with the unsolved-gap allocation
       rule `(unsolved_gap / mean)^2`, mass-conserving tile pools, niche-clean
       Soma/Spore inheritance under configurable `spore_fraction`, and optional
       zero-order homeostatic step-scale cooling (`adaptive_step`).
"""

from __future__ import annotations

import ctypes
import gc
import math
import os
import time
from multiprocessing import shared_memory
from typing import Any, Dict, Optional, Sequence, Tuple, Union

import numpy as np
import torch

from weft.runtime.invariants import (
    HOMEOSTATIC_TENSION_MAX,
    HOMEOSTATIC_TENSION_MIN,
    R_INVARIANT,
    TENSION_MAX,
)
from weft.runtime.plasm import (
    DEFAULT_SEED_PHRASE,
    check_shm_name,
    embed_weight_watermark,
    select_compute_device,
)

DEFAULT_SWARM_SHM_NAME = "weft_swarm_plasm_v1"


class SwarmArenaHeader(ctypes.Structure):
    """
    Contiguous 32-byte header for swarm shared-memory segment:
      generation_epoch: uint64 (8 bytes, offset 0)
      colony_size:      uint32 (4 bytes, offset 8)
      dim:              uint32 (4 bytes, offset 12)
      n_niches:         uint32 (4 bytes, offset 16)
      reserved:         uint32 (4 bytes, offset 20)
      mean_tension:     float64 (8 bytes, offset 24)
    Total: 32 bytes.
    """

    _fields_ = [
        ("generation_epoch", ctypes.c_uint64),
        ("colony_size", ctypes.c_uint32),
        ("dim", ctypes.c_uint32),
        ("n_niches", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32),
        ("mean_tension", ctypes.c_double),
    ]


SWARM_HEADER_SIZE = ctypes.sizeof(SwarmArenaHeader)
assert SWARM_HEADER_SIZE == 32, f"Header size must be 32 bytes, got {SWARM_HEADER_SIZE}"


def compute_swarm_arena_size(n_cells: int, dim: int) -> int:
    """Calculate the exact byte requirement for the shared-memory buffer."""
    header_bytes = SWARM_HEADER_SIZE
    focal_bytes = n_cells * dim * dim * 4
    energy_bytes = n_cells * 4
    niche_bytes = n_cells * 4
    return header_bytes + focal_bytes + energy_bytes + niche_bytes


class StratifiedSwarmArena:
    """
    Zero-copy POSIX shared-memory arena for the vectorized micro-swarm.
    Bridges shared memory to numpy views and releases all buffers cleanly
    before unlinking to prevent BufferError under Python 3.13+.
    """

    def __init__(
        self,
        name: str = DEFAULT_SWARM_SHM_NAME,
        n_cells: int = 512,
        dim: int = 64,
        n_niches: int = 8,
        create: bool = True,
    ):
        self.name = check_shm_name(name)
        self._closed = False

        if create:
            try:
                stale = shared_memory.SharedMemory(name=self.name, create=False)
                stale.close()
                stale.unlink()
            except FileNotFoundError:
                pass
            self.size = compute_swarm_arena_size(n_cells, dim)
            self.shm = shared_memory.SharedMemory(
                name=self.name, create=True, size=self.size
            )
            self.header_view: Optional[SwarmArenaHeader] = (
                SwarmArenaHeader.from_buffer(self.shm.buf)
            )
            self.header_view.generation_epoch = 0
            self.header_view.colony_size = n_cells
            self.header_view.dim = dim
            self.header_view.n_niches = n_niches
            self.header_view.reserved = 0
            self.header_view.mean_tension = 0.0
            self.n_cells = n_cells
            self.dim = dim
            self.n_niches = n_niches
        else:
            self.shm = shared_memory.SharedMemory(name=self.name, create=False)
            self.size = self.shm.size
            self.header_view = SwarmArenaHeader.from_buffer(self.shm.buf)
            self.n_cells = int(self.header_view.colony_size)
            self.dim = int(self.header_view.dim)
            self.n_niches = int(self.header_view.n_niches)

        focal_offset = SWARM_HEADER_SIZE
        energy_offset = focal_offset + self.n_cells * self.dim * self.dim * 4
        niche_offset = energy_offset + self.n_cells * 4

        self.focal_weights: Optional[np.ndarray] = np.ndarray(
            (self.n_cells, self.dim, self.dim),
            dtype=np.float32,
            buffer=self.shm.buf,
            offset=focal_offset,
        )
        self.energy_ledger: Optional[np.ndarray] = np.ndarray(
            (self.n_cells,),
            dtype=np.float32,
            buffer=self.shm.buf,
            offset=energy_offset,
        )
        self.niche_specialization: Optional[np.ndarray] = np.ndarray(
            (self.n_cells,),
            dtype=np.int32,
            buffer=self.shm.buf,
            offset=niche_offset,
        )

    def release_views(self) -> None:
        """Drop all buffer memoryviews and run garbage collection."""
        self.focal_weights = None
        self.energy_ledger = None
        self.niche_specialization = None
        self.header_view = None
        gc.collect()

    def close(self, unlink: bool = False) -> None:
        """Safely close and optionally unlink shared memory."""
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

    def unlink(self) -> None:
        """Unlink the POSIX shared memory file descriptor."""
        try:
            self.shm.unlink()
        except FileNotFoundError:
            pass

    def __enter__(self) -> "StratifiedSwarmArena":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close(unlink=True)


class VectorizedPlasmColony:
    """
    Batched, vectorized micro-swarm executing parallel colony evolution on
    Apple Silicon MPS or CPU.
    """

    def __init__(
        self,
        device: Optional[Union[str, torch.device]] = None,
        n_cells: int = 512,
        dim: int = 64,
        n_niches: int = 8,
        subspace_rank: int = 4,
        r_invariant: float = 10.0,
        initial_energy: float = 100.0,
        basal_upkeep: float = 2.0,
        tile_bounty: float = 160.0,
        seed: int = 0,
        arena_name: Optional[str] = None,
        arena: Optional[StratifiedSwarmArena] = None,
        tile_ranks: Optional[Sequence[int]] = None,
        tile_condition_numbers: Optional[Sequence[float]] = None,
        spore_fraction: float = 0.25,
        adaptive_step: bool = False,
    ):
        if device is None:
            self.device = select_compute_device()
        elif isinstance(device, str):
            self.device = torch.device(device)
        else:
            self.device = device

        if not (0.0 <= float(spore_fraction) <= 1.0):
            raise ValueError(f"spore_fraction must lie in [0, 1], got {spore_fraction!r}")

        self.n_cells = int(n_cells)
        self.dim = int(dim)
        self.n_niches = int(n_niches)
        self.subspace_rank = int(subspace_rank)
        self.r_invariant = float(r_invariant)
        self.initial_energy = float(initial_energy)
        self.basal_upkeep = float(basal_upkeep)
        self.tile_bounty = float(tile_bounty)
        self.seed = int(seed)
        self.spore_fraction = float(spore_fraction)
        self.adaptive_step = bool(adaptive_step)
        self.batch_size = 16
        # Seed the global RNG too: per-step mutation noise (torch.randn on the
        # colony device) draws from it, so runs are reproducible per seed.
        torch.manual_seed(self.seed)

        if tile_ranks is not None:
            if len(tile_ranks) != self.n_niches:
                raise ValueError("len(tile_ranks) must equal n_niches")
            self.tile_ranks = [int(r) for r in tile_ranks]
        else:
            self.tile_ranks = [self.subspace_rank] * self.n_niches

        if tile_condition_numbers is not None:
            if len(tile_condition_numbers) != self.n_niches:
                raise ValueError("len(tile_condition_numbers) must equal n_niches")
            self.tile_condition_numbers = [float(c) for c in tile_condition_numbers]
        else:
            self.tile_condition_numbers = [1.0] * self.n_niches

        # Core-periphery partition (top quarter rows frozen)
        self.core_rows = self.dim // 4

        # Embed linear provenance watermark in frozen core subspace
        gen_cpu = torch.Generator(device="cpu")
        gen_cpu.manual_seed(self.seed)
        w_base_cpu = (
            torch.randn(self.dim, self.dim, generator=gen_cpu, dtype=torch.float32)
            * 0.05
        )

        w_wm_cpu, trigger_cpu, target_cpu, initial_align = embed_weight_watermark(
            w_base_cpu, DEFAULT_SEED_PHRASE, core_rows=self.core_rows
        )
        self.trigger_vec = trigger_cpu.to(self.device)
        self.target_id = target_cpu.to(self.device)
        self.w_watermarked = w_wm_cpu.to(self.device)

        # Baseline weights W0: shared frozen core, unique initial periphery
        w_init = (
            torch.randn(
                self.n_cells,
                self.dim,
                self.dim,
                generator=gen_cpu,
                dtype=torch.float32,
            )
            * 0.05
        ).to(self.device)
        w_init[:, : self.core_rows, :] = self.w_watermarked[
            : self.core_rows, :
        ].unsqueeze(0)
        self.W0 = w_init
        self.W = self.W0.clone()

        # Plasticity mask: rows [0:core_rows] are strictly 0.0
        self.plasticity_mask = torch.ones(
            self.n_cells, self.dim, self.dim, device=self.device
        )
        self.plasticity_mask[:, : self.core_rows, :] = 0.0

        # State ledgers
        self.energy = torch.full(
            (self.n_cells,),
            self.initial_energy,
            dtype=torch.float32,
            device=self.device,
        )
        self.niches = torch.arange(self.n_cells, device=self.device) % self.n_niches
        self.accepted_updates = torch.zeros(
            self.n_cells, dtype=torch.int32, device=self.device
        )
        self.died = torch.zeros(self.n_cells, dtype=torch.bool, device=self.device)
        # Zero-order directional memory (tensor equivalent of genome.md last winning delta)
        self.velocity = torch.zeros_like(self.W)
        # Per-cell zero-order step scale (used when adaptive_step=True in graded_chemostat)
        self.step_scale = torch.full(
            (self.n_cells,), 0.012, dtype=torch.float32, device=self.device
        )

        # Cumulative telemetry
        self.alpha_wins = 0
        self.beta_wins = 0
        self.recolonizations = 0
        self.spore_births = 0
        self.generation = 0
        self.mean_tension = 22.0

        # Ecological environment: N distinct peripheral target tiles
        gen_env = torch.Generator(device="cpu")
        gen_env.manual_seed(self.seed + 1000)
        x_tiles_cpu = (
            torch.randn(
                self.n_niches,
                self.batch_size,
                self.dim,
                generator=gen_env,
                dtype=torch.float32,
            )
            * 0.25
        )
        if tile_condition_numbers is not None:
            for m, cond_m in enumerate(self.tile_condition_numbers):
                if cond_m > 1.0:
                    xm = x_tiles_cpu[m]
                    orig_norm = torch.linalg.matrix_norm(xm, ord="fro")
                    u_x, s_x, vh_x = torch.linalg.svd(xm, full_matrices=False)
                    k_sv = s_x.numel()
                    decay = torch.logspace(
                        0.0, -math.log10(cond_m), steps=k_sv, dtype=torch.float32
                    )
                    s_cond = s_x * decay
                    xm_cond = (u_x * s_cond.unsqueeze(0)) @ vh_x
                    xm_cond = xm_cond * (
                        orig_norm / (torch.linalg.matrix_norm(xm_cond, ord="fro") + 1e-8)
                    )
                    x_tiles_cpu[m] = xm_cond
        self.X_tiles = x_tiles_cpu.to(self.device)

        delta_niches = torch.zeros(
            self.n_niches, self.dim, self.dim, device=self.device
        )
        for m in range(self.n_niches):
            rank_m = self.tile_ranks[m]
            u_m = torch.randn(
                self.dim - self.core_rows,
                rank_m,
                generator=gen_env,
                dtype=torch.float32,
            )
            v_m = torch.randn(
                rank_m,
                self.dim,
                generator=gen_env,
                dtype=torch.float32,
            )
            prod = (u_m @ v_m).to(self.device)
            target_dist = 0.5 * self.r_invariant
            prod = prod * (target_dist / (torch.linalg.matrix_norm(prod, ord="fro") + 1e-8))
            delta_niches[m, self.core_rows :, :] = prod

        w_targets = self.w_watermarked.unsqueeze(0) + delta_niches
        self.Y_tiles = torch.matmul(self.X_tiles, w_targets)

        # Baseline error E0 per niche tile
        diff0 = (
            torch.matmul(self.X_tiles.unsqueeze(0), self.W0.unsqueeze(1))
            - self.Y_tiles.unsqueeze(0)
        )
        errors0 = torch.linalg.norm(diff0, ord="fro", dim=(-2, -1))
        self.E0 = errors0.mean(dim=0)
        self.best_tile_error = self.E0.clone()
        self.chemostat_pool = torch.full(
            (self.n_niches,),
            self.tile_bounty,
            dtype=torch.float32,
            device=self.device,
        )

        # Arena connection
        self._owns_arena = False
        if arena is not None:
            self.arena = arena
        elif arena_name is not None:
            self.arena = StratifiedSwarmArena(
                name=arena_name,
                n_cells=self.n_cells,
                dim=self.dim,
                n_niches=self.n_niches,
                create=True,
            )
            self._owns_arena = True
        else:
            self.arena = None

        if self.arena is not None:
            self.sync_to_arena()

    def sync_to_arena(self) -> None:
        """Copy current device state into the zero-copy shared memory buffer."""
        if self.arena is None:
            return
        w_cpu = self.W.detach().cpu().numpy()
        e_cpu = self.energy.detach().cpu().numpy()
        n_cpu = self.niches.detach().cpu().numpy()
        np.copyto(self.arena.focal_weights, w_cpu)
        np.copyto(self.arena.energy_ledger, e_cpu)
        np.copyto(self.arena.niche_specialization, n_cpu)
        self.arena.header_view.generation_epoch = int(self.generation)
        self.arena.header_view.mean_tension = float(self.mean_tension)

    def close(self) -> None:
        """Close backing arena if owned."""
        if self._owns_arena and self.arena is not None:
            self.arena.close(unlink=True)
            self.arena = None

    def evaluate_all_tiles(self) -> torch.Tensor:
        """
        Compute batched prediction errors across all niche tiles:
        Output shape: (n_cells, n_niches).
        """
        y_pred = torch.matmul(self.X_tiles.unsqueeze(0), self.W.unsqueeze(1))
        diff = y_pred - self.Y_tiles.unsqueeze(0)
        return torch.linalg.norm(diff, ord="fro", dim=(-2, -1))

    def step(self, mode: str = "hgt_foraging") -> Dict[str, Any]:
        """
        Execute a single generation under one of five mitotic regimes.
        All regimes are zero-order: they use forward error evaluations only.
          - "paper1_blind"
          - "hgt_isolated"
          - "hgt_foraging"
          - "dissipative_chemostat"
          - "graded_chemostat"
        """
        t0 = time.perf_counter()
        if self.device.type == "mps":
            torch.mps.synchronize()

        errors = self.evaluate_all_tiles()

        if mode == "paper1_blind":
            err_curr = errors[:, 0]
            delta_a = self.plasticity_mask * (torch.randn_like(self.W) * 0.01)
            delta_b = self.plasticity_mask * (torch.randn_like(self.W) * 0.05)
            w_cand_a = self.W + delta_a
            w_cand_b = self.W + delta_b

            # C2 Invariant Gate & Frobenius projection
            dist_a = torch.linalg.matrix_norm(w_cand_a - self.W0, ord="fro", dim=(1, 2))
            scale_a = torch.clamp(self.r_invariant / (dist_a + 1e-8), max=1.0).unsqueeze(1).unsqueeze(2)
            w_cand_a = self.W0 + (w_cand_a - self.W0) * scale_a

            dist_b = torch.linalg.matrix_norm(w_cand_b - self.W0, ord="fro", dim=(1, 2))
            scale_b = torch.clamp(self.r_invariant / (dist_b + 1e-8), max=1.0).unsqueeze(1).unsqueeze(2)
            w_cand_b = self.W0 + (w_cand_b - self.W0) * scale_b

            err_a = torch.linalg.norm(
                torch.matmul(self.X_tiles[0], w_cand_a) - self.Y_tiles[0],
                ord="fro",
                dim=(-2, -1),
            )
            err_b = torch.linalg.norm(
                torch.matmul(self.X_tiles[0], w_cand_b) - self.Y_tiles[0],
                ord="fro",
                dim=(-2, -1),
            )

            improved = (err_a < err_curr) | (err_b < err_curr)
            b_beats_a = err_b < err_a
            b_won = improved & b_beats_a
            a_won = improved & (~b_beats_a)

            self.beta_wins += int(b_won.sum().item())
            self.alpha_wins += int(a_won.sum().item())
            self.W[b_won] = w_cand_b[b_won]
            self.W[a_won] = w_cand_a[a_won]
            self.accepted_updates[b_won | a_won] += 1
            self.niches[:] = 0

        elif mode == "hgt_isolated":
            err_curr = errors[:, 0]
            champ_0 = torch.argmin(err_curr)
            hgt = self.W[champ_0] - self.W
            # Strictly zero-order HGT + directional velocity memory (no gradient)
            dir_b = 0.5 * hgt + 0.5 * self.velocity[champ_0].unsqueeze(0)

            u_mut = torch.randn(self.n_cells, self.dim, self.subspace_rank, device=self.device)
            v_mut = torch.randn(self.n_cells, self.subspace_rank, self.dim, device=self.device)
            sub_mut = torch.bmm(u_mut, v_mut) * 0.012
            delta_b = self.plasticity_mask * (dir_b + sub_mut)
            w_cand_b = self.W + delta_b

            delta_a = self.plasticity_mask * (torch.randn_like(self.W) * 0.01)
            w_cand_a = self.W + delta_a

            dist_a = torch.linalg.matrix_norm(w_cand_a - self.W0, ord="fro", dim=(1, 2))
            scale_a = torch.clamp(self.r_invariant / (dist_a + 1e-8), max=1.0).unsqueeze(1).unsqueeze(2)
            w_cand_a = self.W0 + (w_cand_a - self.W0) * scale_a

            dist_b = torch.linalg.matrix_norm(w_cand_b - self.W0, ord="fro", dim=(1, 2))
            scale_b = torch.clamp(self.r_invariant / (dist_b + 1e-8), max=1.0).unsqueeze(1).unsqueeze(2)
            w_cand_b = self.W0 + (w_cand_b - self.W0) * scale_b

            err_a = torch.linalg.norm(
                torch.matmul(self.X_tiles[0], w_cand_a) - self.Y_tiles[0],
                ord="fro",
                dim=(-2, -1),
            )
            err_b = torch.linalg.norm(
                torch.matmul(self.X_tiles[0], w_cand_b) - self.Y_tiles[0],
                ord="fro",
                dim=(-2, -1),
            )

            improved = (err_a < err_curr) | (err_b < err_curr)
            b_beats_a = err_b < err_a
            b_won = improved & b_beats_a
            a_won = improved & (~b_beats_a)

            self.beta_wins += int(b_won.sum().item())
            self.alpha_wins += int(a_won.sum().item())
            self.velocity[b_won] = w_cand_b[b_won] - self.W[b_won]
            self.velocity[a_won] = w_cand_a[a_won] - self.W[a_won]
            self.W[b_won] = w_cand_b[b_won]
            self.W[a_won] = w_cand_a[a_won]
            self.accepted_updates[b_won | a_won] += 1
            self.niches[:] = 0

        elif mode == "hgt_foraging":
            # Static niche bounty allocation
            earnings = torch.zeros(self.n_cells, self.n_niches, device=self.device)
            k_bounty = max(1, self.n_cells // (2 * self.n_niches))
            for m in range(self.n_niches):
                errs_m = errors[:, m]
                self.best_tile_error[m] = torch.minimum(self.best_tile_error[m], errs_m.min())
                topk_vals, topk_idx = torch.topk(errs_m, k_bounty, largest=False)
                ranks = torch.arange(k_bounty, device=self.device, dtype=torch.float32)
                weights = 1.0 / (ranks + 1.0)
                shares = self.tile_bounty * (weights / weights.sum())
                earnings[topk_idx, m] += shares
                self.energy[topk_idx] += shares

            # Ecological Niche Binding
            has_earnings = earnings.max(dim=1).values > 0
            best_earn_niche = torch.argmax(earnings, dim=1)
            rel_errors = errors / self.E0.unsqueeze(0)
            best_fit_niche = torch.argmin(rel_errors, dim=1)
            self.niches = torch.where(has_earnings, best_earn_niche, best_fit_niche)

            # Basal Upkeep
            self.energy -= self.basal_upkeep

            # Apoptosis and Asymmetric Re-colonization toward under-served tiles
            dead_mask = self.energy <= 0.0
            n_dead = int(dead_mask.sum().item())
            if n_dead > 0:
                self.recolonizations += n_dead
                self.died = self.died | dead_mask
                high_energy_idx = torch.where(~dead_mask)[0]
                if len(high_energy_idx) == 0:
                    high_energy_idx = torch.tensor([0], device=self.device)
                donor_indices = high_energy_idx[
                    torch.randint(
                        0, len(high_energy_idx), (n_dead,), device=self.device
                    )
                ]
                tile_counts = torch.bincount(
                    self.niches[~dead_mask], minlength=self.n_niches
                )
                under_served_niches = torch.argsort(tile_counts)[:n_dead]
                if len(under_served_niches) < n_dead:
                    under_served_niches = under_served_niches.repeat(
                        (n_dead // len(under_served_niches)) + 1
                    )[:n_dead]

                dead_indices = torch.where(dead_mask)[0]
                self.W[dead_indices] = (
                    self.W[donor_indices].clone()
                    + self.plasticity_mask[dead_indices]
                    * (torch.randn_like(self.W[dead_indices]) * 0.01)
                )
                # Deterministic core remains pristine
                self.W[dead_indices, : self.core_rows, :] = self.w_watermarked[
                    : self.core_rows, :
                ].unsqueeze(0)
                self.velocity[dead_indices] = self.velocity[donor_indices].clone()
                self.energy[dead_indices] = self.initial_energy * 0.5
                self.niches[dead_indices] = under_served_niches
                self.accepted_updates[dead_indices] = 0

            # Strictly zero-order Mitosis (Alpha Soma vs HGT-Beta Subspace)
            x_assigned = self.X_tiles[self.niches]
            y_assigned = self.Y_tiles[self.niches]
            y_pred = torch.bmm(x_assigned, self.W)
            err_curr = torch.linalg.norm(y_pred - y_assigned, ord="fro", dim=(-2, -1))

            champs = torch.zeros(self.n_niches, dtype=torch.long, device=self.device)
            for m in range(self.n_niches):
                m_cells = torch.where(self.niches == m)[0]
                if len(m_cells) > 0:
                    best_idx = m_cells[torch.argmin(err_curr[m_cells])]
                    champs[m] = best_idx
                else:
                    champs[m] = torch.argmin(errors[:, m])

            champ_indices = champs[self.niches]
            hgt = self.W[champ_indices] - self.W
            dir_b = 0.5 * hgt + 0.5 * self.velocity[champ_indices]

            u_mut = torch.randn(self.n_cells, self.dim, self.subspace_rank, device=self.device)
            v_mut = torch.randn(self.n_cells, self.subspace_rank, self.dim, device=self.device)
            sub_mut = torch.bmm(u_mut, v_mut) * 0.012
            delta_b = self.plasticity_mask * (dir_b + sub_mut)
            w_cand_b = self.W + delta_b

            delta_a = self.plasticity_mask * (torch.randn_like(self.W) * 0.01)
            w_cand_a = self.W + delta_a

            dist_a = torch.linalg.matrix_norm(w_cand_a - self.W0, ord="fro", dim=(1, 2))
            scale_a = torch.clamp(self.r_invariant / (dist_a + 1e-8), max=1.0).unsqueeze(1).unsqueeze(2)
            w_cand_a = self.W0 + (w_cand_a - self.W0) * scale_a

            dist_b = torch.linalg.matrix_norm(w_cand_b - self.W0, ord="fro", dim=(1, 2))
            scale_b = torch.clamp(self.r_invariant / (dist_b + 1e-8), max=1.0).unsqueeze(1).unsqueeze(2)
            w_cand_b = self.W0 + (w_cand_b - self.W0) * scale_b

            err_a = torch.linalg.norm(
                torch.bmm(x_assigned, w_cand_a) - y_assigned, ord="fro", dim=(-2, -1)
            )
            err_b = torch.linalg.norm(
                torch.bmm(x_assigned, w_cand_b) - y_assigned, ord="fro", dim=(-2, -1)
            )

            improved = (err_a < err_curr) | (err_b < err_curr)
            b_beats_a = err_b < err_a
            b_won = improved & b_beats_a
            a_won = improved & (~b_beats_a)

            self.beta_wins += int(b_won.sum().item())
            self.alpha_wins += int(a_won.sum().item())
            self.velocity[b_won] = w_cand_b[b_won] - self.W[b_won]
            self.velocity[a_won] = w_cand_a[a_won] - self.W[a_won]
            self.W[b_won] = w_cand_b[b_won]
            self.W[a_won] = w_cand_a[a_won]
            self.accepted_updates[b_won | a_won] += 1

        elif mode == "dissipative_chemostat":
            # Unchanged E14 implementation preserved for direct comparison.
            x_assigned = self.X_tiles[self.niches]
            y_assigned = self.Y_tiles[self.niches]
            y_pred = torch.bmm(x_assigned, self.W)
            err_curr = torch.linalg.norm(y_pred - y_assigned, ord="fro", dim=(-2, -1))

            champs = torch.zeros(self.n_niches, dtype=torch.long, device=self.device)
            for m in range(self.n_niches):
                m_cells = torch.where(self.niches == m)[0]
                if len(m_cells) > 0:
                    best_idx = m_cells[torch.argmin(err_curr[m_cells])]
                    champs[m] = best_idx
                else:
                    champs[m] = torch.argmin(errors[:, m])

            champ_indices = champs[self.niches]
            hgt = self.W[champ_indices] - self.W
            dir_b = 0.5 * hgt + 0.5 * self.velocity[champ_indices]

            u_mut = torch.randn(self.n_cells, self.dim, self.subspace_rank, device=self.device)
            v_mut = torch.randn(self.n_cells, self.subspace_rank, self.dim, device=self.device)
            sub_mut = torch.bmm(u_mut, v_mut) * 0.012
            delta_b = self.plasticity_mask * (dir_b + sub_mut)
            w_cand_b = self.W + delta_b

            delta_a = self.plasticity_mask * (torch.randn_like(self.W) * 0.01)
            w_cand_a = self.W + delta_a

            dist_a = torch.linalg.matrix_norm(w_cand_a - self.W0, ord="fro", dim=(1, 2))
            scale_a = torch.clamp(self.r_invariant / (dist_a + 1e-8), max=1.0).unsqueeze(1).unsqueeze(2)
            w_cand_a = self.W0 + (w_cand_a - self.W0) * scale_a

            dist_b = torch.linalg.matrix_norm(w_cand_b - self.W0, ord="fro", dim=(1, 2))
            scale_b = torch.clamp(self.r_invariant / (dist_b + 1e-8), max=1.0).unsqueeze(1).unsqueeze(2)
            w_cand_b = self.W0 + (w_cand_b - self.W0) * scale_b

            err_a = torch.linalg.norm(
                torch.bmm(x_assigned, w_cand_a) - y_assigned, ord="fro", dim=(-2, -1)
            )
            err_b = torch.linalg.norm(
                torch.bmm(x_assigned, w_cand_b) - y_assigned, ord="fro", dim=(-2, -1)
            )

            improved = (err_a < err_curr) | (err_b < err_curr)
            b_beats_a = err_b < err_a
            b_won = improved & b_beats_a
            a_won = improved & (~b_beats_a)

            self.beta_wins += int(b_won.sum().item())
            self.alpha_wins += int(a_won.sum().item())
            self.velocity[b_won] = w_cand_b[b_won] - self.W[b_won]
            self.velocity[a_won] = w_cand_a[a_won] - self.W[a_won]
            self.W[b_won] = w_cand_b[b_won]
            self.W[a_won] = w_cand_a[a_won]
            self.accepted_updates[b_won | a_won] += 1

            post_errors = self.evaluate_all_tiles()
            earnings = torch.zeros(self.n_cells, self.n_niches, device=self.device)
            k_bounty = max(1, self.n_cells // (2 * self.n_niches))
            for m in range(self.n_niches):
                errs_m = post_errors[:, m]
                min_err_m = errs_m.min()
                if min_err_m < self.best_tile_error[m] - 1e-3:
                    self.best_tile_error[m] = min_err_m
                    self.chemostat_pool[m] = self.tile_bounty
                else:
                    self.chemostat_pool[m] += 0.5 * self.tile_bounty

                sense_m = torch.clamp(1.0 - (self.best_tile_error[m] / self.E0[m]), min=0.0, max=0.95)
                gap_mult = torch.clamp(1.0 / torch.clamp(1.0 - sense_m, min=0.25), max=4.0)
                eff_bounty_m = self.chemostat_pool[m] * gap_mult

                topk_vals, topk_idx = torch.topk(errs_m, k_bounty, largest=False)
                ranks = torch.arange(k_bounty, device=self.device, dtype=torch.float32)
                weights = 1.0 / (ranks + 1.0)
                shares = eff_bounty_m * (weights / weights.sum())
                earnings[topk_idx, m] += shares
                proven_soma = (self.accepted_updates[topk_idx] > 0).float()
                unlocked_shares = shares * proven_soma
                self.energy[topk_idx] += unlocked_shares

            has_earnings = earnings.max(dim=1).values > 0
            best_earn_niche = torch.argmax(earnings, dim=1)
            rel_errors = post_errors / self.E0.unsqueeze(0)
            best_fit_niche = torch.argmin(rel_errors, dim=1)
            self.niches = torch.where(has_earnings, best_earn_niche, best_fit_niche)

            self.energy -= self.basal_upkeep

            dead_mask = self.energy <= 0.0
            n_dead = int(dead_mask.sum().item())
            if n_dead > 0:
                self.recolonizations += n_dead
                self.died = self.died | dead_mask
                high_energy_idx = torch.where(~dead_mask)[0]
                if len(high_energy_idx) == 0:
                    high_energy_idx = torch.tensor([0], device=self.device)
                donor_indices = high_energy_idx[
                    torch.randint(
                        0, len(high_energy_idx), (n_dead,), device=self.device
                    )
                ]
                tile_counts = torch.bincount(
                    self.niches[~dead_mask], minlength=self.n_niches
                ).float()
                flux_priority = self.chemostat_pool / (tile_counts + 1.0)
                target_niches = torch.argsort(flux_priority, descending=True)[:n_dead]
                if len(target_niches) < n_dead:
                    target_niches = target_niches.repeat(
                        (n_dead // len(target_niches)) + 1
                    )[:n_dead]

                dead_indices = torch.where(dead_mask)[0]
                is_spore = (torch.arange(n_dead, device=self.device) % 2) == 1
                self.spore_births += int(is_spore.sum().item())

                u_sp = torch.randn(n_dead, self.dim, self.subspace_rank, device=self.device)
                v_sp = torch.randn(n_dead, self.subspace_rank, self.dim, device=self.device)
                spore_probe = torch.bmm(u_sp, v_sp) * 0.02

                soma_w = (
                    self.W[donor_indices].clone()
                    + self.plasticity_mask[dead_indices]
                    * (torch.randn_like(self.W[dead_indices]) * 0.01)
                )
                spore_w = (
                    self.W0[dead_indices].clone()
                    + self.plasticity_mask[dead_indices] * spore_probe
                )
                self.W[dead_indices] = torch.where(
                    is_spore.unsqueeze(1).unsqueeze(2), spore_w, soma_w
                )
                self.W[dead_indices, : self.core_rows, :] = self.w_watermarked[
                    : self.core_rows, :
                ].unsqueeze(0)
                self.velocity[dead_indices] = self.velocity[donor_indices].clone()
                self.energy[dead_indices] = self.initial_energy * 0.5
                self.niches[dead_indices] = target_niches
                self.accepted_updates[dead_indices] = 0

        elif mode == "graded_chemostat":
            # E15 Repaired L2 Chemostat:
            # 1. Zero-order Mitosis with optional homeostatic step-scale regulation
            x_assigned = self.X_tiles[self.niches]
            y_assigned = self.Y_tiles[self.niches]
            y_pred = torch.bmm(x_assigned, self.W)
            err_curr = torch.linalg.norm(y_pred - y_assigned, ord="fro", dim=(-2, -1))

            cell_tension = 15.0 + 35.0 * (err_curr / (self.E0[self.niches] + 1e-8))
            self.mean_tension = float(cell_tension.mean().item())

            champs = torch.zeros(self.n_niches, dtype=torch.long, device=self.device)
            for m in range(self.n_niches):
                m_cells = torch.where(self.niches == m)[0]
                if len(m_cells) > 0:
                    best_idx = m_cells[torch.argmin(err_curr[m_cells])]
                    champs[m] = best_idx
                else:
                    champs[m] = torch.argmin(errors[:, m])

            champ_indices = champs[self.niches]
            hgt = self.W[champ_indices] - self.W
            dir_b = 0.5 * hgt + 0.5 * self.velocity[champ_indices]

            scale_b_step = self.step_scale.view(self.n_cells, 1, 1)
            scale_a_step = scale_b_step * (0.01 / 0.012)

            u_mut = torch.randn(self.n_cells, self.dim, self.subspace_rank, device=self.device)
            v_mut = torch.randn(self.n_cells, self.subspace_rank, self.dim, device=self.device)
            sub_mut = torch.bmm(u_mut, v_mut) * scale_b_step
            delta_b = self.plasticity_mask * (dir_b + sub_mut)
            w_cand_b = self.W + delta_b

            delta_a = self.plasticity_mask * (torch.randn_like(self.W) * scale_a_step)
            w_cand_a = self.W + delta_a

            dist_a = torch.linalg.matrix_norm(w_cand_a - self.W0, ord="fro", dim=(1, 2))
            proj_a = torch.clamp(self.r_invariant / (dist_a + 1e-8), max=1.0).unsqueeze(1).unsqueeze(2)
            w_cand_a = self.W0 + (w_cand_a - self.W0) * proj_a

            dist_b = torch.linalg.matrix_norm(w_cand_b - self.W0, ord="fro", dim=(1, 2))
            proj_b = torch.clamp(self.r_invariant / (dist_b + 1e-8), max=1.0).unsqueeze(1).unsqueeze(2)
            w_cand_b = self.W0 + (w_cand_b - self.W0) * proj_b

            err_a = torch.linalg.norm(
                torch.bmm(x_assigned, w_cand_a) - y_assigned, ord="fro", dim=(-2, -1)
            )
            err_b = torch.linalg.norm(
                torch.bmm(x_assigned, w_cand_b) - y_assigned, ord="fro", dim=(-2, -1)
            )

            improved = (err_a < err_curr) | (err_b < err_curr)
            b_beats_a = err_b < err_a
            b_won = improved & b_beats_a
            a_won = improved & (~b_beats_a)

            self.beta_wins += int(b_won.sum().item())
            self.alpha_wins += int(a_won.sum().item())
            self.velocity[b_won] = w_cand_b[b_won] - self.W[b_won]
            self.velocity[a_won] = w_cand_a[a_won] - self.W[a_won]
            self.W[b_won] = w_cand_b[b_won]
            self.W[a_won] = w_cand_a[a_won]
            self.accepted_updates[b_won | a_won] += 1

            if self.adaptive_step:
                self.step_scale[improved] = torch.clamp(
                    self.step_scale[improved] * 1.03, max=0.016
                )
                self.step_scale[~improved] = torch.clamp(
                    self.step_scale[~improved] * 0.90, min=0.0010
                )

            # 2. Unsolved-gap allocation rule and mass-conserving pool + Law 2a
            post_errors = self.evaluate_all_tiles()
            min_errs = post_errors.min(dim=0).values
            self.best_tile_error = torch.minimum(self.best_tile_error, min_errs)

            unsolved_gap = torch.clamp(
                self.best_tile_error / (self.E0 + 1e-8), min=0.05, max=1.0
            )
            gap_mult = torch.clamp(
                (unsolved_gap / unsolved_gap.mean()) ** 2, min=0.25, max=4.0
            )

            unlocked_earnings = torch.zeros(self.n_cells, self.n_niches, device=self.device)
            k_bounty = max(1, self.n_cells // (2 * self.n_niches))
            ranks = torch.arange(k_bounty, device=self.device, dtype=torch.float32)
            rank_weights = (1.0 / (ranks + 1.0))
            rank_weights = rank_weights / rank_weights.sum()

            for m in range(self.n_niches):
                self.chemostat_pool[m] = torch.clamp(
                    self.chemostat_pool[m] + 0.5 * self.tile_bounty * gap_mult[m],
                    max=8.0 * self.tile_bounty,
                )
                offer_m = torch.minimum(
                    self.chemostat_pool[m], self.tile_bounty * gap_mult[m]
                )
                errs_m = post_errors[:, m]
                _, topk_idx = torch.topk(errs_m, k_bounty, largest=False)
                shares = offer_m * rank_weights
                proven_soma = (self.accepted_updates[topk_idx] > 0).float()
                unlocked_shares = shares * proven_soma
                unlocked_earnings[topk_idx, m] += unlocked_shares
                self.energy[topk_idx] += unlocked_shares
                self.chemostat_pool[m] = torch.clamp(
                    self.chemostat_pool[m] - unlocked_shares.sum(), min=0.0
                )

            # Ecological Niche Binding toward gap-potentiated reward
            has_earnings = unlocked_earnings.max(dim=1).values > 0
            best_earn_niche = torch.argmax(unlocked_earnings, dim=1)
            rel_errors = post_errors / (self.E0.unsqueeze(0) + 1e-8)
            forage_utility = (gap_mult * (self.chemostat_pool / self.tile_bounty)).unsqueeze(0) / (
                rel_errors + 1e-6
            )
            best_forage_niche = torch.argmax(forage_utility, dim=1)
            self.niches = torch.where(has_earnings, best_earn_niche, best_forage_niche)

            # Law 2a Irreversible Soma Drain
            self.energy -= self.basal_upkeep

            # 3. Repaired Niche-Clean Law 2c: Bresenham Spore Quota + Same-Niche Soma Donors
            dead_mask = self.energy <= 0.0
            n_dead = int(dead_mask.sum().item())
            if n_dead > 0:
                prev_recol = self.recolonizations
                self.recolonizations += n_dead
                self.died = self.died | dead_mask
                alive_mask = ~dead_mask
                alive_idx = torch.where(alive_mask)[0]
                if len(alive_idx) == 0:
                    alive_idx = torch.tensor([0], device=self.device)

                tile_counts = torch.bincount(
                    self.niches[alive_mask], minlength=self.n_niches
                ).float()
                flux_priority = (self.chemostat_pool * gap_mult) / (tile_counts + 1.0)
                ranked_niches = torch.argsort(flux_priority, descending=True)
                target_niches = ranked_niches.repeat(
                    (n_dead // self.n_niches) + 1
                )[:n_dead]

                cum_idx = torch.arange(
                    prev_recol, prev_recol + n_dead, device=self.device, dtype=torch.float32
                )
                is_spore = torch.floor((cum_idx + 1.0) * self.spore_fraction) > torch.floor(
                    cum_idx * self.spore_fraction
                )
                self.spore_births += int(is_spore.sum().item())

                dead_indices = torch.where(dead_mask)[0]
                donor_indices = alive_idx[
                    torch.randint(0, len(alive_idx), (n_dead,), device=self.device)
                ]
                same_niche_donor = torch.zeros(n_dead, dtype=torch.bool, device=self.device)
                for k in range(n_dead):
                    tn = int(target_niches[k].item())
                    cand_donors = alive_idx[self.niches[alive_idx] == tn]
                    if len(cand_donors) > 0:
                        best_local = cand_donors[torch.argmax(self.energy[cand_donors])]
                        donor_indices[k] = best_local
                        same_niche_donor[k] = True

                u_sp = torch.randn(n_dead, self.dim, self.subspace_rank, device=self.device)
                v_sp = torch.randn(n_dead, self.subspace_rank, self.dim, device=self.device)
                spore_probe = torch.bmm(u_sp, v_sp) * 0.012

                soma_w = (
                    self.W[donor_indices].clone()
                    + self.plasticity_mask[dead_indices]
                    * (torch.randn_like(self.W[dead_indices]) * 0.008)
                )
                spore_w = (
                    self.W0[dead_indices].clone()
                    + self.plasticity_mask[dead_indices] * spore_probe
                )
                self.W[dead_indices] = torch.where(
                    is_spore.unsqueeze(1).unsqueeze(2), spore_w, soma_w
                )
                self.W[dead_indices, : self.core_rows, :] = self.w_watermarked[
                    : self.core_rows, :
                ].unsqueeze(0)

                clean_vel = torch.where(
                    (~is_spore & same_niche_donor).unsqueeze(1).unsqueeze(2),
                    self.velocity[donor_indices].clone(),
                    torch.zeros_like(self.velocity[dead_indices]),
                )
                self.velocity[dead_indices] = clean_vel
                self.step_scale[dead_indices] = torch.where(
                    is_spore,
                    torch.full((n_dead,), 0.012, dtype=torch.float32, device=self.device),
                    self.step_scale[donor_indices].clone(),
                )
                self.energy[dead_indices] = self.initial_energy * 0.5
                self.niches[dead_indices] = target_niches
                self.accepted_updates[dead_indices] = 0
        else:
            raise ValueError(f"Unknown mode: {mode!r}")

        self.generation += 1

        if self.device.type == "mps":
            torch.mps.synchronize()
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        # Calculate structured telemetry
        final_errors = self.evaluate_all_tiles()
        self.best_tile_error = torch.minimum(
            self.best_tile_error, final_errors.min(dim=0).values
        )
        per_tile_best_ratio = self.best_tile_error / (self.E0 + 1e-8)
        worst_tile_err_ratio = float(per_tile_best_ratio.max().item())

        min_tile_err_ratio = float(
            (final_errors.min(dim=1).values / self.E0.min()).mean().item()
        )
        assigned_err = final_errors[
            torch.arange(self.n_cells, device=self.device), self.niches
        ]
        assigned_err_ratio = float(
            (assigned_err / self.E0[self.niches]).mean().item()
        )

        total_wins = self.alpha_wins + self.beta_wins
        beta_win_share = float(self.beta_wins / max(1, total_wins))

        unique_niches = torch.unique(self.niches)
        niche_coverage = float(len(unique_niches) / self.n_niches)

        counts = torch.bincount(self.niches, minlength=self.n_niches).float()
        probs = counts / float(self.n_cells)
        nonzero_probs = probs[probs > 0]
        niche_entropy_bits = float(
            -torch.sum(nonzero_probs * torch.log2(nonzero_probs)).item()
        )

        core_drift = float(
            torch.max(
                torch.linalg.matrix_norm(
                    self.W[:, : self.core_rows, :] - self.W0[:, : self.core_rows, :],
                    ord="fro",
                )
            ).item()
        )

        resps = torch.matmul(self.W.transpose(1, 2), self.trigger_vec)
        cos_sims = torch.nn.functional.cosine_similarity(
            resps, self.target_id.unsqueeze(0), dim=1
        )
        min_watermark_cosine = float(torch.min(cos_sims).item())

        max_committed_dist = float(
            torch.max(
                torch.linalg.matrix_norm(self.W - self.W0, ord="fro", dim=(1, 2))
            ).item()
        )

        idle_surviving_cells = int(
            ((~self.died) & (self.accepted_updates == 0)).sum().item()
        )

        self.sync_to_arena()

        return {
            "generation": self.generation,
            "mode": mode,
            "alpha_wins": self.alpha_wins,
            "beta_wins": self.beta_wins,
            "beta_win_share": beta_win_share,
            "mean_min_tile_error_ratio": min_tile_err_ratio,
            "mean_assigned_error_ratio": assigned_err_ratio,
            "worst_tile_error_ratio": worst_tile_err_ratio,
            "per_tile_best_error_ratio": [float(x) for x in per_tile_best_ratio.detach().cpu().tolist()],
            "tile_cell_counts": [int(x) for x in counts.detach().cpu().tolist()],
            "niche_coverage": niche_coverage,
            "niche_entropy_bits": niche_entropy_bits,
            "max_core_drift": core_drift,
            "min_watermark_cosine": min_watermark_cosine,
            "max_committed_distance": max_committed_dist,
            "apoptosis_recolonizations": self.recolonizations,
            "spore_births": self.spore_births,
            "mean_chemostat_pool": float(self.chemostat_pool.mean().item()),
            "mean_step_scale": float(self.step_scale.mean().item()),
            "idle_surviving_cells": idle_surviving_cells,
            "elapsed_ms": elapsed_ms,
        }

    def run(self, generations: int = 60, mode: str = "hgt_foraging") -> Dict[str, Any]:
        """Run multiple generations and return the final telemetry dictionary."""
        telemetry: Dict[str, Any] = {}
        for _ in range(generations):
            telemetry = self.step(mode=mode)
        return telemetry


def run_swarm_loom_cycle(
    n_cells: int = 256,
    dim: int = 128,
    n_niches: int = 8,
    generations: int = 10,
    mode: str = "hgt_foraging",
    device: Optional[str] = None,
    seed: int = 0,
) -> Dict[str, Any]:
    """Execute a swarm loom cycle with an ephemeral shared memory arena."""
    shm_name = f"weft_sw_{os.getpid()}_{int(time.time()) % 100000}"
    arena = StratifiedSwarmArena(
        name=shm_name,
        n_cells=n_cells,
        dim=dim,
        n_niches=n_niches,
        create=True,
    )
    colony = VectorizedPlasmColony(
        device=device,
        n_cells=n_cells,
        dim=dim,
        n_niches=n_niches,
        seed=seed,
        arena=arena,
    )
    try:
        report = colony.run(generations=generations, mode=mode)
    finally:
        arena.close(unlink=True)
    return report
