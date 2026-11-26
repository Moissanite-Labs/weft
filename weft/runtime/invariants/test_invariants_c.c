#include "weft_invariants.h"
#include <ctype.h>
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
 * Direct JSON conformance runner for weft/runtime/invariants/vectors.json (#42),
 * optional 256-vector C11-vs-Python differential stream, and one direct C-only
 * Zeno sub-ULP loop that cannot be expressed as a single JSON vector.
 */

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
            if (derr > 1e-9) {
                fprintf(stderr, "Tolerance mismatch at vec %u: derr=%.3e\n",
                        h.vec_id, derr);
                free(bw); free(cw); free(mask);
                fclose(fp);
                return 1;
            }
        }
        if (bud != h.expected_budget_out) {
            fprintf(stderr, "Budget mismatch at vec %u: bud=%.9g exp_bud=%.9g cost=%.9g ok=%d\n",
                    h.vec_id, bud, h.expected_budget_out, h.step_cost, (int)ok);
            free(bw); free(cw); free(mask);
            fclose(fp);
            return 1;
        }
        free(bw);
        free(cw);
        free(mask);
    }
    fclose(fp);
    printf("C_DIFFERENTIAL_PASS count=%u max_abs_dist_err=%.3e tol=1.000e-09\n", count, max_abs_dist_err);
    return 0;
}

#define MAX_ARRAY_LEN 64
#define MAX_STR_LEN 128

typedef struct {
    const char *src;
    size_t pos;
    size_t len;
} JsonCursor;

static void fail_at(const JsonCursor *c, const char *msg) {
    fprintf(stderr, "JSON/vector error near byte %zu: %s\n", c ? c->pos : 0U, msg);
    exit(1);
}

static void skip_ws(JsonCursor *c) {
    while (c->pos < c->len && isspace((unsigned char)c->src[c->pos])) {
        c->pos++;
    }
}

static void expect_char(JsonCursor *c, char ch) {
    skip_ws(c);
    if (c->pos >= c->len || c->src[c->pos] != ch) {
        char buf[64];
        snprintf(buf, sizeof(buf), "expected '%c'", ch);
        fail_at(c, buf);
    }
    c->pos++;
}

static bool consume_char_if(JsonCursor *c, char ch) {
    skip_ws(c);
    if (c->pos < c->len && c->src[c->pos] == ch) {
        c->pos++;
        return true;
    }
    return false;
}

static void parse_string(JsonCursor *c, char *out, size_t cap) {
    expect_char(c, '"');
    size_t n = 0;
    while (c->pos < c->len && c->src[c->pos] != '"') {
        char ch = c->src[c->pos++];
        if (ch == '\\') {
            if (c->pos >= c->len) fail_at(c, "unterminated escape");
            ch = c->src[c->pos++];
        }
        if (n + 1 >= cap) fail_at(c, "string exceeds buffer");
        out[n++] = ch;
    }
    expect_char(c, '"');
    out[n] = '\0';
}

static bool parse_bool(JsonCursor *c) {
    skip_ws(c);
    if (c->pos + 4 <= c->len && strncmp(c->src + c->pos, "true", 4) == 0) {
        c->pos += 4;
        return true;
    }
    if (c->pos + 5 <= c->len && strncmp(c->src + c->pos, "false", 5) == 0) {
        c->pos += 5;
        return false;
    }
    fail_at(c, "expected boolean literal");
    return false;
}

static double parse_number_or_special(JsonCursor *c) {
    skip_ws(c);
    if (c->pos < c->len && c->src[c->pos] == '"') {
        char tok[32];
        parse_string(c, tok, sizeof(tok));
        if (strcmp(tok, "NaN") == 0) return NAN;
        if (strcmp(tok, "Inf") == 0) return INFINITY;
        if (strcmp(tok, "-Inf") == 0) return -INFINITY;
        fail_at(c, "unknown string float token");
    }
    char *endptr = NULL;
    double val = strtod(c->src + c->pos, &endptr);
    if (endptr == c->src + c->pos) fail_at(c, "expected number");
    c->pos = (size_t)(endptr - c->src);
    return val;
}

