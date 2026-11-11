#!/usr/bin/env python3
"""
Unit tests for Apple Silicon Swarm Loom (`weft/runtime/mac/swarm_loom.py`).
Verifies:
  1. StratifiedSwarmArena zero-copy shared memory lifecycle and teardown.
  2. Strict C1 core provenance watermark retention and C2 Frobenius ball gate.
  3. Comparative mitotic performance: hgt_foraging vs paper1_blind.
  4. MPS hardware device acceleration when available.
"""

from __future__ import annotations

import gc
import os
import unittest
import uuid

import numpy as np
import torch

from weft.runtime.mac.swarm_loom import (
    SWARM_HEADER_SIZE,
    StratifiedSwarmArena,
    VectorizedPlasmColony,
    compute_swarm_arena_size,
    run_swarm_loom_cycle,
)


class TestStratifiedSwarmArena(unittest.TestCase):
    """Test POSIX shared memory buffer allocation, zero-copy mutations, and clean release."""

    def setUp(self) -> None:
        self.arena_name = f"weft_t_{uuid.uuid4().hex[:14]}"
        self.n_cells = 64
        self.dim = 32
        self.n_niches = 4

    def tearDown(self) -> None:
        try:
            arena = StratifiedSwarmArena(name=self.arena_name, create=False)
            arena.close(unlink=True)
        except FileNotFoundError:
            pass

    def test_arena_creation_and_zero_copy_exchange(self) -> None:
        expected_size = compute_swarm_arena_size(self.n_cells, self.dim)
        with StratifiedSwarmArena(
            name=self.arena_name,
            n_cells=self.n_cells,
            dim=self.dim,
            n_niches=self.n_niches,
            create=True,
        ) as arena:
            self.assertEqual(arena.size, expected_size)
            self.assertEqual(arena.header_view.colony_size, self.n_cells)
            self.assertEqual(arena.header_view.dim, self.dim)
            self.assertEqual(arena.header_view.n_niches, self.n_niches)
            self.assertEqual(arena.focal_weights.shape, (self.n_cells, self.dim, self.dim))
            self.assertEqual(arena.energy_ledger.shape, (self.n_cells,))
            self.assertEqual(arena.niche_specialization.shape, (self.n_cells,))

            # Modify views in producer
            arena.focal_weights[0, 1, 2] = 42.125
            arena.energy_ledger[5] = 99.5
            arena.niche_specialization[3] = 2
            arena.header_view.generation_epoch = 12

            # Open raw consumer view onto same segment
            consumer = StratifiedSwarmArena(name=self.arena_name, create=False)
            try:
                self.assertEqual(consumer.n_cells, self.n_cells)
                self.assertEqual(consumer.dim, self.dim)
                self.assertEqual(consumer.focal_weights[0, 1, 2], 42.125)
                self.assertEqual(consumer.energy_ledger[5], 99.5)
                self.assertEqual(consumer.niche_specialization[3], 2)
                self.assertEqual(consumer.header_view.generation_epoch, 12)
            finally:
                consumer.close(unlink=False)

    def test_clean_close_and_unlink_prevents_buffer_error(self) -> None:
        """Verify release_views and close unlink cleanly without BufferError."""
        arena = StratifiedSwarmArena(
            name=self.arena_name,
            n_cells=16,
            dim=16,
            n_niches=2,
            create=True,
        )
        _ = arena.focal_weights[0, 0, 0]
        arena.close(unlink=True)
        self.assertTrue(arena._closed)
        gc.collect()


class TestVectorizedPlasmColonyInvariants(unittest.TestCase):
    """Verify C1 core-periphery watermark contract and C2 Frobenius ball safety."""

    def test_invariants_across_all_modes(self) -> None:
        for mode in ["paper1_blind", "hgt_isolated", "hgt_foraging", "dissipative_chemostat"]:
            with self.subTest(mode=mode):
                colony = VectorizedPlasmColony(
                    device="cpu",
                    n_cells=64,
                    dim=32,
                    n_niches=4,
                    r_invariant=10.0,
                    seed=42,
                )
                try:
                    telemetry = colony.run(generations=15, mode=mode)
                    # C1 Invariants
                    self.assertEqual(telemetry["max_core_drift"], 0.0)
                    self.assertGreaterEqual(telemetry["min_watermark_cosine"], 0.999999)
                    # C2 Invariant
                    self.assertLessEqual(telemetry["max_committed_distance"], 10.0)
                finally:
                    colony.close()


class TestMitoticRegimesComparison(unittest.TestCase):
    """Verify that hgt_foraging outperforms paper1_blind on beta share and niche coverage."""

    def test_hgt_foraging_beats_paper1_blind(self) -> None:
        # Run paper1_blind
        colony_blind = VectorizedPlasmColony(
            device="cpu",
            n_cells=64,
            dim=32,
            n_niches=4,
            seed=10,
        )
        report_blind = colony_blind.run(generations=25, mode="paper1_blind")
        colony_blind.close()

        # Run hgt_foraging
        colony_foraging = VectorizedPlasmColony(
            device="cpu",
            n_cells=64,
            dim=32,
            n_niches=4,
            seed=10,
        )
        report_foraging = colony_foraging.run(generations=25, mode="hgt_foraging")
        colony_foraging.close()

        # Beta win share
        self.assertLess(report_blind["beta_win_share"], 0.05)
        self.assertGreater(report_foraging["beta_win_share"], 0.50)

        # Niche coverage
        self.assertEqual(report_foraging["niche_coverage"], 1.0)

        # Error reduction
        self.assertLess(
            report_foraging["mean_min_tile_error_ratio"],
            report_blind["mean_min_tile_error_ratio"],
        )


class TestMpsHardwareAcceleration(unittest.TestCase):
    """Verify Apple Silicon MPS hardware execution when available."""

    def test_mps_execution(self) -> None:
        if not (hasattr(torch.backends, "mps") and torch.backends.mps.is_available()):
            self.skipTest("Apple Silicon MPS not available on this host")

        colony = VectorizedPlasmColony(
            device="mps",
            n_cells=128,
            dim=64,
            n_niches=4,
            seed=7,
        )
        try:
            report = colony.run(generations=10, mode="hgt_foraging")
            self.assertEqual(report["generation"], 10)
            self.assertEqual(report["max_core_drift"], 0.0)
            self.assertGreaterEqual(report["min_watermark_cosine"], 0.999999)
            self.assertEqual(report["niche_coverage"], 1.0)
            self.assertGreater(report["elapsed_ms"], 0.0)
        finally:
            colony.close()


if __name__ == "__main__":
    unittest.main()
