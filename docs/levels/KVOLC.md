# KVOLC

Made by `tools/lol3_level_report.py` from `DAT/kvolc.wsx` and `DAT/KVOLCs.wsx`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`kvolc.wsx` is 23,325,526 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\KVOLC\KVOLC.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0xD06E955C | 22,163,146 | 1,108,084 | `LEVELS\KVOLC\KVOLC.MAP` |
| 1 | 0xDC8E9552 | 23,271,230 | 54,296 | `LEVELS\KVOLC\KVOLC.ODF` |
| 2 | 0xE0DE956B | 54 | 14,314,762 | `LEVELS\KVOLC\KVOLC.TE_` |
| 3 | 0x005E9553 | 14,314,816 | 7,848,330 | `LEVELS\KVOLC\KVOLC.LMF` |

## Light map

560 stored LZO1X groups holding 29,956 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 1,108,084 | 12,076 | 92,078 | 178,958 | 10,860 |
| `ODF` | 54,296 | 516 | 2,954 | 12,235 | 52,399 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).

## Sounds

`KVOLCs.wsx` holds 257 entries: 207 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit), 50 × format 17 (IMA ADPCM, stereo, 22,050 Hz, 4-bit).

## Open

- What the level's scripts and objects do: no script reader is known yet ([dispatch search](../lol3-dispatch-search.md), Q11).
- MAP sections 0 and 2 and the ODF layout (Q4, Q5); what the renderer does with the light map (Q3).
