/*
 * weft_v2_invariants.h — WEFT-INVARIANTS/2.0 Reference C11 Safety & Mitosis Gate
 *
 * Upgrades Moissanite-Labs/weft `weft/runtime/invariants/weft_invariants.h` with:
 *   1. Strict IEEE-754 finiteness guards (blocks NaN/Inf/negative-zero exploits).
 *   2. Frozen-core IEEE-754 binary32 representation check (`locked_mask`, normalizing +/-0.0f).
 *   3. Scaled Neumaier compensated float64 Frobenius norm accumulation across
 *      65,536-float StratifiedMemoryArena strata (eliminates C11 float32 vs
 *      Python/JS float64 boundary consensus splits and float32 sq-overflow).
 *   4. ULP-monotone metabolic budget deduction via `nextafterf` floor (eliminates
 *      the IEEE-754 Zeno Free-Step Bypass where `budget - cost == budget`).
 *   5. Pythagorean Orthogonal Mitosis verification (`||U_p^T U_c||_F <= eps_orth`)
 *      and Mitotic Diagnostic Ratio (MDR) harness-side trigger (`weft#111` F5/F6/R4).
 *
 * License: Apache-2.0
 */

#ifndef WEFT_V2_INVARIANTS_H
#define WEFT_V2_INVARIANTS_H

#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#define WEFT_V2_R_INVARIANT_DEFAULT      120.0
#define WEFT_V2_TENSION_MAX_DEFAULT       85.0
#define WEFT_V2_HOMEOSTATIC_MIN_DEFAULT   15.0
#define WEFT_V2_HOMEOSTATIC_MAX_DEFAULT   35.0
#define WEFT_V2_MDR_TRIGGER_DEFAULT        2.5
#define WEFT_V2_ORTH_TOL_DEFAULT           1e-5
#define WEFT_V2_ROYALTY_UPSTREAM_BPS    1500ULL

typedef enum {
    WEFT_OK                        = 0,
    WEFT_ERR_NULL_PTR              = 1,
    WEFT_ERR_NONFINITE_INPUT       = 2,
    WEFT_ERR_INVALID_COST          = 3,
    WEFT_ERR_BUDGET_EXHAUSTED      = 4,
    WEFT_ERR_FROZEN_CORE_MUTATED   = 5,
    WEFT_ERR_RADIUS_EXCEEDED       = 6,
    WEFT_ERR_TENSION_EXCISION      = 7,
    WEFT_ERR_SUBSPACE_OVERLAP      = 8
} weft_status_t;

typedef enum {
    WEFT_PLATEAU_NONE              = 0,
    WEFT_PLATEAU_TASK_CEILING      = 1,
    WEFT_PLATEAU_OPTIMIZER_STUCK   = 2,
    WEFT_PLATEAU_CAPACITY_LIMIT    = 3
} weft_plateau_regime_t;

/*
 * Baseline v1 naive float32 implementation preserved strictly as a differential
 * control to demonstrate the Zeno ULP bypass and N=65536 float32 rounding split.
 */
static inline bool weft_v1_naive_verify_weight_update(
    const float *baseline_w,
    const float *candidate_w,
    size_t length,
    float r_invariant,
    float *metabolic_budget,
    float step_cost,
    float *out_distance
) {
    if (!baseline_w || !candidate_w || !metabolic_budget) return false;
    if (!(step_cost > 0.0f) || *metabolic_budget < step_cost) return false;
    if (r_invariant < 0.0f) return false;

    float sum_sq = 0.0f;
    for (size_t i = 0; i < length; ++i) {
        float diff = candidate_w[i] - baseline_w[i];
        sum_sq += diff * diff;
    }
    float dist = sqrtf(sum_sq);
    if (out_distance) *out_distance = dist;
    if (!(dist <= r_invariant)) return false;

    /* Vulnerable in float32 when step_cost < 0.5 * ulp(*metabolic_budget) */
    *metabolic_budget -= step_cost;
    return true;
}

/*
 * Compensated scaled Frobenius norm in IEEE-754 binary64 (Neumaier + Laplace scaling).
 * Prevents overflow for |diff| ~ 1e30 and prevents catastrophic accumulation drift
 * for StratifiedMemoryArena arrays of length >= 65,536.
 */
