/* SharedArrayBuffer-capable telemetry ingest worker (Codebase C7 / Interface I2).
   Enforces SHA-256 verification on every SYM-2P line before updating uniforms (#24 / P22). */

import { parseSym2pLine, verifySym2pLine } from "../../../../../../site/assets/js/sym2p-parse.js";

let sharedView = null;
let pollMs = 45000;
let pollTimer = null;

function applyVerifiedMetrics(metrics, sequence) {
  if (sharedView && sharedView.byteLength >= 16) {
    const floats = new Float32Array(sharedView);
    if (metrics.active_nodes != null) floats[0] = metrics.active_nodes;
    if (metrics.tension != null) floats[1] = metrics.tension;
    if (metrics.gini != null) floats[3] = metrics.gini;
    floats[2] = performance.now() / 1000;
  }
  self.postMessage({
    type: "telemetry",
    hashValid: true,
    sequence,
    metrics,
  });
}

async function poll(dataUrl) {
  try {
    const url = new URL(dataUrl);
    url.searchParams.set("t", String(Date.now()));
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const text = await res.text();
    const line = text.split("\n").find((l) => l.trim().startsWith(":")) || "";
    if (!line) throw new Error("No telemetry packet in response");
    const parsed = parseSym2pLine(line);
    const verified = await verifySym2pLine(line);
    if (!verified) {
      const trimmed = line.trim();
      const payloadEnd = trimmed.lastIndexOf("]");
      const claimed = trimmed.slice(payloadEnd + 1, payloadEnd + 65);
      self.postMessage({
        type: "telemetry_rejected",
        reason: claimed.length !== 64 ? "missing_hash" : "hash_mismatch",
      });
      return;
    }
    applyVerifiedMetrics(parsed.metrics, parsed.sequence);
  } catch (err) {
    self.postMessage({ type: "error", message: err.message || String(err) });
  }
}

self.onmessage = (event) => {
  const msg = event.data || {};
  if (msg.type === "init") {
    pollMs = msg.pollMs || pollMs;
    if (msg.sab) {
      sharedView = msg.sab;
    }
    poll(msg.dataUrl);
    if (pollTimer) clearInterval(pollTimer);
    pollTimer = setInterval(() => poll(msg.dataUrl), pollMs);
  }
};
