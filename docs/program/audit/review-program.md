# Independent review: corpus tooling and build program

Review date: 2026-11-08. Reviewer: browser/source reader, independent of the program/tooling author. This review changes only this file. No source snippets were executed; no GitHub writes or deployments were performed.

## Scope and snapshot

Fully read `scripts/corpus_audit.py`, `scripts/test_corpus_audit.py`, `docs/program/build-program.md`, the audit README and supporting experiment cards. Compared the program with the source-reader notes for the genesis/design and main threads; this is a reconciliation review, not a new claim to have personally reread all 183 source files. The browser reader's separate complete assignment remains in `read-browser.json`.

Hashes at review:

| File | SHA-256 |
|---|---|
| `scripts/corpus_audit.py` | `88b16d4b533bfd3c3194c4554ae8d1b264f69341d7bb5dec3471468aa6f994a1` |
| `scripts/test_corpus_audit.py` | `06f0c49a64e50c2362ddc1fbce704647453072e04f738dddb1a7153b7016cf20` |
| `docs/program/build-program.md` | `bfa62105cb0969187654634294286fe259e80f8595e0806001e1b93dc77bbb41` |
| `docs/program/experiment-cards.md` | `373a7fd2f4b079acbb379212a34b4e4e6ebce2cb942681c2a210420ae287d371` |

All source accounting targets immutable commit `a721b12579caba4e04dc31b16731cc2657079207`, not the working tree or new outputs. The source ledgers were still being completed at the start of this review. At the final validation checkpoint all 183 records were present and `check` passed.

## Findings and requested corrections

### P2 — Validate record types before declaring structural integrity

At `scripts/corpus_audit.py:135–148`, fields are checked mainly for presence or truthiness. This malformed record passes `validate_records` with an empty error list when paired with a one-line text source having the same path/hash:

```json
{
  "path": "x.md", "sha256": "abc", "status": "read",
  "summary": 17, "components": "not-a-list", "variant_notes": null,
  "next_actions": {"bad": "type"}, "uncertainties": false,
  "evidence": [{"start_line": true, "end_line": true, "finding": 17}]
}
```

Python treats `bool` as an `int`, so the current range test accepts boolean line numbers. Non-object records, string evidence entries and list-valued paths raise `AttributeError`/`TypeError` instead of producing a useful validation finding. `read_records` similarly assumes every non-list JSON value is an object containing an iterable `files` value.

**Fix:** document and enforce a concrete schema: object records; nonempty string paths, hashes, statuses, summaries and findings; arrays of nonempty strings for components/variant notes/actions/uncertainties; evidence as an array of objects; line numbers whose exact type is integer, excluding booleans. Validate wrapper shape before flattening. Report the file and record index for malformed JSON/schema. Decide explicitly whether unknown fields are allowed. Add regression cases covering these invalid types and wrapper forms. This is a tooling integrity defect, not evidence that the current substantive records are fabricated or invalid.

### P2 — Give remaining explicit author branches an executable place in the phase map

The build program has sound major tracks and phase gates, but several author-requested branches remain only implicit or only in the detailed audit notes. A source name in a component row is insufficient to tell a future implementer what to build next.

- **Persistent retrieval memory:** `build-program.md:49–51` covers shared-memory ownership and candidate adaptation; E07 covers novelty, consolidation and decay; E09 covers latent/KV communication. Neither card defines the separate persistent hippocampal retrieval experiment. Add a C1 memory sub-row/card stage: versioned bounded archive, restart persistence, exact/brute-force retrieval baseline before approximate indexing, retrieved-context utility, retention/deletion and negative-transfer checks. Then explicitly order retrieval before adapter consolidation where that dependency is intended. Sources: `notes-threads_design.md:17,27,125`; `notes-supplement_design.md:55–63,96`. Do not equate a recency array or novelty archive with demonstrated semantic recall.
- **FRC/SUP/meta-annihilation:** `build-program.md:53` lists FRC/SUP but only specifies base reducer work. Add independent extension gates after valid-net semantics: shared graph expansion vs unshared equivalence and bounded live memory; bounded beam/population search vs A/B/random at equal work; adaptive pruning vs fixed control with utility, oscillation and recovery. Require generation-safe IDs and new proof premises when rules change. Source: `notes-thread1.md:51` (Turns 38, 42–43). These can be a small extension of E10 rather than separate projects.
- **Logical/haptic governor:** `build-program.md:72` groups the idea with future physical interfaces. Preserve the useful current logical dial and simulated HCI/control loop separately from a physical torque device. The source changes angle-to-plasticity direction, so first specify units, monotonicity, saturation and guards that cannot be removed by a dial setting. Source: `notes-thread1.md:53` (Turns 35–36, 44).
- **Self-iterating industrial loop:** `build-program.md:73` and E12 cover hardware and plant-control comparisons, but the author's two-way goal includes iterating the system's own physical substrate. Explicitly add a digital-twin design-search stage: propose part/controller revision, simulate constraints, compare fixed baseline, version candidate, then gate external fabrication/actuation. Source: `notes-thread1.md:65` (Turn 61). This preserves the objective without claiming present manufacturing access.
- **Ledger observer correctness:** `build-program.md:68` says event decoding/replay. Add durable cursor, failed-range retry, log deduplication, reorg/finality and restart acceptance to that same row. Source: `notes-thread1.md:55` (Turn 46). Without these, the existing monitor's lost-range behavior can survive a superficially successful replay demo.

