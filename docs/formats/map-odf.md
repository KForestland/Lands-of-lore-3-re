# MAP and ODF entries (table38 header)

**What:** besides the [LMF](lmf.md), every level archive holds two entries that begin with the same kind of header. The header starts with u32 38, a format tag that both native readers require, followed by fields that are mostly section offsets or counts. The MAP reader reads a 0x244-byte header and also requires a nonzero field 21 (`0x43E7E0–0x43E80B`); the ODF reader reads 0x204 bytes (`0x43FC86–0x43FCAB`). Both checks are bypassed by the `-CONVERT_TEST` switch. The MAP reader reads further dwords at +0xC4/+0xC8 and +0xD8/+0xDC (`0x43EBD9–0x43EC92`). The older pages call this header "table38".

The two kinds differ in field 0 and size. The executable's strings name the level file types `.map` and `.odf`. The resource keys and the [native loaders](../lol3-map-odf-readers.md) confirm which entry has each role.

| Kind | Field 0 | Size | Contents (older notes) |
|---|---:|---|---|
| MAP | 12,076 | 64,423 (RVOL0) to 3,413,407 bytes (BUPP1) | point runs, 8-byte records, a stream with `0xFFFF` markers ([map-format](../map-format.md)) |
| ODF | 516 | 4,010 (RVOL0) to 126,985 bytes (DLOW1) | named material, prop and spawn lists and placement records ([level catalog notes](../level-catalog-notes.md)) |

Measured on the 51 readable WSX files. CONFIRMED:
- **Count:** 18 MAP and 18 ODF entries, one of each per level archive, next to its LMF.
- **Field 0:** 12,076 in every MAP and 516 in every ODF.

## MAP sections

