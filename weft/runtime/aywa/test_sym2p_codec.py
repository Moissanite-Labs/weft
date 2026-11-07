#!/usr/bin/env python3
"""Round-trip tests for the SYM-2P codec (issue #13).

Run: python3 -m unittest discover -s weft/runtime/aywa -p 'test_*.py'
"""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sym2p_codec import encode_sym2p_line, parse_sym2p_line  # noqa: E402

# Shared with test_sym2p_parse.mjs so both languages are held to the same bytes.
GOLDEN_LINE = (
    ":0a:ff:0042[s-exp (state 0.92) (tension -0.14) (drift 1e-05)]"
    "234aa42e75091af1892873ef83caebb0720ed6dbdee6bdc1538fd1c6efdb5757"
)


class Sym2pRoundTrip(unittest.TestCase):
    def test_sequence_is_decimal_packet_number(self):
        # craft.md:145 -- ":0042" is "Packet Number 42", not 0x42 (= 66).
        line = encode_sym2p_line(sequence=42, metrics={"tension": 0.14})
        self.assertIn(":0042[", line)
        self.assertEqual(parse_sym2p_line(line)["sequence"], 42)

    def test_role_and_action_are_hex_bytes(self):
        # craft.md:143-144 -- role and action/state are bytes written like 0x01.
        line = encode_sym2p_line(role=10, action_state=255, sequence=7, metrics={"x": 1})
        self.assertTrue(line.startswith(":0a:ff:0007["), line)
        parsed = parse_sym2p_line(line)
        self.assertEqual((parsed["role"], parsed["action_state"]), (10, 255))

    def test_round_trip_over_field_ranges(self):
        for role in (0, 1, 9, 10, 15, 16, 255):
            for action in (0, 3, 10, 255):
                for seq in (0, 1, 9, 10, 42, 99, 100, 1234, 9999):
                    parsed = parse_sym2p_line(
                        encode_sym2p_line(role=role, action_state=action, sequence=seq, metrics={"m": 1})
                    )
                    self.assertEqual(
                        (parsed["role"], parsed["action_state"], parsed["sequence"]), (role, action, seq)
                    )
                    self.assertTrue(parsed["hash_valid"])

    def test_out_of_range_fields_are_rejected(self):
        for kwargs in ({"role": 256}, {"role": -1}, {"action_state": 256}, {"sequence": 10000}, {"sequence": -1}):
            with self.subTest(**kwargs), self.assertRaises(ValueError):
                encode_sym2p_line(metrics={"m": 1}, **kwargs)

    def test_current_default_bytes_unchanged(self):
        # Defaults role=1, action=3, sequence=1 must still produce ":01:03:0001"
        # so the published docs/data/telemetry.jsonl format does not move.
        self.assertTrue(encode_sym2p_line(metrics={"m": 1}).startswith(":01:03:0001["))

    def test_signed_and_exponent_metrics_survive(self):
        metrics = {"state": 0.92, "tension": -0.14, "drift": 1e-05}
        parsed = parse_sym2p_line(encode_sym2p_line(metrics=metrics))
        self.assertEqual(parsed["metrics"], metrics)

    def test_missing_hash_is_not_valid(self):
        parsed = parse_sym2p_line(":01:03:0001[s-exp (tension 0.14)]")
        self.assertFalse(parsed["hash_present"])
        self.assertFalse(parsed["hash_valid"])

    def test_tampered_payload_fails_hash(self):
        line = encode_sym2p_line(metrics={"tension": 0.14})
        self.assertFalse(parse_sym2p_line(line.replace("0.14", "0.15"))["hash_valid"])

    def test_golden_line(self):
        self.assertEqual(
            encode_sym2p_line(
                role=10, action_state=255, sequence=42, metrics={"state": 0.92, "tension": -0.14, "drift": 1e-05}
            ),
            GOLDEN_LINE,
        )
        parsed = parse_sym2p_line(GOLDEN_LINE)
        self.assertEqual((parsed["role"], parsed["action_state"], parsed["sequence"]), (10, 255, 42))
        self.assertTrue(parsed["hash_valid"])

    def test_published_seed_line_parses(self):
        here = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(here, "..", "..", "..", "docs", "data", "telemetry.jsonl")
        with open(path, encoding="utf-8") as f:
            line = next(l for l in f if l.startswith(":"))
        parsed = parse_sym2p_line(line)
        self.assertTrue(parsed["hash_valid"])
        self.assertEqual((parsed["role"], parsed["action_state"], parsed["sequence"]), (1, 3, 1))


if __name__ == "__main__":
    unittest.main()
