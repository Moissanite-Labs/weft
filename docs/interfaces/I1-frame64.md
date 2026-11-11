# I1: 64-byte uniform telemetry frame

Status: implemented-layout contract and conformance profile, document version 1.
Tracks issue #78. Producer: C6 (`weft/runtime/telemetry/frame64.py`,
`harvester.py`, `weft_daemon.py`). Consumers: C7 (`weft/runtime/aywa/dashboard_layout.wgsl`,
`weft/runtime/aywa/web/assets/workers/telemetry-worker.js`) and local daemon bridges.

## Scope and byte layout

Interface I1 is a contiguous 64-byte buffer of sixteen IEEE-754 binary32 values
in little-endian byte order (`struct.Struct("<16f")`). Every slot must be finite
(`NaN` and `±Inf` are rejected by `encode_frame_64b_bytes`).

| Slot | Byte offset | Field (`dashboard_layout.wgsl`) | Unit / domain | Max binary32 ULP in domain |
|---:|---:|---|---|---:|
| `0` | `0` | `active_nodes` | Node count in `[0, 65536]` | `0.0078125` |
| `1` | `4` | `org_tension` | Tension scalar in `[0.0, 85.0]` | `7.63e-06` |
| `2` | `8` | `system_time` | **Relative elapsed seconds** in `[0.0, 8388608.0]` (`2^23` s ≈ `97.09` d) | `0.5` s (`<= 7.8125` ms under 24 h) |
| `3` | `12` | `gini_index` | Gini ratio in `[0.0, 1.0]` | `1.19e-07` |
| `4` | `16` | `user_rounding` | Eido barycentric rounding in `[0.0, 1.0]` | `1.19e-07` |
| `5` | `20` | `user_density` | Eido barycentric density in `[0.0, 1.0]` | `1.19e-07` |
| `6` | `24` | `user_hue` | Eido barycentric hue in `[0.0, 1.0]` | `1.19e-07` |
| `7` | `28` | `user_contrast` | Eido barycentric contrast in `[0.0, 1.0]` | `1.19e-07` |
| `8..11` | `32..44` | `node_vel_0.{x,y,z,w}` | Normalized velocity in `[0.0, 1024.0]` | `0.000122` |
| `12..15` | `48..60` | `node_vel_1.{x,y,z,w}` | Normalized velocity in `[0.0, 1024.0]` | `0.000122` |

## Why slot 2 is a relative clock, never Unix wall-clock time (#78)

IEEE-754 binary32 has 24 significand bits. At `1,762,560,000` s (2025–2026 Unix
seconds, in `[2^30, 2^31)`), adjacent binary32 values are `2^(30 - 23) = 128`
seconds apart (Paper 2 §6.7, experiment E7). Storing Unix time in slot 2 loses
all sub-two-minute timing and rounds timestamps by tens of seconds.

Slot 2 is therefore strictly a **relative clock** measured in seconds from an
epoch chosen by the producer or animation loop:

- Static snapshot / fixture files (`harvester.py`) write `0.0` into slot 2 and
  carry integer UTC wall-clock time **outside** the 64-byte frame as
  `captured_at_unix_s` in `moissanite_telemetry.json`.
- Browser consumers (`telemetry-worker.js`) write `performance.now() / 1000`
  (tab-relative elapsed seconds).
- Long-running host daemons (`weft_daemon.py`) write monotonic process uptime
  modulo `MAX_RELATIVE_CLOCK_SECONDS` (`8,388,608.0` s).
- `pack_uniform_frame_64b` and `encode_frame_64b_bytes` reject negative values,
  non-finite values, and values above `8,388,608.0` s (`ValueError`).

## Conformance

Run from the repository root:

```sh
python3 -m unittest discover -s weft/runtime/telemetry -p 'test_*.py'
```
