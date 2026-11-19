# WSX archives

**What:** LoL3's archive format. The game's `DAT/` folder holds 52 `.WSX` files: one or two per level (`CKEEP.WSX` and the sidecar `CKEEPS.WSX`), plus `GLOBAL`, `LOCAL`, `LOCALLNG`, `MOVIES1–4`, `MUSIC1–4`, `SLICECD1–4` and `cdcache`. The executable's strings name them (`GLOBAL.wsx`, `MUSIC%d.wsx`, `SLICECD%d.wsx`, `S.wsx`). Tool: `tools/extract_wsx_entries.py`.

## Layout

The layout is the same as Westwood's MIX archive in Lands of Lore II:

| Offset | Type | Meaning |
|---|---|---|
| 0 | u16 | entry count n |
| 2 | u32 | data size (bytes after the index) |
| 6 | n × 12 bytes | rows: u32 key, u32 offset from the start of the data, u32 size |
| 6 + 12n | data size | entry data |

All little-endian. `extract_wsx_entries.py --check` re-ran on 2026-11-18. CONFIRMED on the 52 files:
- **Data size:** in 51 files, 6 + 12n + data size equals the file size.
- **Offsets:** every row's offset and size lie inside the data in those 51 files, and no two entries overlap.
- **Coverage:** the entries cover the data exactly, with no gaps.
- **Order:** the rows are sorted by key read as a signed 32-bit number in all 52 files, as in LoL2.

Two corrections to the [older page](../wsx-extraction.md):
- The second u32 of a row is the entry's offset. It was listed as unknown.
- Payloads are not stored largest first. That holds in only 18 of the 52 files; the earlier peel order only happened to match there.

