# Weft Host & Organization Telemetry (`weft/runtime/telemetry`)

Codebase **C6** in [`docs/program/decomposition.md`](../../../docs/program/decomposition.md), implementing Interfaces **I1** (64-Byte Telemetry Frame) and **I2** (`SYM-2P/1.0` Wire Packet).

## Purpose and boundary

Collect host hardware metrics and organization repository telemetry, encode them into `SYM-2P/1.0` packets with SHA-256 integrity tags, and pack the 64-byte IEEE-754 uniform buffer (`16 x float32`) consumed by the Aywa browser organism (`C7`).

- **Owns**:
  - `host_metrics.py`: Darwin `sysctl` and Linux `/proc/meminfo` host hardware readers with honest `"source": "unavailable"` reporting when probes are absent (#16).
  - `harvester.py`: Moissanite-Labs repository telemetry harvester with `"source": "fixture"` default and `--live` GitHub REST API mode, omitting all personal/suspended account identifiers (#15).
  - `sym2p_codec.py`: `SYM-2P/1.0` encoder and verifier (#13).
  - `frame64.py`: 64-byte IEEE-754 uniform frame packer (`<16f`) and Gini coefficient calculator.
  - `vectors.json` and `test_telemetry.py`: unit and conformance tests.
- **Dependencies**: Python 3 standard library (`json`, `struct`, `hashlib`, `urllib.request`, `subprocess`).

## Verification

```bash
python3 -m unittest discover -s weft/runtime/telemetry -p 'test_*.py'
```
