# Comprehensive audit, 2026-11-08

ML Weft is open research on adaptive models that change within bounds a
reader can check. This audit checks the whole project against that claim.
It covers code, tests, docs, the live site, and GitHub settings.

The audit was requested before any new work lane was claimed. It makes no
code fix. Each finding names evidence and a test that would prove it wrong.
Fixes belong in separate pull requests.

## Baseline

| Item | Value at audit time |
|---|---|
| Audit date | 2026-11-08, about 23:01 UTC for live checks |
| weft main | `a18fc40e31e71325aec507258fb80bb26f125c7c` |
| weft-eido main | `1f7d031e58252db2c8382dfa3bad6446c676f230` |
| weft-corpus main | `4d4c37eb4bc063288bdd5c0b36d868aea7f9a4f9` |
| Unmerged branch tip | `bayan/gallant-tesla-oqw400` at `ddf06bf` in weft |
| Eido PR 1 head | `4edf98b8c287b83c7e9c8b2a25a9affdc3eca68e` |
| Corpus PR 1 head | `6d4a30919ff8adc70fc13c28a69dd35d2be6b317` |
| Visibility, all three | internal, GitHub Pages off |
| Local test host | macOS arm64, Python 3.12.15, Node 22, torch 2.15.0 |

Hosted CI uses Ubuntu, Python 3.12, and Node 20. Local Node is newer.
Local results below state the host for each run.

## Scope and method

In scope:

- `Moissanite-Labs/weft` on main and on the unmerged branch tip.
- `Moissanite-Labs/weft-eido` PR 1 and `Moissanite-Labs/weft-corpus` PR 1.
- The live site at w3ft.org, read with `curl` only. Nothing was deployed.
- GitHub settings read through the API. Nothing was changed.
- All 12 open weft issues and the one open discussion, number 11.

Out of scope:

- Cloudflare account settings beyond what the live site shows.
- Email routing state. Issue 57 records that check. It was not repeated.
- Full visual checks on phone and desktop in light and dark themes.
- Line by line re-derivation of issues 43, 44, 51, and 52.
  Those sections cite the issue and mark what this audit rechecked.

Method: fresh clones, the commands CI runs, direct code reading, and API
reads. Test counts come from run output, not from docs.

## Test evidence

All runs below used a clean tree. `git status --porcelain` stayed empty.

| Check | Host | Result |
|---|---|---|
| C2 invariants unit tests | local macOS | 4 ran, OK |
| C1 plasm unit tests | local macOS | 9 ran, 3 errors. See finding C3 |
| C3 IC unit tests | local macOS | 15 ran, OK |
| C6 telemetry unit tests | local macOS | 4 ran, OK |
| C4/C5 gateway unit tests | local macOS | 5 ran, OK |
| C7 Aywa Python tests | local macOS | 10 ran, OK |
| C7 and site Node tests | local macOS | 20 passed, 0 failed |
| Corpus audit tests and check | local macOS | 7 ran, OK. Check passes |
| Daemon, site, core, Mac self-tests | local macOS | all exit 0 |
| Telemetry browser test | local Chromium | 1 ran, OK |
| Vendored file hash check | local macOS | PASS |
| Hosted CI on weft main | GitHub Ubuntu | success on `a18fc40` |
| Hosted deploy workflow on main | GitHub Ubuntu | skipped. See finding B1 |
| Eido PR 1 Node tests | local macOS | 22 passed, 0 failed |
| Corpus PR 1 integrity check | local macOS | PASS. 62 files, 366 fences |
| Paper 1 experiments check | local, branch tip | PASS, 0 differences |
| Paper build check | local, branch tip | not run. No pandoc locally |

The corpus check reports 92 Python blocks parsed and 5 widgets found.
The hosted checks on both sibling PRs show success for test and DCO jobs.

## What holds up

- Hosted CI passes on weft main. The same suites pass locally, with one
  macOS exception in finding C3.
- Workflow actions are pinned by full commit hash in all three repos.
  Workflow permissions are read only for repository contents.
