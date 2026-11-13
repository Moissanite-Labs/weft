#!/usr/bin/env python3
"""
run_all_55_flex_burn.py — Unified Master Orchestrator, Atomic Loopback `/v1/responses`
Budget Proxy, & Hierarchical `MASTER_SHA256SUMS` Roll-Up Launcher for Expiring $55 OpenAI Credits.

What This Master Launcher Coordinates
-------------------------------------
Orchestrates all four research-org OpenAI Flex (`service_tier="flex"`, 50% Batch-rate)
harnesses concurrently, sequentially, or in 2-wave staged rollover under a SINGLE atomic
cross-process `$53.50` budget ledger (`$1.50` safety buffer below `$55.00` to prevent
asynchronous `credit_balance_exhausted` negative-balance lag):

  - Track 1 (`weft_111` — default `$18.70` Flex / `$37.40` Standard value):
      `weft_111_flex_harness.py` (`Moissanite-Labs/weft` Issue #111 interleaved `hy4` R3
      protocol-adherence replicates + sealed 32,805B R1 out-of-distribution audit).
  - Track 2 (`lean4_astra` — default `$12.60` Flex / `$25.20` Standard value):
      `lean4_astra_proof_harness.py` (`Proven-Commons/semver` & `WeftInvariants.lean`
      `gpt-6-astra` `xhigh` proof synthesis, 12-vector Verified-Bar scanner, & `lake` repair).
  - Track 3 (`scry_abios` — default `$10.20` Flex / `$20.40` Standard value):
      `scry_abios_equal_compute_eval.py` (`Moissanite-Labs/abios` `SYM-2P` vs. `scry` dense
      symbolic scratchpads vs. verbose English JSON at iso-token & iso-dollar compute).
  - Track 4 (`rigid_880` — default `$12.00` Flex / `$24.00` Standard value):
      `rigid_realizations_880_certifier.py` (`Foundation-0/rigid-realizations` exact-rational
      Krawczyk + Kantorovich 880-realization certifier & blind clean-room replication).

How Cross-Process Shared `$53.50` Enforcement Works
---------------------------------------------------
  - Starts an in-process multithreaded loopback HTTP proxy (`127.0.0.1:<ephemeral_port>`)
    and routes every child harness's `/v1/responses` traffic through it (`--base-url` for
    Tracks 1-2; `OPENAI_BASE_URL` for Tracks 3-4) without modifying a single line of the
    four standalone harness scripts.
  - Before forwarding any `POST /v1/responses` call over TLS to `https://api.openai.com`,
    `MasterSharedBudgetLedger` atomically reserves worst-case turn USD against the shared
    `$53.50` ceiling. Uncharged Flex `429 Resource Unavailable` responses release their
    reservation immediately; `200 OK` responses reconcile exact uncached input, cached input,
    and output/reasoning tokens into `master_api_ledger.jsonl`.
  - In `sequential` and `staged` modes, 100% of prompt-cache savings from earlier waves
    automatically roll forward to expand downstream proof/replication budgets while remaining
    strictly inside `--master-budget-usd` (`$53.50`).
  - Verifies each child track's `SHA256SUMS` and compiles a root `MASTER_SHA256SUMS` manifest
    (`sha256sum -c MASTER_SHA256SUMS` compatible) over all harnesses, logs, and certificates.

Quickstart
----------
  # 1. Full offline verification (runs all 4 child `--selftest` suites + live loopback proxy
  #    concurrent/rollover/cutoff tests + `sha256sum -c MASTER_SHA256SUMS`):
  python3 run_all_55_flex_burn.py --selftest

  # 2. Maximum-speed concurrent burn across all 4 tracks (recommended when expiry clock is unknown):
  export OPENAI_API_KEY="sk-..."
  python3 run_all_55_flex_burn.py \
      --mode concurrent \
      --master-budget-usd 53.50 \
      --semver-repo ./semver \
      --rigid-repo ./rigid-realizations

  # 3. Two-wave staged burn with automatic prompt-cache savings rollover into Lean 4 + L880 proofs:
  python3 run_all_55_flex_burn.py \
      --mode staged \
      --master-budget-usd 53.50 \
      --semver-repo ./semver \
      --rigid-repo ./rigid-realizations

License: Apache-2.0 / MIT. Machine-authored orchestration & metering harness (disclosed).
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import http.server
import json
import os
import re
import secrets
import shutil
import signal
import socketserver
import ssl
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple


# =============================================================================
# 1. Official OpenAI Pricing Table & Atomic Cross-Process Master Ledger
#    Source: https://developers.openai.com/api/docs/pricing
# =============================================================================

MODEL_PRICING_STD_PER_MTOK: Dict[str, Dict[str, float]] = {
    "gpt-6-astra":   {"input": 10.00, "cached_input": 1.00,  "output": 50.00},
    "gpt-6.1-sol":   {"input": 2.00,  "cached_input": 0.10,  "output": 10.00},
    "gpt-6-sol":     {"input": 2.00,  "cached_input": 0.20,  "output": 10.00},
    "gpt-6.1-terra": {"input": 1.00,  "cached_input": 0.05,  "output": 5.00},
    "gpt-6-luna":    {"input": 0.10,  "cached_input": 0.01,  "output": 0.50},
}

SERVICE_TIER_MULTIPLIER: Dict[str, float] = {
    "flex": 0.5,
    "batch": 0.5,
    "auto": 1.0,
    "default": 1.0,
    "standard": 1.0,
    "priority": 2.0,
    "fast": 2.0,
}

DEFAULT_TRACK_WEIGHTS_USD: Dict[str, float] = {
    "weft_111":   18.70,
    "lean4_astra": 12.60,
    "scry_abios": 10.20,
    "rigid_880":  12.00,
}  # Exact sum = $53.50 ($107.00 Standard-tier equivalent compute)


_SECRET_PATTERNS = re.compile(r"(sk-[A-Za-z0-9_-]{12,}|Bearer\s+[A-Za-z0-9._~+/-]+=*)")

def redact_secrets_in_text(text: str) -> str:
    return _SECRET_PATTERNS.sub("[REDACTED_CREDENTIAL]", text)

HARNESS_FILENAMES: Dict[str, str] = {
    "weft_111":    "weft_111_flex_harness.py",
    "lean4_astra": "lean4_astra_proof_harness.py",
    "scry_abios":  "scry_abios_equal_compute_eval.py",
    "rigid_880":   "rigid_realizations_880_certifier.py",
}


def compute_exact_cost_usd(
    model: str,
    service_tier: str,
    input_tokens: int,
    cached_tokens: int,
    output_tokens: int,
) -> Tuple[float, float]:
    """Return `(settled_tier_cost_usd, unscaled_list_rate_reference_usd)` (settled billing vs reference list rate)."""
    rates = MODEL_PRICING_STD_PER_MTOK.get(model)
    if rates is None:
        # Conservative fallback to frontier gpt-6-astra rates if a new model alias is passed
        rates = MODEL_PRICING_STD_PER_MTOK["gpt-6-astra"]
    mult = SERVICE_TIER_MULTIPLIER.get(service_tier.lower(), 1.0)
    uncached = max(0, input_tokens - cached_tokens)
    cached = max(0, min(input_tokens, cached_tokens))
    std_usd = (
        uncached * rates["input"] / 1_000_000.0
        + cached * rates["cached_input"] / 1_000_000.0
        + output_tokens * rates["output"] / 1_000_000.0
    )
    return (std_usd * mult, std_usd)


def estimate_payload_input_tokens(payload: Dict[str, Any]) -> int:
    raw = json.dumps(
        {"instructions": payload.get("instructions"), "input": payload.get("input"), "tools": payload.get("tools")},
        ensure_ascii=True,
    )
    return max(128, (len(raw) // 3) + 96)


@dataclass
class TrackUsageStats:
    calls_completed: int = 0
    calls_rejected_cap: int = 0
    calls_retried_429_or_5xx: int = 0
    input_tokens: int = 0
    cached_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    spent_usd: float = 0.0
    standard_equiv_usd: float = 0.0
    reserved_in_flight_usd: float = 0.0


class MasterSharedBudgetLedger:
    """
    Single atomic cross-process USD ledger shared by all child harnesses through the loopback
    `/v1/responses` proxy. Guarantees `spent_usd + reserved_in_flight_usd <= master_cap_usd`.
    """

    def __init__(self, master_cap_usd: float, ledger_log_path: Path) -> None:
        self.master_cap_usd = float(master_cap_usd)
        self.ledger_log_path = ledger_log_path
        self._lock = threading.Lock()
        self.spent_usd: float = 0.0
        self.standard_equiv_usd: float = 0.0
        self.reserved_in_flight_usd: float = 0.0
        self.tracks: Dict[str, TrackUsageStats] = {
            k: TrackUsageStats() for k in DEFAULT_TRACK_WEIGHTS_USD
        }
        self._seq: int = 0

    def try_reserve(
        self, track_id: str, model: str, service_tier: str, est_in_tokens: int, max_out_tokens: int
    ) -> Tuple[bool, float, str]:
        worst_usd, _ = compute_exact_cost_usd(
            model=model,
            service_tier=service_tier,
            input_tokens=est_in_tokens,
            cached_tokens=0,
            output_tokens=max_out_tokens,
        )
        with self._lock:
            t_stats = self.tracks.setdefault(track_id, TrackUsageStats())
            projected = self.spent_usd + self.reserved_in_flight_usd + worst_usd
            if projected > self.master_cap_usd + 1e-12:
                t_stats.calls_rejected_cap += 1
                reason = (
                    f"Master shared cap (${self.master_cap_usd:.2f}) reached: "
                    f"spent=${self.spent_usd:.4f}, reserved=${self.reserved_in_flight_usd:.4f}, "
                    f"needed_worst_case=${worst_usd:.4f}."
                )
                return False, 0.0, reason
            self.reserved_in_flight_usd += worst_usd
            t_stats.reserved_in_flight_usd += worst_usd
            return True, worst_usd, "OK"

    def release_without_spend(self, track_id: str, reserved_usd: float, retryable: bool = False) -> None:
        with self._lock:
            self.reserved_in_flight_usd = max(0.0, self.reserved_in_flight_usd - reserved_usd)
            t_stats = self.tracks.setdefault(track_id, TrackUsageStats())
            t_stats.reserved_in_flight_usd = max(0.0, t_stats.reserved_in_flight_usd - reserved_usd)
            if retryable:
                t_stats.calls_retried_429_or_5xx += 1

    def commit_completed_call(
        self,
        *,
        track_id: str,
        reserved_usd: float,
        response_id: str,
        model: str,
        service_tier: str,
        input_tokens: int,
        cached_tokens: int,
        output_tokens: int,
        reasoning_tokens: int,
        latency_s: float,
    ) -> float:
        actual_usd, std_usd = compute_exact_cost_usd(
            model=model,
            service_tier=service_tier,
            input_tokens=input_tokens,
            cached_tokens=cached_tokens,
            output_tokens=output_tokens,
        )
        with self._lock:
            self._seq += 1
            seq_no = self._seq
            self.reserved_in_flight_usd = max(0.0, self.reserved_in_flight_usd - reserved_usd)
            self.spent_usd += actual_usd
            self.standard_equiv_usd += std_usd

            t_stats = self.tracks.setdefault(track_id, TrackUsageStats())
            t_stats.reserved_in_flight_usd = max(0.0, t_stats.reserved_in_flight_usd - reserved_usd)
            t_stats.calls_completed += 1
            t_stats.input_tokens += input_tokens
            t_stats.cached_tokens += cached_tokens
            t_stats.output_tokens += output_tokens
            t_stats.reasoning_tokens += reasoning_tokens
            t_stats.spent_usd += actual_usd
            t_stats.standard_equiv_usd += std_usd

            entry = {
                "seq": seq_no,
                "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "track": track_id,
                "response_id": response_id,
                "model": model,
                "service_tier": service_tier,
                "input_tokens": input_tokens,
                "cached_tokens": cached_tokens,
                "output_tokens": output_tokens,
                "reasoning_tokens": reasoning_tokens,
                "call_cost_usd": round(actual_usd, 6),
                "standard_equiv_usd": round(std_usd, 6),
                "master_cumulative_spent_usd": round(self.spent_usd, 6),
                "master_remaining_usd": round(max(0.0, self.master_cap_usd - self.spent_usd), 6),
                "latency_s": round(latency_s, 3),
            }
            with self.ledger_log_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=True) + "\n")
        return actual_usd

    def remaining_unreserved_usd(self) -> float:
        with self._lock:
            return max(0.0, self.master_cap_usd - self.spent_usd - self.reserved_in_flight_usd)

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            tot_in = sum(t.input_tokens for t in self.tracks.values())
            tot_cached = sum(t.cached_tokens for t in self.tracks.values())
            tot_out = sum(t.output_tokens for t in self.tracks.values())
            tot_reas = sum(t.reasoning_tokens for t in self.tracks.values())
            return {
                "master_cap_usd": round(self.master_cap_usd, 6),
                "spent_usd": round(self.spent_usd, 6),
                "standard_tier_equivalent_usd": round(self.standard_equiv_usd, 6),
                "flex_and_cache_savings_usd": round(max(0.0, self.standard_equiv_usd - self.spent_usd), 6),
                "remaining_usd": round(max(0.0, self.master_cap_usd - self.spent_usd), 6),
                "total_calls_completed": sum(t.calls_completed for t in self.tracks.values()),
                "total_calls_rejected_cap": sum(t.calls_rejected_cap for t in self.tracks.values()),
                "total_input_tokens": tot_in,
                "total_cached_tokens": tot_cached,
                "prompt_cache_hit_pct": round((tot_cached / tot_in) * 100.0, 2) if tot_in > 0 else 0.0,
                "total_output_tokens": tot_out,
                "total_reasoning_tokens": tot_reas,
                "by_track": {
                    k: {
                        "calls_completed": v.calls_completed,
                        "calls_rejected_cap": v.calls_rejected_cap,
                        "calls_retried_429_or_5xx": v.calls_retried_429_or_5xx,
                        "input_tokens": v.input_tokens,
                        "cached_tokens": v.cached_tokens,
                        "output_tokens": v.output_tokens,
                        "reasoning_tokens": v.reasoning_tokens,
                        "spent_usd": round(v.spent_usd, 6),
                        "standard_equiv_usd": round(v.standard_equiv_usd, 6),
                    }
                    for k, v in self.tracks.items()
                },
            }


# =============================================================================
# 2. Loopback Multithreaded `/v1/responses` Metering & Upstream Proxy
# =============================================================================

UpstreamHandlerFn = Callable[[Dict[str, Any], Dict[str, str], float], Tuple[int, bytes]]


def live_openai_upstream_handler(
    payload: Dict[str, Any], headers: Dict[str, str], timeout_s: float
) -> Tuple[int, bytes]:
    """Forward metered request over TLS to `https://api.openai.com/v1/responses`."""
    upstream_url = os.environ.get(
        "MASTER_UPSTREAM_RESPONSES_URL", "https://api.openai.com/v1/responses"
    )
    body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
    req = urllib.request.Request(
        url=upstream_url,
        data=body,
        method="POST",
        headers={
            "Authorization": headers.get("Authorization", ""),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "moissanite-f0-proven-master-flex-proxy/1.0",
        },
    )
    ctx = ssl.create_default_context(cafile=(os.environ.get('SSL_CERT_FILE') or ('/etc/ssl/cert.pem' if os.path.exists('/etc/ssl/cert.pem') else None)))
    try:
        with urllib.request.urlopen(req, timeout=timeout_s, context=ctx) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as err:
        return err.code, err.read()


class _ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class SharedLedgerProxyServer:
    """
    Binds `127.0.0.1:0` and routes `/t/<track_id>/v1/responses` (or `/v1/responses?track=<id>`)
    through `MasterSharedBudgetLedger` before calling `upstream_fn`.
    """

    def __init__(
        self,
        ledger: MasterSharedBudgetLedger,
        upstream_fn: UpstreamHandlerFn,
        upstream_timeout_s: float = 910.0,
    ) -> None:
        self.ledger = ledger
        self.upstream_fn = upstream_fn
        self.upstream_timeout_s = upstream_timeout_s
        self._server: Optional[_ThreadedHTTPServer] = None
        self._thread: Optional[threading.Thread] = None
        self.port: int = 0

    def start(self) -> int:
        outer = self

        class Handler(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, fmt: str, *args: Any) -> None:
                return  # Keep stdout clean for structured orchestrator progress

            def do_POST(self) -> None:
                parsed = urllib.parse.urlparse(self.path)
                qs = urllib.parse.parse_qs(parsed.query)
                track_id = "unknown"
                m_path = re.match(r"^/t/([^/]+)/v1/responses$", parsed.path)
                if m_path:
                    track_id = m_path.group(1)
                elif "track" in qs and qs["track"]:
                    track_id = qs["track"][0]

                content_len = int(self.headers.get("Content-Length", "0"))
                raw_body = self.rfile.read(content_len)
                try:
                    payload = json.loads(raw_body.decode("utf-8"))
                except Exception as exc:
                    err_bytes = json.dumps({"error": {"message": f"Invalid JSON: {exc}"}}).encode("utf-8")
                    self._send_bytes(400, err_bytes)
                    return

                model = str(payload.get("model", "gpt-6-astra"))
                tier = str(payload.get("service_tier") or "flex")
                max_out = int(payload.get("max_output_tokens") or 8192)
                est_in = estimate_payload_input_tokens(payload)

                ok, reserved_usd, reason = outer.ledger.try_reserve(
                    track_id=track_id,
                    model=model,
                    service_tier=tier,
                    est_in_tokens=est_in,
                    max_out_tokens=max_out,
                )
                if not ok:
                    # Emit `credit_balance_exhausted` / `insufficient_quota` so child harnesses
                    # trigger their clean graceful stop and write SHA256SUMS!
                    cutoff_bytes = json.dumps(
                        {
                            "error": {
                                "code": "credit_balance_exhausted",
                                "type": "insufficient_quota",
                                "message": reason,
                            }
                        }
                    ).encode("utf-8")
                    self._send_bytes(402, cutoff_bytes)
                    return

                t0 = time.monotonic()
                try:
                    status_code, resp_bytes = outer.upstream_fn(
                        payload,
                        {"Authorization": self.headers.get("Authorization", "")},
                        outer.upstream_timeout_s,
                    )
                except Exception as net_exc:
                    outer.ledger.release_without_spend(track_id, reserved_usd, retryable=True)
                    err_bytes = json.dumps(
                        {"error": {"type": "upstream_network_error", "message": str(net_exc)}}
                    ).encode("utf-8")
                    self._send_bytes(502, err_bytes)
                    return

                latency = time.monotonic() - t0
                if 200 <= status_code < 300:
                    try:
                        resp_obj = json.loads(resp_bytes.decode("utf-8"))
                        usage = resp_obj.get("usage") or {}
                        in_tok = int(usage.get("input_tokens", 0))
                        cached_tok = int((usage.get("input_tokens_details") or {}).get("cached_tokens", 0))
                        out_tok = int(usage.get("output_tokens", 0))
                        reas_tok = int((usage.get("output_tokens_details") or {}).get("reasoning_tokens", 0))
                        actual_tier = str(resp_obj.get("service_tier") or tier)
                        outer.ledger.commit_completed_call(
                            track_id=track_id,
                            reserved_usd=reserved_usd,
                            response_id=str(resp_obj.get("id", "resp_unknown")),
                            model=model,
                            service_tier=actual_tier,
                            input_tokens=in_tok,
                            cached_tokens=cached_tok,
                            output_tokens=out_tok,
                            reasoning_tokens=reas_tok,
                            latency_s=latency,
                        )
                    except Exception:
                        outer.ledger.release_without_spend(track_id, reserved_usd, retryable=False)
                else:
                    retryable = status_code in (408, 409, 429, 500, 502, 503, 504)
                    outer.ledger.release_without_spend(track_id, reserved_usd, retryable=retryable)

                self._send_bytes(status_code, resp_bytes)

            def _send_bytes(self, status: int, body: bytes) -> None:
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(body)

        self._server = _ThreadedHTTPServer(("127.0.0.1", 0), Handler)
        self.port = int(self._server.server_address[1])
        self._thread = threading.Thread(
            target=self._server.serve_forever, name="shared-ledger-proxy", daemon=True
        )
        self._thread.start()
        return self.port

    def stop(self) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None

    def responses_url_for_track(self, track_id: str) -> str:
        return f"http://127.0.0.1:{self.port}/t/{track_id}/v1/responses"

    def base_v1_url_for_track(self, track_id: str) -> str:
        return f"http://127.0.0.1:{self.port}/t/{track_id}/v1"


# =============================================================================
# 3. Child Harness Command Builders & Async Subprocess Runner
# =============================================================================

@dataclass
class TrackExecutionResult:
    track_id: str
    script_name: str
    allocated_budget_usd: float
    actual_proxy_spent_usd: float
    returncode: int
    wall_seconds: float
    output_dir: str
    child_sha256sums_status: str
    child_sha256sums_files_checked: int
    log_file: str
    skipped: bool = False
    skip_reason: str = ""


def build_track_command_and_env(
    *,
    track_id: str,
    harnesses_dir: Path,
    track_out_dir: Path,
    budget_slice_usd: float,
    proxy: SharedLedgerProxyServer,
    args: argparse.Namespace,
) -> Tuple[Optional[List[str]], Dict[str, str], str]:
    """
    Build exact CLI command + environment variables routing `track_id` through `proxy`.
    Returns `(cmd_or_none_if_skipped, env_dict, skip_reason)`.
    """
    script_path = harnesses_dir / HARNESS_FILENAMES[track_id]
    env = dict(os.environ)
    # Ensure child scripts have an API key token (even against mock proxy in tests)
    if not env.get("OPENAI_API_KEY"):
        env["OPENAI_API_KEY"] = "sk-proxy-metered"
    env["OPENAI_BASE_URL"] = proxy.base_v1_url_for_track(track_id)

    budget_str = f"{max(0.05, budget_slice_usd):.4f}"

    if track_id == "weft_111":
        cmd = [
            sys.executable,
            str(script_path),
            "--replicates", str(args.weft_replicates),
            "--include-astra-replicates", str(args.weft_astra_replicates),
            "--service-tier", args.service_tier,
            "--budget-usd", budget_str,
            "--output-dir", str(track_out_dir),
            "--base-url", proxy.responses_url_for_track(track_id),
        ]
        if args.strict_flex:
            cmd.append("--strict-flex")
        return cmd, env, ""

    if track_id == "lean4_astra":
        target_mode = "all" if (args.semver_repo and args.semver_repo.exists()) else "weft"
        cmd = [
            sys.executable,
            str(script_path),
            "--target", target_mode,
            "--effort", args.astra_effort,
            "--service-tier", args.service_tier,
            "--budget-usd", budget_str,
            "--output-dir", str(track_out_dir),
            "--base-url", proxy.responses_url_for_track(track_id),
        ]
        if args.semver_repo and args.semver_repo.exists():
            cmd.extend(["--semver-repo", str(args.semver_repo.resolve())])
        if args.pro_mode:
            cmd.append("--pro-mode")
        if args.strict_flex:
            cmd.append("--strict-flex")
        return cmd, env, ""

    if track_id == "scry_abios":
        cmd = [
            sys.executable,
            str(script_path),
            "--suite", args.scry_suite,
            "--models", args.scry_models,
            "--efforts", args.scry_efforts,
            "--tasks-per-family", str(args.scry_tasks_per_family),
            "--handoff-cases", str(args.scry_handoff_cases),
            "--service-tier", "flex" if args.service_tier == "flex" else "default",
            "--budget-usd", budget_str,
            "--out-dir", str(track_out_dir),
        ]
        if args.abios_validator and args.abios_validator.exists():
            cmd.extend(["--abios-validator", str(args.abios_validator.resolve())])
        return cmd, env, ""

    if track_id == "rigid_880":
        has_repo = bool(args.rigid_repo and args.rigid_repo.exists())
        valid_certs = [p for p in args.rigid_cert if p.exists()]
        if not has_repo and not valid_certs:
            if args.skip_missing_repos:
                return None, env, "No --rigid-repo or --rigid-cert provided and --skip-missing-repos set."
            # Auto-materialize the canonical planted 10-vertex L880 rational fixture via child helper
            track_out_dir.mkdir(parents=True, exist_ok=True)
            seed_cert = track_out_dir / "planted_l880_seed_certificate.json"
            gen_code = (
                "import importlib.util, json, sys; "
                f"spec = importlib.util.spec_from_file_location('r880', {str(script_path)!r}); "
                "mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); "
                f"open({str(seed_cert)!r}, 'w').write(json.dumps(mod.build_planted_l880_rational_fixture(), indent=2))"
            )
            subprocess.run([sys.executable, "-c", gen_code], check=True)
            valid_certs = [seed_cert]

        cmd = [
            sys.executable,
            str(script_path),
            "--astra-effort", args.astra_effort,
            "--service-tier", "flex" if args.service_tier == "flex" else "default",
            "--budget-usd", budget_str,
            "--out-dir", str(track_out_dir),
        ]
        if has_repo and args.rigid_repo is not None:
            cmd.extend(["--repo-dir", str(args.rigid_repo.resolve())])
        for cp in valid_certs:
            cmd.extend(["--cert", str(cp.resolve())])
        if args.pro_mode:
            cmd.append("--pro-mode")
        return cmd, env, ""

    raise KeyError(f"Unknown track_id={track_id!r}")


def verify_sha256sums_manifest_pure_python(manifest_path: Path) -> Tuple[str, int]:
    """Verify a standard `SHA256SUMS` file in pure Python without shell assumptions."""
    if not manifest_path.exists():
        return "MISSING", 0
    base_dir = manifest_path.parent
    checked = 0
    for raw_line in manifest_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            return f"MALFORMED_LINE:{line[:60]}", checked
        expected_hex, rel_name = parts[0].strip(), parts[1].lstrip("*").strip()
        target = base_dir / rel_name
        if not target.exists():
            return f"MISSING_FILE:{rel_name}", checked
        actual_hex = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual_hex.lower() != expected_hex.lower():
            return f"HASH_MISMATCH:{rel_name}", checked
        checked += 1
    return ("VERIFIED" if checked > 0 else "EMPTY"), checked


def verify_track_sha256sums_tree(track_out_dir: Path) -> Tuple[str, int]:
    """Discover and verify all `SHA256SUMS` manifests under `track_out_dir` (root or timestamped run_* subdir)."""
    manifests = sorted(track_out_dir.rglob("SHA256SUMS"))
    if not manifests:
        return "MISSING", 0
    total_checked = 0
    for mp in manifests:
        st, cnt = verify_sha256sums_manifest_pure_python(mp)
        if st != "VERIFIED":
            return st, total_checked + cnt
        total_checked += cnt
    return "VERIFIED", total_checked


async def launch_single_track(
    *,
    track_id: str,
    harnesses_dir: Path,
    run_root: Path,
    budget_slice_usd: float,
    proxy: SharedLedgerProxyServer,
    ledger: MasterSharedBudgetLedger,
    args: argparse.Namespace,
) -> TrackExecutionResult:
    track_out_dir = run_root / f"track_{track_id}"
    track_out_dir.mkdir(parents=True, exist_ok=True)
    log_path = run_root / "logs" / f"{track_id}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    cmd, env, skip_reason = build_track_command_and_env(
        track_id=track_id,
        harnesses_dir=harnesses_dir,
        track_out_dir=track_out_dir,
        budget_slice_usd=budget_slice_usd,
        proxy=proxy,
        args=args,
    )
    if cmd is None:
        log_path.write_text(f"[skipped] {skip_reason}\n", encoding="utf-8")
        return TrackExecutionResult(
            track_id=track_id,
            script_name=HARNESS_FILENAMES[track_id],
            allocated_budget_usd=round(budget_slice_usd, 6),
            actual_proxy_spent_usd=0.0,
            returncode=0,
            wall_seconds=0.0,
            output_dir=str(track_out_dir.relative_to(run_root)),
            child_sha256sums_status="SKIPPED",
            child_sha256sums_files_checked=0,
            log_file=str(log_path.relative_to(run_root)),
            skipped=True,
            skip_reason=skip_reason,
        )

    t0 = time.monotonic()
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        env=env,
    )
    stdout_bytes, _ = await proc.communicate()
    elapsed = time.monotonic() - t0

    log_path.write_bytes(stdout_bytes)
    rc = int(proc.returncode or 0)

    sha_status, sha_cnt = verify_track_sha256sums_tree(track_out_dir)
    snap = ledger.snapshot()
    actual_spent = snap["by_track"].get(track_id, {}).get("spent_usd", 0.0)

    return TrackExecutionResult(
        track_id=track_id,
        script_name=HARNESS_FILENAMES[track_id],
        allocated_budget_usd=round(budget_slice_usd, 6),
        actual_proxy_spent_usd=round(actual_spent, 6),
        returncode=rc,
        wall_seconds=round(elapsed, 3),
        output_dir=str(track_out_dir.relative_to(run_root)),
        child_sha256sums_status=sha_status,
        child_sha256sums_files_checked=sha_cnt,
        log_file=str(log_path.relative_to(run_root)),
    )


# =============================================================================
# 4. Concurrent, Staged 2-Wave, & Sequential Rollover Scheduler
# =============================================================================

def compute_scaled_allocations(
    selected_tracks: Sequence[str], total_budget_usd: float
) -> Dict[str, float]:
    weight_sum = sum(DEFAULT_TRACK_WEIGHTS_USD[t] for t in selected_tracks)
    if weight_sum <= 0:
        return {t: 0.0 for t in selected_tracks}
    return {
        t: total_budget_usd * (DEFAULT_TRACK_WEIGHTS_USD[t] / weight_sum)
        for t in selected_tracks
    }


async def execute_master_schedule(
    *,
    selected_tracks: List[str],
    mode: str,
    dynamic_pool: bool,
    harnesses_dir: Path,
    run_root: Path,
    proxy: SharedLedgerProxyServer,
    ledger: MasterSharedBudgetLedger,
    args: argparse.Namespace,
) -> List[TrackExecutionResult]:
    base_allocs = compute_scaled_allocations(selected_tracks, ledger.master_cap_usd)

    if mode == "concurrent":
        # In `--dynamic-pool`, each child gets up to 75% burst cap while the loopback proxy
        # enforces the exact atomic `$53.50` shared ceiling across all 4 concurrent processes!
        results = await asyncio.gather(
            *(
                launch_single_track(
                    track_id=t,
                    harnesses_dir=harnesses_dir,
                    run_root=run_root,
                    budget_slice_usd=(
                        ledger.master_cap_usd * 0.75 if dynamic_pool else base_allocs[t]
                    ),
                    proxy=proxy,
                    ledger=ledger,
                    args=args,
                )
                for t in selected_tracks
            )
        )
        return list(results)

    if mode == "sequential":
        ordered_results: List[TrackExecutionResult] = []
        for idx, t in enumerate(selected_tracks):
            rem_tracks = selected_tracks[idx:]
            rem_budget = ledger.remaining_unreserved_usd()
            # Re-weight remaining unspent pool across remaining tracks (100% savings rollover!)
            rolled_allocs = compute_scaled_allocations(rem_tracks, rem_budget)
            res = await launch_single_track(
                track_id=t,
                harnesses_dir=harnesses_dir,
                run_root=run_root,
                budget_slice_usd=rolled_allocs[t],
                proxy=proxy,
                ledger=ledger,
                args=args,
            )
            ordered_results.append(res)
        return ordered_results

    if mode == "staged":
        # Wave 1: Workhorse multi-replicate benchmarks (`weft_111`, `scry_abios`)
        # Wave 2: Deep `gpt-6-astra` `xhigh` proof/clean-room tracks (`lean4_astra`, `rigid_880`)
        #         absorbing 100% of Wave 1's unspent prompt-cache savings!
        wave1 = [t for t in selected_tracks if t in ("weft_111", "scry_abios")]
        wave2 = [t for t in selected_tracks if t not in ("weft_111", "scry_abios")]
        all_res: List[TrackExecutionResult] = []
        if wave1:
            w1_res = await asyncio.gather(
                *(
                    launch_single_track(
                        track_id=t,
                        harnesses_dir=harnesses_dir,
                        run_root=run_root,
                        budget_slice_usd=base_allocs[t],
                        proxy=proxy,
                        ledger=ledger,
                        args=args,
                    )
                    for t in wave1
                )
            )
            all_res.extend(w1_res)
        if wave2:
            rem_budget = ledger.remaining_unreserved_usd()
            w2_allocs = compute_scaled_allocations(wave2, rem_budget)
            w2_res = await asyncio.gather(
                *(
                    launch_single_track(
                        track_id=t,
                        harnesses_dir=harnesses_dir,
                        run_root=run_root,
                        budget_slice_usd=w2_allocs[t],
                        proxy=proxy,
                        ledger=ledger,
                        args=args,
                    )
                    for t in wave2
                )
            )
            all_res.extend(w2_res)
        return all_res

    raise ValueError(f"Unknown execution mode={mode!r}")


# =============================================================================
# 5. Hierarchical `MASTER_SHA256SUMS` Roll-Up & Summary Renderer
# =============================================================================

def snapshot_harness_sources_and_build_master_sha256sums(
    harnesses_dir: Path, selected_tracks: Sequence[str], run_root: Path
) -> Tuple[Path, int]:
    """
    Copy exact harness `.py` versions used into `<run_root>/provenance_harnesses/` and emit a
    single `sha256sum -c MASTER_SHA256SUMS` manifest over every file in `<run_root>`.
    """
    prov_dir = run_root / "provenance_harnesses"
    prov_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__).resolve(), prov_dir / Path(__file__).name)
    for t in selected_tracks:
        src = harnesses_dir / HARNESS_FILENAMES[t]
        if src.exists():
            shutil.copy2(src, prov_dir / src.name)

    master_manifest = run_root / "MASTER_SHA256SUMS"
    entries: List[str] = []
    for file_p in sorted(run_root.rglob("*")):
        if not file_p.is_file() or file_p.name == "MASTER_SHA256SUMS":
            continue
        rel_posix = file_p.relative_to(run_root).as_posix()
        digest = hashlib.sha256(file_p.read_bytes()).hexdigest()
        entries.append(f"{digest}  {rel_posix}")

    master_manifest.write_text("\n".join(entries) + "\n", encoding="utf-8")
    return master_manifest, len(entries)


def render_master_markdown(report: Dict[str, Any]) -> str:
    b = report["master_ledger"]
    lines = [
        "# Master `$53.50` OpenAI Flex Burn & Provenance Roll-Up",
        "",
        f"- **Generated UTC**: `{report['generated_utc']}`",
        f"- **Schedule Mode**: `{report['mode']}` (`service_tier={report['service_tier']}`)",
        f"- **Shared Atomic Spend**: **`${b['spent_usd']:.4f}`** / `${b['master_cap_usd']:.2f}` cap "
        f"(Standard-tier equivalent: **`${b['standard_tier_equivalent_usd']:.4f}`**, "
        f"saved **`${b['flex_and_cache_savings_usd']:.4f}`** via Flex + `{b['prompt_cache_hit_pct']:.1f}%` cache hits)",
        f"- **Completed `/v1/responses` Calls**: `{b['total_calls_completed']}` "
        f"(`{b['total_calls_rejected_cap']}` cleanly gated at cap)",
        f"- **Root Integrity Manifest**: `MASTER_SHA256SUMS` (`{report['master_sha256sums_file_count']}` files hashed, "
        f"verification=`{report['master_sha256sums_verification']}`)",
        "",
        "## Per-Track Execution & Sub-Manifest Ledger",
        "",
        "| Track | Harness Script | Allocated Cap | Actual Spend | Exit | Wall Time | Child `SHA256SUMS` | Output Dir |",
        "| :--- | :--- | ---: | ---: | ---: | ---: | :--- | :--- |",
    ]
    for tr in report["tracks"]:
        status_col = "SKIPPED" if tr["skipped"] else str(tr["returncode"])
        lines.append(
            f"| `{tr['track_id']}` | `{tr['script_name']}` | `${tr['allocated_budget_usd']:.2f}` | "
            f"`${tr['actual_proxy_spent_usd']:.4f}` | `{status_col}` | `{tr['wall_seconds']:.2f}s` | "
            f"`{tr['child_sha256sums_status']}` ({tr['child_sha256sums_files_checked']}) | `{tr['output_dir']}` |"
        )
    lines.append("")
    return "\n".join(lines)


# =============================================================================
# 6. End-to-End Offline `--selftest` Across All 4 Real Sibling Harnesses
# =============================================================================

def make_universal_mock_upstream() -> UpstreamHandlerFn:
    """
    Universal mock `/v1/responses` responder for `--selftest` capable of serving real live
    HTTP requests from `weft_111_flex_harness.py` AND `scry_abios_equal_compute_eval.py`
    simultaneously over loopback sockets!
    """
    seq = 0
    lock = threading.Lock()

    def _upstream(payload: Dict[str, Any], headers: Dict[str, str], timeout_s: float) -> Tuple[int, bytes]:
        nonlocal seq
        with lock:
            seq += 1
            cid = seq

        model = str(payload.get("model", "gpt-6.1-sol"))
        instr = str(payload.get("instructions", ""))
        uinput = payload.get("input", "")
        uinput_str = uinput if isinstance(uinput, str) else json.dumps(uinput)

        # Case 1: `scry_abios_equal_compute_eval.py` Suite 1 reasoning calls
        if "TASK_ID:" in uinput_str:
            if "Arm A" in instr:
                out_txt = json.dumps(
                    {"scratchpad_steps": ["Step 1 checked."], "primary": "10", "secondary": "J5"}
                )
            elif "Arm B" in instr:
                out_txt = '[2,1,4,3,50,1,95,"(solve (steps (s1 1)) (ans 10 J5))","00000000"]'
            else:
                out_txt = "@1:ok\n§ANS|10|J5"
            resp = {
                "id": f"resp_master_mock_{cid}",
                "model": model,
                "service_tier": "flex",
                "status": "completed",
                "output_text": out_txt,
                "usage": {
                    "input_tokens": 280,
                    "input_tokens_details": {"cached_tokens": 192},
                    "output_tokens": 96,
                    "output_tokens_details": {"reasoning_tokens": 64},
                },
            }
            return 200, json.dumps(resp).encode("utf-8")

        # Case 2: `weft_111_flex_harness.py` tool-using / completion responses
        resp = {
            "id": f"resp_master_mock_{cid}",
            "model": model,
            "service_tier": "flex",
            "status": "completed",
            "output": [
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": "Completed codec verification round cleanly.",
                        }
                    ],
                }
            ],
            "output_text": "Completed codec verification round cleanly.",
            "usage": {
                "input_tokens": 1200,
                "input_tokens_details": {"cached_tokens": 1024},
                "output_tokens": 220,
                "output_tokens_details": {"reasoning_tokens": 160},
            },
        }
        return 200, json.dumps(resp).encode("utf-8")

    return _upstream


def run_selftest(harnesses_dir: Path) -> int:
    print("[selftest] 1/3 Verifying all 4 standalone sibling harnesses in parallel...")
    missing = [
        HARNESS_FILENAMES[k]
        for k in HARNESS_FILENAMES
        if not (harnesses_dir / HARNESS_FILENAMES[k]).exists()
    ]
    if missing:
        raise FileNotFoundError(f"Missing sibling harness scripts in {harnesses_dir}: {missing}")

    # Run `--selftest` on all 4 real sibling scripts concurrently
    procs: Dict[str, subprocess.Popen[str]] = {}
    for track_id, fname in HARNESS_FILENAMES.items():
        procs[track_id] = subprocess.Popen(
            [sys.executable, str(harnesses_dir / fname), "--selftest"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    sibling_status: Dict[str, bool] = {}
    for track_id, p in procs.items():
        out, _ = p.communicate(timeout=90)
        assert p.returncode == 0, f"Sibling {track_id} --selftest failed (rc={p.returncode}):\n{out}"
        sibling_status[track_id] = True

    print("[selftest] 2/3 Testing live loopback `/v1/responses` shared ledger proxy (concurrent + rollover + 402 cap)...")
    with tempfile.TemporaryDirectory(prefix="master_55_burn_selftest_") as tmp:
        run_root = Path(tmp) / "burn_run"
        run_root.mkdir(parents=True, exist_ok=True)
        ledger = MasterSharedBudgetLedger(
            master_cap_usd=53.50, ledger_log_path=run_root / "master_api_ledger.jsonl"
        )
        proxy = SharedLedgerProxyServer(ledger=ledger, upstream_fn=make_universal_mock_upstream())
        port = proxy.start()
        try:
            # Configure fast 2-track live subprocess test (`weft_111` + `scry_abios`) over real loopback TCP!
            ns = parse_args(
                [
                    "--tracks", "weft_111,scry_abios",
                    "--mode", "concurrent",
                    "--master-budget-usd", "53.50",
                    "--weft-replicates", "1",
                    "--scry-suite", "reasoning",
                    "--scry-models", "gpt-6.1-sol",
                    "--scry-efforts", "low",
                    "--scry-tasks-per-family", "1",
                    "--out-dir", str(run_root),
                ]
            )
            track_results = asyncio.run(
                execute_master_schedule(
                    selected_tracks=["weft_111", "scry_abios"],
                    mode="concurrent",
                    dynamic_pool=True,
                    harnesses_dir=harnesses_dir,
                    run_root=run_root,
                    proxy=proxy,
                    ledger=ledger,
                    args=ns,
                )
            )
            for tr in track_results:
                assert tr.returncode == 0, (
                    f"Live proxy run of {tr.track_id} failed (rc={tr.returncode}): "
                    + (run_root / tr.log_file).read_text(encoding="utf-8")
                )
                assert tr.child_sha256sums_status == "VERIFIED", (
                    f"Child SHA256SUMS not verified for {tr.track_id}: {tr.child_sha256sums_status}"
                )
                assert tr.actual_proxy_spent_usd > 0.0

            # Also verify hard atomic 402 cutoff when a tiny $0.0001 cap is hit!
            tiny_ledger = MasterSharedBudgetLedger(
                master_cap_usd=0.0001, ledger_log_path=run_root / "tiny_cap.jsonl"
            )
            tiny_proxy = SharedLedgerProxyServer(
                ledger=tiny_ledger, upstream_fn=make_universal_mock_upstream()
            )
            t_port = tiny_proxy.start()
            try:
                req = urllib.request.Request(
                    f"http://127.0.0.1:{t_port}/t/weft_111/v1/responses",
                    data=json.dumps(
                        {"model": "gpt-6-astra", "service_tier": "flex", "input": "hi", "max_output_tokens": 4096}
                    ).encode("utf-8"),
                    method="POST",
                    headers={"Content-Type": "application/json"},
                )
                got_402 = False
                try:
                    urllib.request.urlopen(req, timeout=5.0)
                except urllib.error.HTTPError as e:
                    got_402 = (e.code == 402) and ("credit_balance_exhausted" in e.read().decode("utf-8"))
                assert got_402, "Expected atomic HTTP 402 credit_balance_exhausted from tiny cap proxy!"
                assert tiny_ledger.snapshot()["spent_usd"] == 0.0
            finally:
                tiny_proxy.stop()
        finally:
            proxy.stop()

        print("[selftest] 3/3 Building & verifying hierarchical MASTER_SHA256SUMS...")
        snap = ledger.snapshot()
        report_obj = {
            "schema_version": "master_55_flex_burn_v1",
            "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "mode": "concurrent",
            "service_tier": "flex",
            "master_ledger": snap,
            "tracks": [tr.__dict__ for tr in track_results],
            "master_sha256sums_file_count": 0,
            "master_sha256sums_verification": "PENDING",
        }
        rep_json = run_root / "master_burn_report.json"
        rep_md = run_root / "master_burn_summary.md"
        rep_json.write_text(json.dumps(report_obj, indent=2) + "\n", encoding="utf-8")
        rep_md.write_text(render_master_markdown(report_obj), encoding="utf-8")

        master_sha_p, total_hashed = snapshot_harness_sources_and_build_master_sha256sums(
            harnesses_dir, ["weft_111", "scry_abios", "lean4_astra", "rigid_880"], run_root
        )
        py_ver, py_cnt = verify_sha256sums_manifest_pure_python(master_sha_p)
        assert py_ver == "VERIFIED" and py_cnt == total_hashed

        cli_chk = subprocess.run(
            ["sha256sum", "-c", "MASTER_SHA256SUMS"],
            cwd=str(run_root),
            text=True,
            capture_output=True,
        )
        assert cli_chk.returncode == 0, f"sha256sum -c MASTER_SHA256SUMS failed:\n{cli_chk.stderr}"

        print(
            json.dumps(
                {
                    "selftest": "PASSED",
                    "proxy_bound_port_tested": port,
                    "all_4_sibling_selftests_passed": sibling_status,
                    "live_proxy_calls_metered": snap["total_calls_completed"],
                    "simulated_shared_spend_usd": snap["spent_usd"],
                    "atomic_402_circuit_breaker_verified": True,
                    "master_sha256sums_files_verified": total_hashed,
                },
                indent=2,
            )
        )
    return 0


# =============================================================================
# 7. CLI Entrypoint
# =============================================================================

def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Unified Master Python Launcher for all four OpenAI Flex harnesses under a shared $53.50 ledger."
    )
    p.add_argument(
        "--selftest",
        action="store_true",
        help="Run all 4 child --selftest suites + live loopback proxy metering/cutoff + MASTER_SHA256SUMS check.",
    )
    p.add_argument(
        "--harnesses-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Directory containing weft_111_flex_harness.py, lean4_astra_proof_harness.py, "
        "scry_abios_equal_compute_eval.py, and rigid_realizations_880_certifier.py.",
    )
    p.add_argument(
        "--tracks",
        default="weft_111,lean4_astra,scry_abios,rigid_880",
        help="Comma-separated tracks to run (default: weft_111,lean4_astra,scry_abios,rigid_880).",
    )
    p.add_argument(
        "--mode",
        choices=("concurrent", "staged", "sequential"),
        default="concurrent",
        help="Execution topology: 'concurrent' (fastest pre-expiry burn), 'staged' (Wave 1 evals -> "
        "Wave 2 proofs with rollover), or 'sequential' (strict cascade with 100%% savings rollover).",
    )
    p.add_argument(
        "--dynamic-pool",
        action="store_true",
        default=True,
        help="Allow concurrent tracks to draw dynamically from the shared $53.50 proxy pool (default: True).",
    )
    p.add_argument(
        "--strict-slices",
        action="store_true",
        help="Restrict each concurrent track strictly to its initial static slice instead of dynamic pooling.",
    )
    p.add_argument(
        "--master-budget-usd",
        type=float,
        default=53.50,
        help="Single cross-process atomic USD cap across all four harnesses (default: 53.50 for $55 grant).",
    )
    p.add_argument(
        "--service-tier",
        choices=("flex", "default", "fast"),
        default="flex",
        help="OpenAI service_tier across harnesses (default: flex for 50%% Batch-rate pricing).",
    )
    p.add_argument(
        "--strict-flex",
        action="store_true",
        help="Never fall back to Standard tier on repeated Flex 429s.",
    )
    p.add_argument(
        "--pro-mode",
        action="store_true",
        help="Enable reasoning.mode='pro' on gpt-6-astra tracks (lean4_astra & rigid_880).",
    )
    p.add_argument(
        "--astra-effort",
        choices=("low", "medium", "high", "xhigh", "max"),
        default="xhigh",
        help="reasoning.effort for gpt-6-astra proof/certifier tracks (default: xhigh).",
    )
    # Optional local repo paths
    p.add_argument("--semver-repo", type=Path, default=None, help="Path to cloned Proven-Commons/semver repo.")
    p.add_argument("--rigid-repo", type=Path, default=None, help="Path to cloned Foundation-0/rigid-realizations repo.")
    p.add_argument("--rigid-cert", type=Path, action="append", default=[], help="Explicit 2D certificate JSON(s).")
    p.add_argument("--abios-validator", type=Path, default=None, help="Optional path to abios sym-validate.py.")
    p.add_argument(
        "--skip-missing-repos",
        action="store_true",
        help="Skip rigid_880 if neither --rigid-repo nor --rigid-cert is supplied (default: runs planted L880 fixture).",
    )
    # Workload sizing knobs
    p.add_argument("--weft-replicates", type=int, default=8, help="R3 paired Sol replicates for weft#111 (default: 8).")
    p.add_argument("--weft-astra-replicates", type=int, default=3, help="R3 paired Astra replicates for weft#111 (default: 3).")
    p.add_argument("--scry-suite", choices=("all", "reasoning", "handoff"), default="all")
    p.add_argument("--scry-models", default="gpt-6.1-sol,gpt-6-astra")
    p.add_argument("--scry-efforts", default="low,medium")
    p.add_argument("--scry-tasks-per-family", type=int, default=6)
    p.add_argument("--scry-handoff-cases", type=int, default=10)
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("./master_55_flex_burn_artifacts"),
        help="Root output directory for all 4 track folders, master ledger JSONL, and MASTER_SHA256SUMS.",
    )
    return p.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    args = parse_args(argv)
    harnesses_dir = args.harnesses_dir.resolve()

    if args.selftest:
        return run_selftest(harnesses_dir)

    if not os.environ.get("OPENAI_API_KEY", "").strip():
        print(
            "Error: OPENAI_API_KEY is not set. Export OPENAI_API_KEY='sk-...' (or run --selftest).",
            file=sys.stderr,
        )
        return 2

    selected_tracks = [t.strip() for t in args.tracks.split(",") if t.strip()]
    for t in selected_tracks:
        if t not in HARNESS_FILENAMES:
            print(f"Error: Unknown track '{t}'. Valid: {list(HARNESS_FILENAMES)}", file=sys.stderr)
            return 2
        if not (harnesses_dir / HARNESS_FILENAMES[t]).exists():
            print(
                f"Error: Missing harness script '{HARNESS_FILENAMES[t]}' in {harnesses_dir}",
                file=sys.stderr,
            )
            return 2

    run_root = args.out_dir.resolve()
    run_root.mkdir(parents=True, exist_ok=True)
    ledger = MasterSharedBudgetLedger(
        master_cap_usd=args.master_budget_usd,
        ledger_log_path=run_root / "master_api_ledger.jsonl",
    )
    proxy = SharedLedgerProxyServer(
        ledger=ledger,
        upstream_fn=live_openai_upstream_handler,
        upstream_timeout_s=910.0,
    )
    port = proxy.start()
    print(
        f"[master] Atomic loopback `/v1/responses` budget proxy listening on 127.0.0.1:{port} "
        f"(cap=${args.master_budget_usd:.2f}, mode={args.mode}, tracks={selected_tracks})"
    )

    try:
        track_results = asyncio.run(
            execute_master_schedule(
                selected_tracks=selected_tracks,
                mode=args.mode,
                dynamic_pool=(args.dynamic_pool and not args.strict_slices),
                harnesses_dir=harnesses_dir,
                run_root=run_root,
                proxy=proxy,
                ledger=ledger,
                args=args,
            )
        )
    finally:
        proxy.stop()

    snap = ledger.snapshot()
    report_obj: Dict[str, Any] = {
        "schema_version": "master_55_flex_burn_v1",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": args.mode,
        "service_tier": args.service_tier,
        "master_ledger": snap,
        "tracks": [tr.__dict__ for tr in track_results],
        "master_sha256sums_file_count": 0,
        "master_sha256sums_verification": "PENDING",
    }

    rep_json_p = run_root / "master_burn_report.json"
    rep_md_p = run_root / "master_burn_summary.md"
    # Write preliminary report files, then compute MASTER_SHA256SUMS over everything
    rep_json_p.write_text(json.dumps(report_obj, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    rep_md_p.write_text(render_master_markdown(report_obj), encoding="utf-8")

    master_sha_p, file_cnt = snapshot_harness_sources_and_build_master_sha256sums(
        harnesses_dir, selected_tracks, run_root
    )
    ver_status, _ = verify_sha256sums_manifest_pure_python(master_sha_p)

    # Update report with final count & re-stamp MASTER_SHA256SUMS so report hashes match 100%!
    report_obj["master_sha256sums_file_count"] = file_cnt
    report_obj["master_sha256sums_verification"] = ver_status
    rep_json_p.write_text(json.dumps(report_obj, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    md_final = render_master_markdown(report_obj)
    rep_md_p.write_text(md_final, encoding="utf-8")

    master_sha_p, file_cnt = snapshot_harness_sources_and_build_master_sha256sums(
        harnesses_dir, selected_tracks, run_root
    )
    ver_status, _ = verify_sha256sums_manifest_pure_python(master_sha_p)
    assert ver_status == "VERIFIED", f"MASTER_SHA256SUMS self-check failed: {ver_status}"

    print(md_final)
    print(f"[done] Master artifacts & MASTER_SHA256SUMS ({file_cnt} files) written to: {run_root}")
    any_hard_fail = any((not tr.skipped and tr.returncode != 0) for tr in track_results)
    return 1 if any_hard_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())