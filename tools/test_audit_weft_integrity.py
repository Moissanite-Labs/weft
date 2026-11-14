#!/usr/bin/env python3
"""Unit tests for `tools/audit_weft_integrity.py` (pipe-safe parser + 2-tier tamper probe)."""

from __future__ import annotations

import unittest

from tools.audit_weft_integrity import (
    canonical_json_sha256,
    probe_json_certificate_tamper_in_memory,
    split_markdown_table_row_pipe_safe,
)


def _strict_verifier(cert: dict) -> bool:
    """A witness-checking verifier: valid outer hash AND a consistent inner claim."""
    if canonical_json_sha256(cert) != cert.get("certificate_sha256"):
        return False
    return cert.get("claim_ok") is True


def _lazy_hash_only_verifier(cert: dict) -> bool:
    """A verifier that trusts the outer SHA-256 alone."""
    return cert.get("certificate_sha256") == canonical_json_sha256(cert)


def _sample_cert() -> dict:
    cert = {"claim_ok": True, "bound_q": "1/60", "witness": "short_rational_witness"}
    cert["certificate_sha256"] = canonical_json_sha256(cert)
    return cert


class TestPipeSafeSplit(unittest.TestCase):
    def test_preserves_norm_bars_and_escapes(self) -> None:
        row = "| P01 | VERIFIED | Error `|e_p| <= delta` and norm \\|x\\| <= 1 | Replay `python3 verify.py` |"
        cells = split_markdown_table_row_pipe_safe(row)
        self.assertEqual(len(cells), 4)
        self.assertEqual(cells[0], "P01")
        self.assertEqual(cells[1], "VERIFIED")
        self.assertIn("`|e_p| <= delta`", cells[2])
        self.assertIn("|x|", cells[2])
        self.assertEqual(cells[3], "Replay `python3 verify.py`")

    def test_plain_row_unchanged(self) -> None:
        self.assertEqual(
            split_markdown_table_row_pipe_safe("| a | b | c |"),
            ["a", "b", "c"],
        )

    def test_unbalanced_backtick_treated_as_code_span(self) -> None:
        cells = split_markdown_table_row_pipe_safe("| `x | y |")
        self.assertEqual(cells, ["`x | y |"])


    def test_double_backtick_span_stays_one_cell(self) -> None:
        # Review 5907258856 item 3: a run of backticks opens a span that only
        # a run of the same length closes.
        self.assertEqual(
            split_markdown_table_row_pipe_safe("| a | ``|x|`` | b |"),
            ["a", "``|x|``", "b"],
        )

    def test_double_backtick_span_holds_single_backtick(self) -> None:
        self.assertEqual(
            split_markdown_table_row_pipe_safe("| a | `` `|` `` | b |"),
            ["a", "`` `|` ``", "b"],
        )

    def test_backslash_kept_inside_code_span(self) -> None:
        self.assertEqual(
            split_markdown_table_row_pipe_safe("| a | `\\|` | b |"),
            ["a", "`\\|`", "b"],
        )

    def test_escape_outside_code_span_still_applies(self) -> None:
        self.assertEqual(
            split_markdown_table_row_pipe_safe("| a \\| b | c |"),
            ["a | b", "c"],
        )


def _seal(cert: dict) -> dict:
    cert = dict(cert)
    cert["certificate_sha256"] = canonical_json_sha256(cert)
    return cert


def _claim_only_verifier(cert: dict) -> bool:
    """Checks the hash and `claim_ok`, ignores the input flag `active`."""
    if canonical_json_sha256(cert) != cert.get("certificate_sha256"):
        return False
    return cert.get("claim_ok") is True


def _nested_claim_verifier(cert: dict) -> bool:
    """Checks the hash and a verdict nested under `witness`."""
    if canonical_json_sha256(cert) != cert.get("certificate_sha256"):
        return False
    witness = cert.get("witness")
    return isinstance(witness, dict) and witness.get("claim_ok") is True


