// Round-trip tests for the browser SYM-2P parser (issue #13).
// Run: node --test weft/runtime/aywa/test_sym2p_parse.mjs
// Lives beside the Python codec (not under docs/) so tests are not published by Pages.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { parseSym2pLine, verifySym2pLine } from "../../../docs/assets/js/sym2p-parse.js";

const here = dirname(fileURLToPath(import.meta.url));

// Produced by sym2p_codec.encode_sym2p_line; also asserted in test_sym2p_codec.py.
const GOLDEN_LINE =
  ":0a:ff:0042[s-exp (state 0.92) (tension -0.14) (drift 1e-05)]" +
  "234aa42e75091af1892873ef83caebb0720ed6dbdee6bdc1538fd1c6efdb5757";

test("sequence is a decimal packet number, role/action are hex bytes", () => {
  const parsed = parseSym2pLine(GOLDEN_LINE);
  assert.equal(parsed.sequence, 42);
  assert.equal(parsed.role, 10);
  assert.equal(parsed.actionState, 255);
});

test("signed and exponent metrics survive", () => {
  assert.deepEqual(parseSym2pLine(GOLDEN_LINE).metrics, { state: 0.92, tension: -0.14, drift: 1e-5 });
});

test("hash verification matches the Python encoder", async () => {
  assert.equal(await verifySym2pLine(GOLDEN_LINE), true);
});

test("missing hash is not valid", async () => {
  assert.equal(await verifySym2pLine(":01:03:0001[s-exp (tension 0.14)]"), false);
});

test("tampered payload fails hash", async () => {
  assert.equal(await verifySym2pLine(GOLDEN_LINE.replace("0.92", "0.93")), false);
});

test("published seed line parses and verifies", async () => {
  const text = readFileSync(join(here, "..", "..", "..", "docs", "data", "telemetry.jsonl"), "utf8");
  const line = text.split("\n").find((l) => l.startsWith(":"));
  const parsed = parseSym2pLine(line);
  assert.deepEqual([parsed.role, parsed.actionState, parsed.sequence], [1, 3, 1]);
  assert.equal(await verifySym2pLine(line), true);
});
