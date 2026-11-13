#!/usr/bin/env python3
"""Credential-in-memory Responses client. Input: request file paths, one per line.

Enter the temporary API key at the hidden terminal prompt. No shell argument,
environment file, request artifact, or response log contains the credential.
This worker sends only to the official OpenAI Responses endpoint.
"""
import argparse
import getpass
import json
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
import certifi

ENDPOINT = "https://api.openai.com/v1/responses"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--max-calls", type=int, default=18)
    p.add_argument("--max-output-tokens", type=int, default=6000)
    args = p.parse_args()
    key = getpass.getpass("Temporary API key (hidden, memory only): ")
    if not key.startswith("sk-"):
        raise SystemExit("Expected an OpenAI API key")
    print("READY: submit request JSON paths, or STOP", flush=True)
    for number, line in enumerate(sys.stdin, 1):
        name = line.strip()
        if name == "STOP":
            break
        if not name:
            continue
        if number > args.max_calls:
            print("STOP: call cap reached", flush=True)
            break
        path = Path(name).resolve()
        request = json.loads(path.read_text())
        if request.get("model") != "gpt-6-astra":
            raise SystemExit("Only the requested teacher model is enabled")
        request["store"] = False
        request["max_output_tokens"] = min(request.get("max_output_tokens", args.max_output_tokens), args.max_output_tokens)
        if key in json.dumps(request):
            raise SystemExit("Credential detected in request body")
        response_path = path.with_suffix(".response.json")
        if response_path.exists():
            print("SKIP: response exists", flush=True)
            continue
        data = json.dumps(request).encode()
        req = urllib.request.Request(ENDPOINT, data=data, headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"}, method="POST")
        start = time.monotonic()
        try:
            context = ssl.create_default_context(cafile=certifi.where())
            with urllib.request.urlopen(req, timeout=240, context=context) as response:
                raw = json.load(response)
            result = {k: raw.get(k) for k in ("id", "model", "status", "usage", "error", "incomplete_details", "created_at")}
            # Keep observable teacher answers and accounting, not internal reasoning items.
            result["output"] = [item for item in raw.get("output", []) if item.get("type") == "message"]
            record = {"request_file": path.name, "elapsed_seconds": time.monotonic() - start, "response": result}
        except urllib.error.HTTPError as exc:
            # Error bodies can contain identifiers. Retain only normalized API error fields.
            try:
                error = json.loads(exc.read()).get("error", {})
            except Exception:
                error = {}
            record = {"request_file": path.name, "elapsed_seconds": time.monotonic() - start, "http_status": exc.code,
                      "error": {k: error.get(k) for k in ("type", "code", "message")}}
        except Exception as exc:
            record = {"request_file": path.name, "elapsed_seconds": time.monotonic() - start, "error": {"type": type(exc).__name__}}
        serialized = json.dumps(record, indent=2).replace(key, "[REDACTED]")
        response_path.write_text(serialized + "\n")
        result = record.get("response", {})
        print(json.dumps({"file": response_path.name, "status": result.get("status"), "usage": result.get("usage"), "error": record.get("error"), "elapsed_seconds": record["elapsed_seconds"]}), flush=True)
        if record.get("http_status") in (401, 403, 429):
            print("STOP: access or quota failure, no automatic retry", flush=True)
            break
    key = ""


if __name__ == "__main__":
    main()
