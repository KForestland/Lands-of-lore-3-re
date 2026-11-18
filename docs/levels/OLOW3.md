# OLOW3

Made by `tools/lol3_level_report.py` from `DAT/olow3.wsx` and `DAT/OLOW3s.wsx`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`olow3.wsx` is 24,387,703 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\OLOW3\OLOW3.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0x8DCAC48B | 23,442,767 | 823,185 | `LEVELS\OLOW3\OLOW3.MAP` |
| 1 | 0x99EAC481 | 24,265,952 | 121,751 | `LEVELS\OLOW3\OLOW3.ODF` |
| 2 | 0x9E3AC49A | 54 | 21,327,256 | `LEVELS\OLOW3\OLOW3.TE_` |
| 3 | 0xBDBAC481 | 21,327,310 | 2,115,457 | `LEVELS\OLOW3\OLOW3.LMF` |

## Light map

228 stored LZO1X groups holding 24,263 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 823,185 | 12,076 | 56,542 | 121,526 | 8,123 |
| `ODF` | 121,751 | 516 | 2,356 | 13,413 | 119,030 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).
Field 21 counts 5,544 surface rows in section 2 ([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).

## Sounds

`OLOW3s.wsx` holds 576 entries: 576 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Related notes

- [Script summary](notes/OLOW3.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
