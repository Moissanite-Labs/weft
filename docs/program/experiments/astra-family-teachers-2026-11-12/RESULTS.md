# Astra family teachers results

Three source seeds are the replicate units. Siblings are correlated family members. These results do not support a population significance claim.

The weight-visible condition supplies both numerical matrices and hidden activations. This comparison cannot isolate the contribution of matrices from activations. Scrambled values form a contradictory-evidence control, not a decisive mechanism test.

## Source outcomes

| Seed | Arm | Split | Active baseline | Active edited | Improvement % | Movement edited | Hazard drift | Low-urgency drift | Retention | ≥5% + retention |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---|
| 17 | weights_behavior | test | 0.0211903 | 0.0171414 | 19.1071 | 0.00661791 | 0 | 0.000480778 | True | True |
| 17 | weights_behavior | test_shift | 0.0370782 | 0.0296216 | 20.1106 | 0.00988483 | 0 | 0.000699654 | False | False |
| 17 | behavior_only | test | 0.0211903 | 0.0212683 | -0.368013 | 0.00803316 | 0 | 7.41361e-05 | True | False |
| 17 | behavior_only | test_shift | 0.0370782 | 0.036619 | 1.23861 | 0.0118739 | 0 | 7.71643e-05 | True | False |
| 17 | scrambled_weights | test | 0.0211903 | 0.0211903 | 0 | 0.00796729 | 0 | 0 | True | False |
| 17 | scrambled_weights | test_shift | 0.0370782 | 0.0370782 | 0 | 0.0119828 | 0 | 0 | True | False |
| 29 | weights_behavior | test | 0.0256621 | 0.0200525 | 21.8595 | 0.00757171 | 2.25054e-05 | 0.000521096 | False | False |
| 29 | weights_behavior | test_shift | 0.0403191 | 0.0318978 | 20.8867 | 0.0108102 | 0.000113205 | 0.000809638 | False | False |
| 29 | behavior_only | test | 0.0256621 | 0.0257514 | -0.347908 | 0.0095431 | 0 | 6.32784e-05 | True | False |
| 29 | behavior_only | test_shift | 0.0403191 | 0.040446 | -0.314865 | 0.013437 | 0 | 6.28362e-05 | True | False |
| 29 | scrambled_weights | test | 0.0256621 | 0.0251169 | 2.12468 | 0.00936507 | 0 | 0.000215822 | True | False |
| 29 | scrambled_weights | test_shift | 0.0403191 | 0.0396021 | 1.77834 | 0.0132588 | 0 | 0.000210729 | True | False |
| 43 | weights_behavior | test | 0.0233122 | 0.0184706 | 20.7682 | 0.00595003 | 0 | 0.000462528 | True | True |
| 43 | weights_behavior | test_shift | 0.0405105 | 0.0325656 | 19.612 | 0.0114756 | 0 | 0.000811835 | False | False |
| 43 | behavior_only | test | 0.0233122 | 0.0231756 | 0.585866 | 0.00724006 | 0 | 9.82338e-06 | True | False |
| 43 | behavior_only | test_shift | 0.0405105 | 0.040324 | 0.460406 | 0.013818 | 0 | 9.87423e-06 | True | False |
| 43 | scrambled_weights | test | 0.0233122 | 0.0199738 | 14.3203 | 0.00632918 | 0 | 0.000264661 | True | True |
| 43 | scrambled_weights | test_shift | 0.0405105 | 0.0349342 | 13.7652 | 0.0121559 | 0 | 0.000483224 | True | True |

behavior_only, test: 0/3 source seeds meet the 5% improvement and retention rule.

behavior_only, test_shift: 0/3 source seeds meet the 5% improvement and retention rule.

scrambled_weights, test: 1/3 source seeds meet the 5% improvement and retention rule.

scrambled_weights, test_shift: 1/3 source seeds meet the 5% improvement and retention rule.

weights_behavior, test: 2/3 source seeds meet the 5% improvement and retention rule.

weights_behavior, test_shift: 0/3 source seeds meet the 5% improvement and retention rule.

## Family transfer

