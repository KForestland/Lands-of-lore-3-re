# RVOL0

Made by `tools/lol3_level_report.py` from `DAT/rvol0.wsx` and `DAT/RVOL0s.wsx`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`rvol0.wsx` is 2,336,324 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\RVOL0\RVOL0.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0xD075F12C | 2,267,891 | 64,423 | `LEVELS\RVOL0\RVOL0.MAP` |
| 1 | 0xDC95F122 | 2,332,314 | 4,010 | `LEVELS\RVOL0\RVOL0.ODF` |
| 2 | 0xE0E5F13B | 54 | 2,007,878 | `LEVELS\RVOL0\RVOL0.TE_` |
| 3 | 0x0065F123 | 2,007,932 | 259,959 | `LEVELS\RVOL0\RVOL0.LMF` |

## Light map

16 stored LZO1X groups holding 1,220 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 64,423 | 12,076 | 15,423 | 19,815 | 549 |
| `ODF` | 4,010 | 516 | 700 | 2,486 | 3,665 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).

## Sounds

`RVOL0s.wsx` holds 208 entries: 158 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit), 50 × format 17 (IMA ADPCM, stereo, 22,050 Hz, 4-bit).

## Open

- What each script group does: the streams frame with the native size table ([script opcodes](../lol3-script-opcodes.md)), many command effects are open (Q11).
- MAP sections 0 and 2 and the ODF layout (Q4, Q5); what the renderer does with the light map (Q3).
