#!/usr/bin/env python3
"""
Apple Silicon Metal Performance Engine (Lineage Alpha / Lineage Beta mitosis loop).
Extracted from weft/mac.md. Uses MPS when available; falls back to CPU for CI/Linux.
"""

from __future__ import annotations

import argparse
import json
import sys

import numpy as np

try:
    import torch
except ImportError:  # pragma: no cover
    torch = None  # type: ignore


class AppleSiliconLoomEngine:
    def __init__(self, token_dim: int = 512, seq_len: int = 64):
        if torch is None:
            raise RuntimeError("torch is required for metal_loom")
        self.dim = token_dim
        self.seq_len = seq_len
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
            self.backend = "mps"
        else:
            self.device = torch.device("cpu")
            self.backend = "cpu"
        self.core_weights = torch.randn(self.dim, self.dim, device=self.device) * 0.02
        self.system_tension = 12.0
        self.metabolic_budget = 100.0
        self.step = 1
        self.last_winner = "LINEAGE_ALPHA [SAFE]"

    def execute_evolutionary_generation(self) -> dict:
        live = torch.randn(self.seq_len, self.dim, device=self.device) * 1.5
        lora_a = torch.randn(self.dim, 2, device=self.device) * 0.005
        lora_b = torch.randn(self.dim, 2, device=self.device) * 0.22
        with torch.no_grad():
            out_a = torch.matmul(live, self.core_weights + torch.matmul(lora_a, lora_a.t()))
            out_b = torch.matmul(live, self.core_weights + torch.matmul(lora_b, lora_b.t()))
            loss_a = float(torch.norm(out_a).item())
            loss_b = float(torch.norm(out_b).item())
        if loss_a < loss_b:
            winner = "LINEAGE_ALPHA [SAFE]"
            self.system_tension = loss_a
            self.core_weights += torch.matmul(lora_a, lora_a.t()) * 0.15
        else:
            winner = "LINEAGE_BETA [BOLD]"
            self.system_tension = loss_b
            self.core_weights += torch.matmul(lora_b, lora_b.t()) * 0.15
        decay_pressure = 0.04 * (1.0 + (1.0 / (self.system_tension + 1e-5)))
        self.core_weights *= 1.0 - (decay_pressure * 0.01)
        self.last_winner = winner
        self.metabolic_budget -= 2.5
        self.step += 1
        return {
            "step": self.step,
            "winner": winner,
            "loss_a": round(loss_a, 4),
            "loss_b": round(loss_b, 4),
            "system_tension": round(self.system_tension, 4),
            "metabolic_budget": round(self.metabolic_budget, 2),
            "backend": self.backend,
        }


def run_self_test(cycles: int = 3) -> dict:
    loom = AppleSiliconLoomEngine(token_dim=64, seq_len=8)
    trace = [loom.execute_evolutionary_generation() for _ in range(cycles)]
    ok = all(t["system_tension"] > 0 for t in trace)
    return {"status": "PASS" if ok else "FAIL", "cycles": trace}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--cycles", type=int, default=3)
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(run_self_test(args.cycles), indent=2))
        return 0 if run_self_test(args.cycles)["status"] == "PASS" else 1
    loom = AppleSiliconLoomEngine()
    for _ in range(args.cycles):
        loom.execute_evolutionary_generation()
    return 0


if __name__ == "__main__":
    sys.exit(main())
