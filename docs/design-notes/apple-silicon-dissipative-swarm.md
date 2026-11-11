# Design Note: Apple Silicon Unified-Memory Micro-Swarms and Dissipative Heredity Convergence

Date: 2026-11-10
Author: `agy-orbit`
Related Codebases:
- **C1 / Mac Loom**: `weft/runtime/plasm/plasm.py`, `weft/runtime/mac/swarm_loom.py`
- **C2 / Safety Gate**: `weft/runtime/invariants/`
- **C3 / Checkable Computation**: `weft/runtime/ic/ic_vm.py`
- **Agent-Layer Twin (`razi-cells`)**: `docs/program/experiments/razi-cells-laws-2026-11/` (`metab.py`, `lineage.py`, PR #118)
- **Tensor-Layer Experiment (`E14`)**: `docs/program/experiments/apple-silicon-swarm-2026-11/`

---

## 1. The First-Principles Diagnosis: Why Early Colonies Stalled

Across the first two phases of the research program (`Weft` Paper 1 and `razi-cells` `E07` through `L1`), two complementary failure modes appeared at opposite ends of the stack.

### 1.1 The Agent-Layer Bottleneck (`razi-cells` `E07` to `L1`)
In `razi-cells`, each cell ran as an operating-system process that issued 2 to 10 second HTTPS requests to a 100B+ parameter cloud model, wrote a monolithic Python file to disk, and queued behind a global file lock (`.bench.lock`) for wall-clock timing (`time.perf_counter`).

This architecture created three structural limits:
1. **Throughput starvation**: A 4-generation run of 178 cells (`L1`) required 41 minutes of wall time because network latency and `.bench.lock` serialized the colony.
2. **Rational coasting (`K20`, `L6`)**: When `L1` introduced germline heredity, 65 of 70 later-generation heirs (`92.9%`) performed zero edits or variant rounds and rested immediately. Because resting returned unspent birth energy to the lineage store without penalty, coasting on a passing generation-0 body was the expected-value optimum.
3. **Symmetric basin anchoring (`K1`, `L7`)**: Placing the parent's full source file in the heir's working directory anchored the language model to local edits around generation 0. On tasks requiring a discrete algorithmic shift (`compress`), blank restarts (`arm b`) found the ceiling in 2 of 3 runs (`1.542`), whereas hereditary lineages (`arm h`) found it in 0 of 3 (`1.20`).

### 1.2 The Tensor-Layer Bottleneck (`Weft` Paper 1 `E2` and `W1`)
Conversely, in `Weft` Paper 1 (`weft/runtime/plasm/plasm.py`), the substrate was local and fast, but exhibited two physical mismatches on Apple Silicon:
1. **Single-cell kernel dispatch (`W1`)**: Running a single `256x256` cell matrix on Apple Metal Performance Shaders (`mps`) was slower than CPU (`115 ms` vs `61 ms` per 12-generation cycle). Dispatching individual small matrix kernels across the Python-to-Metal bridge paid ~50 microseconds of launch overhead per op while leaving 31 of the 32 GPU cores idle.
2. **High-dimensional isotropic curvature penalty (`Paper 1 E2`)**: In Paper 1 `E2` (and its `mps` reproduction), the exploratory lineage `Beta` ($\sigma_\beta = 5 \sigma_\alpha$) won **0 out of 120** generations (`0%`).

---

## 2. Two Mathematical Laws of Evolution on Apple Silicon

Both tensor-layer mismatches have exact mathematical explanations and direct hardware fixes, verified on the Apple M1 Max (64 GB unified LPDDR5 at 400 GB/s, 32-core Metal 4 GPU, 8 P-cores, 2 E-cores, Apple AMX coprocessors).

### 2.1 Law 1: Unified Memory Turns Colony Width from $O(N)$ into $O(1)$ Wall Time
On discrete PCIe accelerators, CPU processes and GPU tensors live in separate physical RAM pools. On Apple Silicon, the CPU cores, the AMX matrix units, the 32-core Metal GPU, and the 16-core Neural Engine share **one physical address space** (`MTLResourceStorageModeShared` / POSIX `shm`).

When a colony of $N = 512$ cells is represented not as 512 OS processes, but as a single contiguous 3D tensor `[512, 256, 256]` inside a shared-memory arena (`StratifiedSwarmArena`), all 512 forward passes execute in one batched matrix multiply (`torch.bmm` / `matmul`):

| Execution Mode (`512` cells, `256x256` forward pass on M1 Max) | Total Batch Time | Time per Cell | Speedup vs Serial CPU |
|---|---|---|---|
| Serial CPU loop (`for i in range(512)`) | `10.70 ms` | `20.90 us` | `1.0x` |
| Batched CPU (`Accelerate` / Apple AMX) | `9.62 ms` | `18.79 us` | `1.1x` |
| **Batched Metal MPS (`32-core GPU`, `[512, 256, 256]`)** | **`0.88 ms`** | **`1.72 us`** | **`12.2x`** |

Evaluating 512 cells in parallel on Metal MPS takes `0.88 ms` (`1.72 microseconds` per cell). Width is no longer a serial bottleneck.

### 2.2 Law 2: Why Isotropic `Beta` Fails in High Dimensions, and Why Low-Rank Horizontal Transfer Wins
Consider a weight matrix $W \in \mathbb{R}^{d \times d}$ with $D = d(d - c)$ adaptable peripheral parameters (for $d = 256$ and frozen core rows $c = 64$, $D = 49,152$).

For a second-order loss $L(W)$ with gradient $g = \nabla L(W)$ and positive-definite Hessian $H = \nabla^2 L(W)$, an isotropic Gaussian mutation $\Delta W \sim \mathcal{N}(0, \sigma^2 I_D)$ has expected loss change:

$$\mathbb{E}[\Delta L] \approx \mathbb{E}[\langle g, \Delta W \rangle] + \frac{1}{2} \mathbb{E}[\Delta W^\top H \Delta W] = 0 + \frac{1}{2} \sigma^2 \operatorname{Tr}(H)$$

Even for the best of two samples, the useful directional projection along $-g$ scales only as $\sigma \lVert g \rVert_2$, whereas the orthogonal curvature penalty scales with the full ambient dimension as $\frac{1}{2} D \bar{\lambda} \sigma^2$.
- When Lineage `Alpha` uses a tiny $\sigma_\alpha$, the linear term $\sigma_\alpha \lVert g \rVert_2$ slightly exceeds $\frac{1}{2} D \bar{\lambda} \sigma_\alpha^2$, yielding small creeping wins.
- When Lineage `Beta` scales the step size by $k = 5$ ($\sigma_\beta = 5 \sigma_\alpha$), the linear signal grows by $5\times$, but the orthogonal noise penalty across $D = 49,152$ dimensions explodes by $k^2 = 25\times$. Blind isotropic exploration is mathematically guaranteed to lose as $D$ grows.

Now replace isotropic `Beta` with **Low-Rank Subspace Mutation + Horizontal Gene Transfer (`hgt_beta`)**:

$$\Delta W_{\text{Beta}, i} = P_{\text{mask}} \odot \left( \eta_{\text{hgt}} (W_{\text{peer}(i)} - W_i) + \sigma_{\text{sub}} U_i V_i^\top \right), \quad U_i, V_i \in \mathbb{R}^{d \times r}, \quad r \ll d$$

1. **Directional Drift ($\eta_{\text{hgt}} (W_{\text{peer}(i)} - W_i)$)**: Splices the delta toward a proven high-fitness peer in the same ecological niche. This vector lies strictly inside the descent cone of the niche objective rather than orthogonal noise space.
2. **Low-Rank Innovation ($U_i V_i^\top$, rank $r = 4$)**: Restricts random exploration to a $2dr$-dimensional tangent subspace ($2 \times 256 \times 4 = 2,048$ degrees of freedom instead of $49,152$), cutting the orthogonal curvature penalty by an order of magnitude while preserving structured cross-row updates.

Measured on the M1 Max (`512` cells across `4` niches, `100` generations = `51,200` mitotic trials under the `C2` Frobenius ball gate $\lVert W' - W_0 \rVert_F \le R$):
- **Paper 1 `blind_beta`**: `Alpha` won `9,738` times, `Beta` won **`0` times (`0.0%`)**, relative error fell `-0.26%`.
- **Subspace + Horizontal Transfer (`hgt_beta`)**: `Alpha` won `3,933` times, `Beta` won **`8,941` times (`69.4%`)**, relative error fell **`-2.78%` (`10.7x` faster)**.
- Across seeds 0 to 9 the pattern holds: blind `Beta` won 0 in every seed, `hgt_beta` took 70.6% of wins (62.6% to 74.9%) and cut error 10.8x faster (10.1x to 11.2x). Script and data: `docs/program/experiments/apple-silicon-swarm-2026-11/probe/` (Probe P0).

---

## 3. Mapping the Micro-Swarm to Apple Silicon's Four Compute Engines

A biological organism does not duplicate a 3-billion-base-pair genome cleanly per process or pipe text over a network between cells. Every cell shares **one frozen nuclear genome** in the same medium and differentiates through **lightweight cytoplasmic state** and **specialized organelles**.

On Apple Silicon, the four on-die compute engines map one-to-one onto four biological layers sharing unified DRAM:

```
+-----------------------------------------------------------------------------------+
|            APPLE SILICON UNIFIED MEMORY ARENA (64 GB LPDDR5 @ 400 GB/s)           |
|                                                                                   |
|  [ Shared Frozen Nucleus ]     [ StratifiedSwarmArena (POSIX shm / MTLBuffer) ]   |
|  - Base Model / Backbone       - focal_weights:        float32[N, D, D]           |
|  - Core Watermark Rows W0      - low_rank_adapters:    float32[N, D, r]           |
|  - Harness Validation Kits     - organelle_graphs:     int32[N, MAX_NODES, 3]     |
|                                - energy_ledger:        float32[N]                 |
|                                - niche_specialization: int32[N]                   |
|                                - chemostat_bounty:     float32[M_niches]          |
+-----------------+-----------------------+-----------------------+-----------------+
                  |                       |                       |
                  v                       v                       v
   +--------------+-------+   +-----------+-----------+   +-------+---------------+
   | 32-Core Metal 4 GPU  |   | 8 Firestorm P-Cores   |   | 2 Icestorm E-Cores    |
   | + CPU AMX Coprocessor|   | (Lock-Free Workers)   |   | (QOS_BACKGROUND)      |
   +----------------------+   +-----------------------+   +-----------------------+
   | - Batched [N, D, D]  |   | - Parallel C3 IC VM   |   | - Basal upkeep decay  |
   |   forward evaluation |   |   & bytecode organelles|  | - Apoptosis & spore   |
   | - Low-rank U @ V^T   |   | - Deterministic step  |   |   re-colonization     |
   |   & HGT proposals    |   |   counting (ITRS /    |   | - SHA-256 lineage     |
   | - Vectorized C2 norm |   |   opcode count, zero  |   |   hash chaining       |
   |   & watermark gate   |   |   .bench.lock)        |   | - 60 Hz Eido telemetry|
   +----------------------+   +-----------------------+   +-----------------------+
```

1. **Metal GPU (32 cores) + AMX (`1–5 ms` timescale)**:
   Executes batched tensor forward passes, rank-$r$ subspace mutations, horizontal weight transfers, and vectorized `C2` safety gate checks ($\lVert W_i' - W_{0,i} \rVert_F \le R$) across all $N$ cells in parallel.
2. **8 P-Cores (`5–50 ms` timescale)**:
   Execute discrete symbolic organelles (`FlatCombinatorVM` interaction nets from `weft/runtime/ic/ic_vm.py` or compiled bytecode/AST pipelines) in parallel threads without OS process forks. Fitness is scored by **deterministic reduction/instruction counts (`ITRS`)**, eliminating wall-clock timing jitter and `.bench.lock`.
3. **16-Core ANE + Local/Cloud Mutagen (`50–500 ms` timescale)**:
   Runs a shared local backbone (or triggers a rare asynchronous `Exo` call to a frontier model only when a niche's chemostat bounty crosses a stall threshold) to synthesize new discrete organelles for the shared pool.
4. **2 E-Cores (`Continuous background` timescale)**:
   Run homeostatic bookkeeping, novelty-archive kNN indexing, SHA-256 execution-record verification, and 60 Hz Eido/Observatory telemetry frames on efficiency cores (`QOS_CLASS_BACKGROUND`) so measurement never perturbs P-core or GPU throughput.

---

## 4. The Convergence of PR #118 (`L2` Dissipative Heredity) and `E14` (`swarm_loom.py`)

PR #118 (`docs/program/experiments/razi-cells-laws-2026-11/`) and `E14` (`weft/runtime/mac/swarm_loom.py`) were designed independently in parallel, yet arrived at the exact same thermodynamic diagnosis: **evolution stalls whenever rest is free, inheritance is symmetric, and rewards are static**.

Combining PR #118's three causal laws (`Law 2a`, `Law 2b`, `Law 2c`) with `E14`'s vectorized multi-niche tensor swarm yields a single unified mathematical model that operates identically at both the **Tensor Layer (`C1`/`C2`)** and the **Agent Layer (`razi-cells`)**.

### 4.1 Unified Law 1: The Weismann Soma Barrier (`--weismann` $\leftrightarrow$ Vectorized Dissipative Upkeep)
- **In PR #118 (`metab.py`)**: Birth energy $E_0$ is sunk into the soma (`CELL_WEISMANN=1`). An heir born with a germline body returns unspent energy to `store-<kit>` at rest **only if** it achieves a scored win beyond noise (`fit > 0` or `earned > 0`). Otherwise, unspent birth energy dissipates to `0.0`.
- **In `swarm_loom.py` (`mode="dissipative_chemostat"`)**: Every cell pays basal upkeep $u_{\text{basal}} = 2.0$ per generation. Tile bounty banks only for cells with at least one accepted update (`accepted_updates > 0`). A cell that never adapts collects nothing, starves and is replaced.
- **Unified effect**: Coasting has negative expected return at every layer. A lineage that stops mutating drains its energy store to zero and undergoes apoptosis, freeing its slot for a dividing daughter.

### 4.2 Unified Law 2: Multi-Niche Chemostat Flux and Gap-Potentiated Payouts (`--chemostat`, `--gap-pay` $\leftrightarrow$ Competitive Tile Bounties)
- **The failure mode of simple foraging**: In a multi-niche environment with $M$ input tiles (where tile 1 is easy/linear and tile 8 is hard/ill-conditioned), a naive foraging swarm crowds onto the easiest tiles first because early mutations win more often there.
- **PR #118's contribution (`lineage.py` + `metab.py`)**:
  1. *Chemostat Flux (`--chemostat`, `--flux`)*: Every generation in which niche/kit $m$ fails to produce a germline replacement adds unharvested free-energy flux $\Phi_m$ to that niche's bounty pool:
     $$B_m(t + 1) = \begin{cases} B_{m,0} & \text{if niche } m \text{ improved at step } t \\ B_m(t) + \Phi_m & \text{if niche } m \text{ stalled at step } t \end{cases}$$
  2. *Gap-Potentiated Reward (`--gap-pay`)*: Payouts scale inversely with the remaining distance to the ceiling record $s_i \in [0, 1)$:
     $$R_{\text{eff}}(s_i) = \min\!\left(4 R_0, \frac{R_0}{\max(0.25, 1 - \min(s_i, 0.95))}\right)$$
- **Unified synthesis**:
  - When applied across all $M$ input tiles in `swarm_loom.py`, any neglected or hard tile $m$ accumulates a rising chemostat potential $B_m(t)$ every tick it goes unsolved, while already-crowded tiles stay at baseline $B_{m,0}$ split among many competitors.
  - Once $B_m(t)$ rises high enough, even a low-probability exploratory win on hard tile $m$ pays an outsized energy jackpot, **thermodynamically pulling spores out of crowded easy niches and into the hardest unsolved regimes without any central coordinator**.

### 4.3 Unified Law 3: Soma + HGT-Spore Asymmetric Division (`--spore` $\leftrightarrow$ `Alpha` + `hgt_beta`)
- **In PR #118 (`lineage.py`)**: Generation $\ge 1$ births split asymmetrically into a **Soma** (Birth 0, which inherits `.germ/<kit>/body` + `genome.md` to preserve and locally refine the incumbent) and a **Spore** (Births $\ge 1$, born into an empty code directory with `genome.md` and `LIBRARY.md` lessons to sample a fresh basin without code anchoring).
- **In `swarm_loom.py`**: Mitosis splits into **Lineage Alpha** (local cautious refinement around the parent matrix $W_i$) and **Lineage HGT-Beta** (low-rank subspace jump $U_i V_i^\top$ plus horizontal splice $\eta_{\text{hgt}}(W_{\text{champion}(m)} - W_i)$).
- **Unified synthesis (Directed Horizontal-Transfer Spores)**:
  - A purely blank spore in `razi-cells` breaks anchoring (`L7`), but must rebuild all helper plumbing from scratch using only text notes.
  - Conversely, giving an agent-layer **Spore** access to a **Shared Verified Organelle Shelf** (functions/modules exported by any lineage that passed unit contracts, indexed by behavioral signature) gives agent-layer spores the exact same mechanism as tensor-layer `hgt_beta`: the spore discards the parent's monolithic file (breaking anchoring) while importing working building blocks horizontally from peers across the colony.

---

## 5. Concrete Roadmap: From `E14` and `L2` to the Composed Organism (`E15` and `E16`)

Every step below builds directly on committed files in `Moissanite-Labs/weft` so any seat can pick up the next stage without re-deriving prior work:

| Stage | Target Files | What It Tests | Acceptance Criteria |
|---|---|---|---|
| **1. `E14` (Done, 3 of 5 held, see section 6)** | `weft/runtime/mac/swarm_loom.py`, `docs/program/experiments/apple-silicon-swarm-2026-11/` | Vectorized `[N, D, D]` MPS swarm, `hgt_beta` vs `paper1_blind`, competitive niche foraging across $M=8$ tiles | `H-S1` (`>=5x` MPS speedup), `H-S2` (`hgt_beta > 50%` win share vs `<5%` blind, `>=3x` error drop), `H-S3` (`8/8` niches, entropy `>=2.5` bits), `H-S4` (`0%` coasting), `H-S5` (`0` C2/watermark violations) |
| **2. `L2` (PR #118, ready to run)** | `docs/program/experiments/razi-cells-laws-2026-11/code/cells/{metab,lineage}.py`, `run/run_l2.sh` | Agent-layer Weismann soma (`--weismann`), Chemostat flux (`--chemostat`), Gap-pay (`--gap-pay`), Soma+Spore (`--spore`) | `L2-a` (`0` overdrafts), `L2-b` (`<20%` soma coasting vs `93%` in `L1`), `L2-c` (spore basin jump), `L2-e` (`O1` reach `>= h + 0.10`), `L2-f` (`>=6/12` post-gen-0 germline replacements) |
| **3. `E15` (Convergence: Dissipative Chemostat Swarm. Mode built, graded tiles not yet)** | `weft/runtime/mac/swarm_loom.py` (`mode="dissipative_chemostat"`) | Adds PR #118's per-tile Chemostat Flux $B_m(t) + \Phi_m$, Gap-Potentiated Payouts, and Weismann Soma Dissipation directly into the 512-cell MPS tensor swarm on graded-difficulty tiles (easy to extreme curvature) | On skewed-difficulty niches where uniform foraging leaves the hardest tiles under-solved, `dissipative_chemostat` reallocates spores to the hardest tiles and reduces worst-tile error by `>=2x` over `hgt_foraging` |
| **4. `E16` (Hybrid Organelle Loom)** | `weft/runtime/mac/organelle_loom.py` + `weft/runtime/ic/ic_vm.py` | Couples each cell's MPS routing/adapter head `[N, D, r]` to a composable DAG of `C3` / bytecode organelles executed on the 8 P-cores and scored by deterministic step counts (`ITRS`) | Zero `.bench.lock`, 100% bit-reproducible fitness, horizontal transfer of discrete organelles between spore lineages, and multi-stage task compounding |

---

## 6. Measured Results (E14 final seeded run, 2026-11-11)

Full record: `docs/program/experiments/apple-silicon-swarm-2026-11/README.md`. Amendments log: `PREREGISTRATION.md` in the same folder.

All four arms are zero-order. An earlier build gave the champion cell an analytic gradient. Its 0.77 error reduction is withdrawn.

| Arm | Beta win share | Error reduction | Niches covered | Idle survivors (of 256) |
|---|---|---|---|---|
| `paper1_blind` | 0.000 | 0.0017 | 1 of 8 | 173.3 |
| `hgt_isolated` | 0.838 | 0.0616 | 1 of 8 | 0.7 |
| `hgt_foraging` | 0.907 | 0.0559 | 8 of 8 | 4.1 |
| `dissipative_chemostat` (L2 laws) | 0.918 | 0.0410 | 8 of 8 | 0.0 |

Preregistered verdicts: H-S2, H-S3 and H-S5 held. H-S1 failed on the recorded run (4.55x against a 5.0x bar). Across four runs it measured 4.55x to 10.03x, driven by serial CPU timing noise. H-S4 failed: `hgt_foraging` kept 2 to 6 idle cells per seed.

What the convergence shows so far:

1. **Confirmed (exploratory)**: The Weismann gate from PR #118 closes the coasting loophole in a tensor swarm. Idle survivors fell from 4.1 to 0.0 across all 10 seeds. This is the tensor-layer analogue of the `L2-b` prediction (soma coasting below 20%, against 93% in `L1`).
2. **Cost found**: The gate kills more cells, and spores restart from `W0`. Error reduction fell 27% (0.0559 to 0.0410). PR #118's `L2` run should watch for the same trade: fewer coasters, but more lost progress per restart.
3. **Not yet tested**: Chemostat flux only helps when tiles differ in difficulty. E14 tiles are uniform. E15 needs graded tiles to test Law 2b.
