# I3: Invariant safety gate and conformance corpus

Status: implemented predicate contract and cross-language conformance profile,
document version 1. Tracks issue #42. Producer: C2 (`weft/runtime/invariants/`).
Consumers: C1 (`weft/runtime/plasm/`), C3 (`weft/runtime/ic/`), C5
(`weft/runtime/gateway/`), and C7 (`site/assets/js/invariant-gate.js`).

## Scope

Interface I3 specifies the pure safety predicates shared across the Python
reference (`invariants.py`), the standalone C11 header (`weft_invariants.h`),
and the browser JavaScript port (`site/assets/js/invariant-gate.js`), together
with the shared JSON conformance corpus in
[`weft/runtime/invariants/vectors.json`](../../weft/runtime/invariants/vectors.json).

All three implementations are tested directly against `vectors.json` in CI:
Python and C11 execute all 25 cases (13 weight-update, 8 tension, 4 royalty),
and the browser port executes all 9 weight-update cases.

## Shared constants (`WEFT-INVARIANTS/1.0`)

| Constant | Value | Meaning |
|---|---:|---|
| `R_INVARIANT` | `120.0` | Default maximum Frobenius distance $\lVert W_{\text{cand}} - W_{\text{base}} \rVert_F$ |
| `TENSION_MAX` | `85.0` | Maximum accepted organizational or cellular tension |
| `HOMEOSTATIC_TENSION_MIN` | `15.0` | Lower inclusive bound of homeostatic tension band |
| `HOMEOSTATIC_TENSION_MAX` | `35.0` | Upper inclusive bound of homeostatic tension band |
| `ROYALTY_UPSTREAM_BPS` | `1500` | Upstream / excision share in basis points (`15%`) |
| `ROYALTY_WEAVER_BPS` | `8500` | Weaver / creator share in basis points (`85%`) |

## Predicate 1: Baseline-relative weight update gate

Given baseline array $W_{\text{base}}$, candidate array $W_{\text{cand}}$,
radius $R$, remaining metabolic budget $b$, and step cost $c$, evaluation
proceeds in strict precondition order:

1. **Parameter finiteness (`non_finite_parameters`)**: if any of $b, c, R$ is
   `NaN` or `±Inf`, reject with `distance = +Inf`.
2. **Sign preconditions (`non_positive_budget_or_cost`)**: if $b \le 0$,
   $c \le 0$, or $R < 0$, reject with `distance = +Inf` and deficit budget
   $b - c$.
3. **Budget sufficiency (`insufficient_metabolic_budget`)**: if $b < c$, reject
   with `distance = +Inf` and deficit budget $b - c$.
4. **Shape and non-empty check (`shape_mismatch`)**: if lengths differ or length
   is `0` (or a pointer is `NULL` in C11), reject with `distance = +Inf` and
   unchanged budget $b$.
5. **Element finiteness (`non_finite_weights`)**: if any element of
   $W_{\text{base}}$ or $W_{\text{cand}}$ is `NaN` or `±Inf`, reject with
   `distance = +Inf` and unchanged budget $b$.
6. **Baseline Frobenius bound (`baseline_distance_exceeded` vs. `ok`)**: compute
   $d = \sqrt{\sum_i (W_{\text{cand},i} - W_{\text{base},i})^2}$. If $d$ is
   non-finite, reject (`non_finite_weights`, budget $b$). If $d > R$, reject
   (`baseline_distance_exceeded`, budget $b$). If $d \le R$ (inclusive boundary),
   accept with `distance = d` and `remaining_budget = b - c`.

### Numeric representation across languages

- **Python (`invariants.py`)** and **JavaScript (`invariant-gate.js`)** evaluate
  scalar list inputs in IEEE-754 binary64 (`float` / `Number`); Python's PyTorch
  fast path uses the input tensor dtype.
- **C11 (`weft_invariants.h`)** accepts `const float *` (IEEE-754 binary32),
  accumulates squared differences in `double`, and casts `sqrt(sq_sum)` and
  `*metabolic_budget` to `float`. Conformance tolerances in `test_invariants_c.c`
  (`1e-5f`) reflect single-precision input representation.

## Predicate 2: Tension bound

Given scalar `tension` $t$ and upper bound `max_tension` $M$ (default `85.0`):

- If $t$ or $M$ is `NaN`, `±Inf`, or $t < 0.0$: `accepted = false`,
  `homeostatic = false`, `excision_triggered = true`.
- Otherwise `accepted = (t <= M)`, `homeostatic = (15.0 <= t <= 35.0)`, and
  `excision_triggered = !accepted`. Both `0.0`, `15.0`, `35.0`, and `85.0` are
  inclusive boundaries.

## Predicate 3: Integer wei split and cross-codebase rounding note

In C2 (`compute_royalty_split` in `invariants.py` and `weft_royalty_split_u64`
in `weft_invariants.h`), integer division floors the `15%` upstream share first
and assigns any sub-basis-point remainder (`dust`) to the `85%` weaver share:

$$
\text{upstream\_wei} = \lfloor (\text{gross\_wei} \times 1500) / 10000 \rfloor,
\qquad
\text{weaver\_wei} = \text{gross\_wei} - \text{upstream\_wei}.
$$

At `gross_wei = 1` (`single_wei_dust` in `vectors.json`), C2 yields
`upstream_wei = 0, weaver_wei = 1`; at `gross_wei = 1001` (`odd_amount_rounding`),
C2 yields `upstream_wei = 150, weaver_wei = 851`. Exact conservation
`upstream_wei + weaver_wei == gross_wei` holds for every unsigned input
(assuming `gross_wei * upstream_bps` does not overflow `uint64_t` in C11).

**Known discrepancy with C4 (`WeftTokenTissue.sol`):** `executeExcisionValve` in
[`weft/runtime/ledger/WeftTokenTissue.sol`](../../weft/runtime/ledger/WeftTokenTissue.sol)
computes `creatorShare = (value * 8500) / 10000` and
`burnShare = value - creatorShare`, flooring the `85%` creator share rather than
the `15%` burn/upstream share. On non-multiples of `20` wei (for example
`value = 1` -> `creatorShare = 0, burnShare = 1`, or `value = 1001` ->
`creatorShare = 850, burnShare = 151`), C2 and C4 differ by `1` wei on remainder
assignment while both conserve total supply. Changing the Solidity contract is
intentionally out of scope for I3; reconciling remainder direction between C2
and C4 requires an explicit C4/I6 economics decision.

## Conformance commands

Run from the repository root:

```sh
python3 -m unittest discover -s weft/runtime/invariants -p 'test_*.py'
node --test weft/runtime/aywa/test_invariant_gate.mjs
```
