# Weft Off-Chain Gateway & Ledger Simulator (`weft/runtime/gateway`)

Codebase **C5** in [`docs/program/decomposition.md`](../../../docs/program/decomposition.md), implementing Interface **I5** (On-Chain Provenance and Excision ABI) between the local runtime (`C1`, `C2`, `C6`) and the Solidity contract triad (`C4`).

## Purpose and boundary

Compute real Ethereum ABI event topic hashes via pure-Python Keccak-256, enforce localhost-only RPC bounds by default, read signing keys only from environment variables, and simulate the three-contract ledger triad offline.

- **Owns**:
  - `keccak256.py`: pure-Python Keccak-f[1600] (`0x01` padding) implementation verified against standard Ethereum test vectors (#20 L7).
  - `gateway.py`: `EVENT_TOPIC_HASHES`, `validate_rpc_endpoint` (localhost-only unless `allow_remote=True`), `load_gateway_private_key`, and `LedgerTriadSimulator`.
  - `test_gateway.py`: unit and conformance tests for `C4` and `C5`.
- **Dependencies**: `weft/runtime/invariants` (`C2`) and Python 3 standard library.

## Verification

```bash
python3 -m unittest discover -s weft/runtime/gateway -p 'test_*.py'
```
