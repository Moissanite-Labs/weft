# Design Note: Constitutional Governance vs. On-Chain Contract Enforcement

Date: 2026-11-08
Phase: `PROGRAM.md` Phase 3 Deliverable (`W5`)
Related Codebases: **C4** (`weft/runtime/ledger/`) and **C5** (`weft/runtime/gateway/`)

## 1. The Structural Tension in the Raw Corpus

The `weft/` governance corpus (`weft/govern.md`, `weft/ethos.md`, `weft/whitepaper.md`, and `weft/README.md` §15) articulates a constitutional vision designed to prevent authoritarian capture, oligarchic compute monopoly, and rogue autonomous loops:
1. **Human Sovereignty & Dual-Signature Consent**: Critical parameter changes, cross-host migrations, and slashing actions require multi-party human and independent-witness verification.
2. **Anti-Oligarchic Homeostasis**: Economic and governance weight decays with concentration (`gini_index`) so no single actor can buy permanent control of the weave.
3. **Unforgeable Creator Provenance**: The 85/15 metabolic excision valve routes value automatically to root lineage creators across arbitrary splicing depth.

However, the initial Solidity drafts pasted into `weft/README.md` §15 and `weft/more.md` fell short of those constitutional guarantees in five specific ways (tracked and repaired in Issue #20 and PR #33):

| ID | Constitutional Requirement (`govern.md` / `ethos.md`) | Raw Transcript Draft Defect (`README.md` / `more.md`) | Repaired Implementation in `weft/runtime/ledger/` & Phase 5 Roadmap |
| :--- | :--- | :--- | :--- |
| **L1/L3** | Metabolic token supply must circulate between active harnesses and creators. | `more.md` omitted initial minting (`totalSupply == 0`), locking every transfer and excision call permanently. | `WeftTokenTissue.sol` mints initial treasury supply in the constructor and exposes governance-guarded `mintMetabolicAllocation`. |
| **L4** | No single key may unilaterally control the court or rewrite harness permissions. | `onlyWeaver` checked a single EOA (`msg.sender == technicalWeaverCore`) with no timelock or multi-witness threshold. | `TensionGovernor.sol` separates the reporting harness from the adjudicator (`enforceIndependentAdjudicator = true`), and Horizon III binds `technicalWeaverCore` to a threshold multisig + timelock contract. |
| **L5** | Accusers cannot judge their own slashing claims (no self-dealing bounty). | `adjudicateTensionDispute` allowed `reportingHarness` to receive the `500 WEFT` slash even when `reportingHarness == technicalWeaverCore`. | `TensionGovernor.sol` enforces `require(msg.sender != dispute.reportingHarness, "ASL_ERROR: REPORTER_CANNOT_SELF_ADJUDICATE")` when `enforceIndependentAdjudicator` is active. |
| **L6** | Lineage attribution must never drop out or loop infinitely. | `recordCrossSplicing` did not check for cycles or enforce the 12-hop ceiling at registration time, allowing a 13th hop to silently return `address(0)` in `getCreator`. | `ProvenanceRegistry.sol` walks the ancestor chain inside `recordCrossSplicing`, rejecting both cycles (`LINEAGE_CYCLE_DETECTED`) and chains exceeding `MAX_LINEAGE_DEPTH = 12`. |
| **L7** | Off-chain gateways must verify authentic ABI event topics. | `monitor_excision.py` in `more.md` checked a hand-typed prefix `0x8f3e...` that does not match `keccak256("CapitalExcision(address,address,uint256,bytes32)")`. | `weft/runtime/gateway/keccak256.py` computes the exact Ethereum Keccak-256 topic digest (`0x90d2...`) verified against standard Ethereum vectors in `test_gateway.py`. |

## 2. Non-Negotiable Safety Boundaries (Phase 5 Governance Rules)

Per `PROGRAM.md` Phase 5 and `docs/corpus/safety-index.md`, the following boundaries govern all current and future implementations:

1. **Invariants Cannot Be Loosened by Runtime Dials**: Corpus passages that metaphorically describe "dissolving safety gates at 180 degrees" (`G5`) are treated strictly as out-of-scope literary metaphor. In code (`C2`: `weft/runtime/invariants/`), `R_INVARIANT`, finiteness checks, and positive budget preconditions are hard invariants that no aesthetic or runtime dial can disable.
2. **No Unconsented Autonomous Weight Evacuation (`Exo-Mitosis`, Issue #25)**: Cells do not migrate weights across network boundaries on their own when thermal or budget thresholds trip. Cross-host replication (`C8`) remains a non-goal unless explicitly initiated and signed by a human operator over an authenticated channel.
3. **Distinction Between Style Priors, Predictive Models, and Personhood**: A documented policy or aesthetic prior left by a human contributor is an engineering specification (`ProvenanceRegistry`), never a biological claim of consciousness or post-mortal survival (`PROGRAM.md` Phase 4b).
