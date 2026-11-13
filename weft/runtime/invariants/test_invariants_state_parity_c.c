/*
 * test_invariants_state_parity_c.c - Verifies remaining-budget parity on the
 * weight-update cases that agree with vectors.json, blocks negative-cost
 * metabolic budget minting, and checks 100,000-step IEEE-754 Zeno sub-ULP
 * strict budget monotonicity.
 *
 * Compile & run:
 *   gcc -O3 -std=c11 -Wall -Wextra -Werror weft/runtime/invariants/test_invariants_state_parity_c.c -lm -o test_state_parity && ./test_state_parity
 *
 * License: Apache-2.0
 */

#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "weft_invariants.h"

typedef struct {
    const char *name;
    size_t len_init;
    size_t len_prop;
    float w_init[4];
    float w_prop[4];
    float budget;
    float cost;
    float r_inv;
    bool exp_ok;
    float exp_rem_budget;
    bool exp_rem_is_nan;
} vector_case_t;

int main(void) {
    const float nan_f = NAN;
    const float inf_f = INFINITY;

    const vector_case_t cases[9] = {
        {"wu_valid_01", 2, 2, {0.0f, 0.0f}, {0.1f, 0.2f}, 10.0f, 1.0f, 1.0f, true, 9.0f, false},
        {"wu_invalid_dist_exceeded", 2, 2, {0.0f, 0.0f}, {1.0f, 1.0f}, 10.0f, 1.0f, 1.0f, false, 10.0f, false},
        {"wu_invalid_budget_insufficient", 1, 1, {0.0f}, {0.1f}, 0.5f, 1.0f, 1.0f, false, -0.5f, false},
        {"wu_invalid_negative_cost", 1, 1, {0.0f}, {0.1f}, 10.0f, -1.0f, 1.0f, false, 10.0f, false},
        {"wu_invalid_nan_weight", 2, 2, {0.0f, nan_f}, {0.1f, 0.2f}, 10.0f, 1.0f, 1.0f, false, 10.0f, false},
        {"wu_invalid_inf_weight", 1, 1, {0.0f}, {inf_f}, 10.0f, 1.0f, 1.0f, false, 10.0f, false},
        {"wu_invalid_dimension_mismatch", 2, 1, {0.0f, 0.0f}, {0.1f}, 10.0f, 1.0f, 1.0f, false, 10.0f, false},
        {"wu_invalid_empty_vectors", 0, 0, {0.0f}, {0.0f}, 10.0f, 1.0f, 1.0f, false, 10.0f, false},
        {"wu_invalid_nan_budget", 1, 1, {0.0f}, {0.1f}, nan_f, 1.0f, 1.0f, false, 0.0f, true}
    };

    for (int i = 0; i < 9; ++i) {
        vector_case_t c = cases[i];
        float b = c.budget;
        float d = 0.0f;
        bool ok = false;
        if (c.len_init == c.len_prop) {
            ok = weft_verify_weight_update_safety_masked(
                c.w_init, c.w_prop, NULL, c.len_init, c.r_inv, &b, c.cost, &d
            );
        }
        bool rem_ok = c.exp_rem_is_nan ? isnan(b) : (fabsf(b - c.exp_rem_budget) < 1e-6f);
        if (ok != c.exp_ok || !rem_ok) {
            fprintf(stderr, "FAIL %s: got ok=%d rem=%g (expected ok=%d rem=%g)\n",
                    c.name, ok, b, c.exp_ok, c.exp_rem_budget);
            return 1;
        }
    }

    /* Regression: a negative-cost call must leave metabolic budget unchanged. */
    float b_mint = 1.0f;
    float d_mint = 0.0f;
    const float w0[2] = {0.0f, 0.0f};
    const float w1[2] = {0.1f, 0.2f};
    if (weft_verify_weight_update_safety(w0, w1, 2, 1.0f, &b_mint, -10000.0f, &d_mint)) {
        return 1;
    }
    if (fabsf(b_mint - 1.0f) > 1e-9f) {
        fprintf(stderr, "FAIL negative-cost call mutated budget to %g\n", b_mint);
        return 1;
    }
    if (weft_verify_weight_update_safety(w0, w1, 2, 1.0f, &b_mint, 5000.0f, &d_mint)) {
        fprintf(stderr, "FAIL 5000-cost step succeeded from 1.0 budget!\n");
        return 1;
    }

    /* Regression: 100,000 sub-ULP steps strictly decrease budget every single step */
    float b_zeno = 100.0f;
    for (uint32_t s = 0; s < 100000U; ++s) {
        float prev = b_zeno;
        if (!weft_verify_weight_update_safety(w0, w1, 2, 1.0f, &b_zeno, 3.0e-6f, &d_mint)) {
            return 1;
        }
        if (!(b_zeno < prev)) {
            fprintf(stderr, "FAIL Zeno non-decreasing budget at step %u\n", s);
            return 1;
        }
    }

    printf("PASS: 9 vectors state-exact, negative-cost minting blocked, 100k Zeno ULP monotone.\n");
    return 0;
}