| Seed | Arm | Split | Alignment | Mean baseline active | Mean edited active | Mean improvement % | Retention count |
|---|---|---|---|---:|---:|---:|---:|
| 17 | behavior_only | test | aligned | 0.0218531 | 0.0219253 | -0.322159 | 4/4 |
| 17 | behavior_only | test | raw | 0.0218531 | 0.0218396 | 0.14957 | 3/4 |
| 17 | behavior_only | test_shift | aligned | 0.0383385 | 0.0378654 | 1.23878 | 4/4 |
| 17 | behavior_only | test_shift | raw | 0.0383385 | 0.0378523 | 1.30695 | 3/4 |
| 17 | scrambled_weights | test | aligned | 0.0218531 | 0.0218531 | 0 | 4/4 |
| 17 | scrambled_weights | test | raw | 0.0218531 | 0.0218531 | 0 | 4/4 |
| 17 | scrambled_weights | test_shift | aligned | 0.0383385 | 0.0383385 | 0 | 4/4 |
| 17 | scrambled_weights | test_shift | raw | 0.0383385 | 0.0383385 | 0 | 4/4 |
| 17 | weights_behavior | test | aligned | 0.0218531 | 0.0177314 | 18.8772 | 4/4 |
| 17 | weights_behavior | test | raw | 0.0218531 | 0.0209261 | 4.31423 | 1/4 |
| 17 | weights_behavior | test_shift | aligned | 0.0383385 | 0.0307855 | 19.7205 | 0/4 |
| 17 | weights_behavior | test_shift | raw | 0.0383385 | 0.0357495 | 6.92075 | 0/4 |
| 29 | behavior_only | test | aligned | 0.0262368 | 0.0262918 | -0.212291 | 4/4 |
| 29 | behavior_only | test | raw | 0.0262368 | 0.0263851 | -0.568057 | 4/4 |
| 29 | behavior_only | test_shift | aligned | 0.0410564 | 0.0411459 | -0.218985 | 4/4 |
| 29 | behavior_only | test_shift | raw | 0.0410564 | 0.0413423 | -0.69244 | 4/4 |
| 29 | scrambled_weights | test | aligned | 0.0262368 | 0.025786 | 1.71325 | 4/4 |
| 29 | scrambled_weights | test | raw | 0.0262368 | 0.0262812 | -0.177417 | 4/4 |
| 29 | scrambled_weights | test_shift | aligned | 0.0410564 | 0.0404371 | 1.50639 | 4/4 |
| 29 | scrambled_weights | test_shift | raw | 0.0410564 | 0.0409665 | 0.21533 | 4/4 |
| 29 | weights_behavior | test | aligned | 0.0262368 | 0.0205548 | 21.6603 | 0/4 |
| 29 | weights_behavior | test | raw | 0.0262368 | 0.0255202 | 2.68921 | 3/4 |
| 29 | weights_behavior | test_shift | aligned | 0.0410564 | 0.0325604 | 20.6957 | 0/4 |
| 29 | weights_behavior | test_shift | raw | 0.0410564 | 0.0401342 | 2.21392 | 0/4 |
| 43 | behavior_only | test | aligned | 0.023483 | 0.0233403 | 0.608444 | 4/4 |
| 43 | behavior_only | test | raw | 0.023483 | 0.0234132 | 0.308839 | 4/4 |
| 43 | behavior_only | test_shift | aligned | 0.0407536 | 0.0405628 | 0.469132 | 4/4 |
| 43 | behavior_only | test_shift | raw | 0.0407536 | 0.0406273 | 0.316465 | 4/4 |
| 43 | scrambled_weights | test | aligned | 0.023483 | 0.0202023 | 13.9786 | 4/4 |
| 43 | scrambled_weights | test | raw | 0.023483 | 0.022802 | 2.91638 | 2/4 |
| 43 | scrambled_weights | test_shift | aligned | 0.0407536 | 0.0352662 | 13.4695 | 4/4 |
| 43 | scrambled_weights | test_shift | raw | 0.0407536 | 0.038855 | 4.69249 | 1/4 |
| 43 | weights_behavior | test | aligned | 0.023483 | 0.0186975 | 20.3866 | 4/4 |
| 43 | weights_behavior | test | raw | 0.023483 | 0.023536 | -0.253832 | 0/4 |
| 43 | weights_behavior | test_shift | aligned | 0.0407536 | 0.0329018 | 19.2719 | 0/4 |
| 43 | weights_behavior | test_shift | raw | 0.0407536 | 0.0392548 | 3.699 | 0/4 |

## Per-sibling outcomes

