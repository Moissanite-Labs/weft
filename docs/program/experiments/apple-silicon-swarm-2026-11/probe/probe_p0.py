#!/usr/bin/env python3
"""
Probe P0: the first test of the E14 ideas, before swarm_loom.py existed.

Run on 2026-11-10 as an inline command (task-265 in the agy-orbit session).
This file is that command, unchanged in logic, with a seed argument and JSON output.

Question: in a batched colony on Apple Silicon MPS, does a Beta lineage that uses
rank-4 subspace mutation plus horizontal transfer from the niche's best cell win
where Paper 1's isotropic Beta (5x Alpha noise) does not?

Setup: 512 cells, 256x256 matrices, 64 frozen core rows, 4 niches of 128 cells,
C2 radius 15.0, 100 generations. Zero-order: forward errors only. The niche's best
cell gets W_best - W_cur = 0, so its Beta move is the low-rank term alone.

Usage:
  python3 probe_p0.py                 # seed 0, the original run
  python3 probe_p0.py --seeds 0-9     # robustness check
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import torch


def run(seed: int, device: str) -> dict:
    torch.manual_seed(seed)
    N, D, CORE, R = 512, 256, 64, 15.0

    X = torch.randn(4, 32, D, device=device).repeat_interleave(128, dim=0)
    W_true = torch.randn(4, D, D, device=device).repeat_interleave(128, dim=0) * 0.2
    Y = torch.bmm(X, W_true)

    W0 = torch.randn(N, D, D, device=device) * 0.05
    mask = torch.ones(1, D, D, device=device)
    mask[:, :CORE, :] = 0.0

    def run_colony(mode: str):
        W_cur = W0.clone()
        a_wins = b_wins = 0
        for _ in range(100):
            err_0 = torch.linalg.matrix_norm(torch.bmm(X, W_cur) - Y, ord="fro")
            # Daughter A: cautious isotropic mutation (Paper 1 Alpha)
            Wa = W_cur + torch.randn_like(W_cur) * 0.005 * mask
            if mode == "blind_beta":
                # Paper 1 Beta: larger isotropic noise
                Wb = W_cur + torch.randn_like(W_cur) * 0.025 * mask
            else:
                # Rank-4 subspace mutation + horizontal transfer from best peer in niche
                niche_err = err_0.view(4, 128)
                best_idx = niche_err.argmin(dim=1) + torch.arange(4, device=device) * 128
                W_best = W_cur[best_idx].repeat_interleave(128, dim=0)
                u = torch.randn(N, D, 4, device=device)
                v = torch.randn(N, 4, D, device=device)
                low_rank = torch.bmm(u, v) * 0.008
                Wb = W_cur + (0.35 * (W_best - W_cur) + low_rank) * mask

            err_a = torch.linalg.matrix_norm(torch.bmm(X, Wa) - Y, ord="fro")
            err_b = torch.linalg.matrix_norm(torch.bmm(X, Wb) - Y, ord="fro")
            dist_a = torch.linalg.matrix_norm(Wa - W0, ord="fro")
            dist_b = torch.linalg.matrix_norm(Wb - W0, ord="fro")
            ok_a = (dist_a <= R) & (err_a < err_0) & ((err_a <= err_b) | (dist_b > R))
            ok_b = (dist_b <= R) & (err_b < err_0) & ((err_b < err_a) | (dist_a > R))
            W_cur = torch.where(ok_b[:, None, None], Wb, torch.where(ok_a[:, None, None], Wa, W_cur))
            a_wins += ok_a.sum().item()
            b_wins += ok_b.sum().item()
        final_err = (
            torch.linalg.matrix_norm(torch.bmm(X, W_cur) - Y, ord="fro")
            / torch.linalg.matrix_norm(torch.bmm(X, W0) - Y, ord="fro")
        ).mean().item()
        return int(a_wins), int(b_wins), float(final_err)

    # Same call order as the original: blind first, then hgt, sharing one RNG stream.
    blind = run_colony("blind_beta")
    hgt = run_colony("hgt_beta")
    return {
        "seed": seed,
        "blind_beta": {"alpha_wins": blind[0], "beta_wins": blind[1], "final_error_ratio": blind[2]},
        "hgt_beta": {"alpha_wins": hgt[0], "beta_wins": hgt[1], "final_error_ratio": hgt[2]},
    }


def parse_seeds(text: str) -> list[int]:
    if "-" in text:
        lo, hi = text.split("-")
        return list(range(int(lo), int(hi) + 1))
    return [int(s) for s in text.split(",")]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="0")
    ap.add_argument("--device", default="mps" if torch.backends.mps.is_available() else "cpu")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    records = []
    for seed in parse_seeds(args.seeds):
        t0 = time.perf_counter()
        rec = run(seed, args.device)
        rec["seconds"] = round(time.perf_counter() - t0, 2)
        records.append(rec)
        b, h = rec["blind_beta"], rec["hgt_beta"]
        print(
            f"seed {seed}: blind A/B {b['alpha_wins']}/{b['beta_wins']} err {b['final_error_ratio']:.4f} | "
            f"hgt A/B {h['alpha_wins']}/{h['beta_wins']} err {h['final_error_ratio']:.4f} | {rec['seconds']}s"
        )

    out = {
        "probe": "P0",
        "device": args.device,
        "torch_version": torch.__version__,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "records": records,
    }
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(out, indent=2))
        print(f"saved {args.out}")


if __name__ == "__main__":
    main()
