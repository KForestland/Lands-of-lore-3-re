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

## Sounds

`JUNDRs.wsx` holds 292 entries: 292 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Open

- What the level's scripts and objects do: no script reader is known yet ([dispatch search](../lol3-dispatch-search.md), Q11).
- MAP sections 0 and 2 and the ODF layout (Q4, Q5); what the renderer does with the light map (Q3).
