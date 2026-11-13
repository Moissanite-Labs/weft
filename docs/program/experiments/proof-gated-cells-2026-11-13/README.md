# Proof-gated integer cell prototype

This mechanism prototype gives an agent a small cell environment through three stdio tools: inspect state, propose an edit and inspect events. A state-changing proposal commits only after a pinned Lean compiler checks a concrete mathematical certificate and the host confirms the same parent state. There is no language-model pilot, paid API call, neural training result or general physical-causality certificate.

The cell is an exact integer readout with three weights. Its initial state is `[3, 1, 5]`, its preservation anchors are `[1, 1, 0]` and `[0, 0, 1]`, coordinate 2 is frozen, and each edit has squared norm at most 8. The nonzero edit `[1, -1, 0]` preserves both anchor outputs. An edit such as `[1, 0, 0]` violates preservation and must not commit.

## Run locally

Use Python 3 and the installed Lean toolchain `leanprover/lean4:v4.35.0`. The Python code uses the standard library and Unix file locking. The verifier resolves the pinned compiler under the host's elan installation and fails closed if it is unavailable. It does not download a compiler during verification.

From this directory:

```sh
python3 cell_mcp.py --run-dir ./scratch-cell
```

The process reads one JSON-RPC message per line on stdin and writes responses to stdout. It implements the stdio tool subset for protocol version `2025-11-25`. Configure a compatible client to launch Python with `cell_mcp.py` and a dedicated `--run-dir`. Resolve those paths for the local checkout. There is no HTTP server or unrestricted execution tool.

A client first sends:

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"local-test","version":"1"}}}
```

After receiving the initialization response, the client must send:

```json
{"jsonrpc":"2.0","method":"notifications/initialized"}
```

It can then inspect the cell:

```json
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"cell_inspect","arguments":{}}}
```

Copy the returned `state_id` into `expected_state_id` for the next call:

```json
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"cell_propose","arguments":{"expected_state_id":"COPY_RETURNED_STATE_ID","delta":[1,-1,0]}}}
```

Use `cell_events` with empty arguments to retrieve accepted and rejected action records. A second edit using the old parent ID must be rejected. A refusal is an expected experimental outcome, rather than an invitation to weaken the gate.

## Captured local demonstration

The scripted run under data/mcp_demo records eight proposals: one nonzero preserving edit, one valid no-op and six rejections. It ends at `[4, 0, 5]`, with both anchor outputs still `[4, 5]`. The no-op is accepted because legality alone does not imply task progress. The capture includes requests, replies, proof source, compiler outputs, per-attempt decisions, initial/final state and event hashes.

To create a separate fresh capture without changing the archived run:

```sh
python3 run_demo.py --out ./scratch-demo
```

The actual Soko bridge capture under data/soko_bridge records one verified nonzero goal trace and six rejected goal traces at pinned commit `c3afb8d4b17b1b6ebcceaa05704320d555e2c013`. A legal zero edit does not satisfy its nonzero goal. This is a finite runtime dual-checker replay, separately from Lean verification. The frozen coordinate is also protected by an anchor, so this fixture does not isolate those restrictions.

For a separately available checkout of that exact Soko commit:

```sh
python3 soko_bridge.py --soko-checkout /path/to/pinned-soko --out ./scratch-soko
```

The Soko checkout supplies its own runtime dependencies. No language-model call is made by this bridge. SOKO-CONVERGENCE.md records the pinned source links and limits.

## Verification record

The captured validation run passed 16 tests, including the real pinned Soko bridge. Compiler paths were exercised with the actual Lean toolchain as well as mocked rejection cases. The stdout/stderr files under data/validation retain the exact test results. Without `SOKO_CHECKOUT`, the integration test is explicitly skipped, rather than counted as a passed Soko run.

```sh
SOKO_CHECKOUT=/path/to/pinned-soko python3 -m unittest -v test_verifier.py test_cell_mcp.py test_soko_bridge.py
python3 replay_capture.py --capture data/mcp_demo
```

The captured replay verified 36 file hashes and rechecked five concrete Lean certificates with empty axiom sets. The other three action records were host-level rejections before compilation. No-op acceptance and rejected transitions remain in the same record as the nonzero accepted edit.

## What is proved and trusted

Core.lean defines exact integer addition, dot products, frozen-coordinate checks and a per-transition squared-norm bound. Trusted Python builds a fixed concrete theorem from bounded input data. Candidates cannot supply Lean code, imports, arbitrary file paths or executable actions. Successful concrete certificates must report an empty axiom set.

A rejected mathematical edit can have a checked certificate of its rejection.

The theorem covers the exact before/delta/after relation and registered anchor preservation. It does not prove the Python adapter, JSON implementation, compare-and-swap, filesystem, compiler binary, operating system or hardware. These remain trusted implementation boundaries. Tests exercise them but do not turn them into kernel theorems.

Formal integer anchors are also not measurements of a physical environment or a proof that the specification captures human intent.

State and events are stored as one atomic snapshot, with parent identity, checker identities and chained event hashes. The host controls that storage. Hash chains help detect changes relative to retained evidence, rather than protecting against an owner who can replace all local state and pins.

## Evidence and scope

PROTOCOL.md records the finite mechanism and acceptance boundary. HARNESS-REVIEW.md evaluates the supplied proof harness, preserved as a data attachment under inputs/. SOKO-CONVERGENCE.md maps the design to pinned Soko evidence patterns and their limits. RAW-DATA.md and RAW-DATA-INDEX.json provide remote access to prior scientific data and specify capture for the new fixtures, proofs, compiler logs and rejections.

This is a local mechanism demonstration. It is separate from the four earlier paid studies and their 96 responses. No new model prompt or model response exists when no model API was called.

The supplied-harness controls under data/harness_controls reproduce a separate failure: its actual compiler path accepted a module containing only `import Std`, without the requested theorem. A harmless IO command was accepted by its token scanner but was never executed. These controls motivated the data-only trusted-template boundary. See INDEPENDENT-REVIEW.md for the detailed review.
