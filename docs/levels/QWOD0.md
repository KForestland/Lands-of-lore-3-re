# QWOD0

Made by `tools/lol3_level_report.py` from `DAT/QWOD0.WSX` and `DAT/QWOD0S.WSX`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`QWOD0.WSX` is 7,832,695 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\QWOD0\QWOD0.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0xD0B8E10A | 7,529,099 | 289,385 | `LEVELS\QWOD0\QWOD0.MAP` |
| 1 | 0xDCD8E100 | 7,818,484 | 14,211 | `LEVELS\QWOD0\QWOD0.ODF` |
| 2 | 0xE128E119 | 54 | 6,871,261 | `LEVELS\QWOD0\QWOD0.TE_` |
| 3 | 0x00A8E101 | 6,871,315 | 657,784 | `LEVELS\QWOD0\QWOD0.LMF` |

## Light map

49 stored LZO1X groups holding 5,364 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 289,385 | 12,076 | 22,574 | 41,518 | 2,368 |
| `ODF` | 14,211 | 516 | 1,298 | 6,138 | 13,762 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).
Field 21 counts 1,430 surface rows in section 2 ([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).

## Sounds

`QWOD0S.WSX` holds 26 entries: 26 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Related notes

- [Script summary](notes/QWOD0.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
