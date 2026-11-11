#include "weft_invariants.h"
#include <assert.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    uint32_t vec_id;
    uint32_t length;
    float    r_invariant;
    float    budget_in;
    float    step_cost;
    uint8_t  has_mask;
    uint8_t  expected_ok;
    uint16_t pad0;
    double   expected_dist_f64;
    float    expected_budget_out;
    uint32_t pad1;
} diff_vec_hdr_t;

static int run_differential_stream(const char *bin_path) {
    FILE *fp = fopen(bin_path, "rb");
    if (fp == NULL) {
        perror("fopen differential stream");
        return 1;
    }
    uint32_t count = 0;
    if (fread(&count, sizeof(uint32_t), 1, fp) != 1) {
        fclose(fp);
        return 1;
    }

    double max_abs_dist_err = 0.0;
    for (uint32_t idx = 0; idx < count; ++idx) {
        diff_vec_hdr_t h;
        if (fread(&h, sizeof(diff_vec_hdr_t), 1, fp) != 1) {
            fclose(fp);
            return 1;
        }
        size_t n = (size_t)h.length;
        float *bw = (float *)malloc(n * sizeof(float));
        float *cw = (float *)malloc(n * sizeof(float));
        uint8_t *mask = h.has_mask ? (uint8_t *)malloc(n * sizeof(uint8_t)) : NULL;
        if (bw == NULL || cw == NULL || (h.has_mask && mask == NULL)) {
            free(bw); free(cw); free(mask);
            fclose(fp);
            return 1;
        }
        if (fread(bw, sizeof(float), n, fp) != n ||
            fread(cw, sizeof(float), n, fp) != n ||
            (h.has_mask && fread(mask, sizeof(uint8_t), n, fp) != n)) {
            free(bw); free(cw); free(mask);
            fclose(fp);
            return 1;
        }

        double dist_d = 0.0;
        bool norm_ok = weft_frobenius_distance_masked_f64(bw, cw, mask, n, &dist_d);
        float bud = h.budget_in;
        float dist_f = 0.0f;
        bool ok = weft_verify_weight_update_safety_masked(
            bw, cw, mask, n, h.r_invariant, &bud, h.step_cost, &dist_f
        );

        if ((ok ? 1U : 0U) != h.expected_ok) {
            fprintf(stderr, "Verdict mismatch at vec %u: got %d expected %u\n", h.vec_id, ok, h.expected_ok);
            free(bw); free(cw); free(mask);
            fclose(fp);
            return 1;
        }
        if (ok) {
            if (!norm_ok) {
                free(bw); free(cw); free(mask);
                fclose(fp);
                return 1;
            }
            double derr = fabs(dist_d - h.expected_dist_f64);
            if (derr > max_abs_dist_err) {
                max_abs_dist_err = derr;
            }
            /* Bounded binary64 tolerance across compilers/ISAs (not exact bit identity) */
            if (derr > 1e-9 || bud != h.expected_budget_out) {
                fprintf(stderr, "Tolerance/budget mismatch at vec %u: derr=%.3e bud=%.9g exp_bud=%.9g\n",
                        h.vec_id, derr, bud, h.expected_budget_out);
                free(bw); free(cw); free(mask);
                fclose(fp);
                return 1;
            }
        }
        free(bw);
        free(cw);
        free(mask);
    }
    fclose(fp);
    printf("C_DIFFERENTIAL_PASS count=%u max_abs_dist_err=%.3e tol=1.000e-09\n", count, max_abs_dist_err);
    return 0;
}

