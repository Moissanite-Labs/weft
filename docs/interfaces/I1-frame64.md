# I1: 64-byte uniform telemetry frame

Status: implemented-layout contract and conformance profile, document version 1.
Tracks issue #78. Producer: C6 (`weft/runtime/telemetry/frame64.py`,
`harvester.py`, `weft_daemon.py`). Consumers: C7 (`weft/runtime/aywa/web/assets/shaders/dashboard_layout.wgsl`,
`weft/runtime/aywa/web/assets/js/weft-loom.js`,
`weft/runtime/aywa/web/assets/workers/telemetry-worker.js`) and local daemon bridges.

## Scope and byte layout

Interface I1 is a contiguous 64-byte buffer of sixteen IEEE-754 binary32 values
in little-endian byte order (`struct.Struct("<16f")`). Every slot must be finite
(`NaN` and `±Inf` are rejected by `encode_frame_64b_bytes`).

| Slot | Byte offset | Field (`dashboard_layout.wgsl`) | Unit / domain | Max binary32 ULP in domain |
|---:|---:|---|---|---:|
| `0` | `0` | `active_nodes` | Node count in `[0, 65536]` | `0.0078125` |
| `1` | `4` | `org_tension` | Tension scalar in `[0.0, 1.0]`; the served shader clamps to `[0.0, 1.0]` | `1.19e-07` |
| `2` | `8` | `system_time` | **Relative elapsed seconds** in `[0.0, 8388608.0]` (`2^23` s ≈ `97.09` d) | `1.0` s (`<= 7.8125` ms under 24 h) |
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
- `weft-loom.js` writes `(performance.now() - t0) / 1000` into slot 2 on every
  frame, or the constant `12.0` under reduced motion.
- `telemetry-worker.js` writes `performance.now() / 1000` (tab-relative elapsed
  seconds) on each poll. These JS writers do not enforce `[0, 2^23]`.
- `weft_daemon.py` is a one-shot harvest: slot 2 is the harvest interval
  (about `0.0006` s on a self-test). Callers may pass `elapsed_seconds`
  explicitly; values outside `[0.0, 8,388,608.0]` raise `ValueError`.
- `pack_uniform_frame_64b` and `encode_frame_64b_bytes` reject negative values,
  values that are not finite in binary32, and values above `8,388,608.0` s
  (`ValueError`).

## Conformance

Run from the repository root:

```sh
python3 -m unittest discover -s weft/runtime/telemetry -p 'test_*.py'
```
