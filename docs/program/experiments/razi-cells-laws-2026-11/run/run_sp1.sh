#!/bin/sh
# SP1: flat and stem arms, interleaved, one at a time. Order fixed in TESTS.md before data.
cd $HOME/Work/razi-cells/exp
for r in fl1 sp1 fl2 sp2; do
  case $r in fl*) sh run_metab.sh $r ;; sp*) sh run_stem.sh $r ;; esac > results/sp1-$r.log 2>&1
  echo "$r rc $?"
done
