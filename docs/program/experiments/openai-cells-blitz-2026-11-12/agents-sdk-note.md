# Evaluation: OpenAI Agents SDK and tracing for colony-style experiments

- Date: 2026-11-12. Follows `RESULTS.md`; same blitz window and key.
- Status: hands-on evaluation, not a commitment. One live demo call (gpt-6-luna, 273 total tokens) plus the official docs.

## What the SDK is

`openai-agents-python` (v0.24.0, installed and exercised here) is the productionized descendant of `openai/swarm`. It gives you Agents, tools, handoffs, guardrails, sessions and a tracing layer. Swarm's pattern (handoffs between specialist agents) lives on as `handoffs`.

## What we verified

- `Runner.run_sync` through `gpt-6-luna` with one function tool (`sh`) completed in ~4 to 6 s and printed trace id `trace_4747859631ac488f8c52207551ac244d` (first run) and `trace_55516363c8f54f71a17b1c57fc6a821d` (re-run); both flushed with `flush_traces()`.
- Traces export by default to the OpenAI Traces dashboard (platform.openai.com/traces) using the same `OPENAI_API_KEY`. Tracing is unavailable to organizations under Zero Data Retention.
- Spans observed in `sdk_spans.jsonl` (via a custom `TracingProcessor` that copied them out):
  `ResponseSpanData` per model turn with full request input and usage (cache-write detail included),
  `FunctionSpanData` per tool call with exact arguments and output and wall-clock start/end,
  `TurnSpanData`, `AgentSpanData`, `TaskSpanData` (total usage: 2 requests, 241 in / 32 out),
  and trace_start/trace_end markers with a `group_id` field left null.
- A custom processor registered with `add_trace_processor()` receives spans alongside the default OpenAI exporter; `set_trace_processors()` can replace the default entirely (local or redacted export).

## What this buys the colony program

1. Instrument-first, for free. The E07 record lists "cost not yet logged" and "harness-fixed reference workloads" as gaps. The tracing layer emits per-turn input/output tokens (including cached and cache-write tokens), exact tool arguments/outputs and timestamps, without any per-call bookkeeping in our harness. Our `harness.py` reimplements this by hand and gets a coarser version of the same thing.
2. Colony grouping in the dashboard. A `trace()` per cell wrapped in one parent trace per colony (or a shared `group_id`) gives the whole run one linked visualization. Useful for spotting pathological trajectories and for debugging stuck cells.
3. Handoffs as a mitosis primitive. Swarm's handoff is close to `try` (a daughter exploring one idea) but without the selection machinery; handoffs transfer control, they do not score outcomes. Do not read them as mitosis.
4. Guardrails could carry C2-style bounds. Output guardrails and input guardrails can enforce budget/tension-style checks with trips logged as `guardrail_span()`. Not demonstrated here; plausible fit, and it would make gate violations visible in traces instead of only in logs.
5. Everything exports somewhere. Default lands on OpenAI's backend. For E07's "keys never enter cells" posture and for pre-publication hygiene, decide per run: local/redacted export via `set_trace_processors()` (reader `trace_redaction.py` pattern), or accept the OpenAI dashboard as a debugging surface only. The record stays in-repo either way.
6. `trace_include_sensitive_data` defaults to true; spans store full generation inputs and outputs (cell-written code). Fine for our synthetic corpus work; set it false or redact before sending any real corpora or personal data.

## What this does not buy

- No selection machinery. Assay validation, the win rule, bench locks and body replacement stay ours. The SDK is a model-call and observability layer.
- No fitness. It cannot tell a kept improvement from noise; it does not see the corpus, the round-trip check or the assay stability gate.
- No substrate isolation. `sh` as a demo tool is unsandboxed. Our harness's `sandbox-exec` profile remains the containment boundary; the SDK does not sandbox anything (the new `SandboxAgent`/`sandbox` package is file-mount oriented and was not evaluated here).
- No non-OpenAI model story without adapters (`AnyLLMModel`/LiteLLM), and tracing of third-party models needs `set_tracing_export_api_key`.

## Recommendation

Adopt the tracing layer, not the runner, for API-backed experiment rounds:

- Wrap each cell in `with trace("colony-<id>", group_id=<colony>)`.
- Keep our assay/selection harness as the body loop; call the model through the SDK so spans come for free, or keep `harness.py` and add an exporter only if the rewrite is not wanted today.
- Export spans locally (redacted) if the run touches anything beyond synthetic corpora; otherwise let the dashboard hold the debug view while the in-repo JSONL remains the record.
- Do not use handoffs to model mitosis; keep `try` ours.

## Swarm, specifically

Swarm is archived-era work that became the Agents SDK. Its one transferable lesson is the explicitness of the handoff (what context the delegate sees, who speaks next). Our colony already passes parent genome and LIBRARY excerpts to daughters; that is the same discipline with scoring attached. Port nothing from Swarm itself beyond that reading.

## Housekeeping notes

- `pip install openai-agents` (0.24.0) on the system Python 3.14 framework. No dependency landed in this repo; the demo's imports are listed here.
- Live traces from the demo live on the OpenAI platform under this project's API key; no secrets were committed.
