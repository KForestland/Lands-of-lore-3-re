# MAP and ODF entries (table38 header)

**What:** besides the [LMF](lmf.md), every level archive holds two entries that begin with the same kind of header. The header is a u32 38 and then 38 u32 fields, most of them section offsets or counts; the older pages call it "table38".

The two kinds differ in field 0 and size. The executable's strings name the level file types `.map` and `.odf`. The resource keys and the [native loaders](../lol3-map-odf-readers.md) confirm which entry has each role.

| Kind | Field 0 | Size | Contents (older notes) |
|---|---:|---|---|
| MAP | 12,076 | large, 0.5–3.4 MB | point runs, 8-byte records, a stream with `0xFFFF` markers ([map-format](../map-format.md)) |
| ODF | 516 | small, 47–127 KB | named material, prop and spawn lists and placement records ([level catalog notes](../level-catalog-notes.md)) |

Re-run 2026-11-18 on the 51 readable WSX files. CONFIRMED:
- **Count:** 18 MAP and 18 ODF entries, one of each per level archive, next to its LMF.
- **Field 0:** 12,076 in every MAP and 516 in every ODF.

## MAP sections

| Field | Meaning | Evidence |
|---|---|---|
| 0 | start of section 0 | CONFIRMED value (12,076 in all 18) |
| 1 | start of section 1 | CONFIRMED: in all 18 MAP entries, field 2 − field 1 = 8 × field 20 |
| 2 | start of section 2 | as above |
| 20 | number of 8-byte records in section 1 | CONFIRMED (same check) |

**Section 0. CONFIRMED.** Field 19 counts eight-byte signed 16.16
X/Z pairs at field 0. A 34–8,399-byte tail follows the vertices
before field 1. The native +0xC8 seek binds its 8-byte waypoint rows and the file partitions into points, name slots and a final counted span. The final record roles are **UNCONFIRMED**. This explains the earlier
measurement that only 88% of the section's 8-byte slots look like points: 110,373 of 124,764 slots
have that shape, 108,043 of them whole-number vertices; the rest of the 114,483 vertices have a
fraction, and 2,330 point-like slots lie in the tails.
[Native readers](../lol3-map-odf-readers.md).

**Section 1.** 8-byte records. The older notes report that the last u16 is often 16 and the third clusters on multiples of 128. Their meaning is open.

**Section 2.** A stream with frequent `0xFFFF` words; layout open.

## Worked example

`CKEEP.WSX` entry 1, the MAP: file offset 13,349,250, 503,908 bytes. It starts:

```
26 00 00 00   2c 2f 00 00   aa a9 00 00   fa 47 01 00   …
```

| Field | Value |
|---|---|
| count | 38 |
| field 0 | 12,076 |
| field 1 | 43,434 |
| field 2 | 83,962 |
| field 20 | 5,066 |

Check: 83,962 − 43,434 = 40,528 = 8 × 5,066.

The first vertices of section 0, read as 16.16 dwords, are X 1370, Z −5530 (bytes `00 00 5a 05`, `00 00 66 ea`), then X 1740, Z −5530 and X 930, Z −5520. The first records of section 1 read `(170, 0, 1920, 16)` and `(412, 0, 128, 16)`.

`CKEEP.WSX` entry 2 is the ODF: 47,696 bytes, starting `26 00 00 00 04 02 00 00`. That is count 38 and field 0 = 516.

## Open ([Q4](../OPEN_QUESTIONS.md), [Q5](../OPEN_QUESTIONS.md))

- The remaining fields of the MAP waypoint tail, section 2 and the meaning of the section-1 fields.
- The header fields not yet bound by the [native readers](../lol3-map-odf-readers.md) (MAP field 19 and ODF fields 0–4 and 14–20 are bound).
- The ODF per-row meanings, the section-0 companions and what follows the field-2 252-byte rows.
