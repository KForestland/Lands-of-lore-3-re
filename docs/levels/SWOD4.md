# SWOD4

Made by `tools/lol3_level_report.py` from `DAT/swod4.wsx` and `DAT/SWOD4s.wsx`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`swod4.wsx` is 6,435,161 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\SWOD4\SWOD4.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0xD0BB054A | 5,929,418 | 497,535 | `LEVELS\SWOD4\SWOD4.MAP` |
| 1 | 0xDCDB0540 | 6,426,953 | 8,208 | `LEVELS\SWOD4\SWOD4.ODF` |
| 2 | 0xE12B0559 | 54 | 4,031,175 | `LEVELS\SWOD4\SWOD4.TE_` |
| 3 | 0x00AB0541 | 4,031,229 | 1,898,189 | `LEVELS\SWOD4\SWOD4.LMF` |

## Light map

165 stored LZO1X groups holding 10,232 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 497,535 | 12,076 | 38,746 | 77,882 | 4,892 |
| `ODF` | 8,208 | 516 | 1,022 | 3,990 | 7,495 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).

## Sounds

`SWOD4s.wsx` holds 33 entries: 33 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Open

- What the level's scripts and objects do: no script reader is known yet ([dispatch search](../lol3-dispatch-search.md), Q11).
- MAP sections 0 and 2 and the ODF layout (Q4, Q5); what the renderer does with the light map (Q3).
