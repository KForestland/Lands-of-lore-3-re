# Tooling Catalog

> **History.** Kept as a record of an earlier pass. Current pages: [STATUS.md](STATUS.md) and [formats/](formats/wsx.md); where they differ, the current pages are right.

Current LoL3 public checkpoint was built mainly with:

- local extraction / byte-inspection scripts
- local comparison passes over `layer6` windows
- Wine runtime tracing with the viable launch form:
  - `wine LOL3.EXE -CD. -16MB -NO_ASSERTS`

Tooling classes used in practice:

- extraction helpers
  - locate and peel `LMF` / `WSX` records into comparable opaque blobs
  - public peeler: [`../tools/extract_wsx_entries.py`](../tools/extract_wsx_entries.py) — general `u16`-count WSX family (51/52 DAT files; see [`wsx-extraction.md`](wsx-extraction.md))
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

- this page describes the earlier workflow; the current tools are listed in tools/README.md
- `tools/` is intentionally conservative until helpers are cleaned for public release
- diagrams in `examples/` are the current public-facing output of that tooling

Intentionally not shipped here:

- full private scratch scripts
- raw large trace dumps
- temporary one-off analysis drivers
- uncensored retail asset material

- level catalog notes: [`level-catalog-notes.md`](level-catalog-notes.md)
