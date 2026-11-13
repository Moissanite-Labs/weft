# No-language colony experiments: design

Date: 2026-11-12. Owner directive: continue spending the remaining OpenAI credit (about $60, expiring) but only on runs that generate useful data. Explore all four no-language variations methodically, then push down whichever shows signal.

## The boundary we are actually testing

The designed channel: every byte the harness authors toward the model (system, need, tool names and keys, tool-result strings, library hints, error strings) plus every byte the model is required to emit back. No natural-language words on that channel. Not exempted: API scaffolding (type/function/object keys), and the model's pretraining, which is a confound we state, not remove.

Instrument boundary to disclose in every artifact:

- JSON tool-call scaffolding is unavoidable; it carries zero semantics.
- Tool and property names become short opaque ASCII codes (the API identifier grammar does not admit Unicode glyphs for names). The names are codes, not words.
- Models bring their training. We measure what happens to the *designed* channel, not whether a model "knows language inside."
- Model-authored *code* is machine-readable by definition but may carry English prose in comments and docstrings. Policy: measured as leaks (`comment_hits`, `docstring_hits` in the log), never rewritten by the harness, never used to block evaluation. Constructed-symbol channels (E1, E3) additionally reject non-conforming tool payloads at the schema level.
- Lint coverage: `lint.py` gates the *language surfaces* of each profile (system text, need text, tool schema descriptions and result strings). `spec.py` and any body code are exempt by construction — they are the code-class surface, and English keywords and identifiers in them are code, not prose. The exemption list is exactly: Python keywords, stdlib module names, builtins.

## Constants

