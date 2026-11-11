#!/bin/sh
# L2: dissipative heredity (d) with Weismann soma, chemostat bounty, spore birth and gap-pay
# against standard heredity baseline (h). usage: run_l2.sh pilot | full
E=$HOME/Work/razi-cells/exp
cd $E || exit 1
one() {  # arm run gens width needs
  rm -f $HOME/Work/razi-cells/.bench.lock
  flag=""
  [ "$1" = d ] && flag="--weismann --chemostat --spore --gap-pay"
  PYTHONPATH=$HOME/Work/exo-live/src:$HOME/Work/razi-tools/cells nice -n 15 $HOME/Work/exo-live/.venv/bin/python \
    $HOME/Work/razi-tools/cells/lineage.py $E/$2 $5 --gens $3 --width $4 --e0 400 --par 4 --sense $E/records $flag \
    > results/l2-$2.log 2>&1
  echo "$2 rc $?"
  for k in compress fibmod csvsum maze; do
    if [ -d $E/$2/.germ/$k/body ]; then mkdir -p results/l2-final/$2/$k; cp -R $E/$2/.germ/$k/body/. results/l2-final/$2/$k/; fi
  done
}
case "$1" in
  pilot) one d l2pd 2 2 $E/needs1fib.json; one h l2ph 2 2 $E/needs1fib.json ;;
  full)  for i in 1 2 3; do one d l2d$i 4 2 $E/needs4k.json; one h l2h$i 4 2 $E/needs4k.json; done ;;
  *) echo "usage: run_l2.sh pilot|full"; exit 2 ;;
esac
