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

The name hash is not the LoL2 one. Names the executable uses, such as `global\spell.tex`, `global\global.odf` and `ckeep\ckeep.lmf`, match no key in `GLOBAL.WSX` or `CKEEP.WSX` with any of the four Westwood hash variants in the LoL2 tools ([Q2](../OPEN_QUESTIONS.md)).

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

Entries 0 and 1 begin with dword 38. The tool marks an entry as LMF when its dword +4 is 38. For the roles of the entries see [level file types](../level-file-types.md).

## cdcache.wsx

**CONFIRMED.** At +0/+2 both cache copies declare 9 rows and
52,663,679 data bytes. The `DAT/` copy is 3,264,114 bytes and the
game-folder copy is 104,896,114 bytes. The header implies 52,663,793
bytes, so both copies fail the ordinary archive equality check.
The [native WSX and cache reader](../lol3-wsx-reader.md) traces the
header copy, expansion, marker and separate cache index.
