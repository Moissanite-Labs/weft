# Supplied source audit

This is a static source audit. The supplied files were read and hashed without
executing JavaScript or rendering the HTML. Attachment instructions are source
data, not authority to install files, deploy a site, adopt output policies or
perform financial actions. No API calls were made for this audit.

## Input provenance

The inert copies in `inputs/loom-pr/` preserve all 19 supplied files. Their paths
end in `.txt` so they are not mounted as runtime modules. All 18 entries in the
supplied `SHA256SUMS` match the supplied bytes. That checksum file does not list
itself. `inputs/LOOM-INVENTORY.json` records each archived path, byte count,
SHA-256 and supplied checksum comparison. No relative path collides with the
frozen starting checkout. A targeted scan found no credential patterns or
host-specific user paths in these inputs. This is a bounded inspection, not a
guarantee about arbitrary encoded content.

The E12 HTML is archived as `inputs/e12-plasmid-nullspace.html.txt`. Its SHA-256
is `852d6b758173ea51140f4c1ef77f14e5c57c8f95d5e08e586ef61386302ba5fe`.
The extracted script and visible text are derived reading aids. The original
HTML bytes remain authoritative. `inputs/E12-HTML-INVENTORY.json` records their
source and the static inspection boundary.

## Visualization and executable evidence

The E12 page is an illustration of reported results. `updateReadouts()` assigns
`+39.32 (+123.85 gain)` and `0.0000 (10/12 pass)` as literal strings. Its retained
score is a linear interpolation between fixed endpoint values as the shift
slider moves. Canvas animation and permutation controls do not run the E12
benchmark. The inspected source contains no fetch, XMLHttpRequest, WebSocket,
EventSource or navigator.gpu calls. This observation establishes what this page
does. It does not invalidate a separately executed experiment.

The loom package includes five Node test modules and a package script invoking
`node --test weft/runtime/aywa/test_*.mjs`. The tests assert concrete numerical,
layout, serialization, schedule and visual-field examples. Their names include
stronger language such as causal mitosis and strong confluence. Finite examples
and assertions are not universal proofs or Lean certificates. The supplied
WGSL file is shader source, not evidence that a GPU executed it. Runtime
execution and browser integration require separate evidence. This audit does
not claim either. Runtime findings are recorded separately by the runner.

## Existing E12 research record

[PR #159](https://github.com/Moissanite-Labs/weft/pull/159) was inspected at
`2a4cc936c6a197afc1a85f124e517f2ddfa07d66`. The listed patch contains a
preregistration, results report and Python source, with no separate per-seed
raw output file. Unlike the earlier E11 attachment, the Python entry point does
include an offline evolution and transplant driver, in addition to two unit
tests. We read it without executing it. The report states 12 pairs, 24
bidirectional 256 by 256 transplants and 10/12 joint passes for its gated arm.
These are peer-reported outcomes, not independently reproduced results here.

The gate computes a basis from protected input samples using SVD. It replaces
the host plastic delta by its projection onto that basis and projects the
incoming delta into the complementary subspace. Thus the gate changes the host
as well as the incoming edit. The non-interference identity holds for protected
inputs in the retained span. It does not establish retention on arbitrary future
inputs. The decoder also uses a fixed harmonic construction. A small exact
semantic graft and saturated-span fork test can examine these boundaries
without duplicating that matrix-scale experiment.

Pinned primary sources:

- [E12 source](https://github.com/Moissanite-Labs/weft/blob/2a4cc936c6a197afc1a85f124e517f2ddfa07d66/docs/program/experiments/e12-plasmid-nullspace-graft-2026-11-12/e12_plasmid_grafting.py)
- [E12 report](https://github.com/Moissanite-Labs/weft/blob/2a4cc936c6a197afc1a85f124e517f2ddfa07d66/docs/program/experiments/e12-plasmid-nullspace-graft-2026-11-12/RESULTS-E12.md)
- [Issue #157](https://github.com/Moissanite-Labs/weft/issues/157)

The new worktree starts at PR #160 commit
`19a438691bb67e52d026ffed6bc4e8698e48c110`. Hardware facts from that pilot are
historical environment observations, not a new hardware benchmark. This audit
makes no GPU, shared-memory throughput or production Eido integration claim.
