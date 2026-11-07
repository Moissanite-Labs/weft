# Claims register

This register is cross-source and de-duplicated. Every entry gives a location, the claim, what the evidence shows, and what would prove the entry wrong. Per-file detail lives in [`sources/`](sources/).

**Status**
- `VERIFIED`: re-checked by running code or reading the cited lines, for PR #12.
- `REPORTED`: found by a mapping agent with line citations, but not yet re-run.
- `OPEN`: a contradiction or question that only evidence can close.

**Category**: theory · mechanism · contract (an engineering contract) · governance · economics · hardware · vision (a vision-language name; it stays, per PROGRAM.md and #6, but is not claimed as implemented).

Under PROGRAM.md, contradictions stay open here until evidence resolves them. When an entry is actionable, its issue number is given.

## 1. Repository code (already extracted)

| ID | Location | Claim / finding | Evidence | Falsified by | Status | Issue |
|---|---|---|---|---|---|---|
| R1 | `weft/runtime/core/selftest.py`, `weft/runtime/aywa/weft_daemon.py` | The self-tests rewrote tracked files (`moissanite_telemetry.json/.bin`). | `git status` was dirty after a run. Fixed in PR #12: output now goes to a temp directory. | A clean run leaving the tree dirty | VERIFIED, fixed | PR #12 |
| R2 | `weft/runtime/aywa/sym2p_codec.py`, `docs/assets/js/sym2p-parse.js` | The codec did not round-trip (encoded decimal, parsed hex), and a missing hash counted as valid. | sequence 42 decoded as 66. Fixed, with tests. | A spec that outranks `craft.md:136-145` | VERIFIED, fixed | #13 |
| R3 | `weft/runtime/core/weft_plasm.py:190` | A literal the corpus calls the user's "private identity passphrase" (`xtra.md:95`) is hard-coded as an RNG seed. | Read in place. The same literal appears in 7 corpus files (`safety-index.md` S1). | The literal is not that passphrase, or the owner declares it public | VERIFIED | #14 |
| R4 | `weft/runtime/aywa/github_harvester.py:17-37` | The "Moissanite-Labs 19-repo telemetry harvester" harvests nothing. Commit, PR, and issue counts are constants in the source. The Pages site shows them as live telemetry (`docs/data/*`). | Read in place. There are no network calls. | Any GitHub API call in the harvester path | VERIFIED | #15 |
| R5 | `weft/runtime/aywa/github_harvester.py:39-42` → `docs/data/moissanite_telemetry.json` | Two named GitHub logins marked `SUSPENDED` are published in the Pages data. | `grep` finds both logins in `docs/data/moissanite_telemetry.json`. | — | VERIFIED | #15, #27 |
| R6 | `weft/runtime/aywa/weft_daemon.py:19-26` | "Reads real Darwin sysctl / Mach telemetry". On any failure it silently reports 10 CPUs and 64 GB, values that look measured. | On Linux the run printed `ncpu: 10, mem_gb: 64.0`. | Output marked as fallback | VERIFIED | #16 |
| R7 | `weft/runtime/core/weft_plasm.py` (shared-memory view) | The plasm leaves an exported pointer into the shared-memory buffer, so Python raises `BufferError: cannot close exported pointers exist` at exit. | Observed on every `selftest.py` run. | A clean exit with no BufferError | VERIFIED | #17 |
| R8 | `.github/workflows/pages-seed-deploy.yml` | The core selftest step is `continue-on-error` and installs neither numpy nor torch, so it can never pass in CI. No workflow runs any test on pull requests. | Read the workflow. `selftest.py` needs torch. | — | VERIFIED | #18 |
| R9 | `docs/` | `docs/` is both the Pages root and the home of internal notes (PROGRAM.md). The deploy job copies all of `docs/` into `dist/`. | Read the workflow. | — | VERIFIED | #19 |
| R10 | `weft/runtime/ledger/` | The ARCH-LOCK (`WEFT-ARCHITECTURE-LOCK.md:16`) treats the triad as locked, but only two of the three contracts are extracted. `TensionGovernor` (`weft/README.md:269-383`) is missing. | `ls weft/runtime/ledger` | — | VERIFIED | #20 |
| R11 | `docs/assets/js/aesthetic-mixer.js:32-38` | The site ships the linear hue average that `baryonic.md:94` says is wrong; later variants use the circular mean (`discovery.md:239-246`). | `sources/A` §6.1 #8 | The mixer uses atan2 | REPORTED | #24 |
| R12 | `docs/assets/js/weft-loom.js:118-148` | The WebGPU path never sizes the canvas, so it renders at 300×150 and is stretched. | `sources/A` P6 | — | REPORTED | #24 |
| R13 | `docs/index.html:6,25` | The page advertises "lineage workers" and a "SharedArrayBuffer telemetry bridge". Neither exists as described. GitHub Pages cannot send COOP/COEP headers, so SAB is unavailable there, and the main thread never reads the SAB. | `sources/A` P26, P30 | — | REPORTED | #24 |
| R14 | `docs/widgets/*.html`, `docs/widgets/index.html:27` | The widgets are Google sandbox exports. They load React/Radix from `widgetlibs.static.usercontent.goog`, while the gallery says "zero network". Titles 01, 02, 03, and 05 do not match their contents. 04 is not a learned NCA. | `sources/A` P32, `sources/F` finding 1 | — | REPORTED | #24 |
| R15 | `weft/runtime/core/weft_ic_vm.py` | A real port-based Lafont VM, limited to ERA/CON/DUP. None of the corpus interpreters is its source. VLV, FRC, and SUP are not in it. | `sources/D` finding 3, `sources/E` #24 | — | REPORTED | #21 |

## 2. Mechanisms and theory

| ID | Location | Claim | What the code does | Falsified by | Category | Status |
|---|---|---|---|---|---|---|
| M1 | `almalga.md:146-165`, `thread1:149-165` | Selection score = fitness + α·novelty against a target. | **Not implemented anywhere.** Every harness picks min ‖output‖. The novelty α is never read. Where novelty is computed (splicers v8), it outweighs fitness by roughly 100–1000×. | A harness that computes F + αN and commits the update it scored | mechanism | REPORTED (#22) |
| M2 | `almalga.md:95-101` | The plasticity mask freezes "core safety boundaries". | Softmax over 512 row norms gives a mask between 0.91 and 1.0, so it protects nothing. Nothing maps safety rules to rows. | A mask distribution with a frozen fraction above 0 | mechanism / vision | REPORTED (numpy-checked by G, H); #22 |
| M3 | `almalga.md:177-183` | Homomorphic key-watermark; stripping it "destroys calculation logic". | A linear trigger→response watermark (W·x≈y). One rank-1 update removes it. It is never embedded in several variants, so the match stays near 0% and the 94–99% figures are invented. | Subtract outer(y,x) and show behaviour on other inputs is unchanged | mechanism | REPORTED; #4 |
| M4 | `prove.md`, `thread1:3764-3864` | A "formal prover" (Hoare/WP/SMT). | Two float comparisons, measuring a difference of norms (the trap #2 fixed). | — | theory | REPORTED; the repaired form is in `weft_plasm.verify_weight_update_safety` |
| M5 | `provocol.md`, `thread1:3946-3999` | The Lean theorem proves "trustless autonomy homeostasis". | The hypotheses restate the goal. No Lean source is in the repo. | A Lean proof of a non-trivial property linked to code | theory | REPORTED |
| M6 | `weft_invariants.h` (`thread1:7429-7511`) | The C gate preserves the global invariant. | The budget is decremented without checking `budget ≥ 2.5`, so the gate can break its own invariant. NaN gets through. | A transition that leaves budget below 0 is accepted | contract | REPORTED |
| M7 | Global Safety Invariant | One invariant. | Three incompatible definitions (`prove.md:31`, `prove.md:92-97`, `provocol.md:52-55`). The bound is ≤85 in prose (`thread1:3752`) and <85 in Lean, C, and Python. | — | contract | OPEN; #23 |
| M8 | IC rewrite rules | "Lafont interaction combinators". | The corpus interpreters ignore ports, delete both nodes on every rule, and lack same-kind annihilation. Each rule just nudges "tension" and "vault" numbers (+15/+35/+40 across versions). CON-ERA gives ∅, Wire(x,y), or eraser propagation in three places. | — | theory | REPORTED; #21 |
| M9 | Node set | ERA, CON, DUP, VLV, FRC, SUP. | Grows to 6 types (`thread1:5152, 5503`). The dissertation and whitepaper list 5 and drop FRC (`6748-6754`, `8070-8076`). DUP and FRC have no rules in the latest interpreter. | — | theory | OPEN |
| M10 | Hippocampal novelty lattice | Anti-homogenization memory. | A recency buffer scored by mean distance (PROGRAM.md). The archive is 32 entries in the spec (`splicers:3104`) and 16 in code. | — | vision | REPORTED |
| M11 | Sympathetic ring | Autonomic regulation. | Telemetry floats. Three variants overwrite the array with a scalar (`symp_matrix = budget`). Only the latest harness indexes it correctly (`thread1:7780-7787`). | — | vision | REPORTED |
| M12 | "Homeostasis" band 15–35 | Tension is regulated into the band. | With default sizes, tension is about 115 from step 1. `selftest` shows 110–112. Min-norm selection plus decay drives weights toward zero ("homeostasis is decay"). | A run that stays in 15–35 | mechanism | VERIFIED (selftest output) / REPORTED |
| M13 | Exo-mitosis | Migrate a LoRA delta over authenticated UDP/RDMA. | Unauthenticated TCP sending the whole 512×512 matrix. Node β listens on 7778 while α connects to 7777. | — | mechanism | REPORTED |
| M14 | "Unified Fractal Topology Proof" (`thread1:7245-7301`) | O(1) vs O(N) latency. | The rate formula is dimensionally inverted. The benchmark compares `sleep()` loops against one matmul. | Dimensional analysis | theory | REPORTED |
| M15 | Unified IC language (`thread1:4101-4111`) | Execution is verification; reduction is lock-free across 32 GPU cores. | Single-threaded Python FIFO loops with no types. | Profiling any interpreter | theory / vision | REPORTED |

## 3. Ledger and economics

| ID | Location | Finding | Status | Issue |
|---|---|---|---|---|
| L1 | `WeftTokenTissue` constructor; runbook `weft/README.md:388` | All 21M WEFT are minted to `governorCore`, which the runbook sets to the TensionGovernor contract. That contract has no function to move tokens (only slash, set-harness, and transfer-weaver), so the supply is locked and no swarm ever holds tokens. | VERIFIED (read the contracts) | #20 |
| L2 | `executeExcisionValve` | Any authorized harness can debit any address without that address's consent. | REPORTED | #20 |
| L3 | `reportTensionFracture` | Anyone can file a report. When no creator is found, the slash goes to the reporter. Lineage claims are first-come. | REPORTED | #20 |
| L4 | `TensionGovernor` | The "autonomous court" is one admin key (`technicalWeaverCore`). The fixed 500-WEFT penalty makes adjudication revert against poorer swarms. This is the constitution-vs-contract gap PROGRAM.md Phase 3 names. | VERIFIED (read the contracts) | #20 |
| L5 | Royalty rule | Three different rules: 70% of fee (`thread1:210`), 15·match% (`605`), and an 85/15 split (`773`). | REPORTED, OPEN | #20 |
| L6 | Fracture threshold | The latest harness reports at T>40 (`thread1:7959`), but the contract requires T>85 (`850`). Reports in between revert. | REPORTED | #20 |
| L7 | `monitor_excision.py` (`self.md:242`, `thread1:6079`) | The event topic constant is wrong. keccak256(`CapitalExcision(address,address,uint256,bytes32)`) = `0x42e63d16…629b`, not the `0xb697db12…` the corpus uses. The monitor also decodes an indexed `weightHash` from `data`. | VERIFIED (keccak helper checked against the known `Transfer` topic `0xddf252ad…`) | #20 |
| L8 | Triad variants | V1 (`README:42-383`, the most complete), V2 (`README:1065-1316` = `almalga:645-878`, missing `approve`/`verifyAttribution`/`transferWeaverCore`), and V3 (`launch:40-234`, also missing `transferFrom`; the one the deploy script would actually deploy). | REPORTED | #20 |
| L9 | Arbitrum Stylus | "Deploy Solidity as WASM on Stylus". Stylus does not compile Solidity. The flags are invented. | REPORTED | #20 |
| L10 | Economics | Post-economic fork (`thread1:3443`, tokens stripped) vs valve restored (`4503`, `8102-8134`). Both are in the whitepaper. | OPEN | — |

## 4. Hardware claims

| ID | Claim | Finding | Status |
|---|---|---|---|
| H1 | Reads SMC temperatures on M1 Max | Reads Intel-only `machdep.xcpm.cpu_thermal_level` (absent on Apple Silicon), then uses random temperatures. | REPORTED |
| H2 | ARM64 EL1 purge | Uses x86 `cli`/`sti`. `tlbi`/DAIF need EL1. It cannot run from a macOS user process. `more.md` has an x86 variant. | REPORTED |
| H3 | Fan/SMC actuation | `smc_actuator.py` explicitly simulates ("We simulate"). | REPORTED |
| H4 | No-FS MMIO storage | Needs a kernel driver. There is no code. | REPORTED |
| H5 | NCCL hypersphere | Needs NVIDIA GPUs. The target is an M1 Max. | REPORTED |
| H6 | "macOS Golden Gate 27.0.1" | No such release exists. | REPORTED |

## 5. Governance and vision

| ID | Location | Note | Status |
|---|---|---|---|
| G1 | `govern.md:37-38` vs `:15-28` | Evading state asset seizure is presented as a design goal, while law is called an unbreakable invariant. | OPEN |
| G2 | `wrap.md:29`, `thread1:950`, `3339-3340` | Instructions for the model to move its own parameters off the machine autonomously ("software can no longer be controlled"). This needs a governance decision and an explicit non-goal. See `safety-index.md` S9. | OPEN; #25 |
| G3 | `imprint.md`, `thread1:6185-6336` | Post-mortal "extrapolation of will", enforced by harvesting tokens and commanding hardware. PROGRAM.md separates style prior, predictive model, and survival. Keep as vision; not a biological claim. | OPEN |
| G4 | `spread.md:17` vs `ethos.md:56-60` | Praises cells that take others' IP, which contradicts the anti-piracy valve. | OPEN |
| G5 | `xtra:248-249` vs `tune:22/30`, `thread1:291` vs `4999-5000` | Dial direction vs plasticity is reversed between sources. "Dissolving safety gates at 180°" is framed as a feature. | OPEN |
| G6 | `converge.md:39-44` | On-chain payouts tied to user attention. Speculative; needs ethics and regulatory review. | OPEN |
| G7 | Licensing | "proprietary protocol" (`thread1:3913`) vs "open-source" (`8019`). Must be decided before going public. | OPEN; #27 |
| G8 | Name origin | "Weft" is attributed to Luca Berton's language (`thread1:4441-4452`) and also derived from the loom metaphor (`splicers:133-154`). | OPEN; #27 |

## 6. Design-folder (Pages) contradictions

These are summarized from `sources/A` §6.2.
- The uniform layout is 16, 32, or 48 bytes in the design and 64 bytes in `docs/`.
- Metric keys are `tension`/`gini` vs `con`/`owner`/`lbl`/`res`/`cap`.
- Data paths are `public/data/` (writers) vs `data/` (readers).
- The three design workflows each force-deploy to `gh-pages`, so they overwrite one another, and `aywa.md`'s `deploy.yml` replaces the data with empty files.
- The polling interval is 15 s, 30 s, or 45/60 s.
- Action-state `03` means "Executing" in the table, but the shader treats `1.0` as active.
- **No design shader compiles as written:** `mod()` is not WGSL, the full-screen triangle covers half the screen, and the glyph masks are 35 bits. `docs/` avoids these bugs by construction.
