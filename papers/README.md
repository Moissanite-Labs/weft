# Papers

The ML Weft paper series. Each paper is published on [w3ft.org/papers](https://w3ft.org/papers/) as a web page in
the site's design and as a PDF typeset for print.

| # | Paper | Source |
|---|---|---|
| 0 | *ML Weft: adaptive models within bounds you can check* | [`00-overview/paper.md`](00-overview/paper.md) |
| 1 | *Models as Cells* | [`01-models-as-cells/paper.md`](01-models-as-cells/paper.md) |
| 2 | *Checkable Computation* | [`02-checkable-computation/paper.md`](02-checkable-computation/paper.md) |
| 3 | *Eido* | in preparation |
| 4 | *Constitution vs. Contract* | planned |

## Rules for every paper

- **Label the evidence.** The front matter's `status` says what runs, what is simulated, and what is design. The text
  never presents a design as a result.
- **Pin the code.** `commit` names the repository commit the paper describes.
- **Numbers come from code.** Every number reported as a result is produced by a script in the paper's directory
  that imports the tested modules. CI re-runs it and fails if the numbers drift (`experiments.py --check`).
- **Say what it does not show.** Every technical paper has a limitations section.
- **Keep the vision language, tie it to mechanisms.** Each biological term is linked to the code that implements it
  today.

## Layout

```
papers/
  NN-slug/paper.md          Markdown with YAML front matter (title, subtitle, number, slug, version, date,
                            authors, status, commit, abstract, keywords)
  NN-slug/figures/*.svg     figures referenced from the paper
  NN-slug/experiments.py    optional: produces results.json and figures
  series.yml                upcoming papers shown on the index
  templates/                site-paper.html, site-index.html, print-paper.html, print.css, fonts
```

Generated output goes to `site/papers/`: an index, one page per paper, figures, the PDFs, and `manifest.json`, which
ties each PDF to the hashes of its sources. The output is committed so the site stays a plain static directory.

## Building

You need pandoc 3.1.3 exactly ([release page](https://github.com/jgm/pandoc/releases/tag/3.1.3)), PyYAML, and Playwright with Chromium. Other pandoc releases produce different HTML, so the CI check would fail; the build script refuses to run with any other version, and CI installs the same release.

```bash
pip install pyyaml playwright && python3 -m playwright install chromium
python3 papers/01-models-as-cells/experiments.py   # if you changed the experiments (also needs numpy, torch, matplotlib)
python3 scripts/build_papers.py                    # HTML and PDF
python3 scripts/build_papers.py --check            # what CI runs
```

Set `WEFT_BROWSER_EXECUTABLE` to use a system Chromium. The header and footer of the paper pages are taken from
`site/index.html`, so rebuild after changing the landing page's navigation.

## Versioning

Bump `version` and `date` for any change of substance, and say what changed in the pull request. A new version
gets a new PDF file name (`ml-weft-paper-<n>-<slug>-v<version>.pdf`). Earlier PDFs are never deleted: they stay at
their URLs and are listed on the paper's page, so existing citations and links keep working.

## License

The text and figures are under [CC BY 4.0](../LICENSE-docs), and the scripts under [Apache-2.0](../LICENSE). The
fonts in `templates/fonts/` are under the SIL Open Font License ([`OFL.txt`](templates/fonts/OFL.txt)).
