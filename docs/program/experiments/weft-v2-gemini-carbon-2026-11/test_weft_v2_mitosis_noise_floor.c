/*
 * test_weft_v2_mitosis_noise_floor.c — Standalone noise-floor regression test for the
 * MDR gate in weft_v2_verify_tension_and_mitosis_trigger.
 *
 * Background: the gate used to compute mdr = grad_orth_norm / (grad_parallel_norm + 1e-12)
 * and compared mdr >= mdr_threshold. On a converged parallel direction
 * (grad_parallel_norm == 0.0), binary64 rounding dust such as grad_orth_norm = 3e-12
 * produced mdr = 3.0, forcing a false WEFT_PLATEAU_CAPACITY_LIMIT and capacity mitosis.
 * The gate is now division-free with an explicit WEFT_V2_MDR_ORTH_FLOOR (1e-9) sub-floor
 * dust threshold. Compiles with: gcc -O2 -std=c11 -Wall -Wextra -Werror -o test_weft_v2_mitosis_noise_floor test_weft_v2_mitosis_noise_floor.c
 */

#include <stdio.h>
#include <math.h>
#include "weft_v2_invariants.h"

static int g_failures = 0;

static void check(const char *name,
                  double tension, double max_tension,
                  double heldout_error, double error_floor,
                  double grad_parallel_norm, double grad_orth_norm,
                  double mdr_threshold,
                  bool expected_trigger, weft_plateau_regime_t expected_regime) {
    bool homeostatic = false, excision = false, trigger = false;
    weft_plateau_regime_t regime = WEFT_PLATEAU_NONE;
    bool ok = weft_v2_verify_tension_and_mitosis_trigger(
        tension, max_tension, heldout_error, error_floor,
        grad_parallel_norm, grad_orth_norm, mdr_threshold,
        &homeostatic, &excision, &trigger, &regime);
    if (!ok) {
        printf("FAIL %s: expected structural accept, got fail-closed\n", name);
        g_failures++;
        return;
    }
    if (trigger != expected_trigger || regime != expected_regime) {
        printf("FAIL %s: trigger=%d (want %d) regime=%d (want %d)\n",
               name, trigger, expected_trigger, regime, expected_regime);
        g_failures++;
    } else {
        printf("PASS %s\n", name);
    }
}

int main(void) {
    /* 1. The reported bug: converged parallel gradient, orthogonal binary64 dust.
     *    Old code: mdr = 3e-12 / (0.0 + 1e-12) = 3.0 >= 2.5 -> CAPACITY_LIMIT.
     *    New code: 3e-12 < WEFT_V2_MDR_ORTH_FLOOR -> OPTIMIZER_STUCK, no trigger. */
    check("rounding_dust_does_not_trigger_capacity",
          20.0, 85.0, 1e-6, 1e-9, 0.0, 3.0e-12, WEFT_V2_MDR_TRIGGER_DEFAULT,
          false, WEFT_PLATEAU_OPTIMIZER_STUCK);

    /* 2. Exact zero parallel gradient with a real orthogonal signal still triggers. */
    check("real_orthogonal_signal_at_zero_parallel_triggers",
          20.0, 85.0, 1e-6, 1e-9, 0.0, 1e-3, WEFT_V2_MDR_TRIGGER_DEFAULT,
          true, WEFT_PLATEAU_CAPACITY_LIMIT);

    /* 3. Small parallel gradient with real orthogonal signal triggers. */
    check("real_orthogonal_signal_small_parallel_triggers",
          20.0, 85.0, 1e-6, 1e-9, 1e-4, 1e-2, WEFT_V2_MDR_TRIGGER_DEFAULT,
          true, WEFT_PLATEAU_CAPACITY_LIMIT);

    /* 4. Small parallel gradient with insufficient orthogonal signal stays stuck. */
    check("insufficient_orthogonal_signal_does_not_trigger",
          20.0, 85.0, 1e-6, 1e-9, 1e-4, 1e-4, WEFT_V2_MDR_TRIGGER_DEFAULT,
          false, WEFT_PLATEAU_OPTIMIZER_STUCK);

    /* 5. Orthogonal signal exactly at the dust floor still triggers (floor is inclusive). */
    check("orthogonal_signal_at_floor_triggers",
          20.0, 85.0, 1e-6, 1e-9, 0.0, 1e-9, WEFT_V2_MDR_TRIGGER_DEFAULT,
          true, WEFT_PLATEAU_CAPACITY_LIMIT);

    /* 6. Orthogonal signal just below the dust floor never triggers. */
    check("orthogonal_signal_below_floor_does_not_trigger",
          20.0, 85.0, 1e-6, 1e-9, 0.0, 9.9e-10, WEFT_V2_MDR_TRIGGER_DEFAULT,
          false, WEFT_PLATEAU_OPTIMIZER_STUCK);

    /* 7. Task at ceiling wins over everything. */
    check("task_ceiling_short_circuits",
          20.0, 85.0, 1e-10, 1e-9, 0.0, 1e-3, WEFT_V2_MDR_TRIGGER_DEFAULT,
          false, WEFT_PLATEAU_TASK_CEILING);

    /* 8. Excision is a structural fail-closed verdict by contract: the function
     *    returns false with trigger=false and regime=NONE; nothing mitogenic. */
    {
        bool homeostatic = false, excision = false, trigger = true;
        weft_plateau_regime_t regime = WEFT_PLATEAU_CAPACITY_LIMIT;
        bool ok = weft_v2_verify_tension_and_mitosis_trigger(
            90.0, 85.0, 1e-6, 1e-9, 0.0, 1e-3, WEFT_V2_MDR_TRIGGER_DEFAULT,
            &homeostatic, &excision, &trigger, &regime);
        if (ok || trigger || regime != WEFT_PLATEAU_NONE || !excision) {
            printf("FAIL excision_fail_closed: ok=%d trigger=%d regime=%d excision=%d\n",
                   ok, trigger, regime, excision);
            g_failures++;
        } else {
            printf("PASS excision_fail_closed\n");
        }
    }

    /* 9. Large parallel gradient disengages the gate entirely (task progressing). */
    check("large_parallel_gradient_disengages_gate",
          20.0, 85.0, 1e-6, 1e-9, 1e-1, 1e-2, WEFT_V2_MDR_TRIGGER_DEFAULT,
          false, WEFT_PLATEAU_NONE);

    /* 10. What the old code would have flagged at threshold 2.5 with parallel = 0.
     *     A dust orth of exactly 1e-12 is below the floor; no mitosis. */
    check("dust_1e_minus_12_never_triggers",
          20.0, 85.0, 1e-6, 1e-9, 0.0, 1.0e-12, WEFT_V2_MDR_TRIGGER_DEFAULT,
          false, WEFT_PLATEAU_OPTIMIZER_STUCK);

    if (g_failures != 0) {
        printf("FAIL: %d check(s) failed\n", g_failures);
        return 1;
    }
    printf("OK: all MDR noise-floor checks passed\n");
    return 0;
}
