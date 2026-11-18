# PWOD3

Made by `tools/lol3_level_report.py` from `DAT/PWOD3.WSX` and `DAT/PWOD3S.WSX`. Formats: [WSX](../formats/wsx.md), [LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).

## Level archive

`PWOD3.WSX` is 30,046,627 bytes with 4 entries. Each entry is named by the native name hash of `LEVELS\PWOD3\PWOD3.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).

| Entry | Key | File offset | Size | Name |
|---:|---|---:|---:|---|
| 0 | 0xD0B7D43A | 28,151,609 | 1,824,035 | `LEVELS\PWOD3\PWOD3.MAP` |
| 1 | 0xDCD7D430 | 29,975,644 | 70,983 | `LEVELS\PWOD3\PWOD3.ODF` |
| 2 | 0xE127D449 | 54 | 21,163,672 | `LEVELS\PWOD3\PWOD3.TE_` |
| 3 | 0x00A7D431 | 21,163,726 | 6,987,883 | `LEVELS\PWOD3\PWOD3.LMF` |

## Light map

562 stored LZO1X groups holding 39,851 light-map members (directory read; `walk_lmf_leaves.py --decode` checks every member).

## MAP and ODF headers

| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |
|---|---:|---:|---:|---:|---:|
| `MAP` | 1,824,035 | 12,076 | 103,547 | 253,899 | 18,794 |
| `ODF` | 70,983 | 516 | 3,322 | 18,942 | 67,750 |

For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).

## Sounds

`PWOD3S.WSX` holds 92 entries: 92 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Open

- What the level's scripts and objects do: no script reader is known yet ([dispatch search](../lol3-dispatch-search.md), Q11).
- MAP sections 0 and 2 and the ODF layout (Q4, Q5); what the renderer does with the light map (Q3).
