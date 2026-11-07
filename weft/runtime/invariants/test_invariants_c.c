#include "weft_invariants.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>

int main(void) {
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

    printf("C_INVARIANTS_VECTORS_PASS\n");
    return 0;
}
