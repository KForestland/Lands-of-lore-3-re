# Tooling Catalog

Current LoL3 public checkpoint was built mainly with:

- local extraction / byte-inspection scripts
- local comparison passes over `layer6` windows
- Wine runtime tracing with the viable launch form:
  - `wine LOL3.EXE -CD. -16MB -NO_ASSERTS`

Tooling classes used in practice:

- extraction helpers
  - locate and peel `LMF` / `WSX` records into comparable opaque blobs
- local structural passes
  - band counts
  - transition matrices
  - regime and branch classification
- local semantic passes
  - witness-specific neighborhood, handoff, and replication checks
- runtime provenance helpers
  - confirm which witness families stay quiet baselines versus higher-activity sidecars
- promotion helpers
  - turn private checkpoint results into stricter public docs and diagrams

Main practical workflow:

1. confirm runtime provenance
2. split witnesses structurally
3. replicate and falsify
4. promote only the durable structural and semantic checkpoint

Public repo note:

- this repo currently documents the workflow more than it ships the private working toolkit
- `tools/` is intentionally conservative until helpers are cleaned for public release
- diagrams in `examples/` are the current public-facing output of that tooling lane

Intentionally not shipped here:

- full private scratch scripts
- raw large trace dumps
- temporary one-off analysis drivers
- uncensored retail asset material
