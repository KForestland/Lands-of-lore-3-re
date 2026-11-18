# LMF geometry index

**What:** one entry in each level's WSX archive. A header with a table of 38 records at `0x100` points into a tree of blocks: index blocks point to further blocks, and leaf blocks hold the level's geometry data, whose layout is open. Tool: `tools/walk_lmf_leaves.py`. Detailed notes: [lmf-size-formula.md](../lmf-size-formula.md).

## Layout

| Offset | Type | Meaning | Evidence |
|---|---|---|---|
| +0x00 | u32 | 0 | CONFIRMED on all 18 LMF entries |
| +0x04 | u32 | 38, the number of table records (the tools recognise an LMF by this value) | CONFIRMED on all 18 |
| +0x08 | u32 | 0x100, the offset of the record table | CONFIRMED on all 18 |
| +0x0C… | u32 | further header fields; the pool start and end are candidates | UNCONFIRMED |
| 0x100 | 38 × 16 bytes | records: u32 offset (from the end of the table, `0x100 + 38 × 16`), u32 block size, u32 marker, u32 extra | layout CONFIRMED by the walk |

**Block sizes.** Every block is `(2^n + 2) × 16 + 12` bytes for n = 1 to 10: 76, 108, 172, 300, 556, 1,068, 2,092, 4,140, 8,236 or 16,428.

**Index blocks.** An index block holds rows of `(offset, size, 0xCDCDCDCD, 0)` that point to more blocks. `0xCDCDCDCD` is the fill value of a Microsoft C debug heap, written into the file as the marker.

**Leaf blocks.** All other blocks are leaves.

`walk_lmf_leaves.py --check --data <DAT>` re-ran on 2026-11-18. CONFIRMED on the 18 LMF entries of the 51 readable WSX files:
- 45,836 index blocks and 311,934 leaf blocks;
- every block size lies on the ladder.

## Worked example

`CKEEP.WSX` entry 0 (file offset 12,685,444, 663,806 bytes) starts:

```
00 00 00 00   26 00 00 00   00 01 00 00   00 fa 02 00
```

The bytes give 0, then 38 records, then the record table at 0x100, then field 0x2FA00 = 195,072.

The first records at 0x100:

| Record | Bytes | Offset | Size | Marker | Extra |
|---:|---|---:|---:|---|---:|
| 0 | `00 00 00 00 4c 00 00 00 cc cd cd cd 91 02 00 00` | 0 | 76 | 0xCDCDCDCC | 657 |
| 1 | `4c 00 00 00 4c 00 00 00 cd cd cd cd 00 00 00 00` | 76 | 76 | 0xCDCDCDCD | 0 |

Record 0 points to the block at 0x100 + 38 × 16 = 864. That block begins `28 29 00 00 2c 01 00 00 cd cd cd cd 00 00 00 00`, an index row pointing to a 300-byte block at relative offset 0x2928.

The walk of CKEEP finds 6,173 leaf blocks and 4,576 index blocks. That matches the September probe on the [older page](../lmf-size-formula.md).

## Open ([Q3](../OPEN_QUESTIONS.md))

- What a leaf block holds. The older page reports that leaves are not raw 16-bit coordinates, and that no whole leaf is LZO1X-compressed (not re-run here). The reader in `LOL3.EXE` has not been located.
- The meaning of header fields after +0x08, and of the marker variant `0xCDCDCDCC` and the extra word in record 0.
