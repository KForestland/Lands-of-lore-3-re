# GRULO

Made by `tools/lol3_level_report.py` from `DAT/grulo.wsx` and `DAT/GRULOs.wsx`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`grulo.wsx` is 13,613,906 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\GRULO\GRULO.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0x355A621D | 12,862,102 | 715,230 | `LEVELS\GRULO\GRULO.MAP` |
| 1 | 0x417A6213 | 13,577,332 | 36,574 | `LEVELS\GRULO\GRULO.ODF` |
| 2 | 0x45CA622C | 54 | 6,527,747 | `LEVELS\GRULO\GRULO.TE_` |
| 3 | 0x654A6213 | 6,527,801 | 6,334,301 | `LEVELS\GRULO\GRULO.LMF` |

## Light map

577 stored LZO1X groups holding 26,690 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 715,230 | 12,076 | 78,024 | 138,936 | 7,614 |
| `ODF` | 36,574 | 516 | 1,068 | 5,061 | 35,413 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).
Field 21 counts 6,556 surface rows in section 2 ([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).

## Waypoints and paths

Waypoints 150. Paths 0. These are the header counts at +0xC4 and +0xD8, the same counts `lol3_map_spans.py --list` prints.

## Placements

Rows of the five MAP placement tables, numbered from 1. No names.

| Type | Count | Row ids |
|---|---:|---|
| type 3 | 624 | 1-624 |
| type 16 | 286 | 1-286 |
| creature | 148 | 1-148 |
| mover (type 32) | 23 | 1-23 |
| item | 205 | 1-205 |

## Sounds

`GRULOs.wsx` holds 131 entries: 131 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Scripts

The object stream has 2,845 records and the region stream has 172 records. Both counts are a walk of the MAP command bytes with the opcode sizes from the executable. The [script summary](notes/GRULO.md) gives the same record counts with the event pools.

Object stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x01 | 40 |
| 0x02 | 31 |
| 0x03 | 84 |
| 0x05 | 241 |
| 0x06 | 58 |
| 0x07 | 165 |
| 0x09 | 707 |
| 0x0D | 133 |
| 0x0E | 82 |
| 0x0F | 67 |
| 0x10 | 293 |
| 0x11 | 55 |
| 0x12 | 11 |
| 0x14 | 112 |
| 0x15 | 1 |
| 0x16 | 29 |
| 0x17 | 2 |
| 0x19 | 4 |
| 0x1A | 8 |
| 0x1B | 22 |
| 0xC5 | 47 |
| 0xC6 | 1 |
| 0xC7 | 1 |
| 0xCC | 40 |
| 0xCE | 1 |
| 0xCF | 70 |
| 0xD2 | 6 |
| 0xF0 | 534 |

Region stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x01 | 2 |
| 0x09 | 150 |
| 0x12 | 4 |
| 0xF0 | 16 |

Opcode 0x15 byte +4 names `mshard2` (index 10, 1 command). Byte +5 is 0 on each of these commands. VA `0x447F97` passes byte +4 to VA `0x46FA60`, and VA `0x46FCF2` reads `[index*4 + 0x54A3D0]`, the 19 stems at file `0x148BD0`.
No framed command contains a music stem from the pointer table at file `0x148180`, or the hash of `MUSIC\<stem>.aud`.
No framed command contains another level stem, in either case, or the hash of that level's MAP name. So no exit in these two streams names its target level by stem or MAP hash; an exit by numeric index or another path is not ruled out.

## Related notes

- [Script summary](notes/GRULO.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
