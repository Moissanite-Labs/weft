#!/usr/bin/env python3
"""Unit tests for Codebase C6 (`weft/runtime/telemetry`) covering Issues #13, #15, #16, #31."""

import tempfile
import unittest
from pathlib import Path

from weft.runtime.telemetry import (
    decode_frame_64b_bytes,
    encode_frame_64b_bytes,
    encode_sym2p,
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

    def test_harvester_omits_suspended_accounts_and_marks_source(self) -> None:
        """Issue #15: harvester must omit suspended_accounts and mark offline data source='fixture'."""
        with tempfile.TemporaryDirectory() as tmp:
            payload = harvest_moissanite_telemetry(tmp, live=False)
            self.assertEqual(payload["source"], "fixture")
            self.assertNotIn("suspended_accounts", payload)
            json_text = (Path(tmp) / "moissanite_telemetry.json").read_text(encoding="utf-8")
            self.assertNotIn("suspended_accounts", json_text)
            self.assertEqual((Path(tmp) / "moissanite_telemetry.bin").stat().st_size, 64)

    def test_frame64_roundtrip_and_sym2p_roundtrip(self) -> None:
        """Interfaces I1 and I2: 64-byte frame and SYM-2P packet round-trip cleanly."""
        floats = pack_uniform_frame_64b(
            active_nodes=19.0,
            org_tension=0.2662,
            system_time=100.0,
            gini_index=0.2655,
            barycentric={"rounding": 0.18, "density": 0.55, "hue": 0.22, "contrast": 0.12},
            velocities=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
        )
        raw = encode_frame_64b_bytes(floats)
        self.assertEqual(len(raw), 64)
        decoded = decode_frame_64b_bytes(raw)
        self.assertEqual(len(decoded), 16)
        self.assertAlmostEqual(decoded[0], 19.0, places=4)

        line = encode_sym2p(role=0x02, action_state=0x10, sequence=412, metrics={"active_nodes": 19, "tension": -0.25})
        pkt = parse_sym2p(line)
        self.assertTrue(pkt["hash_valid"])
        self.assertEqual(pkt["sequence"], 412)
        self.assertEqual(pkt["role"], 0x02)
        self.assertEqual(pkt["action_state"], 0x10)
        self.assertAlmostEqual(pkt["metrics"]["tension"], -0.25, places=4)


if __name__ == "__main__":
    unittest.main()