static inline bool weft_v2_compensated_frobenius_distance(
    const float *baseline_w,
    const float *candidate_w,
    const uint8_t *locked_mask,
    size_t length,
    double *out_distance,
    weft_status_t *out_status
) {
    double scale = 0.0;
    double ssq   = 1.0;
    double comp  = 0.0;

    for (size_t i = 0; i < length; ++i) {
        float b = baseline_w[i];
        float c = candidate_w[i];
        if (!isfinite(b) || !isfinite(c)) {
            if (out_status) *out_status = WEFT_ERR_NONFINITE_INPUT;
            return false;
        }
        if (locked_mask && locked_mask[i] != 0U) {
            uint32_t b_bits = 0U, c_bits = 0U;
            memcpy(&b_bits, &b, sizeof(uint32_t));
            memcpy(&c_bits, &c, sizeof(uint32_t));
            /* Normalize +0.0f and -0.0f before bitwise comparison */
            if (b == 0.0f && c == 0.0f) {
                b_bits = 0U;
                c_bits = 0U;
            }
            if (b_bits != c_bits) {
                if (out_status) *out_status = WEFT_ERR_FROZEN_CORE_MUTATED;
                return false;
            }
            continue;
        }

        double abs_diff = fabs((double)c - (double)b);
        if (abs_diff == 0.0) continue;

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
        if (out_status) *out_status = WEFT_ERR_NONFINITE_INPUT;
        return false;
    }
    if (out_distance) *out_distance = dist;
    if (out_status) *out_status = WEFT_OK;
    return true;
}

/*
 * Hardened WEFT-INVARIANTS/2.0 weight-update predicate.
 * Enforces:
 *   1. All inputs finite, r_invariant >= 0, step_cost > 0, budget >= step_cost.
 *   2. Frozen-core IEEE-754 representation check on locked_mask != NULL.
 *   3. Compensated binary64 Frobenius distance <= (double)r_invariant.
 *   4. Strict ULP-monotone budget decrease (`new_budget < old_budget`).
 */
static inline bool weft_v2_verify_weight_update_safety(
    const float *baseline_w,
    const float *candidate_w,
    const uint8_t *locked_mask,
    size_t length,
    double r_invariant,
    float *metabolic_budget,
    float step_cost,
    double *out_distance,
    weft_status_t *out_status
) {
    if (!baseline_w || !candidate_w || !metabolic_budget) {
        if (out_status) *out_status = WEFT_ERR_NULL_PTR;
        return false;
    }
    float budget = *metabolic_budget;
    if (!isfinite(budget) || !isfinite(step_cost) || !isfinite(r_invariant) || r_invariant < 0.0) {
        if (out_status) *out_status = WEFT_ERR_NONFINITE_INPUT;
        return false;
    }
    if (!(step_cost > 0.0f)) {
        if (out_status) *out_status = WEFT_ERR_INVALID_COST;
        return false;
    }
    if ((double)budget < (double)step_cost) {
        if (out_status) *out_status = WEFT_ERR_BUDGET_EXHAUSTED;
        return false;
    }

    double dist = 0.0;
    weft_status_t st = WEFT_OK;
    if (!weft_v2_compensated_frobenius_distance(baseline_w, candidate_w, locked_mask, length, &dist, &st)) {
        if (out_distance) *out_distance = NAN;
        if (out_status) *out_status = st;
        return false;
    }
    if (out_distance) *out_distance = dist;

    if (!(dist <= r_invariant)) {
        if (out_status) *out_status = WEFT_ERR_RADIUS_EXCEEDED;
        return false;
    }

    /* Strict ULP-monotone metabolic deduction: blocks Zeno sub-ULP free steps */
    double exact_rem = (double)budget - (double)step_cost;
    float next_budget = (float)exact_rem;
    if (next_budget >= budget) {
        next_budget = nextafterf(budget, -INFINITY);
    }
    if (next_budget < 0.0f || !isfinite(next_budget)) {
        if (out_status) *out_status = WEFT_ERR_BUDGET_EXHAUSTED;
        return false;
    }

    *metabolic_budget = next_budget;
    if (out_status) *out_status = WEFT_OK;
    return true;
}

/*
 * Homeostatic metabolic tension and harness-side Mitotic Diagnostic Ratio (MDR) gate.
 * Distinguishes the three plateau regimes identified in Moissanite-Labs/weft#111 (F5):
 *   1. Task at ceiling (heldout_error <= error_floor)
 *   2. Optimizer stuck inside fixed capacity (MDR < mdr_threshold, dormant units recycled)
 *   3. Capacity bottleneck (heldout_error > error_floor && MDR >= mdr_threshold -> Mitosis)
 */
