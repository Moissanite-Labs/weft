#!/usr/bin/env python3
"""Unit tests for Codebase C6 (`weft/runtime/telemetry`) covering Issues #13, #15, #16, #31, #78."""

import tempfile
import unittest
from pathlib import Path

from weft.runtime.telemetry import (
    FIXTURE_CAPTURED_AT_UNIX_S,
    FRAME64_SLOT_SPECS,
    MAX_RELATIVE_CLOCK_SECONDS,
    decode_frame_64b_bytes,
    encode_frame_64b_bytes,
    encode_sym2p,
    float32_ulp_spacing,
    harvest_moissanite_telemetry,
    pack_uniform_frame_64b,
    parse_sym2p,
    read_host_hardware_metrics,
)


class TestWeftTelemetry(unittest.TestCase):
    def test_host_metrics_unavailable_never_invents_hardware(self) -> None:
        """Issue #16: when sysctl/procfs is unavailable, return source='unavailable' and None fields."""
        res = read_host_hardware_metrics(force_unavailable=True)
        self.assertEqual(res["source"], "unavailable")
        self.assertIsNone(res["ncpu"])
        self.assertIsNone(res["mem_gb"])
        self.assertIsNone(res["load_1m"])
        self.assertIsNone(res["estimated_load_thermal_c"])
        self.assertTrue(res["thermal_is_estimate"])

    def test_host_metrics_linux_procfs_parser(self) -> None:
        """Issue #16: Linux /proc/meminfo path parses real MemTotal without darwin sysctl."""
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix="_meminfo") as tmp:
            tmp.write("MemTotal:       32768000 kB\nMemFree:        16384000 kB\n")
            tmp.flush()
            res = read_host_hardware_metrics(
                platform_override="linux",
                proc_meminfo_path=tmp.name,
            )
            self.assertEqual(res["source"], "linux-procfs")
            self.assertEqual(res["mem_gb"], round(32768000 / (1024**2), 2))
            self.assertGreater(res["ncpu"], 0)
            self.assertTrue(res["thermal_is_estimate"])

    def test_harvester_omits_suspended_accounts_and_separates_wall_clock(self) -> None:
        """Issues #15 & #78: omit suspended_accounts, keep slot 2 relative, and store integer wall time outside frame."""
        with tempfile.TemporaryDirectory() as tmp:
            payload = harvest_moissanite_telemetry(tmp, live=False)
            self.assertEqual(payload["source"], "fixture")
            self.assertNotIn("suspended_accounts", payload)
            self.assertEqual(payload["captured_at_unix_s"], FIXTURE_CAPTURED_AT_UNIX_S)
            self.assertIsInstance(payload["captured_at_unix_s"], int)
            self.assertEqual(payload["uniform_frame_64b_floats"][2], 0.0)
            json_text = (Path(tmp) / "moissanite_telemetry.json").read_text(encoding="utf-8")
            self.assertNotIn("suspended_accounts", json_text)
            raw_bin = (Path(tmp) / "moissanite_telemetry.bin").read_bytes()
            self.assertEqual(len(raw_bin), 64)
            decoded = decode_frame_64b_bytes(raw_bin)
            self.assertEqual(decoded[2], 0.0)

    def test_frame64_slot_map_and_relative_clock_resolution(self) -> None:
        """Issue #78: assert documented meaning/offset/resolution of all 16 slots and reject Unix wall time in slot 2."""
        self.assertEqual(len(FRAME64_SLOT_SPECS), 16)
        for idx, spec in enumerate(FRAME64_SLOT_SPECS):
            self.assertEqual(spec["slot"], idx)
            self.assertEqual(spec["offset"], idx * 4)

        # Demonstrate why Unix timestamps cannot live in slot 2: binary32 ULP at 1,762,560,000 is 128.0 s.
        self.assertEqual(float32_ulp_spacing(1762560000.0), 128.0)
        # Across a 24-hour relative session (86,400 s), binary32 spacing is <= 7.8125 ms; at 2^23 s max, <= 1.0 s.
        self.assertLessEqual(float32_ulp_spacing(86400.0), 0.0078125)
        self.assertLessEqual(float32_ulp_spacing(MAX_RELATIVE_CLOCK_SECONDS - 1.0), 0.5)

        for bad_time in (1762560000.0, MAX_RELATIVE_CLOCK_SECONDS + 1.0, -0.001, float("nan"), float("inf")):
            with self.subTest(bad_time=bad_time):
                with self.assertRaises(ValueError):
                    pack_uniform_frame_64b(
                        active_nodes=19.0,
                        org_tension=0.2,
                        system_time=bad_time,
                        gini_index=0.2,
                        barycentric={"rounding": 0.18, "density": 0.55, "hue": 0.22, "contrast": 0.12},
                        velocities=[0.1] * 8,
                    )

        # Direct raw float array encoding must also enforce slot 2 relative-clock bounds
        with self.assertRaises(ValueError):
            encode_frame_64b_bytes([19.0, 0.2, 1762560000.0] + [0.0] * 13)

    def test_frame64_roundtrip_and_sym2p_roundtrip(self) -> None:
        """Interfaces I1 and I2: 64-byte frame and SYM-2P packet round-trip cleanly."""
        floats = pack_uniform_frame_64b(
            active_nodes=19.0,
            org_tension=0.2662,
            system_time=100.25,
            gini_index=0.2655,
            barycentric={"rounding": 0.18, "density": 0.55, "hue": 0.22, "contrast": 0.12},
            velocities=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
        )
        raw = encode_frame_64b_bytes(floats)
        self.assertEqual(len(raw), 64)
        decoded = decode_frame_64b_bytes(raw)
        self.assertEqual(len(decoded), 16)
        self.assertAlmostEqual(decoded[0], 19.0, places=4)
        self.assertAlmostEqual(decoded[2], 100.25, places=4)

        line = encode_sym2p(role=0x02, action_state=0x10, sequence=412, metrics={"active_nodes": 19, "tension": -0.25})
        pkt = parse_sym2p(line)
        self.assertTrue(pkt["hash_valid"])
        self.assertEqual(pkt["sequence"], 412)
        self.assertEqual(pkt["role"], 0x02)
        self.assertEqual(pkt["action_state"], 0x10)
        self.assertAlmostEqual(pkt["metrics"]["tension"], -0.25, places=4)


if __name__ == "__main__":
    unittest.main()