| Seed | Arm | Sibling | Split | Alignment | Active baseline | Active edited | Improvement % | Retention |
|---|---|---|---|---|---:|---:|---:|---|
| 17 | weights_behavior | family-17:sibling-0 | test | aligned | 0.0207212 | 0.0167928 | 18.9584 | True |
| 17 | weights_behavior | family-17:sibling-0 | test | raw | 0.0207212 | 0.0170719 | 17.6114 | False |
| 17 | weights_behavior | family-17:sibling-1 | test | aligned | 0.023382 | 0.0190428 | 18.5579 | True |
| 17 | weights_behavior | family-17:sibling-1 | test | raw | 0.023382 | 0.022116 | 5.4148 | True |
| 17 | weights_behavior | family-17:sibling-2 | test | aligned | 0.0205647 | 0.0165858 | 19.3481 | True |
| 17 | weights_behavior | family-17:sibling-2 | test | raw | 0.0205647 | 0.0215537 | -4.8095 | False |
| 17 | weights_behavior | family-17:sibling-3 | test | aligned | 0.0227446 | 0.018504 | 18.6445 | True |
| 17 | weights_behavior | family-17:sibling-3 | test | raw | 0.0227446 | 0.0229629 | -0.959782 | False |
| 17 | weights_behavior | family-17:sibling-0 | test_shift | aligned | 0.0360354 | 0.0288168 | 20.0317 | False |
| 17 | weights_behavior | family-17:sibling-0 | test_shift | raw | 0.0360354 | 0.0291559 | 19.0909 | False |
| 17 | weights_behavior | family-17:sibling-1 | test_shift | aligned | 0.041532 | 0.0335306 | 19.2656 | False |
| 17 | weights_behavior | family-17:sibling-1 | test_shift | raw | 0.041532 | 0.039178 | 5.668 | False |
| 17 | weights_behavior | family-17:sibling-2 | test_shift | aligned | 0.0367384 | 0.0293392 | 20.1404 | False |
| 17 | weights_behavior | family-17:sibling-2 | test_shift | raw | 0.0367384 | 0.0364275 | 0.84624 | False |
| 17 | weights_behavior | family-17:sibling-3 | test_shift | aligned | 0.039048 | 0.0314554 | 19.4443 | False |
| 17 | weights_behavior | family-17:sibling-3 | test_shift | raw | 0.039048 | 0.0382367 | 2.07784 | False |
| 17 | behavior_only | family-17:sibling-0 | test | aligned | 0.0207212 | 0.0208024 | -0.391473 | True |
| 17 | behavior_only | family-17:sibling-0 | test | raw | 0.0207212 | 0.0211707 | -2.1692 | True |
| 17 | behavior_only | family-17:sibling-1 | test | aligned | 0.023382 | 0.0234664 | -0.360608 | True |
| 17 | behavior_only | family-17:sibling-1 | test | raw | 0.023382 | 0.0234664 | -0.360608 | True |
| 17 | behavior_only | family-17:sibling-2 | test | aligned | 0.0205647 | 0.0205518 | 0.0625534 | True |
| 17 | behavior_only | family-17:sibling-2 | test | raw | 0.0205647 | 0.0193996 | 5.6655 | False |
| 17 | behavior_only | family-17:sibling-3 | test | aligned | 0.0227446 | 0.0228809 | -0.599108 | True |
| 17 | behavior_only | family-17:sibling-3 | test | raw | 0.0227446 | 0.0233217 | -2.53741 | True |
| 17 | behavior_only | family-17:sibling-0 | test_shift | aligned | 0.0360354 | 0.0355994 | 1.20972 | True |
| 17 | behavior_only | family-17:sibling-0 | test_shift | raw | 0.0360354 | 0.036607 | -1.58641 | True |
| 17 | behavior_only | family-17:sibling-1 | test_shift | aligned | 0.041532 | 0.0410524 | 1.15484 | True |
| 17 | behavior_only | family-17:sibling-1 | test_shift | raw | 0.041532 | 0.0410524 | 1.15484 | True |
| 17 | behavior_only | family-17:sibling-2 | test_shift | aligned | 0.0367384 | 0.0361836 | 1.51021 | True |
| 17 | behavior_only | family-17:sibling-2 | test_shift | raw | 0.0367384 | 0.0339808 | 7.50596 | False |
| 17 | behavior_only | family-17:sibling-3 | test_shift | aligned | 0.039048 | 0.0386262 | 1.08033 | True |
| 17 | behavior_only | family-17:sibling-3 | test_shift | raw | 0.039048 | 0.0397691 | -1.84658 | True |
| 17 | scrambled_weights | family-17:sibling-0 | test | aligned | 0.0207212 | 0.0207212 | 0 | True |
| 17 | scrambled_weights | family-17:sibling-0 | test | raw | 0.0207212 | 0.0207212 | 0 | True |
| 17 | scrambled_weights | family-17:sibling-1 | test | aligned | 0.023382 | 0.023382 | 0 | True |
| 17 | scrambled_weights | family-17:sibling-1 | test | raw | 0.023382 | 0.023382 | 0 | True |
| 17 | scrambled_weights | family-17:sibling-2 | test | aligned | 0.0205647 | 0.0205647 | 0 | True |
| 17 | scrambled_weights | family-17:sibling-2 | test | raw | 0.0205647 | 0.0205647 | 0 | True |
| 17 | scrambled_weights | family-17:sibling-3 | test | aligned | 0.0227446 | 0.0227446 | 0 | True |
| 17 | scrambled_weights | family-17:sibling-3 | test | raw | 0.0227446 | 0.0227446 | 0 | True |
| 17 | scrambled_weights | family-17:sibling-0 | test_shift | aligned | 0.0360354 | 0.0360354 | 0 | True |
| 17 | scrambled_weights | family-17:sibling-0 | test_shift | raw | 0.0360354 | 0.0360354 | 0 | True |
| 17 | scrambled_weights | family-17:sibling-1 | test_shift | aligned | 0.041532 | 0.041532 | 0 | True |
| 17 | scrambled_weights | family-17:sibling-1 | test_shift | raw | 0.041532 | 0.041532 | 0 | True |
| 17 | scrambled_weights | family-17:sibling-2 | test_shift | aligned | 0.0367384 | 0.0367384 | 0 | True |
| 17 | scrambled_weights | family-17:sibling-2 | test_shift | raw | 0.0367384 | 0.0367384 | 0 | True |
| 17 | scrambled_weights | family-17:sibling-3 | test_shift | aligned | 0.039048 | 0.039048 | 0 | True |
| 17 | scrambled_weights | family-17:sibling-3 | test_shift | raw | 0.039048 | 0.039048 | 0 | True |
| 29 | weights_behavior | family-29:sibling-0 | test | aligned | 0.0266792 | 0.0209241 | 21.5713 | False |
| 29 | weights_behavior | family-29:sibling-0 | test | raw | 0.0266792 | 0.023871 | 10.5257 | True |
| 29 | weights_behavior | family-29:sibling-1 | test | aligned | 0.0269772 | 0.0211446 | 21.6204 | False |
| 29 | weights_behavior | family-29:sibling-1 | test | raw | 0.0269772 | 0.0269215 | 0.206615 | True |
| 29 | weights_behavior | family-29:sibling-2 | test | aligned | 0.0263621 | 0.0206786 | 21.5594 | False |
| 29 | weights_behavior | family-29:sibling-2 | test | raw | 0.0263621 | 0.0264276 | -0.248505 | True |
| 29 | weights_behavior | family-29:sibling-3 | test | aligned | 0.0249287 | 0.0194718 | 21.8903 | False |
| 29 | weights_behavior | family-29:sibling-3 | test | raw | 0.0249287 | 0.0248607 | 0.272981 | False |
| 29 | weights_behavior | family-29:sibling-0 | test_shift | aligned | 0.0417375 | 0.0331143 | 20.6607 | False |
| 29 | weights_behavior | family-29:sibling-0 | test_shift | raw | 0.0417375 | 0.037839 | 9.34057 | False |
| 29 | weights_behavior | family-29:sibling-1 | test_shift | aligned | 0.0420362 | 0.033386 | 20.578 | False |
| 29 | weights_behavior | family-29:sibling-1 | test_shift | raw | 0.0420362 | 0.0422626 | -0.538446 | False |
| 29 | weights_behavior | family-29:sibling-2 | test_shift | aligned | 0.0411127 | 0.0325954 | 20.717 | False |
| 29 | weights_behavior | family-29:sibling-2 | test_shift | raw | 0.0411127 | 0.0412173 | -0.254464 | False |
| 29 | weights_behavior | family-29:sibling-3 | test_shift | aligned | 0.0393391 | 0.0311459 | 20.8271 | False |
| 29 | weights_behavior | family-29:sibling-3 | test_shift | raw | 0.0393391 | 0.0392179 | 0.308016 | False |
| 29 | behavior_only | family-29:sibling-0 | test | aligned | 0.0266792 | 0.0268013 | -0.45788 | True |
| 29 | behavior_only | family-29:sibling-0 | test | raw | 0.0266792 | 0.0266774 | 0.00682308 | True |
| 29 | behavior_only | family-29:sibling-1 | test | aligned | 0.0269772 | 0.0269541 | 0.0855488 | True |
| 29 | behavior_only | family-29:sibling-1 | test | raw | 0.0269772 | 0.0271863 | -0.775012 | True |
| 29 | behavior_only | family-29:sibling-2 | test | aligned | 0.0263621 | 0.0263989 | -0.139625 | True |
| 29 | behavior_only | family-29:sibling-2 | test | raw | 0.0263621 | 0.026561 | -0.754285 | True |
| 29 | behavior_only | family-29:sibling-3 | test | aligned | 0.0249287 | 0.0250128 | -0.337206 | True |
| 29 | behavior_only | family-29:sibling-3 | test | raw | 0.0249287 | 0.0251157 | -0.749755 | True |
| 29 | behavior_only | family-29:sibling-0 | test_shift | aligned | 0.0417375 | 0.0418934 | -0.37346 | True |
| 29 | behavior_only | family-29:sibling-0 | test_shift | raw | 0.0417375 | 0.042071 | -0.799167 | True |
| 29 | behavior_only | family-29:sibling-1 | test_shift | aligned | 0.0420362 | 0.042074 | -0.0898417 | True |
| 29 | behavior_only | family-29:sibling-1 | test_shift | raw | 0.0420362 | 0.0423028 | -0.634221 | True |
| 29 | behavior_only | family-29:sibling-2 | test_shift | aligned | 0.0411127 | 0.0411592 | -0.113169 | True |
| 29 | behavior_only | family-29:sibling-2 | test_shift | raw | 0.0411127 | 0.0415277 | -1.00946 | True |
| 29 | behavior_only | family-29:sibling-3 | test_shift | aligned | 0.0393391 | 0.0394569 | -0.299468 | True |
| 29 | behavior_only | family-29:sibling-3 | test_shift | raw | 0.0393391 | 0.0394677 | -0.326915 | True |
| 29 | scrambled_weights | family-29:sibling-0 | test | aligned | 0.0266792 | 0.0265096 | 0.635726 | True |
| 29 | scrambled_weights | family-29:sibling-0 | test | raw | 0.0266792 | 0.0265627 | 0.436684 | True |
| 29 | scrambled_weights | family-29:sibling-1 | test | aligned | 0.0269772 | 0.0263031 | 2.49881 | True |
| 29 | scrambled_weights | family-29:sibling-1 | test | raw | 0.0269772 | 0.0274931 | -1.9122 | True |
| 29 | scrambled_weights | family-29:sibling-2 | test | aligned | 0.0263621 | 0.0257621 | 2.27605 | True |
| 29 | scrambled_weights | family-29:sibling-2 | test | raw | 0.0263621 | 0.0257954 | 2.14996 | True |
| 29 | scrambled_weights | family-29:sibling-3 | test | aligned | 0.0249287 | 0.0245692 | 1.44241 | True |
| 29 | scrambled_weights | family-29:sibling-3 | test | raw | 0.0249287 | 0.0252738 | -1.38412 | True |
| 29 | scrambled_weights | family-29:sibling-0 | test_shift | aligned | 0.0417375 | 0.0414067 | 0.792471 | True |
| 29 | scrambled_weights | family-29:sibling-0 | test_shift | raw | 0.0417375 | 0.0414241 | 0.750952 | True |
| 29 | scrambled_weights | family-29:sibling-1 | test_shift | aligned | 0.0420362 | 0.0412152 | 1.95308 | True |
| 29 | scrambled_weights | family-29:sibling-1 | test_shift | raw | 0.0420362 | 0.0424977 | -1.09779 | True |
| 29 | scrambled_weights | family-29:sibling-2 | test_shift | aligned | 0.0411127 | 0.0403051 | 1.96426 | True |
| 29 | scrambled_weights | family-29:sibling-2 | test_shift | raw | 0.0411127 | 0.0403645 | 1.81985 | True |
| 29 | scrambled_weights | family-29:sibling-3 | test_shift | aligned | 0.0393391 | 0.0388215 | 1.31574 | True |
| 29 | scrambled_weights | family-29:sibling-3 | test_shift | raw | 0.0393391 | 0.0395797 | -0.611688 | True |
| 43 | weights_behavior | family-43:sibling-0 | test | aligned | 0.0235496 | 0.0188183 | 20.0905 | True |
| 43 | weights_behavior | family-43:sibling-0 | test | raw | 0.0235496 | 0.0223412 | 5.13142 | False |
| 43 | weights_behavior | family-43:sibling-1 | test | aligned | 0.022728 | 0.0179701 | 20.934 | True |
| 43 | weights_behavior | family-43:sibling-1 | test | raw | 0.022728 | 0.02364 | -4.01263 | False |
| 43 | weights_behavior | family-43:sibling-2 | test | aligned | 0.0242661 | 0.0194142 | 19.9944 | True |
| 43 | weights_behavior | family-43:sibling-2 | test | raw | 0.0242661 | 0.0245289 | -1.08305 | False |
| 43 | weights_behavior | family-43:sibling-3 | test | aligned | 0.0233882 | 0.0185872 | 20.5276 | True |
| 43 | weights_behavior | family-43:sibling-3 | test | raw | 0.0233882 | 0.023634 | -1.05107 | False |
| 43 | weights_behavior | family-43:sibling-0 | test_shift | aligned | 0.0408309 | 0.0329347 | 19.3389 | False |
| 43 | weights_behavior | family-43:sibling-0 | test_shift | raw | 0.0408309 | 0.0379058 | 7.16401 | False |
| 43 | weights_behavior | family-43:sibling-1 | test_shift | aligned | 0.0397402 | 0.0319499 | 19.6031 | False |
| 43 | weights_behavior | family-43:sibling-1 | test_shift | raw | 0.0397402 | 0.0384194 | 3.32358 | False |
| 43 | weights_behavior | family-43:sibling-2 | test_shift | aligned | 0.0418195 | 0.0339663 | 18.7789 | False |
| 43 | weights_behavior | family-43:sibling-2 | test_shift | raw | 0.0418195 | 0.041852 | -0.0774892 | False |
| 43 | weights_behavior | family-43:sibling-3 | test_shift | aligned | 0.0406239 | 0.0327563 | 19.3669 | False |
| 43 | weights_behavior | family-43:sibling-3 | test_shift | raw | 0.0406239 | 0.0388421 | 4.38588 | False |
| 43 | behavior_only | family-43:sibling-0 | test | aligned | 0.0235496 | 0.023415 | 0.571581 | True |
| 43 | behavior_only | family-43:sibling-0 | test | raw | 0.0235496 | 0.0234946 | 0.233381 | True |
| 43 | behavior_only | family-43:sibling-1 | test | aligned | 0.022728 | 0.0225708 | 0.692045 | True |
| 43 | behavior_only | family-43:sibling-1 | test | raw | 0.022728 | 0.0224516 | 1.21627 | True |
| 43 | behavior_only | family-43:sibling-2 | test | aligned | 0.0242661 | 0.0241284 | 0.567357 | True |
| 43 | behavior_only | family-43:sibling-2 | test | raw | 0.0242661 | 0.0243309 | -0.267203 | True |
| 43 | behavior_only | family-43:sibling-3 | test | aligned | 0.0233882 | 0.0232472 | 0.602793 | True |
| 43 | behavior_only | family-43:sibling-3 | test | raw | 0.0233882 | 0.0233758 | 0.0529028 | True |
| 43 | behavior_only | family-43:sibling-0 | test_shift | aligned | 0.0408309 | 0.0406515 | 0.439449 | True |
| 43 | behavior_only | family-43:sibling-0 | test_shift | raw | 0.0408309 | 0.0406863 | 0.354192 | True |
| 43 | behavior_only | family-43:sibling-1 | test_shift | aligned | 0.0397402 | 0.0395273 | 0.535735 | True |
| 43 | behavior_only | family-43:sibling-1 | test_shift | raw | 0.0397402 | 0.0392948 | 1.12098 | True |
| 43 | behavior_only | family-43:sibling-2 | test_shift | aligned | 0.0418195 | 0.0416476 | 0.411133 | True |
| 43 | behavior_only | family-43:sibling-2 | test_shift | raw | 0.0418195 | 0.0418049 | 0.0350644 | True |
| 43 | behavior_only | family-43:sibling-3 | test_shift | aligned | 0.0406239 | 0.0404247 | 0.490213 | True |
| 43 | behavior_only | family-43:sibling-3 | test_shift | raw | 0.0406239 | 0.0407231 | -0.244379 | True |
| 43 | scrambled_weights | family-43:sibling-0 | test | aligned | 0.0235496 | 0.0202646 | 13.9491 | True |
| 43 | scrambled_weights | family-43:sibling-0 | test | raw | 0.0235496 | 0.021983 | 6.65219 | True |
| 43 | scrambled_weights | family-43:sibling-1 | test | aligned | 0.022728 | 0.0194568 | 14.393 | True |
| 43 | scrambled_weights | family-43:sibling-1 | test | raw | 0.022728 | 0.02221 | 2.27931 | False |
| 43 | scrambled_weights | family-43:sibling-2 | test | aligned | 0.0242661 | 0.021011 | 13.4139 | True |
| 43 | scrambled_weights | family-43:sibling-2 | test | raw | 0.0242661 | 0.024273 | -0.0286681 | True |
| 43 | scrambled_weights | family-43:sibling-3 | test | aligned | 0.0233882 | 0.0200768 | 14.1584 | True |
| 43 | scrambled_weights | family-43:sibling-3 | test | raw | 0.0233882 | 0.0227421 | 2.7627 | False |
| 43 | scrambled_weights | family-43:sibling-0 | test_shift | aligned | 0.0408309 | 0.035301 | 13.5435 | True |
| 43 | scrambled_weights | family-43:sibling-0 | test_shift | raw | 0.0408309 | 0.0377856 | 7.45839 | True |
| 43 | scrambled_weights | family-43:sibling-1 | test_shift | aligned | 0.0397402 | 0.0342832 | 13.7317 | True |
| 43 | scrambled_weights | family-43:sibling-1 | test_shift | raw | 0.0397402 | 0.0375485 | 5.51525 | False |
| 43 | scrambled_weights | family-43:sibling-2 | test_shift | aligned | 0.0418195 | 0.0363716 | 13.0274 | True |
| 43 | scrambled_weights | family-43:sibling-2 | test_shift | raw | 0.0418195 | 0.0417189 | 0.24058 | False |
| 43 | scrambled_weights | family-43:sibling-3 | test_shift | aligned | 0.0406239 | 0.0351089 | 13.5756 | True |
| 43 | scrambled_weights | family-43:sibling-3 | test_shift | raw | 0.0406239 | 0.0383669 | 5.55575 | False |

