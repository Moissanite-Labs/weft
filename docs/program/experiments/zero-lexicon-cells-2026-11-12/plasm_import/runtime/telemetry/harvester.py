#!/usr/bin/env python3
"""
Moissanite-Labs Organization Telemetry Harvester (Codebase C6 — Interfaces I1, I2)
==================================================================================
Fixes Issue #15:
  1. Never publishes `suspended_accounts` or named personal logins in any output
     JSON or public site data.
  2. Explicitly labels offline snapshot data with `"source": "fixture"`.
  3. Supports `--live` (or `live=True` / `WEFT_GITHUB_LIVE=1`) to fetch live
     repository metadata from the GitHub REST API (`https://api.github.com/orgs/Moissanite-Labs/repos`),
     marking the resulting payload `"source": "github-api"`.
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.request
from typing import Any, Dict, List, Optional

from .frame64 import compute_gini, encode_frame_64b_bytes, pack_uniform_frame_64b
from .sym2p_codec import encode_sym2p_line

MOISSANITE_REPOS_FIXTURE: List[Dict[str, Any]] = [
    {"name": "compass",          "role": "Origin Vision & Architecture Thread (#5)", "commits": 14, "prs": 3, "issues": 5, "layer": "governance", "tension": 0.18},
    {"name": "aywa",             "role": "WebGPU Spatial Canvas & Barycentric UI",   "commits": 42, "prs": 8, "issues": 4, "layer": "interface",  "tension": 0.24},
    {"name": "qalam",            "role": "Kinetic Typography & MSDF/Laya Engine",    "commits": 31, "prs": 6, "issues": 2, "layer": "interface",  "tension": 0.19},
    {"name": "splicers",         "role": "Darwin Mach/SCM_RIGHTS Splicer Substrate", "commits": 27, "prs": 5, "issues": 3, "layer": "substrate",  "tension": 0.32},
    {"name": "alkindus",         "role": "Epistemic Verification & Benchmark Core",  "commits": 19, "prs": 4, "issues": 2, "layer": "cognition",  "tension": 0.21},
    {"name": "averroes",         "role": "Dialectical Debate & Consensus Engine",    "commits": 16, "prs": 3, "issues": 1, "layer": "cognition",  "tension": 0.17},
    {"name": "avicenna",         "role": "Homeostatic Diagnostic & Autonomic Loop",  "commits": 22, "prs": 4, "issues": 3, "layer": "substrate",  "tension": 0.28},
    {"name": "alhazen",          "role": "Optical Perception & Visual Grounding",    "commits": 15, "prs": 2, "issues": 1, "layer": "interface",  "tension": 0.15},
    {"name": "kindi",            "role": "Cryptographic Frequency & Watermark Core", "commits": 21, "prs": 4, "issues": 2, "layer": "ledger",     "tension": 0.22},
    {"name": "farabi",           "role": "Polyphonic Resonance & Harmonic Scheduler","commits": 12, "prs": 2, "issues": 1, "layer": "cognition",  "tension": 0.14},
    {"name": "biruni",           "role": "Empirical Geodesic & Cross-Corpus Index",  "commits": 18, "prs": 3, "issues": 2, "layer": "cognition",  "tension": 0.20},
    {"name": "khwarizmi",        "role": "Algebraic Reduction & IC Rewrite Engine",  "commits": 29, "prs": 6, "issues": 3, "layer": "substrate",  "tension": 0.29},
    {"name": "tusi",             "role": "Coupled Oscillator & Orbital Kinematics",  "commits": 14, "prs": 2, "issues": 1, "layer": "interface",  "tension": 0.16},
    {"name": "khayyam",          "role": "Geometric Cubic Solver & Lattice Layout",  "commits": 11, "prs": 2, "issues": 1, "layer": "interface",  "tension": 0.13},
    {"name": "jazari",           "role": "Automata Mechanical Valve & Clockwork",    "commits": 24, "prs": 5, "issues": 2, "layer": "substrate",  "tension": 0.26},
    {"name": "banu-musa",        "role": "Feedback Control & Differential Float",    "commits": 13, "prs": 2, "issues": 1, "layer": "substrate",  "tension": 0.18},
    {"name": "suhrawardi",       "role": "Illuminationist Shader & Photonic Field",  "commits": 17, "prs": 3, "issues": 2, "layer": "interface",  "tension": 0.21},
    {"name": "mulla-sadra",      "role": "Substantial Motion & Weight Plasticity",   "commits": 20, "prs": 4, "issues": 2, "layer": "cognition",  "tension": 0.25},
    {"name": "moissanite-HQ",    "role": "Organization Charter & Sovereign Ledger",  "commits": 9,  "prs": 2, "issues": 1, "layer": "ledger",     "tension": 0.12},
]


def fetch_live_org_repos(org: str = "Moissanite-Labs", timeout: float = 10.0) -> List[Dict[str, Any]]:
    """Fetch live repository metadata from the GitHub REST API (#15)."""
    url = f"https://api.github.com/orgs/{org}/repos?per_page=100&sort=updated"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "weft-telemetry-harvester/1.0",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw_repos = json.loads(resp.read().decode("utf-8"))

    by_name = {r["name"]: r for r in MOISSANITE_REPOS_FIXTURE}
    nodes: List[Dict[str, Any]] = []
    for item in raw_repos:
        name = item.get("name", "unknown")
        base = by_name.get(name, {})
        open_issues = int(item.get("open_issues_count", 0))
        size_kb = max(1, int(item.get("size", 10)))
        commits_est = int(base.get("commits", max(1, min(100, size_kb // 8))))
        prs_est = int(base.get("prs", max(1, open_issues // 2)))
        tension = round(min(0.84, 0.10 + 0.02 * open_issues + 0.003 * commits_est), 4)
        nodes.append(
            {
                "name": name,
                "role": item.get("description") or base.get("role", "Moissanite-Labs repository"),
                "commits": commits_est,
                "prs": prs_est,
                "issues": open_issues,
                "layer": base.get("layer", "substrate"),
                "tension": tension,
            }
        )
    return nodes


def harvest_moissanite_telemetry(
    out_dir: Optional[str] = None,
    *,
    live: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Build the 19-repository telemetry snapshot, 64-byte uniform binary frame,
    and canonical SYM-2P/1.0 packet line.
    """
    if live is None:
        live = os.environ.get("WEFT_GITHUB_LIVE", "").strip() in ("1", "true", "yes")

    source = "fixture"
    repos = [dict(r) for r in MOISSANITE_REPOS_FIXTURE]
    if live:
        try:
            live_repos = fetch_live_org_repos()
            if live_repos:
                repos = live_repos
                source = "github-api"
        except Exception:
            source = "fixture"

    commits = [float(r["commits"]) for r in repos]
    tensions = [float(r["tension"]) for r in repos]
    gini = compute_gini(commits)
    mean_tension = sum(tensions) / max(1, len(tensions))
    active_nodes = float(len(repos))

    barycentric = {
        "rounding": 0.18,
        "density": 0.55,
        "hue": 0.22,
        "contrast": 0.12,
    }
    vel = [float(r["commits"]) / 50.0 for r in repos[:8]]

    floats_16 = pack_uniform_frame_64b(
        active_nodes=active_nodes,
        org_tension=round(mean_tension, 4),
        system_time=1762560000.0,
        gini_index=round(gini, 4),
        barycentric=barycentric,
        velocities=vel,
    )
    floats_16 = [round(float(x), 4) for x in floats_16]
    binary_frame = encode_frame_64b_bytes(floats_16)

    sym2p_line = encode_sym2p_line(
        role=0x01,
        action_state=0x03,
        sequence=1,
        metrics={
            "active_nodes": int(active_nodes),
            "tension": round(mean_tension, 4),
            "gini": round(gini, 4),
        },
    )

    payload: Dict[str, Any] = {
        "schema": "SYM-2P/1.0",
        "source": source,
        "organization": "Moissanite-Labs",
        "origin_thread": "Moissanite-Labs/compass#5",
        "active_nodes": len(repos),
        "org_tension": round(mean_tension, 4),
        "gini_index": round(gini, 4),
        "barycentric_state": barycentric,
        "uniform_frame_64b_floats": floats_16,
        "binary_frame_bytes": len(binary_frame),
        "sym2p_wire_packet": sym2p_line,
        "repositories": repos,
    }

    if out_dir is not None:
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "moissanite_telemetry.json"), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
            fh.write("\n")
        with open(os.path.join(out_dir, "moissanite_telemetry.bin"), "wb") as fh:
            fh.write(binary_frame)
        with open(os.path.join(out_dir, "telemetry.jsonl"), "w", encoding="utf-8") as fh:
            fh.write(sym2p_line + "\n")

    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Harvest Moissanite-Labs telemetry (fixture or --live).")
    parser.add_argument("--out-dir", default=None, help="Optional directory to write telemetry files.")
    parser.add_argument("--live", action="store_true", help="Query live GitHub REST API instead of offline fixture.")
    args = parser.parse_args()
    res = harvest_moissanite_telemetry(args.out_dir, live=args.live)
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
