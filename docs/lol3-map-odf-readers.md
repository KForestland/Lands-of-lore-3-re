# Native MAP and ODF readers

VAs are for the English retail [LOL3.DAT image](lol3-lmf-reader.md).
Header fields are numbered from zero after the leading u32 38.

## MAP section 0

**CONFIRMED.** The `.map` suffix at `LOL3.DAT+0x147F6C` reaches
loader `0x43E6B0` at `0x43E304`. It reads 0x244 header bytes
at `0x43E7E7`. At `0x43EAB2–0x43EACA`, field 0 (header +4)
is the seek offset and field 19 (header +0x50) is the count.
`0x4F01E0` allocates 4+8*count bytes, prepends the count in memory and
reads exactly 8*count bytes from the file (`0x4F01EE–0x4F0218`).
The first row pointer is stored at world +0x1C (`0x43EAD7`), which
is cell `0x57018C` for world `0x570170` (`0x4369BD`).

| Row offset | Field | Native evidence |
|---|---|---|
| +0 | Signed 16.16 X | `0x4F0126–0x4F0137` indexes by a u16 endpoint and copies this dword into the first coordinate of an XYZ point. `0x4432F2–0x4432FE` shifts it right 16 arithmetically. |
| +4 | Signed 16.16 Z | `0x4F0139–0x4F0141` copies this dword to the third coordinate, with height separately assigned at `0x4F0106–0x4F0123`. `0x4432F5–0x443301` uses the same shift. |

**CONFIRMED.** The CKEEP MAP starts at `CKEEP.WSX+0xCBB182`.
Field 0 is 0x2F2C, count is 0xF10 and the first row at +0xCBE0AE
gives X 1370 and Z −5530. The read ends at MAP +0xA7AC and field 1
starts at +0xA9AA. All 18 hashed MAP entries have a 34–8,399-byte
gap between the counted vertices and field 1. Among 114,483 vertices,
6,440 have a nonzero fractional halfword in at least one coordinate.

### Tail after the vertices

**CONFIRMED.** All 18 MAP headers at +0xC8 give exactly field 0
plus 8 × field 19. Native `0x43EBD9–0x43EBF4` seeks to +0xC8
and reads the +0xC4 count. It allocates 4 + 8 × count, prepends
a live count and reads the rows into world +0x34
(`0x43EBF9–0x43EC45`). Mode 0/12 creature behavior obtains an
8-byte row from that table using actor u16 +0xD4. It takes signed
s16 +0/+2 as X/Z and shifts each left 16
(`0x4B4D7E–0x4B4DA9`).

These 8-byte rows are **waypoints**: the path consumer at
`0x4B5AF8–0x4B5B5E` takes the path base `[0x5701A8]` plus
|actor +0xF9|, copies the row's X/Z to actor +0x94/+0x98, then
advances the index with loop or ping-pong (`0x4B5B95–0x4B5BCF`).
A **surface** is a 56-byte row of section 2 (below).

**CONFIRMED.** After those 8-byte rows are the same number of
26-byte NUL-terminated name slots, then 35 × u32(MAP+0xD8)
bytes. The exact partition is
`field1 - u32(+0xC8) = 34 * u32(+0xC4) + 35 * u32(+0xD8)`
in all 18 archives. There are 2,384 point and name rows and
36 final 35-byte records. In CKEEP, 15 points begin at
`CKEEP.WSX+0xCC592E`, 15 names at +0xCC59A6, and the
next section begins at +0xCC5B2C. Its count at MAP +0xD8
is zero.

**CONFIRMED.** Waypoint u16 +4 is the surface index into world
+0x24, the 56-byte table below. For `0xFFFF` the creature uses
zero for its height and takes the out-of-range branch. For a valid
index it reads signed surface +0x18 as the waypoint height, shifted
left 16, and sets the selected surface pointer
(`0x4B4DAD–0x4B4DF7, 0x4B4E7E–0x4B4EA6`). All 2,186
non-sentinel indices fit field 21, including JUNDR's first
waypoint +4 = 6,867, which exceeds its field-20 count 5,725
(`JUNDR.WSX+0xEB88B3`). The other 198 use `0xFFFF`.
CKEEP's first waypoint is (188, −495) at `CKEEP.WSX+0xCC592E`;
its surface 3,242 is the row at `+0xCFBEAC`, with height 0 at
`+0xCFBEC4` (surface +0x18).

