# Releasing and archiving on Zenodo

The owner approved Zenodo records for ML Weft on 2026-11-09, effective once the repository is public. This page is the
checklist. Every step that publishes something is an owner action. Zenodo records cannot be deleted once published,
only superseded by new versions, so check each one before pressing Publish.

There are two kinds of record:

| Record | What it holds | Licence | How it is made |
|---|---|---|---|
| **Software** | An archive of this repository at a release tag | Apache-2.0 (docs inside it CC BY 4.0, see `NOTICE`) | Zenodo's GitHub integration, from a GitHub release. Metadata from [`.zenodo.json`](../../.zenodo.json). |
| **Papers 0–2** | Each paper's PDF, one record per paper | CC BY 4.0 | Uploaded as a *preprint*. Metadata from `scripts/zenodo_metadata.py papers`. |

Each record gets a *concept DOI* (all versions) and a *version DOI* (this version). Cite the concept DOI unless a
specific version matters. The creator on every record is Ahraz Arifuddin (Moissanite Labs). The creator list lives
in `.zenodo.json` and `CITATION.cff`, and CI checks that the two agree (`python3 scripts/zenodo_metadata.py --check`).

## What the archive holds

The software record archives the whole repository at the release tag, the same files anyone can see on GitHub. The
owner decided on 2026-11-08 that the exported widgets in `site/widgets/` stay in their original form; `NOTICE` names
the Google-hosted modules and fonts they load at runtime, which are not part of the archive. `weft-corpus` is not
archived: it holds raw session transcripts. To leave a path out of future archives, add it to `.gitattributes` with
`export-ignore`.

## Steps

1. **Repository is public.** The Zenodo GitHub integration only archives public repositories.
2. **Enable the repository** in Zenodo under *Account → GitHub* (the organisation is already connected). Do this
   before creating the release: Zenodo only sees releases published after the switch is on.
3. **Tag and release** from `main` on GitHub, for example `v0.1.0`, with short release notes. Zenodo mints the
   software DOI within a few minutes. Check the record's files, creators and licence, then note its concept DOI.
4. **Write the paper metadata** with the software DOI linked:

   ```bash
   python3 scripts/zenodo_metadata.py papers --software-doi 10.5281/zenodo.NNNNNNN --out zenodo-papers
   ```

   This writes one JSON file per paper (title, abstract, version, date, keywords, licence, and links to the w3ft.org
   page, the commit the paper describes and the software record). `_file` names the PDF to upload. Use it with the
   Zenodo API, or copy the fields into the upload form. The output is not committed.
5. **Upload Papers 0, 1 and 2** as *Publication → Preprint* under CC BY 4.0, one record each. Check the preview, then
   publish.
6. **Record the DOIs in the repository** in a pull request: add `doi:` to each paper's front matter and rebuild with
   `scripts/build_papers.py` so the pages and the BibTeX show it; add the software DOI badge to `README.md` and
   `doi:` to `CITATION.cff`.

## Later versions

- **Software:** each new GitHub release becomes a new version of the same software record automatically.
- **Papers:** when a paper's `version` changes, open its Zenodo record and choose *New version*, upload the new PDF and
  regenerate the metadata with step 4. Don't create a fresh record, or the concept DOI splits.