static uint64_t parse_u64(JsonCursor *c) {
    skip_ws(c);
    if (c->pos < c->len && c->src[c->pos] == '-') fail_at(c, "negative uint64");
    char *endptr = NULL;
    unsigned long long val = strtoull(c->src + c->pos, &endptr, 10);
    if (endptr == c->src + c->pos) fail_at(c, "expected uint64");
    c->pos = (size_t)(endptr - c->src);
    return (uint64_t)val;
}

static size_t parse_u8_array(JsonCursor *c, uint8_t *out, size_t cap) {
    expect_char(c, '[');
    if (consume_char_if(c, ']')) {
        return 0;
    }
    size_t count = 0;
    for (;;) {
        if (count >= cap) fail_at(c, "u8 array exceeds MAX_ARRAY_LEN");
        uint64_t v = parse_u64(c);
        if (v > 1U) fail_at(c, "locked_mask entry must be 0 or 1");
        out[count++] = (uint8_t)v;
        if (consume_char_if(c, ',')) continue;
        expect_char(c, ']');
        break;
    }
    return count;
}

static size_t parse_float_array(JsonCursor *c, float *out, size_t cap) {
    expect_char(c, '[');
    if (consume_char_if(c, ']')) {
        return 0;
    }
    size_t count = 0;
    for (;;) {
        if (count >= cap) fail_at(c, "float array exceeds MAX_ARRAY_LEN");
        out[count++] = (float)parse_number_or_special(c);
        if (consume_char_if(c, ',')) continue;
        expect_char(c, ']');
        break;
    }
    return count;
}

static void assert_close_f32(const char *vec_name, const char *field, float got, double expected, float tol) {
    if (isnan(expected)) {
        if (!isnan(got)) {
            fprintf(stderr, "[%s] %s: expected NaN, got %.9g\n", vec_name, field, (double)got);
            exit(1);
        }
        return;
    }
    if (isinf(expected)) {
        if (!isinf(got) || ((expected > 0.0) != (got > 0.0f))) {
            fprintf(stderr, "[%s] %s: expected Inf, got %.9g\n", vec_name, field, (double)got);
            exit(1);
        }
        return;
    }
    if (!isfinite(got) || fabsf(got - (float)expected) > tol) {
        fprintf(stderr, "[%s] %s: expected %.9g, got %.9g\n", vec_name, field, expected, (double)got);
        exit(1);
    }
}

static void check_constants_object(JsonCursor *c) {
    expect_char(c, '{');
    unsigned seen = 0;
    while (!consume_char_if(c, '}')) {
        char key[MAX_STR_LEN];
        parse_string(c, key, sizeof(key));
        expect_char(c, ':');
        if (strcmp(key, "R_INVARIANT") == 0) {
            assert_close_f32("constants", key, WEFT_R_INVARIANT_DEFAULT, parse_number_or_special(c), 1e-6f);
            seen |= 1U << 0;
        } else if (strcmp(key, "TENSION_MAX") == 0) {
            assert_close_f32("constants", key, WEFT_TENSION_MAX_DEFAULT, parse_number_or_special(c), 1e-6f);
            seen |= 1U << 1;
        } else if (strcmp(key, "HOMEOSTATIC_TENSION_MIN") == 0) {
            assert_close_f32("constants", key, WEFT_HOMEOSTATIC_MIN_DEFAULT, parse_number_or_special(c), 1e-6f);
            seen |= 1U << 2;
        } else if (strcmp(key, "HOMEOSTATIC_TENSION_MAX") == 0) {
            assert_close_f32("constants", key, WEFT_HOMEOSTATIC_MAX_DEFAULT, parse_number_or_special(c), 1e-6f);
            seen |= 1U << 3;
        } else if (strcmp(key, "ROYALTY_UPSTREAM_BPS") == 0) {
            uint64_t v = parse_u64(c);
            if (v != WEFT_ROYALTY_UPSTREAM_BPS) fail_at(c, "ROYALTY_UPSTREAM_BPS mismatch");
            seen |= 1U << 4;
        } else if (strcmp(key, "ROYALTY_WEAVER_BPS") == 0) {
            uint64_t v = parse_u64(c);
            if (v + WEFT_ROYALTY_UPSTREAM_BPS != 10000ULL) fail_at(c, "ROYALTY_WEAVER_BPS mismatch");
            seen |= 1U << 5;
        } else {
            fail_at(c, "unexpected constant key");
        }
        consume_char_if(c, ',');
    }
    if (seen != 0x3FU) fail_at(c, "missing required constant in constants block");
}

