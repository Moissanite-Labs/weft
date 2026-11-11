// Papers that have condensed versions written beside them, as
// site/papers/<slug>/condensed.json. papers.js fetches condensed.json only for
// these, so the other paper pages log no 404 for a file that was never meant
// to exist. weft/runtime/aywa/test_condensed_papers.mjs fails if this list and
// the files on disk disagree.
export const CONDENSED_PAPERS = Object.freeze(["overview", "models-as-cells", "checkable-computation"]);

/** The paper slug for a pathname ending in papers/<slug>/ or papers/<slug>/index.html, else null. */
export function paperSlug(pathname) {
  const m = /\/papers\/([^/]+)\/(?:index\.html)?$/.exec(pathname);
  return m ? m[1] : null;
}

export function hasCondensed(pathname) {
  return CONDENSED_PAPERS.includes(paperSlug(pathname));
}
