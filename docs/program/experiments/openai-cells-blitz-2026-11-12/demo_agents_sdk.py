#!/usr/bin/env python3
"""One-cell demo: colony-style agent through the OpenAI Agents SDK.

Verifies the SDK path works against this project's API key and model set, and
shows what the tracing layer captures that the hand-rolled JSONL does not.
One gpt-6-luna call. Traces export to the OpenAI Traces dashboard; a copy of
every span payload is also written to sdk_spans.jsonl by a local processor.
"""
import json
import os
import subprocess
import time

from agents import Agent, Runner, function_tool, flush_traces, add_trace_processor
from agents.tracing import TracingProcessor

@function_tool
def sh(command: str) -> str:
    """Run a shell command locally (demo only: unsandboxed)."""
    p = subprocess.run(["/bin/sh", "-c", command], capture_output=True, text=True, timeout=20)
    return f"exit {p.returncode}\n{p.stdout}{p.stderr}"[:2000]

local_spans = open("sdk_spans.jsonl", "w")

class LocalDump(TracingProcessor):
    def on_trace_start(self, trace):
        local_spans.write(json.dumps({"trace_start": trace.name, "trace_id": trace.trace_id,
                                      "group_id": getattr(trace, "group_id", None)}) + "\n")
        local_spans.flush()

    def on_trace_end(self, trace):
        local_spans.write(json.dumps({"trace_end": trace.trace_id}) + "\n")
        local_spans.flush()

    def on_span_start(self, span):
        pass

    def on_span_end(self, span):
        sd = getattr(span, "span_data", None)
        kind = type(sd).__name__ if sd is not None else "unknown"
        fields = {}
        for f in ("model", "name", "input", "output", "usage", "gen_ai_id", "span_data"):
            v = getattr(sd, f, None)
            if v is not None:
                fields[f] = str(v)[:300]
        local_spans.write(json.dumps({"kind": kind, **fields,
                                      "started_at": str(getattr(span, "started_at", "")),
                                      "ended_at": str(getattr(span, "ended_at", ""))}, default=str) + "\n")
        local_spans.flush()

    def shutdown(self):
        local_spans.flush()

    def force_flush(self):
        local_spans.flush()

add_trace_processor(LocalDump())

cell = Agent(
    name="sdk-demo-cell",
    instructions="You are a colony cell under test. Call the sh tool exactly once to compute 6*7 with python3, then report the number.",
    model="gpt-6-luna",
    tools=[sh],
)

if __name__ == "__main__":
    t0 = time.time()
    result = Runner.run_sync(cell, "Compute 6*7 via sh and report it.")
    print("output:", result.final_output)
    print("elapsed_s:", round(time.time() - t0, 2))
    print("usage:", result.context_wrapper.usage)
    flush_traces()
