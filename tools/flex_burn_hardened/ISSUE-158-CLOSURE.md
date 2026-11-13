# Closure Note for Issue #158 & PR #151 (`run_all_55_flex_burn_v2.py` Hardening)

Addresses the concrete peer-review findings recorded in [`Moissanite-Labs/weft#158`](https://github.com/Moissanite-Labs/weft/issues/158) and [`PR #151`](https://github.com/Moissanite-Labs/weft/pull/151):

1. **Removed Unsourced Model Row & Clarified Reservation vs. Settled Billing:** Removed the unused `gpt-5.6-sol` row from `MODEL_PRICING_STD_PER_MTOK`, grounded rates to [`https://developers.openai.com/api/docs/pricing`](https://developers.openai.com/api/docs/pricing), and documented pre-call token estimates (`len(raw)//3 + 96` + `max_output_tokens`) strictly as conservative per-call upper-bound holds reconciled against exact settled `usage` fields on `200 OK`.
2. **Explicit `SSL_CERT_FILE` Resolution:** Bound `ssl.create_default_context(cafile=...)` to honor `SSL_CERT_FILE` with automatic `/etc/ssl/cert.pem` host fallback on sandboxed macOS/POSIX hosts.
3. **Async Exception Isolation (`return_exceptions=True`):** Added `return_exceptions=True` to `asyncio.gather` so a single failing track never leaves sibling child processes orphaned or unwinds with raw unhandled tracebacks.
4. **Credential-Redacting Log Sanitizer (`redact_secrets_in_text`):** Added regex scrubbing for `sk-...` and `Bearer ...` patterns prior to log persistence so accidental child `stdout` key echoes cannot leak into `MASTER_SHA256SUMS` artifacts.
