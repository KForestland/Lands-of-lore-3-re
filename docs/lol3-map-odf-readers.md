# Native MAP and ODF readers

VAs are for the English retail [LOL3.DAT image](lol3-lmf-reader.md).
Header fields are numbered from zero after the leading u32 38.

## Shared block before the vertices

**CONFIRMED.** In all 18 MAPs, header +0xCC is `0x244` and header +0x04
is `0x2F2C`. The enclosed 11,496 bytes are identical across all levels.
In `QWOD0.WSX` the block starts at +0x72E4CF and the vertices at +0x7311B7.
The first u32 is `0xB39` (2,873), and the remaining span fits exactly
2,873 four-byte rows. The two `C5 A5` hits at +0x730744 and +0x730748
start at byte 1 of zero-based rows 2,204 and 2,205 under that framing.

**CONFIRMED.** The retail `.map` loader at `0x43E6B0` reads exactly
0x244 bytes into stack +0x14 (`0x43E7DA–0x43E7EF`). Its first further
read at `0x43E89A` follows a seek to header +0x28 (`0x43E87B–0x43E884`).
All 22 direct calls to the MAP seek helper `0x435A90`, and one nested
seek at `0x4EFE96` inside `0x4EFE40` (called at `0x43EB67`) to header
+0x30, take header offsets at or beyond the vertices on all 18 maps.
These are the direct call sites and header offsets in execution order.

| Seek calls | Header offsets, in the same order |
|---|---|
| `0x43E884`, `0x43E927`, `0x43E953`, `0x43E97D`, `0x43E9BD`, `0x43E9FD`, `0x43EA3D`, `0x43EA79` | `+28`, `+B4`, `+BC`, `+38`, `+3C`, `+40`, `+4C`, `+44` |
| `0x43EAB9`, `0x43EAE6`, `0x43EB16`, `0x43EB46`, `0x43EB83`, `0x43EBB0`, `0x43EBE3`, `0x43EC57` | `+04`, `+0C`, `+A4`, `+34`, `+08`, `+2C`, `+C8`, `+DC` |
| `0x43EEB6`, `0x43EEE0`, `0x43EF0A`, `0x43EF34`, `0x43EF5E`, `0x43EF9A` | `+14`, `+18`, `+1C`, `+24`, `+20`, `+48` |

**CONFIRMED.** The `.map` suffix is referenced only by the instruction
at `0x43E293`, which leads to `0x43E304`, the only caller of the retail
loader above. An exact 24-byte prefix and suffix search of the original
`DAT` directory and `LOL3.DAT` finds this block only inside the 18 MAPs.

**CONFIRMED.** The conversion option `-CONVERT_TEST` (`LOL3.DAT+0x147FAC`)
is looked up at `0x43E7F4` after the MAP header read. A match branches to
`0x43E825`. With the option absent, the same address is reached only
when the header begins with 38 and the surface count at +0x58 is
nonzero (`0x43E7FC–0x43E822`). Both accepted cases continue with the
same handle and header to the seek at `0x43E884`. The other five
operands referencing this option are at `0x43F742`, `0x43FC96`,
`0x44051B`, `0x440608` and `0x440BCE`, in the level texture, level ODF,
shared definition and light-map loaders.

