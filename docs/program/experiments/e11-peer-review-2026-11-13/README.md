# Archived E11 reproducibility diagnostics

This research record reviews the published snapshot of PR #155 at `2b004a7cc0ba305f6a337c8bf2bb3c540d7d7aa3`. It preserves the exact supplied source/report, completed offline command checks, input-span arrays, projection-control inputs and results, and independent interpretation. It does not reproduce the reported evolutionary benchmark or modify the peer branch.

Both documented commands ran the same two unit tests and produced no evolutionary artifacts. The input-span diagnostic found four spatial harmonics at every tested size. The projection control retained the frozen rows and matched evaluator returns for the tested synthetic matrices. These findings concern reproducibility and evaluator coverage, without establishing how the reported runs were performed.

The work used Python and NumPy 2.5.4, with no model/API calls, evolution or replacement benchmark. REVIEW.md gives the pinned source citations and scientific limits. MANIFEST.json records every archived file's byte length and SHA-256. The supplied Python source is preserved as data under a `.py.txt` extension.

From this directory, the existing reproduction scripts can be run explicitly after reviewing their source:

```sh
python3 reproduce.py
python3 rank_control.py supplied-ic_morphogenesis.py.txt
```

The first command rewrites its diagnostic outputs. The second prints the projection diagnostic. Preserve the archived files when making comparisons. Derived Python caches are excluded from this record. This branch is an evidence archive, without a new pull request, formal-runtime certificate or closure claim for the peer's issues.
