# Tools

Curated public tooling notes for LoL3.

Current public state:

- no standalone public helper has been promoted yet
- the repo is still documentation-first
- the current visible outputs of the tooling lane are summarized in:
  - [`../docs/tooling-catalog.md`](../docs/tooling-catalog.md)
  - [`../examples/README.md`](../examples/README.md)

This folder is reserved for:

- public extraction helpers
- analysis helpers that are clean enough to publish
- short workflow wrappers

Expected first candidates for promotion:

- small witness-window comparison helpers
- diagram-generation helpers for the public checkpoint visuals
- safe extraction wrappers that do not require shipping retail assets

Why it is still empty:

- the private LoL3 workflow still contains too many one-off passes and scratch drivers
- the public repo should prefer a smaller, cleaner tool surface over a noisy dump

## Promoted helpers

### `extract_wsx_entries.py`

Peels retail `.WSX` containers into entry blobs and LMF candidates.

- Format notes: [`../docs/wsx-extraction.md`](../docs/wsx-extraction.md)
- Container map: [`../docs/container-inventory.md`](../docs/container-inventory.md)

```bash
python3 tools/extract_wsx_entries.py \
  --game-dat /path/to/retail/DAT \
  --out /path/to/out \
  --manifest /path/to/manifest.json
```

Verified against private staged peels for `QWOD0` / `SWOD4` / `RVOL0` / `CKEEP` (16/16 SHA1).
Does not bundle retail assets.

