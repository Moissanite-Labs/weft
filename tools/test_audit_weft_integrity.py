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


if __name__ == "__main__":
    unittest.main()