int main(int argc, char **argv) {
    if (argc == 2) {
        return run_differential_stream(argv[1]);
    }

    assert(WEFT_R_INVARIANT_DEFAULT == 120.0f);

    /* 1. matching_sizes_large_move: rejected because baseline distance = sqrt(8) > 0.5 */
    {
        float base[4] = {1.0f, 0.0f, 0.0f, 1.0f};
        float cand[4] = {-1.0f, 0.0f, 0.0f, -1.0f};
        float budget = 10.0f;
        float dist = 0.0f;
        bool ok = weft_verify_weight_update_safety(base, cand, 4, 0.5f, &budget, 1.0f, &dist);
        assert(!ok);
        assert(fabsf(dist - 2.828427f) < 1e-4f);
        assert(fabsf(budget - 10.0f) < 1e-6f);
    }

    /* 2. valid_small_move: accepted, budget decremented from 10.0 to 9.0 */
    {
        float base[4] = {1.0f, 0.0f, 0.0f, 1.0f};
        float cand[4] = {1.1f, 0.0f, 0.0f, 0.9f};
        float budget = 10.0f;
        float dist = 0.0f;
        bool ok = weft_verify_weight_update_safety(base, cand, 4, 0.5f, &budget, 1.0f, &dist);
        assert(ok);
        assert(fabsf(dist - 0.14142136f) < 1e-5f);
        assert(fabsf(budget - 9.0f) < 1e-6f);
    }

    /* 3. reject_nan_candidate */
    {
        float base[4] = {1.0f, 0.0f, 0.0f, 1.0f};
        float cand[4] = {NAN, 0.0f, 0.0f, 1.0f};
        float budget = 10.0f;
        float dist = 0.0f;
        bool ok = weft_verify_weight_update_safety(base, cand, 4, 10.0f, &budget, 1.0f, &dist);
        assert(!ok);
        assert(isinf(dist));
        assert(fabsf(budget - 10.0f) < 1e-6f);
    }

    /* 4. reject_inf_candidate */
    {
        float base[4] = {1.0f, 0.0f, 0.0f, 1.0f};
        float cand[4] = {INFINITY, 0.0f, 0.0f, 1.0f};
        float budget = 10.0f;
        float dist = 0.0f;
        bool ok = weft_verify_weight_update_safety(base, cand, 4, 10.0f, &budget, 1.0f, &dist);
        assert(!ok);
        assert(isinf(dist));
    }

    /* 5. reject_insufficient_budget */
    {
        float base[4] = {1.0f, 0.0f, 0.0f, 1.0f};
        float cand[4] = {1.05f, 0.0f, 0.0f, 1.0f};
        float budget = 0.5f;
        float dist = 0.0f;
        bool ok = weft_verify_weight_update_safety(base, cand, 4, 0.5f, &budget, 1.0f, &dist);
        assert(!ok);
        assert(budget < 0.0f);
    }

    /* 6. tension bounds */
    {
        bool homeo = false, exc = false;
        assert(weft_verify_tension_bound(28.5f, 85.0f, &homeo, &exc) && homeo && !exc);
        assert(weft_verify_tension_bound(85.0f, 85.0f, &homeo, &exc) && !homeo && !exc);
        assert(!weft_verify_tension_bound(85.01f, 85.0f, &homeo, &exc) && !homeo && exc);
        assert(!weft_verify_tension_bound(-0.1f, 85.0f, &homeo, &exc) && !homeo && exc);
    }

    /* 7. royalty split */
    {
        uint64_t up = 0, wv = 0;
        weft_royalty_split_u64(10000ULL, 1500ULL, &up, &wv);
        assert(up == 1500ULL && wv == 8500ULL);
    }

    /* 8. Zeno sub-ULP monotone deduction (`cost < 0.5 * ulp_f32(100.0f)`) */
    {
        float base[4] = {1.0f, 2.0f, 3.0f, 4.0f};
        float cand[4] = {1.1f, 2.1f, 3.1f, 4.1f};
        float budget = 100.0f;
        float sub_ulp_cost = 3.0e-6f; /* 0.5 * ulp_f32(100.0f) = 3.8147e-6f */
        for (int s = 0; s < 1000; ++s) {
            float prev = budget;
            float dist = 0.0f;
            bool ok = weft_verify_weight_update_safety(base, cand, 4, 120.0f, &budget, sub_ulp_cost, &dist);
            if (!ok || !(budget < prev)) return 1;
        }
    }

    /* 9. Pre-cast double radius check (rejects 120.000003 where float32 rounds to 120.0f) & 1e25 scale */
    {
        float base[2] = {0.0f, 0.0f};
        float cand_over[2] = {120.0f, 0.02683282f}; /* sqrt(120^2 + 0.02683282^2) = 120.000003 > 120.0 */
        float budget = 10.0f;
        float dist = 0.0f;
        bool ok_over = weft_verify_weight_update_safety(base, cand_over, 2, 120.0f, &budget, 1.0f, &dist);
        if (ok_over || budget != 10.0f) return 1;

        float cand_huge[2] = {1.0e25f, 0.0f};
        bool ok_huge = weft_verify_weight_update_safety(base, cand_huge, 2, 1.0e26f, &budget, 1.0f, &dist);
        if (!ok_huge || !(budget < 10.0f)) return 1;
    }

    /* 10. Frozen-bitmask (`locked_mask`) 1-ULP tamper rejection & +/-0.0f normalization */
    {
        uint8_t mask[4] = {1U, 1U, 0U, 0U};
        float base[4] = {1.0f, 0.0f, 2.0f, 3.0f};
        float cand_tamper[4] = {nextafterf(1.0f, 2.0f), 0.0f, 2.5f, 3.0f};
        float budget = 10.0f;
        float dist = 0.0f;
        bool ok_tamper = weft_verify_weight_update_safety_masked(
            base, cand_tamper, mask, 4, 120.0f, &budget, 1.0f, &dist
        );
        if (ok_tamper || !isinf(dist) || budget != 10.0f) return 1;

        float cand_negzero[4] = {1.0f, -0.0f, 2.5f, 3.0f};
        bool ok_nz = weft_verify_weight_update_safety_masked(
            base, cand_negzero, mask, 4, 120.0f, &budget, 1.0f, &dist
        );
        if (!ok_nz || fabsf(dist - 0.5f) > 1e-6f || fabsf(budget - 9.0f) > 1e-6f) return 1;
    }

    printf("C_INVARIANTS_VECTORS_PASS\n");
    return 0;
}
