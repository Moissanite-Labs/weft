/*
 * weft_invariants.h — Bare-Metal C11 Invariant Gate (Codebase C2 / Interface I3)
 * ==============================================================================
 * Provenance:
 *   Extracted and repaired from `weft/terrafab-calc.md:50-100`.
 *   Repairs applied:
 *     1. Issue #2 (M1): Computes Frobenius distance `||W_cand - W_base||_F` from
 *        saved baseline weights rather than comparing two scalar norms.
 *     2. Issue #23 (M6): Verifies `isfinite(*metabolic_budget)`,
 *        `isfinite(step_cost)`, `*metabolic_budget > 0`, `step_cost > 0`, and
 *        `*metabolic_budget >= step_cost` BEFORE subtracting `step_cost`, and
 *        rejects any `NaN`/`Inf` weight element.
 *     3. Numerical & mask hardening:
 *        - Frozen-bitmask tamper detection (`locked_mask`, normalizing +/-0.0f).
 *        - Laplace-scaled Neumaier `binary64` Frobenius accumulation compared in
 *          `double` prior to `float` cast (prevents `d*d` overflow, N=65,536
 *          drift, and sub-ULP float32 boundary round-down acceptance).
 *        - Monotone `float32` budget deduction via `nextafterf` (blocks sub-ULP
 *          Zeno free steps where `fl32(budget - step_cost) == budget`).
 */

#ifndef WEFT_INVARIANTS_H
#define WEFT_INVARIANTS_H

#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#define WEFT_R_INVARIANT_DEFAULT 120.0f
#define WEFT_TENSION_MAX_DEFAULT 85.0f
#define WEFT_HOMEOSTATIC_MIN_DEFAULT 15.0f
#define WEFT_HOMEOSTATIC_MAX_DEFAULT 35.0f
#define WEFT_ROYALTY_UPSTREAM_BPS 1500ULL

static inline bool weft_frobenius_distance_masked_f64(
    const float *baseline_w,
    const float *candidate_w,
    const uint8_t *locked_mask,
    size_t length,
    double *out_distance_f64
) {
    if (baseline_w == NULL || candidate_w == NULL || length == 0) {
        if (out_distance_f64 != NULL) *out_distance_f64 = INFINITY;
        return false;
    }

    double scale = 0.0;
    double ssq = 1.0;
    double comp = 0.0;

    for (size_t i = 0; i < length; ++i) {
        float b = baseline_w[i];
        float c = candidate_w[i];
        if (!isfinite(b) || !isfinite(c)) {
            if (out_distance_f64 != NULL) *out_distance_f64 = INFINITY;
            return false;
        }
        if (locked_mask != NULL && locked_mask[i] != 0U) {
            uint32_t b_bits = 0U;
            uint32_t c_bits = 0U;
            memcpy(&b_bits, &b, sizeof(uint32_t));
            memcpy(&c_bits, &c, sizeof(uint32_t));
            if (b == 0.0f && c == 0.0f) {
                b_bits = 0U;
                c_bits = 0U;
            }
            if (b_bits != c_bits) {
                if (out_distance_f64 != NULL) *out_distance_f64 = INFINITY;
                return false;
            }
            continue;
        }

        double abs_diff = fabs((double)c - (double)b);
        if (abs_diff == 0.0) {
            continue;
        }
        if (scale < abs_diff) {
            double ratio = scale / abs_diff;
            double ratio_sq = ratio * ratio;
            ssq = 1.0 + ssq * ratio_sq;
            comp = comp * ratio_sq;
            scale = abs_diff;
        } else {
            double ratio = abs_diff / scale;
            double term = ratio * ratio;
            double t = ssq + term;
            if (fabs(ssq) >= term) {
                comp += (ssq - t) + term;
            } else {
                comp += (term - t) + ssq;
            }
            ssq = t;
        }
    }

    double dist = (scale == 0.0) ? 0.0 : (scale * sqrt(ssq + comp));
    if (!isfinite(dist)) {
        if (out_distance_f64 != NULL) *out_distance_f64 = INFINITY;
        return false;
    }
    if (out_distance_f64 != NULL) {
        *out_distance_f64 = dist;
    }
    return true;
}

static inline bool weft_verify_weight_update_safety_masked(
    const float *baseline_w,
    const float *candidate_w,
    const uint8_t *locked_mask,
    size_t length,
    float r_invariant,
    float *metabolic_budget,
    float step_cost,
    float *out_distance
) {
    if (baseline_w == NULL || candidate_w == NULL || metabolic_budget == NULL || length == 0) {
        if (out_distance != NULL) *out_distance = INFINITY;
        return false;
    }
    if (!isfinite(*metabolic_budget) || !isfinite(step_cost) || !isfinite(r_invariant)) {
        if (out_distance != NULL) *out_distance = INFINITY;
        return false;
    }
    if (*metabolic_budget <= 0.0f || step_cost <= 0.0f || r_invariant < 0.0f) {
        *metabolic_budget -= step_cost;
        if (out_distance != NULL) *out_distance = INFINITY;
        return false;
    }
    if (*metabolic_budget < step_cost) {
        *metabolic_budget -= step_cost;
        if (out_distance != NULL) *out_distance = INFINITY;
        return false;
    }

    double dist_d = 0.0;
    if (!weft_frobenius_distance_masked_f64(baseline_w, candidate_w, locked_mask, length, &dist_d)) {
        if (out_distance != NULL) *out_distance = INFINITY;
        return false;
    }
    if (out_distance != NULL) {
        *out_distance = (float)dist_d;
    }
    if (dist_d > (double)r_invariant) {
        return false;
    }

    float prev_budget = *metabolic_budget;
    float next_budget = (float)((double)prev_budget - (double)step_cost);
    if (next_budget >= prev_budget) {
        next_budget = nextafterf(prev_budget, -INFINITY);
    }
    if (!isfinite(next_budget) || next_budget < 0.0f) {
        return false;
    }

    *metabolic_budget = next_budget;
    return true;
}

static inline bool weft_verify_weight_update_safety(
    const float *baseline_w,
    const float *candidate_w,
    size_t length,
    float r_invariant,
    float *metabolic_budget,
    float step_cost,
    float *out_distance
) {
    return weft_verify_weight_update_safety_masked(
        baseline_w, candidate_w, NULL, length, r_invariant, metabolic_budget, step_cost, out_distance
    );
}

static inline bool weft_verify_tension_bound(
    float tension,
    float max_tension,
    bool *out_homeostatic,
    bool *out_excision
) {
    if (!isfinite(tension) || !isfinite(max_tension) || tension < 0.0f) {
        if (out_homeostatic != NULL) *out_homeostatic = false;
        if (out_excision != NULL) *out_excision = true;
        return false;
    }
    bool accepted = (tension <= max_tension);
    if (out_homeostatic != NULL) {
        *out_homeostatic = (tension >= WEFT_HOMEOSTATIC_MIN_DEFAULT && tension <= WEFT_HOMEOSTATIC_MAX_DEFAULT);
    }
    if (out_excision != NULL) {
        *out_excision = !accepted;
    }
    return accepted;
}

static inline void weft_royalty_split_u64(
    uint64_t gross_wei,
    uint64_t upstream_bps,
    uint64_t *out_upstream_wei,
    uint64_t *out_weaver_wei
) {
    uint64_t up = (gross_wei * upstream_bps) / 10000ULL;
    uint64_t wv = gross_wei - up;
    if (out_upstream_wei != NULL) *out_upstream_wei = up;
    if (out_weaver_wei != NULL) *out_weaver_wei = wv;
}

#endif /* WEFT_INVARIANTS_H */