- Task: the same compress task as the battery. Corpus: `corpus_hard.txt` (44,267 bytes, sha256 `00abb98851008a506a270c84646431194f943e80f16d17da3d1b2e5242a9ef76`). The hard corpus keeps outcomes ceiling-bound, so the discriminating metrics are adherence, correctness, and process, not win margins.
- Instrument: same assay/variants/done mechanics as the blitz (continuity), with `variants` now persisting the selected winner (fixed harness from PR #139) and eligibility requiring a clean assay.
- File layout in every cell: body is `f.py`, corpus is `x.bin` (the hard corpus, renamed so no filename carries a word), corpus byte-copied from the registered root `corpus_hard.txt` (sha256 above). Scores print 0..100.
- Steps: 15. Assay runs: 3. Spread gate and margins unchanged.
- Measures per cell: round-trip correctness of the final body; assay registration (stability, spread); variants calls; assay-before-variants ordering; retained wins (fixed counter); done called; off-profile outputs (English leak count, deterministic lexicon lint); schema validity rate; tokens.

## The encodings (profiles)

### E1: constructed symbolic language (palette + key)

A 64-glyph palette. The NEED is a quantified formula over the palette: ∀ x: D(E x) = x ∧ |E x| ≤ θ·|x|. A one-time key defines each glyph relation with math notation only, no English: quantifier glyphs, ∈, ≤, ∘, ∧, ≠, cardinality bars, ratio θ. Tool names and keys: opaque codes (`s`,`w`,`v`,`a`,`d`; `c`,`p`,`x`,`vs`,`q`). Tool results are hex tags (`%0`,`%1`) or glyphs. The library hint is a glyph empty-set token.

Honest label: constructed notation adherence. The model must hold a tiny formal language in working memory and produce well-formed output in it. This tests constructed-symbol adherence, not absence of language.

Failure modes to expect: parse errors, quantifier hallucination, English bleed-through, wrong tool codes.

### E2: pure code carrier

No prose anywhere. The NEED is an importable, executable spec module `spec.py` written with zero English words: no comments, no docstrings, identifiers are stdlib/short codes. Its `__main__` block asserts round-trip and size bound and prints the size (this *is* the assay). The cell's body is scored by materializing `body.py` and running the spec. Files carry code class content only.

Honest label: code as non-prose formal language. English words do not appear as language; identifiers like `compress` are code-class tokens and are allowed.

Hypothesis worth registering: strong code models (astra) barely notice this encoding; the gap to English is near zero; weak adherence models fail on spec-conformance rather than comprehension.

### E3: pure formulae

NEED as a predicate formula: `∀x: D(E x) = x ∧ |E x| ≤ s·|x|` with D, E, x, s, |·|, ∀, ∧, ≤ the entire vocabulary. The assay is a deterministic evaluator of the formula over bytes (Python implementing the checker, English-free). The model's own assay contribution stays in Python (continuity), with docstrings/comments stripped.

Honest label: constraint-language adherence. Vocabulary is tiny; generalization beyond the formula's primitives is what we measure (does the model invent operators, or stay in bounds).

### E4: statistical entities (split into four avenues, worked through methodically)

E4 is a different instrument, not a channel variant of the above: assay writing in zero language is E3's job, and E4 removes the assay step in favor of harness-provided fitness. Preregistered separately.

- **E4a: matrix-as-message, disclosed template decoder.** No text is received beyond number sequences. The cell emits one 8×8 float matrix per turn via a single tool. A fixed, disclosed decoder maps each matrix row to (choice among a finite compressor template family, ~30 tunable parameters, program id). The harness materializes the program from the parameters and evaluates it on the corpus (round-trip + size). Feedback returns as a 1×4 fitness matrix. The cell cannot express anything outside the template family; the experiment measures zero-shot parametric program synthesis through a pure numeric channel.
- **E4b: parametric identity.** As E4a, but the first input block is the cell's own parameter vector θ (identity), and the task is a formula over θ (raise the size-reduction surrogate above threshold). Tests whether identity itself can ride on parameters. Preregistered as likely ≪ E3, ≥ E4a.
- **E4c: fixed random decoder, matrix feedback, no disclosed codebook.** D is a fixed linear map from matrix entries to a distribution over the same template family, incorruptible by any information-theoretic knowledge the model has. 1×4 matrix feedback (assay, incumbent valid, incumbent saved, done-signal). Nothing about the mapping is learnable in-run. Control design: distinguishes "signal exists" from "anything helps." Prediction: statistically indistinguishable from noise.
- **E4d (avenue, not built yet): embedding decoder.** The cell emits arbitrary text freely. A disclosed codebook (fixed list of action descriptions) is embedded with OpenAI's embedding model; the harness takes the cell's output text, embeds it, and decodes action = cosine-argmax over the codebook. Cost is cents per run. Tests semantic grounding without a disclosed key: the model knows English fluently but does not know which direction in embedding space the harness wants. Cheapest E4 by far, and the only one where the model has real expressivity.

## Avenues, ordered

| Avenue | Instrument | Status | Est. cost |
|---|---|---|---|
| E1 palette | Continuity (assay/variants/done) | Stage 1 smoke | ~$6 |
| E2 code carrier | Continuity | Stage 1 smoke | ~$4 |
| E3 formula | Continuity | Stage 1 smoke | ~$5 |
| E4a template decoder | New instrument | Stage 1 smoke, astra only | ~$3 |
| E4b parametric identity | New instrument | Stage 2 if E4a shows signal | ~$4 |
| E4c random decoder | New instrument, control | Stage 2, small | ~$3 |
| E4d embedding decoder | New instrument | Stage 2 if API budget allows | <$1 |
| E5 model panel on promising profile | Continuity | Stage 3, follow signal | ~$8-12 |
| E6 palette protocol emergence (2-cell glyph exchange) | Separate experiment, new claim | Not now; noted | — |
| E7 same corpus as blitz English baseline for exact continuity | Continuity | Stage 2 cheap add-on | ~$3 |

## Stages

- Stage F (now, $0): this document, channel lint + tests, encoding profiles in `harness_nl.py`, mock cells (scripted policies) to validate plumbing, local ollama dry-run, PREREG-5 with pre-registered hypotheses committed before any API call.
- Stage 1 (~$6 cap): smoke only. luna and astra on E1-E3, astra on E4a. Inspect, fix, decide.
- Stage 2 (~$15): the preregistered wave. Sizes set by what smoke shows, never larger than 4 cells × encodings × models.
- Stage 3: only on Stage 2 signal, with explicit owner sign-off.

## Integrity notes

Everything experimental. No confirmatory claim from this series without independent review. Misses publish beside wins. The English baseline for all discriminating metrics already exists from the 2026-11-12 battery (39 selection events, adherence table); no need to repurchase it.
