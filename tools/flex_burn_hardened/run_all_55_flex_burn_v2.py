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
      --confirm-live-spend \
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
import contextlib
import hashlib
import http.server
import json
import fcntl
import math
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

# Standard short-context, cache-write, and long-context (>272K input) rates
# per 1M tokens from https://developers.openai.com/api/docs/pricing
LONG_CONTEXT_INPUT_THRESHOLD = 272_000

MODEL_PRICING_STD_PER_MTOK: Dict[str, Dict[str, float]] = {
    "gpt-6-astra": {
        "input": 10.00, "cached_input": 1.00, "output": 50.00,
        "cache_write_30m": 12.50, "cache_write_12h": 25.00,
        "long_input": 20.00, "long_cached_input": 2.00, "long_output": 75.00,
        "long_cache_write_30m": 25.00, "long_cache_write_12h": 50.00,
    },
    "gpt-6.1-sol": {
        "input": 2.00, "cached_input": 0.10, "output": 10.00,
        "cache_write_30m": 2.50, "cache_write_12h": 5.00,
        "long_input": 4.00, "long_cached_input": 0.20, "long_output": 15.00,
        "long_cache_write_30m": 5.00, "long_cache_write_12h": 10.00,
    },
    "gpt-6-sol": {
        "input": 2.00, "cached_input": 0.20, "output": 10.00,
        "cache_write_30m": 2.50, "cache_write_12h": 5.00,
        "long_input": 4.00, "long_cached_input": 0.40, "long_output": 15.00,
        "long_cache_write_30m": 5.00, "long_cache_write_12h": 10.00,
    },
    "gpt-6.1-terra": {
        "input": 1.00, "cached_input": 0.05, "output": 5.00,
        "cache_write_30m": 1.25, "cache_write_12h": 2.50,
        "long_input": 2.00, "long_cached_input": 0.10, "long_output": 7.50,
        "long_cache_write_30m": 2.50, "long_cache_write_12h": 5.00,
    },
    "gpt-6-luna": {
        "input": 0.10, "cached_input": 0.01, "output": 0.50,
        "cache_write_30m": 0.125, "cache_write_12h": 0.25,
        "long_input": 0.20, "long_cached_input": 0.02, "long_output": 0.75,
        "long_cache_write_30m": 0.25, "long_cache_write_12h": 0.50,
    },
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


def write_child_log(log_path: Path, raw_output: bytes) -> None:
    """Persist child stdout after running redact_secrets_in_text, so hashes see redacted bytes."""
    text = raw_output.decode("utf-8", errors="replace")
    log_path.write_text(redact_secrets_in_text(text), encoding="utf-8")

HARNESS_FILENAMES: Dict[str, str] = {
    "weft_111":    "weft_111_flex_harness.py",
    "lean4_astra": "lean4_astra_proof_harness.py",
    "scry_abios":  "scry_abios_equal_compute_eval.py",
    "rigid_880":   "rigid_realizations_880_certifier.py",
}


class UnknownModelPricingError(ValueError):
    """Raised when a model has no row in MODEL_PRICING_STD_PER_MTOK."""


class InvalidLedgerAmount(ValueError):
    """Raised when a token count or USD amount is negative or non-finite."""


class LedgerWriteError(OSError):
    """Raised when a ledger append fails after the cap has been closed for this process."""


def is_finite_nonnegative(value: Any) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(number) and number >= 0.0


def require_finite_nonnegative(value: Any, name: str) -> float:
    if not is_finite_nonnegative(value):
        raise InvalidLedgerAmount(
            f"{name} must be a finite non-negative number, got {value!r}"
        )
    return float(value)


def require_nonnegative_int(value: Any, name: str) -> int:
    try:
        number = int(value)
        as_float = float(value)
    except (TypeError, ValueError) as exc:
        raise InvalidLedgerAmount(
            f"{name} must be a non-negative integer, got {value!r}"
        ) from exc
    if not math.isfinite(as_float) or number < 0:
        raise InvalidLedgerAmount(f"{name} must be a non-negative integer, got {value!r}")
    return number


def _rate_column(rates: Dict[str, float], input_tokens: int) -> Dict[str, float]:
    if input_tokens > LONG_CONTEXT_INPUT_THRESHOLD:
        return {
            "input": rates["long_input"],
            "cached_input": rates["long_cached_input"],
            "output": rates["long_output"],
            "cache_write_30m": rates["long_cache_write_30m"],
            "cache_write_12h": rates["long_cache_write_12h"],
        }
    return {
        "input": rates["input"],
        "cached_input": rates["cached_input"],
        "output": rates["output"],
        "cache_write_30m": rates["cache_write_30m"],
        "cache_write_12h": rates["cache_write_12h"],
    }


def compute_exact_cost_usd(
    model: str,
    service_tier: str,
    input_tokens: int,
    cached_tokens: int,
    output_tokens: int,
    cache_write_30m_tokens: int = 0,
    cache_write_12h_tokens: int = 0,
) -> Tuple[float, float]:
    """Return `(settled_tier_cost_usd, unscaled_list_rate_reference_usd)` (settled billing vs reference list rate)."""
    rates = MODEL_PRICING_STD_PER_MTOK.get(model)
    if rates is None:
        raise UnknownModelPricingError(f"No pricing row for model {model!r}")
    col = _rate_column(rates, input_tokens)
    cached = max(0, min(input_tokens, cached_tokens))
    write_30 = max(0, cache_write_30m_tokens)
    write_12 = max(0, cache_write_12h_tokens)
    # Cache writes are a subset of input tokens and are disjoint from cache reads.
    billed = cached + write_30 + write_12
    if billed > input_tokens:
        overflow = billed - input_tokens
        drop_12 = min(write_12, overflow)
        write_12 -= drop_12
        overflow -= drop_12
        drop_30 = min(write_30, overflow)
        write_30 -= drop_30
    uncached_plain = max(0, input_tokens - cached - write_30 - write_12)
    std_usd = (
        uncached_plain * col["input"] / 1_000_000.0
        + cached * col["cached_input"] / 1_000_000.0
        + write_30 * col["cache_write_30m"] / 1_000_000.0
        + write_12 * col["cache_write_12h"] / 1_000_000.0
        + output_tokens * col["output"] / 1_000_000.0
    )
    mult = SERVICE_TIER_MULTIPLIER.get(str(service_tier).lower(), 1.0)
    return (std_usd * mult, std_usd)


def estimate_payload_input_tokens(payload: Dict[str, Any]) -> int:
    raw = json.dumps(
        {"instructions": payload.get("instructions"), "input": payload.get("input"), "tools": payload.get("tools")},
        ensure_ascii=True,
    )
    return max(128, (len(raw) // 3) + 96)


def _prompt_cache_ttl(payload: Dict[str, Any]) -> str:
    options = payload.get("prompt_cache_options")
    if isinstance(options, dict) and str(options.get("ttl") or "") == "12h":
        return "12h"
    return "30m"


def _authorization_matches_proxy_token(received: Optional[str], token: str) -> bool:
    expected = f"Bearer {token}".encode("utf-8")
    got = (received or "").encode("utf-8")
    if len(got) != len(expected):
        return False
    return secrets.compare_digest(got, expected)


def _kill_process_group(pgid: int) -> None:
    if pgid <= 0:
        return
    try:
        os.killpg(pgid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError, OSError):
        return
    try:
        time.sleep(0.05)
        os.killpg(pgid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        return


def _terminate_popen(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    try:
        if proc.pid:
            _kill_process_group(os.getpgid(proc.pid))
    except (ProcessLookupError, PermissionError, OSError):
        try:
            proc.terminate()
        except OSError:
            pass
    try:
        proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            if proc.pid:
                _kill_process_group(os.getpgid(proc.pid))
        except (ProcessLookupError, PermissionError, OSError):
            try:
                proc.kill()
            except OSError:
                pass
        try:
            proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            pass


class ChildProcessGroupRegistry:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._pgids: set = set()

    def register_pid(self, pid: Optional[int]) -> None:
        if not pid:
            return
        try:
            pgid = os.getpgid(pid)
        except OSError:
            pgid = pid
        with self._lock:
            self._pgids.add(pgid)

    def discard_pid(self, pid: Optional[int]) -> None:
        if not pid:
            return
        try:
            pgid = os.getpgid(pid)
        except OSError:
            pgid = pid
        with self._lock:
            self._pgids.discard(pgid)

    def kill_all(self) -> None:
        with self._lock:
            pgids = list(self._pgids)
            self._pgids.clear()
        for pgid in pgids:
            _kill_process_group(pgid)


CHILD_PROCESS_GROUPS = ChildProcessGroupRegistry()


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
    `/v1/responses` proxy. A reserve reloads disk spend under an exclusive lock, then appends the hold before releasing that lock.
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
        self._cap_closed: bool = False
        self._cap_closed_reason: str = ""
        self._file_lock_fh = None
        self._file_lock_depth: int = 0
        self._reload_prior_spend_from_ledger()

    def _closed_sibling_path(self) -> Path:
        return Path(str(self.ledger_log_path) + ".closed")

    def _closed_dir_marker_path(self) -> Path:
        return self.ledger_log_path.parent / f".flex_burn_cap_closed.{self.ledger_log_path.name}"

    def _seen_stamp_path(self) -> Path:
        return self.ledger_log_path.parent / f".flex_burn_ledger_seen.{self.ledger_log_path.name}"

    def _lock_path(self) -> Path:
        return Path(str(self.ledger_log_path) + ".lock")

    def _fsync_directory(self, directory: Path) -> None:
        fd = os.open(str(directory), os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def _fsync_parent(self, path: Path) -> None:
        self._fsync_directory(path.parent)

    def _write_json_fsync(self, path: Path, payload: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = json.dumps(payload, ensure_ascii=True, allow_nan=False) + "\n"
        with path.open("w", encoding="utf-8") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        self._fsync_parent(path)

    def _read_json_object(self, path: Path) -> Optional[Dict[str, Any]]:
        try:
            raw = path.read_text(encoding="utf-8")
            obj = json.loads(raw)
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return None
        return obj if isinstance(obj, dict) else None

    @contextlib.contextmanager
    def _ledger_file_lock(self):
        """Exclusive flock, reentrant in the same thread."""
        if self._file_lock_depth > 0:
            self._file_lock_depth += 1
            try:
                yield
            finally:
                self._file_lock_depth -= 1
            return
        lock_path = self._lock_path()
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        created = not lock_path.exists()
        fh = lock_path.open("a+")
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
            if created:
                fh.flush()
                os.fsync(fh.fileno())
                self._fsync_parent(lock_path)
            self._file_lock_fh = fh
            self._file_lock_depth = 1
            try:
                yield
            finally:
                self._file_lock_depth = 0
                self._file_lock_fh = None
                try:
                    fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
                except OSError:
                    pass
        finally:
            fh.close()

    def _reload_prior_spend_from_ledger(self) -> None:
        """Load already-settled spend from the ledger file so a later process inherits the remaining cap.

        A non-empty line that is not valid JSON, or a record with a negative or
        non-finite USD amount, closes the cap: later reserves are refused until
        an operator repairs the file and explicitly removes the durable close
        markers. A later cumulative below one already seen also closes the cap,
        and spent is at least the maximum cumulative seen.

        A first run has no ledger, no close markers, and no seen stamp, so
        reserves are allowed. The first successful append writes the seen stamp.
        After that, a missing, empty, renamed-away, or replaced ledger is a lost
        record, not a first run, and the cap closes.

        Reserve, commit, credit, and unresolved-hold paths take the exclusive
        file lock, reload this state from disk, and only then append, so a
        second process sees the first process's hold before it checks the cap.
        """
        with self._ledger_file_lock():
            self._reload_prior_spend_from_ledger_locked()

    def _reset_ledger_derived_memory(self) -> Dict[str, Any]:
        """Reset spend loaded from disk. Keep process-local reservations and counters."""
        saved = {
            "reserved": self.reserved_in_flight_usd,
            "closed": self._cap_closed,
            "reason": self._cap_closed_reason,
            "tracks": {
                key: (
                    track.reserved_in_flight_usd,
                    track.calls_rejected_cap,
                    track.calls_retried_429_or_5xx,
                )
                for key, track in self.tracks.items()
            },
        }
        self.spent_usd = 0.0
        self.standard_equiv_usd = 0.0
        self._seq = 0
        for track in self.tracks.values():
            track.spent_usd = 0.0
            track.standard_equiv_usd = 0.0
            track.calls_completed = 0
            track.input_tokens = 0
            track.cached_tokens = 0
            track.output_tokens = 0
            track.reasoning_tokens = 0
        return saved

    def _restore_process_local_memory(self, saved: Dict[str, Any]) -> None:
        self.reserved_in_flight_usd = saved["reserved"]
        if saved["closed"]:
            self._cap_closed = True
            if not self._cap_closed_reason:
                self._cap_closed_reason = saved["reason"]
        for key, values in saved["tracks"].items():
            track = self.tracks.setdefault(key, TrackUsageStats())
            track.reserved_in_flight_usd = values[0]
            track.calls_rejected_cap = values[1]
            track.calls_retried_429_or_5xx = values[2]

    def _honor_durable_close_markers(self) -> Optional[float]:
        """Return any spent amount stored on a durable close marker, or None."""
        marked_spent: Optional[float] = None
        sources = []
        sibling = self._closed_sibling_path()
        directory = self._closed_dir_marker_path()
        if sibling.is_file():
            sources.append(sibling)
        if directory.is_file():
            sources.append(directory)
        if not sources:
            return None
        reason = f"durable cap-closed marker at {sources[0]}"
        for path in sources:
            obj = self._read_json_object(path)
            if obj:
                if obj.get("reason"):
                    reason = str(obj["reason"])
                if is_finite_nonnegative(obj.get("spent_usd")):
                    value = float(obj["spent_usd"])
                    marked_spent = value if marked_spent is None else max(marked_spent, value)
        already = self._cap_closed
        self._cap_closed = True
        self._cap_closed_reason = reason
        if not already:
            print(
                f"[master] Ledger cap closed: {reason}. "
                "Refusing new reserves until an operator repairs the ledger.",
                file=sys.stderr,
            )
        return marked_spent

    def _ledger_file_is_empty(self, raw_text: str) -> bool:
        return not any(line.strip() for line in raw_text.splitlines())

    def _reload_prior_spend_from_ledger_locked(self) -> None:
        saved = self._reset_ledger_derived_memory()
        marked_spent = self._honor_durable_close_markers()
        jsonl_missing = not self.ledger_log_path.is_file()
        raw_text = ""
        if not jsonl_missing:
            try:
                raw_text = self.ledger_log_path.read_text(encoding="utf-8")
            except OSError as exc:
                if marked_spent is not None:
                    self.spent_usd = max(self.spent_usd, marked_spent)
                self._close_cap(
                    f"cannot read ledger file {self.ledger_log_path}: {exc}",
                    spent_usd=self.spent_usd,
                )
                self._restore_process_local_memory(saved)
                return
        jsonl_empty = jsonl_missing or self._ledger_file_is_empty(raw_text)
        if jsonl_empty:
            if self._cap_closed:
                if marked_spent is not None:
                    self.spent_usd = max(self.spent_usd, marked_spent)
                self._restore_process_local_memory(saved)
                return
            if self._seen_stamp_path().is_file():
                self._close_cap(
                    f"ledger file is missing or empty after spend was recorded: {self.ledger_log_path}",
                    spent_usd=self.spent_usd,
                )
                self._restore_process_local_memory(saved)
                return
            # Genuinely first run: no ledger, no close marker, no seen stamp.
            self._restore_process_local_memory(saved)
            return

        prior_spent = 0.0
        prior_std = 0.0
        prior_seq = 0
        max_cumulative = 0.0
        saw_cumulative = False

        def _remember_spent() -> None:
            self.spent_usd = max(self.spent_usd, prior_spent, max_cumulative)
            if marked_spent is not None:
                self.spent_usd = max(self.spent_usd, marked_spent)

        for raw in raw_text.splitlines():
            line = raw.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                _remember_spent()
                self._close_cap(
                    f"torn or invalid ledger line in {self.ledger_log_path}: {line[:120]!r}",
                    spent_usd=self.spent_usd,
                )
                self._restore_process_local_memory(saved)
                return
            if not isinstance(entry, dict):
                _remember_spent()
                self._close_cap(
                    f"corrupt ledger record in {self.ledger_log_path}: line is not an object",
                    spent_usd=self.spent_usd,
                )
                self._restore_process_local_memory(saved)
                return
            money_keys = (
                "call_cost_usd",
                "computed_call_cost_usd",
                "master_cumulative_spent_usd",
                "reserved_usd",
                "standard_equiv_usd",
                "spend_delta_usd",
            )
            for key in money_keys:
                if key in entry and not is_finite_nonnegative(entry[key]):
                    _remember_spent()
                    self._close_cap(
                        f"corrupt ledger amount {key}={entry[key]!r} in {self.ledger_log_path}",
                        spent_usd=self.spent_usd,
                    )
                    self._restore_process_local_memory(saved)
                    return
            if "seq" in entry:
                try:
                    prior_seq = max(prior_seq, int(entry["seq"]))
                except (TypeError, ValueError):
                    pass
            call_cost = 0.0
            std_cost = 0.0
            if "call_cost_usd" in entry:
                call_cost = float(entry["call_cost_usd"])
            if "standard_equiv_usd" in entry:
                std_cost = float(entry["standard_equiv_usd"])
            if "spend_delta_usd" in entry:
                track_cost = float(entry["spend_delta_usd"])
            else:
                track_cost = call_cost
            if "master_cumulative_spent_usd" in entry:
                cumulative = float(entry["master_cumulative_spent_usd"])
                if saw_cumulative and cumulative < max_cumulative - 1e-12:
                    _remember_spent()
                    self._close_cap(
                        f"later master_cumulative_spent_usd {cumulative} is below "
                        f"already-seen {max_cumulative} in {self.ledger_log_path}",
                        spent_usd=self.spent_usd,
                    )
                saw_cumulative = True
                max_cumulative = max(max_cumulative, cumulative)
                prior_spent = max_cumulative
            elif not saw_cumulative:
                prior_spent += call_cost
                max_cumulative = max(max_cumulative, prior_spent)
            if not is_finite_nonnegative(prior_spent):
                _remember_spent()
                self._close_cap(
                    f"corrupt cumulative spent {prior_spent!r} in {self.ledger_log_path}",
                    spent_usd=self.spent_usd,
                )
                self._restore_process_local_memory(saved)
                return
            prior_std += std_cost
            track_id = entry.get("track")
            if track_id:
                t_stats = self.tracks.setdefault(str(track_id), TrackUsageStats())
                t_stats.spent_usd += track_cost
                t_stats.standard_equiv_usd += std_cost
                t_stats.calls_completed += 1
                for field_name, attr in (
                    ("input_tokens", "input_tokens"),
                    ("cached_tokens", "cached_tokens"),
                    ("output_tokens", "output_tokens"),
                    ("reasoning_tokens", "reasoning_tokens"),
                ):
                    try:
                        setattr(t_stats, attr, getattr(t_stats, attr) + int(entry.get(field_name, 0) or 0))
                    except (TypeError, ValueError):
                        pass
        if not is_finite_nonnegative(prior_spent):
            _remember_spent()
            self._close_cap(
                f"corrupt reloaded spent {prior_spent!r} in {self.ledger_log_path}",
                spent_usd=self.spent_usd,
            )
            self._restore_process_local_memory(saved)
            return
        self.spent_usd = max(prior_spent, max_cumulative)
        if marked_spent is not None:
            self.spent_usd = max(self.spent_usd, marked_spent)
        self.standard_equiv_usd = prior_std if is_finite_nonnegative(prior_std) else 0.0
        self._seq = prior_seq
        self._restore_process_local_memory(saved)

    def _existing_marker_spent(self) -> float:
        marked = 0.0
        for path in (self._closed_sibling_path(), self._closed_dir_marker_path()):
            if not path.is_file():
                continue
            obj = self._read_json_object(path)
            if obj and is_finite_nonnegative(obj.get("spent_usd")):
                marked = max(marked, float(obj["spent_usd"]))
        return marked

    def _close_cap(self, reason: str, spent_usd: Optional[float] = None) -> None:
        candidates = [self._existing_marker_spent()]
        for value in (spent_usd, self.spent_usd):
            if is_finite_nonnegative(value):
                candidates.append(float(value))
        recorded = max(candidates)
        if is_finite_nonnegative(self.spent_usd):
            self.spent_usd = max(self.spent_usd, recorded)
        else:
            self.spent_usd = recorded
        already = self._cap_closed
        self._cap_closed = True
        self._cap_closed_reason = reason
        if not already:
            print(
                f"[master] Ledger cap closed: {reason}. "
                "Refusing new reserves until an operator repairs the ledger.",
                file=sys.stderr,
            )
        payload = {
            "closed": True,
            "ledger": self.ledger_log_path.name,
            "reason": reason,
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "spent_usd": recorded,
        }
        for path in (self._closed_sibling_path(), self._closed_dir_marker_path()):
            try:
                self._write_json_fsync(path, payload)
            except (OSError, TypeError, ValueError) as exc:
                print(
                    f"[master] Failed to write durable cap-closed marker {path}: {exc}",
                    file=sys.stderr,
                )

    def _append_ledger_line_locked(self, entry: Dict[str, Any]) -> None:
        """Append one complete JSON line, then the caller may credit spent_usd.

        Safe ordering: validate and write the full line (flush + fsync) before
        any in-memory spent_usd update. If the append raises, the cap is closed
        for this process, spent_usd is left unchanged, and in-flight
        reservations are kept so later reserves are refused. The caller must
        hold the exclusive file lock (or this method takes it, reentrantly)
        around append and reload so concurrent processes share one ledger.
        After creating the jsonl or the seen stamp, the parent directory is
        fsynced so the new directory entries survive a crash.
        """
        money_keys = (
            "call_cost_usd",
            "computed_call_cost_usd",
            "master_cumulative_spent_usd",
            "reserved_usd",
            "standard_equiv_usd",
            "overrun_usd",
            "over_cap_usd",
            "spend_delta_usd",
        )
        for key in money_keys:
            if key in entry:
                require_finite_nonnegative(entry[key], key)
        try:
            line = json.dumps(entry, ensure_ascii=True, allow_nan=False) + "\n"
        except (TypeError, ValueError) as exc:
            self._close_cap(f"refusing to write a non-JSON ledger amount: {exc}")
            raise LedgerWriteError(str(exc)) from exc
        try:
            with self._ledger_file_lock():
                self.ledger_log_path.parent.mkdir(parents=True, exist_ok=True)
                with self.ledger_log_path.open("a", encoding="utf-8") as fh:
                    fh.write(line)
                    fh.flush()
                    os.fsync(fh.fileno())
                self._fsync_parent(self.ledger_log_path)
                seen = {
                    "ledger": self.ledger_log_path.name,
                    "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
                self._write_json_fsync(self._seen_stamp_path(), seen)
        except OSError as exc:
            self._close_cap(f"ledger append failed for {self.ledger_log_path}: {exc}")
            raise LedgerWriteError(str(exc)) from exc

    def _credit_spent_locked(self, amount: float, target: Optional[TrackUsageStats] = None) -> None:
        """Add a finite non-negative amount to spent_usd. Never decreases spent."""
        credit = require_finite_nonnegative(amount, "spent credit")
        if not is_finite_nonnegative(self.spent_usd):
            self._close_cap(f"in-memory spent_usd is not finite and non-negative: {self.spent_usd!r}")
            raise InvalidLedgerAmount(self._cap_closed_reason)
        self.spent_usd += credit
        if target is not None:
            if not is_finite_nonnegative(target.spent_usd):
                target.spent_usd = 0.0
            target.spent_usd += credit

    def _reservation_already_on_disk(self, reserved: float) -> bool:
        """True when this process still holds a reservation that try_reserve persisted."""
        return is_finite_nonnegative(reserved) and self.reserved_in_flight_usd + 1e-12 >= reserved

    def try_reserve(
        self,
        track_id: str,
        model: str,
        service_tier: str,
        est_in_tokens: int,
        max_out_tokens: int,
        cache_write_ttl: str = "30m",
    ) -> Tuple[bool, float, str]:
        if int(max_out_tokens) <= 0:
            return False, 0.0, "max_output_tokens must be a positive integer"
        write_12 = int(est_in_tokens) if cache_write_ttl == "12h" else 0
        write_30 = int(est_in_tokens) if cache_write_ttl != "12h" else 0
        try:
            worst_usd, _ = compute_exact_cost_usd(
                model=model,
                service_tier=service_tier,
                input_tokens=est_in_tokens,
                cached_tokens=0,
                output_tokens=max_out_tokens,
                cache_write_30m_tokens=write_30,
                cache_write_12h_tokens=write_12,
            )
        except UnknownModelPricingError as exc:
            return False, 0.0, str(exc)
        if not is_finite_nonnegative(worst_usd):
            return False, 0.0, "reservation estimate is not a finite non-negative amount"
        with self._lock:
            with self._ledger_file_lock():
                self._reload_prior_spend_from_ledger_locked()
                t_stats = self.tracks.setdefault(track_id, TrackUsageStats())
                if self._cap_closed:
                    t_stats.calls_rejected_cap += 1
                    return False, 0.0, (
                        self._cap_closed_reason
                        or "Ledger cap is closed until an operator repairs the ledger."
                    )
                if not is_finite_nonnegative(self.spent_usd):
                    self._close_cap("in-memory spent or reserved amount is not finite and non-negative")
                    t_stats.calls_rejected_cap += 1
                    return False, 0.0, self._cap_closed_reason
                # spent_usd is the disk max, including persisted reservations from
                # this process and others. Do not add reserved_in_flight again.
                if self.spent_usd >= self.master_cap_usd - 1e-12:
                    t_stats.calls_rejected_cap += 1
                    reason = (
                        f"Master shared cap (${self.master_cap_usd:.2f}) reached: "
                        f"spent=${self.spent_usd:.4f}, reserved=${self.reserved_in_flight_usd:.4f}."
                    )
                    return False, 0.0, reason
                projected = self.spent_usd + worst_usd
                if projected > self.master_cap_usd + 1e-12:
                    t_stats.calls_rejected_cap += 1
                    reason = (
                        f"Master shared cap (${self.master_cap_usd:.2f}) reached: "
                        f"spent=${self.spent_usd:.4f}, reserved=${self.reserved_in_flight_usd:.4f}, "
                        f"needed_worst_case=${worst_usd:.4f}."
                    )
                    return False, 0.0, reason
                seq_no = self._seq + 1
                entry = {
                    "seq": seq_no,
                    "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "event": "reserved",
                    "track": track_id,
                    "call_cost_usd": round(worst_usd, 6),
                    "reserved_usd": round(worst_usd, 6),
                    "computed_call_cost_usd": round(worst_usd, 6),
                    "spend_delta_usd": round(worst_usd, 6),
                    "over_cap_usd": round(max(0.0, projected - self.master_cap_usd), 6),
                    "master_cumulative_spent_usd": round(projected, 6),
                    "master_remaining_usd": round(self.master_cap_usd - projected, 6),
                }
                try:
                    self._append_ledger_line_locked(entry)
                except LedgerWriteError:
                    # Cap is closed. Keep the in-memory hold so this process
                    # still refuses later reserves if the durable markers could
                    # not be written, then let the handler return 502.
                    self.reserved_in_flight_usd += worst_usd
                    t_stats.reserved_in_flight_usd += worst_usd
                    raise
                self._seq = seq_no
                self._credit_spent_locked(worst_usd, t_stats)
                self.reserved_in_flight_usd += worst_usd
                t_stats.reserved_in_flight_usd += worst_usd
                return True, worst_usd, "OK"

    def release_without_spend(self, track_id: str, reserved_usd: float, retryable: bool = False) -> None:
        with self._lock:
            if not is_finite_nonnegative(reserved_usd):
                return
            # The reservation was already persisted under the file lock. Spent
            # never decreases, so a 429 or 5xx does not return the hold to the
            # shared cap. Only the process-local in-flight bookkeeping is cleared.
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
        cache_write_30m_tokens: int = 0,
        cache_write_12h_tokens: int = 0,
    ) -> float:
        reserved = require_finite_nonnegative(reserved_usd, "reserved_usd")
        in_tok = require_nonnegative_int(input_tokens, "input_tokens")
        cached_tok = require_nonnegative_int(cached_tokens, "cached_tokens")
        out_tok = require_nonnegative_int(output_tokens, "output_tokens")
        reas_tok = require_nonnegative_int(reasoning_tokens, "reasoning_tokens")
        write_30 = require_nonnegative_int(cache_write_30m_tokens, "cache_write_30m_tokens")
        write_12 = require_nonnegative_int(cache_write_12h_tokens, "cache_write_12h_tokens")
        actual_usd, std_usd = compute_exact_cost_usd(
            model=model,
            service_tier=service_tier,
            input_tokens=in_tok,
            cached_tokens=cached_tok,
            output_tokens=out_tok,
            cache_write_30m_tokens=write_30,
            cache_write_12h_tokens=write_12,
        )
        charged_usd = require_finite_nonnegative(actual_usd, "computed_call_cost_usd")
        charged_std = require_finite_nonnegative(std_usd, "standard_equiv_usd")
        overrun_usd = max(0.0, charged_usd - reserved)
        with self._lock:
            with self._ledger_file_lock():
                self._reload_prior_spend_from_ledger_locked()
                if not is_finite_nonnegative(self.spent_usd):
                    self._close_cap(f"in-memory spent_usd is not finite and non-negative: {self.spent_usd!r}")
                    raise InvalidLedgerAmount(self._cap_closed_reason)
                # If try_reserve already appended this hold, disk max includes
                # `reserved`. Credit only the overrun so a later settle cannot
                # double-count the reservation. A cheaper settle does not lower
                # the cumulative: unused reserve stays spent, which keeps the
                # ledger monotonic. If this process has no matching in-flight
                # hold, treat the charge as new spend.
                if self._reservation_already_on_disk(reserved):
                    delta = max(0.0, charged_usd - reserved)
                else:
                    delta = charged_usd
                projected_spent = self.spent_usd + delta
                seq_no = self._seq + 1
                entry = {
                    "seq": seq_no,
                    "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "track": track_id,
                    "response_id": response_id,
                    "model": model,
                    "service_tier": service_tier,
                    "input_tokens": in_tok,
                    "cached_tokens": cached_tok,
                    "output_tokens": out_tok,
                    "reasoning_tokens": reas_tok,
                    "event": "settled",
                    "call_cost_usd": round(charged_usd, 6),
                    "standard_equiv_usd": round(charged_std, 6),
                    "computed_call_cost_usd": round(charged_usd, 6),
                    "reserved_usd": round(reserved, 6),
                    "spend_delta_usd": round(delta, 6),
                    "overrun_usd": round(overrun_usd, 6),
                    "over_cap_usd": round(max(0.0, projected_spent - self.master_cap_usd), 6),
                    "master_cumulative_spent_usd": round(projected_spent, 6),
                    "master_remaining_usd": round(self.master_cap_usd - projected_spent, 6),
                    "latency_s": round(latency_s, 3),
                }
                self._append_ledger_line_locked(entry)
                self._seq = seq_no
                self.reserved_in_flight_usd = max(0.0, self.reserved_in_flight_usd - reserved)
                t_stats = self.tracks.setdefault(track_id, TrackUsageStats())
                t_stats.reserved_in_flight_usd = max(0.0, t_stats.reserved_in_flight_usd - reserved)
                self._credit_spent_locked(delta, t_stats)
                t_stats.standard_equiv_usd += charged_std
                t_stats.calls_completed += 1
                t_stats.input_tokens += in_tok
                t_stats.cached_tokens += cached_tok
                t_stats.output_tokens += out_tok
                t_stats.reasoning_tokens += reas_tok
                self.standard_equiv_usd += charged_std
                if overrun_usd > 1e-12 or self.spent_usd > self.master_cap_usd + 1e-12:
                    print(
                        f"[master] Ledger overrun: computed=${charged_usd:.6f} reserved=${reserved:.6f} "
                        f"spent=${self.spent_usd:.6f} cap=${self.master_cap_usd:.2f} "
                        f"over_cap=${max(0.0, self.spent_usd - self.master_cap_usd):.6f}",
                        file=sys.stderr,
                    )
        return charged_usd

    def commit_unresolved_hold(self, track_id: str, reserved_usd: float, reason: str) -> None:
        if not is_finite_nonnegative(reserved_usd):
            print(
                f"[master] Rejected unresolved hold: amount is not a finite "
                f"non-negative number: {reserved_usd!r} (reason={reason})",
                file=sys.stderr,
            )
            return
        reserved = float(reserved_usd)
        with self._lock:
            with self._ledger_file_lock():
                self._reload_prior_spend_from_ledger_locked()
                if not is_finite_nonnegative(self.spent_usd):
                    self._close_cap(f"in-memory spent_usd is not finite and non-negative: {self.spent_usd!r}")
                    return
                # try_reserve already wrote this hold. Confirm it without adding
                # the reserved amount a second time. If there is no matching
                # in-flight reservation, persist the hold as new spend.
                if self._reservation_already_on_disk(reserved):
                    delta = 0.0
                else:
                    delta = reserved
                projected_spent = self.spent_usd + delta
                seq_no = self._seq + 1
                entry = {
                    "seq": seq_no,
                    "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "event": "unresolved_hold",
                    "reason": reason,
                    "track": track_id,
                    "call_cost_usd": round(reserved, 6),
                    "reserved_usd": round(reserved, 6),
                    "computed_call_cost_usd": round(reserved, 6),
                    "spend_delta_usd": round(delta, 6),
                    "over_cap_usd": round(max(0.0, projected_spent - self.master_cap_usd), 6),
                    "master_cumulative_spent_usd": round(projected_spent, 6),
                    "master_remaining_usd": round(self.master_cap_usd - projected_spent, 6),
                }
                self._append_ledger_line_locked(entry)
                self._seq = seq_no
                self.reserved_in_flight_usd = max(0.0, self.reserved_in_flight_usd - reserved)
                t_stats = self.tracks.setdefault(track_id, TrackUsageStats())
                t_stats.reserved_in_flight_usd = max(0.0, t_stats.reserved_in_flight_usd - reserved)
                if delta > 0.0:
                    self._credit_spent_locked(delta, t_stats)
                print(
                    f"[master] Unresolved hold persisted: reason={reason} "
                    f"held=${reserved:.6f} spent=${self.spent_usd:.6f} cap=${self.master_cap_usd:.2f}",
                    file=sys.stderr,
                )

    def remaining_unreserved_usd(self) -> float:
        with self._lock:
            # spent_usd already includes persisted reservations.
            return max(0.0, self.master_cap_usd - self.spent_usd)


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
                "remaining_usd": round(self.master_cap_usd - self.spent_usd, 6),
                "over_cap_usd": round(max(0.0, self.spent_usd - self.master_cap_usd), 6),
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
        proxy_token: Optional[str] = None,
        upstream_token: Optional[str] = None,
    ) -> None:
        self.ledger = ledger
        self.upstream_fn = upstream_fn
        self.upstream_timeout_s = upstream_timeout_s
        self.proxy_token = proxy_token or ("sk-proxy-" + secrets.token_urlsafe(32))
        self.upstream_token = (
            upstream_token if upstream_token is not None else os.environ.get("OPENAI_API_KEY", "")
        )
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
                if not _authorization_matches_proxy_token(
                    self.headers.get("Authorization"), outer.proxy_token
                ):
                    err_bytes = json.dumps(
                        {"error": {"type": "invalid_proxy_token", "message": "Proxy token required"}}
                    ).encode("utf-8")
                    self._send_bytes(401, err_bytes)
                    return

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
                if not isinstance(payload, dict):
                    err_bytes = json.dumps({"error": {"message": "JSON body must be an object"}}).encode("utf-8")
                    self._send_bytes(400, err_bytes)
                    return

                model = str(payload.get("model", "gpt-6-astra"))
                tier = str(payload.get("service_tier") or "flex")
                raw_max = payload.get("max_output_tokens")
                if raw_max is None:
                    max_out = 8192
                else:
                    try:
                        max_out = int(raw_max)
                    except (TypeError, ValueError):
                        err_bytes = json.dumps(
                            {"error": {"message": "max_output_tokens must be a positive integer"}}
                        ).encode("utf-8")
                        self._send_bytes(400, err_bytes)
                        return
                    if max_out <= 0:
                        err_bytes = json.dumps(
                            {"error": {"message": "max_output_tokens must be a positive integer"}}
                        ).encode("utf-8")
                        self._send_bytes(400, err_bytes)
                        return

                payload = dict(payload)
                payload["max_output_tokens"] = max_out
                cache_ttl = _prompt_cache_ttl(payload)
                est_in = estimate_payload_input_tokens(payload)

                try:
                    ok, reserved_usd, reason = outer.ledger.try_reserve(
                        track_id=track_id,
                        model=model,
                        service_tier=tier,
                        est_in_tokens=est_in,
                        max_out_tokens=max_out,
                        cache_write_ttl=cache_ttl,
                    )
                except LedgerWriteError as write_exc:
                    err_bytes = json.dumps(
                        {
                            "error": {
                                "type": "ledger_write_error",
                                "message": str(write_exc),
                            }
                        }
                    ).encode("utf-8")
                    self._send_bytes(502, err_bytes)
                    return
                if not ok:
                    # Emit `credit_balance_exhausted` / `insufficient_quota` so child harnesses
                    # trigger their clean graceful stop and write SHA256SUMS!
                    cutoff_code = "invalid_model" if "No pricing row" in reason else "credit_balance_exhausted"
                    cutoff_status = 400 if cutoff_code == "invalid_model" else 402
                    cutoff_bytes = json.dumps(
                        {
                            "error": {
                                "code": cutoff_code,
                                "type": "invalid_request_error" if cutoff_status == 400 else "insufficient_quota",
                                "message": reason,
                            }
                        }
                    ).encode("utf-8")
                    self._send_bytes(cutoff_status, cutoff_bytes)
                    return

                t0 = time.monotonic()
                try:
                    status_code, resp_bytes = outer.upstream_fn(
                        payload,
                        {"Authorization": f"Bearer {outer.upstream_token}" if outer.upstream_token else ""},
                        outer.upstream_timeout_s,
                    )
                except Exception as net_exc:
                    # Persist the hold: a transport error may still have been billed upstream.
                    try:
                        outer.ledger.commit_unresolved_hold(
                            track_id, reserved_usd, reason="upstream_network_error"
                        )
                    except LedgerWriteError:
                        # Cap is closed and the in-memory reservation is kept.
                        pass
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
                        details = usage.get("input_tokens_details") or {}
                        cached_tok = int(details.get("cached_tokens", 0))
                        write_details = details.get("cache_write_tokens_details") or {}
                        write_30 = int(write_details.get("ttl_30m_tokens", 0) or 0)
                        write_12 = int(write_details.get("ttl_12h_tokens", 0) or 0)
                        if write_30 == 0 and write_12 == 0:
                            total_write = int(
                                details.get("cache_write_tokens")
                                or details.get("cache_creation_tokens")
                                or 0
                            )
                            if cache_ttl == "12h":
                                write_12 = total_write
                            else:
                                write_30 = total_write
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
                            cache_write_30m_tokens=write_30,
                            cache_write_12h_tokens=write_12,
                        )
                    except LedgerWriteError:
                        # Cap is closed and the in-memory reservation is kept.
                        pass
                    except Exception:
                        # Persist the hold: a 200 with unparsable usage or a negative /
                        # non-finite cost may still have been billed.
                        try:
                            outer.ledger.commit_unresolved_hold(
                                track_id, reserved_usd, reason="unparsable_200"
                            )
                        except LedgerWriteError:
                            pass
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
    # Children authenticate to the loopback proxy with the proxy token, not the upstream key.
    env["OPENAI_API_KEY"] = proxy.proxy_token
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
        start_new_session=True,
    )
    CHILD_PROCESS_GROUPS.register_pid(proc.pid)
    try:
        stdout_bytes, _ = await proc.communicate()
    except BaseException:
        if proc.returncode is None and proc.pid:
            try:
                _kill_process_group(os.getpgid(proc.pid))
            except (ProcessLookupError, PermissionError, OSError):
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass
        raise
    finally:
        CHILD_PROCESS_GROUPS.discard_pid(proc.pid)
    elapsed = time.monotonic() - t0

    write_child_log(log_path, stdout_bytes or b"")
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


def _normalize_gather_results(
    tracks: Sequence[str],
    results: Sequence[Any],
    budget_slices: Dict[str, float],
) -> List[TrackExecutionResult]:
    normalized: List[TrackExecutionResult] = []
    for track_id, res in zip(tracks, results):
        if isinstance(res, TrackExecutionResult):
            normalized.append(res)
            continue
        normalized.append(
            TrackExecutionResult(
                track_id=track_id,
                script_name=HARNESS_FILENAMES.get(track_id, track_id),
                allocated_budget_usd=round(float(budget_slices.get(track_id, 0.0)), 6),
                actual_proxy_spent_usd=0.0,
                returncode=1,
                wall_seconds=0.0,
                output_dir=f"track_{track_id}",
                child_sha256sums_status="ERROR",
                child_sha256sums_files_checked=0,
                log_file=f"logs/{track_id}.log",
                skipped=False,
                skip_reason=f"{type(res).__name__}: {res}",
            )
        )
    return normalized


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
        slices = {
            t: (ledger.master_cap_usd * 0.75 if dynamic_pool else base_allocs[t])
            for t in selected_tracks
        }
        results = await asyncio.gather(
            *(
                launch_single_track(
                    track_id=t,
                    harnesses_dir=harnesses_dir,
                    run_root=run_root,
                    budget_slice_usd=slices[t],
                    proxy=proxy,
                    ledger=ledger,
                    args=args,
                )
                for t in selected_tracks
            ),
            return_exceptions=True,
        )
        return _normalize_gather_results(selected_tracks, results, slices)

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
            w1_slices = {t: base_allocs[t] for t in wave1}
            w1_res = await asyncio.gather(
                *(
                    launch_single_track(
                        track_id=t,
                        harnesses_dir=harnesses_dir,
                        run_root=run_root,
                        budget_slice_usd=w1_slices[t],
                        proxy=proxy,
                        ledger=ledger,
                        args=args,
                    )
                    for t in wave1
                ),
                return_exceptions=True,
            )
            all_res.extend(_normalize_gather_results(wave1, w1_res, w1_slices))
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
                ),
                return_exceptions=True,
            )
            all_res.extend(_normalize_gather_results(wave2, w2_res, w2_allocs))
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
        print(
            f"Error: Missing sibling harness scripts in {harnesses_dir}: {missing}. "
            "This slice ships the orchestrator and ISSUE-158-CLOSURE.md. "
            "--selftest requires the four sibling scripts named in that note.",
            file=sys.stderr,
        )
        return 1

    # Run `--selftest` on all 4 real sibling scripts concurrently
    procs: Dict[str, subprocess.Popen[str]] = {}
    for track_id, fname in HARNESS_FILENAMES.items():
        procs[track_id] = subprocess.Popen(
            [sys.executable, str(harnesses_dir / fname), "--selftest"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=True,
        )
    sibling_status: Dict[str, bool] = {}
    for track_id, proc in procs.items():
        try:
            out, _ = proc.communicate(timeout=90)
        except subprocess.TimeoutExpired:
            _terminate_popen(proc)
            print(
                f"Error: Sibling {track_id} --selftest timed out after 90s and was terminated.",
                file=sys.stderr,
            )
            for other in procs.values():
                if other is not proc and other.poll() is None:
                    _terminate_popen(other)
            return 1
        if proc.returncode != 0:
            print(
                f"Error: Sibling {track_id} --selftest failed (rc={proc.returncode}):\n{out}",
                file=sys.stderr,
            )
            return 1
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
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {tiny_proxy.proxy_token}",
                    },
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
            CHILD_PROCESS_GROUPS.kill_all()
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
        help="Run all 4 child --selftest suites + live loopback proxy metering/cutoff + MASTER_SHA256SUMS check. "
        "Requires the four sibling harness scripts in --harnesses-dir (see ISSUE-158-CLOSURE.md).",
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
        "--confirm-live-spend",
        action="store_true",
        help="Required, together with OPENAI_API_KEY, to send billed upstream requests. "
        "Defaults run four concurrent tracks at $53.50.",
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
    if not args.confirm_live_spend:
        print(
            "Error: live spend requires --confirm-live-spend. "
            "Defaults run four concurrent tracks at $53.50. Use --selftest for the offline path.",
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
        CHILD_PROCESS_GROUPS.kill_all()
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