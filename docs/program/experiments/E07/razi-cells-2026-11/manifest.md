# Manifest: E07 razi-cells run, 2026-11

Exploratory run. Not preregistered. Numbers come from logged runs listed in data/.

## Files

Classes follow the weft recording contract: measured (raw output of a logged run), derived (computed or converted from measured data), fixture (input given to a run), code (source that produced the runs), notes (human-written text).
This manifest itself is not hashed (it would be self-referential).

| File | sha256 | Size (bytes) | Class |
|---|---|---|---|
| code/cell.py | ef2d16ee8d3191fa2a01d7c1ad0ff63e8d92da1940fd8353e5dc8025c7fb9eb6 | 23773 | code |
| code/colony.py | 0b676368946cbb4baab5b81b1be75717c670ef7fd2d3acf128d5dda8de0c5035 | 5428 | code |
| code/embed.py | d5903a48a8c90b1bfbbafeec7be2e4630269a0b991203f67c2994abb9b20d87c | 4699 | code |
| code/heldout_audit.py | b0849e79df0301b0ebbcb885ffbf3071a4c50f0e4bfc7d9a67179cbfee8d5fc3 | 31453 | code |
| code/perm.py | 25207b5b03ab136fc1673f1ff7d3f93337d54526bb1d357c990abf7ea5905e24 | 1202 | code |
| data/IDEAS.md | 0261fc11d31beafed1cd85fb7758c3e8fd489c2b4c8638664cd32d31a8455c79 | 7811 | notes |
| data/TESTS.md | a9a726d00278a90c141f6d8cf938b1062e4dcdd242d521cb1e665320e43a691d | 6363 | notes |
| data/b10-summary.json | 671ced251f6bdede6b0942cd5453239e4e6be20c61ffbef6b1d5524453532487 | 3622 | measured |
| data/b11-summary.json | b158a9ef46af8e2c44340cf08ac5c1055d85fd6eb60eab90bebb11ffd6ee3c15 | 3742 | measured |
| data/b5-summary.json | 8f40ec2e6e6c376af278549d9d9a0d436f736cbf4d2dcbd2c085b2717a24c718 | 3771 | measured |
| data/b6-summary.json | 9f73ef8dde9688c21300004d00a8bd6ad808917e5689713e337ce709cc1723ce | 3467 | measured |
| data/b7-summary.json | 6ae03e218f025139d791247c11514ff304ae7ddd00035526c4898832dd7de1e3 | 3330 | measured |
| data/b8-summary.json | 7f2b1bbe37bf331a14202eb85a97da0b0920d6ddd310001c4ce240390f95029f | 3609 | measured |
| data/b9-summary.json | 8093da8c5044121485a7b4587fdf494145d380ca2a413e075f78ac7442694cba | 3679 | measured |
| data/g3-summary.json | 21cf907eb830c836fe183370fe8d6d929564e7773fa8cd3602e73eb386aefedb | 3113 | measured |
| data/g4-summary.json | e2a3f633e1be257c1a91dd76af0af0b0f28efd69c6a7bfda1cef0b4228a2d283 | 3050 | measured |
| data/heldout-audit-r1.json | f090ad461fdd84052f740f41346ed41fe9d761967bfec85e1d983265fe121a5a | 30548 | measured |
| data/needs8v3.json | 55f7ae5ee14ae8e6d4dd1806747f04d5b4c018e7611b038dfecc21aec4b30f8f | 1788 | fixture |
| report.md | 9c0f2836c6632d5fdf81fd145c1a7ba5eabde944cc6dc5113a0279c398171e26 | 41054 | derived |
| convergence.md | 0d9e93010b1fac28db11feef81c827767cd5988559861c63ed26afaef60fba02 | 9375 | notes |
| corpus-findings.md | 32a13285451c54c2460729eaa227059783928f147fd9f8e6dabf125ffe8676fa | 11652 | notes |
| heldout-audit-r1.md | 82be4bea3a19b9d7e8d09a9fe855918d66bd8a289c2af6100696ecb03eb5f8ca | 7693 | derived |

Class notes:
- data/*-summary.json: per-run summary files run summaries (calls, improvements, wall time, per-cell results) for runs g3, g4, b5 to b11). measured.
- data/needs8v3.json: the 8 written NEEDs (coding tasks) given to the cells. fixture.
- data/TESTS.md, data/IDEAS.md: planning notes (test list, idea list). notes.
- report.md: Markdown conversion of the HTML report (Report 1, version 2). derived. Tables and text are unchanged apart from the sanitizing listed below.
- convergence.md: Report 2, where razi-cells and Weft converged and split. notes.
- corpus-findings.md: Report 3, corpus ideas not in the Weft code, verification of scout citations, and the protocol for the remaining experiments. notes.
- code/heldout_audit.py: Self-contained R1 held-out audit harness scoring finished cell directories against 8 deterministic reference tasks under benchmark lock. code.
- data/heldout-audit-r1.json: Machine-readable audit scores across 5 interleaved repeats for runs b5 to b11, g3, and g4. measured.
- heldout-audit-r1.md: Report on the R1 held-out audit, comparing headline improvements against held-out artifact performance. derived.
- code/*.py: cell.py, colony.py, perm.py, embed.py. cell.py, perm.py and embed.py are as used by the runs. colony.py was patched after the runs (2026-11-10) to count `splits` from `try` events, which cell.py logs, instead of `mitosis`, which it never logged. The data/ summaries are unchanged. code.
- Not included: run folders g1, g2, g3smoke and b6-failed-400, and any raw per-cell logs.

## Environment

- Machine: Apple M1 Max (sysctl machdep.cpu.brand_string on the run host), 8 performance + 2 efficiency cores, 64 GB RAM.
- OS: macOS 27.0.1 (build 26A434), from `sw_vers` at assembly time.
- Python: 3.14.7 (the exo-live virtualenv interpreter).
- Models were served through the Exo router.
- Cost per call was not logged. No dollar figures exist for these runs.

## Sanitize log

- Absolute home path prefix: 0 occurrences found in the copied files. Nothing to replace.
- Secret pattern scan (sk dash prefix, Bearer, api_key, token=, OPENCODE, ghp_, github_pat) and the owner account name over the whole folder: 1 hit, `code/embed.py` line 42, the string `"Bearer " + _openai_key()` building an HTTP header. It contains no secret value (the key is read at run time from the Exo router credentials, in process only). Reviewed as a false positive and left unchanged so the code stays runnable.
- No hits for the other patterns. The word "token" appears in report.md only as an LLM-token concept (line 244).
- Em dashes (U+2014) and en dashes (U+2013) in report.md and manifest.md: 0 found, 0 replaced.
- report.md line 3 contains "Exo canary seat ([redacted])". The `[redacted]` is already in the source HTML.
- data/IDEAS.md: the machine name "M1 Pro" was corrected to "M1 Max" (1 occurrence), matching sysctl. report.md had the same fix at lines 9 and 165.
- Conversion check: every word and number token in the HTML body text appears in report.md (token-multiset comparison, 0 missing). The only additions are Markdown list numbering.
