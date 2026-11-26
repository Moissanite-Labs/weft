# Beyond tokens: inference where language is only an edge decoder

**Status:** proposed research direction (no in-repo experiments yet)  
**Date:** 2026-11-18  
**Evidence marking:** **[fact]** statements are tied to a cited source; everything else is **[interpretation]**.

---

## 1. Thesis

**[interpretation]** Push inference efficiency to its logical end: stop treating discrete tokens as the native currency of machine thought. Models should reason and coordinate in their own internal representations—weights, activations, key–value (KV) caches, and fixed-size concept vectors—and human language should appear only at the boundary, when a person must read or approve something.

That is stricter than:

- **Fewer tokens on the wire** (agent-tuned vocabularies, compact protocols such as SYM-2P), and
- **Less energy per token** (hardware that co-designs silicon with a fixed model shape, e.g. Exstill),

because it asks whether tokens can leave the *critical path inside and between models*, not merely cost less.

**[interpretation]** The program splits into two engineering boundaries:

1. **Model-to-model:** compatible latent or cache transport (the [nullmodem](https://github.com/Moissanite-Labs/nullmodem) half of the stack).
2. **Model-to-human:** a faithful, inspectable decoder from internal state to language (an open problem for arbitrary activations; partial solutions exist for sentence embeddings and mid-layer states).

---

## 2. How this ties to Moissanite Labs and Weft

Weft’s research question is whether adaptive “cells” can change within checkable bounds while agents and interfaces stay honest about what ran ([`Moissanite-Labs/weft@df4f9fa:README.md`](https://github.com/Moissanite-Labs/weft/blob/df4f9fa45640d7ee840f4529025a9a556d98684c/README.md)). This direction adds a transport hypothesis: **if specialist cells exchange meaning in a shared latent space, the membrane (C1 shared memory), the gate (C2), and the wire format (abios today; nullmodem tomorrow) must evolve together**—without abandoning auditability at the human edge.

| Piece | Repo (pinned main at authoring time) | What it does today | Role in the tokenless arc |
| --- | --- | --- | --- |
| **Compact agent messages** | [`abios@21154fd:SPEC.md`](https://github.com/Moissanite-Labs/abios/blob/21154fdc2fe925047560134fdedea5d0c073ca25/SPEC.md) | SYM-2P/1.0: one canonical JSON object per line, validated, fail-closed. **L-18 [fact]** explicitly forbids latent, embedding, or KV channels on the normative inter-agent surface. | Horizon 0 **typed text** baseline and audit spine. Anything below text must stay out of band or force a new protocol revision. |
| **Tokenizer economics** | [`tokenpage@bc105aa:CHARTER.md`](https://github.com/Moissanite-Labs/tokenpage/blob/bc105aa3430d4c5fadec6a07b7fc3d3cad6df1cd/CHARTER.md) | Measures how public vocabs waste tokens on agent traffic; experiments on open-weight models with changed vocabs. | Shrinks tokens while tokens remain; supplies benchmarks and falsifiers for “is vocabulary enough?” |
| **Below-text exchange** | [`nullmodem@53c981f:CHARTER.md`](https://github.com/Moissanite-Labs/nullmodem/blob/53c981f771babfbf96ae15bf72874cf2f1e836c8/CHARTER.md) | Requires measurable wins over English and abios on local open models; mandates an audit path back to human-readable form. | Primary home for latent/KV experiments; success criteria align with **E09** in Weft. |
| **Cellular runtime & gates** | [`weft@df4f9fa:weft/runtime/plasm`](https://github.com/Moissanite-Labs/weft/tree/df4f9fa45640d7ee840f4529025a9a556d98684c/weft/runtime/plasm), [`weft@df4f9fa:docs/interfaces/I4-shared-memory.md`](https://github.com/Moissanite-Labs/weft/blob/df4f9fa45640d7ee840f4529025a9a556d98684c/docs/interfaces/I4-shared-memory.md) | C1 shared-memory layout and C2 Frobenius gate—tested, not latent transport. | Future host for zero-copy exchange between cells on one machine; must not weaken C2 without evidence. |
| **Falsifier card** | [`weft@df4f9fa:docs/program/experiment-cards.md`](https://github.com/Moissanite-Labs/weft/blob/df4f9fa45640d7ee840f4529025a9a556d98684c/docs/program/experiment-cards.md) (E09) | Preregistered question: when is latent communication better than typed/text? | Experiment records belong in **weft-loom** under `experiments/E09/`; this doc only names the direction. |
| **Ecosystem map** | [`weft@df4f9fa:docs/mission.md`](https://github.com/Moissanite-Labs/weft/blob/df4f9fa45640d7ee840f4529025a9a556d98684c/docs/mission.md) | Places tokenpage, nullmodem, and abios on Horizon 0–I. | Shows tokenless transport as an extension of Horizon I, not a replacement for checkable messages at the human boundary. |

**[interpretation]** Weft does not implement nullmodem or tokenpage; it defines the invariants and evaluation discipline those repos must satisfy to merge into a single cellular fabric.

---

## 3. Prior work: synthesis (not a bibliography)

Each subsection states what the work **establishes**, what it **leaves open**, and which part of the owner’s vision it **supplies**.

### 3.1 Meta Large Concept Models (LCM) and SONAR

**Source (LCM):** [Large Concept Models: Language Modeling in a Sentence Representation Space](https://arxiv.org/abs/2412.08821), arXiv:2412.08821, 12 Dec 2024.  
**Source (SONAR):** [Sonar: Sentence-Level Multimodal and Language-Agnostic Representations](https://arxiv.org/abs/2308.11466), arXiv:2308.11466.

**What it proves [fact]:** LCM treats a *concept* (in the paper, one sentence) as one step in an autoregressive chain in **SONAR** embedding space, then decodes to text or speech with SONAR decoders. Training explored MSE regression, diffusion, and quantized SONAR at scales up to billions of parameters and trillions of tokens of training data. **SONAR [fact]** provides fixed-size multilingual sentence embeddings plus text/speech encoders and a text decoder for many languages.

**What it leaves open [fact]:** LCM still alternates **latent concept prediction** with **explicit SONAR decode** for human-observable output; it does not remove tokens inside a single transformer’s layer stack, nor does it specify agent-to-agent KV handoff. The paper notes that a representation space *optimized for reasoning* could differ from off-the-shelf SONAR.

**Supplies to the vision [interpretation]:** A worked example of **two-level generation**: fast motion in a continuous sentence space, language only at decode. That matches the owner’s **model-to-human boundary** when the latent unit is a vetted SONAR vector. It does **not** yet supply arbitrary activation interchange between arbitrary agents.

---

### 3.2 Coconut (Chain of Continuous Thought)

**Source:** [Training Large Language Models to Reason in a Continuous Latent Space](https://arxiv.org/abs/2412.06769), arXiv:2412.06769, submitted 9 Dec 2024.

**What it proves [fact]:** Coconut feeds the **last hidden state** back as the **next input embedding** instead of sampling a vocabulary token, switching between “language mode” and “latent mode.” Training uses a multi-stage curriculum that gradually replaces chain-of-thought tokens with latent steps while still supervising eventual text outputs. On some logical planning tasks it reports better accuracy–efficiency trade-offs than chain-of-thought, with latent states that can encode multiple successor hypotheses.

**What it leaves open [fact]:** Latent steps still live **inside one model**; supervision still flows through text losses; there is no cross-model protocol, no audit channel, and no claim that mid-stack states are interchangeable across checkpoints or architectures.

**Supplies to the vision [interpretation]:** Evidence that **intra-model** reasoning can shed *intermediate* tokens without shedding *all* tokens—final answers still surface in language. This is the closest published analogue to “think without emitting,” but it is **not** “tokens are gone between agents.”

---

### 3.3 Byte-level and tokenizer-free *input* models (ByT5, MegaByte, Byte Latent Transformer)

| Work | arXiv | What it proves [fact] | What it leaves open | Supplies [interpretation] |
| --- | --- | --- | --- | --- |
| **ByT5** | [2105.13626](https://arxiv.org/abs/2105.13626) | Standard Transformers on UTF-8 **bytes** (256-way vocab) can match parameter-matched mT5 on many tasks; stronger on noise and spelling-sensitive benchmarks. | Still autoregressive **byte/token predictions** at the output; longer sequences → higher FLOPs than subword models at equal parameter count. | Removes **fixed subword tokenizer** on input; does not remove discrete prediction steps. Supports **tokenpage**-style “change the vocabulary” but at the byte extreme. |
| **MegaByte** | [2305.07185](https://arxiv.org/abs/2305.07185) | Multiscale patches: global transformer over patch embeddings, local transformer over bytes inside a patch; models **million-byte** contexts with better compute scaling than flat byte LMs. | Patch boundaries are not semantic “concepts”; still byte-level likelihood training. | Shows **hierarchical latents** (patch states) as a compute unit—conceptually adjacent to “concepts” but trained for density modeling, not agent protocols. |
| **BLT** | [2412.09871](https://arxiv.org/abs/2412.09871) | **Entropy-based dynamic patches** as primary compute units; byte-level LM matches token LMs up to 8B params / multi-trillion-byte training with better FLOP-scaling at inference. | Patches are still derived from **bytes**, not free-form activations from another agent; no cross-system stitching. | Strongest **[fact]** claim that tokenizer-free **training at scale** is viable—undermines “you must have a SentencePiece table” without eliminating sequential predictions inside the model. |

**[interpretation]** Together these attack **tokenizer idiosyncrasy and vocabulary lock-in**, which is the problem `tokenpage` documents for agent JSON and SYM traffic. They do **not** attack **token-mediated agent dialogue**; output heads still emit discrete symbols.

---

### 3.4 Latent communication between models and agents

**DroidSpeak** — [KV Cache Sharing for Cross-LLM Communication and Multi-LLM Serving](https://arxiv.org/abs/2411.02820), arXiv:2411.02820.

**What it proves [fact]:** For **same-architecture** model pairs, prefix **KV caches** (and embeddings) can be reused across different fine-tunes with selective recomputation of a few layers, yielding large prefill speedups and throughput gains with small quality loss on tested tasks.

**Cache-to-Cache (C2C)** — [Cache-to-Cache: Direct Semantic Communication Between Large Language Models](https://arxiv.org/abs/2510.03215), arXiv:2510.03215.

**What it proves [fact]:** A learned projector can fuse a **source model’s KV cache** into a **target model’s** cache, with layer gating; reports accuracy gains over text-mediated multi-LLM pipelines and lower latency than generating intermediate text.

**KVComm (selective KV)** — [KVComm: Enabling Efficient LLM Communication through Selective KV Sharing](https://arxiv.org/abs/2510.03346), arXiv:2510.03346.  
**KVComm (multi-agent cache reuse)** — [KVComm: Online Cross-context KV-cache Communication for Efficient LLM-based Multi-agent Systems](https://arxiv.org/abs/2510.12872), arXiv:2510.12872.

**What they prove [fact]:** KV pairs carry enough semantics for **partial sharing** or **offset-corrected reuse** across agents that see different prompt prefixes; the 2025 online variant targets multi-agent prefill without re-encoding shared context.

**Relative representations & stitching** — [Relative representations enable zero-shot latent space communication](https://arxiv.org/abs/2209.15430), arXiv:2209.15430; **PARAM (2026)** — [Improving Relative Representations with Learned Anchors and Whitened Inner Products](https://arxiv.org/abs/2605.30596), arXiv:2605.30596; **MoSECroT** — [Model Stitching with Static Word Embeddings for Crosslingual Zero-shot Transfer](https://arxiv.org/abs/2401.04821), arXiv:2401.04821.

**What they prove [fact]:** Representing a state by similarities to **anchor points** can align independently trained encoders enough for **zero-shot module stitching** in some vision, graph, and language settings; PARAM reports stronger cross-architecture alignment among small LMs. MoSECroT shows the promise and limits of **embedding-layer swapping** for crosslingual transfer.

**What the cluster leaves open [interpretation]:** Most results assume **known model pairs**, **offline profiling**, or **learned projectors trained on paired data**; none provide a **normative, versioned agent protocol** with fail-closed validation like abios. **Cross-architecture** KV transfer remains fragile; **text is still the default fallback** in every system discussed.

**Supplies to the vision [interpretation]:** Direct evidence for the **nullmodem** charter questions (KV reuse, embeddings as messages, cross-model adapters). This is the empirical backbone for **model-to-model without natural-language serialization**, but only where compatibility is engineered and measured.

---

### 3.5 Decoders from internal states back to language (external-conversion boundary)

| Mechanism | Source | What it proves [fact] | Limits [fact] | Supplies [interpretation] |
| --- | --- | --- | --- | --- |
| **SONAR decoder** | arXiv:2308.11466 | Encoder–decoder MT and generation from **fixed sentence embeddings**. | Sentence-level bottleneck; not arbitrary layer activations. | Production-grade **edge decoder** for one chosen latent geometry (SONAR). |
| **Vec2Text** | [Text Embeddings Reveal (Almost) As Much As Text](https://arxiv.org/abs/2310.06816), arXiv:2310.06816 | Iterative correction can **invert embeddings** to text with high exact-match rates on short spans for some embedders. | Length-capped; embedder-specific; privacy warning that embeddings leak content. | Shows **audit reconstruction** is feasible for **sentence embeddings**—relevant to nullmodem’s “audit path,” with security implications. |
| **Logit lens** | Nostalgebraist, 2020 (blog); analyzed in arXiv:2303.08112 | Applying final **unembedding** to mid-layer states yields a **crude next-token distribution**. | Brittle; drift across layers (Belrose et al. report failures on several models). | Cheap **probe**, not a faithful decoder. |
| **Tuned lens** | [Eliciting Latent Predictions from Transformers with the Tuned Lens](https://arxiv.org/abs/2303.08112), arXiv:2303.08112 | Per-layer affine maps trained to match final-layer **KL** produce more reliable vocabulary projections from hidden states. | Still **vocabulary-anchored**, not guaranteed semantically complete; trained per model. | Engineering pattern for **inspectable shadows** of latent thought—usable for safety monitoring, not for user-facing paraphrase without further work. |
| **Scaling lens tooling (2026)** | [Interpreting Language Model Hidden States at Scale](https://arxiv.org/abs/2608.10260), arXiv:2608.10260 | Extends lens families to more component types at scale. | Research tooling; not an agent protocol. | Suggests the **probe layer** will keep improving for white-box audit. |

**[interpretation]** These works support the owner’s **second boundary**: humans can recover *some* language from *some* latents, but **faithful, policy-grade decoding of arbitrary cooperative activations** is not solved. That gap is where Weft’s insistence on **checkable evidence** matters: any production latent channel needs a defined decoder with measured faithfulness, not an informal logit lens screenshot.

---

### 3.6 Energy per token (context, not the end state)

**Exstill** — [Exstill: The Most Efficient Single-Chip Processor for the Next Token](https://arxiv.org/abs/2611.18859), arXiv:2611.18859, submitted 13 Nov 2026.

**What it proves [fact]:** Gate-level co-design of **fixed-shape** small models with on-die weights and KV can approach a computed **arithmetic energy floor** per **decoded token**, with large reported gaps versus general-purpose GPUs on multi-user serving.

**What it leaves open [fact]:** The unit of account remains **one generated token**; the report’s models are still autoregressive token emitters at the interface.

**Supplies to the vision [interpretation]:** Shows how far **token-centric** efficiency can go—useful for hybrid systems where an edge still speaks tokens to humans—but **[interpretation]** if internal agent traffic shed tokens, silicon budgets might shift from “next token” to “next latent step,” a different co-design target not covered by Exstill’s published claims.

---

### 3.7 What is novel in this direction (versus the literature)

**[interpretation]** Prior work typically:

- Removes or reshapes **tokenizers** but keeps **discrete outputs** (ByT5, BLT, MegaByte), or
- Runs **continuous thoughts inside one model** with text supervision (Coconut), or
- Communicates **caches/embeddings between models** without a constitutional, fail-closed **agent envelope** (DroidSpeak, C2C, KVComm), or
- Decodes **specific latent geometries** to text (SONAR, Vec2Text, tuned lens).

**Moissanite’s distinct claim** is the **composition**:

1. **Normative text for humans and persistence** (abios L-17, L-18 **[fact]**) coexists with
2. **Experimental sub-text transport** (nullmodem charter **[fact]**) gated by measured task accuracy and mandatory **reconstruction for audit**, and
3. **Cells and gates** (Weft C1/C2) that treat latent promotion like any other state change—bounded, logged, reversible where promised.

The literature supplies parts; none ties them into a **governed multi-agent cell fabric** with explicit falsifiers (E09) and tokenizer economics (tokenpage) on the same baseline tasks.

---

## 4. First experiments (4090-scale)

Records of runs belong in **weft-loom** (`experiments/E09/`). Hardware target: **one NVIDIA RTX 4090-class GPU**, 24 GB VRAM, local loopback only.

### E-A: Hidden-state handoff versus ABIOS text on a cooperative task

| | |
| --- | --- |
| **Hypothesis [interpretation]** | Two instances of the **same** small instruct model (e.g. 1–3B) complete a two-step pipeline (planner → executor) with lower bytes-on-wire and prefill FLOPs when the planner passes a **last-layer hidden state** (fixed shape) plus a typed checksum, versus the same content in minimal SYM-style JSON lines. |
| **Setup [interpretation]** | Pair on one GPU; shared tokenizer; tasks from a frozen JSONL fixture (counting, structured JSON edits). Latent arm: projector identity or single learned linear map trained only on held-out pairs. |
| **Baseline** | ABIOS-shaped compact JSON (or abios fixtures) serialized to UTF-8. |
| **Success [falsifiable]** | Latent arm ≥ **baseline accuracy − 2%** on task correctness, **≥ 30%** reduction in bytes transferred, **≥ 20%** prefill time reduction, measured at equal temperature and seeds. |
| **Failure refutes** | Latent arm misses accuracy bound **or** saves no bytes/FLOPs **or** requires per-checkpoint retuning to transfer. |

### E-B: KV prefix reuse across two fine-tunes (DroidSpeak-style)

| | |
| --- | --- |
| **Hypothesis [interpretation]** | Two LoRA adapters on the same base share **≥ 70%** of prefix KV layers on a fixed long system prompt with no Task F1 drop > 1 point. |
| **Setup** | Base 7B-class model if VRAM allows with 4-bit loading; else 3B. Profile which layers can be copied per DroidSpeak-style layer sweep. |
| **Baseline** | Full prefill on receiver. |
| **Success** | Measured TTFT and total prefill FLOPs reduction with quality within bound. |
| **Failure refutes** | No layer set meets reuse target without quality collapse on held-out prompts. |

### E-C: Faithful edge decode from cooperative hidden states

| | |
| --- | --- |
| **Hypothesis [interpretation]** | A small **tuned-lens-style** probe plus greedy continuation matches **reference text** BLEU ≥ 0.85 / exact structured fields ≥ 95% for a constrained output schema (JSON with ≤ 8 keys). |
| **Setup** | Fine-tune per-layer affine translators (arXiv:2303.08112 recipe) on 5k in-domain pairs; evaluate on held-out 1k. |
| **Baseline** | Model-generated text (no latent shortcut). |
| **Success** | Meets thresholds; human spot-check of 50 failures logged. |
| **Failure refutes** | Cannot meet field-accuracy bound → **human edge cannot rely on this decoder**; latent channel must remain debug-only. |

### E-D: Tokenpage counterfactual versus “no tokens between agents”

| | |
| --- | --- |
| **Hypothesis [interpretation]** | Agent-tuned vocabulary (tokenpage Track 1) reduces tokens **less** than latent handoff (E-A) on the **same** fixture, while latent pays a decode/audit tax documented in E-C. |
| **Setup** | Reuse tokenpage measurement scripts on frozen traffic; compare to E-A metrics. |
| **Baseline** | Stock tokenizer + ABIOS JSON. |
| **Success** | Publish a single table ranking **stock / agent vocab / latent** on accuracy, bytes, FLOPs, audit BLEU. |
| **Failure refutes** | Agent vocab beats latent on **all** resource metrics at equal accuracy → **tokenizer path suffices**; full token abolition deprioritized. |

---

## 5. Risks and open questions

**Interpretability [interpretation]:** Latent channels are opaque by default. Probes may track the model’s vocabulary bias (tuned lens) rather than intent. **Mitigation:** mandatory parallel **typed audit record** (abios) for human-boundary acts; probes for monitoring only until E-C thresholds pass.

**Safety [interpretation]:** Hidden states can carry **more recoverable information than intended** (arXiv:2310.06816 on embeddings). KV sharing may leak prompt prefixes across trust domains. **Mitigation:** treat latents like secrets; never cross tenant boundaries without encryption and explicit consent; fail closed like abios L-16.

**Training signal [interpretation]:** Coconut-style curricula need **text traces**; fully token-free training may lack dense supervision unless tasks supply external reward or paired decoders. **Open question:** can C1’s **A/B mitosis** select latent messenger policies without silent regression past C2 radius?

**Compatibility [fact from literature]:** Cross-model KV and stitching degrade under architecture mismatch. **Open question:** are **relative representations** (arXiv:2209.15430, arXiv:2605.30596) enough for a *versioned* nullmodem wire format?

**Governance [fact]:** abios L-18 forbids latent channels in SYM-2P/1.0. **[interpretation]** A tokenless stack requires a **new profile** with explicit decoding, hashing, and dispute semantics—not a silent bypass of L-18.

---

## 6. How we manifest it: staged roadmap

Stages are **gates**, not calendar dates. Each stage names **reuse**, **new build**, **gating experiments**, and **what would show the thesis wrong**.

### Stage 0 — Today (typed text, measured tokenizer cost)

| | |
| --- | --- |
| **Reuse [fact]** | abios validators and SYM-2P fixtures; tokenpage measurement charter; Weft C6 telemetry lines; E09 card text. |
| **Moissanite builds** | Nothing tokenless in production paths; nullmodem = survey + pilot scripts only. |
| **Gate** | tokenpage benchmark table on agent traffic exists and is rerunnable. |
| **Thesis wrong if** | Agent-tuned vocab achieves target byte/token cuts **without** latent work and accuracy holds—tokenizer optimization is sufficient. |

### Stage 1 — Cheaper tokens, same envelope (4090)

| | |
| --- | --- |
| **Reuse** | tokenpage open-weight experiments; abios packet shapes as semantic ground truth. |
| **Build** | tokenpage proposals (reserved protocol tokens, merges); optional SYM **vNext** draft in abios **without** breaking L-18 in 1.0. |
| **Gate** | E-D table: stock vs tuned vocab on frozen fixtures. |
| **Thesis wrong if** | No vocabulary change beats stock by charter thresholds (tokenpage success criteria). |

### Stage 2 — Same machine, below-text transport (4090)

| | |
| --- | --- |
| **Reuse** | nullmodem measurement discipline; DroidSpeak/KVComm recipes; Weft E09 bounds (512-d messages, 2 GiB tensor cap **[fact from card]**). |
| **Build** | nullmodem reference “latent line” format (versioned, hashed payload, no claim of semantic equivalence without projector ID); optional hook in exo harness (out of tree). |
| **Gate** | E-A and E-B pass; recorded in weft-loom. |
| **Thesis wrong if** | Latent/KV arms fail accuracy **or** save no resources vs compact text on **all** tasks in the fixture suite. |

### Stage 3 — Edge decoders and audit (4090 → small cluster)

| | |
| --- | --- |
| **Reuse** | tuned lens tooling; Vec2Text-style iterative decode for sentence-sized audit snapshots; SONAR decoder where concepts are sentence-level. |
| **Build** | nullmodem **audit manifest**: every latent exchange links to `decode_spec`, `faithfulness_bleu`, and optional human `relay` text; Weft C6 frame fields for decode job status (design only until implemented). |
| **Gate** | E-C thresholds; spot-check protocol documented. |
| **Thesis wrong if** | No decoder meets field-accuracy bounds at fixed compute—**humans cannot safely oversee** latent traffic; thesis retreats to SONAR-sentence or text-only production. |

### Stage 4 — Cells and shared memory (Apple Silicon / UMA first)

| | |
| --- | --- |
| **Reuse** | Weft C1 `StratifiedAppleSiliconPlasm`, I4 layout; C2 gate on any promoted messenger weights. |
| **Build** | Typed **Dialectic region** experiments (build program C1d **[interpretation]**): zero-copy latent slots with generation counters, separate from hippocampal recency buffer. |
| **Gate** | Two-process attach test (build program P2 for C1a) plus latent exchange without tearing shared memory. |
| **Thesis wrong if** | Gate rejects latent promotion as often as weight mitosis **or** shared memory offers no latency win vs loopback TCP on UMA. |

### Stage 5 — Cross-device nullmodem (post-4090)

| | |
| --- | --- |
| **Reuse** | abios English recovery ladder (L-17 **[fact]**); C8 handshake sketches from roadmap. |
| **Build** | exo-os profile: encrypted latent frames; relative-representation adapters (arXiv:2605.30596) between heterogeneous small models. |
| **Gate** | Federated E09 with consent gate #25; cross-version compatibility matrix. |
| **Thesis wrong if** | Cross-model latent traffic needs continual retraining per pair—**cost exceeds text** at operational scale. |

### Stage 6 — End state (owner vision)

| | |
| --- | --- |
| **Reuse** | Entire stack: cells (C1), gates (C2), checkable traces (C3/C6), human boundary (abios + relay). |
| **Build** | **Internal:** agents exchange projector-versioned latents/KV; **no tokenizer on hot path** between compatible cells. **External:** mandatory decoder to language (+ optional speech via SONAR) for any human or legal record. Silicon (Horizon II) optimizes **latent-step joules**, not token joules alone. |
| **Gate** | End-to-end demo: multi-agent task with zero inter-agent text, full audit decode, C2-bounded cell updates; negative result published if any stage fails. |
| **Thesis wrong if** | Any production task still requires inter-agent text for accuracy **or** audit decode cannot be bound **or** safety incidents trace to uninspectable latent side-channels. |

**[interpretation]** Stages 0–3 fit a single RTX 4090; Stage 4 prefers UMA; Stage 5+ needs federation and ops not yet in CI here.

---

## 7. Document control

| Field | Value |
| --- | --- |
| Kind | Research direction (program doc) |
| Experiments | Not run in this repository |
| Next action | File weft-loom E09 preregistration; open scoped issues for nullmodem wire sketch and tokenpage fixture hash |

---

## References (verified arXiv IDs and titles)

1. Hao et al., *Training Large Language Models to Reason in a Continuous Latent Space* — arXiv:2412.06769  
2. Schwenk et al. (LCM), *Large Concept Models: Language Modeling in a Sentence Representation Space* — arXiv:2412.08821  
3. Duquenne et al., *Sonar: Sentence-Level Multimodal and Language-Agnostic Representations* — arXiv:2308.11466  
4. Pagnoni et al., *Byte Latent Transformer: Patches Scale Better Than Tokens* — arXiv:2412.09871  
5. Yu et al., *MegaByte: Predicting Million-byte Sequences with Multiscale Transformers* — arXiv:2305.07185  
6. Xue et al., *ByT5: Towards a Token-Free Future with Pre-trained Byte-to-Byte Models* — arXiv:2105.13626  
7. Morris et al., *Text Embeddings Reveal (Almost) As Much As Text* — arXiv:2310.06816  
8. Belrose et al., *Eliciting Latent Predictions from Transformers with the Tuned Lens* — arXiv:2303.08112  
9. Moschella et al., *Relative representations enable zero-shot latent space communication* — arXiv:2209.15430  
10. PARAM authors, *Improving Relative Representations with Learned Anchors and Whitened Inner Products* — arXiv:2605.30596  
11. DroidSpeak, *KV Cache Sharing for Cross-LLM Communication and Multi-LLM Serving* — arXiv:2411.02820  
12. *Cache-to-Cache: Direct Semantic Communication Between Large Language Models* — arXiv:2510.03215  
13. *KVComm: Enabling Efficient LLM Communication through Selective KV Sharing* — arXiv:2510.03346  
14. *KVComm: Online Cross-context KV-cache Communication for Efficient LLM-based Multi-agent Systems* — arXiv:2510.12872  
15. MoSECroT, *Model Stitching with Static Word Embeddings for Crosslingual Zero-shot Transfer* — arXiv:2401.04821  
16. Manohararajah & Thangarasa, *Exstill: The Most Efficient Single-Chip Processor for the Next Token* — arXiv:2611.18859  
17. *Interpreting Language Model Hidden States at Scale* — arXiv:2608.10260  

Moissanite repository pins (main at authoring): abios `21154fd`, nullmodem `53c981f`, tokenpage `bc105aa`, weft `df4f9fa`.