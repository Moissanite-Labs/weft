#!/bin/sh
# E13: E12 rerun on harness-owned kits (needs4k.json). Usage: run_e13.sh
E=$HOME/Work/razi-cells/exp; M=anthropic:claude-sonnet-5-5; export NEEDS=$E/needs4k.json
for i in 1 2 3 4; do
  CELL_HOLD= sh $E/run_cheap.sh $E/e13c$i $M ctrl || echo "FAILED e13c$i"
  CELL_HOLD= sh $E/run_cheap.sh $E/e13n$i $M novar || echo "FAILED e13n$i"
  CELL_HOLD=1 sh $E/run_cheap.sh $E/e13ch$i $M ctrl || echo "FAILED e13ch$i"
  CELL_HOLD=1 sh $E/run_cheap.sh $E/e13nh$i $M novar || echo "FAILED e13nh$i"
done
