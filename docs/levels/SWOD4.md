# SWOD4

Made by `tools/lol3_level_report.py` from `DAT/swod4.wsx` and `DAT/SWOD4s.wsx`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`swod4.wsx` is 6,435,161 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\SWOD4\SWOD4.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0xD0BB054A | 5,929,418 | 497,535 | `LEVELS\SWOD4\SWOD4.MAP` |
| 1 | 0xDCDB0540 | 6,426,953 | 8,208 | `LEVELS\SWOD4\SWOD4.ODF` |
| 2 | 0xE12B0559 | 54 | 4,031,175 | `LEVELS\SWOD4\SWOD4.TE_` |
| 3 | 0x00AB0541 | 4,031,229 | 1,898,189 | `LEVELS\SWOD4\SWOD4.LMF` |

## Light map

165 stored LZO1X groups holding 10,232 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 497,535 | 12,076 | 38,746 | 77,882 | 4,892 |
| `ODF` | 8,208 | 516 | 1,022 | 3,990 | 7,495 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).
Field 21 counts 2,636 surface rows in section 2 ([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).

## Waypoints and paths

Waypoints 188. Paths 2. These are the header counts at +0xC4 and +0xD8, the same counts `lol3_map_spans.py --list` prints.

## Placements

Rows of the five MAP placement tables, numbered from 1. No names.

| Type | Count | Row ids |
|---|---:|---|
| type 3 | 406 | 1-406 |
| type 16 | 20 | 1-20 |
| creature | 1 | 1 |
| mover (type 32) | 0 |  |
| item | 4 | 1-4 |

## Sounds

`SWOD4s.wsx` holds 33 entries: 33 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Scripts

The object stream has 115 records and the region stream has 5 records. Both counts are a walk of the MAP command bytes with the opcode sizes from the executable. The [script summary](notes/SWOD4.md) gives the same record counts with the event pools.

Object stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x02 | 8 |
| 0x03 | 8 |
| 0x05 | 13 |
| 0x09 | 7 |
| 0x0D | 9 |
| 0x0E | 2 |
| 0x10 | 4 |
| 0x13 | 1 |
| 0x14 | 22 |
| 0x15 | 1 |
| 0x16 | 6 |
| 0xD2 | 3 |
| 0xF0 | 31 |

Region stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x09 | 1 |
| 0x0D | 2 |
| 0xC5 | 1 |
| 0xF0 | 1 |

Opcode 0x15 byte +4 names `mcmpfire` (index 7, 1 command). Byte +5 is 0 on each of these commands. VA `0x447F97` passes byte +4 to VA `0x46FA60`, and VA `0x46FCF2` reads `[index*4 + 0x54A3D0]`, the 19 stems at file `0x148BD0`.
No framed command contains a music stem from the pointer table at file `0x148180`, or the hash of `MUSIC\<stem>.aud`.
No framed command contains another level stem, in either case, or the hash of that level's MAP name. So no exit in these two streams names its target level by stem or MAP hash; an exit by numeric index or another path is not ruled out.

## Related notes

- [Script summary](notes/SWOD4.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