- Two active rulesets protect each repo. Applied rules match the files
  in `.github/rulesets/` on weft main.
- Secret scanning and push protection are enabled on all three repos.
  Open Dependabot alerts read back as zero in each repo.
- A pattern scan found no token, cloud key, or private key text.
  The scan covered tracked trees and full patch history in all three repos.
  It used fixed patterns only. It is not an entropy scan.
- Licenses are present and consistent. Code uses Apache-2.0.
  Docs use CC BY 4.0. `NOTICE` states the split in each repo checked.
- The gateway reads its key only from an environment variable.
  It refuses non-local RPC hosts unless a caller opts in.
  See `weft/runtime/gateway/gateway.py` lines 45 to 58.
- The landing page sends a strict content security policy.
  It also sends `X-Frame-Options: DENY` and HSTS. Scope limits are in S3.
- Compatibility files under `weft/runtime/core/` only re-export C1 and C3.
  The Aywa SYM-2P file only re-exports the C6 codec. No second logic copy.
- Paper 1 numbers reproduce from the branch code with zero differences.

## Blockers before any public flip

### B1. The live site does not come from main

Evidence:

- Live `https://w3ft.org/` returned 200 with 31,351 bytes.
  Its SHA-256 matches `site/index.html` at branch tip `ddf06bf`.
  It does not match the same file on main at `a18fc40`.
- Live paper pages and both PDFs returned 200. Main has no `papers/`
  tree and no `site/papers/` tree.
- The branch adds 71 files against main by direct diff.
  Five commits after `d81d4bf` have no pull request in weft.
- Hosted runs for that branch stop at `d81d4bf` and `45266b16`.
  Those runs came from PR 56. The five later commits have no hosted run.
  The CI workflow runs on pull requests and on pushes to main only.
- The deploy workflow run on main shows skipped.
  No `SITE_DEPLOY_ENABLED` repository variable is set.
  The workflow needs that variable to deploy. See
  `.github/workflows/deploy-site.yml`.

Impact: review, required checks, and the record in main do not cover the
bytes the public sees. A fix to main would not fix the live site.

Proved wrong by: a merged PR that brings the branch tip to main, green
required checks at that head, and a deploy record from main whose output
hashes match live responses.

Note on mechanics: the tree at squash commit `a18fc40` equals the tree
at `d81d4bf`. A direct diff shows zero lines. A PR from the branch to
main should therefore show only the later work in file terms.

### B2. The charter preface states a public flip that did not happen

Evidence: `docs/program/charter.md` says the repository went public on
2026-11-08 and that post and outreach limits lift. The API reads all
three repos as internal. Issue 27 keeps stealth limits in place.
Issue 64 also warns that the preface is not an owner directive.

Impact: a new reader follows the preface and breaks standing limits.
If history ships as is, the false statement ships with it.

Proved wrong by: API output that shows public visibility, with an owner
record that lifts the limits. No such output exists at audit time.

### B3. Sibling main branches hold only placeholder files

Evidence: weft-eido main and weft-corpus main each track one file.
Real content sits in Eido PR 1 (30 files) and Corpus PR 1 (88 files).
Both PRs read `REVIEW_REQUIRED` with no reviews recorded.
The weft README links to Eido philosophy under `main`.
That path returns 404 through the contents API today.

Impact: a flip today publishes two empty repos and at least one dead
link from the main README. The widgets index link to corpus `main`
has the same problem until Corpus PR 1 merges.

Proved wrong by: merged sibling PRs at reviewed heads, then a link
check over README and site files with zero missing repo paths.

### B4. Published contact paths do not reach anyone yet

Evidence: `SECURITY.md` directs reports to GitHub private reporting
or to `security@w3ft.org`. Issue 57 records private reporting calls
returning 404 while repos stay internal. Issue 57 also records email
routing disabled with no destination address verified.
This audit did not repeat the Cloudflare account check.

Impact: a security reporter can follow the policy and reach no inbox.
The conduct address in `CODE_OF_CONDUCT.md` has the same gap.

