#!/bin/sh
# E11: ctrl vs novar on Sonnet 5.5, cheap protocol, 4 interleaved reps. Usage: run_e11.sh pilot|full
E=$HOME/Work/razi-cells/exp; M=anthropic:claude-sonnet-5-5
if [ "$1" = pilot ]; then sh $E/run_cheap.sh $E/e11p $M ctrl; exit $?; fi
for i in 1 2 3 4; do
  sh $E/run_cheap.sh $E/e11c$i $M ctrl || echo "FAILED e11c$i"
  sh $E/run_cheap.sh $E/e11n$i $M novar || echo "FAILED e11n$i"
done
