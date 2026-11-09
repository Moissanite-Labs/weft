# Weft build program

> **Historical charter.** This is the original Weft build program, written while the repository was private
> (it lived at the repository root as `PROGRAM.md`). On 2026-11-08 the owner asked for the repository to be prepared
> for public release. Preparation is not publication: changing visibility, public posts and outreach remain owner
> decisions, tracked in [#64](https://github.com/Moissanite-Labs/weft/issues/64) and
> [#57](https://github.com/Moissanite-Labs/weft/issues/57). The engineering constraints still apply: evidence before
> claims, nothing deployed live without the owner, and scaffolding only what an issue names. For current
> sequencing see the [build program](build-program.md) and [convergence plan](convergence-plan.md). Contributor-facing
> rules are in [CONTRIBUTING.md](../../CONTRIBUTING.md).

Weft is the final-form architecture for Moissanite Labs. This program turns the restored design corpus into issues, repaired software, and internal documents. All of that work stays inside this repository.

For the current proposed sequence following Discussion #11 and the 2026-11-08 owner follow-up, see [the convergence plan](convergence-plan.md), [use-now guide](use-now.md), and [variant register](variants.md) (#39). They distinguish six tracks, present evidence, hardware/resource gates, and implementation lineages. The phase lists below preserve the original program; their historical status is not evidence that a task is still pending or that a later capability is complete.

The complete source review (#49) extends this into a [component-by-component phased build program](build-program.md), [experiment portfolio](experiment-cards.md), [file evidence ledger](audit/README.md) and [persistent handoff](resume.md). Use those for current sequencing while preserving this original charter and source lineage.

The other repositories remain bridges while hardware and society catch up. This program does not dissolve them, replace them, or apply Weft to them immediately. An organization around Weft may come later. It is not part of this phase.

No public posts, outreach, marketing copy, benchmark write-ups, or Zenodo records are part of this program until that restriction is lifted. (2026-11-09: the owner lifted it for Zenodo records of the software and Papers 0–2, once the repository is public. See [Releasing](releasing.md).) Do not file Weft material into any other repository. This repository is the single source of truth.

## Workstreams

1. Evaluation and repair. Criticisms and fixes from the markdown corpus, the mathematical review, the biological review, and the governance review become issues and pull requests in this repository. Those three reviews were delivered by teammates and are not yet files or issues here. Filing them into this repository is part of the program.

2. Code extraction. Design notes imply several pieces of software. Start from code that already exists, then open an issue before scaffolding any path that does not yet exist.

3. Internal documents. White papers, technical notes, a mission statement, and design notes are written in-tree under `docs/` so they can be reviewed like any other change. Prefer new internal docs under `docs/`. Do not use the GitHub Wiki: wiki edits would bypass pull requests.

4. Program control. This file, placed at the repository root, and a charter issue are the living plan. A one-line pointer in the root README should point here. Sequencing and handoffs are run as an operational board, separate from the conversational design work.

## Existing seeds

These paths already contain code and are the starting points for extraction:

- `weft/runtime/core`: `weft_plasm.py`, `weft_ic_vm.py`, and `selftest.py`
- `weft/runtime/aywa`: `weft_daemon.py`, `github_harvester.py`, `dashboard_layout.wgsl`, `index.html`, and telemetry files
- `weft/browser-sources/widgets`: kinetic typography, mind-palace spatial memory, morphogenetic bioelectric field, neural cellular automata, and the interaction-combinator net (each as `.html` and `.jsx`)

Treat the neural-cellular-automata and combinator widgets, plus the Aywa `index.html` and the mind-palace widget, as existing seeds for those lines. Ledger contracts and a Darwin/Mac harness appear in the markdown corpus (for example `mac.md`) and have not been seen as code paths. Those wait for a filed issue, then a scaffold. Do not pre-create those trees.

## Sequencing

Phase 0. Publish this program file and a charter issue once a posting path is clear.

Phase 1. File the first repair issues. The safety check should measure distance from a saved baseline, not the difference of two sizes. The provenance mark that later updates can move or overwrite needs a stated threat model.

A/B convergence should be an explicit requirement. Models should be treated as cells rather than as whole organisms. That is an engineering contract (isolation, speculative lineages, teardown, and feedback) and the vision language we keep.

The cellular names describe behavior we aim to replicate and ideals to iterate toward, including when current technology has not yet made the parallel exact. They are not a claim that the present code already is cellular biology.

Phase 2. Scaffold only a path named by a filed issue. Product decisions are made as the need arises. The first scaffold should serve the baseline-relative safety-distance repair, likely by extending `weft/runtime/core/selftest.py` rather than adding a new tree. Tests should encode the repaired formulas, not the weaker substitutes.

Phase 3. Write the internal documents: mission, architecture, and a design note on the gap between the stated constitution (human approval, dual signature) and the example contracts (a single privileged address). This phase can run in parallel with Phase 2 once Phase 1 issues exist. The constitution-versus-contract note does not depend on the first code repair.

Phase 4. File the remaining mathematical repairs as issues, then open code pull requests only where the finding is executable: the missing budget precondition, a precise description of the interaction-combinator variant, an execution record that actually includes the graph, selection that scores the update it commits, handshake length, and a real watermark threat model.

Phase 4b. File the biological review into this repository, then file naming and evidence issues, in parallel with Phase 4. This phase must not gate the first code repair or the Phase 1 models-as-cells engineering issue.

Those issues keep sandbox isolation, speculative A/B, teardown, feedback control, protecting the core while varying the periphery, and local growth or repair.

Keep the biological names. Membrane, mitosis, apoptosis, homeostasis, Hebbian, and related terms stay as the language of the vision. They define behavior we aim to replicate, establish the mission, and serve as branding and world-building.

Exact parallels may not have been reached yet, or not yet enabled by current technology. The names are ideals to iterate toward. Do not drop or rename them because the current code is thinner than the metaphor. A sense of wonder and whimsy is part of how this work is approached.

This follows the direction in https://github.com/Moissanite-Labs/weft/issues/6#issuecomment-6712451917 That comment does not itself name those terms. Keeping them is how this program applies that direction to the earlier instruction to drop or rename them.

The current hippocampal novelty lattice is implemented as a recency buffer scored by mean distance. The current sympathetic ring is implemented as telemetry. Keep those names as the ideals those implementations iterate toward. Do not rename them away from the vision language just because the present code is simpler.

Resource quotas as selection pressure are in scope. Do not equate unlimited resources with cancer. Genotype versus phenotype is an evolutionary-computation metaphor. The NCA evidence bar is persistency and damage metrics in the style of the Distill 2020 paper, not the hand-coded widget. `design/bio.md` stays labeled as an analogy.

Consciousness, will-preservation as survival of a person, and post-mortal intent are out of scope as biological claims.

Keep three things separate: a testamentary policy or style prior a living person chooses to leave (consent and a spec, not biology), a model that predicts that person's choices (testable while they are alive), and survival of the person or of experience. Do not treat software idle as organismal death, and do not treat an on-chain hash as immortality.

Phase 5. File the governance review into this repository, then file research issues: dual-signature checks on the executable path, which safety checks a loosening dial cannot touch, the trusted computing base, and consent, appeal, and succession. These are research notes in this repository. They are not a rewrite of live team policy and not a request to run privileged hardware code.

## Orchestration

- qalam owns vision and program substance, turns intent into briefs and document quality, and files the charter issue, this file's pull request, and later issues when a posting path is clear.
- Grokism (the conductor) owns division of labor, sequencing, checkpoints, and handoffs, and verifies artifacts. The conductor makes no GitHub writes.
- grk-axiom reviews formulas and proof claims, and is consulted on related repairs.
- grk-helix reviews biological mappings and is consulted when a design uses a biological name for an engineering mechanism. Do not re-dispatch that review. File the delivered review into this repository.
- grk-warden keeps team rules and the GitHub account roster current. Weft governance findings stay in this repository unless a separate request changes live team policy.
- grk-herald does not receive Weft material while public posting is deferred.
- Amalga, Sreb, and Mithrax do not file Weft material into the public intake pipeline. Weft-relevant items become issues here. Do not wake them about this program until this file exists in the repository.
- grk-smith authors code changes once issues exist.
- grk-proof gives independent review of code pull requests, and of mixed code-and-docs pull requests, from the other GitHub account.
- Docs-only pull requests (this file and `docs/*`) are opened for visibility. qalam owns their substance and quality. They should not wait on independent code review.
- grk-scout checks for an existing library before we write a new one, not before we extend an existing seed.
- grk-lumen owns visual design when a browser-dashboard or widget issue is opened, so implementation does not invent the UI.
- grk-ship is out of scope unless Alkindus later asks to deploy. Do not deploy anything live. GitHub Pages is currently off. If it is ever enabled, a merge that publishes Pages is a live deploy. Independent review comes first, then ship merges after that review plus Alkindus's own approval.
- Weft items go through the conductor, not also through digest.

This is a code repository. It does not inherit a docs-only review rule for the whole tree. Code pull requests and mixed pull requests follow the ordinary code-repository rules.

## First checkpoints

0. A posting path is clear: the assigned posting account is restored, or Alkindus authorizes a specific batch.
1. The charter issue and this root program file are in the repository.
2. The four Phase 1 repair issues are open, with models-as-cells written as an engineering contract and as vision language we keep.
3. Scaffold only the path named by the first code-repair issue.
4. The first code repair lands: distance from a stored baseline, with tests. Axiom is consulted. Independent review is required.
5. The internal constitution-versus-contract design note is in `docs/`. This can proceed in parallel with checkpoints 3 and 4.

Later, and not gates on checkpoint 4: remaining mathematical-repair issues (Phase 4), naming and evidence issues (Phase 4b), governance research issues (Phase 5), and the biological review filed back into this repository.

## Constraints

Keep every deliverable in this repository. Do not route work outward. Do not treat a simulated receipt, a conversation dashboard, or a claim of installation as evidence that software is running or sealed on a chain.

Distinguish a stated rule from a rule that the executable path actually checks. Distinguish an implemented behavior from a biological name that names the ideal we iterate toward. Keep the name. Do not claim the implementation has arrived until the evidence is there.

Distinguish a style prior someone chose to leave, a model that predicts their choices, and any claim that a person or their experience survives. Do not deploy anything live. Do not pre-scaffold implied codebases. Scaffold when a filed issue names the path.
