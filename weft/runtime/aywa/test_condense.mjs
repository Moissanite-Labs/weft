// Condense guard (issue #96): the level clamp and the passage-key hash.
// Run: node --test weft/runtime/aywa/test_condense.mjs
// The clamp is the guard the PR 93 review caught missing on the
// ?condense= path: a negative level left passages at -1 while the panel
// showed 0. These tests pin the helper every call site uses, including
// its NaN case. The fnv vectors pin the hash the key check in
// scripts/check_condensed.py recomputes in Python.
// condense.js imports attention.js, which starts itself on the next
// microtask unless held, so this test holds it first, like papers.js does.
import { test } from "node:test";
import assert from "node:assert/strict";
import { holdAttention } from "../../../site/assets/js/attention.js";
import { clamp, fnv } from "../../../site/assets/js/condense.js";

holdAttention();

test("clamp keeps levels inside their range", () => {
  assert.equal(clamp(-1, 0, 3), 0);
  assert.equal(clamp(4, 0, 3), 3);
  assert.equal(clamp(2, 0, 3), 2);
  assert.equal(clamp(0, 0, 5), 0);
  assert.equal(clamp(5, 0, 5), 5);
  assert.equal(clamp(6, 0, 5), 5);
});

test("clamp sends a bad level to the floor, never NaN", () => {
  assert.equal(clamp(NaN, 0, 3), 0);
  assert.equal(clamp(NaN, 0, 5), 0);
  assert.ok(!Number.isNaN(clamp(NaN, 0, 3)));
});

test("fnv matches the known vectors", () => {
  assert.equal(fnv(""), "811c9dc5");
  assert.equal(fnv("hello world"), "d58b3fa7");
  assert.equal(
    fnv("C7 · The browser field. A WebGPU renderer, with a Canvas2D fallback, draws live state as a field of cells."),
    "da024371",
  );
  assert.equal(fnv("a — b"), "5c819336");
});

test("fnv is stable and separates texts", () => {
  assert.equal(fnv("one line per section"), fnv("one line per section"));
  assert.notEqual(fnv("one line per section"), fnv("one line per sectoin"));
});
