# EWOD1

Made by `tools/lol3_level_report.py` from `DAT/EWOD1.WSX` and `DAT/EWOD1S.WSX`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`EWOD1.WSX` is 26,770,728 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\EWOD1\EWOD1.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0xD0AC221A | 24,890,106 | 1,825,978 | `LEVELS\EWOD1\EWOD1.MAP` |
| 1 | 0xDCCC2210 | 26,716,084 | 54,644 | `LEVELS\EWOD1\EWOD1.ODF` |
| 2 | 0xE11C2229 | 54 | 18,087,754 | `LEVELS\EWOD1\EWOD1.TE_` |
| 3 | 0x009C2211 | 18,087,808 | 6,802,298 | `LEVELS\EWOD1\EWOD1.LMF` |

## Light map

569 stored LZO1X groups holding 40,084 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 1,825,978 | 12,076 | 99,924 | 248,372 | 18,556 |
| `ODF` | 54,644 | 516 | 2,770 | 17,791 | 52,987 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).
Field 21 counts 11,160 surface rows in section 2 ([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).

## Waypoints and paths

Waypoints 173. Paths 2. These are the header counts at +0xC4 and +0xD8, the same counts `lol3_map_spans.py --list` prints.

## Placements

Rows of the five MAP placement tables, numbered from 1. No names.

| Type | Count | Row ids |
|---|---:|---|
| type 3 | 1,125 | 1-1125 |
| type 16 | 191 | 1-191 |
| creature | 156 | 1-156 |
| mover (type 32) | 16 | 1-16 |
| item | 44 | 1-44 |

## Sounds

`EWOD1S.WSX` holds 199 entries: 199 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Scripts

The object stream has 2,629 records and the region stream has 82 records. Both counts are a walk of the MAP command bytes with the opcode sizes from the executable. The [script summary](notes/EWOD1.md) gives the same record counts with the event pools.

Object stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x01 | 10 |
| 0x02 | 54 |
| 0x03 | 248 |
| 0x05 | 309 |
| 0x06 | 8 |
| 0x07 | 3 |
| 0x09 | 487 |
| 0x0D | 195 |
| 0x0E | 62 |
| 0x10 | 176 |
| 0x11 | 53 |
| 0x12 | 85 |
| 0x13 | 2 |
| 0x14 | 214 |
| 0x15 | 3 |
| 0x16 | 30 |
| 0x17 | 2 |
| 0x19 | 6 |
| 0x1A | 8 |
| 0x1B | 11 |
| 0x1C | 7 |
| 0xC5 | 5 |
| 0xC6 | 10 |
| 0xC7 | 6 |
| 0xD0 | 7 |
| 0xD2 | 5 |
| 0xF0 | 623 |

Region stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x01 | 5 |
| 0x02 | 3 |
| 0x09 | 42 |
| 0x0D | 2 |
| 0x0E | 12 |
| 0x12 | 1 |
| 0xC6 | 1 |
| 0xF0 | 16 |

Opcode 0x15 byte +4 names `mfrozen` (index 0, 1 command); `mvolc` (index 5, 1 command); `mvol0` (index 15, 1 command). Byte +5 is 0 on each of these commands. VA `0x447F97` passes byte +4 to VA `0x46FA60`, and VA `0x46FCF2` reads `[index*4 + 0x54A3D0]`, the 19 stems at file `0x148BD0`.
No framed command contains a music stem from the pointer table at file `0x148180`, or the hash of `MUSIC\<stem>.aud`.
No framed command contains another level stem, in either case, or the hash of that level's MAP name. So no exit in these two streams names its target level by stem or MAP hash; an exit by numeric index or another path is not ruled out.

## Related notes

- [Script summary](notes/EWOD1.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
