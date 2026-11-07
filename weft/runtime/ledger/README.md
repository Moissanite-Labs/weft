# Weft Provenance & Metabolic Ledger Contracts (`weft/runtime/ledger`)

Codebase **C4** in [`docs/program/decomposition.md`](../../../docs/program/decomposition.md), implementing Interface **I5** (On-Chain Provenance and Excision ABI).

## Purpose and boundary

Hold the three-contract Solidity triad extracted from `weft/README.md` §15 and repaired per Issue #20 and Issue #30:

- `ProvenanceRegistry.sol`: registers baseline weight genotypes (`registerGenotype`), records cross-splicing edges (`recordCrossSplicing`) with cycle prevention and a strict 12-hop depth bound (`MAX_LINEAGE_DEPTH = 12`, fixing L6), and resolves root creator attribution (`verifyAttribution`, `getCreator`).
- `WeftTokenTissue.sol`: metabolic token contract with initial treasury minting plus governance-controlled `mintMetabolicAllocation` (fixing L3) and the 85% creator / 15% burn excision split (`executeExcisionValve`).
- `TensionGovernor.sol`: balancing court extracted from `weft/README.md` §15.2 (fixing L1), enforcing `MAX_SAFE_TENSION = 85` (`85.0%` tension threshold) and blocking reporting harnesses from self-adjudicating their own slash reports (`enforceIndependentAdjudicator`, fixing L4 and L5).

These contracts are tested offline via the reference simulator and ABI topic verifier in [`weft/runtime/gateway/`](../gateway/README.md) (`C5`) and are never deployed to live networks by CI.

## Verification

```bash
python3 -m unittest discover -s weft/runtime/gateway -p 'test_*.py'
```
