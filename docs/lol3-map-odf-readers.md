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

**CONFIRMED (values). UNCONFIRMED (meaning).** Waypoint byte
+6 takes 15 values across the 2,384 rows: 0 (114), 1 (57),
2 (1,957), 4 (3), 6 (3), 10 (2), 12 (8), 15 (180), 23 (2),
31 (3), 37 (1), 46 (27), 78 (4), 125 (20) and 255 (3). The
largest pair with byte +7 is +6 = 2 and +7 = 4 (1,757 rows).
Six levels use only the value 2: CKEEP, ISHAT, JUNDR, MLOW2,
OLOW3 and QWOD0. The save record at `0x436077–0x43608C`
copies the table pointer and a byte length of count × 8, so
the saved image includes this byte. The other five absolute
uses of `0x5701A4` are `0x4B4D7E` (s16 +0, s16 +2, u16 +4),
`0x4B5B1E` (u16 +4, then s16 +0 and s16 +2), `0x4B8A38`
(stores the row pointer in `0x7D772C`; that global is read at
`0x4BDE92`/`0x4BDEAE` for +0 and +2 only, copied to object +0x1990
at `0x4F8F7C` and exported at `0x438E47`, so those paths are not
yet checked for +6), `0x4BCAD1` (s16 +0 and
s16 +2) and `0x4FD6C8` (u16 +4 and byte +7). A read of byte
+6 from one of those rows would name the field.

**CONFIRMED (on-disk text). UNCONFIRMED (reader).** The 2,384
name slots are 2,330 NUL-padded printable strings of length
3–25 (ten of them a plain `WayPoint` with NUL padding: BUPP1 5,
EWOD1 1, LUPP2 4), 39 copies of the eight characters `WayPoint` followed by
`0xCD` through byte 24 and a final 0, and 15 copies of one
26-byte record: `BadName`, a NUL, u32 0, three u32 values of 1
and a u16 0. The `WayPoint` slots are BUPP1 1, DLOW1 1, EWOD1 3,
FLAIR 2, HWHIT 1, KVOLC 21, LUPP2 1, NWOD2 3, PWOD3 3 and
SWOD4 3. One starts at `BUPP1.WSX+0x181EEA2`. The `BadName`
records are BUPP1 index 35 at `BUPP1.WSX+0x181E940`, FLAIR
indexes 1 and 3, and LUPP2 indexes 3, 5–14 and 35. 
The loader's waypoint read is 8 × the +0xC4 count and its path
read is 4 × the +0xD8 count, so both label spans sit outside
those reads. The 31-byte slots, 36 in all, are printable C
strings. Thirty-two are filled out with `0xCD`. `Vic` and `Sam`,
each in BUPP1 and again in LUPP2, have one extra NUL and then
`0xCD`. The first label starts at `BUPP1.WSX+0x181E90C`. There are 19
distinct labels: one occurs 13 times, five occur twice and 13 once.
The repository does not reproduce them (they are level-author
text); `lol3_map_spans.py --check` compares their counts and a
digest. The retail executable image contains neither `WayPoint`
nor `BadName`.
CKEEP, GRULO, ISHAT, MLOW2, OLOW3 and QWOD0 have a path count
of zero. A seek to header +0xC8 + 8 × count, or to header
+0xDC + 4 × count, would identify a reader.

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
**CONFIRMED (extent). UNCONFIRMED (consumer).** Between the
56-byte surface table and header +0x44 the archives hold
1,784 bytes in 223 groups of eight. The lengths are BUPP1 248,
CKEEP 104, DLOW1 304, EWOD1 56, FLAIR 80, HWHIT 152, JUNDR 16,
LUPP2 168, MLOW2 304, NWOD2 40, OLOW3 272 and PWOD3 40. GRULO,
ISHAT, KVOLC, QWOD0, RVOL0 and SWOD4 have length 0, so on those
six the start equals header +0x44. On the twelve nonempty
levels no header dword equals the start. The first CKEEP byte
is `CKEEP.WSX+0xD0368C`. Each group is four little-endian u16,
and every word is below that level's vertex count and below its
surface count. Read as surface indexes, 113 of the 223 groups
share no vertex between cyclic neighbors. The loader calls the
seek helper sixteen times in `0x43E884–0x43EC57`, and each call
pushes one stored header dword. The call at `0x43EA72–0x43EA79`
pushes `[esp+0x58]`. By the same three-push rule as the waypoint
seek at `0x43EBD9` (`[esp+0xDC]` is header +0xC8), that dword is
header +0x44, the first byte after this span. A seek to field 2
+ 56 × field 21 would identify the consumer.

