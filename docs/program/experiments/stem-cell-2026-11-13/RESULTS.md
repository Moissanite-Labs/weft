# Completed Astra controller pilot

The registered loop completed eight Astra calls and evaluated 32 valid typed children. Concrete execution, selection and allocation checks passed. The important failure is generalization: the second quiet generation improved validation cost but worsened held-out cost in both source seeds. Formal legality and correct selection arithmetic did not establish future usefulness.

## Quiet-demand results

Lower integer cost is better. Generation-one teacher values are also the unchanged parents for generation two.

| Seed | Root | Fixed hand | G1 teacher / G2 parent | G2 teacher final | G1 random selection | G2 random selection |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 171 | 2104 | 1307 | 1149 | 1216 | 1184 | 1149 |
| 293 | 1830 | 998 | 884 | 949 | 1142 | 884 |

Final quiet controllers reduced cost versus the original root by 42.21% and 48.14%, and beat the fixed hand controller. However, generation two raised held-out cost by 67 (5.83%) and 65 (7.35%) relative to its teacher-selected parent. Validation cost moved in the opposite direction: 409→401 and 466→438. The marginal generation-two random control retained that better parent in both seeds.

This is an observed overfitting pattern in two exploratory cases, without a population-significance claim. The random comparator starts from the actual teacher parent each generation. It is not an independent cumulative evolutionary lineage.

## Differentiation, allocation and limits

Generation one selected the same quiet genome in both seeds: gain 1/1, deadband 1, bias 0 and caps 1/1. Generation two changed bias to +1 for seed 171 and −1 for seed 293. Those changes passed validation selection but caused the held-out regressions above.

Urgent lineages retained the original root through both generations. Their held-out costs remained 1813 and 1058, compared with 2376 and 1605 for the fixed hand control. Applying the final quiet controllers to urgent demand cost 3128 and 2184. The quiet specialization therefore did not transfer broadly across demand regimes.

Each final colony contained the unchanged reserved root plus three quiet copies. Actual dispatch traces were recorded and checked. Copies repeat a selected controller, with episodes starting from the registered initial state.

This demonstrates bounded allocation and execution, without cooperation, throughput improvement or arbitrary persistent-state cloning. Demand weights never reversed within a lineage, so recovery after an ecological reversal was not tested.

## Verification and raw record

All 178 official proof records reported acceptance with empty concrete axiom sets: 80 training/validation, 18 lifecycle, 48 held-out and 32 dispatch records. These certify the exact finite integer claims and supplied score/eligibility records. Python input binding, storage, actual compiler execution, hardware and the task specification remain trusted boundaries.

The independent audit re-derived all 48 held-out and 32 dispatch trajectories, covering 6,656 integer steps, and checked retained proof/hash bindings. It did not independently recompile all 178 certificates. The archived replay passed hash and arithmetic checks for all eight selections. RESULTS-REVIEW.md and INDEPENDENT-RESULTS.json retain the detailed audit.

The registration commit is `f2a72fdc0fa8b859df6ccc98e41d0420e86cddbf`, published before paid calls. It contains four concrete generation-one requests and the procedure for generating later requests from validation feedback.

data/ retains all eight prepared/wire/response records, candidates, selection lock, proof source/compiler outputs, lifecycle decisions, held-out results, resource observations and actual colony dispatch.

## Usage and post-registration reporting

The eight completed responses reported 11,045 input tokens, including 11,021 cache-write tokens and zero cached reads, plus 4,259 output tokens including 2,688 reasoning tokens. Observable message text and usage counts were retained. Internal reasoning content and credentials were excluded.

The standard API rate estimate is **$0.3509525**, using $10/M ordinary input, $1/M cache reads, $12.50/M default cache writes and $50/M output. The conservative reservation guard totaled $4.304825 within the registered $5 limit. Neither figure is an invoice or an account-balance statement. Coding-agent and subagent compute are excluded.

Rates are attributed to the [official Astra model page](https://developers.openai.com/api/docs/models/gpt-6-astra).

After registration, analyze_results.py was corrected only to account for the provider's cache-write usage field. The five registered experiment sources, configuration and episode/request rules were unchanged.

POST-REGISTRATION-CHANGES.json records the report-only code change, command-path normalization and narrowly scoped scanner false-positive handling. PREREG-MANIFEST.json remains the immutable initial-snapshot index. FINAL-MANIFEST.json describes this completed archive.