static size_t run_weight_vectors(JsonCursor *c) {
    expect_char(c, '[');
    if (consume_char_if(c, ']')) return 0;
    size_t count = 0;
    for (;;) {
        expect_char(c, '{');
        char name[MAX_STR_LEN] = "";
        char expected_reason[MAX_STR_LEN] = "";
        float base[MAX_ARRAY_LEN];
        float cand[MAX_ARRAY_LEN];
        size_t base_len = 0, cand_len = 0;
        float r_inv = 0.0f, budget = 0.0f, cost = 0.0f;
        bool expected_accepted = false;
        double expected_distance = 0.0;
        double expected_rem = 0.0;
        uint8_t locked_mask[MAX_ARRAY_LEN];
        size_t mask_len = 0;
        bool has_locked_mask = false;

        while (!consume_char_if(c, '}')) {
            char key[MAX_STR_LEN];
            parse_string(c, key, sizeof(key));
            expect_char(c, ':');
            if (strcmp(key, "name") == 0) {
                parse_string(c, name, sizeof(name));
            } else if (strcmp(key, "baseline") == 0) {
                base_len = parse_float_array(c, base, MAX_ARRAY_LEN);
            } else if (strcmp(key, "candidate") == 0) {
                cand_len = parse_float_array(c, cand, MAX_ARRAY_LEN);
            } else if (strcmp(key, "locked_mask") == 0) {
                mask_len = parse_u8_array(c, locked_mask, MAX_ARRAY_LEN);
                has_locked_mask = true;
            } else if (strcmp(key, "r_invariant") == 0) {
                r_inv = (float)parse_number_or_special(c);
            } else if (strcmp(key, "budget") == 0) {
                budget = (float)parse_number_or_special(c);
            } else if (strcmp(key, "cost") == 0) {
                cost = (float)parse_number_or_special(c);
            } else if (strcmp(key, "expected_accepted") == 0) {
                expected_accepted = parse_bool(c);
            } else if (strcmp(key, "expected_distance") == 0) {
                expected_distance = parse_number_or_special(c);
            } else if (strcmp(key, "expected_remaining_budget") == 0) {
                expected_rem = parse_number_or_special(c);
            } else if (strcmp(key, "expected_reason") == 0) {
                parse_string(c, expected_reason, sizeof(expected_reason));
            } else {
                fail_at(c, "unexpected key in weight_update_vectors");
            }
            consume_char_if(c, ',');
        }

        if (base_len != cand_len) {
            fprintf(stderr, "[%s] C11 signature takes single length, got %zu vs %zu\n", name, base_len, cand_len);
            exit(1);
        }
        if (has_locked_mask && mask_len != base_len) {
            fprintf(stderr, "[%s] locked_mask length %zu does not match weights %zu\n", name, mask_len, base_len);
            exit(1);
        }
        float mut_budget = budget;
        float got_dist = -1.0f;
        bool got_ok = has_locked_mask
            ? weft_verify_weight_update_safety_masked(
                  base, cand, locked_mask, base_len, r_inv, &mut_budget, cost, &got_dist)
            : weft_verify_weight_update_safety(
                  base, cand, base_len, r_inv, &mut_budget, cost, &got_dist);
        if (got_ok != expected_accepted) {
            fprintf(stderr, "[%s] accepted mismatch: expected %d, got %d (reason=%s)\n",
                    name, (int)expected_accepted, (int)got_ok, expected_reason);
            exit(1);
        }
        assert_close_f32(name, "distance", got_dist, expected_distance, 1e-5f);
        if (!isnan(expected_rem)) {
            assert_close_f32(name, "remaining_budget", mut_budget, expected_rem, 1e-5f);
        }
        count++;
        if (consume_char_if(c, ',')) continue;
        expect_char(c, ']');
        break;
    }
    return count;
}

