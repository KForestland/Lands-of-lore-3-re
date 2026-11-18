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

## Sounds

`GRULOs.wsx` holds 131 entries: 131 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Related notes

- [Script summary](notes/GRULO.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
