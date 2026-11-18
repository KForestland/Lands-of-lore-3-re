# RVOL0

Made by `tools/lol3_level_report.py` from `DAT/rvol0.wsx` and `DAT/RVOL0s.wsx`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`rvol0.wsx` is 2,336,324 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\RVOL0\RVOL0.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0xD075F12C | 2,267,891 | 64,423 | `LEVELS\RVOL0\RVOL0.MAP` |
| 1 | 0xDC95F122 | 2,332,314 | 4,010 | `LEVELS\RVOL0\RVOL0.ODF` |
| 2 | 0xE0E5F13B | 54 | 2,007,878 | `LEVELS\RVOL0\RVOL0.TE_` |
| 3 | 0x0065F123 | 2,007,932 | 259,959 | `LEVELS\RVOL0\RVOL0.LMF` |

## Light map

16 stored LZO1X groups holding 1,220 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 64,423 | 12,076 | 15,423 | 19,815 | 549 |
| `ODF` | 4,010 | 516 | 700 | 2,486 | 3,665 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).
Field 21 counts 398 surface rows in section 2 ([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).

## Sounds

`RVOL0s.wsx` holds 208 entries: 158 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit), 50 × format 17 (IMA ADPCM, stereo, 22,050 Hz, 4-bit).

## Scripts

The object stream has 194 records and the region stream has 13 records. Both counts are a walk of the MAP command bytes with the opcode sizes from the executable. The [script summary](notes/RVOL0.md) gives the same record counts with the event pools.

Opcode 0x15 does not occur, so these streams name no movie stem.
No framed command contains a music stem from the pointer table at file `0x148180`, or the hash of `MUSIC\<stem>.aud`.
No framed command contains another level stem, in either case, or the hash of that level's MAP name. So no exit in these two streams names its target level by stem or MAP hash; an exit by numeric index or another path is not ruled out.

## Related notes

- [Script summary](notes/RVOL0.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
