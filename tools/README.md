# Tools

## Common options

The tools follow one set of rules:
- `--help` changes nothing.
- The game's `DAT` folder comes from `--data` or `$LOL3_DAT`; there is no built-in path.
- Nothing is written unless you pass `--out` (or `-o`).
- `--check` prints one `CHECK` line and exits 0 when it passes.

Run examples outside the repository.

| Tool | Reads | `--check` |
|---|---|---|
| `check_all.py` | all checks below | prints each line, then `ALL 3 CHECKS PASSED` |
| `repo_guard.py` | the repository | no game files, media, stray images, machine paths, private or assistant names, or foreign commit identities |
| `extract_wsx_entries.py` | `DAT/*.WSX` | parses every WSX and writes nothing (51/52; `cdcache.wsx` is open question Q1) |
| `walk_lmf_leaves.py` | the LMF entries inside the WSX files | walks all 18 and checks every block size against the ladder |

Curated public tooling notes for LoL3.

Current public state:

- no standalone public helper has been promoted yet
- the repo is still documentation-first
- the current visible outputs of the tooling are summarized in:
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

