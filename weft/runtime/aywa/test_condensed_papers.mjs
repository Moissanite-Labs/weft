import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import { CONDENSED_PAPERS, hasCondensed, paperSlug } from "../../../site/assets/js/condensed-papers.js";

const PAPERS = new URL("../../../site/papers/", import.meta.url);
const slugs = fs.readdirSync(PAPERS, { withFileTypes: true }).filter((d) => d.isDirectory()).map((d) => d.name);

test("the condensed list matches the condensed.json files on disk, for both page paths", () => {
  const onDisk = slugs.filter((s) => fs.existsSync(new URL(`${s}/condensed.json`, PAPERS))).sort();
  assert.deepEqual([...CONDENSED_PAPERS].sort(), onDisk);
  for (const s of slugs) {
    const has = onDisk.includes(s);
    assert.equal(hasCondensed(`/papers/${s}/`), has, s);
    assert.equal(hasCondensed(`/papers/${s}/index.html`), has, s);
  }
});

test("paperSlug reads paper paths and ignores everything else", () => {
  assert.equal(paperSlug("/papers/overview/"), "overview");
  assert.equal(paperSlug("/weft/papers/overview/index.html"), "overview");
  assert.equal(paperSlug("/papers/"), null);
  assert.equal(paperSlug("/"), null);
  assert.equal(paperSlug("/papers/overview/figures/fig1.png"), null);
  assert.equal(hasCondensed("/papers/models-as-cells/"), true);
  assert.equal(hasCondensed("/papers/a-future-paper/"), false);
});