The [typed native table reads](../lol3-map-odf-readers.md#writing-the-stored-fields)
give the row layouts for surfaces, region descriptors, the +0x34 and
+0x30 tables and both event pools. The MAP writer reports each remaining
byte range with its file offset.

| Field | Meaning | Evidence |
|---|---|---|
| 0 | start of section 0 | CONFIRMED value (12,076 in all 18) |
| 1 | start of section 1 | CONFIRMED: in all 18 MAP entries, field 2 − field 1 = 8 × field 20 |
| 2 | start of section 2 | **CONFIRMED** resident surface table, `LOL3.DAT` VA `0x43EADF–0x43EB04` |
| 20 | number of 8-byte records in section 1 | **CONFIRMED** (same check) |
| 21 | number of 56-byte surface records in section 2 | **CONFIRMED** `LOL3.DAT` VA `0x43EAE6–0x43EAF7` |

**Section 0. CONFIRMED.** Field 19 counts eight-byte signed 16.16
X/Z pairs at field 0. A 34–8,399-byte tail follows the vertices
before field 1. The native +0xC8 seek binds its 8-byte waypoint rows (positions that creature paths step through, [readers](../lol3-map-odf-readers.md#tail-after-the-vertices)) and the file partitions into points, name slots and a final counted span. The first 4 bytes per path are a native path record. The loader's 23 seek/read paths skip the 26-byte name slots and the 31-byte path labels (**CONFIRMED**, [readers](../lol3-map-odf-readers.md#tail-after-the-vertices)). This explains the earlier
measurement that only 88% of the section's 8-byte slots look like points: 110,373 of 124,764 slots
have that shape, 108,043 of them whole-number vertices; the rest of the 114,483 vertices have a
fraction, and 2,330 point-like slots lie in the tails.
[Native readers](../lol3-map-odf-readers.md).

**Section 1. CONFIRMED.** Eight-byte rows referenced by contiguous ranges on individual surfaces. The native matcher tests row +5 low five bits (`0x4A74C0–0x4A74F7`). Every byte has a native reader or writer; what the bits mean is **UNCONFIRMED** ([section-1 bytes and settling test](../lol3-map-odf-readers.md#map-sections-1-and-2)). Rows with byte +5 bit `0x10` use bytes +2, +3, +4 and +7 as edge geometry (`0x500600`).

**Section 2. CONFIRMED.** Field-21 56-byte surfaces. Four neighbor indices, four vertex indices, waypoint height and the attached section-1 range are mapped in the [native reader](../lol3-map-odf-readers.md#map-sections-1-and-2).

## Worked example

`CKEEP.WSX` entry 1, the MAP: file offset 13,349,250, 503,908 bytes. It starts:

```
26 00 00 00   2c 2f 00 00   aa a9 00 00   fa 47 01 00   …
```

| Field | Value |
|---|---|
| format tag | 38 |
| field 0 | 12,076 |
| field 1 | 43,434 |
| field 2 | 83,962 |
| field 20 | 5,066 |

Check: 83,962 − 43,434 = 40,528 = 8 × 5,066.

The first vertices of section 0, read as 16.16 dwords, are X 1370, Z −5530 (bytes `00 00 5a 05`, `00 00 66 ea`), then X 1740, Z −5530 and X 930, Z −5520. The first records of section 1 read `(170, 0, 1920, 16)` and `(412, 0, 128, 16)`.

`CKEEP.WSX` entry 2 is the ODF: 47,696 bytes, starting `26 00 00 00 04 02 00 00`. That is format tag 38 and field 0 = 516 (the ODF header size).

## Overhead schematic

**CONFIRMED.** The [QWOD0 drawing](../images/qwod0-schematic.svg) (made by `python3 tools/lol3_level_schematic.py QWOD0 --data DAT --out docs/images/qwod0-schematic.svg`; `--check` confirms it regenerates byte-identical)
uses the 1,308 vertices and 1,430 surface rows from
`QWOD0.WSX+0x72E28B`. The vertices begin at +0x7311B7.
The surface rows begin at +0x7384B9. The native loader selects
these tables at `0x43EAB2–0x43EB04`, and the geometry helper
reads the four u16 vertex indices at `0x4A7500–0x4A7566`.

The drawing projects the stored X/Z coordinates with the same scale
on both axes. It joins each surface's consecutive corner positions,
including the closing edge, and discards edges of zero length.
Edges used by multiple surfaces are pale. The colour measures
edge reuse in the projection. Hollow squares are waypoints and
dashed lines are paths. Dots are the rows of the five placement
tables (type 3, type 16, creature, mover, item), one number
series per table, numbered from 1 (row 0 is drawn as 1); the
legend under the plan names them. The scale fits the surface
edges only: waypoints and placements outside their bounding box
are not drawn and are counted in the footer (SWOD4: 162 of 188
waypoints), and a number that would overlap one already drawn is
left out and counted (`--no-labels` draws none). Heights and
collision are outside the drawing. Large levels give SVGs over
the repository's 300 KB file limit (BUPP1 about 650 KB), so
write those outside the repository.

The placement tables are read as the MAP loader reads them. It
seeks to each header offset at `0x43EEB6–0x43EF6F` and calls the
five loaders in this order:

| Table | Header offset / count | Loader, row read | Row bytes |
|---|---|---|---:|
| type 3 | +0x14 / +0x60 | `0x44FCD0`, `0x44FCEB` | 0x25 (37) |
| type 16 | +0x18 / +0x64 | `0x469980`, `0x4699A2` | 0x21 (33) |
| creature (type 2) | +0x1C / +0x68 | `0x4B44F0`, `0x4B4553` | 0x38 (56) |
| mover (type 32) | +0x24 / +0x70 | `0x4D59F0`, `0x4D5A1C` | 0x29 (41) |
| item (type 4) | +0x20 / +0x6C | `0x4D7480`, `0x4D74AC` | 0x25 (37) |

Each row reaches the shared object constructor `0x4411F0` (the
mover through `0x4D58F0 → 0x4698D0`), which sign-extends the
row's s16 at +0 and +2, shifts each left 16 and stores them as
object +4 (X) and +8 (Z) (`0x4411FB–0x441212`). The drawing uses
those two values. See [the native surface fields](../lol3-map-odf-readers.md#map-sections-1-and-2)
and [the waypoint and path rows](../lol3-map-odf-readers.md#tail-after-the-vertices).

```bash
python3 tools/lol3_level_schematic.py --data DAT QWOD0 --out ../qwod0.svg
```

## Open ([Q4](../OPEN_QUESTIONS.md), [Q5](../OPEN_QUESTIONS.md))

- The remaining MAP surface and section-1 bit meanings, the authoring code for the label spans and a typed consumer for the gap before field 16. Waypoint byte +6 enters predicate 41's distance limit at `0x4BDED6–0x4BDEE9`.
- The header fields not yet bound by the [native readers](../lol3-map-odf-readers.md) (MAP fields 19–21 and ODF fields 0–4 and 14–20 are bound).
- The ODF per-row meanings, a reader of the 22-byte section-0 names, and what follows the field-2 252-byte rows.
