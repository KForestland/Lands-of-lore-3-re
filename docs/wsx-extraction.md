# LoL3 WSX extraction (reproducible)

Updated 2026-09-17.

## Status
**Closed for the four witness WSX families.** A smoke peel from retail
`DAT/*.WSX` reproduces all 16 unique staged blobs under
`private staged peels` by SHA1 (aliases like `LEVELS_*` / `SWOD4.TEX`
are duplicate names for the same bytes).

## Tool
``tools/extract_wsx_entries.py``

```bash
python3 `tools/extract_wsx_entries.py` \
  --game-dat <retail-DAT> \
  --out <out-dir> \
  --manifest <manifest.json>
```

## Format
- Prefix: 6 bytes
- 4 records × 12 bytes: `u32 hash`, `u32 unk`, `u32 size` (LE)
- Payload base: offset 54
- Payloads packed **largest size first**; sum(sizes) == file_size − 54
- LMF heuristic: `u32` at offset 4 equals 38 (same as `lol3_re_toolkit.parse_lmf`)

## Naming note
Staged `CKEEP.LMF` is the large opaque art blob (hash `73EA231D`), not the
smaller true LMF (`LEVELS_CKEEP_CKEEP.LMF`, 663806 bytes). The new extractor
writes the true LMF as `CKEEP.LMF` and keeps the art blob as
`CKEEP.WSX_entry3_h73EA231D.bin`. Prefer SHA1 over filename when comparing
to the old staging dir.

## Still open
- Peel all other `DAT/*.WSX` (levels, music, movies, slice CDs) into a full inventory
- Map stems → Gladstone / portal worlds for a Classic coverage board
- Geometry/material decode above LMF (Godot import) — next RE lane
- Promote cleaned extractor to `Lands-of-lore-3-re/tools/` (no retail paths)


## Scope limit
This peeler currently targets the **4-record packed** WSX layout used by the
witness families (`QWOD0`, `SWOD4`, `RVOL0`, `CKEEP`). Other `DAT/*.WSX` files
(e.g. many `*S` sidecars and larger level packs) use different framing and will
error with a size-mismatch until a second parser family is added.