static size_t run_tension_vectors(JsonCursor *c) {
    expect_char(c, '[');
    if (consume_char_if(c, ']')) return 0;
    size_t count = 0;
    for (;;) {
        expect_char(c, '{');
        char name[MAX_STR_LEN] = "";
        float tension = 0.0f, max_tension = 0.0f;
        bool exp_acc = false, exp_homeo = false, exp_exc = false;

        while (!consume_char_if(c, '}')) {
            char key[MAX_STR_LEN];
            parse_string(c, key, sizeof(key));
            expect_char(c, ':');
            if (strcmp(key, "name") == 0) {
                parse_string(c, name, sizeof(name));
            } else if (strcmp(key, "tension") == 0) {
                tension = (float)parse_number_or_special(c);
            } else if (strcmp(key, "max_tension") == 0) {
                max_tension = (float)parse_number_or_special(c);
            } else if (strcmp(key, "expected_accepted") == 0) {
                exp_acc = parse_bool(c);
            } else if (strcmp(key, "expected_homeostatic") == 0) {
                exp_homeo = parse_bool(c);
            } else if (strcmp(key, "expected_excision") == 0) {
                exp_exc = parse_bool(c);
            } else {
                fail_at(c, "unexpected key in tension_vectors");
            }
            consume_char_if(c, ',');
        }

        bool got_homeo = false, got_exc = false;
        bool got_acc = weft_verify_tension_bound(tension, max_tension, &got_homeo, &got_exc);
        if (got_acc != exp_acc || got_homeo != exp_homeo || got_exc != exp_exc) {
            fprintf(stderr, "[%s] tension mismatch: got (%d,%d,%d), expected (%d,%d,%d)\n",
                    name, (int)got_acc, (int)got_homeo, (int)got_exc,
                    (int)exp_acc, (int)exp_homeo, (int)exp_exc);
            exit(1);
        }
        count++;
        if (consume_char_if(c, ',')) continue;
        expect_char(c, ']');
        break;
    }
    return count;
}

static size_t run_royalty_vectors(JsonCursor *c) {
    expect_char(c, '[');
    if (consume_char_if(c, ']')) return 0;
    size_t count = 0;
    for (;;) {
        expect_char(c, '{');
        char name[MAX_STR_LEN] = "";
        uint64_t gross = 0, bps = 0, exp_up = 0, exp_wv = 0;

        while (!consume_char_if(c, '}')) {
            char key[MAX_STR_LEN];
            parse_string(c, key, sizeof(key));
            expect_char(c, ':');
            if (strcmp(key, "name") == 0) {
                parse_string(c, name, sizeof(name));
            } else if (strcmp(key, "gross_wei") == 0) {
                gross = parse_u64(c);
            } else if (strcmp(key, "upstream_bps") == 0) {
                bps = parse_u64(c);
            } else if (strcmp(key, "expected_upstream_wei") == 0) {
                exp_up = parse_u64(c);
            } else if (strcmp(key, "expected_weaver_wei") == 0) {
                exp_wv = parse_u64(c);
            } else {
                fail_at(c, "unexpected key in royalty_vectors");
            }
            consume_char_if(c, ',');
        }

        uint64_t got_up = 0, got_wv = 0;
        weft_royalty_split_u64(gross, bps, &got_up, &got_wv);
        if (got_up != exp_up || got_wv != exp_wv || got_up + got_wv != gross) {
            fprintf(stderr, "[%s] royalty mismatch: got (%llu,%llu), expected (%llu,%llu)\n",
                    name,
                    (unsigned long long)got_up, (unsigned long long)got_wv,
                    (unsigned long long)exp_up, (unsigned long long)exp_wv);
            exit(1);
        }
        count++;
        if (consume_char_if(c, ',')) continue;
        expect_char(c, ']');
        break;
    }
    return count;
}

