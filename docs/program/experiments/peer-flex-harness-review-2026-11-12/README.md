# Supplied Flex harness: offline review evidence

This package records an offline review of the user-supplied Issue #111 telemetry harness. It is separate from the Astra family-teacher experiments and the geometry diagnostic. The supplied code is preserved verbatim as `supplied-harness.py.txt`, a data attachment without automatic execution.

Original SHA-256:

```text
bc8f51d24fd5f6f1b310328222f4e7f313bfbbb2ecac735681573a6defd66ac3
```

The original attachment was inspected before execution. No actual API-key values were found. key placeholders and generic budget amounts in its documentation are preserved. Those amounts are source claims, not an account balance.

The local protocol is to test narrow failure modes without credentials, real API traffic, production data or generated model code. The reproduction imports the reviewed attachment, mocks `urlopen` before invoking transport, suppresses retry sleeps and executes only fixed benign snippets against synthetic files in a temporary directory.

The snippets demonstrate filesystem escape using a synthetic sentinel immediately outside a workspace. Temporary files are removed when the test exits.

Run with standard Python. no external packages are required:

```sh
env -i PATH=/usr/local/bin:/usr/bin:/bin python3 reproduce.py > reproduction.json
```

An explicitly selected reviewed attachment can be used with:

```sh
env -i PATH=/usr/local/bin:/usr/bin:/bin python3 reproduce.py --supplied-file ./supplied-harness.py.txt
```

The script uses `SourceFileLoader` to import the `.txt` attachment only when explicitly run. Do not point it at an unreviewed file: importing Python executes its top-level code.

`reproduction.json` records input-reservation and tier-fallback overruns, missing cache-write accounting, mocked ambiguous retries, synthetic filesystem escape, forged verifier stdout, and the same-process one-byte codec false positive. Assertions make the reproduction fail if its expected observations change.

The cache-write comparison uses the review's declared $12.50 per million standard-input-write rate. this local probe does not independently verify pricing or an invoice.

`selftest.log` records the attachment's built-in offline mock selftest, run after inspecting that path. It passed with no API key. Its output directory prefix is replaced with `<scratch-selftest>` to avoid publishing an unnecessary machine path. The untouched original log remains in the private scratch evidence. Passing that mock selftest does not address the reproduced verifier, isolation or ledger failures.

To reproduce that selftest manually after reviewing the supplied attachment:

```sh
env -i PATH=/usr/local/bin:/usr/bin:/bin python3 supplied-harness.py.txt --selftest --output-dir ./scratch-selftest
```

No paid run was attempted because the local checks already invalidate the claimed hard financial cap and the codec-verification boundary. This package records review evidence. it does not repair or endorse the supplied harness. See `REVIEW.md` for the independent review and actionable findings.
