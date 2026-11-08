# Security policy

## Reporting a vulnerability

Please **do not open a public issue** for security problems.

Report privately through GitHub: **Security → Report a vulnerability** on
[Moissanite-Labs/weft](https://github.com/Moissanite-Labs/weft/security/advisories/new).
If you cannot use GitHub, email **security@w3ft.org**.

Include what you found, how to reproduce it, and what an attacker could do with it.
We aim to acknowledge reports within 3 working days and to agree on a disclosure
date with you. We are happy to credit you in the advisory.

## Scope

In scope:

- Code in `weft/runtime/`, `scripts/` and `site/`.
- The w3ft.org website and its deploy configuration (`wrangler.jsonc`, `.github/workflows/`).
- Ways the safety predicates in `weft/runtime/invariants` can be bypassed by an input
  the tests do not cover. These count as security bugs here, not just correctness bugs.

Out of scope:

- The design corpus under `weft/*.md` and `weft/design/`. It is a preserved record of
  design conversations and contains example code that was never meant to run as is.
  Problems in it are welcome as ordinary issues.
- The Solidity drafts in `weft/runtime/ledger/`. They are research drafts that are not
  deployed anywhere, so please report findings as ordinary issues.

## Things to know

- Weft has **no token and nothing deployed on any blockchain**. Anyone claiming
  otherwise is not us. Please report impersonation to security@w3ft.org.
- Nothing in this repository needs real keys. The gateway reads signing keys only from
  environment variables and refuses non-localhost RPC endpoints unless told otherwise.
  Never commit keys or tokens, including test ones.
