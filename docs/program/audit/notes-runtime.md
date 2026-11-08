# Runtime full-read audit

Snapshot: `a721b12579caba4e04dc31b16731cc2657079207`. Reader: runtime partition. Completed: all 42 assigned files fully read; hashes, assignment coverage and evidence bounds validated. No audited-source edits.

## Checkpoint 1: C2 / I3

All seven invariant files read completely. The valuable kernel is a small, portable gate with finite budget preconditions and saved-baseline distance. This can be developed now on CPU/M1 and compiled C; it is neither a sandbox nor a proof of semantic alignment.

The actual policies remain inconsistent: Python default radius120 versus C/vector10; generic Python checks flattened length while torch checks shape; C mutates rejected budgets while Python returns a diagnostic deficit; C uses double accumulation rounded to float; Python integers cannot overflow but C multiplication can. Current passing tests duplicate C cases instead of executing the JSON corpus. Preserve these as explicit choices under #42 and evaluate a common conformance suite before adding Rust/Wasm/Metal consumers.

Phase gate: settle I3 numeric/input/state semantics; drive Python/C with identical cases; require budget and weights unchanged on rejected operations under whichever versioned state contract is adopted; test boundary rounding, NaN/Inf, wrong shapes and uint64 overflow. A Frobenius-distance acceptance test must never be described as behavioral safety without a separate empirical claim and falsifier.

## Checkpoint 2: C3 / I5

All five IC files read completely. The useful kernel is a compact, inspectable reducer with a deterministic graph snapshot and graph-bound trace digest. It is not yet a compiler/runtime for general applications, a proof-carrying execution engine or a demonstrated confluent implementation. BCP is a graph snapshot rather than a full continuation checkpoint: it omits allocator history, reductions, trace and initial snapshot.

Near-term repair under #43: decoder must preserve capacity (current count+16 floor changes serialized bytes), validate metadata before resource allocation, and reductions must either commit atomically or preserve prior state on exhaustion. VLV must have an explicit finite budget/cost contract. A deeper semantic issue is that ports store peer-node IDs without peer-port identity; multi-edges cannot be rewired unambiguously by first-match lookup. `interact` also does not verify an active principal pair. These must be settled before claiming Lafont confluence or adding GPU parallel scheduling.

Phases: canonical graph format and malformed-input rejection → transactional valid-net reducer plus reference oracle → deterministic scheduler and replay validation → source-language/compiler experiment → measured Wasm/GPU backends. Pure, labeled and metabolic calculi need independent claims and falsifiers. SHA-256 graph inclusion is useful tamper evidence, not evidence that the logged computation followed valid rules.

## Checkpoint 3: C1 / I4 / I7

All four Plasm files read completely. The present system is a useful small tensor laboratory: two exact candidate matrices, explicit target error, bounded baseline drift, frozen-row plasticity, trigger-response retention and clean owning-process teardown. Its meaningful next step is a trustworthy experiment harness, not scaling hardware. The matrix experiment is tiny relative to the reported64GB machine.

Current limitations needing distinct work: arena creation unlinks any existing same-name segment; attached clients also unlink by default; no sequence lock or coherent multi-field snapshot; copied tensor path rather than shared GPU tensors; no cell process isolation or OS quotas; one static seeded hippocampal summary; target generated from nearby weights; synthetic drift-derived tension and abstract budget; global RNG perturbations not reproducibly seeded; candidate metrics reported even when no commit occurred; zero generations fails via history indexing.

Phase gates: I4 byte contract(PR47) → explicit state/metric/seed/ownership behavior → reproducible CPU/MPS matrix benchmark → isolated speculative child processes with cancellation, quotas and teardown → real model adapter experiment with separate task/retention/novelty baselines. A watermark/provenance hypothesis must distinguish retention under mask-preserving updates from attribution under adversarial copying or seed disclosure. A frozen weight row is not proof that a human policy or identity is preserved.

## Checkpoint 4: C4 / C5 ledger and gateway

All nine ledger/gateway files read completely. This is an optional accounting/provenance research branch, not a prerequisite for present web or matrix tooling. The triad has real Solidity source, a useful local simulator seed, and real Ethereum Keccak topic generation. It has no Solidity compile/EVM verification yet; the named compile test searches for a pragma string.

