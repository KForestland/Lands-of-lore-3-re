# Textures

LoL3 has two texture formats. Only the first is decoded.

| Format | Where | State |
|---|---|---|
| Row-span records, flags `0x028E` / `0x828E` | the texture banks in `cdcache.wsx` in the game folder | layout CONFIRMED on all 854 records; colour open |
| LEVED `+1` packs | the per-level art entries named with `.pcx` names | not decoded ([Q7](../OPEN_QUESTIONS.md)) |

Older notes: [tex-format](../tex-format.md), [texture 028E evidence](../texture-028e-evidence.md). Tool: `tools/lol3_texture_spans.py`. It writes nothing and makes no pictures.

## Row-span record

```
u32 flags            0x028E or 0x828E
u16 width, u16 height
u32 size             bytes of rows that follow
height rows of:
    u16 A            A & 0xC000: 0 = opaque copy, 0x4000 = skip palette index 0; A & 0x3FFF = start column
    u16 B            number of bytes in this row
    B bytes          palette indices placed from the start column
```

`lol3_texture_spans.py --check --data <DAT>` re-ran on 2026-11-18 over the whole `cdcache.wsx` in the game folder (104,896,114 bytes). It found 854 record headers with these flags. All 854 consume exactly `height` rows, every row fits inside the width, and the last row ends at the payload end: 815 with flags `0x028E` and 39 with `0x828E`. CONFIRMED. The older pages tested 26 samples; this check covers every record.

## Worked example

At file offset 1,230,562 of `cdcache.wsx`:

```
8e 02 00 00   80 00   00 01   35 20 00 00   80 00 00 00 …
```

| Bytes | Meaning |
|---|---|
| `8e 02 00 00` | flags 0x028E |
| `80 00`, `00 01` | 128 × 256 |
| `35 20 00 00` | 8,245 bytes of rows |
| `80 00 00 00` | row 0: column 128, 0 bytes (an empty row) |

The next records follow directly, each half the size of the one before: 64 × 128 at 1,238,819 (= 1,230,562 + 12 + 8,245), then 32 × 64, 16 × 32 and 8 × 16. Together they form a chain of five mip levels.

## Colour

**CONFIRMED.** The executable selects a per-descriptor source through
`0x44B6E0` and builds 256 output words at `0x4826D0`. The native
[texture colour bake](../lol3-texture-bake.md) gives the source selector,
zero handling and indexed writes. The source record for a specific
archived texture remains **UNCONFIRMED**.

## The cache file

The `cdcache.wsx` in the game folder has a WSX header for 9 entries and 52,663,679 bytes of data. The file is 104,896,114 bytes, so the header covers only its first 52,663,793 bytes. 420 of the 854 texture records lie after that point. The `cdcache.wsx` in `DAT/` is a different, 3,264,114-byte file with the same kind of header, and it holds no span records. How the game fills and indexes this cache is open ([Q1](../OPEN_QUESTIONS.md)).
