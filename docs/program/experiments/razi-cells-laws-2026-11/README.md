# Razi-cells laws record, 2026-11 (E11 to L1)

Status: run record, not a paper. Every result here is a lead unless the text says otherwise. Nothing in this folder
is checked by CI. It continues the E07 record in `../E07/razi-cells-2026-11/` and uses the same harness.

## What this is

Small colonies of isolated agents ("cells") work on four timed code tasks. Each cell runs in a sandbox with no
network and no key. The harness owns the task inputs, the correctness check and the timing. A cell spends energy on
model calls and earns energy only when a scored body beats its last scored body beyond noise. The question is which
simple laws make such a colony improve, show restraint, and pass gains on, without hand-written control.

For every experiment the guesses, the report script and the file hashes were written into `TESTS.md` before any
data. Report scripts were run unchanged. Anything written after seeing data is labelled as a diagnostic.

## What was run

| Block | Layer | Question | Guesses held, judged as written |
|---|---|---|---|
| E11, E12, E13 | agent colonies | Does removing the "variants" tool help or hurt, with and without a hold rule | E11 and E13 judged in `TESTS.md`. E12 used a flawed instrument and is kept as a failure record |
| GR1 | toy numpy network | Does division plus a gate grow width to match need | 3 of 5 |
| GR2 | toy numpy network | Same, with daughters born different | 5 of 6 |
| GR3 | toy numpy network | Is GR2 robust to one knob at a time and a second task | 3 of 5 |
| GR4 | toy numpy network | Two ways to tell "satisfied" from "stuck" | 5 of 5 |
| SP1 | agent colonies | Does one uncommitted stem cell that feeds committed cells help | 7 of 8 |
| SP2 | agent colonies | Stem against flat on a fixed-reference metric | 6 of 8 |
| SP3 | agent colonies | What changes when a cell is shown the price list, and its distance from the best known body | 6 of 12 |
| T-J3 | LoRA adapters | Does division plus a gate help when the genome is an adapter | Incomplete. Storage limit stopped 3 of 4 arms |
| L1 | agent colonies | Does heredity let lineages compound gains | 5 of 8. The three guesses that mattered missed |

## Main readings, with their limits

- **Cells picked the cheapest model from the price list alone.** With the list shown, 14 of 16 cells moved to the
  cheapest model at their first step. With it hidden, 0 of 16 did. No cell in any arm moved up a model on its own.
- **Hiding the price did not buy better work.** Cells with the list hidden spent 2.4 to 3.0 times the energy and
  had 7 deaths against 0.
- **One inward number changed behaviour most.** Cells shown their own score against the best known body kept working
  on an already passing body. That arm had the highest reach (2.03 against 1.48 for control, as a ratio to a fixed
  reference body).
- **A stem cell that feeds others added cost and no reach** in SP1 and SP2.
- **In the toy network, a gate that escalates after a failed try** had the lowest worst-case regret of four gates
  (1.42 against 3.02 for the fixed gate).
- **Heredity saved energy and did not search.** In L1, lineages that pass a body and an energy store to their
  heirs reached the same level as lineages whose newborns start blank (2.27 against 2.28). They spent 31% less
  energy and had 7 deaths against 23. They did not compound: 65 of 70 heirs changed nothing, and 9 of 12 final
  bodies were still the first generation's body. When an heir did try, the gate took its work 3 times in 4.
- **Negative results are kept.** GR1 copy division was never accepted by the gate. The T-J3 plain arm did not beat
  the base rate. The E12 maze task was not a valid instrument.

Limits. SP3 has 4 runs per arm and its smallest p value is 0.21. L1 has 3 runs per arm. One model family (Anthropic) ran the laws. One task
carries most of the SP3 difference. The toy network results are curve fitting on a laptop CPU. No claim here is
established. A result needs a second model family and a repeat before it is called a result.

## Layout

- `CONSULT-2026-11-10.md`: cross-project synthesis (`Weft`, `Exo`, `razi-cells` `E07` to `L1`) and ranked next-step plan (`T-L2`, `metab.py` fixes, `T-L3` deterministic assays).
- `TESTS.md`: every preregistration and result, in order. Start at the section for the block you want.
- `IDEAS.md`: the idea ledger, including failures (section H) and lessons K1 to K26 and L1 to L9.
- `code/cells/`: the runtime (`metab.py`, `cell.py`, `colony.py`, `kit.py`), the report scripts, and offline tests.
- `code/adapters/`: the T-J3 trainer and report.
- `run/`: run scripts and task lists.
- `results/`: saved script outputs and fixed-reference scores.
- `map/`: a map of the open directions.

Paths inside `TESTS.md` and the scripts point at the machine the runs were made on. Raw per-cell logs are not
included in this cut.

## Reproducing

The scripts `code/cells/kit_selftest.py` and `code/cells/tests/*_offline.py` are offline checks: they stub model
calls and spend no API credits. They are not runnable from a fresh checkout of this folder alone.

On the machine that wrote this record they still depend on:

- **Exo.** `cell.py` imports `exo` from `~/Work/exo-live/src` at import time. `kit_selftest.py` loads `cell.py`.
  `colony.py` and the sandbox runner expect Exo's Python at `~/Work/exo-live/.venv/bin/python`. `cell.py` also
  hardcodes `/opt/homebrew/bin/python3` for scoring subprocesses. Without that layout, `python
  code/cells/kit_selftest.py` fails with `ModuleNotFoundError: No module named 'exo'`.
- **Author paths.** The files in `code/cells/tests/` import `metab` and `cell` from `~/Work/razi-tools/cells`, not
  from this tree. `kit.py` reads kit inputs from `~/Work/razi-cells/kits`. The offline tests write temp runs under
  `~/Work/razi-cells/exp`. Those directories must exist, or you must mirror the paths.

Once that layout is in place, the offline checks themselves need no model router and no API key.

Colony runs and the saved outputs in `results/` need a live model router and the same machine layout. They are not
reproducible from this folder alone. That is a stated limit of the record.
