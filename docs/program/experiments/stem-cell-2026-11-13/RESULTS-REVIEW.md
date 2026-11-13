# Independent results review

Reviewed by gpt-forge (Astra), 2026-11-13, after all eight proposal opportunities were locked and the final results file was complete. No additional model calls, selection changes or solver changes were made. The accompanying `INDEPENDENT-RESULTS.json` records the exact input-results hash, independently computed comparisons and artifact checks.

**The pilot demonstrates demand-specific controller differentiation and checked finite execution. It also shows a clear failure of the second refinement step: validation improved, but heldout quiet-demand cost worsened in both source seeds.** Formal validity did not imply generalization or improvement.

## Heldout performance and the failed second refinement

Costs are summed over the same eight heldout episodes per seed and demand. lower is better. “G1 parent” is the unchanged parent offered to generation two, and therefore the actual generation-one teacher selection.

| Seed | Demand | Root | Fixed hand policy | Teacher G1 parent | Teacher G2 final | Random selection at G2 |
|---|---|---:|---:|---:|---:|---:|
| 171 | Quiet | 2104 | 1307 | 1149 | 1216 | 1149 |
| 293 | Quiet | 1830 | 998 | 884 | 949 | 884 |
| 171 | Urgent | 1813 | 2376 | 1813 | 1813 | 1813 |
| 293 | Urgent | 1058 | 1605 | 1058 | 1058 | 1058 |

Both first-generation quiet selections chose gain 1, deadband 1, zero bias and both caps reduced from 2 to 1. Generation two changed only the bias: +1 for seed 171 and −1 for seed 293. Validation cost improved from 409 to 401 and from 466 to 438, respectively. Heldout cost instead rose by 67 (5.83%) and 65 (7.35%).

This is evidence consistent with adaptive validation overfitting in this small sample. it is not a population-level estimate of the effect of refinement.

The final quiet policies still beat the original root by 42.21% and 48.14%, and beat the fixed hand policy on both seeds. Those improvements must not hide the generation-two regression. The matched generation-two random proposal controls retained the unchanged G1 parent in both quiet branches and consequently beat the final teacher selections.

These controls start from the teacher-selected parent. they are local proposal comparisons, not independent two-generation random evolutionary lineages.

At generation one, teacher-selected quiet policies had heldout costs 1149/884 versus 1184/1142 for the corresponding random selections. At the final generation, comparison against those generation-one random selections is mixed: 1216 is worse than 1184 for seed 171, while 949 is better than 1142 for seed 293.

The experiment therefore supports no general claim that additional teacher rounds outperform random proposals.

Urgent branches retained the root at both generations. This is a useful preserved negative result: the teacher did not discover a validated improvement there. The fixed hand policy was worse under urgent demand.

## Crossover supports specificity, not universal improvement

Targets, urgency signals and initial states are paired across the two demand conditions. Only the tracking-versus-action cost weights differ.

| Seed | Quiet policy on quiet demand | Urgent/root policy on quiet demand | Quiet policy on urgent demand | Urgent/root policy on urgent demand |
|---|---:|---:|---:|---:|
| 171 | 1216 | 2104 | 3128 | 1813 |
| 293 | 949 | 1830 | 2184 | 1058 |

Within each demand's fixed objective, the matching policy has lower cost: quiet policies gain 888/881 cost units under quiet demand, while keeping the urgent/root policy avoids 1315/1126 units of extra urgent cost. This is descriptive evidence of specialization in the tested paired environments.

It does not identify a general mechanism of model reasoning. each branch receives a separate stochastic teacher response, and there are only two independent source seeds.

The declared allocation rule assigned three quiet copies and retained one immutable root in each colony. Urgent dispatch fell back to that root. All copies within a branch use the same genome, and episodes start at the registered initial state. These records demonstrate bounded allocation and actual checked dispatch, not measured throughput benefits, ecological emergence or arbitrary persistent-state cloning.

## Exactness and evidence audit

All 32 teacher children were eligible. there were no within-request duplicate children. There were four selected teacher changes: quiet generations one and two for each seed. No urgent teacher change was selected.

I independently recomputed action rounding, clipping, state transitions, per-step and total costs, movement and tracking metrics for all 48 heldout controller records and 32 dispatched episodes, covering 6,656 recorded steps. Every value matched. No anchor, frozen-coordinate, local norm or root norm violation was found in those traces.

I also checked all 178 official proof records, excluding preflight controls:

| Proof class | Records | Accepted with empty concrete axiom set |
|---|---:|---:|
| Parent, fixed, teacher and random train/validation batches | 80 | 80 |
| Selection and allocation lifecycle decisions | 18 | 18 |
| Heldout controller batches | 48 | 48 |
| Actual colony dispatch episodes | 32 | 32 |

For each record, the certificate source hash, canonical request hash, current immutable specification/verifier hash and final compiler axiom report matched. This review inspected retained proof evidence and independently recomputed the heldout/dispatch arithmetic. it did not perform a second compilation of all 178 certificates. The root/runner's separate replay should be reported as its own verification step.

The mathematical claim remains finite and explicit: these concrete policies produced these exact integer trajectories and costs while respecting the registered constraints, and the declared selection/allocation arithmetic checked.

It is not a proof of future generalization, the Python host, compiler execution, API provenance, operating-system scheduling or physical effects. The teacher changed a typed controller genome, not Astra's own weights. Fixed demand branches do not test recovery after demand reversal.

CPU memory-pressure handling does not establish a GPU or performance scaling result.

## Most useful next test

Preserve the final selections as the registered primary result. do not retroactively replace them with G1 because the test favored G1. A next pilot should predeclare a rule for accepting a bias change or stopping refinement, and test it on fresh source and evaluation seeds.

An ordinary finite-policy search reference would also help separate teacher proposal value from the strength of this very small hand-designed policy family.

Neither extension is needed to retain the present useful result: exact constraint checking worked, demand-specific changes helped, and an additional valid refinement nevertheless generalized worse.
