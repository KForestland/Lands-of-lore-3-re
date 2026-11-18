# MLOW2

Made by `tools/lol3_level_report.py` from `DAT/mlow2.wsx` and `DAT/MLOW2s.wsx`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`mlow2.wsx` is 22,309,533 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\MLOW2\MLOW2.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0x8DC8A37B | 21,380,707 | 811,406 | `LEVELS\MLOW2\MLOW2.MAP` |
| 1 | 0x99E8A371 | 22,192,113 | 117,420 | `LEVELS\MLOW2\MLOW2.ODF` |
| 2 | 0x9E38A38A | 54 | 19,285,704 | `LEVELS\MLOW2\MLOW2.TE_` |
| 3 | 0xBDB8A371 | 19,285,758 | 2,094,949 | `LEVELS\MLOW2\MLOW2.LMF` |

## Light map

232 stored LZO1X groups holding 24,920 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 811,406 | 12,076 | 56,764 | 122,316 | 8,194 |
| `ODF` | 117,420 | 516 | 1,712 | 11,317 | 115,963 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).

## Sounds

`MLOW2s.wsx` holds 668 entries: 668 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Open

- What each script group does: the streams frame with the native size table ([script opcodes](../lol3-script-opcodes.md)), many command effects are open (Q11).
- MAP sections 0 and 2 and the ODF layout (Q4, Q5); what the renderer does with the light map (Q3).