Proved wrong by: a test report through each published path, with a
recorded receipt in a monitored inbox. The destination choice needs
the owner. No address should be guessed.

### B5. Owner decisions have no visible queue

Evidence: open owner choices sit in issues 27 and 57, section 6.
They cover history form, widget terms, corpus inclusion, and flip time.
Issue 25 also needs an owner ruling on migration scope.
No `needs decision` label exists in weft. All 12 open issues carry
no labels at audit time.

Impact: agents cannot tell owner work from agent work by label.
The team rule in `AGENTS.md` asks for that label on owner calls.

Proved wrong by: the label present in all three repos and applied to
each issue that waits on the owner, removed after each ruling.

## Correctness and public claims

### C1. The shared vectors claim on main overstates coverage

Evidence:

- `README.md` line 28 says all three ports test against one shared set.
  `site/index.html` lines 120 to 121 and line 287 say the same on main.
- The vector file holds 12 cases. Six cover weight updates.
  Four cover tension. Two cover royalty splits.
- Python tests load all 12 cases from `vectors.json`.
- The browser test loads only the six weight update cases.
  See `weft/runtime/aywa/test_invariant_gate.mjs`.
- The C test holds hand written copies. It never reads `vectors.json`.
- Defaults also differ. Python sets the radius to 120.0.
  The C header sets 10.0. The vector constants set 10.0.
  See `invariants.py` line 24 and `weft_invariants.h` line 23.

The branch tip corrects most of this wording. One table cell remains.
Branch `README.md` line 46 still says tested against the same cases.
Live site text already uses the corrected branch wording.
Main still serves the stronger claim to anyone who clones it.

Proved wrong by: one added edge case that runs from the same file in
Python, C, and JavaScript, with equal results and equal defaults.
Issue 42 already scopes that work. No new issue is needed.

### C2. Plasm reports candidate error as held error

Evidence: this audit ran the issue 63 reproducer on CPU with radius
0.05 and 12 generations. Zero generations passed the gate flag.
Initial error read 1.657278. Reported final error read 1.457711.
The ratio read 0.880. The last parent error stayed 1.657278.
Code at `plasm.py` lines 449 and 459 uses the winner error for both
the status test and the reported final error.

Impact: a run that commits nothing can report progress that never
reached the held weights. Paper 1 works around this in its own code.
Other callers still read the wrong field.

Proved wrong by: the same reproducer reporting a ratio of 1.0, plus a
test that pins that case. Issue 63 lists a fix shape. Issue 51 covers
the wider report and ownership family in the same component.

### C3. Plasm shared memory tests fail on macOS. CI never runs macOS

Evidence: three of nine local plasm tests error on macOS with
`OSError: [Errno 63] File name too long`. The test helper builds names
from `weft_i4_` plus 32 hex characters. Darwin shared memory names
have a short limit. The same suite passes in hosted Ubuntu CI.
All CI jobs run on `ubuntu-latest`. No macOS job exists.

The default name `weft_stratified_plasm_v1` fits. The cycle helper
adds an underscore and the process ID at `plasm.py` line 320.
That form sits near the Darwin limit and has no length check.
A caller that passes a long name gets a raw OS error on macOS only.

Impact: Horizon I names Apple Silicon as the first hardware target.
The only host that cannot run these tests is that target family.

Proved wrong by: the plasm suite passing on a macOS host, plus a CI
job that keeps it passing. A short name test should cover a long
caller name and expect a clear error or a safe short form.

### C4. Ledger contracts have no compiled evidence

Evidence: CI has no Solidity compiler step. The gateway test checks a
pragma string for the contracts. Local `solc` was also absent here,
so this audit compiled nothing. README labels C4 as a draft that CI
does not compile. That label is accurate.

One simulator defect was rechecked by reading code. The dispute path
sets `dispute.adjudicated` before the slash balance check.
See `gateway.py` lines 235 to 241. A raised error after that write
leaves changed state. A reverting contract call would roll back.

Proved wrong by: clean local compilation of all three contracts, plus
shared cases that run in an EVM and in the simulator with equal state
after success and after failure. Issue 44 scopes this work.

