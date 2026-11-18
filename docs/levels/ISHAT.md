# ISHAT

Made by `tools/lol3_level_report.py` from `DAT/ishat.wsx` and `DAT/ISHATs.wsx`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`ishat.wsx` is 15,968,698 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\ISHAT\ISHAT.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0x98A0873D | 14,967,948 | 930,151 | `LEVELS\ISHAT\ISHAT.MAP` |
| 1 | 0xA4C08733 | 15,898,099 | 70,599 | `LEVELS\ISHAT\ISHAT.ODF` |
| 2 | 0xA910874C | 54 | 12,018,923 | `LEVELS\ISHAT\ISHAT.TE_` |
| 3 | 0xC8908733 | 12,018,977 | 2,948,971 | `LEVELS\ISHAT\ISHAT.LMF` |

## Light map

283 stored LZO1X groups holding 20,890 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 930,151 | 12,076 | 72,302 | 136,014 | 7,964 |
| `ODF` | 70,599 | 516 | 1,436 | 15,650 | 69,638 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).

## Sounds

`ISHATs.wsx` holds 306 entries: 306 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Open

- What each script group does: the streams frame with the native size table ([script opcodes](../lol3-script-opcodes.md)), many command effects are open (Q11).
- MAP sections 0 and 2 and the ODF layout (Q4, Q5); what the renderer does with the light map (Q3).
