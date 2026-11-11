# What can be used now

Companion to the [convergence plan](convergence-plan.md) and [variant register](variants.md), for [#39](https://github.com/Moissanite-Labs/weft/issues/39). Baseline: `main@94b9064f`, reviewed 2026-11-08. Commands below are existing entrypoints and a proposed local runbook, not a claim that they have run on the owner's Mac.

The user reports an M1 MacBook, 64 GB RAM, Chrome, and macOS “Golden Gate 27.0.1.” Preserve that report as given. Probes confirmed: Apple M1 Max, 64 GB RAM (68,719,476,736 bytes), macOS 27.0.1 (Build 26A434), architecture `arm64`, Google Chrome 157.0.8103.50, Python 3.14.6, and PyTorch 2.15.0 (`mps_built: true`, `mps_available: true`).

The Paper 1 experiments and runtime suite ran on this Apple Silicon machine on 2026-11-10. The CPU run (`--device cpu`) reproduced the committed numbers in `results.json` (`0.278059` mean final error ratio) with zero numerical differences under `--check`. An opt-in MPS baseline run (`--device mps`) recorded execution in `papers/01-models-as-cells/results-mps-m1.json`.

## Capability by environment

| Capability | Usable now / purpose | Requirements and present limit |
|---|---|---|
| C2 predicates and C11 header | Local invariant experiments and Python/C checks. | Python and C compiler. Defaults and complete cross-language parity remain an open work item; these are numerical checks, not a proof of all system behavior. |
| C3 graph reducer and BCP | Local graph experiments, serializer and existing tests. | Python plus C2. Malformed input, continuation state and exhaustion need stronger coverage; GPU reduction and formal language guarantees are not established. |
| C1 Plasm harness | Bounded matrix adaptation, baseline checks, watermark experiments and shared-memory teardown. | NumPy, Torch; CPU path or MPS if the installed backend reports available. This is not general self-modifying application software or demonstrated process isolation. |
| Host and fixture telemetry | Inspect host probes; exercise deterministic frame and packet producers. | Python. Use source labels; Linux CPU evidence does not prove Darwin/SMC probes. Live harvesting requires separate provenance/freshness validation. |
| Aywa in Chrome | Procedural field, mixer, spatial navigation and widgets. | Local HTTP server, JavaScript; WebGPU availability is runtime-dependent, with Canvas2D fallback. Current reading cadence uses a heuristic. No model per pixel is running. |
| Laya feasibility work | Model-responsive web is a concrete candidate for a bounded experiment. | The English 421M [model](https://huggingface.co/convaiinnovations/laya) and [r4ai browser runtime](https://github.com/r4ai/laya-web) existence were checked on 2026-11-08. That runtime targets a different multilingual 322M checkpoint, with listed browser assets totaling about 934 MB. API, artifact licenses, cold start, memory and UX remain to be validated; no model was downloaded or executed for this assessment. |
| C5 ledger simulator and hashing | Offline economic/ABI experiments. | Python plus C2. A simulator pass is not Solidity compilation, EVM execution or chain deployment. |
| Original corpus and whitepapers | Sources, alternatives, hypotheses and design research. | Read with the variant register and current evidence ledger. Narrated execution and proposed APIs are not installation instructions or proof. |

## Establish a Mac baseline

From a checkout of this repository, record the outputs with the commit SHA in a private test report. These are read-only probes; `system_profiler` may take a little time.

```bash
git rev-parse HEAD
sw_vers
uname -m
sysctl -n hw.memsize
system_profiler SPHardwareDataType
python3 --version
node --version
cc --version
```

In Chrome, record the version from `chrome://version` and WebGPU status from `chrome://gpu`. Do not publish hardware identifiers from the profiler; the report needs chip, memory, architecture, OS build and software versions. A failed or unavailable probe is a result to retain.

## Prepare a local Python environment

The current CI targets Python 3.12 and Node 20, installs NumPy/Torch without a dependency lock, and uses a C11 compiler. Use an available Python 3.12 installation and compiler; on macOS, the compiler is normally supplied by Xcode Command Line Tools. This runbook does not install system tools automatically.

Create the virtual environment beside the repository so the checkout stays clean:

```bash
python3.12 -m venv ../weft-venv
source ../weft-venv/bin/activate
python -m pip install numpy torch
python -m pip freeze
```

This is a bootstrap recipe, not a reproducible lockfile. Retain installed versions with results; adding declared and pinned component dependencies is planned work. Use the normal platform Torch package on the Mac, rather than CI's Linux CPU wheel index.

Check what the installed backend can actually do:

```bash
python - <<'PY'
import platform
import torch
print({
    "machine": platform.machine(),
    "torch": torch.__version__,
    "mps_built": torch.backends.mps.is_built(),
    "mps_available": torch.backends.mps.is_available(),
})
PY
```

`mps_available: true` is an availability check, not a performance or correctness result. CPU and MPS comparisons need separate runs of the same workload, recorded device selection and tolerances. `papers/01-models-as-cells/experiments.py` supports explicit `--device {cpu,mps}`, `--check`, and `--check-mps` flags. Default execution remains CPU for deterministic CI checks.

On the Apple M1 Max host, CPU execution runs in `float32`, as does MPS: the Plasm cycle builds float32 tensors on both devices, and only E1 uses float64. It records an 81.24 ms median elapsed time per 12-generation cycle and reproduces the committed 0.278059 mean final error ratio.

MPS execution also runs in `float32` because PyTorch MPS lacks `float64` support, so E2 and E5 have the same precision on both devices. It records a 121.96 ms median elapsed time and a 0.277101 mean final error ratio, a 0.05% to 1.5% per-seed difference from the CPU run. The spread comes from the MPS generator drawing a different noise stream, not from precision. Both devices yield identical gate decisions: 15.0 degrees first rejected angle, 120/120 committed proposals, zero core-row drift, and full watermark retention.

Compare the actual host record with the current [PyTorch MPS requirements](https://developer.apple.com/metal/pytorch/). Native Torch/MLX experiments and Chrome WebGPU/ONNX experiments are different stacks; a working native backend does not validate a browser model path.

## Run the existing local checks

Run these from the repository root with the environment active. No networked weight transfer, contract deployment or privileged hardware operation is needed.

```bash
python -m unittest discover -s weft/runtime/invariants -p 'test_*.py'
python -m unittest discover -s weft/runtime/plasm -p 'test_*.py'
python -m unittest discover -s weft/runtime/ic -p 'test_*.py'
python -m unittest discover -s weft/runtime/telemetry -p 'test_*.py'
python -m unittest discover -s weft/runtime/gateway -p 'test_*.py'
python -m unittest discover -s weft/runtime/aywa -p 'test_*.py'
node --test weft/runtime/aywa/test_*.mjs
python weft/runtime/aywa/weft_daemon.py --self-test
python weft/runtime/aywa/site_selftest.py
python weft/runtime/core/selftest.py
python weft/runtime/mac/darwin_sysctl.py
python weft/runtime/mac/metal_loom.py
python papers/01-models-as-cells/experiments.py --check
python papers/01-models-as-cells/experiments.py --check-mps
git status --short
```

The Mac entrypoints are compatibility wrappers around current C1/C6 code. Their names do not establish native Metal kernels, direct CPU/GPU aliasing or hardware actuation. `metal_loom.py` currently reports some wrapper arguments without forwarding them into the experiment; use the actual implementation and report when interpreting parameter changes.

C1 copies shared-memory views into independent device tensors. “Zero-copy” therefore needs a named boundary; it does not describe the whole experiment. A fixed arena also does not prove an allocation-free Python execution path.

## Preview Aywa without publishing

Use a disposable directory and the existing public allow-list staging function. Calling the full `sync_pages_seed.py` CLI also regenerates tracked fixture assets; it is not necessary just to preview the checked-out site.

```bash
python - <<'PY'
import tempfile
from scripts.sync_pages_seed import stage_pages_dist
preview_dir = tempfile.mkdtemp(prefix="weft-preview-")
print(stage_pages_dist(preview_dir))
print("Serve this directory:", preview_dir)
PY
```

Use the printed directory in this command, then open `http://127.0.0.1:8000/` in Chrome:

```bash
python -m http.server 8000 --bind 127.0.0.1 --directory /tmp/weft-preview-REPLACE
```

On macOS the printed temporary path may start with `/var/folders/`; use that exact path, not the example. Check initial load and later telemetry updates, the browser console and worker, mobile-width layout, keyboard access, reduced motion and both renderer paths. Record which renderer actually ran. A successful screenshot or static selftest alone does not establish worker behavior; the startup defect is tracked in [#41](https://github.com/Moissanite-Labs/weft/issues/41).

The bundled data is a fixture. The exported widget pages can load third-party assets, so offline behavior must be checked rather than assumed. Model-responsive/Laya experiments are separate future work; the present reading-cadence effect is not model inference.

For that experiment, choose a specific checkpoint/runtime pair from the [variant register](variants.md). Current `r4ai/laya-web` documentation uses `load()` and `agent.predict(state, questions)` with `criteria` and `result.answers`; the corpus's `LayaWebAgent`/`options` example should not be copied as working code. Evaluate the upstream `laya-ts` path separately. If using ONNX Runtime WebGPU, its [worker guidance](https://onnxruntime.ai/docs/tutorials/web/env-flags-and-session-options.html) requires loading the runtime directly in a dedicated Worker rather than enabling `env.wasm.proxy`. Keep model acquisition and inference out of the default site until the experiment has measured its actual cost and behavior.

## What needs another gate

There is no actual local-EVM project at this baseline; build that before interpreting C5 tests as contract verification. There is no extracted C8 mesh, bootable Weft OS, RTL/FPGA implementation, fabricated chip, trained self-healing application, or deployed civilizational governance system demonstrated by these commands. Each remains a preserved branch with its own next experiment. The [convergence plan](convergence-plan.md) separates near-term work from hardware, R&D and societal dependencies.
