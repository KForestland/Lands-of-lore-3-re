# Tooling Catalog

Current LoL3 public checkpoint was built mainly with:

- local extraction / byte-inspection scripts
- local comparison passes over `layer6` windows
- Wine runtime tracing with the viable launch form:
  - `wine LOL3.EXE -CD. -16MB -NO_ASSERTS`

Main practical workflow:

1. confirm runtime provenance
2. split witnesses structurally
3. replicate and falsify
4. promote only the durable structural and semantic checkpoint

This repo intentionally does not ship the full private working toolkit or scratch outputs.