## Controls and interpretation

Local search has three candidate evaluations and the same selection gate. Tokens, time, information and computation are not matched. The gradient comparator is a separate optimization diagnostic. Random directions match selected support and norm. All 32 remain unselected. Their midrank percentiles count ties and are descriptive, not formal p values.

Full control values and the true-versus-scrambled round-one pair are in summary.json.

## Shared-arena rollout means

Three fixed rollout seeds are averaged within each source family. These exploratory dynamics do not establish that static imitation targets are optimal.

| Seed | Arm | Variant | Collisions | Hazard steps | Progress | Energy |
|---|---|---|---:|---:|---:|---:|
| 17 | weights_behavior | no_edit | 761 | 4.33333 | 0.0119931 | 0.136844 |
| 17 | weights_behavior | edited_aligned | 705.333 | 4.66667 | 0.0119796 | 0.138234 |
| 17 | weights_behavior | edited_raw | 795 | 4.66667 | 0.0120009 | 0.137664 |
| 17 | behavior_only | no_edit | 761 | 4.33333 | 0.0119931 | 0.136844 |
| 17 | behavior_only | edited_aligned | 753 | 4.33333 | 0.0119946 | 0.137234 |
| 17 | behavior_only | edited_raw | 660.333 | 4.33333 | 0.0119205 | 0.135864 |
| 17 | scrambled_weights | no_edit | 761 | 4.33333 | 0.0119931 | 0.136844 |
| 17 | scrambled_weights | edited_aligned | 761 | 4.33333 | 0.0119931 | 0.136844 |
| 17 | scrambled_weights | edited_raw | 761 | 4.33333 | 0.0119931 | 0.136844 |
| 29 | weights_behavior | no_edit | 862.333 | 4.66667 | 0.0119993 | 0.136939 |
| 29 | weights_behavior | edited_aligned | 702.667 | 4.66667 | 0.0119551 | 0.138073 |
| 29 | weights_behavior | edited_raw | 811 | 4.66667 | 0.0119499 | 0.13711 |
| 29 | behavior_only | no_edit | 862.333 | 4.66667 | 0.0119993 | 0.136939 |
| 29 | behavior_only | edited_aligned | 861 | 4.66667 | 0.0120219 | 0.136963 |
| 29 | behavior_only | edited_raw | 774.667 | 4.33333 | 0.0119488 | 0.136734 |
| 29 | scrambled_weights | no_edit | 862.333 | 4.66667 | 0.0119993 | 0.136939 |
| 29 | scrambled_weights | edited_aligned | 814.333 | 4.66667 | 0.0119295 | 0.136339 |
| 29 | scrambled_weights | edited_raw | 846.667 | 4.66667 | 0.0119769 | 0.137795 |
| 43 | weights_behavior | no_edit | 914 | 4.33333 | 0.011938 | 0.136718 |
| 43 | weights_behavior | edited_aligned | 754 | 4.33333 | 0.0118645 | 0.137498 |
| 43 | weights_behavior | edited_raw | 656.333 | 4 | 0.0116772 | 0.135949 |
| 43 | behavior_only | no_edit | 914 | 4.33333 | 0.011938 | 0.136718 |
| 43 | behavior_only | edited_aligned | 933.333 | 4.33333 | 0.0119326 | 0.136633 |
| 43 | behavior_only | edited_raw | 877.333 | 4.33333 | 0.0119012 | 0.136633 |
| 43 | scrambled_weights | no_edit | 914 | 4.33333 | 0.011938 | 0.136718 |
| 43 | scrambled_weights | edited_aligned | 776.333 | 4.33333 | 0.0118812 | 0.137756 |
| 43 | scrambled_weights | edited_raw | 726.333 | 4.33333 | 0.0118133 | 0.136537 |

