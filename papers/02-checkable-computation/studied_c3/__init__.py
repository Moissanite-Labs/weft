"""The C3 reducer and BCP codec exactly as Paper 2 studied them.

These two files are byte-for-byte copies of `weft/runtime/ic/ic_vm.py` and
`weft/runtime/ic/bcp_codec.py` at commit a18fc40, the commit named in the
paper's front matter. The runtime has since moved to port-indexed wires and
BCP version 2 (see weft/runtime/ic/README.md), which fixes the defects the
paper reports. The experiments import this frozen copy so that every number in
results.json still reproduces. Do not edit these files.
"""