**CONFIRMED (each byte is read or written). UNCONFIRMED (what
the bits mean).** The 167,942 section-1 rows are eight bytes,
and the loader copies all eight (`0x43EB7C–0x43EBA1`). Word +0
ranges from 1 to 65535 (935 distinct values; 213 are `0xFFFF`;
the value 0 does not occur). 165,745 of those words are below
both the vertex count and the surface count, and 1,984 of the non-`0xFFFF` words are at
or above both. Bytes +2 and +3 are written and copied as
separate bytes. Taken together as a little-endian word they
range from 0 to 65535. Bytes +4 and +5, taken the same way,
range from 10 to 8191. Byte +4 has 161 values and is 128 on
162,397 rows. Byte +5 masked with `0x1F` takes every value
0–31; the counts for 4, 5, 6 and 7 are 26,616, 32,254, 33,511
and 27,297. Byte +6 has 21 values; 16, 8 and 0 account for
83,014, 74,591 and 6,811 rows. Byte +7 has 128 values and is
0 on 160,071 rows.

| Bytes | Native use |
|---|---|
| +0, +1 | Word. Written from the caller's word +6 at `0x4E6425–0x4E6431`. Compared with zero at `0x4FFD69`. Sign-extended and used as an index at `0x4FFE05` and again at `0x4EFC01`; a negative index reads the table at `0x5701DC`. |
| +2 | Added or replaced from the caller's byte +7 (`0x4E6474`, `0x4E64CB`). Copied to the caller's object +0x30 at `0x4FFD91`. |
| +3 | Added or replaced the same way (`0x4E6493`, `0x4E64B2`). Copied to object +0x31 at `0x4FFD97`. |
| +4 | Replaced from the caller's byte +7 by switch arms 0 and 15 (`0x4E65CE`). Copied to object +0x40 at `0x4FFD9D`. |
| +5 | Low five bits select a row (`0x4A74E0–0x4A74E3`, `0x4EFE2C–0x4EFE32`). Bits `0x20`, `0x40` and `0x10` are tested at `0x4FFD61`, `0x4FFD89` and `0x50071A`. Switch arm 17 sets `0x20` (with `0x40`), arm 18 clears `0x20` and arm 19 toggles `0x20` (`0x4E6600`, `0x4E6611`, `0x4E6625`). Every arm of the switch ORs in bit `0x40`, and `0x4FFE00` clears that bit after the copy. |
| +6 | Switch arms 5–13 set, clear or toggle masks 4, `0x20` and `0x40` (`0x4E64E4–0x4E65CB`). The copy at `0x4FFDA3–0x4FFDED` tests masks `0x10`, 8, `0x20`, `0x40`, 4 and 1. `0x4FFD4B` sets ebx to 1, and `0x4FFDDF` ORs that 1 into the object word +0x3E when mask 4 is set. Bit `0x80` is passed to `0x4FFFB0` at `0x50072A–0x500737`. |
| +7 | Replaced from the caller's byte +7 by switch arms 14 and 16 (`0x4E65E7`). Zero-extended, shifted left 14 and ORed into the u16 object +0x3E at `0x4FFDF1–0x4FFDF9`, which keeps only its bits 0–1 although the byte takes 128 values, so another consumer may exist (**UNCONFIRMED**). |

The switch is `0x4E6450`. Its index is the caller's byte +6,
its operand is byte +7, and the row index is the caller's
word +4. The 20 targets are the dwords at `0x4E663C`. An index
above 19 returns 1 at `0x4E6631` and leaves the row unchanged.
The export at `0x438B80` reports the same table with stride 8.
`lol3_map_spans.py --check` re-counts the rows, the waypoint +6/+7 histograms, the
section-1 range and byte-value counts, the name classes, the
path-label counts and digest and the gap lengths above.

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

### Type tags and AI resources

**CONFIRMED.** The lookup at `0x4FDEF0` searches cached objects by
the original tag at runtime +0x2764. On a miss `0x4FD8F0`
copies that tag and formats `global\ai\%s` at
`0x4FD932–0x4FD963`. The next calls build the resources
`stat.csv`, `goals.csv`, `actions.csv` and `effector.csv`
(`0x4FD986–0x4FDA0D`; leaf strings at VAs `0x551BE4`,
`0x551BD8`, `0x551BCC`, `0x551BBC`). The lookup increments
the cached object's count at +0x2774 (`0x4FDF4E–0x4FDF56`).

**CONFIRMED.** The 18 original ODFs contain 334 field-3 rows and
68 distinct tags. Hashing the four paths against `GLOBAL.WSX`
joins all four for 60 tags, three for one, two for one and
zero for six. In QWOD0, the tag `SPIDER` starts at
`QWOD0.WSX+0x7781AB`. Its four resource payload starts in the
order above are `GLOBAL.WSX+0x1FDBA3`, `+0x1FBE73`,
`+0x1FB11F` and `+0x1FB568`. This establishes a use of the type
tag without assigning gameplay meaning to every tag.

**UNCONFIRMED.** The role of the 22-byte section-0 companions
and the missing leaf files remains open. For the former,
follow another read or a writer for the exact span, beginning
at `CKEEP.WSX` ODF entry +0x5DC. For the latter, follow the
failed resource branch from `0x420300 → 0x4FD780`, using a
missing input such as the tag `NONE`.
