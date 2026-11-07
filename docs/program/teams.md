# Cross-team boundary, ownership, interfaces, and review

Status: **proposal**, for Discussion #11 and PR #12. It sits alongside PROGRAM.md's Orchestration section and does not replace it: PROGRAM.md says who plays which role; this file says which team owns which code and what crossing a boundary requires.

## 1. Teams and ownership

Ownership follows the codebases in [`decomposition.md`](decomposition.md). A team owns a codebase's code, tests, README, technical document, and the interface specs it produces.

| Team | Owns | Produces interfaces | Consumes |
|---|---|---|---|
| **Substrate** | C1 plasm, C2 invariants, C3 ic | I3 (gate), I4 (shm layout), I5 (IC serialization), I7 (weight commitments) | I1 (host telemetry) |
| **Surface** | C6 telemetry, C7 aywa (Pages site, widgets) | I1 (frame), I2 (SYM-2P) | — |
| **Ledger** | C4 ledger, C5 gateway; Phase 5 governance research notes | I6 (ABI/events) | I3, I5, I7 |
| **Corpus** | `docs/corpus/`, `docs/whitepapers/`, mission, glossary, roadmap, wiki, the `weft/*.md` corpus itself | — | everything (documents are checked against code) |

PROGRAM.md roles map onto this as follows:
- `grk-smith` authors code PRs for any team, once an issue exists.
- `grk-proof` gives independent review of code and mixed PRs.
- `grk-axiom` is consulted on formulas in C2, C3, and the white papers.
- `grk-helix` is consulted whenever a biological name is attached to a mechanism.
- `grk-lumen` owns C7's visual design.
- `qalam` owns Corpus-team substance.
- The conductor sequences the work.

The parallel agents named in #9 and #11 (a Cursor cloud agent, a Codex agent, and Claude Code sessions) take team work through the same rules.

## 2. The boundary rule

**No change crosses a team boundary without review and acceptance by the team on the other side.** Concretely:

1. A PR that edits files owned by another team needs an approving review from someone acting for that team.
2. A PR that changes an interface spec (`docs/interfaces/*`) or its conformance vectors needs approval from the producer team *and* every consumer team listed in the table above.
3. A codebase never imports another codebase's internals. It uses the interface (a file format, ABI, or published function) and runs the interface's vectors in its own tests.
4. Corpus documents that describe a codebase are reviewed by that codebase's owner team for accuracy. Code PRs that change described behaviour must update the document or open an issue saying it is stale.

## 3. What counts as review

A review counts only if all of the following hold:

- **The reviewer is not the author.** For agent-authored work, that means a different session or account from the one that wrote the change (PROGRAM.md: `grk-proof` from the other GitHub account).
- **The reviewer ran the PR's stated verification commands**, or CI ran them, and the result is quoted in the review.
- **The reviewer checked the change against its issue's falsifier** ("what would prove this wrong"), not only against the description.
- **The review records a decision:** accept, request changes, or contest (§4). A comment without a decision does not count.

Docs-only PRs follow PROGRAM.md: they are opened for visibility, qalam owns substance, and they do not wait on independent code review. One exception: a docs PR that changes an interface spec is treated as code for the purposes of §2.2.

**No change merges on assertion alone.** A PR with no runnable verification, no document it can be checked against, and no recorded decision does not merge.

## 4. Disagreements

When two sides disagree:

1. Record the disagreement as an issue labelled `contested`. It gives both positions, the evidence each relies on, and **a test or measurement that would decide it**.
2. The status quo holds until the deciding test exists and has been run. Nothing is merged "pending agreement".
3. The stronger case on evidence wins. The decision and its reasons go in the decision log (`docs/wiki/decisions/`). The losing position stays in the issue so the branch is not lost; it can be reopened by new evidence.
4. If no test can decide the question (values, naming, scope), the owner decides. PROGRAM.md names Alkindus for live-deploy and visibility decisions. The decision is recorded with its reasons.

The contradictions already found in the corpus (`docs/corpus/claims-register.md`, status `OPEN`) are handled the same way. They stay open until evidence resolves them.

## 5. Claiming work in a multi-agent repository

Other agents work in this repository in parallel. Before editing a path:

1. Check open PRs and recent branches for that path.
2. Comment on, or assign yourself to, the issue that names the path.
3. If another agent already holds the path, take complementary uncovered work instead of overwriting.

Every PR names its issue, scope, rationale, and verification.

## 6. Provenance

Every idea and every line of code should be traceable:

- **Code** extracted from the corpus cites the source `file:line` range and says whether it was copied, repaired, or re-implemented (as `weft/runtime/ledger/README.md` already does).
- **Documents** cite corpus locations for each claim they adopt.
- **Decisions** cite the issue and evidence.

This is what lets the codebases move later into separate repositories, under separate licenses and governance, without losing their history.
