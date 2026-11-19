# BUPP1

Made by `tools/lol3_level_report.py` from `DAT/BUPP1.WSX` and `DAT/BUPP1S.WSX`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

Related references: [Progression rows for BUPP1](../PROGRESSION.md#level-bupp1) and [item, spell and creature numbers](../NUMBERS.md).

## Level archive

`BUPP1.WSX` is 28,712,797 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\BUPP1\BUPP1.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0xE120F24D | 25,198,902 | 3,413,407 | `LEVELS\BUPP1\BUPP1.MAP` |
| 1 | 0xED40F243 | 28,612,309 | 100,488 | `LEVELS\BUPP1\BUPP1.ODF` |
| 2 | 0xF190F25C | 54 | 23,210,492 | `LEVELS\BUPP1\BUPP1.TE_` |
| 3 | 0x1110F244 | 23,210,546 | 1,988,356 | `LEVELS\BUPP1\BUPP1.LMF` |

## Light map

208 stored LZO1X groups holding 30,415 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 3,413,407 | 12,076 | 92,459 | 198,371 | 13,239 |
| `ODF` | 100,488 | 516 | 2,908 | 15,297 | 99,983 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).
Field 21 counts 10,483 surface rows in section 2 ([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).

## Waypoints and paths

Waypoints 179. Paths 11. These are the header counts at +0xC4 and +0xD8, the same counts `lol3_map_spans.py --list` prints.

## Placements

Rows of the five MAP placement tables, numbered from 1. No names.

| Type | Count | Row ids |
|---|---:|---|
| type 3 | 740 | 1-740 |
| type 16 | 257 | 1-257 |
| creature | 60 | 1-60 |
| mover (type 32) | 96 | 1-96 |
| item | 959 | 1-959 |

## Sounds

`BUPP1S.WSX` holds 1684 entries: 1684 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Scripts

The object stream has 8,795 records and the region stream has 759 records. Both counts are a walk of the MAP command bytes with the opcode sizes from the executable. The [script summary](notes/BUPP1.md) gives the same record counts with the event pools.

Object stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x01 | 167 |
| 0x02 | 458 |
| 0x03 | 207 |
| 0x05 | 463 |
| 0x06 | 69 |
| 0x07 | 75 |
| 0x09 | 1,498 |
| 0x0D | 1,235 |
| 0x0E | 92 |
| 0x0F | 4 |
| 0x10 | 330 |
| 0x11 | 16 |
| 0x12 | 32 |
| 0x14 | 290 |
| 0x16 | 871 |
| 0x17 | 5 |
| 0x18 | 1 |
| 0x19 | 26 |
| 0x1A | 33 |
| 0x1B | 514 |
| 0x1C | 4 |
| 0xC4 | 29 |
| 0xC5 | 82 |
| 0xC6 | 52 |
| 0xC7 | 41 |
| 0xCC | 64 |
| 0xCF | 6 |
| 0xD0 | 10 |
| 0xD2 | 15 |
| 0xF0 | 2,106 |

Region stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x01 | 47 |
| 0x02 | 55 |
| 0x07 | 2 |
| 0x09 | 349 |
| 0x0D | 14 |
| 0x10 | 11 |
| 0x14 | 2 |
| 0x1B | 25 |
| 0xC4 | 2 |
| 0xC5 | 16 |
| 0xC6 | 21 |
| 0xC7 | 4 |
| 0xF0 | 211 |

Opcode 0x15 does not occur, so these streams name no movie stem.
No framed command contains a music stem from the pointer table at file `0x148180`, or the hash of `MUSIC\<stem>.aud`.
No framed command contains another level stem, in either case, or the hash of that level's MAP name. So no exit in these two streams names its target level by stem or MAP hash; an exit by numeric index or another path is not ruled out.

## Related notes

- [Script summary](notes/BUPP1.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
