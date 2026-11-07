# Moissanite-Labs to Weft Synthesis Map

Date: 2026-11-07
Origin Anchor: `Moissanite-Labs/compass` Discussion #5

## 1. Origin Thread Lineage (`Moissanite-Labs/compass` Discussion #5)

Discussion #5 in `Moissanite-Labs/compass` documents the exact progression that produced the Desktop 8 Chrome session (`thread1-splicers-genesis-90133B.md` and `thread1-weft-main-84ADC9.md`):

1. **Splicer Architectural Seed**: Biological-machine symbiosis where components self-assemble and upgrade in place rather than relying on static external orchestration.
2. **Stratified Shared-Memory Bus**: Separation of fast focal tensor channels, sympathetic scalar telemetry, and hippocampal novelty archives over POSIX shared memory.
3. **Mitotic A/B Speculation and Thermodynamic Selection**: Parallel safe (`alpha`) and exploratory (`beta`) mutations scored jointly by task fitness and hippocampal novelty.
4. **Hardware Coupling and Provenance**: Direct ingestion of Apple Silicon thermal and memory pressure into the tensor bus, paired with weight-space watermarking and the three-contract governance triad.

## 2. Repository Disposition Across the 19 `Moissanite-Labs` Repositories

| Repository | Weft Plane | Disposition | Integration Path in Weft |
| :--- | :--- | :--- | :--- |
| `compass` | North-Star Spec | **Connect & Anchor** | Discussion #5 is the canonical origin record and feeds `MOISSANITE-SYNTHESIS.md` and `browser-sources/thread1-splicers-genesis-90133B.md`. |
| `synbios` | Mission Control | **Connect & Extend** | Live capability stewardship and dashboard telemetry stream into `runtime/aywa/github_harvester.py` (`SYNBIOS-MATRIX`). |
| `abios` | Cellular Runtime | **Absorb into Core** | Mitotic cell lifecycle (`PlasticOrganismCell`, `M1MaxOrganismCell`) is unified in `runtime/core/weft_plasm.py` (`ABIOS-PROTOCOL`). |
| `statos` | Kernel Substrate | **Connect & Absorb** | Bare-metal Darwin `sysctl`, Mach VM, and ARM64 EL1 cache-purge primitives map to `mac.md`, `almalga.md`, and `runtime/aywa/weft_daemon.py` (`STATOS-KERNEL`). |
| `mlx` | Tensor Engine | **Connect & Absorb** | Unified memory zero-copy array bindings power the 3-tier tensor bus in `runtime/core/weft_plasm.py` (`MLX-TENSOR-CORE`). |
| `ethos` | Constitutional Gate | **Absorb into Spec** | Invariant bounds and anti-rogue slashing rules merge into `ethos.md`, `govern.md`, and `TensionGovernor` (`ETHOS-GOVERN`). |
| `synmerit` | Provenance Ledger | **Absorb into Core** | Homomorphic watermark verification and the 85/15 royalty excision valve live in `ProvenanceRegistry` and `WeftTokenTissue` (`SYNMERIT-LEDGER`). |
| `exofab` | Silicon & Lithography | **Connect & Extend** | Physical fabrication and wafer yield physics connect directly to `terrafab.md`, `terrafab-calc.md`, and `terraweft.md` (`EXOFAB-SILICON`). |
| `exoframe` | Spatial Viewport | **Replace by Aywa** | Superseded by the single-pass WebGPU SDF + procedural ASCII viewport in `design/aywa.md` and `runtime/aywa/index.html` (`EXOFRAME-SHELL`). |
| `exorien` | Peer Handshake | **Absorb into Core** | Binary 104-byte magic-header peer handshake (`WEFT`) and UDP mesh splicing live in `README.md` Section 17 and `mac.md` (`EXORIEN-VECTOR`). |
| `tokenpage` | Memory Arena | **Absorb into Core** | Fixed-size page table and flat-array node arena live in `runtime/core/weft_ic_vm.py` and `runtime/core/weft_plasm.py` (`TOKENPAGE-MEM`). |
| `scry` | Introspection | **Connect & Absorb** | Zero-overhead eBPF and Mach VM page-fault telemetry map to `perception.md`, `test.md`, and `runtime/aywa/weft_daemon.py` (`SCRY-OBSERVE`). |
| `nullmodem` | IPC Descriptor Bus | **Absorb into Core** | UNIX domain socket `SCM_RIGHTS` file-descriptor passing (`send_file_descriptor`) lives in `README.md` and `almalga.md` (`NULLMODEM-LINK`). |
| `exyber` | Fault Quarantine | **Absorb into Core** | Byzantine fault isolation and outbound exo-mitosis evacuation gates live in `launch.md` and `runtime/core/weft_plasm.py` (`EXYBER-SHIELD`). |
| `exo-os` | Unikernel Boot | **Connect & Extend** | x86_64 real-mode bootloader (`README.md` Section 16) and ARM64 EL1 purge (`mac.md`) form the bare-metal boot layer (`EXO-OS-HYPER`). |
| `n001` | Genesis Prototype | **Supersede** | Historical first-generation seed superseded by the unified Weft runtime (`N001-GENESIS`). |
| `mettle` | Thermodynamic Bench | **Connect & Absorb** | Landauer bit-erasure and FLOP/Joule benchmarks map to `whoa.md`, `ult.md`, and `runtime/core/selftest.py` (`METTLE-BENCH`). |
| `n30` | Frontier Synthesis | **Connect & Extend** | Long-horizon planetary compute and photonic/silicon convergence map to `dissertation-mac.md` and `whitepaper.md` (`N30-HORIZON`). |
| `.github` | Org Charter | **Connect** | Organization-wide metadata indexed by `runtime/aywa/github_harvester.py` (`ORG-CHARTER`). |

## 3. Suspended Contributor Accounts Audit (`mb-aska` and `mk-aska`)

Two contributor GitHub accounts (`mb-aska` and `mk-aska`) were suspended by GitHub, while active contributor seats (`abu-aska`, `aska-root`, `J-Aska`) remain operational:

- **Observed Quirks**:
  1. Pull requests and review records authored by `mb-aska` or `mk-aska` across `synbios`, `abios`, `statos`, `compass`, `synmerit`, `exoframe`, `tokenpage`, and `exo-os` resolve to suspended/ghost author handles in REST and GraphQL queries when dereferencing fork head refs.
  2. Branch heads that pointed to personal forks under `mb-aska/*` or `mk-aska/*` cannot be fetched from the suspended fork namespaces. Their surviving commits live inside the org repositories (`Moissanite-Labs/*`) and local worktrees under ``~/Work/``.
- **Mitigation in Weft**:
  1. `runtime/aywa/github_harvester.py` tracks `suspended_touch` across all 19 repositories and incorporates fork/author discontinuity into the `org_tension` metric (`0.2662`) without failing when fork author objects return null.
  2. All canonical code and specifications now reside directly in ``exo/weft/`` and organization-owned branches, eliminating dependency on personal fork namespaces of `mb-aska` or `mk-aska`.
