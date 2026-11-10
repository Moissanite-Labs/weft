#!/bin/sh
# Metabolism runtime (metab.py): no step cap, no hold, no arms, no assigned model. Energy is the only limit.
# usage: [NEEDS=file.json] [CELL_E0=400] [CELL_START=mid] run_metab.sh OUTDIR
E=$HOME/Work/razi-cells/exp
rm -f $HOME/Work/razi-cells/.bench.lock
CELL_RUNTIME=metab.py PYTHONPATH=$HOME/Work/exo-live/src \
  $HOME/Work/exo-live/.venv/bin/python $HOME/Work/razi-tools/cells/colony.py "$E/$1" "${NEEDS:-$E/needs4k.json}" \
  --par 4 --calls 80 --steps 0