### C5. Telemetry live mode mixes measured and estimated fields

Evidence: `harvester.py` live mode reads one API page. It copies
fixture commit and PR counts for known names. It estimates both
fields for other names from size and open issue counts.
It then marks the payload source as `github-api`.
The frame time is the fixed value 1762560000.0 in the harvest path.

README calls site data a fixture. That part is honest for the site.
The live label still covers fields that no API call measured.

Proved wrong by: field level source tags that split measured,
derived, fixture, and missing values, plus tests for paging, failure,
and stale data. Issue 45 scopes this work.

### C6. Royalty rounding has no shared edge case or ruling

Evidence: royalty vectors cover gross amounts 10000 and 1001 only.
Issues 42 and 44 record different floor choices for amount 1.
C2 floors the 15 percent share. Solidity floors the 85 percent share.
No vector pins amounts 0, 1, 2, 6, 7, 19, 20, or 21.

Proved wrong by: a recorded rounding policy plus vectors at those
amounts that pass in Python, C, JavaScript, and Solidity tests.
The policy choice comes first. Code should not pick it silently.

### C7. Open contract issues remain open by design

Issues 43 and 52 cover IC state and graph rules. Issue 51 covers
Plasm reports beyond finding C2. This audit ran current suites and
read the named code paths. It did not re-derive each acceptance case.
Treat those issues as open until their own tests land.

One change since their baselines deserves note. The IC suite now
runs 15 tests and includes `test_state_contract.py`. Green counts
alone still do not prove graph rules or confluence. Issue 52 says
why. Keep compiler and parallel reducer work behind that contract.

## Security and privacy

### S1. History carries more than the current tree shows

Evidence: current trees scan clean for token patterns. History still
holds the full corpus that main later split into its own repo.
It also holds stealth era program files and early site files.
Commit author fields include 14 commits under three addresses that
do not use the GitHub no-reply form. This report omits those addresses.

Impact: the flip choice is not only about files on main today.
Publishing history as is publishes every earlier tree and author line.

Proved wrong by: an owner ruling that names the history form, plus a
repeat scan of the exact history that would ship. A strong pre-flip
step is an entropy aware scanner in CI, such as gitleaks.
This audit ran fixed patterns only, so absence here has limits.

### S2. Widget pages load third party assets under weak headers

Evidence: each of the five widget HTML files loads Google fonts and
icon CSS. The files also name Google image hosts. `NOTICE` states
that those assets stay under their owners terms.
`site/_headers` sets the strict policy and frame deny rule for `/`
only. Paths under `/widgets/` and `/papers/` get the short shared
header set. That set has no content security policy.

Impact: opening a widget sends visitor requests to Google hosts.
Widget pages also lack the framing and script limits the home page has.
The license question in issue 57 stays open for the owner.

Proved wrong by: self hosted widget assets, or an owner ruling that
keeps remote assets with a scoped policy for widget paths.
A header check per path should prove the chosen policy ships.

### S3. The DCO gate rejects valid sign-offs it cannot match

Evidence: five Dependabot PRs sit open in weft, numbers 58 to 62.
Each shows the `dco` check failing and the other checks passing.
The bot author address differs from its sign-off address.
The script in `.github/workflows/dco.yml` needs an exact match.
Its pattern escapes dots only. Brackets and plus signs in an
address then act as pattern syntax, not as literal text.
A human rebase with sign-off still leaves the author field unchanged.

Publishing this audit proved the wider case. Its commit carries a
sign-off line that matches the author field by eye. The author uses
the ID based no-reply form with a plus sign. Hosted DCO still failed
that commit while the other three required checks passed.
Prior green DCO runs used an author address with no plus sign.

Impact: action updates stall. Standard privacy address commits stall
too. Pinned old versions then age in place. The open bumps include
major versions for checkout, setup actions, and the Wrangler action.
None should merge on green tests alone without change log review.

Proved wrong by: one human PR and one Dependabot PR that each pass
all required checks with no admin bypass. The script fix should
match addresses as fixed text and keep the human sign-off rule.
Bot sign-off handling needs its own narrow stated rule.

