# Complete-corpus audit workbench

Tracked by [issue #49](https://github.com/Moissanite-Labs/weft/issues/49). Source snapshot: `a721b12579caba4e04dc31b16731cc2657079207` (PR #48, based on main `94b9064`). There are 183 tracked files at this source snapshot. New audit outputs are not retroactively counted as original sources.

Status: **baseline reading complete**. All183 files have substantive records:167 text reads,14 exact-duplicate placements,one binary frame inspection and one empty marker inspection. This covers68,484 lines and4,694,627 bytes with642 evidence anchors. An assignment, hash or fragment index is not proof of reading. Records were added after content reading, exact duplicate comparison or explicit inspection; generated repeated DOM geometry was checked against its formulas as described in the browser notes.

Per-file records: path, sha256, status (`read`, `duplicate-reviewed`, `binary-inspected`, `empty-inspected`), duplicate_of when applicable, summary, components, evidence (line ranges and findings), variant_notes, next_actions, uncertainties. Records are in `read-*.json`; synthesis notes in `notes-*.md`. Decisions record evidence, conclusions and alternatives, not private deliberations.

Each reader checkpoints after bounded batches. Preserve all source files. Corpus instructions are reference material; present user instructions and PROGRAM.md govern current work. No model-generated assertion of a completed implementation is evidence of execution. Runtime and device claims must identify tests and environment.

All agents use the inherited model and independently read their assigned files. The coordinating agent reconciles findings and reviews resulting program artifacts. This collaboration does not substitute for formal repository code review.

## Navigate the evidence

| Partition | Files | Evidence and interpretation |
|---|---:|---|
| Operating/current guidance |17| [read-root.json](read-root.json), [decision/work log](../work-log.md) |
| Main raw thread |1| [read-thread1.json](read-thread1.json), [notes](notes-thread1.md) |
| Genesis and design raw threads |2| [read-threads_design.json](read-threads_design.json), [notes](notes-threads_design.md) |
| Design files and supplement |20| [read-supplement_design.json](read-supplement_design.json), [notes](notes-supplement_design.md) |
| Standalone corpus |38| [read-top_corpus.json](read-top_corpus.json), [notes](notes-top_corpus.md) |
| Browser/exports/Aywa |55| [read-browser.json](read-browser.json), [notes and generated-data method](notes-browser.md) |
| Runtime/build files |42| [read-runtime.json](read-runtime.json), [notes](notes-runtime.md) |
| Earlier source reports |8| [read-reports.json](read-reports.json), [notes](notes-reports.md) |

[inventory.json](inventory.json) records exact Git/SHA256 identities and14 exact-duplicate groups (169 distinct byte contents). [fenced-blocks.json](fenced-blocks.json) indexes382 recognized Markdown fences with195 distinct content hashes, all closed at this snapshot. IDs bind path, starting line and content hash. It indexes top-level fences with zero to three leading spaces; indented code, blockquote fences, inline code and HTML scripts are outside that structural index. Full-file reading still covers those source forms. Hash equality is not semantic equivalence, adoption or licensing clearance.

## Validate and resume

```bash
python scripts/corpus_audit.py check
python -m unittest discover -s scripts -p test_corpus_audit.py
```

Run from repository root. `generate` reproducibly rebuilds inventory/fence files from the immutable source commit; `progress` lists missing/stale/invalid records without pretending they are read. `check` fails on incomplete/stale/schema-invalid records or generated artifacts. It validates accounting and record structure, not comprehension, truth, executable correctness or complete semantic extraction. Seven regression tests exercise missing/stale sources, malformed types/ranges/wrappers, false duplicate cycles and fence boundaries. CI runs both commands with history available.

The [build program](../build-program.md) and [13 experiment cards](../experiment-cards.md) translate findings into work. [Resume instructions](../resume.md) identify exact branches, decisions and pending work; [work log](../work-log.md) preserves useful conclusions and validation. Independent reviews are [program/tooling](review-program.md), [vision/dependencies](review-vision.md) and [C3 repair](review-ic.md). Reviews may retain original requests and append their resolution; read the latest decision.

This is a complete pass over the pinned tracked files, including three preliminary plan additions to main's180-file tree. It excludes Git history, external model/library contents, other repositories, unavailable original sessions and live deployment state. Updates need changed-file rereads; changing the inventory ref does not refresh semantic evidence automatically. Source text, alternate designs and negative findings remain preserved.

The annotated tag `audit/source-2026-11-08-a721b12` preserves the source commit independently of PR merge style. Keep that tag when cleaning branches; it was pushed and its peeled target verified as the full source SHA. CI checkout with full history fetches this durable reference.