**CONFIRMED.** Waypoint byte +7 filters the nearest-point
search. The search skips an absent surface, requires at least one
shared bit between caller mask and byte +7, and skips surfaces
with byte +4 bit 1 set. It keeps the point with the lowest integer
X/Z Euclidean distance (`0x4FD6C0–0x4FD751`,
`0x44AAB0–0x44AADF`). Across the same 2,384 waypoint rows,
the byte has values 0, 4 and 5 with counts 304, 2,067 and 13.

**CONFIRMED.** The last span starts at the offset in header
+0xDC. Native `0x43EC4D–0x43EC92` reads +0xD8 × 4 bytes
from there to world +0x38. Each four-byte path record supplies
a base u16 waypoint index, a byte count and a flag byte. The
creature indexes the path by its +0xF8 byte and uses
base + abs(signed actor +0xF9) for the point
(`0x4B5AF8–0x4B5B5E`). At the upper end, path +3 bit 0
resets the actor index to zero when set. Otherwise the engine
sets it to `2 − count`, reversing traversal through the absolute
value on the next lookup (`0x4B5B95–0x4B5BCF`). The 36
path ranges all fit their waypoint table. The first two
BUPP1 path rows at `BUPP1.WSX+0x181E8E0, +0x181E8E4`
are (0, 4, 1) and (4, 11, 0).

**UNCONFIRMED.** Waypoint byte +6 and the consumers of the
26-byte name slots remain open. The low byte of the last
waypoint word has 15 values in the original corpus. None of
the six direct references to world +0x34 established a use for
it. The space after the four-byte path records partitions into
36 31-byte slots across the 18 MAPs, each with an early NUL.
For example, they start at `BUPP1.WSX+0x181E90C` and
end at field 1. These remaining bytes may be editor metadata.
A native reader starting at each of those spans, or a file
writer that identifies their serialized fields, would settle them.

## MAP sections 1 and 2

**CONFIRMED.** Field 1 (header +0x08) points to field-20
eight-byte rows, copied to world +0x20 by
`0x43EB7C–0x43EBA1 → 0x4EFDC0`. Field 2 (header +0x0C)
points to field-21 56-byte surface rows. The loader reads the
rows to world +0x24 (`0x43EADF–0x43EB04 → 0x4A65F0`).
It stores field 21 at world +0x44 (`0x5701B4`), the count
tested against waypoints above. The surface reader then
initializes live bytes +0x24–+0x27 and +0x2D and applies a
type-specific rule to +0x2C
(`0x4A6653–0x4A66DF`, dispatch `0x4A671C`).

| Surface offset | Confirmed field or consumer |
|---|---|
| +0x08–+0x0F | Four u16 neighboring surface indices. The neighbor search compares the target surface index, stops a chain on `0xFFFF` and can move to the next 56-byte row when +0x35 is set (`0x4A67D0–0x4A685A`). |
| +0x10–+0x17 | Four u16 vertex indices into world +0x1C. The geometry helper walks the four vertices and computes X/Z coordinate bounds (`0x4A7500–0x4A7566`). |
| +0x18 | Signed height read alongside the waypoint's X/Z (`0x4B4DD2–0x4B4DDA`). |
| +0x1E, +0x32 | Start u16 and count u8 in the section-1 table. Lookup checks each row's byte +5 masked with `0x1F` against the requested selector, returning the first match (`0x4A74C0–0x4A74F7`). |

**CONFIRMED.** All 118,951 surfaces in the 18 MAP entries
have in-bounds vertices and either in-bounds neighbors or
the sentinel. All 85,221 attached section-1 spans are in
range. The remaining 33,730 have count 0 and index `0xFFFF`.
For example, `CKEEP.WSX+0xCCF97C` starts the first
surface with vertices 334, 376, 377 and 335. Its section-1
span starts at 0 with count 2, at `CKEEP.WSX+0xCC5B2C`.
The remaining section-1 fields and the additional 0–304 bytes
between the surface table end and field 16 are **UNCONFIRMED**.
The first CKEEP byte of that span is `CKEEP.WSX+0xD0368C`.
The measured spans are multiples of eight. A load or seek
between the 56-byte surface read and the field-16 reader
would identify their consumer.