### S4. Hash checks prove integrity, not sender identity

Evidence: SYM-2P lines carry a SHA-256 digest of the payload.
Issue 45 already states the limit in plain terms.
Site and docs text checked here did not claim sender proof.
Keep that line in future copy. Words like verified need a nearby
statement of what was verified: bytes, not origin.

Proved wrong by: a signed packet design with key ownership, replay
rules, and tests. Until then, treat digest checks as damage checks.

## Repository and process health

### P1. Branch and ruleset sequencing needs one careful step

Evidence: the clone saw 19 remote branches. Six `codex/` branches
already sit inside main history. Five `mithrax/` branches and one
`ccr-` branch hold one or two commits and sit 15 to 31 commits
behind main. No open PR uses those six stale heads.
The long lived branch sits 11 ahead and 1 behind by commit count.

The branch ruleset file adds a fifth required check named `papers`.
Applied rules on weft still list four checks without it.
Applying the branch file first would block main PRs on a missing job.
Merging first leaves the file and applied rules out of step for a time.

Proved wrong by: the branch PR merged, the applied rules updated in
the same change window, and a follow up PR that passes all five
checks. Stale branch cleanup needs author consent per branch.
Keep the annotated audit source tag during any cleanup.

### P2. Vendored pins point at unmerged commits

Evidence: `site/VENDORED.json` pins Eido and Corpus PR head commits.
Hash checks pass today. Squash merges will create new main commits.
Those pin values will then name branch heads, not main commits.
Issue 57 already tracks the refresh choice.

Proved wrong by: pins updated to merged main commits in both sibling
repos, with the vendor check still passing and no file hash drift.

### P3. Settings and templates have small mismatches

Evidence:

- Wiki and Projects read as enabled in all three repos.
  The charter says docs live in tree and the Wiki stays unused.
- Corpus Discussions read as off. Weft and Eido read as on.
  No doc states whether that split is deliberate.
- `CODEOWNERS` names one maintainer account in each repo.
  Rulesets do not require code owner review. One approval still
  needs an account other than the PR author account.
- PR 56 body text lists five commits and an older head value.
  The merged PR holds six commits. Issue 57 tracks that edit.
- Only one of the last 30 main commits carries a sign-off line.
  The DCO rule is new. History will not gain sign-offs later.
  Readers should not read old commits as DCO covered.

None of these items blocks code work alone. Together they blur who
reviews, where docs live, and what the record claims.

### P4. The test matrix is narrow for the claims it guards

Evidence: CI runs one Ubuntu image, Python 3.12, and Node 20.
It has no macOS job, no Solidity build, no link check, and no
secret scan job beyond GitHub platform features.
The browser job covers the telemetry worker path only.
It does not cover the full checks listed in issue 57 section 4.

Proved wrong by: matrix jobs or scheduled jobs that cover macOS
plasm tests, contract compilation, and repo link targets.
Keep pull request jobs fast. Slower jobs can run on main pushes.

### P5. Papers need the same gates as other public claims

Evidence: paper sources, figures, PDFs, and generated site pages all
sit on the unmerged branch only. Experiment numbers reproduce here.
The full paper build check needs pandoc and PyYAML. CI on the branch
installs both. This audit lacked pandoc, so that check stayed unrun.
Generated PDFs appear twice by design: under `papers/` outputs and
under `site/papers/`. The branch build check guards that pair.

Proved wrong by: a merged papers PR whose hosted `papers` job passes,
plus a clean tree after regeneration. Issue 63 must stay linked from
Paper 1 until the plasm fix lands and numbers rerun.

## Suggested order

Owner calls stay with the owner. Agent work can proceed in parallel
where no owner call blocks it. One branch and one PR per change.

1. Review Eido PR 1 and Corpus PR 1 from an account other than the
   author account. Merge only at reviewed heads with green checks.
   Then refresh `site/VENDORED.json` pins to merged commits.
