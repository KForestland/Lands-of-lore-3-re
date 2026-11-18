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
Field 21 counts 7,761 surface rows in section 2 ([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).

## Sounds

`FLAIRs.wsx` holds 384 entries: 384 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Scripts

The object stream has 5,718 records and the region stream has 697 records. Both counts are a walk of the MAP command bytes with the opcode sizes from the executable. The [script summary](notes/FLAIR.md) gives the same record counts with the event pools.

Opcode 0x15 byte +4 names `mfinale` (index 8, 1 command); `mcredits` (index 16, 1 command); `mepilog` (index 17, 1 command). Byte +5 is 0 on each of these commands. VA `0x447F97` passes byte +4 to VA `0x46FA60`, and VA `0x46FCF2` reads `[index*4 + 0x54A3D0]`, the 19 stems at file `0x148BD0`.
No framed command contains a music stem from the pointer table at file `0x148180`, or the hash of `MUSIC\<stem>.aud`.
No framed command contains another level stem, in either case, or the hash of that level's MAP name. So no exit in these two streams names its target level by stem or MAP hash; an exit by numeric index or another path is not ruled out.

## Related notes

- [Script summary](notes/FLAIR.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
