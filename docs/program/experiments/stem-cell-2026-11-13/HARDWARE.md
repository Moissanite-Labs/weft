# Bounded Apple Silicon readiness record

data/environment-readiness.json preserves a read-only probe of the current interpreter and aggregate hardware/memory counters. It records no credentials, machine serial number, process listing or personal path. No package was installed and no training or performance benchmark was run.

| Item | Observed value |
| --- | --- |
| Processor | Apple M1 Max, arm64 |
| Model family | MacBookPro18,2 |
| Physical memory | 68,719,476,736 bytes, or 64 GiB |
| Reported physical/logical CPUs | 10 / 10 |
| Python | 3.14.6 |
| NumPy | 2.5.4, available |
| certifi | 2026.10.23, available |
| PyTorch / MLX | Not installed in the probed default Python environment |

The memory-pressure query reported a system-wide free percentage of 78% at capture. Swap counters separately reported about 19,305 MiB used. These are different aggregate counters at one moment. Swap occupancy can include earlier activity and does not by itself establish current contention or safe capacity for a new large allocation. The probe makes no throughput or accelerator-speed claim.

## What unified memory contributes

Apple documents that its GPUs share system memory with the CPU. Metal shared resources still require correct ordering of CPU/GPU access. This can reduce explicit copies and storage duplication, without making synchronization free.

[Apple GPU storage modes](https://developer.apple.com/documentation/metal/choosing-a-resource-storage-mode-for-apple-gpus), [shared-resource synchronization](https://developer.apple.com/documentation/metal/mtlstoragemode/shared).

MLX places arrays in a shared memory pool and selects the execution device for operations. Its lazy evaluation separates graph construction from actual execution. These are useful array/runtime properties, rather than evidence of automatic self-modification or learned adaptation.

MLX is absent from the currently probed interpreter, so no MLX computation is claimed here. [MLX unified-memory documentation](https://github.com/ml-explore/mlx/blob/main/docs/src/usage/unified_memory.rst), [MLX overview](https://ml-explore.github.io/mlx/build/html/index.html).

NumPy is available, but the registered pilot uses exact Python integer arithmetic and Lean on CPU, without a NumPy dependency. A future accelerator comparison would need an explicitly installed, pinned backend, matched precision and workload, synchronization around timing, and captured warmup/measurement rules. That comparison is outside this bounded readiness probe.

PyTorch absence also means no PyTorch MPS availability test was made, without implying that the hardware lacks Metal support.

## Existing teacher transport

The earlier teacher_api.py and batch_api.py use Python's urllib Responses client and certifi, rather than an installed model SDK. They receive a key through a hidden prompt and keep it in memory. No persistent credential path is defined by those workers. The root operator separately owns credential access for the new authorized experiment. This readiness work did not search secret stores or use a key.

The prior transport sets storage off, retains observable message output and returned usage, and excludes reasoning items. Raw Authorization headers must never enter artifacts.

If request/response metadata are captured for this experiment, use explicit safe fields such as request hashes, model, status, timing, usage and permitted provider request identifiers. Preserve normalized failures and unknown-charge states separately from successful response accounting. Cost estimates remain distinct from invoices.
