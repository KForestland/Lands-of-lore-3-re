# ISHAT

Made by `tools/lol3_level_report.py` from `DAT/ishat.wsx` and `DAT/ISHATs.wsx`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`ishat.wsx` is 15,968,698 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\ISHAT\ISHAT.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0x98A0873D | 14,967,948 | 930,151 | `LEVELS\ISHAT\ISHAT.MAP` |
| 1 | 0xA4C08733 | 15,898,099 | 70,599 | `LEVELS\ISHAT\ISHAT.ODF` |
| 2 | 0xA910874C | 54 | 12,018,923 | `LEVELS\ISHAT\ISHAT.TE_` |
| 3 | 0xC8908733 | 12,018,977 | 2,948,971 | `LEVELS\ISHAT\ISHAT.LMF` |

## Light map

283 stored LZO1X groups holding 20,890 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 930,151 | 12,076 | 72,302 | 136,014 | 7,964 |
| `ODF` | 70,599 | 516 | 1,436 | 15,650 | 69,638 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).
Field 21 counts 7,341 surface rows in section 2 ([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).

## Waypoints and paths

Waypoints 109. Paths 0. These are the header counts at +0xC4 and +0xD8, the same counts `lol3_map_spans.py --list` prints.

## Placements

Rows of the five MAP placement tables, numbered from 1. No names.

| Type | Count | Row ids |
|---|---:|---|
| type 3 | 874 | 1-874 |
| type 16 | 176 | 1-176 |
| creature | 109 | 1-109 |
| mover (type 32) | 74 | 1-74 |
| item | 3 | 1-3 |

## Sounds

`ISHATs.wsx` holds 306 entries: 306 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Scripts

The object stream has 3,061 records and the region stream has 162 records. Both counts are a walk of the MAP command bytes with the opcode sizes from the executable. The [script summary](notes/ISHAT.md) gives the same record counts with the event pools.

Object stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x01 | 102 |
| 0x02 | 30 |
| 0x03 | 67 |
| 0x05 | 253 |
| 0x06 | 280 |
| 0x07 | 77 |
| 0x09 | 558 |
| 0x0D | 101 |
| 0x0E | 208 |
| 0x0F | 39 |
| 0x10 | 211 |
| 0x11 | 10 |
| 0x12 | 71 |
| 0x14 | 148 |
| 0x15 | 1 |
| 0x16 | 69 |
| 0x17 | 10 |
| 0x19 | 3 |
| 0x1A | 20 |
| 0x1B | 21 |
| 0x1C | 56 |
| 0xC4 | 75 |
| 0xC5 | 44 |
| 0xC6 | 7 |
| 0xC7 | 1 |
| 0xCC | 28 |
| 0xCF | 11 |
| 0xD0 | 20 |
| 0xD2 | 9 |
| 0xF0 | 531 |

Region stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x09 | 132 |
| 0x0D | 18 |
| 0x0E | 2 |
| 0xF0 | 10 |

Opcode 0x15 byte +4 names `mshard3` (index 11, 1 command). Byte +5 is 0 on each of these commands. VA `0x447F97` passes byte +4 to VA `0x46FA60`, and VA `0x46FCF2` reads `[index*4 + 0x54A3D0]`, the 19 stems at file `0x148BD0`.
No framed command contains a music stem from the pointer table at file `0x148180`, or the hash of `MUSIC\<stem>.aud`.
No framed command contains another level stem, in either case, or the hash of that level's MAP name. So no exit in these two streams names its target level by stem or MAP hash; an exit by numeric index or another path is not ruled out.

## Related notes

- [Script summary](notes/ISHAT.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