static inline bool weft_v2_verify_tension_and_mitosis_trigger(
    double tension,
    double max_tension,
    double heldout_error,
    double error_floor,
    double grad_parallel_norm,
    double grad_orth_norm,
    double mdr_threshold,
    bool *out_homeostatic,
    bool *out_excision,
    bool *out_trigger_mitosis,
    weft_plateau_regime_t *out_regime
) {
    if (!isfinite(tension) || !isfinite(max_tension) || tension < 0.0 || max_tension <= 0.0 ||
        !isfinite(heldout_error) || !isfinite(error_floor) ||
        !isfinite(grad_parallel_norm) || !isfinite(grad_orth_norm) ||
        grad_parallel_norm < 0.0 || grad_orth_norm < 0.0 || !isfinite(mdr_threshold)) {
        if (out_homeostatic) *out_homeostatic = false;
        if (out_excision) *out_excision = true;
        if (out_trigger_mitosis) *out_trigger_mitosis = false;
        if (out_regime) *out_regime = WEFT_PLATEAU_NONE;
        return false;
    }

    bool excision = (tension > max_tension);
    bool homeostatic = (tension >= WEFT_V2_HOMEOSTATIC_MIN_DEFAULT &&
                        tension <= WEFT_V2_HOMEOSTATIC_MAX_DEFAULT);

    if (out_homeostatic) *out_homeostatic = homeostatic;
    if (out_excision) *out_excision = excision;

    if (excision) {
        if (out_trigger_mitosis) *out_trigger_mitosis = false;
        if (out_regime) *out_regime = WEFT_PLATEAU_NONE;
        return false;
    }

    double mdr = grad_orth_norm / (grad_parallel_norm + 1e-12);
    weft_plateau_regime_t regime = WEFT_PLATEAU_NONE;
    bool trigger = false;

    if (heldout_error <= error_floor) {
        regime = WEFT_PLATEAU_TASK_CEILING;
    } else if (grad_parallel_norm <= 1e-3 && mdr >= mdr_threshold) {
        regime = WEFT_PLATEAU_CAPACITY_LIMIT;
        trigger = true;
    } else if (grad_parallel_norm <= 1e-3) {
        regime = WEFT_PLATEAU_OPTIMIZER_STUCK;
    }

    if (out_trigger_mitosis) *out_trigger_mitosis = trigger;
    if (out_regime) *out_regime = regime;
    return true;
}

/*
 * Pythagorean Orthogonal Mitosis Bound Check:
 * Verifies |<Delta_parent, Delta_child>_F| <= eps_orth * ||Delta_p||_F * ||Delta_c||_F
 * and ||Delta_parent + Delta_child||_F <= r_max.
 */
static inline bool weft_v2_verify_pythagorean_mitosis(
    const float *delta_parent,
    const float *delta_child,
    size_t length,
    double r_max,
    double eps_orth,
    double *out_combined_norm,
    double *out_cosine_overlap,
    weft_status_t *out_status
) {
    if (!delta_parent || !delta_child || !isfinite(r_max) || r_max < 0.0 || !isfinite(eps_orth) || eps_orth < 0.0) {
        if (out_status) *out_status = WEFT_ERR_NONFINITE_INPUT;
        return false;
    }

    double dot = 0.0, dot_c = 0.0;
    double np_sq = 0.0, np_c = 0.0;
    double nc_sq = 0.0, nc_c = 0.0;

    for (size_t i = 0; i < length; ++i) {
        double p = (double)delta_parent[i];
        double c = (double)delta_child[i];
        if (!isfinite(p) || !isfinite(c)) {
            if (out_status) *out_status = WEFT_ERR_NONFINITE_INPUT;
            return false;
        }
        /* Neumaier compensated inner product & norms */
        double prod = p * c;
        double t_dot = dot + prod;
        dot_c += (fabs(dot) >= fabs(prod)) ? ((dot - t_dot) + prod) : ((prod - t_dot) + dot);
        dot = t_dot;

        double p2 = p * p;
        double t_np = np_sq + p2;
        np_c += (np_sq >= p2) ? ((np_sq - t_np) + p2) : ((p2 - t_np) + np_sq);
        np_sq = t_np;

        double c2 = c * c;
        double t_nc = nc_sq + c2;
        nc_c += (nc_sq >= c2) ? ((nc_sq - t_nc) + c2) : ((c2 - t_nc) + nc_sq);
        nc_sq = t_nc;
    }

    double norm_p = sqrt(fmax(0.0, np_sq + np_c));
    double norm_c = sqrt(fmax(0.0, nc_sq + nc_c));
    double inner  = dot + dot_c;
    double denom  = norm_p * norm_c;
    double cos_ov = (denom > 0.0) ? (fabs(inner) / denom) : 0.0;
    double comb_sq = fmax(0.0, (np_sq + np_c) + (nc_sq + nc_c) + 2.0 * inner);
    double comb_norm = sqrt(comb_sq);

    if (out_combined_norm) *out_combined_norm = comb_norm;
    if (out_cosine_overlap) *out_cosine_overlap = cos_ov;

    if (cos_ov > eps_orth) {
        if (out_status) *out_status = WEFT_ERR_SUBSPACE_OVERLAP;
        return false;
    }
    if (comb_norm > r_max) {
        if (out_status) *out_status = WEFT_ERR_RADIUS_EXCEEDED;
        return false;
    }
    if (out_status) *out_status = WEFT_OK;
    return true;
}

#endif /* WEFT_V2_INVARIANTS_H */
