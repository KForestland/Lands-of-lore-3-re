# DLOW1

Made by `tools/lol3_level_report.py` from `DAT/dlow1.wsx` and `DAT/DLOW1s.wsx`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`dlow1.wsx` is 22,791,662 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\DLOW1\DLOW1.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0x8DBF126B | 21,845,042 | 819,635 | `LEVELS\DLOW1\DLOW1.MAP` |
| 1 | 0x99DF1261 | 22,664,677 | 126,985 | `LEVELS\DLOW1\DLOW1.ODF` |
| 2 | 0x9E2F127A | 54 | 19,749,463 | `LEVELS\DLOW1\DLOW1.TE_` |
| 3 | 0xBDAF1261 | 19,749,517 | 2,095,525 | `LEVELS\DLOW1\DLOW1.LMF` |

## Light map

232 stored LZO1X groups holding 24,920 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 819,635 | 12,076 | 55,435 | 119,963 | 8,066 |
| `ODF` | 126,985 | 516 | 1,666 | 9,169 | 125,680 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).
Field 21 counts 5,422 surface rows in section 2 ([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).

## Sounds

`DLOW1s.wsx` holds 907 entries: 907 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Related notes

- [Script summary](notes/DLOW1.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
