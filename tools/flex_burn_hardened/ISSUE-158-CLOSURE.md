# Closure Note for Issue #158 (`run_all_55_flex_burn_v2.py`)

This directory holds the hardened Flex orchestrator and this note. It records how the revision treats the findings in [`Moissanite-Labs/weft#158`](https://github.com/Moissanite-Labs/weft/issues/158) about `run_all_55_flex_burn.py`.

`--selftest` step 1 runs four sibling harness scripts from `--harnesses-dir` (default: this directory):

- `weft_111_flex_harness.py`
- `lean4_astra_proof_harness.py`
- `scry_abios_equal_compute_eval.py`
- `rigid_realizations_880_certifier.py`

Those scripts live outside this slice. When they are missing, `--selftest` prints the missing names and exits 1.

The orchestrator:

1. **Pricing.** Rates follow the public OpenAI pricing table, including cache-write (30-minute and 12-hour) and long-context (input above 272K tokens) columns. A model without a row is rejected; billing does not fall back to another model's rate.
2. **Reservation and settlement.** Prior spend is reloaded from `master_api_ledger.jsonl`, so a later process inherits the remaining cap. Settlement charges the computed table cost against the cap, including when that cost exceeds the reservation; the ledger entry records the overrun, and new reserves are refused once spent is at or above the cap. Transport errors and unparsable `200` responses persist the reserved hold to the ledger file, and a later process reloads it as spent. The reserved `max_output_tokens` is written onto the forwarded payload.
3. **Live spend gate.** A billed upstream call requires both `OPENAI_API_KEY` and `--confirm-live-spend`. Defaults are four concurrent tracks at `$53.50`.
4. **Child isolation.** `asyncio.gather(..., return_exceptions=True)` turns a failed track into exit code 1. The run `finally` kills child process groups. A selftest `Popen` that exceeds the 90s `communicate` timeout is terminated.
5. **Log sanitization.** `redact_secrets_in_text` runs on child output before the log is written and hashed into `MASTER_SHA256SUMS`.
6. **Proxy credential and token bounds.** A non-positive `max_output_tokens` is rejected. The loopback proxy has its own token; children receive that token, and the upstream handler uses the process `OPENAI_API_KEY`.
7. **TLS.** `ssl.create_default_context(cafile=...)` honors `SSL_CERT_FILE`, with a `/etc/ssl/cert.pem` fallback when that path exists.

[PR 151](https://github.com/Moissanite-Labs/weft/pull/151) reviews `supplied-harness.py.txt`. That file is outside this diff; the list above is the work on this orchestrator.