class TestTwoTierTamperProbe(unittest.TestCase):
    def test_strict_verifier_passes_both_probes(self) -> None:
        res = probe_json_certificate_tamper_in_memory(_sample_cert(), _strict_verifier)
        self.assertTrue(res["ok"], res)

    def test_lazy_hash_only_verifier_caught_by_probe_2(self) -> None:
        res = probe_json_certificate_tamper_in_memory(_sample_cert(), _lazy_hash_only_verifier)
        self.assertFalse(res["ok"])
        self.assertEqual(res["reason"], "rehashed_semantic_tamper_accepted")

    def test_base_certificate_rejected(self) -> None:
        bad = _sample_cert()
        bad["claim_ok"] = False
        res = probe_json_certificate_tamper_in_memory(bad, _strict_verifier)
        self.assertEqual(res["reason"], "baseline_certificate_rejected")

    def test_input_flag_ahead_of_verdict_is_not_hash_only(self) -> None:
        # Review 5907258856 item 1: `active` sorts before `claim_ok`. A checker
        # that enforces `claim_ok` and ignores `active` is not hash-only.
        cert = _seal({"active": True, "claim_ok": True})
        res = probe_json_certificate_tamper_in_memory(cert, _claim_only_verifier)
        self.assertTrue(res["ok"], res)
        self.assertEqual(res["rejected_path"], ["claim_ok"])

    def test_nested_verdict_is_visited(self) -> None:
        cert = _seal({"version": 1, "witness": {"claim_ok": True}})
        res = probe_json_certificate_tamper_in_memory(cert, _nested_claim_verifier)
        self.assertTrue(res["ok"], res)
        self.assertEqual(res["rejected_path"], ["witness", "claim_ok"])

    def test_nested_hash_only_reports_every_mutated_path(self) -> None:
        cert = _seal({"version": 1, "witness": {"claim_ok": True}})
        res = probe_json_certificate_tamper_in_memory(cert, _lazy_hash_only_verifier)
        self.assertFalse(res["ok"])
        self.assertEqual(res["reason"], "rehashed_semantic_tamper_accepted")
        self.assertIn(["witness", "claim_ok"], res["mutated_paths"])
        self.assertIn(["version"], res["mutated_paths"])

    def test_float_only_bound_hash_only_is_caught(self) -> None:
        cert = _seal({"eps_bound": 0.25})
        res = probe_json_certificate_tamper_in_memory(cert, _lazy_hash_only_verifier)
        self.assertFalse(res["ok"])
        self.assertEqual(res["reason"], "rehashed_semantic_tamper_accepted")
        self.assertEqual(res["mutated_paths"], [["eps_bound"]])

    def test_named_verdict_paths_must_each_be_enforced(self) -> None:
        cert = _seal({"active": True, "claim_ok": True})
        res = probe_json_certificate_tamper_in_memory(
            cert, _claim_only_verifier, verdict_paths=[["claim_ok"], ["active"]]
        )
        self.assertFalse(res["ok"])
        self.assertEqual(res["reason"], "rehashed_semantic_tamper_accepted")
        self.assertEqual(res["mutated_path"], ["active"])

    def test_missing_digest_returns_reason(self) -> None:
        # Review 5907258856 item 2.
        res = probe_json_certificate_tamper_in_memory(
            {"claim_ok": True}, lambda c: c.get("claim_ok") is True
        )
        self.assertEqual(res, {"ok": False, "reason": "digest_missing"})

    def test_empty_digest_returns_reason(self) -> None:
        res = probe_json_certificate_tamper_in_memory(
            {"claim_ok": True, "certificate_sha256": ""}, lambda c: c.get("claim_ok") is True
        )
        self.assertEqual(res, {"ok": False, "reason": "digest_empty"})

    def test_non_string_digest_returns_reason(self) -> None:
        res = probe_json_certificate_tamper_in_memory(
            {"claim_ok": True, "certificate_sha256": 7}, lambda c: c.get("claim_ok") is True
        )
        self.assertEqual(res, {"ok": False, "reason": "digest_not_a_string"})


if __name__ == "__main__":
    unittest.main()