2. Open the weft PR from the long lived branch to main.
   Review the direct file diff, including papers and site changes.
   Fix the one table cell noted in finding C1 in that review cycle.
   Apply the five check ruleset right after merge. Prove it with a
   small follow up PR that passes all five checks.
3. Make deploys come from main through one recorded path.
   Set the deploy variable and secrets only by owner action.
   Record which path owns production. Retire manual branch deploys.
   Compare live hashes to main output after the first such deploy.
4. Correct the charter preface to match issue 27.
   Correct the PR 56 body text. Neither edit needs a code change.
5. Fix the DCO bot rule in its own PR. Then review each Dependabot
   major bump on change log evidence. Merge one at a time.
6. Fix Plasm held error reporting under issue 63 with its test.
   Then take the macOS name length fix and a macOS CI job.
   Rerun Paper 1 numbers after the reporting fix.
7. Work the open contract queue in issue order: 42, 43 with 52,
   44, 45, and 51. Keep economics and lineage rulings explicit.
   Do not bury policy choices inside test fixtures.
8. Finish admin prep that needs no owner data. The decision label
   now exists in all three repos with owner issues labeled.
   Settle Wiki and Discussions settings next. Add the link check.
9. Hold these for owner rulings: email destination, social preview
   upload, widget asset terms, history form, corpus inclusion, and
   the visibility flip itself. Keep Pages off. Keep outreach off.

## Where each finding lives

Filed at publication time so the team can claim work in the open.
Owner issues carry the decision label created at the same time.

| Finding | Repo home |
|---|---|
| B1 | Issue 71. Umbrella in issue 57 |
| B2 | Issue 72 |
| B3 | Eido PR 1 and Corpus PR 1 in sibling repos |
| B4 | Issue 57, decision label applied |
| B5 | Label created in all three repos. Issues 25, 27, 57 labeled |
| C1 | Issue 42 |
| C2 | Issue 63, wider family in issue 51 |
| C3 | Issue 68 |
| C4 | Issue 44 |
| C5 | Issue 45 |
| C6 | Issues 42 and 44 |
| C7 | Issues 43, 51, 52. New detail in issue 66 |
| S1 | Issue 57 for history form. Scan job in issue 73 |
| S2 | Issue 70. Asset terms in issue 57 |
| S3 | Issue 69 |
| S4 | Issue 67. Label limits also in issue 45 |
| P1 | Ruleset order in issue 71. Branch consent stays per author |
| P2 | Issue 57 |
| P3 | Issue 57 |
| P4 | Issues 44, 68, and 73 |
| P5 | Issue 71 for landing. Issue 63 for rerun duty |

## Appendix: commands behind the counts

Weft main, from repo root in a Python 3.12 venv with numpy and torch:

```text
python -m unittest discover -s weft/runtime/invariants -p 'test_*.py'
python -m unittest discover -s weft/runtime/plasm -p 'test_*.py'
python -m unittest discover -s weft/runtime/ic -p 'test_*.py'
python -m unittest discover -s weft/runtime/telemetry -p 'test_*.py'
python -m unittest discover -s weft/runtime/gateway -p 'test_*.py'
python -m unittest discover -s weft/runtime/aywa -p 'test_*.py'
node --test weft/runtime/aywa/test_*.mjs
python weft/runtime/aywa/weft_daemon.py --self-test
python weft/runtime/aywa/site_selftest.py
python weft/runtime/core/selftest.py
python -m unittest discover -s scripts -p test_corpus_audit.py
python scripts/corpus_audit.py check
python scripts/vendor.py --check
python scripts/test_telemetry_browser.py
```

Sibling PR heads, in detached worktrees:

```text
node --test test/*.test.mjs
python3 scripts/check_corpus.py
python papers/01-models-as-cells/experiments.py --check
```

Live checks used `curl` status, size, header, and SHA-256 reads.
GitHub reads used `gh` API calls for repos, rulesets, runs, issues,
pull requests, variables, and alert counts. No write call was made
during evidence gathering. Writes since then: this PR, issues 68 to
73, and the decision label in all three repos with labels applied
to issues 25, 27, and 57. No merge or deploy write was made.
