#!/usr/bin/env python3
"""
Syntactic Weft // Master Self-Test & Corpus Integrity Suite
Exercises:
  1. Stratified Apple Silicon Unified Memory Plasm (POSIX shm + PyTorch MPS)
  2. Lafont Interaction Combinator VM (CON/DUP/ERA reduction + cryptographic trace)
  3. Aywa WebGPU & Moissanite-Labs 19-Repository Telemetry Bridge
  4. Full 53-file Markdown Corpus + 4 Browser Transcripts + 5 Sandbox Widgets Audit
"""

import ast
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WEFT_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "aywa")))

from weft_plasm import run_plasm_cycle
from weft_ic_vm import run_ic_verification
from weft_daemon import read_darwin_hardware_metrics
from github_harvester import harvest_moissanite_telemetry

def audit_corpus(root_dir):
    md_files = sorted(glob.glob(f"{root_dir}/**/*.md", recursive=True))
    odd_fences = []
    caution_hits = []
    followup_hits = []
    py_errors = []
    total_py_blocks = 0
    total_fenced_blocks = 0

    for mf in md_files:
        rel = os.path.relpath(mf, root_dir)
        with open(mf) as f:
            txt = f.read()
        fc = len(re.findall(r"^```", txt, re.M))
        total_fenced_blocks += fc // 2
        if fc % 2 != 0:
            odd_fences.append((rel, fc))
        if "Use code with caution." in txt:
            caution_hits.append(rel)
        if "<FollowUp>" in txt or "</FollowUp>" in txt:
            followup_hits.append(rel)
        for b_i, m in enumerate(re.finditer(r"```python\n(.*?)```", txt, re.S)):
            total_py_blocks += 1
            try:
                ast.parse(m.group(1))
            except SyntaxError as e:
                py_errors.append((rel, b_i, e.lineno, e.msg))

    widgets = sorted(glob.glob(f"{root_dir}/browser-sources/widgets/*.html"))
    return {
        "markdown_files_checked": len(md_files),
        "total_fenced_code_blocks": total_fenced_blocks,
        "python_blocks_ast_verified": total_py_blocks,
        "interactive_widgets_count": len(widgets),
        "odd_fences": odd_fences,
        "caution_artifacts": caution_hits,
        "followup_artifacts": followup_hits,
        "python_syntax_errors": py_errors,
        "status": "PASS" if (not odd_fences and not caution_hits and not followup_hits and not py_errors and len(widgets) == 5) else "FAIL",
    }

def main():
    plasm_res = run_plasm_cycle(cycles=3)
    ic_res = run_ic_verification()
    aywa_dir = os.path.abspath(os.path.join(HERE, "..", "aywa"))
    moiss_res = harvest_moissanite_telemetry(aywa_dir)
    hw_res = read_darwin_hardware_metrics()
    corpus_res = audit_corpus(WEFT_ROOT)

    overall = all(x == "PASS" for x in [plasm_res["status"], ic_res["status"], corpus_res["status"]])
    summary = {
        "overall_status": "PASS" if overall else "FAIL",
        "plasm_substrate": plasm_res,
        "interaction_combinator_vm": ic_res,
        "moissanite_telemetry": {
            "active_nodes": moiss_res["active_nodes"],
            "org_tension": moiss_res["org_tension"],
            "gini_index": moiss_res["gini_index"],
            "binary_frame_bytes": moiss_res["binary_frame_bytes"],
            "darwin_hardware": hw_res,
        },
        "corpus_audit": corpus_res,
    }
    print(json.dumps(summary, indent=2))
    return 0 if overall else 1

if __name__ == "__main__":
    sys.exit(main())
