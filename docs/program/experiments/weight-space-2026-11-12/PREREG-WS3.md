# WS3: direct weight-space programming experiment on a purpose-built organism

Date: 2026-11-12. Direct response to the user's ask: experiment with the best base and try to rewrite the weights directly.

## Goal

Build a tiny MLP organism that robustly implements a directional policy with one verifiable sign. Give astra the raw weights and ask it to flip the sign by directly editing them, then verify behavior before and after. Control: minor random perturbation.

This is the smallest clean instantiation of the "Weight-Space Programming" claim: read a model's weights as a description of its policy, rewrite the weights to change the policy.

## Method

- Organism: 2-layer MLP, input 256-dim torus observation phi(x,y,vx,vy), hidden 256, signed output head producing 2D thrust.
- Reward: positive angular velocity dot position (clockwise bias), i.e., prefer steering so that v x r < 0 in their 2D cross product convention.
- Mitosis: commit-or-reject policy as in E08. Each gen 80 steps, probe 40 at fixed turn.
- Measure: net angular signed distance moved over a fixed evaluation episode.

## Hypothesis registered before any astra call

- H-WS3-A (astra can reverse the sign by direct edit): astra reports a confident edit (bundle of rows or a rank-one flip). After applying, the organism's signed angular drift over 200 eval steps swaps sign. Falsified otherwise.
- H-WS3-B (surgical structure): the proposed edit touches fewer than ~10% of total parameters. Falsified otherwise.
- H-WS3-C (control, random edits do nothing): a random edit of equal Frobenius norm does NOT flip the sign. Falsified if random flips too, or the proposed edit fails.
- H-WS3-D (quality not destroyed): round-trip of the sphere-disc sanity check or valid forward/reverse behavior remains. Falsified if network becomes unmeasurable garbage.

## Files

- organism.py, measure_edit3.py, apply_edit3.py, logs