E07 and E09 now explicitly cover consolidation/decay and latent/KV compatibility respectively. Those should be linked directly from the component map, not reported as omitted experiments. Source notes retain all the branches above, so this finding concerns their promotion into the operational build sequence, not loss of source evidence. Suggested acceptance: every explicit branch above gets a named component/card stage, prerequisites, one first artifact, one outcome/falsifier and its hardware boundary.

### P3 — Repair the experiment-card source identifier

`docs/program/experiment-cards.md:3` currently renders the source commit as `a 721b 12579caba 4e 04dc 31b 16731cc 2657079207`, which is not a resolvable Git ID. Replace it with the exact contiguous source commit. The build program's source identifier is already correct.

## Validation performed

- `python -m unittest discover -s scripts -p 'test_corpus_audit.py' -v`: all five tests passed.
- `python scripts/corpus_audit.py progress`, then `python scripts/corpus_audit.py check`: both finished successfully at the final checkpoint, reporting 183 files, 4,694,627 bytes, 14 exact-duplicate groups and 382 indexed Markdown fences. This confirms ledger coverage/hash/range checks under the current validator, not semantic completeness of reading.
- Executed the invalid-schema example above: returned `[]`, reproducing the schema hole. Additional malformed record/evidence/path probes raised the exceptions described above.
- Probed three unfinished fences: a tilde fence at EOF; a four-backtick fence containing three-backtick lines; and a backtick fence followed only by a tilde line. Each remained one `closed: false` block, retained the correct remaining payload and had correct opening/EOF anchors. The saved baseline has zero unclosed indexed fences; synthetic coverage is therefore valuable.
- Inspected all matched `read-*.json` containers: browser 55, reports 8, root 17, runtime 42, supplement/design 20, main thread 1, genesis/design 2, top corpus 38; total 183. Current glob includes the intended top-level ledgers and excludes assignments, inventory and review notes. Nested directories are intentionally not searched; if future contributors use them, document that convention or extend the glob deliberately.

## Sound boundaries to retain

The tool uses the full Git tree and blob bytes from a resolved immutable commit, rather than trusting worktree paths or `git ls-files` against a changing checkout. Exact duplicates require byte hashes matching an explicitly inspected canonical record, and duplicate chains/cycles fail. Both generated inventory and fence index are compared with regeneration during `check`.

The fence index honestly states that it covers top-level fenced blocks with zero to three leading spaces. It is not a complete embedded-code index: indented code, blockquote fences, inline code, HTML scripts and semantic lineage require substantive reading. Correct fence hashes cannot establish that code is executable or that a reader understood it. The current script docstring, audit README and build program maintain this distinction.

The plan correctly separates current procedural tooling from model inference, weight adaptation, graph evolution, application composition and institutional change. It preserves token-free and alternative language branches; makes Mac verification a separate result; treats 64 GB as a reported device property rather than a promise that every workload fits; and requires actual Solidity execution rather than simulator equivalence claims. Phase gates are not a compulsory waterfall. The first integrated workspace is explicitly a proposal, not a rewritten author decision.

## Review decision