## Control outcomes

| Seed | Arm | Split | Control | Active edited | Improvement % | Retention |
|---|---|---|---|---:|---:|---|
| 17 | weights_behavior | test | no_edit | 0.0211903 | 0 | True |
| 17 | weights_behavior | test | gradient_diagnostic | 0.0143239 | 32.4035 | False |
| 17 | weights_behavior | test | local_evolution | 0.0211903 | 0 | True |
| 17 | weights_behavior | test_shift | no_edit | 0.0370782 | 0 | True |
| 17 | weights_behavior | test_shift | gradient_diagnostic | 0.0250405 | 32.4657 | False |
| 17 | weights_behavior | test_shift | local_evolution | 0.0370782 | 0 | True |
| 17 | behavior_only | test | no_edit | 0.0211903 | 0 | True |
| 17 | behavior_only | test | gradient_diagnostic | 0.0143239 | 32.4035 | False |
| 17 | behavior_only | test | local_evolution | 0.0211903 | 0 | True |
| 17 | behavior_only | test_shift | no_edit | 0.0370782 | 0 | True |
| 17 | behavior_only | test_shift | gradient_diagnostic | 0.0250405 | 32.4657 | False |
| 17 | behavior_only | test_shift | local_evolution | 0.0370782 | 0 | True |
| 17 | scrambled_weights | test | no_edit | 0.0211903 | 0 | True |
| 17 | scrambled_weights | test | gradient_diagnostic | 0.0143239 | 32.4035 | False |
| 17 | scrambled_weights | test | local_evolution | 0.0211903 | 0 | True |
| 17 | scrambled_weights | test_shift | no_edit | 0.0370782 | 0 | True |
| 17 | scrambled_weights | test_shift | gradient_diagnostic | 0.0250405 | 32.4657 | False |
| 17 | scrambled_weights | test_shift | local_evolution | 0.0370782 | 0 | True |
| 29 | weights_behavior | test | no_edit | 0.0256621 | 0 | True |
| 29 | weights_behavior | test | gradient_diagnostic | 0.0187367 | 26.987 | False |
| 29 | weights_behavior | test | local_evolution | 0.0256621 | 0 | True |
| 29 | weights_behavior | test_shift | no_edit | 0.0403191 | 0 | True |
| 29 | weights_behavior | test_shift | gradient_diagnostic | 0.0295546 | 26.6982 | False |
| 29 | weights_behavior | test_shift | local_evolution | 0.0403191 | 0 | True |
| 29 | behavior_only | test | no_edit | 0.0256621 | 0 | True |
| 29 | behavior_only | test | gradient_diagnostic | 0.0187367 | 26.987 | False |
| 29 | behavior_only | test | local_evolution | 0.0256621 | 0 | True |
| 29 | behavior_only | test_shift | no_edit | 0.0403191 | 0 | True |
| 29 | behavior_only | test_shift | gradient_diagnostic | 0.0295546 | 26.6982 | False |
| 29 | behavior_only | test_shift | local_evolution | 0.0403191 | 0 | True |
| 29 | scrambled_weights | test | no_edit | 0.0256621 | 0 | True |
| 29 | scrambled_weights | test | gradient_diagnostic | 0.0187367 | 26.987 | False |
| 29 | scrambled_weights | test | local_evolution | 0.0256621 | 0 | True |
| 29 | scrambled_weights | test_shift | no_edit | 0.0403191 | 0 | True |
| 29 | scrambled_weights | test_shift | gradient_diagnostic | 0.0295546 | 26.6982 | False |
| 29 | scrambled_weights | test_shift | local_evolution | 0.0403191 | 0 | True |
| 43 | weights_behavior | test | no_edit | 0.0233122 | 0 | True |
| 43 | weights_behavior | test | gradient_diagnostic | 0.0180444 | 22.5965 | False |
| 43 | weights_behavior | test | local_evolution | 0.0233122 | 0 | True |
| 43 | weights_behavior | test_shift | no_edit | 0.0405105 | 0 | True |
| 43 | weights_behavior | test_shift | gradient_diagnostic | 0.0316637 | 21.8383 | False |
| 43 | weights_behavior | test_shift | local_evolution | 0.0405105 | 0 | True |
| 43 | behavior_only | test | no_edit | 0.0233122 | 0 | True |
| 43 | behavior_only | test | gradient_diagnostic | 0.0180444 | 22.5965 | False |
| 43 | behavior_only | test | local_evolution | 0.0233122 | 0 | True |
| 43 | behavior_only | test_shift | no_edit | 0.0405105 | 0 | True |
| 43 | behavior_only | test_shift | gradient_diagnostic | 0.0316637 | 21.8383 | False |
| 43 | behavior_only | test_shift | local_evolution | 0.0405105 | 0 | True |
| 43 | scrambled_weights | test | no_edit | 0.0233122 | 0 | True |
| 43 | scrambled_weights | test | gradient_diagnostic | 0.0180444 | 22.5965 | False |
| 43 | scrambled_weights | test | local_evolution | 0.0233122 | 0 | True |
| 43 | scrambled_weights | test_shift | no_edit | 0.0405105 | 0 | True |
| 43 | scrambled_weights | test_shift | gradient_diagnostic | 0.0316637 | 21.8383 | False |
| 43 | scrambled_weights | test_shift | local_evolution | 0.0405105 | 0 | True |

