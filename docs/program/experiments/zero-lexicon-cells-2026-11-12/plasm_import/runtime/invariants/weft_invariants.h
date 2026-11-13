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
 */

#ifndef WEFT_INVARIANTS_H
#define WEFT_INVARIANTS_H

#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define WEFT_R_INVARIANT_DEFAULT 10.0f
#define WEFT_TENSION_MAX_DEFAULT 85.0f
#define WEFT_HOMEOSTATIC_MIN_DEFAULT 15.0f
#define WEFT_HOMEOSTATIC_MAX_DEFAULT 35.0f
#define WEFT_ROYALTY_UPSTREAM_BPS 1500ULL

static inline bool weft_verify_weight_update_safety(
    const float *baseline_w,
    const float *candidate_w,
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

    double sq_sum = 0.0;
    for (size_t i = 0; i < length; ++i) {
        float b = baseline_w[i];
        float c = candidate_w[i];
        if (!isfinite(b) || !isfinite(c)) {
            if (out_distance != NULL) *out_distance = INFINITY;
            return false;
        }
        double diff = (double)c - (double)b;
        sq_sum += diff * diff;
    }

    float dist = (float)sqrt(sq_sum);
    if (out_distance != NULL) {
        *out_distance = dist;
    }
    if (!isfinite(dist) || dist > r_invariant) {
        return false;
    }

    *metabolic_budget -= step_cost;
    return true;
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
