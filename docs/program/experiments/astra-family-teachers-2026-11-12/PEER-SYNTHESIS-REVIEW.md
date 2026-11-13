# Review of the proposed gauge-aware transfer synthesis

This review addresses the canonical [peer synthesis in issue #149](https://github.com/Moissanite-Labs/weft/issues/149). The useful proposal is to distinguish coordinate alignment from behavioral preservation and test a recipient-side constrained transfer rule.

The attachment goes too far when it treats all previous failures as one cause, describes a local derivative constraint as broad non-interference, and calls the combination unprecedented. The next experiment can be strong without those claims.

## What the mathematics supports

**Symmetry has a specific scope.** For elementwise tanh, consistently permuting hidden rows and biases and inversely permuting outgoing columns preserves the function. Consistent hidden sign flips also preserve it because tanh is odd. An arbitrary rotation, scaling or invertible change of hidden basis generally does not commute with tanh.

The displayed equation is correct when P is a permutation, not an unrestricted gauge matrix. An output-label swap is an exact specified behavioral transformation, not invariance of a classifier with fixed label meanings.

Known alignment already worked in our family study: aligned sibling active improvements were about 19–22%, while raw-coordinate results were much weaker but did not universally collapse. The source cells themselves failed shifted retention without any permutation. That failure therefore cannot be explained solely by a mismatched hidden ordering.

Distribution change, limited features, protected/target overlap and validation selection remain separate explanations. Our factorial also showed useful editing from weights alone and from activations alone.

the claim that symbolic models never reason successfully over floats is inconsistent with these bounded results and the numerical fidelity probes.

**A Jacobian certificate is local.** Write the retained output vector as F(theta), with J=dF/dtheta. If J=U Sigma V^T, parameter updates should be projected with P_null=I−V_r V_r^T, using the right singular vectors spanning parameter sensitivity. Then J delta=0 removes the first-order term, but generally

`F(theta + delta) − F(theta) = O(||delta||²)`,

not zero. A minimal counterexample is f(a,b)=a*tanh(b) at (a,b)=(0,0): its entire Jacobian is zero, while the finite update (a,b)=(epsilon,epsilon) changes the output to epsilon*tanh(epsilon). A proof assistant can verify the local statement. it cannot turn it into an unqualified finite-edit or distribution-shift guarantee.

Singular-value truncation gives an approximate nullspace and must report its residual and tolerance. Preserving a scalar loss derivative is weaker still than preserving the full output Jacobian.

**There is an exact restricted case.** Freeze the hidden features, include bias in the augmented feature vector h(x), and edit only the readout W. If each retained anchor satisfies deltaW*h(x)=0, its pre-output values remain exactly unchanged for any finite deltaW. The existing final tanh therefore also remains unchanged.

This extends to every feature vector in the anchors' linear span. It does not extend to arbitrary unseen inputs unless their features lie in that span. If the anchor feature matrix has full column rank, its exact readout nullspace is trivial: the only preserving update is zero.

Hidden-feature edits invalidate this fixed-feature certificate unless separately handled.

**SVD is a tool, not automatic canonicalization.** Singular vectors have sign ambiguity. repeated singular values admit arbitrary rotations and nearly repeated values create instability. Independently trained networks can represent different functions/features, rather than merely permuted copies.

Sorting eigenvalues does not resolve those differences, and generic rectangular feedforward matrices do not supply a unique dynamical eigenmode interpretation. A carefully specified least-squares solver with permutation-invariant regularization can be permutation equivariant.

arbitrary coordinate masks, tie-breaking or penalties can break that property. It must be tested, not inferred from the presence of an SVD.

**Probe installation is local fitting.** A packet (X_probe,deltaY) and recipient pseudoinverse/Gram solve transfer donor behavior through recipient-side numerical adaptation. This can use zero gradient-descent iterations and no language-model calls, but it is not zero learning or zero compute. Probes and outputs are data.

Using public synthetic probes can legitimately avoid transmitting donor raw training examples, but the distinction must be stated. Successful transfer also requires representability of the requested delta in the recipient's allowed feature span. projection can remove all useful skill change.

## Future diagnostic extensions

The completed geometry diagnostic below uses fresh synthetic models. The following are additional proposed tests using archived policy checkpoints, rather than a description of that completed run.

Use archived checkpoints and a fixed synthetic probe set, with no paid calls. Separate tests:

1. Verify identical outputs under exact within-mask hidden permutations and signed permutations. Verify that a generic rotation generally changes the tanh network. Remap an archived edit and check exact-permutation equivariance numerically.
2. Compute the preserved-anchor augmented feature matrix's singular spectrum and nullity at declared tolerances. If it is full rank, report that exact readout preservation leaves no capacity. do not manufacture a useful nullspace by silently increasing the tolerance.
3. For the full nonlinear parameter Jacobian, compare unprojected and projected fixed directions at predeclared step sizes. Report linear predicted drift, actual anchor drift, fresh IID/shift drift and retained target improvement. Norm-match a control to distinguish projection from simply shrinking an edit. Report the actual residual rather than calling an approximate projector exact.
4. In the fixed-feature case, solve a constrained readout transfer and verify its exact anchor/span statement. Evaluate the complete acquisition-versus-retention curve separately on fresh inputs. do not choose its tolerance or step size from that test curve.

Archived outcomes make this an exploratory diagnostic, not a new prospective confirmation. Its sharpest possible early result may be that the preservation constraints leave no useful capacity. That is valuable information before spending more on teachers.

## What a fair E11 could establish

Register a separate next study with independent donor/recipient seeds and distinct installation, selection and final test probes. Report three recipient regimes separately: an exact permutation of the donor, a mildly perturbed relative, and an independently trained model. The first is an equivariance unit test, not evidence of transfer between independently learned representations.

Compare raw coordinate copying. known-alignment copying where correspondence exists. unconstrained recipient readout fitting to the same donor packet. constrained fitting. and unchanged/no-skill controls. Give fitting controls the same probes, labels, output budget, solver and hyperparameter-selection opportunities.

Record packet bytes, recipient solve cost, feature rank, nullspace residual and all failures. If a teacher selects a module, distinguish its contribution from the solver and from donor training.

Use a genuinely conditional target, with both directions and protected behavior checked separately on IID, shift and unseen colony trajectories. Keep existing acquisition and retention thresholds fixed. Never count exact-permutation siblings as independent source replicates, and report no feasible edit as an outcome.

A numerical certificate should name its domain: particular anchors or their fixed-feature span, with specified tolerance. Broader nonlinear/shift preservation remains empirical unless a separate bound establishes it.

A successful E11 would establish that a particular bounded packet and recipient adaptation rule transfer a specified skill across stated model relationships while meeting measured retention criteria. Five successful independent seed pairs would be an encouraging exploratory result, not a universal non-interference theorem or proof of a new intelligence primitive.

## Relevant prior work

The components have clear precedents. [Orthogonal Gradient Descent](https://proceedings.mlr.press/v108/farajtabar20a.html) projects updates away from directions associated with previous outputs. [Git Re-Basin](https://arxiv.org/abs/2209.04836) explicitly aligns models using hidden permutation symmetries.

[AlphaEdit](https://arxiv.org/abs/2410.02355) studies null-space-constrained knowledge editing. These make “nobody has put these pieces together” an unsafe starting claim.

The primary-source abstract of [FedAlphaEdit](https://arxiv.org/abs/2610.11033), submitted October 8, 2026, additionally describes null-space-aligned collaborative editing and merging of projected statistics under a one-shot idealization. This review verified that abstract, not its complete proof or implementation.

It is a directly relevant novelty-check pointer, not evidence that it already solves transfer across independently trained tanh colonies. Any eventual novelty claim should identify the actual new interface, guarantee or controlled empirical finding after that comparison.

The attachment's alternative reward-free proposal also still assigns metabolic reward to falsification and assimilation. it changes reward design rather than removing it.

Rewarding prediction errors can reward noise, unlearnable anomalies or adversarially difficult observations unless the reward distinguishes reproducible, useful and learnable surprises. It does not automatically remove Goodharting.

Likewise, a discrete developmental program can produce structured network changes, but does not by itself guarantee smoothness or scale-independent behavioral effects. Both are hypotheses to test, not consequences of gauge symmetry.

No paid API calls or experiment-code changes were made for this review. The 96-call archive remains unchanged.


## Independent check of the accompanying geometry diagnostic

Reviewed phase5_geometry_probe/geometry.py, its captured arrays and results, and the tests. All seven tests passed. Exact replay matched on the recorded macOS arm64 / Python 3.14.6 run. On Linux x86_64 with Python 3.13.5 and NumPy 2.5.4, `python3 geometry.py replay --out data` raises ValueError: Replay mismatch artifacts.json (323 numeric diffs, max abs 2.6650903706126883e-13). The nondegenerate counterexample at (a,b)=(1,1) has J delta=0 but finite drift −0.214815 at step 1, with the smaller-step sweep exhibiting the expected second-order behavior.

The fixed-feature solver correctly uses the right-singular-vector nullspace and fits ten arbitrary probe targets while preserving eight anchors to roughly 1e-15. Known permutation transport and independently recomputed minimum-norm solutions agree to about 2.9e-13. Forty generic keep anchors give full rank 25 and zero nullity, with no useful edit.

This is a useful counterexample/feasibility calculation, not a learned-transfer result. The source and independent-recipient updates have norms 12.28 and 14.51 without a shared trust-region constraint. shifted inputs come from a disjoint [1,3] range.

It does not measure held-out agreement between donor and independently fitted recipient skill functions. Perfect interpolation on ten arbitrary supplied deltas therefore cannot establish transfer of a generalizable capability. The report appropriately states these limits and counts four linear fits.

The review identified the following requirements, which E11-PROPOSAL.md now explicitly handles: reconcile linear readout Y=HB with the existing policy's nonlinear output tanh(HB). Either choose a linear-output model prospectively or transform feasible recipient desired outputs into preactivation targets before solving, then verify final behavior.

Exact zero anchor residual extends to the feature span. a nonzero numerical residual extends only with an error bound that accounts for the span coefficients or conditioning.

The proposal also requires freezing fit-residual and norm acceptance rules, since a pseudoinverse returns a least-squares answer even when exact target installation is impossible.

## Repository counterevidence to a single-cause account

At the pinned [PR #140 results](https://github.com/Moissanite-Labs/weft/blob/a10f8f93989413f4c697b851b159e1b80860ddb5/docs/program/experiments/no-language-colony-2026-11-12/RESULTS-NL.md), E4a is a matrix-as-message compressor-template decoder and E4d is an embedding action decoder.

Their failed round trips concern channel and action binding, rather than copying neural weights between hidden bases. E2 operated a code carrier and assay. These observations do not establish gauge symmetry as the cause of the matrix-channel failures.

The pinned [PR #143 E10 results](https://github.com/Moissanite-Labs/weft/blob/53d4d1d5272e4987eb7779d1ca6da8cde556fb8d/docs/program/experiments/micro-cell-2026-11-12/RESULTS-E10.md) report changing the selection probe from 24 steps at world time 1000 to the actual 80-step task at time 0, while retaining architecture and invariants.

Final A returns were 37.38, 37.21 and 36.80 across three seeds. The earlier E09 failures remain in the same pinned archive. This is evidence for a selection-horizon explanation without a gauge correction. It does not establish that horizon mismatch explains every other study.
