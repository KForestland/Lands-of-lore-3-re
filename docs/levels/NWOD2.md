# NWOD2

Made by `tools/lol3_level_report.py` from `DAT/NWOD2.WSX` and `DAT/NWOD2S.WSX`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`NWOD2.WSX` is 30,304,516 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\NWOD2\NWOD2.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0xD0B5B32A | 28,458,798 | 1,776,030 | `LEVELS\NWOD2\NWOD2.MAP` |
| 1 | 0xDCD5B320 | 30,234,828 | 69,688 | `LEVELS\NWOD2\NWOD2.ODF` |
| 2 | 0xE125B339 | 54 | 21,516,899 | `LEVELS\NWOD2\NWOD2.TE_` |
| 3 | 0x00A5B321 | 21,516,953 | 6,941,845 | `LEVELS\NWOD2\NWOD2.LMF` |

## Light map

558 stored LZO1X groups holding 39,384 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 1,776,030 | 12,076 | 101,087 | 250,015 | 18,616 |
| `ODF` | 69,688 | 516 | 3,276 | 20,851 | 67,263 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).

## Sounds

`NWOD2S.WSX` holds 131 entries: 131 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Open

- What each script group does: the streams frame with the native size table ([script opcodes](../lol3-script-opcodes.md)), many command effects are open (Q11).
- MAP sections 0 and 2 and the ODF layout (Q4, Q5); what the renderer does with the light map (Q3).
