# HWHIT

Made by `tools/lol3_level_report.py` from `DAT/hwhit.wsx` and `DAT/HWHITs.wsx`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`hwhit.wsx` is 18,226,802 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\HWHIT\HWHIT.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0x99AF775F | 17,464,069 | 682,538 | `LEVELS\HWHIT\HWHIT.MAP` |
| 1 | 0xA5CF7755 | 18,146,607 | 80,195 | `LEVELS\HWHIT\HWHIT.ODF` |
| 2 | 0xAA1F776E | 54 | 13,795,845 | `LEVELS\HWHIT\HWHIT.TE_` |
| 3 | 0xC99F7755 | 13,795,899 | 3,668,170 | `LEVELS\HWHIT\HWHIT.LMF` |

## Light map

293 stored LZO1X groups holding 21,085 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 682,538 | 12,076 | 69,286 | 131,094 | 7,726 |
| `ODF` | 80,195 | 516 | 1,482 | 11,088 | 78,418 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).
Field 21 counts 5,192 surface rows in section 2 ([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).

## Waypoints and paths

Waypoints 171. Paths 4. These are the header counts at +0xC4 and +0xD8, the same counts `lol3_map_spans.py --list` prints.

## Placements

Rows of the five MAP placement tables, numbered from 1. No names.

| Type | Count | Row ids |
|---|---:|---|
| type 3 | 598 | 1-598 |
| type 16 | 204 | 1-204 |
| creature | 109 | 1-109 |
| mover (type 32) | 46 | 1-46 |
| item | 178 | 1-178 |

## Sounds

`HWHITs.wsx` holds 353 entries: 353 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Scripts

The object stream has 3,549 records and the region stream has 146 records. Both counts are a walk of the MAP command bytes with the opcode sizes from the executable. The [script summary](notes/HWHIT.md) gives the same record counts with the event pools.

Object stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x01 | 136 |
| 0x02 | 166 |
| 0x03 | 179 |
| 0x05 | 202 |
| 0x06 | 16 |
| 0x07 | 4 |
| 0x09 | 703 |
| 0x0D | 459 |
| 0x0E | 76 |
| 0x0F | 11 |
| 0x10 | 167 |
| 0x11 | 7 |
| 0x12 | 8 |
| 0x13 | 2 |
| 0x14 | 157 |
| 0x15 | 1 |
| 0x16 | 167 |
| 0x17 | 3 |
| 0x19 | 1 |
| 0x1A | 10 |
| 0x1B | 155 |
| 0x1C | 7 |
| 0xC4 | 28 |
| 0xC5 | 43 |
| 0xC6 | 30 |
| 0xC7 | 3 |
| 0xCE | 1 |
| 0xCF | 32 |
| 0xD0 | 1 |
| 0xD2 | 10 |
| 0xF0 | 764 |

Region stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x01 | 6 |
| 0x02 | 1 |
| 0x09 | 70 |
| 0x10 | 1 |
| 0x14 | 1 |
| 0xC4 | 41 |
| 0xF0 | 26 |

Opcode 0x15 byte +4 names `mshard2` (index 10, 1 command). Byte +5 is 0 on each of these commands. VA `0x447F97` passes byte +4 to VA `0x46FA60`, and VA `0x46FCF2` reads `[index*4 + 0x54A3D0]`, the 19 stems at file `0x148BD0`.
No framed command contains a music stem from the pointer table at file `0x148180`, or the hash of `MUSIC\<stem>.aud`.
No framed command contains another level stem, in either case, or the hash of that level's MAP name. So no exit in these two streams names its target level by stem or MAP hash; an exit by numeric index or another path is not ruled out.

## Related notes

- [Script summary](notes/HWHIT.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
