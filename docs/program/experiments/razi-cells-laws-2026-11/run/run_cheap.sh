#!/bin/sh
# Cheap paired protocol (2026-11-10). Usage: [NEEDS=file.json] run_cheap.sh OUTDIR MODEL [ARM]
# 4 tasks, 16 calls, 8 steps, output cap 2000, effort low, 40k billed tokens per colony.
set -e
OUT=$1; MODEL=$2; ARM=${3:-novar}
rm -f "$HOME/Work/razi-cells/.bench.lock"
CELL_ARM=$ARM CELL_MAX_OUT=2000 CELL_EFFORT=low CELL_TOKEN_BUDGET=40000 \
  "$HOME/Work/exo-live/.venv/bin/python" "$HOME/Work/razi-tools/cells/colony.py" \
  "$OUT" "${NEEDS:-$HOME/Work/razi-cells/exp/needs4.json}" --par 4 --calls 16 --steps 8 --model "$MODEL"
