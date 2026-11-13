#!/usr/bin/env python3
"""Bounded, memory-only credential transport for a preregistered pilot.

Only observable model messages and accounting are retained. No automatic retry:
an ambiguous failed request consumes its full reservation. Budget is a conservative
rate estimate, not an account balance or invoice. Keys never enter request files.
"""
import argparse
import getpass
import hashlib
import json
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import certifi

ENDPOINT = "https://api.openai.com/v1/responses"
INPUT_RESERVE_PER_TOKEN = 25 / 1_000_000
OUTPUT_PER_TOKEN = 50 / 1_000_000


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--max-calls", type=int, default=8)
    parser.add_argument("--budget-usd", type=float, default=5.0)
    parser.add_argument("--max-output-tokens", type=int, default=6000)
    args = parser.parse_args()
    if not (1 <= args.max_calls <= 8 and 0 < args.budget_usd <= 5 and 1 <= args.max_output_tokens <= 6000):
        raise SystemExit("Pilot bounds: 1..8 calls, at most 5 USD, 1..6000 output tokens")
    root = args.root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    ledger_path = root / "api-ledger.jsonl"
    if ledger_path.exists():
        raise SystemExit("Existing ledger: resume requires explicit reconciliation, not reset")
    key = getpass.getpass("Temporary API key (hidden, memory only): ")
    if not key.startswith("sk-"):
        raise SystemExit("Expected an OpenAI API key")
    context = ssl.create_default_context(cafile=certifi.where())
    spent_or_reserved = 0.0
    count = 0
    print("READY: request JSON paths, or STOP", flush=True)
    for line in sys.stdin:
        if line.strip() == "STOP":
            break
        if not line.strip():
            continue
        path = Path(line.strip()).resolve()
        if root not in path.parents:
            raise SystemExit("Request must be below registered artifact root")
        response_path = path.with_suffix(".response.json")
        if response_path.exists():
            print("SKIP: response exists", flush=True)
            continue
        request = json.loads(path.read_text())
        if request.get("model") != "gpt-6-astra":
            raise SystemExit("Only the requested model is enabled")
        if request.get("tools") or request.get("previous_response_id"):
            raise SystemExit("This pilot accepts one data-only request, no tools or hidden history")
        if "reasoning" in request:
            raise SystemExit("This pilot preserves the existing API default reasoning setting")
        if request.get("service_tier", "default") != "default":
            raise SystemExit("Only standard service tier is budgeted")
        request["store"] = False
        request["service_tier"] = "default"
        requested_output = request.get("max_output_tokens", args.max_output_tokens)
        if type(requested_output) is not int or not 1 <= requested_output <= 6000:
            raise SystemExit("Output token count must be an integer in 1..6000")
        request["max_output_tokens"] = min(requested_output, args.max_output_tokens)
        data = json.dumps(request, ensure_ascii=False).encode()
        if key.encode() in data:
            raise SystemExit("Credential found in payload")
        # UTF-8 byte count deliberately overcounts normal text tokens. Additional
        # allowance covers message framing. This is an engineering reserve.
        reservation = (len(data) + 4096) * INPUT_RESERVE_PER_TOKEN + request["max_output_tokens"] * OUTPUT_PER_TOKEN
        if count >= args.max_calls or spent_or_reserved + reservation > args.budget_usd:
            print(json.dumps({"stop": "budget_or_call_cap", "calls": count, "reserved_usd": spent_or_reserved, "next_reservation_usd": reservation}), flush=True)
            break
        count += 1
        spent_or_reserved += reservation
        outbound_path = path.with_suffix(".wire.json")
        outbound_path.write_bytes(data + b"\n")
        entry = {"attempt": count, "request_file": path.name, "request_sha256": hashlib.sha256(data).hexdigest(), "reservation_usd": reservation, "cumulative_reserved_usd": spent_or_reserved}
        with ledger_path.open("a") as ledger:
            ledger.write(json.dumps({**entry, "event": "reserved"}) + "\n")
            ledger.flush()
            import os
            os.fsync(ledger.fileno())
        start = time.monotonic()
        record = dict(entry)
        req = urllib.request.Request(ENDPOINT, data=data, headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=240, context=context) as response:
                raw = json.load(response)
                record["http_status"] = response.status
            result = {k: raw.get(k) for k in ("id", "model", "status", "usage", "error", "incomplete_details", "created_at", "service_tier")}
            result["output"] = [item for item in raw.get("output", []) if item.get("type") == "message"]
            record["response"] = result
        except urllib.error.HTTPError as exc:
            try:
                error = json.loads(exc.read()).get("error", {})
            except Exception:
                error = {}
            record["http_status"] = exc.code
            record["error"] = {k: error.get(k) for k in ("type", "code", "message")}
        except Exception as exc:
            record["error"] = {"type": type(exc).__name__}
        record["elapsed_seconds"] = time.monotonic() - start
        record = json.loads(json.dumps(record).replace(key, "[REDACTED]"))
        response_path.write_text(json.dumps(record, indent=2) + "\n")
        with ledger_path.open("a") as ledger:
            ledger.write(json.dumps({**entry, "event": "finished", "response_file": response_path.name, "http_status": record.get("http_status"), "ambiguous": "http_status" not in record}) + "\n")
        print(json.dumps({"file": response_path.name, "http_status": record.get("http_status"), "status": record.get("response", {}).get("status"), "usage": record.get("response", {}).get("usage"), "error": record.get("error"), "elapsed_seconds": record["elapsed_seconds"]}), flush=True)
        if record.get("http_status") != 200 or record.get("response", {}).get("status") != "completed":
            print("STOP: incomplete or failed call; no retry", flush=True)
            break
    key = ""


if __name__ == "__main__":
    main()
