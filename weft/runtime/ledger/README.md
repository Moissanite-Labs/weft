# Ledger contracts (extracted corpus)

Solidity sources extracted from `weft/README.md`. **Not deployed** by this repository.

Use environment placeholders for deployment (see `weft/deploymap.md` for policy — never commit keys or RPC secrets):

- `WEFT_GOVERNOR_ADDRESS` — constructor arg for `WeftTokenTissue`
- `WEFT_RPC_URL` — RPC endpoint when a harness chooses to deploy
- `WEFT_DEPLOYER_PRIVATE_KEY` — must remain outside the repo (CI secret only, if ever used)
