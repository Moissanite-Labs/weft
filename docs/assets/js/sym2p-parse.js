/**
 * Client-side SYM-2P positional parser (craft.md / build.md).
 */

export function parseSym2pLine(line) {
  const trimmed = (line || "").trim();
  if (!trimmed.startsWith(":")) {
    throw new Error("SYM-2P line must start with ':'");
  }
  const role = parseInt(trimmed.slice(1, 3), 16);
  const actionState = parseInt(trimmed.slice(4, 6), 16);
  const sequence = parseInt(trimmed.slice(7, 11), 16);
  const payloadStart = trimmed.indexOf("[");
  const payloadEnd = trimmed.lastIndexOf("]");
  if (payloadStart < 0 || payloadEnd < 0) {
    throw new Error("SYM-2P s-expression missing");
  }
  const payload = trimmed.slice(payloadStart + 1, payloadEnd);
  const metrics = {};
  for (const match of payload.matchAll(/\((\w+)\s+([\d.]+)\)/g)) {
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
  if (payloadStart < 0) return false;
  const payloadBlock = trimmed.slice(payloadStart, payloadEnd + 1);
  const claimed = trimmed.slice(payloadEnd + 1, payloadEnd + 65);
  if (!claimed) return true;
  const computed = await digestSha256Hex(payloadBlock);
  return claimed === computed;
}
