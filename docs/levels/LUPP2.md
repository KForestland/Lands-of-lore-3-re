# LUPP2

Made by `tools/lol3_level_report.py` from `DAT/LUPP2.WSX` and `DAT/LUPP2S.WSX`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`LUPP2.WSX` is 23,557,699 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\LUPP2\LUPP2.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0xE12B935D | 20,676,434 | 2,811,332 | `LEVELS\LUPP2\LUPP2.MAP` |
| 1 | 0xED4B9353 | 23,487,766 | 69,933 | `LEVELS\LUPP2\LUPP2.ODF` |
| 2 | 0xF19B936C | 54 | 19,226,111 | `LEVELS\LUPP2\LUPP2.TE_` |
| 3 | 0x111B9354 | 19,226,165 | 1,450,269 | `LEVELS\LUPP2\LUPP2.LMF` |

## Light map

152 stored LZO1X groups holding 19,879 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 2,811,332 | 12,076 | 67,307 | 144,163 | 9,607 |
| `ODF` | 69,933 | 516 | 3,644 | 17,922 | 68,964 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).

## Sounds

`LUPP2S.WSX` holds 92 entries: 92 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Open

- What the level's scripts and objects do: no script reader is known yet ([dispatch search](../lol3-dispatch-search.md), Q11).
- MAP sections 0 and 2 and the ODF layout (Q4, Q5); what the renderer does with the light map (Q3).
