/**
 * Client-side SYM-2P positional parser (craft.md / build.md).
 *
 * Field widths follow weft/design/craft.md:136-145: role and action/state are
 * single bytes as two hex digits; the sequence ID is a four-digit decimal
 * packet number. Must stay in step with weft/runtime/aywa/sym2p_codec.py.
 */

// Signed decimal with optional fraction and exponent (Python float repr can emit 1e-05).
const METRIC_RE = /\((\w+)\s+(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)\)/g;

export function parseSym2pLine(line) {
  const trimmed = (line || "").trim();
  if (!trimmed.startsWith(":")) {
    throw new Error("SYM-2P line must start with ':'");
  }
  const role = parseInt(trimmed.slice(1, 3), 16);
  const actionState = parseInt(trimmed.slice(4, 6), 16);
  const sequence = parseInt(trimmed.slice(7, 11), 10);
  const payloadStart = trimmed.indexOf("[");
  const payloadEnd = trimmed.lastIndexOf("]");
  if (payloadStart < 0 || payloadEnd < 0) {
    throw new Error("SYM-2P s-expression missing");
  }
  const payload = trimmed.slice(payloadStart + 1, payloadEnd);
  const metrics = {};
  for (const match of payload.matchAll(METRIC_RE)) {
    metrics[match[1]] = parseFloat(match[2]);
  }
  return { role, actionState, sequence, metrics };
}

export async function digestSha256Hex(text) {
  const data = new TextEncoder().encode(text);
  const hash = await crypto.subtle.digest("SHA-256", data);
  return [...new Uint8Array(hash)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

export async function verifySym2pLine(line) {
  const trimmed = (line || "").trim();
  const payloadStart = trimmed.indexOf("[");
  const payloadEnd = trimmed.lastIndexOf("]");
  if (payloadStart < 0 || payloadEnd < 0) return false;
  const payloadBlock = trimmed.slice(payloadStart, payloadEnd + 1);
  const claimed = trimmed.slice(payloadEnd + 1, payloadEnd + 65);
  // A line without a hash is unverified, not valid.
  if (claimed.length !== 64) return false;
  const computed = await digestSha256Hex(payloadBlock);
  return claimed === computed;
}
