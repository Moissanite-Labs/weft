import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import { layoutCells } from "../../../docs/assets/js/cell-layout.js";
import { LAYERS, LOCUS_LAYERS, labelMetrics, layerHue, packCellRecords } from "../../../docs/assets/js/weft-loom.js";

const wgsl = fs.readFileSync(new URL("../../../docs/assets/shaders/dashboard_layout.wgsl", import.meta.url), "utf8");
const repos = JSON.parse(
  fs.readFileSync(new URL("../../../docs/data/moissanite_telemetry.json", import.meta.url), "utf8"),
).repositories;

test("struct Cell in the shader is four 16-byte vectors (64 bytes), matching packCellRecords", () => {
  const body = wgsl.match(/struct Cell \{([\s\S]*?)\};/)[1];
  const fields = [...body.matchAll(/(\w+)\s*:\s*(vec4<f32>|vec4<u32>)/g)].map((m) => m[1]);
  assert.deepEqual(fields, ["rect", "style", "info", "chars"]);
});

test("packCellRecords writes centre, half side, value, layer and label where the shader reads them", () => {
  const { options } = labelMetrics(1200);
  const L = layoutCells(repos.map((r) => ({ weight: r.commits, labelLength: r.name.length })), { width: 1200, height: 700 }, options);
  const n = repos.length;
  const dyn = { hue: repos.map((_, i) => i / n), emphasis: new Array(n).fill(1), hover: new Array(n).fill(0) };
  const buf = packCellRecords(L, repos, dyn);
  assert.equal(buf.byteLength, 32 * 64);
  const f = new Float32Array(buf);
  const u = new Uint32Array(buf);
  L.cells.forEach((c, i) => {
    const o = i * 16;
    assert.ok(Math.abs(f[o] - c.x) < 1e-3 && Math.abs(f[o + 1] - c.y) < 1e-3);
    assert.ok(Math.abs(f[o + 2] - c.half) < 1e-3);
    assert.equal(f[o + 9], repos[c.index].commits);
    assert.equal(f[o + 11], LAYERS.indexOf(repos[c.index].layer));
    const name = repos[c.index].name.toUpperCase().slice(0, 16);
    assert.equal(f[o + 8], name.length);
    const chars = [];
    for (let k = 0; k < name.length; k++) chars.push((u[o + 12 + (k >> 2)] >>> (8 * (k & 3))) & 255);
    assert.equal(String.fromCharCode(...chars), name);
  });
});

test("every fixture layer has a hue and every locus maps to known layers", () => {
  for (const r of repos) assert.ok(LAYERS.includes(r.layer), r.layer);
  for (const set of LOCUS_LAYERS) for (const l of set) assert.ok(LAYERS.includes(l));
  const hues = LAYERS.map((_, k) => layerHue(0.95, k));
  assert.ok(hues.every((h) => h >= 0 && h < 1));
  assert.equal(new Set(hues.map((h) => h.toFixed(6))).size, LAYERS.length);
});
