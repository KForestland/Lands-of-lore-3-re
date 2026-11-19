# QWOD0

Made by `tools/lol3_level_report.py` from `DAT/QWOD0.WSX` and `DAT/QWOD0S.WSX`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`QWOD0.WSX` is 7,832,695 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\QWOD0\QWOD0.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0xD0B8E10A | 7,529,099 | 289,385 | `LEVELS\QWOD0\QWOD0.MAP` |
| 1 | 0xDCD8E100 | 7,818,484 | 14,211 | `LEVELS\QWOD0\QWOD0.ODF` |
| 2 | 0xE128E119 | 54 | 6,871,261 | `LEVELS\QWOD0\QWOD0.TE_` |
| 3 | 0x00A8E101 | 6,871,315 | 657,784 | `LEVELS\QWOD0\QWOD0.LMF` |

## Light map

49 stored LZO1X groups holding 5,364 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 289,385 | 12,076 | 22,574 | 41,518 | 2,368 |
| `ODF` | 14,211 | 516 | 1,298 | 6,138 | 13,762 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).
Field 21 counts 1,430 surface rows in section 2 ([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).

## Waypoints and paths

Waypoints 1. Paths 0. These are the header counts at +0xC4 and +0xD8, the same counts `lol3_map_spans.py --list` prints.

## Placements

Rows of the five MAP placement tables, numbered from 1. No names.

| Type | Count | Row ids |
|---|---:|---|
| type 3 | 472 | 1-472 |
| type 16 | 53 | 1-53 |
| creature | 1 | 1 |
| mover (type 32) | 0 |  |
| item | 6 | 1-6 |

## Sounds

`QWOD0S.WSX` holds 26 entries: 26 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Scripts

The object stream has 164 records and the region stream has 42 records. Both counts are a walk of the MAP command bytes with the opcode sizes from the executable. The [script summary](notes/QWOD0.md) gives the same record counts with the event pools.

Object stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x02 | 11 |
| 0x03 | 6 |
| 0x05 | 24 |
| 0x07 | 2 |
| 0x09 | 33 |
| 0x0E | 4 |
| 0x10 | 4 |
| 0x14 | 20 |
| 0x15 | 2 |
| 0x16 | 5 |
| 0xC5 | 6 |
| 0xC7 | 1 |
| 0xD2 | 2 |
| 0xF0 | 44 |

Region stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x09 | 37 |
| 0xF0 | 5 |

Opcode 0x15 byte +4 names `mintro02` (index 1, 2 commands). Byte +5 is 0 on each of these commands. VA `0x447F97` passes byte +4 to VA `0x46FA60`, and VA `0x46FCF2` reads `[index*4 + 0x54A3D0]`, the 19 stems at file `0x148BD0`.
No framed command contains a music stem from the pointer table at file `0x148180`, or the hash of `MUSIC\<stem>.aud`.
No framed command contains another level stem, in either case, or the hash of that level's MAP name. So no exit in these two streams names its target level by stem or MAP hash; an exit by numeric index or another path is not ruled out.

## Related notes

- [Script summary](notes/QWOD0.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
