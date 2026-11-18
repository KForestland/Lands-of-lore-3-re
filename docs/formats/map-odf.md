# MAP and ODF entries (table38 header)

**What:** besides the [LMF](lmf.md), every level archive holds two entries that begin with the same kind of header. The header is a u32 38 and then 38 u32 fields, most of them section offsets or counts; the older pages call it "table38".

The two kinds differ in field 0 and size. The executable's strings name the level file types `.map` and `.odf`. Their link to these two entries is a working reading from the older notes ([level file types](../level-file-types.md)), UNCONFIRMED.

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

**Section 0.** 88% of its 8-byte slots (110,373 of 124,764 over the 18 levels) have the form `(u16 0, i16 x, u16 0, i16 z)`. In 16 of the 18 levels the section length is not a multiple of 8. So it is not purely a run of point records; its exact layout is open.

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

The first records of section 0 read `(0, 1370, 0, −5530)`, `(0, 1740, 0, −5530)` and `(0, 930, 0, −5520)`. The first records of section 1 read `(170, 0, 1920, 16)` and `(412, 0, 128, 16)`.

`CKEEP.WSX` entry 2 is the ODF: 47,696 bytes, starting `26 00 00 00 04 02 00 00`. That is count 38 and field 0 = 516.

## Open ([Q4](../OPEN_QUESTIONS.md), [Q5](../OPEN_QUESTIONS.md))

- The exact layout of MAP sections 0 and 2, and the meaning of the section-1 fields.
- The other 35 header fields.
- The ODF section layout and the placement record format.
- Which executable routines read these entries. That would also settle which entry is the `.map` and which the `.odf`.
