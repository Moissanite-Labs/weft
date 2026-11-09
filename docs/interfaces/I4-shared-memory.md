# I4: current Plasm shared-memory layout

Status: implemented-layout contract and conformance profile, document version 1.
Tracks issue #40. Producer: C1 (`weft/runtime/plasm/`). Prospective consumers:
cells, the daemon, and C3 adapters. This document does not claim those integrations
already exist. I5, not I4, names the IC graph serialization interface.

## Scope and platform

The profile `i4-native-le64-current` describes the layout implemented by
`StratifiedMemoryArena` and the NumPy views in `plasm.py`. It fixes a contradiction
between that implementation and the shapes previously presented as current in
the architecture summaries. Runtime code and behavior are unchanged.

The implementation uses native `ctypes.Structure` layout and native NumPy
`float32`, not an explicitly packed portable wire format. This profile requires
little-endian byte order, 8-byte `uint64` and IEEE-754 binary64, 4-byte IEEE-754
binary32, and 8-byte structure alignment with the offsets below. The tests check
these assumptions on the host running them. They do not establish compatibility
on an untested ABI, big-endian host, GPU, or accelerator. A CPU run does not
establish an Apple Silicon/MPS result.

`document_version: 1` versions this specification and its JSON fixture only.
There is **no runtime version or magic field**. The `weft_stratified_plasm_v1`
name prefix is not an in-memory compatibility check. A consumer must agree on
the profile out of band before attaching; size alone cannot identify a layout.

Segment names are at most 30 bytes with no `/`. macOS caps POSIX shared-memory
names at 31 bytes including the leading `/` that Python adds; Linux allows 255.
`StratifiedAppleSiliconPlasm` refuses a longer name on every platform, so a name
that passes on Linux CI also works on Apple Silicon (#68). The cycle's
per-process default is `weft_plasm_<pid>`.

## Byte layout

Offsets are decimal bytes from the beginning of the shared-memory mapping.
Array elements are contiguous and in C order (last index varies fastest).

| Field | Offset | Bytes | Native representation / mapped shape |
|---|---:|---:|---|
| `generation_epoch` | 0 | 8 | `uint64` scalar |
| `metabolic_tension` | 8 | 8 | `double` scalar |
| `focal_workspace` | 16 | 262,144 | `float32[256,256]` (`focal_matrix`) |
| `sympathetic_ring` | 262,160 | 4,096 | `float32[1024]` (`symp_matrix`) |
| `hippocampal_lattice` | 266,256 | 262,144 | `float32[64,1024]` (`hippo_matrix`) |
| `cryptographic_lock` | 528,400 | 12,288 | `uint8[12288]` |
| **Total** | | **540,688** | No gaps or trailing padding in this profile |

The epoch and tension are separate header fields. The 1,024 sympathetic floats
do not currently implement the four-scalar semantic map described in earlier
summaries. The field named `cryptographic_lock` is reserved storage: its name
does not imply mutual exclusion, cryptographic enforcement, or atomic commits.

## Access and lifetime

The ctypes and NumPy CPU views map the same shared-memory bytes without copying.
`read_tensors_to_device()` explicitly copies those views into independent CPU
or MPS tensors; it is not a zero-copy device binding. `write_focal_from_tensor()`
copies a tensor back into the focal region, then updates epoch and tension.

No synchronization, atomic snapshot, multi-writer protocol, bounds-enforcing
sandbox, or version negotiation is implemented by this layout. Consumers must
coordinate access externally; the conformance test uses sequential writes.

`release_views()` drops the owner's ctypes/NumPy views. Callers must release any
additional exported views before closing their mapping. `close(unlink=False)`
closes the owner's mapping without removing its name; the default `close()` and
context-manager exit also unlink it. Detached tensors can survive the mapping.
Other attachers must close their own mappings. Creating an arena with an existing
name currently unlinks that name first; callers must not use creation as a safe
join or assume it arbitrates ownership.

## Lineage and alternative layouts

The prior [architecture summary at `94b9064`](https://github.com/Moissanite-Labs/weft/blob/94b9064f9d09509a46c9e9d9ba219707f9551bb9/weft/WEFT-ARCHITECTURE-LOCK.md)
described focal `[4,64,512]`, sympathetic `[4]`, and hippocampal `[8,512]`, totaling
540,688 bytes with no header or lock region. That is a distinct source variant,
not the layout implemented here. The identical total does not make the two byte
layouts interchangeable. Earlier corpus diagrams also describe a `3x64x512`
focal nerve ([`weft/almalga.md`](https://github.com/Moissanite-Labs/weft-corpus/blob/main/weft/almalga.md),
[`weft/dissertation-mac.md`](https://github.com/Moissanite-Labs/weft-corpus/blob/main/weft/dissertation-mac.md)).

These alternatives remain part of the design lineage; this contract does not
erase them, label them invalid, or select one for every future technology stack.
An iteration can retain or reintroduce a variant for a different role when its
purpose, constraints, tradeoffs, and evidence justify it. Adopting a different
layout requires an explicit producer/consumer decision, new conformance data,
and a compatibility/migration design. It must not silently reinterpret an arena
by reusing its name or byte count. Original corpus sources are unchanged.

## Conformance

[`i4-vectors.json`](../../weft/runtime/plasm/i4-vectors.json) contains independently
specified offsets, widths, shapes and little-endian golden bytes. It includes
both header fields; first, row-boundary and last matrix elements; the first and
last sympathetic values; and the first and last reserved lock bytes. Expected
data is static, not generated from `plasm.py` during tests.

`test_plasm.py` checks native ctypes offsets and sizes, mapped NumPy shape and
C-order strides, region coverage, both directions of exchange with an independent
`struct` consumer using a separately attached mapping, and mapping cleanup with
detached tensor survival. These are local layout/interchange tests, not concurrent
process or hardware performance evidence.

Run from the repository root with NumPy and PyTorch installed:

```sh
python3 -m unittest discover -s weft/runtime/plasm -p 'test_*.py'
```
