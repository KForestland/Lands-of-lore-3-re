# NWOD2

Made by `tools/lol3_level_report.py` from `DAT/NWOD2.WSX` and `DAT/NWOD2S.WSX`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

Related references: [Progression rows for NWOD2](../PROGRESSION.md#level-nwod2) and [item, spell and creature numbers](../NUMBERS.md).

## Level archive

`NWOD2.WSX` is 30,304,516 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\NWOD2\NWOD2.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0xD0B5B32A | 28,458,798 | 1,776,030 | `LEVELS\NWOD2\NWOD2.MAP` |
| 1 | 0xDCD5B320 | 30,234,828 | 69,688 | `LEVELS\NWOD2\NWOD2.ODF` |
| 2 | 0xE125B339 | 54 | 21,516,899 | `LEVELS\NWOD2\NWOD2.TE_` |
| 3 | 0x00A5B321 | 21,516,953 | 6,941,845 | `LEVELS\NWOD2\NWOD2.LMF` |

## Light map

558 stored LZO1X groups holding 39,384 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 1,776,030 | 12,076 | 101,087 | 250,015 | 18,616 |
| `ODF` | 69,688 | 516 | 3,276 | 20,851 | 67,263 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).
Field 21 counts 11,197 surface rows in section 2 ([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).

## Waypoints and paths

Waypoints 208. Paths 1. These are the header counts at +0xC4 and +0xD8, the same counts `lol3_map_spans.py --list` prints.

## Placements

Rows of the five MAP placement tables, numbered from 1. No names.

| Type | Count | Row ids |
|---|---:|---|
| type 3 | 1,126 | 1-1126 |
| type 16 | 184 | 1-184 |
| creature | 167 | 1-167 |
| mover (type 32) | 14 | 1-14 |
| item | 33 | 1-33 |

## Sounds

`NWOD2S.WSX` holds 131 entries: 131 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Scripts

The object stream has 1,891 records and the region stream has 66 records. Both counts are a walk of the MAP command bytes with the opcode sizes from the executable. The [script summary](notes/NWOD2.md) gives the same record counts with the event pools.

Object stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x01 | 7 |
| 0x02 | 42 |
| 0x03 | 254 |
| 0x05 | 211 |
| 0x06 | 6 |
| 0x07 | 37 |
| 0x09 | 281 |
| 0x0D | 217 |
| 0x0E | 56 |
| 0x0F | 1 |
| 0x10 | 102 |
| 0x11 | 51 |
| 0x12 | 2 |
| 0x14 | 122 |
| 0x15 | 4 |
| 0x16 | 36 |
| 0x17 | 8 |
| 0x18 | 1 |
| 0x1A | 3 |
| 0x1B | 9 |
| 0x1C | 8 |
| 0xC5 | 5 |
| 0xC6 | 3 |
| 0xC7 | 2 |
| 0xD0 | 4 |
| 0xD2 | 5 |
| 0xF0 | 414 |

Region stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x01 | 5 |
| 0x02 | 10 |
| 0x09 | 21 |
| 0x0E | 16 |
| 0x10 | 1 |
| 0xC6 | 1 |
| 0xF0 | 12 |

Opcode 0x15 byte +4 names `mfrozen` (index 0, 1 command); `mruloi` (index 3, 1 command); `mvolc` (index 5, 1 command); `munder` (index 14, 1 command). Byte +5 is 0 on each of these commands. VA `0x447F97` passes byte +4 to VA `0x46FA60`, and VA `0x46FCF2` reads `[index*4 + 0x54A3D0]`, the 19 stems at file `0x148BD0`.
No framed command contains a music stem from the pointer table at file `0x148180`, or the hash of `MUSIC\<stem>.aud`.
No framed command contains another level stem, in either case, or the hash of that level's MAP name. So no exit in these two streams names its target level by stem or MAP hash; an exit by numeric index or another path is not ruled out.

## Related notes

- [Script summary](notes/NWOD2.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
