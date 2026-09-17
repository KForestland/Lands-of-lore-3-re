# LoL3 WSX extraction (reproducible)

Updated 2026-09-17.

## Status
**General WSX peeler covers 51/52 retail `DAT/*.WSX` files.** Only `cdcache.wsx`
fails the size check and needs a separate pass.

Privately verified:
- Witness packed peels for `QWOD0` / `SWOD4` / `RVOL0` / `CKEEP` matched staged SHA1s
- Full DAT peel produced thousands of entry blobs + 18 LMF candidates

## Tool
[`../tools/extract_wsx_entries.py`](../tools/extract_wsx_entries.py)

```bash
python3 tools/extract_wsx_entries.py \
  --game-dat /path/to/retail/DAT \
  --out /path/to/out \
  --manifest /path/to/manifest.json
```

Optional: `--max-blob-write BYTES` to catalog oversized entries without writing them.

## Format
- `u16` entry count at offset 0 (little-endian)
- 6-byte prefix total
- `count × 12` byte records: `u32 hash`, `u32 unk`, `u32 size` (LE)
- Payload base: `6 + count*12`
- Payloads packed **largest size first**; `sum(sizes) == file_size − payload_base`
- LMF heuristic: `u32` at offset 4 equals 38

## Naming
Outputs go under `--out/<STEM>/`. First LMF-heuristic blob is `<STEM>.LMF`;
other entries are `<STEM>.WSX_entryN_hHASH.bin`.

## Still open
- `cdcache.wsx` framing
- Decode entry payloads (geometry, textures, audio/video codecs)
- Map stems to Gladstone / portal worlds for Classic coverage
