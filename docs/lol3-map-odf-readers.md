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

**CONFIRMED.** After those 8-byte rows are the same number of
26-byte NUL-terminated name slots, then 35 × u32(MAP+0xD8)
bytes. The exact partition is
`field1 - u32(+0xC8) = 34 * u32(+0xC4) + 35 * u32(+0xD8)`
in all 18 archives. There are 2,384 point and name rows and
36 final 35-byte records. In CKEEP, 15 points begin at
`CKEEP.WSX+0xCC592E`, 15 names at +0xCC59A6, and the
next section begins at +0xCC5B2C. Its count at MAP +0xD8
is zero.

**UNCONFIRMED.** The full roles of point offsets +4–+7 and
the readers for the two remaining spans are open. The 26-byte
slots all have a NUL. A provisional +4 region-index test
has exceptions, notably JUNDR, so a region interpretation
needs a native consumer. Follow the point's later word
loads after `0x4B4DA9`, and search for a reader whose
initial position starts after `8 * u32(+0xC4)` for the names
and after `34 * u32(+0xC4)` for the 35-byte rows.

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

### Type-tagged definitions in field 3 (creature reading UNCONFIRMED)

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
The meanings of untouched body bytes and consumers of the other
table fields remain **UNCONFIRMED**. The section-1 and section-3
subtables share reader `0x4FD560`. It assigns each 16-byte row
a pointer into the subsequent 12-byte array (`0x4FD5DC–0x4FD617`).
Follow that pointer into the first consumer to identify the subtable.
