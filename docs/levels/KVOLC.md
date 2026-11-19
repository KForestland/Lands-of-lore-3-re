# KVOLC

Made by `tools/lol3_level_report.py` from `DAT/kvolc.wsx` and `DAT/KVOLCs.wsx`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

Related references: [Progression rows for KVOLC](../PROGRESSION.md#level-kvolc) and [item, spell and creature numbers](../NUMBERS.md).

## Level archive

`kvolc.wsx` is 23,325,526 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\KVOLC\KVOLC.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0xD06E955C | 22,163,146 | 1,108,084 | `LEVELS\KVOLC\KVOLC.MAP` |
| 1 | 0xDC8E9552 | 23,271,230 | 54,296 | `LEVELS\KVOLC\KVOLC.ODF` |
| 2 | 0xE0DE956B | 54 | 14,314,762 | `LEVELS\KVOLC\KVOLC.TE_` |
| 3 | 0x005E9553 | 14,314,816 | 7,848,330 | `LEVELS\KVOLC\KVOLC.LMF` |

## Light map

560 stored LZO1X groups holding 29,956 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 1,108,084 | 12,076 | 92,078 | 178,958 | 10,860 |
| `ODF` | 54,296 | 516 | 2,954 | 12,235 | 52,399 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).
Field 21 counts 8,728 surface rows in section 2 ([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).

## Waypoints and paths

Waypoints 183. Paths 4. These are the header counts at +0xC4 and +0xD8, the same counts `lol3_map_spans.py --list` prints.

## Placements

Rows of the five MAP placement tables, numbered from 1. No names.

| Type | Count | Row ids |
|---|---:|---|
| type 3 | 1,160 | 1-1160 |
| type 16 | 326 | 1-326 |
| creature | 119 | 1-119 |
| mover (type 32) | 85 | 1-85 |
| item | 66 | 1-66 |

## Sounds

`KVOLCs.wsx` holds 257 entries: 207 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit), 50 × format 17 (IMA ADPCM, stereo, 22,050 Hz, 4-bit).

## Scripts

The object stream has 3,183 records and the region stream has 834 records. Both counts are a walk of the MAP command bytes with the opcode sizes from the executable. The [script summary](notes/KVOLC.md) gives the same record counts with the event pools.

Object stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x01 | 152 |
| 0x02 | 66 |
| 0x03 | 92 |
| 0x05 | 192 |
| 0x06 | 16 |
| 0x07 | 38 |
| 0x09 | 367 |
| 0x0D | 210 |
| 0x0E | 121 |
| 0x0F | 5 |
| 0x10 | 232 |
| 0x11 | 4 |
| 0x12 | 9 |
| 0x14 | 177 |
| 0x15 | 1 |
| 0x16 | 55 |
| 0x17 | 4 |
| 0x19 | 1 |
| 0x1A | 19 |
| 0x1B | 51 |
| 0xC4 | 305 |
| 0xC5 | 182 |
| 0xC6 | 20 |
| 0xC7 | 2 |
| 0xCC | 102 |
| 0xCE | 1 |
| 0xCF | 12 |
| 0xD0 | 29 |
| 0xD2 | 10 |
| 0xF0 | 708 |

Region stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x01 | 40 |
| 0x09 | 159 |
| 0x0D | 42 |
| 0x0E | 24 |
| 0x10 | 3 |
| 0x12 | 7 |
| 0x14 | 123 |
| 0x1A | 1 |
| 0x1B | 29 |
| 0xC4 | 113 |
| 0xC6 | 9 |
| 0xCE | 1 |
| 0xD0 | 39 |
| 0xF0 | 244 |

Opcode 0x15 byte +4 names `mshard1` (index 9, 1 command). Byte +5 is 0 on each of these commands. VA `0x447F97` passes byte +4 to VA `0x46FA60`, and VA `0x46FCF2` reads `[index*4 + 0x54A3D0]`, the 19 stems at file `0x148BD0`.
No framed command contains a music stem from the pointer table at file `0x148180`, or the hash of `MUSIC\<stem>.aud`.
No framed command contains another level stem, in either case, or the hash of that level's MAP name. So no exit in these two streams names its target level by stem or MAP hash; an exit by numeric index or another path is not ruled out.

## Related notes

- [Script summary](notes/KVOLC.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
