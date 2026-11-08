# Contributing to ML Weft

Thanks for your interest. Weft is early research, and the most valuable contributions make a claim testable or show
that one is wrong. A failing test that exposes a gap is a welcome pull request.

By taking part you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to help

- **Repairs with tests.** Fix a formula, predicate or codec, and add the test that would have caught the problem.
- **Conformance.** Extend the shared vectors (for example `weft/runtime/invariants/vectors.json`) so Python, C11 and
  JavaScript are held to the same behaviour.
- **Falsifiers.** Write an experiment that could refute a claim in the [claims register](docs/corpus/claims-register.md),
  run it, and record the result, including a negative one.
- **Documentation.** Tighten wording, correct a status, or add the missing plain-language description of a vision term.
- **The website** (`site/`). Fix accessibility, performance or accuracy problems.

Open issues are a good place to start. Comment on one before starting larger work so effort isn't duplicated.

## Ground rules for evidence

These rules matter more here than style does:

1. **A stated rule is not a checked rule.** If a doc says the system enforces something, link to the test that checks
   the executable path. Otherwise, say it is not enforced yet.
2. **Narration is not evidence.** The design corpus describes commands running and contracts deploying. None of that
   counts as proof. Evidence is a test in CI, or a recorded run with its commit, environment and output.
3. **Keep the vision names, don't overclaim.** *Cell, membrane, mitosis, homeostasis* and the other biological terms
   stay. They name what the design aims for. Never write that the code *is* the thing the name describes unless the
   evidence is there. Please don't open PRs that only rename these terms.
4. **Tests encode the repaired formula,** not a weaker substitute that happens to pass.
5. **Nothing live.** Tests and scripts must not deploy contracts, move weights between hosts, or touch privileged
   hardware interfaces. They must not need real keys or network access beyond installing packages.
6. **Scaffold only what an issue names.** Open an issue before you create a new top-level directory or component.

## Where things live

- **The design corpus** is in [Moissanite-Labs/weft-corpus](https://github.com/Moissanite-Labs/weft-corpus). It is a
  verbatim, read-only archive. Put corrections, analysis and repairs here instead, in `docs/` (for example
  `docs/corpus/` or `docs/design-notes/`) or in code under `weft/runtime/`, and cite the source by path and line,
  such as `weft/mac.md:50-100`. `scripts/corpus_audit.py` keeps the evidence ledger tied to the commit the corpus was
  read at.
- **The design language** (Eido) is in [Moissanite-Labs/weft-eido](https://github.com/Moissanite-Labs/weft-eido).
  `site/assets/js/{aesthetic-mixer,simplex-pad,cell-layout,glyph-font}.js` and `site/widgets/*.{html,jsx}` are
  vendored copies pinned by hash in `site/VENDORED.json`. Change them upstream, then run
  `python3 scripts/vendor.py --eido ../weft-eido --corpus ../weft-corpus`. CI fails if they are edited here.

## Development setup

You need Python 3.12 or newer, Node 20 or newer, and a C11 compiler.

```bash
git clone https://github.com/Moissanite-Labs/weft
cd weft
python3 -m venv .venv && . .venv/bin/activate
pip install numpy torch
```

CI runs the commands in the [README quick start](README.md#quick-start), plus:

```bash
python3 -m unittest discover -s scripts -p test_corpus_audit.py
python3 scripts/corpus_audit.py check
python3 weft/runtime/aywa/weft_daemon.py --self-test
python3 weft/runtime/mac/darwin_sysctl.py
python3 weft/runtime/mac/metal_loom.py
pip install -r scripts/requirements-browser.txt && python3 -m playwright install chromium
python3 scripts/test_telemetry_browser.py
git status --porcelain   # must be empty: tests may not rewrite tracked files
```

### Working on the website

`site/` is plain HTML, CSS and ES modules with no build step. Preview it with:

```bash
python3 -m http.server 8000 --directory site
```

- Everything in `site/` is public. Never put internal notes there.
- The landing page must not load anything from third parties. `site/_headers` sets a strict Content Security Policy.
- The demos import the same modules the tests cover. Tests for Weft's own modules are in `weft/runtime/aywa/`, and tests for the vendored Eido modules are in weft-eido.
- Keep the status table on the page in step with the README and the evidence.
- Check phone width (390 px), light and dark themes, keyboard navigation, and `prefers-reduced-motion`.

Merges to `main` that touch `site/` are deployed to w3ft.org by `.github/workflows/deploy-site.yml` once maintainers
have enabled it.

## Pull requests

1. Fork the repository and create a branch from `main`.
2. Keep each PR to one concern. Small PRs get reviewed sooner.
3. Write commit messages that describe the behaviour change in the imperative mood, for example
   "Reject NaN candidates before the distance check (#42)".
4. **Sign off every commit** (see below).
5. Make sure CI passes and the working tree stays clean after the tests.
6. Fill in the PR template, and say what evidence supports the change.

`main` is protected. It needs one approving review, passing checks, resolved conversations and linear history, and
merges are squash or rebase only.

### Developer Certificate of Origin

Weft uses the [Developer Certificate of Origin 1.1](https://developercertificate.org/) instead of a CLA. By signing off
you certify that you wrote the change, or otherwise have the right to submit it under the project's licenses. Add the
sign-off with `-s`:

```bash
git commit -s -m "Describe the change"
```

This adds a line like `Signed-off-by: Your Name <you@example.com>` that must match the commit author. If you forgot:

```bash
git rebase --signoff main
git push --force-with-lease
```

### AI-assisted contributions

You may use AI tools. A lot of this project was built with them. You are still responsible for every line you submit:
read it, run it, and sign it off yourself. Say in the PR description where a tool did substantial work. Don't submit
generated claims of execution or results you have not reproduced.

## Licensing of contributions

Contributions are accepted under the same licenses as the repository (see [NOTICE](NOTICE)):

- code under the [Apache License 2.0](LICENSE), as described in its Section 5;
- documentation and prose under [CC BY 4.0](LICENSE-docs).

## Reporting security issues

Please don't open public issues for vulnerabilities. See [SECURITY.md](SECURITY.md).
