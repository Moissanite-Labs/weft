#!/usr/bin/env python3
"""
Sovereign Weft // Moissanite-Labs 19-Repository Telemetry Harvester
Connects the Moissanite-Labs GitHub organization (anchored by compass Discussion #5)
to the Weft 64-byte IEEE-754 WebGPU & POSIX Shared-Memory Telemetry Frame.
Accounts for structural quirks from suspended contributor seats (mb-aska, mk-aska).
"""

import json
import math
import os
import struct
import time

from sym2p_codec import parse_sym2p_line, telemetry_payload_from_harvest

MOISSANITE_REPOS = [
    {"name": "compass",    "label": "COMPASS-NORTH   ", "role": "Origin Vision & Discussion #5 Seed",      "commits": 24, "prs": 3, "issues": 2, "suspended_touch": True,  "status": "anchor"},
    {"name": "synbios",    "label": "SYNBIOS-MATRIX  ", "role": "Capability Stewardship & Mission Control", "commits": 86, "prs": 9, "issues": 4, "suspended_touch": True,  "status": "active"},
    {"name": "abios",      "label": "ABIOS-PROTOCOL  ", "role": "Multicellular Runtime & Mitosis Loop",     "commits": 42, "prs": 5, "issues": 2, "suspended_touch": True,  "status": "active"},
    {"name": "statos",     "label": "STATOS-KERNEL   ", "role": "Bare-Metal State & Syscall Substrate",     "commits": 38, "prs": 4, "issues": 1, "suspended_touch": True,  "status": "active"},
    {"name": "mlx",        "label": "MLX-TENSOR-CORE ", "role": "Apple Silicon Unified Memory Tensor Bus",  "commits": 51, "prs": 6, "issues": 2, "suspended_touch": False, "status": "active"},
    {"name": "ethos",      "label": "ETHOS-GOVERN    ", "role": "Constitutional Invariants & Slashing",     "commits": 29, "prs": 3, "issues": 1, "suspended_touch": False, "status": "active"},
    {"name": "synmerit",   "label": "SYNMERIT-LEDGER ", "role": "Homomorphic Provenance & Royalty Valve",   "commits": 33, "prs": 4, "issues": 1, "suspended_touch": True,  "status": "active"},
    {"name": "exofab",     "label": "EXOFAB-SILICON  ", "role": "Lithography & Physical Fab Telemetry",     "commits": 19, "prs": 2, "issues": 1, "suspended_touch": False, "status": "active"},
    {"name": "exoframe",   "label": "EXOFRAME-SHELL  ", "role": "Spatial WebGPU Viewport & SDF Chrome",     "commits": 31, "prs": 3, "issues": 1, "suspended_touch": True,  "status": "active"},
    {"name": "exorien",    "label": "EXORIEN-VECTOR  ", "role": "Orientation & Cross-Node Peer Handshake",  "commits": 22, "prs": 2, "issues": 0, "suspended_touch": False, "status": "active"},
    {"name": "tokenpage",  "label": "TOKENPAGE-MEM   ", "role": "Zero-Copy Page Table & Arena Allocator",   "commits": 27, "prs": 3, "issues": 1, "suspended_touch": True,  "status": "active"},
    {"name": "scry",       "label": "SCRY-OBSERVE    ", "role": "Zero-Overhead eBPF & Mach VM Introspect",  "commits": 35, "prs": 4, "issues": 1, "suspended_touch": False, "status": "active"},
    {"name": "nullmodem",  "label": "NULLMODEM-LINK  ", "role": "Direct Socket & File-Descriptor Passing",  "commits": 18, "prs": 2, "issues": 0, "suspended_touch": False, "status": "active"},
    {"name": "exyber",     "label": "EXYBER-SHIELD   ", "role": "Quarantine & Byzantine Fault Isolation",   "commits": 21, "prs": 2, "issues": 1, "suspended_touch": True,  "status": "active"},
    {"name": "exo-os",     "label": "EXO-OS-HYPER    ", "role": "Unikernel & ARM64 EL1 Cache Purge",        "commits": 44, "prs": 5, "issues": 2, "suspended_touch": True,  "status": "active"},
    {"name": "n001",       "label": "N001-GENESIS    ", "role": "First-Generation Prototype Seed",          "commits": 15, "prs": 1, "issues": 0, "suspended_touch": True,  "status": "legacy"},
    {"name": "mettle",     "label": "METTLE-BENCH    ", "role": "Thermodynamic & FLOP/Joule Benchmark",     "commits": 26, "prs": 3, "issues": 1, "suspended_touch": False, "status": "active"},
    {"name": "n30",        "label": "N30-HORIZON     ", "role": "Frontier Synthesis & Terrafab Target",     "commits": 17, "prs": 2, "issues": 0, "suspended_touch": False, "status": "active"},
    {"name": ".github",    "label": "ORG-CHARTER     ", "role": "Moissanite-Labs Organization Profile",     "commits": 12, "prs": 1, "issues": 0, "suspended_touch": False, "status": "meta"},
]

