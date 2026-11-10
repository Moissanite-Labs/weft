#!/bin/sh
# SP3 (T-K3 plus the price question): 2 by 2 on the flat shape f (4 parts, 400 each, born on mid).
#   a: price list shown, sense measured but not shown (control)     b: price list hidden (cost felt only)
#   c: price list shown, sense shown                                 d: price list hidden, sense shown
# Sense is measured in every arm (CELL_SENSE_DIR), so bench load is equal and every arm has readings.
# usage: run_sp3.sh full | run_sp3.sh pilot      Order fixed in TESTS.md before data. One run at a time.
cd $HOME/Work/razi-cells/exp
one() {  # arm run
  case $1 in
    a) P=1 S=0 ;; b) P=0 S=0 ;; c) P=1 S=1 ;; d) P=0 S=1 ;;
  esac
  CELL_SENSE_DIR=$PWD/records CELL_PRICE_SHOW=$P CELL_SENSE_SHOW=$S sh run_metab.sh $2 > results/sp3-$2.log 2>&1
  echo "$2 rc $?"
}
if [ "$1" = pilot ]; then
  one b sp3pb; one c sp3pc
else
  one a s3w0; one b s3w1   # warm the provider caches for both prompt forms. Excluded from the analysis.
  for i in 1 2 3 4; do for a in a b c d; do one $a s3$a$i; done; done
fi
