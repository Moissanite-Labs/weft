#!/bin/sh
# L1 after the full run: score final germlines against the fixed reference bodies, then the report, unchanged.
E=$HOME/Work/razi-cells/exp; cd $E || exit 1
PY="$HOME/Work/exo-live/.venv/bin/python"; export PYTHONPATH=$HOME/Work/exo-live/src:$HOME/Work/razi-tools/cells
rm -f $HOME/Work/razi-cells/.bench.lock
nice -n 15 $PY ~/Work/razi-tools/cells/refscore.py results/l1-ref.json results/l1-final/l1h1 results/l1-final/l1b1 results/l1-final/l1h2 results/l1-final/l1b2 results/l1-final/l1h3 results/l1-final/l1b3 > results/l1-refscore-out.txt 2>&1; echo "refscore rc $?"
$PY ~/Work/razi-tools/cells/lineage_report.py results/l1-ref.json h=l1h1,l1h2,l1h3 b=l1b1,l1b2,l1b3 > results/l1-out.txt 2>&1; echo "report rc $?"
