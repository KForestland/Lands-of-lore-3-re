# JUNDR

Made by `tools/lol3_level_report.py` from `DAT/jundr.wsx` and `DAT/JUNDRs.wsx`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`jundr.wsx` is 16,531,924 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\JUNDR\JUNDR.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0xBF29952A | 15,382,399 | 1,041,973 | `LEVELS\JUNDR\JUNDR.MAP` |
| 1 | 0xCB499520 | 16,424,372 | 107,552 | `LEVELS\JUNDR\JUNDR.ODF` |
| 2 | 0xCF999539 | 54 | 13,498,253 | `LEVELS\JUNDR\JUNDR.TE_` |
| 3 | 0xEF199520 | 13,498,307 | 1,884,092 | `LEVELS\JUNDR\JUNDR.LMF` |

## Light map

131 stored LZO1X groups holding 20,335 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 1,041,973 | 12,076 | 57,059 | 102,859 | 5,725 |
| `ODF` | 107,552 | 516 | 1,574 | 13,044 | 106,447 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).
Field 21 counts 6,973 surface rows in section 2 ([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).

## Sounds

`JUNDRs.wsx` holds 292 entries: 292 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Scripts

The object stream has 7,766 records and the region stream has 195 records. Both counts are a walk of the MAP command bytes with the opcode sizes from the executable. The [script summary](notes/JUNDR.md) gives the same record counts with the event pools.

Opcode 0x15 byte +4 names `mshard2` (index 10, 1 command). Byte +5 is 0 on each of these commands. VA `0x447F97` passes byte +4 to VA `0x46FA60`, and VA `0x46FCF2` reads `[index*4 + 0x54A3D0]`, the 19 stems at file `0x148BD0`.
No framed command contains a music stem from the pointer table at file `0x148180`, or the hash of `MUSIC\<stem>.aud`.
No framed command contains another level stem, in either case, or the hash of that level's MAP name. So no exit in these two streams names its target level by stem or MAP hash; an exit by numeric index or another path is not ruled out.

## Related notes

- [Script summary](notes/JUNDR.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