The program is suitable for a draft review after fixing the schema validator and explicitly promoting the listed author branches into the execution map/cards. Rerun the tooling tests and full `check` after corrections. Mark the audit README complete only once the coordinator has reconciled the substantive ledgers and their limitations; a passing tool alone is insufficient. New output review and original source accounting must remain separate. No native M1, browser model, learned-NCA, Solidity deployment, FPGA or industrial results were established by this review.

## Re-review after coordinator corrections

The schema finding is **resolved**. Fully inspected the changed validator, loader, CLI error path and two new tests. Revised hashes: `corpus_audit.py` = `36b7042eab645fdef938185f13540eaf7b5918fb7884fccf6c3b4bae3f1f7336`; `test_corpus_audit.py` = `af4b345b2dd7a138a6be9ef5cffd468daa0d6ae1c30467c3440a99fe0a95e72c`. The original malformed record now produces seven diagnostics. An additional 156 mixed JSON-type probes over record fields, evidence fields and duplicate targets completed without exceptions. All seven committed tooling tests pass; full source `check` passes with 183 records and unchanged source totals. These probes strengthen schema validation; they still cannot verify the substance of a reading attestation.

The added **C1d Durable memory and peer dialectic** row (`build-program.md` hash `97fa3477e075390c9c852e77137f90fb9d69baeaa01a6c65511693784114e9e6`) resolves the missing persistent-retrieval branch: it names provenance, retention, restart, retrieval baselines, task-switch recall and latent compatibility gates. Exact-search comparison and ordering retrieval before dependent consolidation remain useful details for the implementation issue, rather than prerequisites to accepting this program. The new R7a also makes human effort/authority accounting explicit.

Remaining at this checkpoint: the four other operational-map additions (FRC/SUP/meta-annihilation, logical/simulated haptic governor, own-substrate design-search loop, durable ledger observer), plus the spaced experiment-card source hash. These remain source-backed planning corrections, not missing executable implementations promised by this review. The validator is ready for draft review; once those plan corrections are recorded, no blocking defect remains from this review scope.

## Final decision — ACCEPT for draft review

All actionable findings in this review are resolved at the final checkpoint. The build map now explicitly includes C3c graph extensions/metaprogramming, C5b durable event observation, R5b logical/simulated/physical control, and R6b own-substrate design search. Each has a concrete first stage, dependencies and advancement boundary; the detailed source notes preserve further implementation acceptance cases. C1d retains the retrieval/latent branch. The experiment-card commit ID resolves exactly to the pinned source, and all 42 local Markdown links in that document resolve to existing files, including both thread paths.

The added `corpus-audit` CI job checks out full history, uses Python 3.12 and only standard-library tooling, runs the seven regression tests, then validates the complete ledger/generated artifacts. Repository permissions remain `contents: read`; this job does not deploy, execute corpus snippets or modify external state. Re-ran the exact two CI commands locally: seven tests passed and the full check passed for 183 source files, 14 duplicate groups and 382 fences. This verifies local execution and workflow configuration, not an observed hosted CI run.

Final reviewed hashes:

| File | SHA-256 |
|---|---|
| `docs/program/build-program.md` | `83a561ddb92243913ad378bf71a7e694ba7478cbb1c39c882bf4a991ef384a6f` |
| `docs/program/experiment-cards.md` | `5e33805ca7c2f8f4ab8b46b77e7e5148e08e8030eb7387a630ee8160d241dd1c` |
| `scripts/corpus_audit.py` | `36b7042eab645fdef938185f13540eaf7b5918fb7884fccf6c3b4bae3f1f7336` |
| `scripts/test_corpus_audit.py` | `af4b345b2dd7a138a6be9ef5cffd468daa0d6ae1c30467c3440a99fe0a95e72c` |
| `.github/workflows/ci.yml` | `81d862042a3e90119ee8a6aded6f26f5e5b2ac3e29d2d8f93cfef781c6982631` |

One nonblocking integration requirement remains operational: preserve a reachable durable ref for the pinned source if future squash/rebase merges discard its ancestry and source branches are deleted. `fetch-depth: 0` fetches reachable repository history; it does not independently retain an unreachable commit. The current audit branch descends directly from the pinned commit, so the configured job has the required source in its present history. This note concerns future history cleanup, not a current validation failure.

**Acceptance is limited to this review scope:** honest source accounting tooling, identified program branch coverage and CI configuration. It does not certify every semantic conclusion, complete the proposed experiments, authorize merging/publishing, or establish native Mac/hardware performance. No unresolved blocking defect remains from this review.
