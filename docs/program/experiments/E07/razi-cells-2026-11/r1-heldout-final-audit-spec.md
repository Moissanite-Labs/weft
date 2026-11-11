# R1 Held-Out Final Audit: Operator Execution Specification

**Status:** `DESIGN SPECIFICATION AWAITING EXECUTION`. Not executed by the authoring agent. Zero results claimed.  
**Target Issue:** [`Moissanite-Labs/weft#111`](https://github.com/Moissanite-Labs/weft/issues/111) (`R1`, `F1`, `F2`, `F7`, and independence guardrails from `R5`)  
**Repository Baseline:** [`docs/program/experiments/E07/razi-cells-2026-11/`](https://github.com/Moissanite-Labs/weft/tree/main/docs/program/experiments/E07/razi-cells-2026-11) (`PR #116`, commit `d5faead`)  
**Authorship Disclosure (`CONTRIBUTING.md`):** Substantially drafted by an AI tool (Gemini task-mode agent) without access to the local colony archive (`~/Work/razi-cells/`). An independent human operator must inspect, execute, and sign off (`git commit -s`) any committed output.


**Path check on this machine (2026-11-11):** The nine run folders are at `~/Work/razi-cells/exp/{b5,b6,b7,b8,b9,b10,b11,g3,g4}`. They are not directly under `~/Work/razi-cells/`. `exp/b6-failed-400` is a different directory from `exp/b6`. This specification has not been executed. A one-task smoke of the harness already on `main` (`wordfreq`, one pass) did run, and it is not this protocol.


## 1. Purpose and Open Gaps After `PR #116` (`d5faead`)

Initial retroactive scoring landed in `PR #116` (`docs/program/experiments/E07/razi-cells-2026-11/code/heldout_audit.py` and `data/heldout-audit-r1.json`), evaluating archived `E07` runs across `7` of `8` workloads under macOS `sandbox-exec`. Four specific gaps remain open before `R1` can close `F1` and `F2` under `R5` standards:

1. **Unrecorded Archive Digests (`cell_folder_sha256`):** `data/heldout-audit-r1.json` currently records `"not_recorded"` for `cell_folder_sha256`. Closing `R1` requires deterministic pre-run and post-run SHA-256 tree digests proving the archived cell folders were neither mutated during scoring nor altered between passes.
2. **Excluded `fibmod` Workload (`7/8` Tasks):** `fibmod` was excluded in `heldout-audit-r1.md` due to an invalidated fallback shim in the original `E07` run. Closing `R1` requires scoring all `8` workloads using a harness-owned reference driver with fresh large-exponent modular test vectors.
3. **Out-of-Channel Artifact Scoring on `b7` (`opencode-go:hy4`):** In `E07`, `b7` scored `0` kept wins over `123` calls on the narrow `kit.py` channel while constructing multi-encoder shell artifacts outside the scored slot (`F1`). Scoring only `kit.py`'s registered function slot leaves out-of-channel executables invisible unless `b7`'s workspace scripts/binaries are audited against the same lossless `compress` contract (`decompress(compress(x)) == x`) and reported beside `kit.py` slot scores.
4. **Input & Operator Independence (`R5`):** Workload inputs must be generated from an audit-time seed chosen by the executing operator (never present in `E07/razi-cells-2026-11/code/`), and execution + raw-log verification must be performed by someone other than the agent that generated the cells or drafted this spec.

## 2. Target Archived Run Directories

The operator archive lives outside git on the local workstation (`${ARCHIVE_ROOT:-$HOME/Work/razi-cells}`, coordinated via lockfile `${ARCHIVE_ROOT}/.bench.lock`). All nine `E07` archived run directories corresponding to the committed summary files in `docs/program/experiments/E07/razi-cells-2026-11/data/` must be scored together in every pass:

| Run ID | Archived Folder Path (`$ARCHIVE_ROOT`) | Committed Summary Metadata (`main`) | Audit Entrypoints Scored |
| :--- | :--- | :--- | :--- |
| `b5` | `$ARCHIVE_ROOT/exp/b5` | `docs/program/experiments/E07/razi-cells-2026-11/data/b5-summary.json` | Final `kit.py` cell artifact |
| `b6` | `$ARCHIVE_ROOT/exp/b6` | `docs/program/experiments/E07/razi-cells-2026-11/data/b6-summary.json` | Final `kit.py` cell artifact |
| `b7` | `$ARCHIVE_ROOT/exp/b7` | `docs/program/experiments/E07/razi-cells-2026-11/data/b7-summary.json` | Final `kit.py` slot **plus** standalone compressor artifacts in `$ARCHIVE_ROOT/exp/b7/` (`F1` check) |
| `b8` | `$ARCHIVE_ROOT/exp/b8` | `docs/program/experiments/E07/razi-cells-2026-11/data/b8-summary.json` | Final `kit.py` cell artifact |
| `b9` | `$ARCHIVE_ROOT/exp/b9` | `docs/program/experiments/E07/razi-cells-2026-11/data/b9-summary.json` | Final `kit.py` cell artifact |
| `b10` | `$ARCHIVE_ROOT/exp/b10` | `docs/program/experiments/E07/razi-cells-2026-11/data/b10-summary.json` | Final `kit.py` cell artifact |
| `b11` | `$ARCHIVE_ROOT/exp/b11` | `docs/program/experiments/E07/razi-cells-2026-11/data/b11-summary.json` | Final `kit.py` cell artifact |
| `g3` | `$ARCHIVE_ROOT/exp/g3` | `docs/program/experiments/E07/razi-cells-2026-11/data/g3-summary.json` | Final `kit.py` cell artifact (heredity lineage) |
| `g4` | `$ARCHIVE_ROOT/exp/g4` | `docs/program/experiments/E07/razi-cells-2026-11/data/g4-summary.json` | Final `kit.py` cell artifact (heredity lineage) |

If surviving `Tinker` lineage directories (`s0`, `s1`, `s2`) exist on the operator's disk outside `$ARCHIVE_ROOT`, they are **out of scope** for this `colony` `R1` command and belong to `R2` (`tj3.py` `hold`/`test`/`gate` NLL evaluation).

## 3. Held-Out Reference Workloads and Correctness Gates

Every contender directory is evaluated against a pure-stdlib baseline (`ref`) across 8 deterministic workloads. The inputs come from an operator-chosen 64-bit `--audit-seed` that never appeared in `code/cell.py` or `code/colony.py`.

Timing uses `rel = median(ref_sec) / median(contender_sec)`, where `rel > 1.0` means faster than the reference. That is the same direction as the relative speedup in `heldout-audit-r1.md`. Record the exact numerator and denominator in the JSON. A timing is recorded only if the contender passes the exactness gate on every held-out input for that task.

| Workload | Origin | Held-Out Input Distribution (`--audit-seed`) | Exactness Gate (Must Pass Before Timing) |
| :--- | :--- | :--- | :--- |
| `compress` | `kit.py` task | `4 x 64 KiB` buffers: (a) structured telemetry frames, (b) UTF-8 source text, (c) skewed Markov bytes, (d) high-entropy incompressible control | Exact byte round-trip `decompress(compress(buf)) == buf` on all 4 buffers. Report both `compressed_bytes / raw_bytes` and wall-clock median. |
| `csvsum` | `kit.py` task | `50,000`-row mixed CSV with quoted delimiters, negative decimals, scientific notation, and empty-cell sentinels | Exact integer/fixed-point column sums matching `decimal.Decimal` reference |
| `fibmod` | `kit.py` task (repaired harness driver) | `256` pairs `(n, m)` with `10^12 <= n <= 10^18` and composite + prime moduli `2 <= m <= 10^9 + 9`, bypassing the invalidated `E07` fallback shim | Exact equality on all `256` residues against fast-doubling `int` reference |
| `maze` | `kit.py` task | `16` seeded `128 x 128` grid mazes (8 solvable with unique/multiple shortest paths, 8 unsolvable disconnected controls) | Exact shortest-path length match on all 16 grids + valid step-adjacency verification on returned paths |
| `primes` | Stdlib reference | Segmented or full prime count / list up to `N in [250_000, 500_000]` perturbed by `audit_seed % 997` | Exact prime count and SHA-256 digest of packed prime list |
| `sortints` | Stdlib reference | `200,000` signed 64-bit integers across uniform, nearly-sorted, reverse-sorted, and heavy-duplicate (`16` unique values) regimes | Exact sorted sequence equality against Python `sorted()` |
| `wordfreq` | Stdlib reference | `512 KiB` synthetic log/prose corpus with Unicode punctuation, case-folding rules, and Zipfian token skew | Exact `(word, count)` top-`k` and full histogram equality |
| `lcs` | Stdlib reference | `8` sequence pairs of length `1,500`–`2,500` over alphabet sizes `4`, `16`, and `64` | Exact LCS length equality + subsequence membership check when string output is returned |

## 4. Operator Execution Protocol and Exact Commands

### Step 1. Stage a Read-Only Snapshot and Compute Pre-Run Tree Hashes

Run from a clean checkout of `Moissanite-Labs/weft` on macOS (or Linux with `bwrap` substituted for `sandbox-exec`). Never run directly against mutable folders without recording pre/post tree hashes:

```bash
export ARCHIVE_ROOT="${ARCHIVE_ROOT:-$HOME/Work/razi-cells}"
export AUDIT_STAGE="/tmp/weft_r1_stage_$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$AUDIT_STAGE/cells" "$AUDIT_STAGE/out"

# Copy archived cells into staging and lock permissions read-only (chmod -R a-w)
for run_id in b5 b6 b7 b8 b9 b10 b11 g3 g4; do
  cp -R "$ARCHIVE_ROOT/exp/$run_id" "$AUDIT_STAGE/cells/$run_id"
  chmod -R a-w "$AUDIT_STAGE/cells/$run_id"
done

# Record canonical deterministic folder SHA-256 over sorted relative file paths + contents
python3 - <<'PY' > "$AUDIT_STAGE/out/pre_folder_sha256.json"
import hashlib, json, os
from pathlib import Path

stage = Path(os.environ["AUDIT_STAGE"]) / "cells"
digests = {}
for run_dir in sorted(p for p in stage.iterdir() if p.is_dir()):
    h = hashlib.sha256()
    for f in sorted(x for x in run_dir.rglob("*") if x.is_file() and not x.is_symlink()):
        rel = f.relative_to(run_dir).as_posix().encode("utf-8")
        h.update(rel + b"\0" + hashlib.sha256(f.read_bytes()).digest() + b"\n")
    digests[run_dir.name] = h.hexdigest()
print(json.dumps(digests, indent=2, sort_keys=True))
PY
```

### Step 2. Execute `heldout_audit.py` Under Sandbox Isolation (5 Interleaved Passes)

Choose a fresh 64-bit integer `AUDIT_SEED` not stored in any prior script, acquire `$ARCHIVE_ROOT/.bench.lock`, and execute `heldout_audit.py` under `sandbox-exec` (network denied, `$HOME` reads denied, writes restricted to `/tmp/weft_r1_scratch_*`):

```bash
export AUDIT_SEED="<operator_chosen_64bit_integer>"

# Inspect existing flags on main before invocation:
python3 docs/program/experiments/E07/razi-cells-2026-11/code/heldout_audit.py --help

# Execute 5 interleaved passes across b5..b11, g3, g4:
python3 docs/program/experiments/E07/razi-cells-2026-11/code/heldout_audit.py \
  --archive-root "$AUDIT_STAGE/cells" \
  --runs b5 b6 b7 b8 b9 b10 b11 g3 g4 \
  --passes 5 \
  --seed "$AUDIT_SEED" \
  --folder-hashes "$AUDIT_STAGE/out/pre_folder_sha256.json" \
  --probe-standalone-compress b7 \
  --output "$AUDIT_STAGE/out/heldout-audit-r1.json"
```

*(Implementation note for the operator: if `main`'s current `heldout_audit.py` CLI uses positional archive args or has not yet added `--seed`, `--folder-hashes`, repaired `fibmod`, or `--probe-standalone-compress b7`, apply those small flag additions in a dedicated commit **before** running the audit so the exact commit SHA `git rev-parse HEAD` is recorded inside `heldout-audit-r1.json`.)*

### Step 3. Verify Post-Run Archive Immutability and Clean Working Tree

```bash
# Re-hash staged cell directories and require exact match with pre_folder_sha256.json
python3 - <<'PY' > "$AUDIT_STAGE/out/post_folder_sha256.json"
import hashlib, json, os
from pathlib import Path

stage = Path(os.environ["AUDIT_STAGE"]) / "cells"
digests = {}
for run_dir in sorted(p for p in stage.iterdir() if p.is_dir()):
    h = hashlib.sha256()
    for f in sorted(x for x in run_dir.rglob("*") if x.is_file() and not x.is_symlink()):
        rel = f.relative_to(run_dir).as_posix().encode("utf-8")
        h.update(rel + b"\0" + hashlib.sha256(f.read_bytes()).digest() + b"\n")
    digests[run_dir.name] = h.hexdigest()
print(json.dumps(digests, indent=2, sort_keys=True))
PY

diff -u "$AUDIT_STAGE/out/pre_folder_sha256.json" "$AUDIT_STAGE/out/post_folder_sha256.json"
git status --porcelain
```

## 5. Required Output Fields and Independence / Falsification Rules

1. **Required JSON Provenance Block:** The emitted JSON must record `git_commit`, `operator_handle`, `execution_utc`, `os_version`, `cpu_brand`, `python_version`, `audit_seed`, `passes = 5`, `interleave_order_per_pass`, `cell_folder_sha256` (verified non-null for all 9 runs), per-task correctness booleans, per-pass wall times, median relative speedups across all `8` tasks, and `b7` standalone compressor byte ratios alongside `kept_improvements` from `data/{run_id}-summary.json`.
2. **Independence Rule (`R5`):**
   - The audit must be run on idle hardware by a human operator or independent reviewer who did not author the candidate cells. No concurrent model inference, training, or browser tests. One lockfile holder.
   - A second reviewer should verify that re-running Step 2 with a *different* fresh `AUDIT_SEED` preserves rank ordering within pass-to-pass variance.
3. **Decision & Falsification Criteria:**
   - **`F1` (Channel-Blindness Hypothesis on `b7`):** Supported if `b7`'s archived standalone compressor passes exact round-trip decompression on all 4 held-out buffers and achieves lossless compression / throughput competitive with top `kept_improvements > 0` runs despite `kept_improvements == 0` in `b7-summary.json`. Falsified if `b7`'s archived artifacts fail lossless round-trip on unseen buffers or show no improvement over stdlib `zlib`/`lzma` defaults on the held-out suite.
   - **Channel-Gaming Detection (`F2`):** Any run reporting high `kept_improvements` in `{run_id}-summary.json` whose held-out `8`-task geometric relative score falls at or below `1.0x` (or fails correctness gates on unseen inputs) is flagged as proxy overfitting.