#44 must make conformance concrete: shared action traces against locally compiled contracts, comparing events, balances, supply, disputes, lineage and rollback. Python floor15%burn/remaindercreator disagrees with Solidity floor85%creator/remainderburn on dust. Solidity unchecked multiplication can overflow. Float tension85.01 is not an ABI uint value and needs declared fixed-point units. Python rejects after mutating dispute flags; EVM reverts. Simulator accepts nonfinite/negative tension and negative allocations outside Solidity domain.

Attribution requires decisions: anyone can register a derived hash and shadow inherited getCreator; anyone can record lineage; single-parent mapping cannot represent general recombination; token excision trusts supplied creator; registry verifyAttribution with zero claimant can report true for unregistered hash. Commitment storage proves neither ownership nor watermark validity. The governor has one privileged key, can disable reporter separation and can swap contracts/mint; constitutional human+agent dual-signature, appeal, consent and succession are not executable.

Phases: local build and parity → domain/authority/rounding contract → adversarial property tests and threat model → opt-in signed local gateway adapter → separate institutional/legal/economic research. No deployment follows from a successful simulation. Distinguish cryptographic hash, legal provenance, adversarial attribution and measured resource usage.

## Checkpoint 5: C6, wrappers and verification

All remaining17 files read completely; runtime assignment42/42 fully read. C6 has useful small codecs and honest top-level fixture/unavailable labels, but field provenance is still mixed: live GitHub rows reuse fixed or estimated commit/PR counts, one page only, static time and sequence, silent fallback. Host code similarly substitutes load0.5/0.0 under a measured source label when individual probes fail. Thermal data is explicitly an estimate; should never be treated as a sensor.

I1 packs16float32 fields; epoch seconds in float32 have coarse precision. I2 hashes payload only, leaving header/sequence outside integrity coverage, and parsing is permissive rather than a strict canonical language. The telemetry vectors file is not consumed by its tests. #45 should establish measured/derived/fixture/unavailable per field, units, observation windows, freshness, pagination completeness, error reporting and shared Python/JS conformance.

Core and Mac files are wrappers around C1/C3/C6. The Mac wrapper currently echoes dim/radius/budget arguments without forwarding them: its report can claim radius10,budget20 while C1 uses120,100. This is a bounded high-value reporting fix once assigned an issue. CPU/Linux success does not verify Darwin, MPS, actual Chrome-on-Mac, real sensors or deployed site. CI is a strong starting point but currently unpinned dependencies and no real EVM compiler. The master corpus selftest checks fences/AST, not semantic comprehension or runnable extracted code.

## Reproductions performed in this audit

Linux Python3.12 environment `/workspace/.venvs/weft-audit/bin/python`, pinned source a721b12. No source runtime changes.

- BCP capacity2 with one CON serializes, decodes as capacity17, and reserializes to different bytes.
- CON/DUP on capacity4 raises MemoryError after growing active nodes2→4; graph differs from before call.
- VLV with positive infinite metabolic_budget returns VLV_PASS.

These falsify current full-state-roundtrip/transactional-resource implications. Tests were narrow reproductions; no new broad verification claim.

## Recommended execution sequence

1. Finish I4/telemetry worker PR47/46 review. Keep source audit/variant maps under review separately.
2. #43 repair canonical decode and transactional failure; explicit finite cost domain. #42 settle language-independent gate semantics and drive shared vectors. These can run in parallel with #45 truthful telemetry.
3. Correct C1 committed-result reporting, reproducible configuration and shared-memory ownership before claims about cells. Record CPU/MPS environment separately.
4. Establish valid graph topology, reference reducer, scheduler and replay checks; only then compiler/Wasm/GPU experiments.
5. Compile C4 locally, execute #44 parity, resolve attribution/rounding/role decisions; keep ledger optional to native/web stack.
6. Introduce actual model adapters, process isolation, resource caps, persistence and cross-process synchronization; benchmark task quality, latency and measured resource use independently.
7. Bare-metal gates, custom silicon and institutional governance remain separate research prototypes with hardware/formal/consent gates, not runtime completion inferred from metaphors.

## Follow-on review

Independently reviewed C3 repair `a9b798bd6254f1e4ef8d344b9ad183a9fcc0be73` after the pinned-source audit. Verdict ACCEPT for its bounded storage/failure scope; full evidence is in [review-ic.md](review-ic.md). This later branch does not retroactively change the pinned source findings. C1 runtime reporting/lifecycle findings are tracked by issue #51; C3 topology/reference semantics by issue #52.
