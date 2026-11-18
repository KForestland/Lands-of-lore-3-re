# FLAIR

Made by `tools/lol3_level_report.py` from `DAT/flair.wsx` and `DAT/FLAIRs.wsx`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`flair.wsx` is 23,448,012 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\FLAIR\FLAIR.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0x1FC1553F | 22,054,047 | 1,294,445 | `LEVELS\FLAIR\FLAIR.MAP` |
| 1 | 0x2BE15535 | 23,348,492 | 99,520 | `LEVELS\FLAIR\FLAIR.ODF` |
| 2 | 0x3031554E | 54 | 17,261,146 | `LEVELS\FLAIR\FLAIR.TE_` |
| 3 | 0x4FB15535 | 17,261,200 | 4,792,847 | `LEVELS\FLAIR\FLAIR.LMF` |

## Light map

378 stored LZO1X groups holding 32,624 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 1,294,445 | 12,076 | 93,557 | 189,421 | 11,983 |
| `ODF` | 99,520 | 516 | 2,678 | 13,114 | 97,463 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).

## Sounds

`FLAIRs.wsx` holds 384 entries: 384 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Open

- What the level's scripts and objects do: no script reader is known yet ([dispatch search](../lol3-dispatch-search.md), Q11).
- MAP sections 0 and 2 and the ODF layout (Q4, Q5); what the renderer does with the light map (Q3).
