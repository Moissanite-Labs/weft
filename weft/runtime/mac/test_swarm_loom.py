#!/usr/bin/env python3
"""
Unit tests for Apple Silicon Swarm Loom (`weft/runtime/mac/swarm_loom.py`).
Verifies:
  1. StratifiedSwarmArena zero-copy shared memory lifecycle and teardown.
  2. Strict C1 core provenance watermark retention and C2 Frobenius ball gate
     across all 5 modes (including `graded_chemostat` and graded tile ladders).
  3. Comparative mitotic performance: hgt_foraging vs paper1_blind, and
     graded_chemostat zero-coasting + spore_fraction quota behavior.
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
    within_shard_midrank_pool,
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
        except (FileNotFoundError, PermissionError):
            pass

    def test_arena_creation_and_zero_copy_exchange(self) -> None:
        expected_size = compute_swarm_arena_size(self.n_cells, self.dim)
        try:
            arena_ctx = StratifiedSwarmArena(
                name=self.arena_name,
                n_cells=self.n_cells,
                dim=self.dim,
                n_niches=self.n_niches,
                create=True,
            )
        except PermissionError as exc:
            self.skipTest(f"POSIX shm_open blocked by sandbox: {exc}")

        with arena_ctx as arena:
            self.assertEqual(arena.size, expected_size)
            self.assertEqual(arena.header_view.colony_size, self.n_cells)
            self.assertEqual(arena.header_view.dim, self.dim)
            self.assertEqual(arena.header_view.n_niches, self.n_niches)
            self.assertEqual(arena.focal_weights.shape, (self.n_cells, self.dim, self.dim))
            self.assertEqual(arena.energy_ledger.shape, (self.n_cells,))
            self.assertEqual(arena.niche_specialization.shape, (self.n_cells,))

            arena.focal_weights[0, 1, 2] = 42.125
            arena.energy_ledger[5] = 99.5
            arena.niche_specialization[3] = 2
            arena.header_view.generation_epoch = 12

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
        try:
            arena = StratifiedSwarmArena(
                name=self.arena_name,
                n_cells=16,
                dim=16,
                n_niches=2,
                create=True,
            )
        except PermissionError as exc:
            self.skipTest(f"POSIX shm_open blocked by sandbox: {exc}")
        _ = arena.focal_weights[0, 0, 0]
        arena.close(unlink=True)
        self.assertTrue(arena._closed)
        gc.collect()


class TestVectorizedPlasmColonyInvariants(unittest.TestCase):
    """Verify C1 core-periphery watermark contract and C2 Frobenius ball safety."""

    def test_invariants_across_all_modes(self) -> None:
        modes = [
            "paper1_blind",
            "hgt_isolated",
            "hgt_foraging",
            "dissipative_chemostat",
            "graded_chemostat",
        ]
        for mode in modes:
            with self.subTest(mode=mode):
                colony = VectorizedPlasmColony(
                    device="cpu",
                    n_cells=64,
                    dim=32,
                    n_niches=4,
                    r_invariant=10.0,
                    seed=42,
                    tile_ranks=[1, 2, 4, 8] if mode == "graded_chemostat" else None,
                    tile_condition_numbers=[1.0, 2.0, 4.0, 8.0] if mode == "graded_chemostat" else None,
                    spore_fraction=0.25,
                    adaptive_step=(mode == "graded_chemostat"),
                )
                try:
                    telemetry = colony.run(generations=15, mode=mode)
                    self.assertEqual(telemetry["max_core_drift"], 0.0)
                    self.assertGreaterEqual(telemetry["min_watermark_cosine"], 0.999999)
                    self.assertLessEqual(telemetry["max_committed_distance"], 10.0)
                finally:
                    colony.close()

    def test_graded_chemostat_spore_quota_bounds(self) -> None:
        colony_zero = VectorizedPlasmColony(
            device="cpu",
            n_cells=64,
            dim=32,
            n_niches=4,
            initial_energy=10.0,
            basal_upkeep=4.0,
            seed=5,
            spore_fraction=0.0,
        )
        rep_zero = colony_zero.run(generations=10, mode="graded_chemostat")
        colony_zero.close()
        self.assertEqual(rep_zero["spore_births"], 0)
        self.assertEqual(rep_zero["idle_surviving_cells"], 0)


class TestMitoticRegimesComparison(unittest.TestCase):
    """Verify that hgt_foraging outperforms paper1_blind on beta share and niche coverage."""

    def test_hgt_foraging_beats_paper1_blind(self) -> None:
        colony_blind = VectorizedPlasmColony(
            device="cpu",
            n_cells=64,
            dim=32,
            n_niches=4,
            seed=10,
        )
        report_blind = colony_blind.run(generations=25, mode="paper1_blind")
        colony_blind.close()

        colony_foraging = VectorizedPlasmColony(
            device="cpu",
            n_cells=64,
            dim=32,
            n_niches=4,
            seed=10,
        )
        report_foraging = colony_foraging.run(generations=25, mode="hgt_foraging")
        colony_foraging.close()

        self.assertLess(report_blind["beta_win_share"], 0.05)
        self.assertGreater(report_foraging["beta_win_share"], 0.50)
        self.assertEqual(report_foraging["niche_coverage"], 1.0)
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


class TestWithinShardMidrankPool(unittest.TestCase):
    """Cross-shard pooling by within-shard mid-rank percentile."""

    SHARDS = [
        [(0, 5.00), (1, 5.20), (2, 4.80)],
        [(0, 5.10), (1, 5.30), (2, 4.90)],
        [(1, -4.80), (2, -5.20)],
    ]

    def test_raw_mean_misorders_but_midrank_keeps_dominance(self) -> None:
        # Cell 1 beats cell 0 and cell 2 on every shard it shares with them,
        # but cell 0 only appears on the two high-baseline shards.
        # This fixture is one case where the pool keeps the shared-shard
        # order. It is a single example, not a general guarantee: the pool is
        # an unweighted mean over each cell's own shards, so once the shard
        # sets differ a cell can lose to one it beats on every shared shard.
        # test_unweighted_mean_can_drop_shared_shard_dominance pins a witness
        # (pools 0.25 vs 0.19125).
        raw = {}
        for shard in self.SHARDS:
            for cid, s in shard:
                raw.setdefault(cid, []).append(s)
        raw_mean = {cid: sum(v) / len(v) for cid, v in raw.items()}
        self.assertGreater(raw_mean[0], raw_mean[1])
        pooled = within_shard_midrank_pool(self.SHARDS)
        self.assertGreater(pooled[1], pooled[0])
        self.assertGreater(pooled[0], pooled[2])

    def test_invariant_under_per_shard_monotone_rescaling(self) -> None:
        base = within_shard_midrank_pool(self.SHARDS)
        shifted = [
            [(cid, 3.0 * s + 100.0) for cid, s in self.SHARDS[0]],
            [(cid, s - 7.5) for cid, s in self.SHARDS[1]],
            [(cid, 0.25 * s + 1e6) for cid, s in self.SHARDS[2]],
        ]
        self.assertEqual(within_shard_midrank_pool(shifted), base)

    def test_unweighted_mean_can_drop_shared_shard_dominance(self) -> None:
        # Cell 1 beats cell 0 on the only shard they share, then is the
        # unique minimum of three 100-cell shards that cell 0 is absent from.
        shared = [(0, 1.0), (1, 2.0)]
        extra = [[(1, 0.0)] + [(cid, 1.0 + cid) for cid in range(100, 199)]
                 for _ in range(3)]
        pooled = within_shard_midrank_pool([shared] + extra)
        self.assertEqual(pooled[0], 0.25)
        self.assertAlmostEqual(pooled[1], 0.19125, places=12)
        self.assertGreater(pooled[0], pooled[1])

    def test_invariance_needs_order_and_ties_preserved_in_float64(self) -> None:
        base = within_shard_midrank_pool([[(0, 0.0), (1, 1.0)]])
        self.assertEqual(base, {0: 0.25, 1: 0.75})
        # Adding 1e16 is increasing on the reals but rounds both scores to
        # the same float64, so the two cells tie.
        self.assertEqual(0.0 + 1e16, 1.0 + 1e16)
        shifted = within_shard_midrank_pool([[(0, 0.0 + 1e16), (1, 1.0 + 1e16)]])
        self.assertEqual(shifted, {0: 0.5, 1: 0.5})
        # Integers go through float() first and tie the same way.
        ints = within_shard_midrank_pool([[(0, 10**16), (1, 10**16 + 1)]])
        self.assertEqual(ints, {0: 0.5, 1: 0.5})
        # A shift that keeps the float64 order and ties leaves the pool alone.
        self.assertEqual(
            within_shard_midrank_pool([[(0, 0.0 + 1e6), (1, 1.0 + 1e6)]]), base
        )

    def test_ties_take_the_midrank(self) -> None:
        pooled = within_shard_midrank_pool([[(0, 1.0), (1, 1.0), (2, 2.0), (3, 0.0)]])
        self.assertEqual(pooled[0], 0.5)
        self.assertEqual(pooled[1], 0.5)
        self.assertEqual(pooled[2], 0.875)
        self.assertEqual(pooled[3], 0.125)

    def test_empty_shards_are_skipped(self) -> None:
        self.assertEqual(within_shard_midrank_pool([[], [(4, 2.0)]]), {4: 0.5})
        self.assertEqual(within_shard_midrank_pool([]), {})

    def test_rejects_non_finite_scores_and_duplicate_cells(self) -> None:
        with self.assertRaises(ValueError):
            within_shard_midrank_pool([[(0, float("nan")), (1, 1.0)]])
        with self.assertRaises(ValueError):
            within_shard_midrank_pool([[(0, float("inf")), (1, 1.0)]])
        with self.assertRaises(ValueError):
            within_shard_midrank_pool([[(0, 1.0), (0, 2.0)]])


if __name__ == "__main__":
    unittest.main()
