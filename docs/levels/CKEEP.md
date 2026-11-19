# CKEEP

Made by `tools/lol3_level_report.py` from `DAT/CKEEP.WSX` and `DAT/CKEEPS.WSX`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`CKEEP.WSX` is 13,900,854 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\CKEEP\CKEEP.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0x936A2304 | 12,685,444 | 663,806 | `LEVELS\CKEEP\CKEEP.LMF` |
| 1 | 0x637A230E | 13,349,250 | 503,908 | `LEVELS\CKEEP\CKEEP.MAP` |
| 2 | 0x6F9A2304 | 13,853,158 | 47,696 | `LEVELS\CKEEP\CKEEP.ODF` |
| 3 | 0x73EA231D | 54 | 12,685,390 | `LEVELS\CKEEP\CKEEP.TE_` |

## Light map

63 stored LZO1X groups holding 12,176 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 503,908 | 12,076 | 43,434 | 83,962 | 5,066 |
| `ODF` | 47,696 | 516 | 2,402 | 10,555 | 47,575 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).
Field 21 counts 3,790 surface rows in section 2 ([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).

## Waypoints and paths

Waypoints 15. Paths 0. These are the header counts at +0xC4 and +0xD8, the same counts `lol3_map_spans.py --list` prints.

## Placements

Rows of the five MAP placement tables, numbered from 1. No names.

| Type | Count | Row ids |
|---|---:|---|
| type 3 | 186 | 1-186 |
| type 16 | 99 | 1-99 |
| creature | 15 | 1-15 |
| mover (type 32) | 30 | 1-30 |
| item | 84 | 1-84 |

## Sounds

`CKEEPS.WSX` holds 357 entries: 357 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Scripts

The object stream has 1,746 records and the region stream has 35 records. Both counts are a walk of the MAP command bytes with the opcode sizes from the executable. The [script summary](notes/CKEEP.md) gives the same record counts with the event pools.

Object stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x01 | 63 |
| 0x02 | 120 |
| 0x03 | 32 |
| 0x05 | 1 |
| 0x06 | 2 |
| 0x09 | 181 |
| 0x0D | 322 |
| 0x0E | 28 |
| 0x10 | 70 |
| 0x11 | 2 |
| 0x12 | 10 |
| 0x14 | 6 |
| 0x15 | 1 |
| 0x16 | 219 |
| 0x1A | 4 |
| 0x1B | 189 |
| 0xC4 | 6 |
| 0xC5 | 20 |
| 0xC6 | 12 |
| 0xC7 | 1 |
| 0xD0 | 6 |
| 0xD2 | 6 |
| 0xF0 | 445 |

Region stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x05 | 1 |
| 0x09 | 19 |
| 0xC5 | 5 |
| 0xF0 | 10 |

Opcode 0x15 byte +4 names `mking` (index 2, 1 command). Byte +5 is 0 on each of these commands. VA `0x447F97` passes byte +4 to VA `0x46FA60`, and VA `0x46FCF2` reads `[index*4 + 0x54A3D0]`, the 19 stems at file `0x148BD0`.
No framed command contains a music stem from the pointer table at file `0x148180`, or the hash of `MUSIC\<stem>.aud`.
No framed command contains another level stem, in either case, or the hash of that level's MAP name. So no exit in these two streams names its target level by stem or MAP hash; an exit by numeric index or another path is not ruled out.

## Related notes

- [Script summary](notes/CKEEP.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
