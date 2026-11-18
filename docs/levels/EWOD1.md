# EWOD1

Made by `tools/lol3_level_report.py` from `DAT/EWOD1.WSX` and `DAT/EWOD1S.WSX`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`EWOD1.WSX` is 26,770,728 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\EWOD1\EWOD1.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0xD0AC221A | 24,890,106 | 1,825,978 | `LEVELS\EWOD1\EWOD1.MAP` |
| 1 | 0xDCCC2210 | 26,716,084 | 54,644 | `LEVELS\EWOD1\EWOD1.ODF` |
| 2 | 0xE11C2229 | 54 | 18,087,754 | `LEVELS\EWOD1\EWOD1.TE_` |
| 3 | 0x009C2211 | 18,087,808 | 6,802,298 | `LEVELS\EWOD1\EWOD1.LMF` |

## Light map

569 stored LZO1X groups holding 40,084 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 1,825,978 | 12,076 | 99,924 | 248,372 | 18,556 |
| `ODF` | 54,644 | 516 | 2,770 | 17,791 | 52,987 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).
Field 21 counts 11,160 surface rows in section 2 ([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).

## Sounds

`EWOD1S.WSX` holds 199 entries: 199 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Related notes

- [Script summary](notes/EWOD1.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