| Seed | Arm | Split | Random mean active | Teacher error midrank % | Ties |
|---|---|---|---:|---:|---:|
| 17 | weights_behavior | test | 0.0245172 | 0 | 0 |
| 17 | weights_behavior | test_shift | 0.0404746 | 0 | 0 |
| 17 | behavior_only | test | 0.021264 | 73.4375 | 17 |
| 17 | behavior_only | test_shift | 0.0371429 | 26.5625 | 17 |
| 17 | scrambled_weights | test | 0.0211903 | 50 | 32 |
| 17 | scrambled_weights | test_shift | 0.0370782 | 50 | 32 |
| 29 | weights_behavior | test | 0.0259142 | 3.125 | 0 |
| 29 | weights_behavior | test_shift | 0.0403994 | 3.125 | 0 |
| 29 | behavior_only | test | 0.0257099 | 62.5 | 0 |
| 29 | behavior_only | test_shift | 0.040329 | 62.5 | 0 |
| 29 | scrambled_weights | test | 0.0258972 | 9.375 | 0 |
| 29 | scrambled_weights | test_shift | 0.0405229 | 12.5 | 0 |
| 43 | weights_behavior | test | 0.0281898 | 0 | 0 |
| 43 | weights_behavior | test_shift | 0.0456768 | 0 | 0 |
| 43 | behavior_only | test | 0.0233208 | 12.5 | 0 |
| 43 | behavior_only | test_shift | 0.0405143 | 15.625 | 0 |
| 43 | scrambled_weights | test | 0.0261269 | 6.25 | 0 |
| 43 | scrambled_weights | test_shift | 0.0438127 | 6.25 | 0 |

