# MLOW2

Made by `tools/lol3_level_report.py` from `DAT/mlow2.wsx` and `DAT/MLOW2s.wsx`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`mlow2.wsx` is 22,309,533 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\MLOW2\MLOW2.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0x8DC8A37B | 21,380,707 | 811,406 | `LEVELS\MLOW2\MLOW2.MAP` |
| 1 | 0x99E8A371 | 22,192,113 | 117,420 | `LEVELS\MLOW2\MLOW2.ODF` |
| 2 | 0x9E38A38A | 54 | 19,285,704 | `LEVELS\MLOW2\MLOW2.TE_` |
| 3 | 0xBDB8A371 | 19,285,758 | 2,094,949 | `LEVELS\MLOW2\MLOW2.LMF` |

## Light map

232 stored LZO1X groups holding 24,920 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 811,406 | 12,076 | 56,764 | 122,316 | 8,194 |
| `ODF` | 117,420 | 516 | 1,712 | 11,317 | 115,963 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).
Field 21 counts 5,550 surface rows in section 2 ([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).

## Sounds

`MLOW2s.wsx` holds 668 entries: 668 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Scripts

The object stream has 3,298 records and the region stream has 202 records. Both counts are a walk of the MAP command bytes with the opcode sizes from the executable. The [script summary](notes/MLOW2.md) gives the same record counts with the event pools.

Opcode 0x15 does not occur, so these streams name no movie stem.
No framed command contains a music stem from the pointer table at file `0x148180`, or the hash of `MUSIC\<stem>.aud`.
No framed command contains another level stem, in either case, or the hash of that level's MAP name. So no exit in these two streams names its target level by stem or MAP hash; an exit by numeric index or another path is not ruled out.

## Related notes

- [Script summary](notes/MLOW2.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
