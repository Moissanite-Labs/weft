#!/bin/sh
# SP2 (T-K2): flat, stem, flat-with-stem-birth-models. Interleaved, one at a time. Order fixed in TESTS.md before data.
cd $HOME/Work/razi-cells/exp
for i in 1 2 3 4; do
  for a in f s m; do
    r=s2$a$i
    case $a in
      f) sh run_metab.sh $r ;;
      s) sh run_stem.sh $r ;;
      m) NEEDS=$PWD/needs4k_stembirth.json sh run_metab.sh $r ;;
    esac > results/sp2-$r.log 2>&1
    echo "$r rc $?"
  done
done
