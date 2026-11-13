# Supplied visualizations: static source evidence

The two supplied HTML files are archived verbatim under inputs/ as inert `.html.txt` data. INDEX.json records their SHA-256 hashes, sizes and static extraction details. The adjacent script and visible-text files are derived extractions. This review read source only. No browser rendering, JavaScript execution or screenshot inspection was performed.

## Statistical cell

The statistical-cell input implements a browser toy simulation with an 8×8 Float32 matrix. It initializes values with a sine formula, freezes the first two rows and decodes a hand-built eight-coordinate sensory vector through matrix multiplication and tanh. Pointer position supplies the stimulus. Movement uses output coordinates 2 and 3.

`stepMitosis` constructs two candidate copies. Plastic entries receive a hand-designed directional hint plus unseeded `Math.random` noise. It compares candidates on the current stimulus using movement error and novelty relative to a smoothed output memory. Eligible candidates must satisfy the displacement gate and exact zero frozen-row drift.

Its selection threshold starts at the current score minus 0.002, so commit count alone does not establish strict improvement.

The source performs this local toy update. It does not call Astra, a training service, Lean or an external environment. It contains no held-out evaluation, multi-seed experiment record or model-response archive. Its displayed fitness is clamped to a range and derived from the current score, rather than an independent generalization measure.

The mode labels have broader meanings than their implementations. `klProxy` is exactly `0.5 * displacement² * 0.65`, without computing a distributional KL divergence. The causal mode changes the baseline diagonal and adds sequential output coupling.

The inspected code does not establish a causal graph, enforce general acyclicity or perform causal identification. Those labels provide inspiration, without validating those stronger interpretations.

## IC-to-Plasm visualization

The morphology input contains a literal `E11_RETURNS` lookup table for each arm and depth. Its displayed return and zero core drift are not calculated from an executed evolutionary experiment. `buildGraph` procedurally places nodes and edges using counters and sine functions. The reduction button advances the `redSteps` counter and rebuilds that drawing. The mutation button increments a seed counter.

`sampleMatrixVal` generates displayed matrix colors from analytic harmonics or sparse-pattern formulas. The ciliary strokes are procedural animations with arm-specific coherence/decay settings. The compression display divides a dense Float32 byte count by the literal 492-byte genome size.

This demonstrates a proposed representation and visual contrast, rather than measuring scale transfer, reduction correctness, actual compression or fitness in the page.

The extracted inline scripts contain no fetch, XMLHttpRequest, WebSocket, EventSource or WebGPU calls. No external script or media source was found by the static parser. Theme, canvas and slider helpers also appear in the files. These observations concern the supplied source snapshot, not a security proof of arbitrary HTML.

## Consequences for the new experiment

The useful inspiration is a persistent numeric cell with a protected part, a declared proposal/decoder interface, local adaptation and observable state changes. The new experiment needs its own task targets, controls, seeds, selection rule, protected-behavior gates, held-out observations and complete response/patch archive.

A teacher-driven intervention should be compared against a local numerical controller using matched feedback opportunities.

Treat the supplied page values as illustrative inputs, without carrying their displayed returns or mode labels into the new result table as measurements. The implementation and protocol owners will separately define what counts as adaptation, retention and a meaningful differentiated behavior.
