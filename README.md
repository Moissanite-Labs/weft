# weft
become the weaver

See [PROGRAM.md](PROGRAM.md) for the build program.

Current work: [convergence plan](docs/program/convergence-plan.md), [what can be used now](docs/program/use-now.md), and [variant and lineage register](docs/program/variants.md). These distinguish current implementations from experiments, source alternatives, and longer-horizon work.

Complete source review: [phased build program](docs/program/build-program.md), [experiment cards](docs/program/experiment-cards.md), [file-by-file evidence](docs/program/audit/README.md), and [resume instructions](docs/program/resume.md).

## GitHub Pages seed (prepared, not enabled)

Static organism site lives under [`docs/`](docs/index.html): WebGPU membrane dashboard, SYM-2P telemetry, SharedArrayBuffer-capable worker (with fallback), and portable widget gallery. Sync artifacts with `python3 scripts/sync_pages_seed.py`. Deployment workflow is manual-only (`.github/workflows/pages-seed-deploy.yml`) until Pages is turned on.
