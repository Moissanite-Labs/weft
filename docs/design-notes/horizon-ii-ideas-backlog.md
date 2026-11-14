# Design Note: The Hardware Track Ideas Backlog

Date: 2026-11-14
Phase: research inventory only. Nothing in this note is adopted. Nothing here authorizes execution, code, RTL, or a new codebase.
Related: `docs/design-notes/scwsp-directional-gate.md`, `docs/design-notes/horizon-ii-dual-plane-silicon.md`, `docs/design-notes/horizon-ii-verified-causal-substrate.md`. `docs/roadmap.md` Horizon II, `docs/program/decomposition.md`, Milestone I.3.
Scope note: capture of the hardware pitch arc. All personal and situational details are excluded by design.

## 1. Purpose

The hardware-track turns produced more ideas than any one note carries. This file is the inventory: each idea, its
soundness status, and the gate an execution decision would have to clear. The list of runnable work is intentionally
empty. Execution gets chosen together later.

## 2. Canonical invariant

`ΔW · K0ᵀ = 0`, with `ΔW` of shape d_out x d_in and `K0` of shape N x d_in (preserved keys as rows). The column-major
AlphaEdit equivalent is `ΔW P = ΔW`, `P = I - K K⁺`, with `K` the d_in x N key matrix. The pasted turns printed
`K0 ΔW = 0` repeatedly. Never carry that symbol forward. When a document
in this track wants the predicate, it means the annihilator of the preserved key directions.

## 3. Inventory

| # | Idea | Status | Execution gate |
| :- | :--- | :--- | :--- |
| 1 | Projection predicate beside the Frobenius ball in the admission gate | Sound concept. unmeasured | K0 from a trained checkpoint. projection vectors in `vectors.json`. Verilog sim of II-B v2 |
| 2 | Stage II-B v2: stacked predicate in the bus admission path | Sound concept | I.3 closed. digital-only predicate. simulated gate must pass all vectors bit-exactly |
| 3 | Subspace MMU: controller admission of weight writes by linear algebra | Real as an idea. speculative as hardware | A synthesized admission core in simulation proving the projection check on bursts, with stated latency |
| 4 | Dual-plane macro: static dense plane plus digital low-rank fabric | Plausible research | Simulation study vs dense-digital baseline. measure energy per adapter write, area, and error rate |
| 5 | Analog crossbar study as energy comparison point | Comparison point only | Cannot carry bit-exact conformance. any adoption decision requires an exact digital check beside it |
| 6 | Async spatial dataflow cells over NoC | Horizon III track, not Terrafab | Per-cell gate enforcement, bounded queues, attribution routing via lineage DAG. multi-year research |
| 7 | Proof-carrying admission: packet carries a certificate the gate verifies | Sound pattern. unmeasured | I.3 proofs. certificate format. experiment on one packet class. retire if over two times gate latency |
| 8 | I.3 Lean mechanization, extended to the projection predicate | Required foundation | Milestone completion. vectors agree between Lean and C11 |
| 9 | Compositional assume/guarantee mesh constraint | Publishable constraint | Written hypotheses (per-cell gate, bounded queues, no analog drift). applied in the III cell-mesh branch |
| 10 | Trait-level mode slicing and semantic tags on low-rank packets | Catalogue-profile feature | Belongs to the ethos catalogue profile track. text space. selective import rule needed first |
| 11 | Capacity planning for `Null(K0)` across tenants, including mode recycling | Open research | K0 harvest methodology. coverage evaluation on the workload. tenant model |
| 12 | KV-cache replacement with static low-rank factors | Strongest claim in the brief, with no measurement | Measured latency and bandwidth on the target checkpoint before any external claim |
| 13 | Sub-10 ms cold starts via tiered storage of composite packets | Systems idea. no numbers | A break-even study with measured cache misses per tier. nothing assumed |
| 14 | Publication-grade numbers for the SC-WSP brief if the track revives | Not actionable today | I.3. K0 harvest. one measured table (quality, size, load time, weave curve) |
| 15 | Functional watermark surviving QR and downstream weaves | Open tooling gap (no such tool exists) | A watermark-survival experiment (no `verify_watermark` tool exists yet) at `eps=1e-3`. measured survival after two weave rounds |
| 16 | Mechanized confluence of IC rewrite rules (Lean) | Not in I.3 scope | I.3 is scoped to the C2 predicates (roadmap §3). IC confluence is the next verification-branch item in decomposition.md. Schedule it separately, not smuggled into I.3 |

## 4. Deliberately excluded

- Any third party, pitch strategy, review process, or external audience framing.
- The SC-WSP brief document as an artifact. It stays shelved until re-measured.
- Analog CIM as anything beyond an energy comparison point, given the bit-exact posture of C2.
- Any claim of verified intelligence, end-to-end verified models, or abolition of train vs serve.
- Vendor-specific silicon critiques. The Terrafab line is ours to argue internally, not to target a supplier.

## 5. Execution discipline

1. Nothing executes before the K0 harvest study and I.3 land.
2. No new codebases or paths are created by this note. Execution starts from a filed issue naming the path.
3. Every item above is measured or retired. Nothing graduates by enthusiasm or repetition.
4. The ball stays beside the projection predicate, always. No gate is removed on the strength of a paper read. New
   gates are adopted only after they beat the ball in simulation, and the ball is never retired on this track.

## 6. Status

Inventory only. The three source notes are in review as PRs #187, #188 and #189 and carry the full audits. This
note indexes them and adds no audit of its own. Rows 10 to 15 carry ideas from the capture turns with no
dedicated source note of their own. They are inventory here, not endorsements. Depends on (unmerged): #187, #188,
#189. It merges when those merge or when the owner rules.
