# Finite-anchor geometry diagnostic

This local calculation tests mathematical limits suggested by a peer synthesis. It is separate from the teacher experiments. All data and networks are fresh synthetic draws. No API or trained-model workload is involved. Linear solves are counted as fits.

For f(a,b)=a tanh(b), the analytic Jacobian times the proposed direction is 0. an epsilon=1.0 edit changes the output by -0.214815. Thus zero first-order change does not imply exact finite nonlinear preservation.

For a frozen feature matrix H_keep, SVD gives an orthonormal nullspace basis Z. The fit is delta = Z pinv(H_probe Z) target. This enforces H_keep delta = 0 numerically on the registered anchors. It makes no corresponding promise for new observations. Readout bias is an additional constant feature.

Rank uses singular values greater than rcond times the largest singular value, with rcond=1e-12. The same cutoff controls the Moore–Penrose pseudoinverse. Minimum-norm solutions are compared after known feature permutation.

| Model | Method | Keep maximum drift | Probe target RMSE | Fresh IID drift RMSE | Shifted drift RMSE |
|---|---|---:|---:|---:|---:|
| source | local_solve | 2.22045e-15 | 6.62383e-16 | 0.775067 | 2.09865 |
| permuted | local_solve | 1.77636e-15 | 4.83482e-16 | 0.775067 | 2.09865 |
| permuted | raw_copy | 14.3793 | 6.27272 | 7.8101 | 3.41275 |
| permuted | known_permutation_copy | 2.66454e-15 | 1.74393e-15 | 0.775067 | 2.09865 |
| independent | local_solve | 3.55271e-15 | 9.03755e-16 | 0.508056 | 2.70079 |
| independent | raw_copy | 5.94025 | 4.35378 | 3.30031 | 2.29663 |

The raw-copy and known-permutation-copy controls have identical Euclidean delta norms because permutation is orthogonal. Local fits are separately measured and need not share that norm. no common trust-region bound is claimed. No teacher is involved.

| Epsilon | Finite nonlinear drift | Drift / epsilon² |
|---:|---:|---:|
| 0.01 | -3.18614e-05 | -0.318614 |
| 0.1 | -0.00307596 | -0.307596 |
| 0.5 | -0.0654904 | -0.261962 |
| 1.0 | -0.214815 | -0.214815 |

| Model | Keep rank | Keep nullity | Reduced probe rank | Fit count |
|---|---:|---:|---:|---:|
| source | 8 | 17 | 10 | 1 |
| permuted | 8 | 17 | 10 | 1 |
| independent | 8 | 17 | 10 | 1 |

Permutation equivariance: maximum delta discrepancy 2.87215e-13.
With 40 generic keep anchors, readout nullity is 0 and target fit RMSE is 0.120758. More retention constraints can remove all editable capacity: no useful nonzero exact-preserving edit exists within this fixed-feature readout class.

There are four linear fits: donor, permuted recipient, independently seeded recipient, and the rank-exhaustion check. A feature permutation has an exact coordinate correspondence. A new feature map does not inherit that guarantee. The tables expose the recipient fit and unconstrained drift rather than treating them as a certificate of general capability preservation.
