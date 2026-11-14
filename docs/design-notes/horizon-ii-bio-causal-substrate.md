# Design Note: The Bio-Causal Analogy Reservoir (Horizon II)

Date: 2026-11-14
Phase: analogy inventory. Not architecture. Not adopted. Nothing here is a plan.
Related: `docs/design-notes/scwsp-directional-gate.md`, `docs/design-notes/horizon-ii-dual-plane-silicon.md`, `docs/design-notes/horizon-ii-verified-causal-substrate.md`, `docs/design-notes/horizon-ii-ideas-backlog.md`.
Source material: a pasted external session turn and one attached figure. The source names nobody and we remove no personal details. The figure is not committed. See Section 5.

## 1. Origin and recurrence

This is the fourth pitch arc in this track. The wrong-product invariant appeared again, in text ("K₀ΔW = 0" is used
for the steric wall) and in the attached figure's legend ("Steric Wall (K₀ΔW ≠ 0)"). The invariant is
`ΔW · K0ᵀ = 0`. Five appearances across the arc, now including pixels. Do not propagate it.

## 2. The pitch, as received, four pillars

1. **Fold topology over unconstrained RAM.** Separator between covalent backbone invariants and conformational
   degrees of freedom restricted to `Null(K0)`.
2. **Adaptation by local energy relaxation** over global backpropagation, equating equilibrium propagation with
   `σ(x)` local gradient descent.
3. **Allostery over symbolic routing.** Compact statistical ligands whose binding reshapes a cell's routing
   landscape on the far side.
4. **Chaperone boundaries and homeodynamic dissipation.** Budget depletion as metabolic current damping a runaway
   cell to its ground state `W0`.

Plus the unresolved question: what is the minimal set of primitive residues whose causal interactions are rich
enough to fold into higher-order reasoning?

## 3. What is honestly useful

1. **Levinthal is the point of the null space.** Folding works because constraint topology collapses an
   astronomical search into a funnel. That is the same argument for restricting adapters to `Null(K0)`: you are
   not adding a check to a free search. You are deleting the invalid states from the search. Any version of the
   II-B v2 gate that cannot state this argument clearly has not earned its silicon.
2. **Allostery gives the mesh a shape worth testing.** Two cells coupled by one compact rank-r spectral field,
   with admission still enforced by the gate at every entry point. It maps to the Horizon III cell-mesh research
   branch. It does not map to tokens and JSON. It is a boundary-coupling protocol, and it must be specified
   (energies, norms, reset) before it is anything else.
3. **Chaperones justify a reset law.** The control-theory claim worth testing: when a cell's adaptation rate or
   displacement exceeds a threshold, damp it back toward `W0`. The static pieces exist in text form already:
   `C2` owns a budget precondition (`budget >= cost > 0`). The tension bound at 85.0 exists in the tested C2 path
   (`weft/runtime/invariants/invariants.py`, `verify_tension_bound` with `TENSION_MAX = 85.0`, exercised by the
   `tension_vectors` in `vectors.json` and `test_tension_vectors` in `test_invariants.py`). The ledger's
   `TensionGovernor.sol` draft says the same thing but is not compiled in CI, so it is not the reference here.
   The plasm owns teardown. Building this claim means joining those three into one specified reset path and measuring
   it on the toy. Nothing more ambitious is earned yet.
4. **Equilibrium propagation is a legitimate toy substrate for the same gate.** Analog Hopfield or Ising settling
   is real research and fine to run behind a gate in toy cells. It is not a training method for production
   networks, and it is not what the word "causal physics" excuses.

## 4. What is not usable

1. **"Invariance becomes a conservation law."** No law conserves rank-r null-space structure in matter. Projection
   is computed arithmetic. We turn physical unavailability of states into a verified digital check. The metaphor is
   the teaching tool. The substance is LUTs and drift checks.
2. **"Adaptation via voltage coupling, zero software optimizer."** Equilibrium propagation requires clamped and
   free phases for credit assignment. Without them there is no learning. The claim conflates inference-time settling
   with weight adaptation, and it repeats a common mistake in neuromorphic prose.
3. **"ATP-backed dissipation makes stability automatic."** Thermodynamically open systems are not automatically
   homeostatic. In the digital substrate, damping must be designed as a feedback path (cap, measure, reset) and
   measured against fault injection, or it does not exist.
4. **"Formal verification stops bolting onto the outside."** Embedding the gate in the memory ordering path (II-B)
   approximates this better than any model-level trick can. It is still an admission check. It is not physics
   enforcing biology.
5. **"Twenty residues suffice, therefore forty gates do."** The minimal-residue question is a real research
   question and must stay open until a compiler exists for the substrate's region graph. None of the current
   corpus answers it.

## 5. The attached figure

Not committed, and this is now one series-wide decision rather than a one-off. The rule for figures in this track:
a figure is committed only when the owner explicitly asks for it, each committed figure carries a provenance line
(source, date, license status) in the note that references it, and no figure printing a false or banned invariant
lands at all. The #195 turn meets the rule: the owner asked for the figure, and that note and its asset carry
their provenance lines. This one does not: it was not requested for the repo, it is a third-party generative
artifact, and its legend prints the banned orientation `K₀ΔW ≠ 0`. If the owner wants it, the conversation to have
is the asset license and a redraw with `ΔW · K0ᵀ = 0` before anything lands.

## 6. Where the analogy legitimately flows further

- A Ramachandran-style allowed-regions figure for `Null(K0)` would communicate the constraint to a technical
  audience in a way no derivation matches. Draft it after II-B v2's predicate vectors exist.
- The funnel narrative is the conceptual test for whether the stacked II-B v2 gate earns silicon: does directed
  optimization within the allowed region beat spherical capacity bounds, measured in quality and stability?
  That is a substrate experiment, not a philosophy question.
- The minimal-residues open question belongs on the ideas backlog as a prompt, not as a plan. See
  `horizon-ii-ideas-backlog.md` for the gated inventory.

## 7. Status

Inventory and honesty audit. No code, no RTL, no figure, no issues filed, no path named, nothing adopted. The
execution sequence stays unchanged: harvest `K0` on a real checkpoint, close I.3, land II-B v2 simulation, then
return to this reservoir.

Depends on (unmerged at the time of writing): PRs #187, #188, #189 and #190. Merge order: #187 first, then #188,
#189 and #190, then this.
