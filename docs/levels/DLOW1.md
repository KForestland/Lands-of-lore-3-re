# DLOW1

Made by `tools/lol3_level_report.py` from `DAT/dlow1.wsx` and `DAT/DLOW1s.wsx`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

Related references: [Progression rows for DLOW1](../PROGRESSION.md#level-dlow1) and [item, spell and creature numbers](../NUMBERS.md).

## Level archive

`dlow1.wsx` is 22,791,662 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\DLOW1\DLOW1.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0x8DBF126B | 21,845,042 | 819,635 | `LEVELS\DLOW1\DLOW1.MAP` |
| 1 | 0x99DF1261 | 22,664,677 | 126,985 | `LEVELS\DLOW1\DLOW1.ODF` |
| 2 | 0x9E2F127A | 54 | 19,749,463 | `LEVELS\DLOW1\DLOW1.TE_` |
| 3 | 0xBDAF1261 | 19,749,517 | 2,095,525 | `LEVELS\DLOW1\DLOW1.LMF` |

## Light map

232 stored LZO1X groups holding 24,920 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 819,635 | 12,076 | 55,435 | 119,963 | 8,066 |
| `ODF` | 126,985 | 516 | 1,666 | 9,169 | 125,680 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).
Field 21 counts 5,422 surface rows in section 2 ([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).

## Waypoints and paths

Waypoints 114. Paths 1. These are the header counts at +0xC4 and +0xD8, the same counts `lol3_map_spans.py --list` prints.

## Placements

Rows of the five MAP placement tables, numbered from 1. No names.

| Type | Count | Row ids |
|---|---:|---|
| type 3 | 628 | 1-628 |
| type 16 | 370 | 1-370 |
| creature | 110 | 1-110 |
| mover (type 32) | 79 | 1-79 |
| item | 573 | 1-573 |

## Sounds

`DLOW1s.wsx` holds 907 entries: 907 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Scripts

The object stream has 4,867 records and the region stream has 355 records. Both counts are a walk of the MAP command bytes with the opcode sizes from the executable. The [script summary](notes/DLOW1.md) gives the same record counts with the event pools.

Object stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x01 | 60 |
| 0x02 | 358 |
| 0x03 | 78 |
| 0x05 | 495 |
| 0x07 | 18 |
| 0x09 | 1,049 |
| 0x0D | 576 |
| 0x0E | 60 |
| 0x10 | 88 |
| 0x11 | 3 |
| 0x12 | 9 |
| 0x14 | 138 |
| 0x16 | 305 |
| 0x17 | 8 |
| 0x19 | 5 |
| 0x1A | 11 |
| 0x1B | 260 |
| 0x1C | 9 |
| 0xC5 | 19 |
| 0xC6 | 15 |
| 0xC7 | 42 |
| 0xD0 | 6 |
| 0xD2 | 11 |
| 0xF0 | 1,244 |

Region stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x01 | 4 |
| 0x02 | 3 |
| 0x09 | 194 |
| 0x0E | 15 |
| 0x10 | 7 |
| 0x1B | 4 |
| 0xC5 | 5 |
| 0xC6 | 2 |
| 0xF0 | 121 |

Opcode 0x15 does not occur, so these streams name no movie stem.
No framed command contains a music stem from the pointer table at file `0x148180`, or the hash of `MUSIC\<stem>.aud`.
No framed command contains another level stem, in either case, or the hash of that level's MAP name. So no exit in these two streams names its target level by stem or MAP hash; an exit by numeric index or another path is not ruled out.

## Related notes

- [Script summary](notes/DLOW1.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