**CONFIRMED.** Editor flag byte `[0x5D5380]` changes two table sizes
(entries at `0x5838B0` and `0x589768`) before the MAP header read. Zero
gives 200 and 300. A nonzero flag gives 100 and 200 (`0x43E6E0–0x43E6F5`, `0x43E73B–0x43E74D`).
Both values use the same MAP open and read at `0x43E7D2` and `0x43E7E7`.
The flag also selects `c:\leved\` shared bank paths at
`0x43FFE4–0x44000D` and disables cache-name resolution at
`0x4E4599–0x4E45A0 → 0x4E4AF3`; the resource wrapper then uses the
supplied path at `0x4356D3–0x4356DB`. The separate `-LEVED` string at
`LOL3.DAT+0x144608` has one direct code reference, the check at
`0x40E84C–0x40E85B`. These branches add no MAP reads in the loader above. In editor mode the
MAP is opened from the supplied plain path, so the seek sites are the
same but the 18-map byte check below covers the shipped archive entries,
not an editor-side file.

**UNCONFIRMED.** The shared block's purpose, whether the leading u32 is a
row count, the fields within the proposed four-byte rows, and whether a
separate program consumes them. The conversion option, editor flag,
`.map` suffix and seek paths were checked in the shipped image. To settle
the layout, find an original reader that accesses the span at header
+0xCC and follow a row to its first typed use. A trace of the MAP
handle at `0x4357A0` can test for reads from an indirect caller during
level load. `lol3_claimed_edges.py --check` verifies the block in the
original archives, pins the bytes of the conversion guard and the
editor-limit code, and checks the 23 seek sites.

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

**CONFIRMED.** Waypoint byte
+6 takes 15 values across the 2,384 rows: 0 (114), 1 (57),
2 (1,957), 4 (3), 6 (3), 10 (2), 12 (8), 15 (180), 23 (2),
31 (3), 37 (1), 46 (27), 78 (4), 125 (20) and 255 (3). The
largest pair with byte +7 is +6 = 2 and +7 = 4 (1,757 rows).
Six levels use only the value 2: CKEEP, ISHAT, JUNDR, MLOW2,
OLOW3 and QWOD0. The save record at `0x436077–0x43608C`
copies the table pointer and a byte length of count × 8, so
the saved image includes this byte. Byte +6 is a distance
limit in steps of 32 X/Z units. Creature command 0x0D subcommand 16
reads the command's u16 +6. It clears `0x7D772C` for `0xFFFF` or
stores the corresponding waypoint row pointer there
(`0x4B8A0D–0x4B8A46`). The [opcode census](lol3-script-opcodes.md#creature-subcommands-of-opcode-0x0d)
found zero stored instances of that subcommand. The creature test loop at
`0x4BD7F4–0x4BDF1F` runs indexes 0–48 through the table at
`0x4BE250`. Index 41 (`0x4BDE92–0x4BDEEC`) passes row s16 +0/+2
and the creature's dwords +4/+8, each shifted right 16, to the
distance routine `0x44AAB0`. It reads byte +6 at `0x4BDED6`
and is true when that distance is less than 32 × byte +6 plus
the value returned by the creature's virtual call +0x14
(`0x4BDEAB`, `0x4BDEDE–0x4BDEE9`). A true result goes to
`0x4FDE80` (`0x4BDF00–0x4BDF12`). The other absolute uses of
`0x5701A4` are `0x4B4D7E` (s16 +0, s16 +2, u16 +4),
`0x4B5B1E` (u16 +4, then s16 +0 and s16 +2), `0x4BCAD1`
(s16 +0 and s16 +2) and `0x4FD6C8` (u16 +4 and byte +7).
The `0x7D772C` pointer is also copied to object +0x1990 at
`0x4F8F7C` and exported at `0x438E47`.

**CONFIRMED.** The 2,384
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
The 31-byte slots, 36 in all, are printable C
strings. Thirty-two are filled out with `0xCD`. `Vic` and `Sam`,
each in BUPP1 and again in LUPP2, have one extra NUL and then
`0xCD`. The first label starts at `BUPP1.WSX+0x181E90C`. There are 19
distinct labels: one occurs 13 times, five occur twice and 13 once.
`lol3_map_spans.py --check` compares their counts and a digest.
The retail executable image contains neither `WayPoint` nor `BadName`.
CKEEP, GRULO, ISHAT, MLOW2, OLOW3 and QWOD0 have a path count
of zero. For every nonempty label span in the 18 entries, the only seeks
below its end in loader `0x43E6B0` are from header +4, +0xC8 and +0xDC.
The subsequent reads of 8 × field 19, 8 × u32(+0xC4) and
4 × u32(+0xD8) end at or before that span (`0x4F0218`, `0x43EC21`,
`0x43EC82`). `lol3_claimed_edges.py --check` tests all 23 seek offsets
and these read widths against both spans.

**UNCONFIRMED.** Which original authoring code writes or reads the two
label spans. A separate original editor reader would settle it if it
reaches `u32(+0xC8) + 8 * u32(+0xC4)` or
`u32(+0xDC) + 4 * u32(+0xD8)` and advances by 26 or 31 bytes.

## MAP sections 1 and 2

**CONFIRMED.** Field 1 (header +0x08) points to field-20
eight-byte rows, copied to world +0x20 by
`0x43EB7C–0x43EBA1 → 0x4EFDC0`. Field 2 (header +0x0C)
points to field-21 56-byte surface rows. The loader reads the
rows to world +0x24 (`0x43EADF–0x43EB04 → 0x4A65F0`).
It stores field 21 at world +0x44 (`0x5701B4`), the count
tested against waypoints above. The surface reader clears
bytes +0x24–+0x27 and +0x2D and can set live +0x2C to 0 or 23
depending on the first material and the row's stack position
(`0x4A6653–0x4A66DF`, dispatch `0x4A671C`). Other branches
leave the stored +0x2C in place.

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
**CONFIRMED (extent, and not read by the game).** Between the
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
share no vertex between cyclic neighbors. The loader calls the seek helper sixteen times in
`0x43E884–0x43EC57` (22 direct calls in the whole function, plus the
nested seek at `0x4EFE96`; all are listed above), and each call pushes one stored header
dword. The call at `0x43EA72–0x43EA79` pushes `[esp+0x58]`.
By the same three-push rule as the waypoint seek at `0x43EBD9`
(`[esp+0xDC]` is header +0xC8), that dword is header +0x44,
the first byte after this span. The traced MAP loader skips the span.
The `.map` suffix at `0x54976C` is used only at `0x43E293`, and
the sole direct call to `0x43E6B0` is at `0x43E304`. In all 18 entries,
the only seeks that start before the span are header +4, +8,
+0x0C, +0xC8 and +0xDC. Their reads (8 × field 19,
8 × field 20, 56 × field 21 at `0x4A6604–0x4A663C`,
8 × +0xC4 and 4 × +0xD8) all end at or before its start.

**CONFIRMED (each byte is read or written). UNCONFIRMED (what
the bits mean).** Settling test: in a running level, change one
bit of byte +5 or +6 in the section-1 row of the surface under
the party (table pointer `0x570190`), let the copy at
`0x4FFD91–0x4FFDF9` run again, and compare what changes on
screen and in movement. Rows with byte +5 bit `0x10` are
already decoded as geometry in the +7 row below. The 167,942 section-1 rows are eight bytes,
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
| +7 | Replaced from the caller's byte +7 by switch arms 14 and 16 (`0x4E65E7`). Zero-extended, shifted left 14 and ORed into the u16 object +0x3E at `0x4FFDF1–0x4FFDF9` and at `0x4FFC65–0x4FFC6D`, which keeps only bits 0–1. **CONFIRMED:** a second consumer reads the whole byte. For rows with byte +5 bit `0x10` (`0x50071A`), `0x500723` calls `0x500600`. It writes four 16.16 X/Y/Z corner points to object +0x00–+0x2F along one surface edge, chosen by object +0x42 bits 0–1. Bytes +2 and +4 give the start and width along the edge in 1/256 steps (`0x500688–0x5006E3`). The top Y is surface s16 +0x1A minus (s16 +0x1A − s16 +0x18 − byte +7) × byte +3 / 256 (`0x50060E–0x50063F`). The bottom Y is the top minus byte +7 minus 1, in whole units (`0x500642–0x500658`). |

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

**CONFIRMED** (the bytes, the skip, and that the game does not
read the names). In all 18 entries, 22 bytes per section-0 row follow
the counted 24-byte rows and end where section 1 begins: 630 slots.
Each is a NUL-terminated printable name, padded with `0x00` or
`0xCD`, and 168 of the names are distinct. CKEEP's first slot is
at entry +0x5DC and is `Floor39`. The loader seeks to field 0
(`0x43FCCE`, call `0x435A90` at `0x43FCD6`) and `0x4AB420` reads
exactly 24 times the count (`0x4AB42E`). The timed walk steps
`0x18` (`0x4AB682`). The next seeks go to field 20 (`0x43FD09`, when field 19 is
nonzero) and then field 1 (`0x43FD45`), so this loader does not read
the names. A scan of the code section for another 22-byte stride found
only `add edi, 0x16` at `0x45D9D9`, a screen spacing, and the game has
no reader of the names. The `.odf` suffix at `0x549774` is used
only at `0x43E202`, and `0x43FC40` is called only from
`0x43E246`. In all 18 entries, the only seek that starts before
the names is field 0, and its read stops where they begin.
Fields 20, 1, 2, 4 and 3 all start at or after section 1.
Most names look like material names (454 are `Floor` plus
digits), but nothing in the game reads them. Section 4
ends at the start of section 3 in all 18 entries.

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
consumers, including HP and behavior. Definition bytes not
listed above or on the combat page have no known reader
(**UNCONFIRMED**). Settling test: in a running level, set read
watchpoints on those bytes of one creature's 139-byte runtime
row (stride at `0x4F0E83`) and note each reading address. The section-1 and section-3
subtables share reader `0x4FD560`. It assigns each 16-byte row
a pointer into the subsequent 12-byte array (`0x4FD5DC–0x4FD617`).
Follow that pointer into the first consumer to identify the subtable.

### Type tags and AI resources

**CONFIRMED.** The lookup at `0x4FDEF0` searches cached objects by
the original tag at runtime +0x2764. On a miss `0x4FD8F0`
copies that tag and formats `global\ai\%s` at
`0x4FD932–0x4FD963` (the format is at `0x551BF0`). The next
calls build five resources: `stat.csv`, `goals.csv`,
`actions.csv`, `effector.csv` and `spells.csv`
(`0x4FD975–0x4FDA39`; leaf strings at `0x551BE4`, `0x551BD8`,
`0x551BCC`, `0x551BBC` and `0x551BB0`). Each call joins the
directory and the leaf at `0x420300`, then loads at `0x4FD780`.
The five grid sizes, rows by columns, are `0x20`×1, `0x2E`×`0x0E`,
`0x2E`×`0x0F`, `0x3A`×`0x20` and `0x2E`×`0x95` (row loop bound at
`0x4FD815`, column loop bound at `0x4FD83B`), stored at object
+8, +0x28, +0x2AC, +0x55E and +0xC9E. The lookup increments
the cached object's count at +0x2774 (`0x4FDF4E–0x4FDF56`).

**CONFIRMED.** The 18 original ODFs contain 334 field-3 rows and
68 distinct tags. Hashing the first four paths against `GLOBAL.WSX`
joins all four for 60 tags, three for one, two for one and
zero for six. The fifth path, `spells.csv`, does not change the
60 or the six: 60 tags have all five files and the same six have
none. `NONE` has `stat.csv`, `goals.csv` and `spells.csv`.
`Spire` has `stat.csv`, `goals.csv` and `actions.csv`. In QWOD0,
the tag `SPIDER` starts at `QWOD0.WSX+0x7781AB`. Its four resource
payload starts in the order above are `GLOBAL.WSX+0x1FDBA3`,
`+0x1FBE73`, `+0x1FB11F` and `+0x1FB568`. This establishes a use
of the type tag without assigning gameplay meaning to every tag.

**CONFIRMED** (the miss arm and both fields it tests).
`0x420300` begins after `nop` padding. It copies the
directory, the backslash at `0x546318` when the directory does not
already end in one, and the leaf into the destination, or into
`0x5D5818` when that pointer is null (always here), and
returns the buffer. It does not look the name up. `0x4FD780`
begins after `ret` and two `nop`s at `0x4FD77D`. It zeros the
row-by-column product, then calls `0x435880`, which returns the
result of `0x435150` (`0x4358A1`, `0x4358C9`). That lookup returns
1 when the virtual call at +0x18 is nonzero (`0x435161`) or when
the hashed name is found (`0x4351E6`). The miss calls `0x494390`
on the name object that `0x435880` builds on its stack with
`0x434E80`. The base constructor `0x493F80` clears the low six
bits of +0x24 (`0x493F9E–0x493FA4`) and zeroes +0x18 (`0x493FAA`).
`0x434E80` then sets the name through `0x494DB0 → 0x494300 →
0x493690`, which stores a heap copy of the name at +0x18
(copy routine `0x529920`, `0x4936D4–0x4936DC`). Bit 5 of +0x24
is set only by other methods of the class (`0x4941D9`,
`0x49445F`, `0x4945A4`, `0x494803`, `0x494A0F`, `0x494AB5`),
which this path does not call. So `0x494390` calls `0x493820`.
After the same virtual +0x18 test, `0x493820` tries to open the
name as a loose disk file with `CreateFileA` (import `0x538090`,
read access, open existing; `0x49385F–0x493875`). It returns 0
when that fails (`0x493889`) and 1 after `CloseHandle`
(`0x493890–0x4938B6`). A zero result at `0x4FD7B1` jumps to the
epilogue `0x4FD8E4` and leaves the zeros. The caller does not
test the return. `lol3_odf_companions.py --check` re-counts the
names, the joins and these bytes.

## Writing the stored fields

**CONFIRMED.** `lol3_map_writer.py --check --data /path/to/DAT` reads each
of the 18 MAPs into fields, writes it again in memory and gets the same
bytes. Command lengths are the 39 opcode sizes that the English retail
image returns at `0x4E56F0/0x4E5790`. The region stream (MAP +0x3C/+0x84)
holds 4,040 command records and the object stream (+0x44/+0x8C) holds
54,940, group headers included; these are the counts on the
[opcode page](lol3-script-opcodes.md). 33 of the 39 opcodes occur. The
other rows are 2,384 waypoints (`0x43EBD9–0x43EC45`), 36 paths
(`0x43EC4D–0x43EC92`) and 23,850 placements (`0x43EEB6–0x43EF6F`; the
common fields, X/Z included, are taken by `0x4411F0`).

**CONFIRMED.** The writer regenerates 17,961,275 of 21,232,680
bytes (84.6%) from typed fields. Here, a typed field is one whose
stored value is read by native code at the listed address with that
width. Some of those fields have uses whose game meaning is still open.
The check also matches the 3,271,405 bytes carried at their original
offsets. Three fields with a known width but no read of the stored
value stay retained: header +0xCC (the shared-block start, which the
loader never seeks; 72 bytes), region descriptor u8 +0x16 (only
cleared, at `0x4F5A8C`; 13,163 bytes) and u8 +9 of the +0x48 rows
(cleared on load at `0x46C5E8` before any read; 95 bytes).

| Source | Newly typed fields | Native evidence | CKEEP example |
|---|---|---|---|
| Header | 46 dwords: the tag (`0x43E800`) and the seeks, counts and lengths the loader reads | Header load `0x43E7E7`, seek and read pairs above | `CKEEP.WSX+0xCBB182`, header +0x00 is 38 |
| MAP +0x04 and +0x08 seeks | Signed X/Z dwords per vertex. Section 1 has a signed index word and six individually held bytes | `0x4F0126–0x4F0161`, `0x4E6425–0x4E65E7`, `0x4FFD91–0x4FFE05` | `CKEEP.WSX+0xCBE0AE` and `+0xCC5B2C` |
| MAP +0x0C seek | Surface neighbors and vertices (+0x08/+0x10), signed low/high heights (+0x18/+0x1A), region index (+0x1C), section-1 index/count (+0x1E/+0x32), dword +4, u16 +0x2A and single bytes +0x20–+0x23, +0x2C, +0x31 and +0x33–+0x37 | `0x4A67D0–0x4A685A`, `0x4A74C0–0x4A7566`; see [surface reads below](#surface-and-placement-reads-and-the-largest-retained-ranges) | `CKEEP.WSX+0xCCF97C` |
| MAP +0x34/+0x7C | Eight-byte rows: two u16 vertex indices, u16 byte offset into the +0x30 table, u8 pair count, u8 traversal count | `0x43EB3F–0x43EB74 → 0x4EFE40`, `0x4EFED1–0x4EFF14`, `0x4F0126–0x4F0161`, `0x4F0170–0x4F0190` | `CKEEP.WSX+0xD0FFDB`: 2858, 2857, 0, 1, 1 |
| MAP +0x30/+0x78 | Pairs of u16 surface indices, four bytes per pair | `0x4EFE72–0x4EFEA7`, `0x4EFF14–0x4EFF36` | `CKEEP.WSX+0xD0E94B`: 5, 22 |
| MAP +0xA4/+0xAC | 28-byte region descriptor. Typed dword +0 indexes the +0x34 rows, u16 +6 selects a +0x2C row (or 0xFFFF), u16 +8 is the state word, u16 +0x0E is the event-list offset, u8 +0x1B supplies the +0x34 run count | `0x43EB0C–0x43EB2A → 0x4E7330`, `0x4AC21A`, `0x4E73C5–0x4E73ED`, `0x4E767B–0x4E7685`, `0x4F5A91–0x4F5AAA` | `CKEEP.WSX+0xD2CEB3` |
| MAP +0x28 | Settings block read of 0x218 bytes. The typed subset is four dwords at +0x0C through +0x18 and the signed word at +0x1A8 | `0x43E87B–0x43E8E6` | `CKEEP.WSX+0xD0E569` |
| MAP +0x2C/+0x74 | 12-byte rows. u16 +4 is decremented by a clock value in one switch arm. u8 +7 selects that arm and u8 +8 is tested for bit 0 | `0x43EBA9–0x43EBC4 → 0x4EFA90`, `0x4EFAF0–0x4EFB3C` | The count is zero in CKEEP. EWOD1 has four rows at its header +0x2C seek. |
| MAP +0x48/+0x90 | 12-byte rows. u8 +8 is the lookup key. u8 +9 is retained: the load clears it (`0x46C5E8`) before the iterator tests it (`0x46C655`) | `0x43EF93–0x43EFAB → 0x46C5B0`, `0x46C61A` | `CKEEP.WSX+0xD0E781` |
| MAP +0x4C/+0x98 | u32 object command offsets. +0x98 is the byte length of the array. | `0x43EA36–0x43EA60`, `0x4A8290–0x4A82A6` | `CKEEP.WSX+0xD07270` |
| MAP +0xBC/+0xB8 and +0xB4/+0xB0 | Five bytes per predicate and separate level byte array | `0x43E91D–0x43E964`, `0x440A20–0x440A5E`, `0x4F02B0–0x4F0414` | `CKEEP.WSX+0xD2F277` and `+0xD2EF83` |
| MAP +0x38/+0x80 and +0x40/+0x88 | Length/kind, known reference and operand fields from the event matchers, and the kind-22 name through its first NUL | `0x4A8255–0x4A82B2`, `0x4A8DE9–0x4A8E13` and the per-kind [event evidence](lol3-script-events.md#two-event-pools) | A region terminator `CKEEP.WSX+0xD0E889` and an object kind 1 at `+0xD0962C` |

### Surface and placement reads, and the largest retained ranges

**CONFIRMED.** The previous accounting emitted 15,822,119 bytes
from known reads and carried 5,410,561 bytes. Among the repeated
rows, the largest groups of retained bytes were surfaces and region
descriptors (3,554,399) and placement records (797,463). The
readers below move 1,544,401 of those bytes into typed fields.

| Stored group | Newly typed bytes across 18 MAPs | Native read |
|---|---:|---|
| Surface dword +4 | 475,804 | `0x4FB1E6–0x4FB207` tests the low flags and uses bits 12–13 to choose one of the neighbor words. The surface constructor at `0x4A664C–0x4A66DF` leaves this dword as loaded. |
| Surface u8 +0x22 and u16 +0x2A | 356,853 | `0x4C0121–0x4C0154` checks the second material byte and uses the base light-map ID in the second-face lookup. The first-face lookup also uses +0x2A at `0x4C00A9–0x4C00D1`. |
| Surface u8s +0x36 and +0x37 | 237,902 | `0x4A6D00–0x4A6D3F` uses them as row offsets when finding the lower and upper surfaces. `0x4C01A2` follows a nonzero +0x37 to the next 56-byte row. |
| Placement common fields and class tails | 473,842 | Each of the five loaders (`0x44FCD0`, `0x469980`, `0x4B44F0`, `0x4D59F0`, `0x4D7480`, called at `0x43EEC7–0x43EF6F`) reads one stored row into a stack buffer through the MAP read `0x4357A0` and passes that buffer to its constructor, which calls `0x4411F0`. The type-specific reads follow below. |

**CONFIRMED.** Surface rows alone accounted for 2,260,069 retained
bytes at 19 bytes per row. Five more stored bytes per row have
native readers. This moves 594,755 bytes into typed fields.
`CKEEP.WSX+0xCCF97C` is row zero. All values below are unsigned bytes.

| Offset | What code does with the value | CKEEP row zero |
|---|---|---:|
| +0x21 | `0x4F6178` and `0x4F61AF` copy it to the first face's geometry record at +0x40, for both sloped and flat faces when +0x20 is present. | 128 |
| +0x23 | `0x4F627D` and `0x4F62B8` copy it to the second face's geometry record at +0x82. | 128 |
| +0x2C | `0x4FB34A–0x4FB355` optionally subtracts it from the signed +0x18 height. `0x4A7883–0x4A7889` subtracts the same byte from a height in 16.16 units. The loader changes it only on specific branches. | 0 |
| +0x31 | `0x4A7057–0x4A70FE` walks the surface table at a 56-byte stride and, when a mask was supplied, tests it against this byte before checking the geometry. | 0 |
| +0x33 | `0x4F7059–0x4F7066` converts it to a signed adjustment as `(value - 128) * 65536`. The lighting calculation reads that adjustment at `0x4C0853` and can add it to all three channels at `0x4C0873–0x4C0877`. | 128 |

**CONFIRMED.** Surface +0x24–+0x27 are two words cleared at
`0x4A66CF–0x4A66D3`. The load clears +0x2D on every row before
subsequent rows consult it as live stack state. These five bytes stay
retained. Dword +0 is zero in all shipped rows. Live code reads and
replaces it as the surface's object-list head (`0x4E5590–0x4E5595`).
**UNCONFIRMED.** The first reader of the stored dword before live setup,
and the stored roles of +0x28–+0x29 and +0x2E–+0x30. A read of the
loaded row before those bytes are replaced would settle their coverage.
The remaining 14 retained bytes per surface total 1,665,314.

#### Surface texture references

**CONFIRMED.** Surface bytes +0x20 and +0x22 select the first and
second material. The renderer skips a face when its byte is 0xFF.
Otherwise it scales the byte by 24 and adds it to the loaded ODF
section-0 base at `[0x5701CC]` (`0x4F6CD3–0x4F6CF4`,
`0x4F6DBC–0x4F6DE0`). It reads the material's signed texture
selector at +4. A nonnegative selector indexes the texture table
at `[0x570200]`. A negative selector first selects an eight-byte
row in the animated lookup at `[0x5701DC]`. Its u16 +0 and u8 +7
are added before the texture table lookup (`0x4F6CFA–0x4F6D30`,
`0x4F6DE4–0x4F6E1C`). The surface word at +0x2A is the
light-map base. When both faces have materials, the second uses base
plus one (`0x4C0134–0x4C0154`).

All 182,851 non-sentinel face references in the 18 levels join to
existing ODF rows. There are 1,200 references with negative selectors.
The OBJ exporter carries each surface's two original references and
the light-map base as metadata in its face order.

**CONFIRMED.** The common placement reads in addition to X/Z
are u16 heading +4 and s16 height +6 (`0x4411FF–0x44124C`),
s16 surface +0x0A with sentinel −1 (`0x441284–0x4412A3`),
u16 event-list word +0x0C, u16 +0x0E, u32 flags +0x10
(`0x441224–0x441263`), and u8s +0x1C and +0x1E
(`0x441250–0x44125C`). The class tails parse these additional
fields while preserving the remaining byte spans.

| Placement class | Native reads from +0x20 | Bytes emitted from fields per row |
|---|---|---:|
| Type 3 | u16 definition index and three u8 inputs, `0x44FBC2–0x44FC28` | 25 |
| Type 16 | u8 definition index, `0x4698E7–0x46990D` | 21 |
| Creature | u8 definition selector: `0x4B4579` loads the dword at +0x20 of the row buffer and keeps only the low byte (`and eax, 0xFF`). `0x4503E0` is `ret 4`, so `[esp+0x30]` is that dword in the 0x38-byte row read at `0x4B454F`. The byte indexes a 139-byte row at `[0x5701D8]` (`0x4B4583` through `0x4B4597`) and `0x4B45AA` stores vtable `0x53FE28`. The row count is `[0x5701F8]` (the save descriptor `0x435FE0` stores it times 139 at `0x43601B–0x43602F`); the setup does not compare the byte with it. +0x21 through +0x37 stay retained | 21 |
| Mover | type-16 index and the eight state bytes at +0x21–+0x28, `0x4D58FB–0x4D5994` | 29 |
| Item | u32 identity and u8 alternate input to the item definition lookup, `0x4D7390–0x4D73A2` | 25 |

**CONFIRMED.** The largest individual retained range is 104,044
bytes starting at `JUNDR.WSX+0xF90748`. The next is 94,532
bytes at `BUPP1.WSX+0x1B32591`. They start at the u32 offset in
MAP header +0xC0 and run to the end of the MAP. Across all 18
levels those tails total 606,420 bytes. Each begins with five
bytes followed by the NUL-terminated text `Expression`. None of
the retail MAP loader's 22 direct seeks, nor the nested seek at
`0x4EFE96`, takes header +0xC0, and on all 18 maps every typed
range ends at or before the tail start. This seek evidence shows
only that the retail loader skips the tails: it does not parse
them, so they are carried as retained bytes, not typed fields.
No `Expression` NUL string occurs in the inspected `LOL3.DAT`. **UNCONFIRMED.** The
grammar of the tail and which original tool reads it. A program
that seeks to header +0xC0 and exposes the record widths would
settle that range. The unexplained surface fields and tails
remain visible in `--coverage STEM`.

The coverage counts come from non-overlapping physical MAP ranges.
Where a record contains retained fields, the writer copies each field
or tail at the original row-relative offsets. The check changes an
object-command operand, a waypoint, a vertex, a creature's Z,
surface +0x21, +0x23, +0x2A, +0x2C, +0x31 and +0x33, and
an item placement's u32 +0x20 in memory. Only
the selected fields change. The script and schematic readers see the
first four edits, and reading the edited MAP again gives the new
surface and item values.

| Part | Bytes from fields | Retained bytes |
|---|---:|---:|
| Header | 3,312 | 7,128 |
| Vertices and section 1 | 2,259,400 | 0 |
| Surfaces and region descriptors | 5,140,735 | 1,889,085 |
| +0x34 and +0x30 tables | 9,125,520 | 0 |
| +0x28, +0x2C and +0x48 tables | 1,071 | 11,673 |
| Object command index, predicates and level bytes | 243,025 | 0 |
| Event pools | 233,398 | 33,830 |
| Region and object commands | 359,668 | 99,314 |
| Waypoint and path rows, placements | 595,146 | 323,621 |
| Shared block, both label arrays and surface-to-script gap | 0 | 271,812 |
| Other sections and gaps | 0 | 634,942 |
| **Total** | **17,961,275** | **3,271,405** |

`--coverage STEM` lists every retained range with end-exclusive MAP and
WSX offsets. In CKEEP it reports 110,020 retained bytes, starting with
MAP +0x10..+0x14 at `CKEEP.WSX+0xCBB192..+0xCBB196`. `--list STEM`
continues to give the hashes and offsets of the four named ranges.

**UNCONFIRMED.** The full meanings of the stored region and surface
fields and the retained subfields. The exact-row reads at `0x4E737A`
and `0x4A663C` established their record extents. The coverage walk
separates the remaining bytes by range. Tracing each retained offset
to the first typed read or write would extend the table. The shared
block still requires a reader witness, as described in [Q8](#q8).

## Close-out

### Q4

**What was measured.** The twelve nonempty gaps are 1,784 bytes, and 11 of those bytes are `0x00`. As 892 little-endian u16 values, none is 0, and 820 of the values are distinct.

**What was tried.** This count is the gap before field 16. The page already records that the loader's seeks skip both label spans and this gap. Running-game observation, 2026-11-20, in a run with two live edits in the cache initializer ([run](NEEDS_A_RUNNING_GAME.md#run-of-2026-11-20-dlow1-autosave-with-two-live-edits)): in the DLOW1 MAP the loader seeked to +0xC944 (`0x43EBE8`) and then to +0xD868 (`0x43EC5C`), past the 26-byte names at +0xCCD4–+0xD868, as listed above. The read before its next seek, which holds the 31-byte label at +0xD86C, was not logged.

**What would settle it.** Log every read the level load makes; a read that covers the 26-byte names or the 31-byte labels, or a read watch on a loaded copy, gives the reader, and a reader that steps by 26 or 31 bytes settles it. The running-game test is partly run, without a settling result ([probes not yet run](NEEDS_A_RUNNING_GAME.md#probes-not-yet-run)).

### Q5

**What was measured.** The 630 name slots hold 8,771 bytes after the terminating NUL: 6,684 are `0xCD` and 2,087 are `0x00`. In 176 slots that pad is not entirely `0xCD`.

**What was tried.** This is a pad-byte count on the section-0 names. The page already records that the loader reads 24 bytes times the count and seeks away without reading the names, and that a zero AI lookup leaves a zeroed buffer. The creature setup index is the low byte of the dword at +0x20 of the 56-byte placement row. `lol3_odf_companions.py --check` re-reads that load, the `ret 4`, the 139-byte stride and the vtable store.

**What would settle it.** A read of a 22-byte section-0 slot past the 24 × count rows (`0x4AB42E`), or a memory search for `Floor39` followed by a read watch, settles it. The running-game test is not yet run ([probes not yet run](NEEDS_A_RUNNING_GAME.md#probes-not-yet-run)).

### Q8

**What was measured.** The 2,873 four-byte rows at `QWOD0.WSX+0x72E4D3` are 11,492 bytes. All 2,873 little-endian dwords are different, and none is 0.

**What was tried.** This is a row-value count in the shared block. The page already records the leading count of 2,873, the identical bytes in all 18 MAPs, and the seeks that skip the block in the standard, conversion and editor cases. Running-game observation, 2026-11-20, in a run with two live edits in the cache initializer ([run](NEEDS_A_RUNNING_GAME.md#run-of-2026-11-20-dlow1-autosave-with-two-live-edits)): in the DLOW1 load the loader read the 0x244 header bytes and all 23 of its seeks on that handle went to member +0x2F2C or later, so that load did not read the block through that handle. Other handles and later play were not covered, and no memory search for the block was made.

**What would settle it.** Log the reads of the MAP loader `0x43E6B0`; a reader of the span at header +0xCC, followed to the first typed use of one row, settles it. The running-game test is partly run, without a settling result ([probes not yet run](NEEDS_A_RUNNING_GAME.md#probes-not-yet-run)).
