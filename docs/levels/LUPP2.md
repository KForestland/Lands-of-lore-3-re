# LUPP2

Made by `tools/lol3_level_report.py` from `DAT/LUPP2.WSX` and `DAT/LUPP2S.WSX`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`LUPP2.WSX` is 23,557,699 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\LUPP2\LUPP2.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0xE12B935D | 20,676,434 | 2,811,332 | `LEVELS\LUPP2\LUPP2.MAP` |
| 1 | 0xED4B9353 | 23,487,766 | 69,933 | `LEVELS\LUPP2\LUPP2.ODF` |
| 2 | 0xF19B936C | 54 | 19,226,111 | `LEVELS\LUPP2\LUPP2.TE_` |
| 3 | 0x111B9354 | 19,226,165 | 1,450,269 | `LEVELS\LUPP2\LUPP2.LMF` |

## Light map

152 stored LZO1X groups holding 19,879 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 2,811,332 | 12,076 | 67,307 | 144,163 | 9,607 |
| `ODF` | 69,933 | 516 | 3,644 | 17,922 | 68,964 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).
Field 21 counts 7,459 surface rows in section 2 ([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).

## Waypoints and paths

Waypoints 116. Paths 5. These are the header counts at +0xC4 and +0xD8, the same counts `lol3_map_spans.py --list` prints.

## Placements

Rows of the five MAP placement tables, numbered from 1. No names.

| Type | Count | Row ids |
|---|---:|---|
| type 3 | 513 | 1-513 |
| type 16 | 234 | 1-234 |
| creature | 41 | 1-41 |
| mover (type 32) | 29 | 1-29 |
| item | 99 | 1-99 |

## Sounds

`LUPP2S.WSX` holds 92 entries: 92 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Scripts

The object stream has 837 records and the region stream has 17 records. Both counts are a walk of the MAP command bytes with the opcode sizes from the executable. The [script summary](notes/LUPP2.md) gives the same record counts with the event pools.

Object stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x01 | 35 |
| 0x02 | 35 |
| 0x03 | 15 |
| 0x05 | 150 |
| 0x07 | 9 |
| 0x09 | 104 |
| 0x0D | 118 |
| 0x0E | 25 |
| 0x10 | 26 |
| 0x12 | 9 |
| 0x14 | 49 |
| 0x16 | 55 |
| 0x17 | 1 |
| 0x1B | 10 |
| 0x1C | 1 |
| 0xC4 | 1 |
| 0xC5 | 5 |
| 0xC6 | 1 |
| 0xCC | 3 |
| 0xD0 | 4 |
| 0xD2 | 3 |
| 0xF0 | 178 |

Region stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x02 | 6 |
| 0x09 | 7 |
| 0xF0 | 4 |

Opcode 0x15 does not occur, so these streams name no movie stem.
No framed command contains a music stem from the pointer table at file `0x148180`, or the hash of `MUSIC\<stem>.aud`.
No framed command contains another level stem, in either case, or the hash of that level's MAP name. So no exit in these two streams names its target level by stem or MAP hash; an exit by numeric index or another path is not ruled out.

## Related notes

- [Script summary](notes/LUPP2.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