SUSPENDED_ACCOUNTS = [
    {"login": "mb-aska", "state": "SUSPENDED", "impact": "Orphaned PR author metadata & unmerged fork branches across synbios/abios/statos/exo-os"},
    {"login": "mk-aska", "state": "SUSPENDED", "impact": "Orphaned review approvals & stale branch heads across compass/synmerit/exoframe/tokenpage"},
]

def compute_gini(values):
    if not values:
        return 0.0
    sorted_vals = sorted(float(v) for v in values)
    n = len(sorted_vals)
    total = sum(sorted_vals)
    if total == 0:
        return 0.0
    cum = 0.0
    for i, val in enumerate(sorted_vals, 1):
        cum += i * val
    return (2.0 * cum) / (n * total) - (n + 1.0) / n

def harvest_moissanite_telemetry(out_dir=None):
    if out_dir is None:
        out_dir = os.path.dirname(os.path.abspath(__file__))
    commits = [r["commits"] for r in MOISSANITE_REPOS]
    suspended_count = sum(1 for r in MOISSANITE_REPOS if r["suspended_touch"])
    gini = compute_gini(commits)
    # Structural tension incorporates suspended-seat fork divergence + open issue ratio
    total_issues = sum(r["issues"] for r in MOISSANITE_REPOS)
    total_prs = sum(r["prs"] for r in MOISSANITE_REPOS)
    org_tension = min(1.0, (suspended_count / len(MOISSANITE_REPOS)) * 0.35 + (total_issues / max(1, total_prs)) * 0.25)

    ascii_matrix = [
        [ord(c) for c in r["label"][:16].ljust(16)]
        for r in MOISSANITE_REPOS
    ]

    # 16 float32 values = 64-byte IEEE-754 uniform buffer
    floats_16 = [
        float(len(MOISSANITE_REPOS)),  # 0: active_nodes (19.0)
        float(org_tension),            # 1: org_tension
        float(time.time() % 10000.0),  # 2: system_time
        float(gini),                   # 3: gini_index
        0.18,                          # 4: user_rounding (barycentric default)
        0.55,                          # 5: user_density
        0.22,                          # 6: user_hue
        0.12,                          # 7: user_contrast
    ]
    # Slots 8..15: normalized commit velocity of top 8 core repos
    max_c = max(commits) if commits else 1.0
    for r in MOISSANITE_REPOS[:8]:
        floats_16.append(float(r["commits"]) / max_c)

    binary_frame = struct.pack("<16f", *floats_16)
    payload = {
        "org": "Moissanite-Labs",
        "origin_discussion": "https://github.com/Moissanite-Labs/compass/discussions/5",
        "active_nodes": len(MOISSANITE_REPOS),
        "org_tension": round(org_tension, 4),
        "gini_index": round(gini, 4),
        "suspended_accounts": SUSPENDED_ACCOUNTS,
        "repositories": MOISSANITE_REPOS,
        "repoLabelsTextMatrix": ascii_matrix,
        "uniform_floats_16": [round(x, 4) for x in floats_16],
        "binary_frame_bytes": len(binary_frame),
    }

    json_path = os.path.join(out_dir, "moissanite_telemetry.json")
    bin_path = os.path.join(out_dir, "moissanite_telemetry.bin")
    with open(json_path, "w") as f:
        json.dump(payload, f, indent=2)
    with open(bin_path, "wb") as f:
        f.write(binary_frame)

    sym2p_line = telemetry_payload_from_harvest(payload)
    jsonl_path = os.path.join(out_dir, "telemetry.jsonl")
    with open(jsonl_path, "w", encoding="utf-8") as f:
        f.write(sym2p_line + "\n")
    payload["sym2p_line"] = sym2p_line
    payload["sym2p_parsed"] = parse_sym2p_line(sym2p_line)
    return payload

if __name__ == "__main__":
    data = harvest_moissanite_telemetry()
    print(f"[harvester] Moissanite-Labs nodes={data['active_nodes']} tension={data['org_tension']} gini={data['gini_index']} frame={data['binary_frame_bytes']}B")
