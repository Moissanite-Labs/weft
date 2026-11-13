# Vendored E08 modules

`plasm_np.py` and `zerolex_e08.py` are byte-for-byte copies of
`docs/program/experiments/zero-lexicon-cells-2026-11-12/` at PR #141 head
`c62d2653ad4989794b0947f4f627a0fbb6b77d57`, copied so `microcell.py` runs on a
tree that contains only this record. Do not edit them here. `microcell.py`
checks both hashes at import and exits with a message if either differs.

| File | sha256 |
|---|---|
| `zerolex_e08.py` | `3e18e18e2c26ab2efea284ef8ba32b3ba83a80918054374b10a825b16432a12b` (the `decoder_sha256` in every committed stdout header) |
| `plasm_np.py` | `2343f4c876b4cc2129c01213161dd283a2f7ca7d7ca4e13c000bb5de82bcd170` |

Their docstrings refer to paths in the E08 record (for example `plasm_import/`);
those paths are not part of this directory. `microcell.py` uses only `phi`,
`Field`, `ring_read`, `ring_write`, the environment constants, `watermark_embed`
and `watermark_verify`.