static int run_zeno_sub_ulp_direct_checks(void) {
    float base[4] = {1.0f, 2.0f, 3.0f, 4.0f};
    float cand[4] = {1.1f, 2.1f, 3.1f, 4.1f};
    float budget = 100.0f;
    float sub_ulp_cost = 3.0e-6f;
    for (int s = 0; s < 1000; ++s) {
        float prev = budget;
        float dist = 0.0f;
        bool ok = weft_verify_weight_update_safety(base, cand, 4, 120.0f, &budget, sub_ulp_cost, &dist);
        if (!ok || !(budget < prev)) {
            return 1;
        }
    }
    return 0;
}

static bool path_looks_like_json(const char *path) {
    FILE *fp = fopen(path, "rb");
    if (fp == NULL) {
        return false;
    }
    int ch = fgetc(fp);
    fclose(fp);
    return ch == '{';
}

static int run_vectors_from_json(const char *path) {
    FILE *fp = fopen(path, "rb");
    if (fp == NULL) {
        fprintf(stderr, "Unable to open conformance vectors file: %s\n", path);
        return 1;
    }
    if (fseek(fp, 0, SEEK_END) != 0) {
        fclose(fp);
        return 1;
    }
    long fsize = ftell(fp);
    if (fsize <= 0 || fseek(fp, 0, SEEK_SET) != 0) {
        fclose(fp);
        return 1;
    }
    char *buf = (char *)malloc((size_t)fsize + 1U);
    if (buf == NULL) {
        fclose(fp);
        return 1;
    }
    size_t nread = fread(buf, 1U, (size_t)fsize, fp);
    fclose(fp);
    if (nread != (size_t)fsize) {
        free(buf);
        return 1;
    }
    buf[nread] = '\0';

    JsonCursor cur = {buf, 0U, nread};
    expect_char(&cur, '{');

    size_t n_weight = 0, n_tension = 0, n_royalty = 0;
    bool saw_schema = false, saw_constants = false;

    while (!consume_char_if(&cur, '}')) {
        char key[MAX_STR_LEN];
        parse_string(&cur, key, sizeof(key));
        expect_char(&cur, ':');
        if (strcmp(key, "schema") == 0) {
            char schema[MAX_STR_LEN];
            parse_string(&cur, schema, sizeof(schema));
            if (strcmp(schema, "WEFT-INVARIANTS/1.0") != 0) {
                fail_at(&cur, "unexpected schema version");
            }
            saw_schema = true;
        } else if (strcmp(key, "constants") == 0) {
            check_constants_object(&cur);
            saw_constants = true;
        } else if (strcmp(key, "weight_update_vectors") == 0) {
            n_weight = run_weight_vectors(&cur);
        } else if (strcmp(key, "tension_vectors") == 0) {
            n_tension = run_tension_vectors(&cur);
        } else if (strcmp(key, "royalty_vectors") == 0) {
            n_royalty = run_royalty_vectors(&cur);
        } else {
            fail_at(&cur, "unexpected top-level key in vectors.json");
        }
        consume_char_if(&cur, ',');
    }

    free(buf);
    if (!saw_schema || !saw_constants || n_weight == 0 || n_tension == 0 || n_royalty == 0) {
        fprintf(stderr, "Incomplete vector sections in %s\n", path);
        return 1;
    }

    printf("C_INVARIANTS_VECTORS_PASS weight=%zu tension=%zu royalty=%zu total=%zu\n",
           n_weight, n_tension, n_royalty, n_weight + n_tension + n_royalty);
    return run_zeno_sub_ulp_direct_checks();
}

int main(int argc, char **argv) {
    if (argc == 2) {
        if (path_looks_like_json(argv[1])) {
            return run_vectors_from_json(argv[1]);
        }
        return run_differential_stream(argv[1]);
    }
    if (argc == 1) {
        return run_vectors_from_json("weft/runtime/invariants/vectors.json");
    }
    fprintf(stderr, "usage: %s [vectors.json|diff_vectors.bin]\n", argv[0] ? argv[0] : "test_invariants_c");
    return 1;
}
