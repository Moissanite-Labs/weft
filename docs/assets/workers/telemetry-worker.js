/* SharedArrayBuffer-capable telemetry ingest worker (craft.md).
   Falls back to postMessage when cross-origin isolation is unavailable. */

let sharedView = null;
let pollMs = 30000;

function applyMetrics(metrics) {
  if (sharedView && sharedView.byteLength >= 16) {
    const floats = new Float32Array(sharedView);
    if (metrics.active_nodes != null) floats[0] = metrics.active_nodes;
    if (metrics.tension != null) floats[1] = metrics.tension;
    if (metrics.gini != null) floats[3] = metrics.gini;
    floats[2] = performance.now() / 1000;
  }
  self.postMessage({ type: "telemetry", metrics });
}

function parseSym2p(line) {
  const trimmed = (line || "").trim();
  if (!trimmed.startsWith(":")) return {};
  const payloadStart = trimmed.indexOf("[");
  const payloadEnd = trimmed.lastIndexOf("]");
  const payload = trimmed.slice(payloadStart + 1, payloadEnd);
  const metrics = {};
  for (const match of payload.matchAll(/\((\w+)\s+([\d.]+)\)/g)) {
    metrics[match[1]] = parseFloat(match[2]);
  }
  return metrics;
}

async function poll(dataUrl) {
  try {
    const res = await fetch(`${dataUrl}?t=${Date.now()}`);
    const text = await res.text();
    const line = text.split("\n").find((l) => l.trim().startsWith(":")) || "";
    applyMetrics(parseSym2p(line));
  } catch (err) {
    self.postMessage({ type: "error", message: String(err) });
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
    setInterval(() => poll(msg.dataUrl), pollMs);
  }
};