**CONFIRMED.** Native `0x509EC3` rotates a 32-bit accumulator right six
and adds a six-bit contribution from each uppercase ASCII filename byte.
The [native reader](../lol3-wsx-reader.md#resource-name-key) gives the
formula, name normalization and 76 exact name/key witnesses.

## Worked example

`DAT/QWOD0.WSX` (7,832,695 bytes) starts:

```
04 00   41 84 77 00   0a e1 b8 d0  55 e2 72 00  69 6a 04 00   …
```

| Bytes | Meaning |
|---|---|
| `04 00` | 4 entries |
| `41 84 77 00` | 0x778441 = 7,832,641 bytes of data = 7,832,695 − 6 − 4 × 12 |
| `0a e1 b8 d0` | entry 0 key 0xD0B8E10A |
| `55 e2 72 00` | entry 0 offset 0x72E255 = 7,529,045 in the data, file offset 7,529,045 + 54 = 7,529,099 |
| `69 6a 04 00` | entry 0 size 0x46A69 = 289,385 |

The four entries are:

| Entry | Key | File offset | Size | First dwords |
|---:|---|---:|---:|---|
| 0 | 0xD0B8E10A | 7,529,099 | 289,385 | 38, 12,076 |
| 1 | 0xDCD8E100 | 7,818,484 | 14,211 | 38, 516 |
| 2 | 0xE128E119 | 54 | 6,871,261 | — |
| 3 | 0x00A8E101 | 6,871,315 | 657,784 | 0, 38: the LMF |

Entries 0 and 1 begin with dword 38. The tool marks an LMF by its first three dwords, 0, 38 and 0x100. For the roles of the entries see [level file types](../level-file-types.md).

## cdcache.wsx

The large game-folder copy measured here was last written by the game when it ran (file date 2026-03-27; the install files date from 2024-01-09). The figures below describe this installation's cache, which the game's initializer creates and fills; another installation may differ.

**CONFIRMED.** `DAT/cdcache.wsx`, game-folder `cdcache.wsx` and
`cdcache.hdr` share bytes +0x00–+0x71. Their ordinary WSX index
declares 9 rows and 52,663,679 data bytes at +0/+2. The
ordinary exact-size check expects 52,663,793 bytes. The DAT copy
is 3,264,114 bytes. After the shared 114 bytes it is 51 copies of
one 64,000-byte block, and that block is not a byte string in the
executable, in the other programs and DLLs in the install folder, or in
this installation's game-written cache. The initializer's fill loop
(`0x4E4E61–0x4E4E95`) writes each 64,000-byte pass from the locked
screen surface (see the [native reader](../lol3-wsx-reader.md#cache-index-lifecycle)),
so the block is screen memory, not a stored resource. Its first
dword is the shipped file's `0xD0BCD8BE` at +0x72, so those bytes
are not an allocator index (the marker compare at `0x4E5118` re-initializes a cache that lacks `0xF1E2D3C4` through `0x4FE480`). Five directory entries of size 0xD
land inside the first copy. The file is missing the larger
declared ranges.
The game-folder copy is 104,896,114 bytes and has a second directory
and separately allocated storage. The original initializer copies
the header and writes in 64,000-byte blocks. Its default target is
100 MiB, rounded up in whole blocks from the header size in the
observed file (`0x4E4D0B`, `0x4E4D9C–0x4E4DC2`,
`0x4E4E41–0x4E4E95`). With `[0x545520]` 0 in the file, the target is 100 MiB, and 114 + ⌈0x6400000 / 64,000⌉ × 64,000 = 104,896,114; the 38,514 bytes past 0x6400000 are never allocated. The header's own relative offsets already allow for the 4-byte marker and the 0x3C0-byte index: its first entry, at relative 0x3C4, lands at file 0x436, and its entries reach 0x32399B5 = 52,663,793 + 964. That is why the plain exact-size figure is 964 bytes short of the header's own extent.

**CONFIRMED.** After the first directory, the game-folder file at
+0x72 has marker `0xF1E2D3C4`. The read/write path advances
four bytes before initializing the second directory at +0x76
(`0x4E50F6–0x4E5194`, `0x4FE4C2–0x4FE4FA`).
This is a mutable allocation index of 40 little-endian rows
of 0x18 bytes. The initial free span starts at +0x436, directly
after the index (`0x4FE56A–0x4FE58A`).

| Row offset | Type | Use and native evidence |
|---|---|---|
| +0x00 | u32 | Absolute cache payload position, returned by `0x4FE8F8–0x4FE902` |
| +0x04 | u32 | Span in bytes. The allocator compares the free span against the requested size and splits it on allocation (`0x4FE8C9–0x4FE8D8`, `0x4FE918–0x4FE981`). |
| +0x08 | u32 | Normalized resource name key, compared at `0x4FE891`. The caller normalizes and hashes at `0x4E448C–0x4E44A8`. |
| +0x0C | u32 | Allocation clock value from `0x51B2D0`, stored at `0x4FE94E`. The eviction walk compares it (`0x4FEA4E–0x4FEA64`), but as compiled `mov ebp, ebx` at `0x4FEA4E` runs for every allocated, unpinned row, so the candidate is the last eligible row and the clock only updates the age kept in `edi` |
| +0x10 | u32 | Generation token copied from the array indexed by +0x15 and rechecked on lookup (`0x4FE954–0x4FE95B`, `0x4FE7D2–0x4FE7F0`) |
| +0x14 | u8 | Allocated flag, set on allocation and cleared on invalidation (`0x4FE92A`, `0x4FE804`) |
| +0x15 | u8 | Index for the generation array. Value 0x11 bypasses the token comparison (`0x4FE7D2–0x4FE7DB`, `0x4FE93D`). |
| +0x16 | u8 | Pin flag, set and cleared by payload position (`0x4FE77B–0x4FE786`, `0x4FE85B–0x4FE866`). Skipped by the ordinary eviction-candidate walk (`0x4FEA40–0x4FEA4C`). |
| +0x17 | u8 | No instruction reads it (manual review of the row loops; no absolute address names it). It travels inside the 0x3C0-byte index read and write and the 6-dword row copies at `0x4FE9BA` and `0x4FEC0E`. It keeps the screen fill the initializer wrote; this installation's cache holds 0x67 on its 8 occupied rows and on 12 empty rows. See the [native reader](../lol3-wsx-reader.md#cache-index-lifecycle). |

**CONFIRMED.** In the installed witness, eight occupied rows
cover four texture banks and their four light maps. The first
row at file +0x76 is `LEVELS\QWOD0\QWOD0.TEX` (key
`0xE128E112`), stored at +0x436 with length 0xA0438A. The
adjacent light map row at +0x8E starts at +0xA047C0 with
length 0xA0978. The original WSX row for that same texture
at +0x12 gives relative offset 0x2794C41, so it would select
file +0x2794CB3. The cache allocator uses the second index for
the actual cached payload. The four texture row offsets are
+0x76, +0xA6, +0xD6 and +0x106, and their payloads start at
+0x436, +0xAA5138, +0x3239974 and +0x52D6662. The free row
at +0x136 covers +0x5666ED3 through +0x6400000, exclusive.
The other 31 rows have zero span. The 38,514 trailing bytes
lie outside the indexed spans in this witness. Compare the
[texture palette sources](../lol3-texture-palette-sources.md)
for the reader evidence within the four banks.
