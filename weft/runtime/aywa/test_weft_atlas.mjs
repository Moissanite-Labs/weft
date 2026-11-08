import assert from "node:assert/strict";
import test from "node:test";
import {
  AYWA_MODULES,
  CODEBASES,
  ECOSYSTEM_REPOS,
  GLOSSARY_ITEMS,
  HORIZONS,
  LOCI,
  WIDGETS,
} from "../../../docs/assets/js/weft-atlas.js";

test("weft-atlas exports all 6 spatial loci covering Aywa web design and the 3 implementation horizons", () => {
  assert.equal(LOCI.length, 6);
  const ids = LOCI.map((l) => l.id);
  assert.deepEqual(ids, ["spine", "aywa", "horizon1", "horizon2", "horizon3", "whitepaper"]);
});

test("weft-atlas exports all 4 evolutionary horizons and all 7 modular codebases (C1-C7)", () => {
  assert.equal(HORIZONS.length, 4);
  assert.equal(CODEBASES.length, 7);
  assert.deepEqual(
    CODEBASES.map((c) => c.id),
    ["C1", "C2", "C3", "C4", "C5", "C6", "C7"],
  );
});

test("weft-atlas exports all 5 Aywa design modules (D1-D5), 5 widgets, ecosystem repos, and glossary", () => {
  assert.equal(AYWA_MODULES.length, 5);
  assert.deepEqual(
    AYWA_MODULES.map((m) => m.code),
    ["D1", "D2", "D3", "D4", "D5"],
  );
  assert.equal(WIDGETS.length, 5);
  assert.ok(ECOSYSTEM_REPOS.length >= 19);
  assert.ok(GLOSSARY_ITEMS.length >= 10);
});
