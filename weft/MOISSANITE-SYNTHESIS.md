# Moissanite-Labs to Weft Synthesis Map

Date: 2026-11-07
Origin Anchor: `Moissanite-Labs/compass` Discussion #5

## 1. Origin Thread Lineage (`Moissanite-Labs/compass` Discussion #5)

Discussion #5 in `Moissanite-Labs/compass` documents the progression that produced the 104-turn Desktop 8 Chrome session (`thread1-splicers-genesis-90133B.md` [29 turns], the 3 pre-window turns preserved in `README.md` Sections 15–24 / `more.md` / `mac.md`, and `thread1-weft-main-84ADC9.md` [72 turns]):

1. **Splicer Architectural Seed**: Biological-machine symbiosis where components self-assemble and upgrade in place rather than relying on static external orchestration.
2. **Stratified Shared-Memory Bus**: Separation of fast focal tensor channels, sympathetic scalar telemetry, and hippocampal novelty archives over POSIX shared memory (`weft/runtime/plasm/`).
3. **Mitotic A/B Speculation and Thermodynamic Selection**: Parallel safe (`alpha`) and exploratory (`beta`) mutations scored jointly by target-directed task fitness, invariant safety (`weft/runtime/invariants/`), and hippocampal novelty.
4. **Hardware Coupling and Provenance**: Host hardware telemetry (`weft/runtime/telemetry/`) paired with weight-space watermarking and the three-contract governance triad (`weft/runtime/ledger/` and `weft/runtime/gateway/`).

## 2. Repository Disposition Across the 19 `Moissanite-Labs` Repositories

| Repository | Weft Plane | Disposition | Integration Path in Weft |
| :--- | :--- | :--- | :--- |
| `compass` | North-Star Spec | **Connect & Anchor** | Discussion #5 is the canonical origin record and feeds `MOISSANITE-SYNTHESIS.md` and `browser-sources/thread1-splicers-genesis-90133B.md`. |
| `synbios` | Mission Control | **Connect & Extend** | Live capability stewardship and dashboard telemetry stream into `weft/runtime/telemetry/harvester.py` (`SYNBIOS-MATRIX`). |
| `abios` | Cellular Runtime | **Absorb into Core** | Mitotic cell lifecycle (`PlasticOrganismCell`, `M1MaxOrganismCell` in `mac.md`, and `SovereignOrganismCell`) is unified in `weft/runtime/plasm/plasm.py` (`ABIOS-PROTOCOL`). |
| `statos` | Kernel Substrate | **Connect & Absorb** | Host `sysctl` / `/proc/meminfo`, Mach VM, and ARM64 cache-purge primitives map to `mac.md`, `almalga.md`, and `weft/runtime/telemetry/host_metrics.py` (`STATOS-KERNEL`). |
| `mlx` | Tensor Engine | **Connect & Absorb** | Unified memory zero-copy array bindings power the 3-tier tensor bus in `weft/runtime/plasm/plasm.py` (`MLX-TENSOR-CORE`). |
| `ethos` | Constitutional Gate | **Absorb into Spec** | Invariant bounds and anti-rogue slashing rules merge into `ethos.md`, `govern.md`, `weft/runtime/invariants/`, and `TensionGovernor.sol` (`ETHOS-GOVERN`). |
| `synmerit` | Provenance Ledger | **Absorb into Core** | Homomorphic watermark verification and the 85/15 royalty excision valve live in `ProvenanceRegistry.sol`, `WeftTokenTissue.sol`, and `weft/runtime/gateway/` (`SYNMERIT-LEDGER`). |
| `exofab` | Silicon & Lithography | **Connect & Extend** | Physical fabrication and wafer yield physics connect directly to `terrafab.md`, `terrafab-calc.md`, and `terraweft.md` (`EXOFAB-SILICON`). |
| `exoframe` | Spatial Viewport | **Replace by Aywa** | Superseded by the single-pass WebGPU SDF + procedural ASCII viewport in `design/aywa.md` and `docs/index.html` (`EXOFRAME-SHELL`). |
| `exorien` | Peer Handshake | **Absorb into Core** | Binary 124-byte (`4s32s64s24s`) magic-header peer handshake (`WEFT`) and UDP mesh splicing live in `README.md` Section 17 (`README.md:575-591`) and `mac.md` (`EXORIEN-VECTOR`). |
| `tokenpage` | Memory Arena | **Absorb into Core** | Fixed-size page table and flat-array node arena live in `weft/runtime/ic/ic_vm.py` and `weft/runtime/plasm/plasm.py` (`TOKENPAGE-MEM`). |
| `scry` | Introspection | **Connect & Absorb** | Zero-overhead eBPF and Mach VM page-fault telemetry map to `perception.md`, `test.md`, and `weft/runtime/telemetry/` (`SCRY-OBSERVE`). |
| `nullmodem` | IPC Descriptor Bus | **Absorb into Core** | UNIX domain socket `SCM_RIGHTS` file-descriptor passing (`send_file_descriptor`) lives in `browser-sources/thread1-splicers-genesis-90133B.md` Turns 27–28 and `almalga.md` (`NULLMODEM-LINK`). |
| `exyber` | Fault Quarantine | **Absorb into Core** | Byzantine fault isolation and outbound exo-mitosis evacuation gates live in `launch.md` and `weft/runtime/plasm/plasm.py` (`EXYBER-SHIELD`). |
| `exo-os` | Unikernel Boot | **Connect & Extend** | x86_64 real-mode bootloader (`README.md` Section 16) and ARM64 EL1 purge (`mac.md`) form the bare-metal boot layer (`EXO-OS-HYPER`). |
| `n001` | Genesis Prototype | **Supersede** | Historical first-generation seed superseded by the unified Weft runtime (`N001-GENESIS`). |
| `mettle` | Thermodynamic Bench | **Connect & Absorb** | Landauer bit-erasure and FLOP/Joule benchmarks map to `whoa.md`, `ult.md`, and `weft/runtime/core/selftest.py` (`METTLE-BENCH`). |
| `n30` | Frontier Synthesis | **Connect & Extend** | Long-horizon planetary compute and photonic/silicon convergence map to `dissertation-mac.md` and `whitepaper.md` (`N30-HORIZON`). |
| `.github` | Org Charter | **Connect** | Organization-wide metadata indexed by `weft/runtime/telemetry/harvester.py` (`ORG-CHARTER`). |

## 3. Suspended Collaborator Accounts Audit

Two early collaborator GitHub accounts were suspended by GitHub, while active organization contributor seats remain operational:

- **Observed Quirks**:
  1. Pull requests and review records authored by those two suspended accounts across `synbios`, `abios`, `statos`, `compass`, `synmerit`, `exoframe`, `tokenpage`, and `exo-os` resolve to ghost author handles in REST and GraphQL queries when dereferencing fork head refs.
  2. Branch heads that pointed to personal forks under those suspended namespaces cannot be fetched from the suspended forks. Their surviving commits reside directly inside the organization repositories (`Moissanite-Labs/*`).
- **Mitigation in Weft**:
  1. `weft/runtime/telemetry/harvester.py` omits all personal and suspended account identifiers from repository and Pages telemetry (`moissanite_telemetry.json`) while supporting both offline `"source": "fixture"` snapshots and `--live` GitHub REST API queries (#15, #26).
  2. All canonical code and specifications reside directly in `Moissanite-Labs/weft` and organization-owned branches, eliminating dependency on external personal fork namespaces.
