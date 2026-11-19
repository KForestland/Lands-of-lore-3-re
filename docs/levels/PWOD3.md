# PWOD3

Made by `tools/lol3_level_report.py` from `DAT/PWOD3.WSX` and `DAT/PWOD3S.WSX`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`PWOD3.WSX` is 30,046,627 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\PWOD3\PWOD3.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0xD0B7D43A | 28,151,609 | 1,824,035 | `LEVELS\PWOD3\PWOD3.MAP` |
| 1 | 0xDCD7D430 | 29,975,644 | 70,983 | `LEVELS\PWOD3\PWOD3.ODF` |
| 2 | 0xE127D449 | 54 | 21,163,672 | `LEVELS\PWOD3\PWOD3.TE_` |
| 3 | 0x00A7D431 | 21,163,726 | 6,987,883 | `LEVELS\PWOD3\PWOD3.LMF` |

## Light map

562 stored LZO1X groups holding 39,851 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 1,824,035 | 12,076 | 103,547 | 253,899 | 18,794 |
| `ODF` | 70,983 | 516 | 3,322 | 18,942 | 67,750 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).
Field 21 counts 11,331 surface rows in section 2 ([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).

## Waypoints and paths

Waypoints 246. Paths 1. These are the header counts at +0xC4 and +0xD8, the same counts `lol3_map_spans.py --list` prints.

## Placements

Rows of the five MAP placement tables, numbered from 1. No names.

| Type | Count | Row ids |
|---|---:|---|
| type 3 | 1,116 | 1-1116 |
| type 16 | 205 | 1-205 |
| creature | 171 | 1-171 |
| mover (type 32) | 14 | 1-14 |
| item | 31 | 1-31 |

## Sounds

`PWOD3S.WSX` holds 92 entries: 92 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Scripts

The object stream has 1,788 records and the region stream has 55 records. Both counts are a walk of the MAP command bytes with the opcode sizes from the executable. The [script summary](notes/PWOD3.md) gives the same record counts with the event pools.

Object stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x01 | 5 |
| 0x02 | 32 |
| 0x03 | 212 |
| 0x05 | 260 |
| 0x06 | 8 |
| 0x07 | 39 |
| 0x09 | 258 |
| 0x0D | 170 |
| 0x0E | 60 |
| 0x10 | 96 |
| 0x11 | 52 |
| 0x12 | 1 |
| 0x13 | 1 |
| 0x14 | 140 |
| 0x15 | 6 |
| 0x17 | 10 |
| 0x1A | 2 |
| 0x1C | 10 |
| 0xC5 | 13 |
| 0xD0 | 4 |
| 0xD2 | 5 |
| 0xF0 | 404 |

Region stream by opcode:

| Opcode | Commands |
|---:|---:|
| 0x01 | 5 |
| 0x02 | 10 |
| 0x09 | 18 |
| 0x0E | 12 |
| 0x16 | 1 |
| 0xC5 | 1 |
| 0xF0 | 8 |

Opcode 0x15 byte +4 names `mfrozen` (index 0, 1 command); `mruloi` (index 3, 1 command); `mvolc` (index 5, 1 command); `mshatter` (index 12, 1 command); `mtent` (index 13, 1 command); `munder` (index 14, 1 command). Byte +5 is 0 on each of these commands. VA `0x447F97` passes byte +4 to VA `0x46FA60`, and VA `0x46FCF2` reads `[index*4 + 0x54A3D0]`, the 19 stems at file `0x148BD0`.
No framed command contains a music stem from the pointer table at file `0x148180`, or the hash of `MUSIC\<stem>.aud`.
No framed command contains another level stem, in either case, or the hash of that level's MAP name. So no exit in these two streams names its target level by stem or MAP hash; an exit by numeric index or another path is not ruled out.

## Related notes

- [Script summary](notes/PWOD3.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
