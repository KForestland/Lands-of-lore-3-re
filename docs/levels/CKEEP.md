# CKEEP

Made by `tools/lol3_level_report.py` from `DAT/CKEEP.WSX` and `DAT/CKEEPS.WSX`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`CKEEP.WSX` is 13,900,854 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\CKEEP\CKEEP.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0x936A2304 | 12,685,444 | 663,806 | `LEVELS\CKEEP\CKEEP.LMF` |
| 1 | 0x637A230E | 13,349,250 | 503,908 | `LEVELS\CKEEP\CKEEP.MAP` |
| 2 | 0x6F9A2304 | 13,853,158 | 47,696 | `LEVELS\CKEEP\CKEEP.ODF` |
| 3 | 0x73EA231D | 54 | 12,685,390 | `LEVELS\CKEEP\CKEEP.TE_` |

## Light map

63 stored LZO1X groups holding 12,176 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 503,908 | 12,076 | 43,434 | 83,962 | 5,066 |
| `ODF` | 47,696 | 516 | 2,402 | 10,555 | 47,575 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).

## Sounds

`CKEEPS.WSX` holds 357 entries: 357 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Open

- What each script group does: the streams frame with the native size table ([script opcodes](../lol3-script-opcodes.md)), many command effects are open (Q11).
- MAP sections 0 and 2 and the ODF layout (Q4, Q5); what the renderer does with the light map (Q3).
