# Runtime and budget review

**Do not use the supplied harness for a paid run in its current form.** Offline checks reproduce false codec verification, writes outside the workspace, and settlements above the configured budget. The original attachment is unchanged. Its passing mock selftest is recorded in `selftest.log`. it does not exercise these failure modes.

The findings below refer to `supplied-harness.py.txt`. `reproduce.py` and `reproduction.json` provide the local evidence. No API requests were sent, and the examples use synthetic files and payloads.

1. **[P1] A stateful one-byte codec passes the lossless check: lines 500–513.** Encoding and decoding share one module instance. An encoder that caches its input and emits one byte passes both the main payload and edge checks when the decoder returns that cache. `stateful_one_byte_false_positive` demonstrates success on two different payloads.

   `fresh_decoder_recovered` shows that a fresh decoder cannot reconstruct them. Decode in a separate process that receives only the compressed artifact and has no encoder state or original payload.

2. **[P1] Untrusted stdout can fabricate verifier success: lines 493–495 and 563–570.** A codec can access the driver's original payload during import, print a forged result containing its correct hash, and exit. The parent accepts the result without encoding or decoding. `forged_verifier` records accepted `ok: true` and a fabricated ratio of 999999.

   Keep measurements and success decisions in a trusted parent. treat codec stdout as untrusted diagnostics.

3. **[P1] The subprocess boundary is not a security sandbox: lines 530–560 and 578–588.** Environment filtering, Python `-I` and a working directory do not restrict filesystem access, network access or child processes. `filesystem_escape` and `outside_write_succeeded` demonstrate reading and writing synthetic files outside the workspace.

   Use an actual filesystem, network and process sandbox with resource limits and descendant cleanup before executing live generated code.

4. **[P1] Estimated input reservation cannot enforce a hard USD cap: lines 169–185 and 819–824.** Reservation uses `4500 + 1500 × turn`, rather than an upper bound on the actual billed context. In `input_underestimate`, a $0.06 cap permits a $0.0475 reservation followed by a $0.125 settlement.

   Bound the full request and conversation input before dispatch, reserve the permitted output cost, and stop when no conservative bound is available. Settlement after an overrun does not prevent it.

5. **[P1] Standard-tier fallback is not covered by its Flex reservation: lines 686–692 and 819–846.** The transport changes the request to `auto` without increasing the reservation. `fallback_tier` settles $0.095 against a $0.0475 reservation under a $0.06 cap. Disable fallback or reserve its maximum allowed cost first.

   The [official Flex guide](https://developers.openai.com/api/docs/guides/flex-processing.md) distinguishes uncharged resource-unavailable responses from fallback processing at standard cost.

6. **[P1] Ambiguous retries can duplicate work without preserving unresolved spend: lines 714–725 and 844–846.** The transport repeats POSTs after timeouts and URL errors, then releases the reservation if no response is returned. Only returned usage is settled. `ambiguous_retry` records six mocked attempts: three Flex and three `auto`.

   This is not equivalent to the specifically uncharged resource-unavailable 429 case described in the [official Flex guide](https://developers.openai.com/api/docs/guides/flex-processing.md). Stop or reconcile unknown-completion requests, retain their reserved exposure, and record every attempt and unresolved charge before further spending.

7. **[P2] Cache writes are omitted from the cost model: lines 120–147 and 195–207.** The ledger accounts for ordinary input, cached reads and output, but has no cache-write category. `cache_write_accounting` records a synthetic 1,000-token write as $0.0100 rather than $0.0125 at the declared standard rate.

   The [official prompt-caching guide](https://developers.openai.com/api/docs/guides/prompt-caching.md) states that cache writes cost 1.25 times ordinary input. Account for recognized write usage and the applicable tier explicitly. missing or ambiguous usage should prevent an exact-cost claim.

The dollar figures above are deterministic ledger examples using the review's declared rates. They are not an invoice or a claim about actual charged usage. These failures are sufficient to reject the hard-cap and safe-execution claims without a paid replacement experiment. Scientific protocol and statistical issues are covered separately in `REVIEW.md`.
