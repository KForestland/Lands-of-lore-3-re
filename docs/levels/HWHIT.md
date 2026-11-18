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

## Sounds

`HWHITs.wsx` holds 353 entries: 353 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Related notes

- [Script summary](notes/HWHIT.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