## First-round true and scrambled pairs

These rows compare round one directly. Best-of-three choices do not enter this comparison.

| Seed | Condition | Valid | Accepted | Split | Active MSE | Hazard MSE |
|---|---|---|---|---|---:|---:|
| 17 | weights_behavior | True | True | test | 0.017443 | 0.00142458 |
| 17 | weights_behavior | True | True | test_shift | 0.0301781 | 0.00276772 |
| 17 | scrambled_weights | True | False | test | 0.021912 | 0.00142458 |
| 17 | scrambled_weights | True | False | test_shift | 0.0376946 | 0.00276772 |
| 29 | weights_behavior | True | True | test | 0.0209805 | 0.0149577 |
| 29 | weights_behavior | True | True | test_shift | 0.0332975 | 0.0194934 |
| 29 | scrambled_weights | True | True | test | 0.0251169 | 0.0149402 |
| 29 | scrambled_weights | True | True | test_shift | 0.0396021 | 0.0194018 |
| 43 | weights_behavior | True | True | test | 0.0192423 | 0.00132072 |
| 43 | weights_behavior | True | True | test_shift | 0.0338264 | 0.00253306 |
| 43 | scrambled_weights | True | True | test | 0.0199738 | 0.00132072 |
| 43 | scrambled_weights | True | True | test_shift | 0.0349342 | 0.00253306 |

## Capture and usage

Candidate counts: {"accepted": 19, "invalid": 0, "selected_no_edit": 1, "valid": 21, "valid_rejected": 2}.

Estimated API cost: $6.291398. This uses saved token usage at $10/M ordinary input, $1/M cached input, $12.50/M cache-write input and $50/M output. It includes calibration responses saved beneath the artifact directory. This is an estimate, not an invoice. Coding-agent token usage is unavailable.

Candidate/response-pattern failures: 0. The earlier TLS failure is archived separately under data/transport_failures and does not match the response-file suffix counted here. Details and raw token counts are in summary.json.
