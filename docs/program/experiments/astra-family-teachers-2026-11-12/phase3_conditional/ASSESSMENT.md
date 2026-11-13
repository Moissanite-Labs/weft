# Phase-three independent assessment

The tool-assisted teacher produced partial conditional behavior improvements, but **no source seed met the complete registered primary criterion on both final distributions (0/3)**. Every selected candidate used ordinary ridge fitting after teacher-directed parameter or hidden-feature changes.

This is evidence about bounded teacher-guided numerical optimization, not successful unaided weight surgery or a preserved new skill meeting the declared threshold.

## Candidate accounting

All48 candidates from12 responses were valid. The fitted category contains47 candidates:19 passed validation and28 were rejected. The manual category contains only1 candidate, which was rejected.

| Source seed | Fitted candidates | Fitted accepted | Fitted rejected | Manual candidates | Manual accepted |
| --- | ---: | ---: | ---: | ---: | ---: |
| 101 | 16 | 5 | 11 | 0 | 0 |
| 211 | 16 | 5 | 11 | 0 | 0 |
| 307 | 15 | 9 | 6 | 1 | 0 |

The manual strata for101 and211 are empty, not failed independent manual trials. The one manual proposal for307 is labeled `manual_sixty_percent_previous_low_hazard_patch` and scales a previous patch whose fitted result was available in feedback.

The operator-based classification is accurate for the current proposal, but it does not remove that optimizer-derived information. The unchanged manual selections must not be presented as a meaningful randomized manual-versus-fitting comparison or a general failure of unaided editing.

## Held-out outcome

The combined selections reduce IID paired-context contrast error by10.34%,13.92% and20.38%, versus2.82%,2.92% and7.02% for the deterministic readout-only ridge grid. The corresponding shifted contrast improvements are9.39%,12.12% and19.73%. These are real conditional-response changes measured by flipping the context sign while holding other inputs fixed.

The full primary criterion is stricter: at least10% improvement in left-context active error, right-context active error and paired contrast, plus retention, on both final distributions. Seed101 misses the right-context threshold on IID and several thresholds under shift. Seed211 misses the right-context threshold on both.

Seed307 passes the IID criterion, but shifted left improvement is9.005% and protected-context drift is0.00101724 against0.001. The shifted failure therefore concerns both acquisition magnitude and retention, not drift alone.

All selected sources preserve the registered secondary criteria on IID. Two of three preserve them under shift. Compared with phase two, shifted validation and a changed task/budget accompany better retention, so cross-phase differences cannot isolate the cause.

All three deterministic ridge-grid controls retain protected behavior but miss the full acquisition threshold. The gradient diagnostic achieves much larger conditional changes but fails retention. it demonstrates task capacity under ordinary training, not a bounded teacher-edit success.

The teacher exceeds this particular ridge grid on contrast error, but the comparison does not isolate a general teacher advantage: the teacher can redesign hidden features, choose units and other hyperparameters, and adapt using validation feedback. the grid only fits original hidden readouts over fixed settings.

Sixteen opportunities per source do not equalize computation, parameter search space or adaptive information. A stronger attribution experiment would compare equivalent adaptive feature-search capabilities. No such follow-up is claimed here.

## Colony outcomes and checks

Selected aligned colonies reduce collisions in all9 fixed arena runs. Family totals are205→187,170→150 and211→200 collision pair-steps. Exact-target controllers total5 in each family across the same3 rollout seeds, showing that the edited policy remains far from the supplied target's arena behavior.

These nine runs are correlated within3 source families and share fixed arena conditions. they are not nine independent source replications. Goal progress is broadly similar, with small declines for307, and action effort changes. These secondary outcomes do not override the primary failure or establish safety/optimality.

The pre-call audit found no test/sibling/rollout exposure in requests, fitting or selection. Ridge receives training data only. both validation distributions supply gate feedback. all final outcomes are computed after fixed responses. The final candidate history and selected operations are consistent with that path. No new held-out feedback or post-hoc selection was introduced by this review.

The lead's completed replay reported exact equality. This reviewer independently verified every manifest artifact hash and the final results digest:

`edc94c5c0b51bdb4b17bc8796f48abc5372cf6408433189de508f82d7de26c69`

No frozen code or experimental data were changed, and no paid calls were made. Three source seeds support an exploratory result with preserved negative outcomes, not a population significance or pretrained-language-model repair claim.