## ODF header and primary tables

**CONFIRMED.** The `.odf` suffix at `LOL3.DAT+0x147F74` reaches
`0x43FC40` via `0x43E246`. The 0x204-byte header read is at
`0x43FC8D`. All 18 ODF hashes match. CKEEP's entry starts at
`CKEEP.WSX+0xD361E6`.

| Offset field | Count or size field | Native reader |
|---:|---:|---|
| 0 | 14 | `0x43FCD6 → 0x4AB420` reads count × 24 bytes (`0x4AB42E–0x4AB44F`) into world +0x5C. These rows feed the timed update at `0x4AB480`. |
| 1 | 15 | `0x43FD45 → 0x4B3B50` reads count × 55 bytes and then a subtable through `0x4FD560`. The reader stores a pointer at each runtime row +0x14 and advances it by 16 times u8 row +0x2E (`0x4B3BF6–0x4B3C17`). |
| 2 | 16 | `0x43FD76 → 0x4F1440` reads count × 60 bytes, then reads a following dword count and passes it to a reader of 252-byte rows (`0x4F14A4–0x4F14C2`, `0x4EED88–0x4EEDB5`). |
| 3 | 17 | `0x43FDE2 → 0x4F0CE0` reads count × 147 bytes as 135-byte bodies and 12-byte type tags. A counted subtable follows (`0x4F0E9A`). |
| 4 | 18 | `0x43FDA7–0x43FDC8` loads exactly field 18 bytes into `[0x7E3200]`. |
| 20 | 19 | `0x43FD09–0x43FD22` loads count × 8 bytes into world +0x70. All 18 entries contain one byte of varying value after that computed end. |

**CONFIRMED.** In all 18 entries, 22 bytes per section-0 row follow
the counted 24-byte rows before section 1. CKEEP's first companion
begins at entry +0x5DC with a NUL-terminated identifier and padding.
The companion reader is **UNCONFIRMED**. Section 4 ends at the
start of section 3 in all 18 entries.

### Creature definitions in field 3

| Disk offset | Native operation |
|---|---|
| +0x00–+0x86 | Read as 135 bytes (`0x4F0D7C–0x4F0D86`). |
| +0x87–+0x92 | Read 12 bytes into scratch. `0x4FDEF0` resolves the type and stores a runtime pointer at +0x87 (`0x4F0D8E–0x4F0DB0`). |
| +0x37 | Dword rebased against the section-4 buffer (`0x4F0DB3–0x4F0DC2`). |
| +0x4B, +0x4D | Runtime words initialized to 50 and 190 (`0x4F0DCB–0x4F0DD1`). |
| +0x51, +0x53, +0x55, +0x57, +0x59, +0x5B | Unsigned pairs. Save their maximum pair sum to runtime +0x6D (`0x4F0E26–0x4F0E5C`). Separately save the maximum of +0x55 and +0x59 scaled by 7/8 to +0x6B (`0x4F0DBE–0x4F0DF2`). |
| +0x61 | Increase the word by 128. Its signed value participates in the threshold stored at +0x69 (`0x4F0DB8`, `0x4F0DE6–0x4F0E22`). |
| +0x81, +0x82 | Set runtime +0x82 to `max(1, floor(u8(+0x81)/10))` (`0x4F0E60–0x4F0E7B`). |

**CONFIRMED.** The first CKEEP creature record starts at
`CKEEP.WSX+0xD40705`, in the eight-row table. Its words +0x59/+0x5B
are 750 and 500. The runtime stride is 139 (`0x4F0E83`).
The [combat reader](lol3-combat-dispatch.md) traces the creature
consumers, including HP and behavior. Unused definition
bytes remain **UNCONFIRMED**. The section-1 and section-3
subtables share reader `0x4FD560`. It assigns each 16-byte row
a pointer into the subsequent 12-byte array (`0x4FD5DC–0x4FD617`).
Follow that pointer into the first consumer to identify the subtable.
