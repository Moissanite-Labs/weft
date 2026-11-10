#!/bin/sh
# Stem pilot (stem.py): one uncommitted stem cell holds the colony's energy and feeds committed cells.
# usage: [NEEDS=file.json] [CELL_E0=400] run_stem.sh OUTDIR
E=$HOME/Work/razi-cells/exp
rm -f $HOME/Work/razi-cells/.bench.lock
CELL_MAX_CALLS=80 PYTHONPATH=$HOME/Work/exo-live/src \
  $HOME/Work/exo-live/.venv/bin/python $HOME/Work/razi-tools/cells/stem.py "$E/$1" "${NEEDS:-$E/needs4k.json}"
