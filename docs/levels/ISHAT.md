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
Field 21 counts 7,341 surface rows in section 2 ([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).

## Sounds

`ISHATs.wsx` holds 306 entries: 306 × format 17 (IMA ADPCM, mono, 22,050 Hz, 4-bit).

## Scripts

The object stream has 3,061 records and the region stream has 162 records. Both counts are a walk of the MAP command bytes with the opcode sizes from the executable. The [script summary](notes/ISHAT.md) gives the same record counts with the event pools.

Opcode 0x15 byte +4 names `mshard3` (index 11, 1 command). Byte +5 is 0 on each of these commands. VA `0x447F97` passes byte +4 to VA `0x46FA60`, and VA `0x46FCF2` reads `[index*4 + 0x54A3D0]`, the 19 stems at file `0x148BD0`.
No framed command contains a music stem from the pointer table at file `0x148180`, or the hash of `MUSIC\<stem>.aud`.
No framed command contains another level stem, in either case, or the hash of that level's MAP name. So no exit in these two streams names its target level by stem or MAP hash; an exit by numeric index or another path is not ruled out.

## Related notes

- [Script summary](notes/ISHAT.md) gives trigger and effect counts from the original MAP.
- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.
- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.
