/**
 * Baseline-relative safety gate (Codebase C2, browser port).
 *
 * A line-for-line port of `verify_weight_update_safety_ex` in
 * `weft/runtime/invariants/invariants.py`. It is checked against the same
 * cross-language conformance vectors (`weft/runtime/invariants/vectors.json`)
 * as the Python and C11 implementations, by
 * `weft/runtime/aywa/test_invariant_gate.mjs`.
 *
 * The gate accepts a candidate weight update only when
 *   budget >= cost > 0   and   ||W_cand - W_base||_F <= r_invariant.
 *
 * Returns { accepted, distance, remainingBudget, reason } with the same
 * semantics as the Python tuple.
 */
export function verifyWeightUpdateSafety(baseline, candidate, rInvariant, budget, cost) {
  const b = Number(budget);
  const c = Number(cost);
  const r = Number(rInvariant);
  const reject = (distance, remainingBudget, reason) => ({ accepted: false, distance, remainingBudget, reason });

  if (!(Number.isFinite(b) && Number.isFinite(c) && Number.isFinite(r))) {
    return reject(Infinity, NaN, "non_finite_parameters");
  }
  if (b <= 0 || c <= 0 || r < 0) return reject(Infinity, b - c, "non_positive_budget_or_cost");
  if (b < c) return reject(Infinity, b - c, "insufficient_metabolic_budget");

  const base = Array.from(baseline ?? [], Number);
  const cand = Array.from(candidate ?? [], Number);
  if (base.length !== cand.length || base.length === 0) return reject(Infinity, b, "shape_mismatch");

  let sq = 0;
  for (let i = 0; i < base.length; i++) {
    if (!(Number.isFinite(base[i]) && Number.isFinite(cand[i]))) return reject(Infinity, b, "non_finite_weights");
    const d = cand[i] - base[i];
    sq += d * d;
  }
  const distance = Math.sqrt(sq);
  if (!Number.isFinite(distance)) return reject(Infinity, b, "non_finite_weights");
  if (distance > r) return reject(distance, b, "baseline_distance_exceeded");
  return { accepted: true, distance, remainingBudget: b - c, reason: "ok" };
}

/** Frobenius norm of a flat array: the "size" the weak, pre-repair check compared. */
export function frobeniusNorm(values) {
  let sq = 0;
  for (const v of values) sq += v * v;
  return Math.sqrt(sq);
}
