# Native Light Map reader

Addresses refer to the English retail `LOL3.DAT` PE32. Its SHA-256 is
`9a9eb04c8f404ebf68f439df4ec7dc6ad5cc230235d0f853059f636ff720ccea`.
The PE header at file `0xC8` gives image base `0x400000`. The code
section in the table at `0x1C0` begins at RVA `0x1000`, file `0x400`,
so for the VAs in this page file offset is VA minus `0x400C00`.
The COFF TimeDateStamp at file +0xD0 is `0x37332C6E`, which encodes
1999-05-07 18:09:50 UTC. That is the field's stored encoding.
`lol3_pht.py --check` re-reads it.

## File and group reader

**CONFIRMED.** The level loader builds the `.lmf` name from the suffix
at `LOL3.DAT+0x147F7C` and calls VA `0x440B40` at `0x43E1BD`.
It opens the resource at `0x440BB0`, reads 0x100 bytes at `0x440BC5`,
and on the ordinary path requires dwords 0 and 38 at `0x440BDE–0x440BEF`.
The archive layout has the exact offset, count and size fields in the
[LMF format page](formats/lmf.md).

**CONFIRMED.** Call `0x440C04` selects archive implementation 2.
Its constructor sets vtable VA `0x540738` (`LOL3.DAT+0x13EF38`,
`0x4E16D0–0x4E1711`, `0x4E1E88`). The loader converts the directory
to live rows at `0x440C55–0x440C89` by passing disk offset
`header[0x0C]+entry[0]`, expanded length, low flag bit and extra dword
to `0x4E1840`.

- At `0x4E1902–0x4E1969`, a continuation requires the preceding row's
  live file offset plus expanded length to equal the new row's offset,
  matching source selectors and a total expanded group size of at most
  `0x40000`. The runtime u8 +0xF stores distance back to the group start.
- At `0x4E2154–0x4E215E`, the member reader subtracts that distance
  times 16 to find the group start. On a cache miss it seeks to the
  stored group offset at `0x4E21C1`. The low 18 bits of the encoded
  length are assembled at `0x4E21C6–0x4E21D8`.
- A positive encoded length is read into scratch space at `0x4E21E6`
  and decoded at `0x4E21FD → 0x4ECDB0`. The zero arm reads the expanded
  range directly at `0x4E2213`. The reader returns the member address
  by adding its expanded offset to the cached group (`0x4E221B–0x4E2229`).

**CONFIRMED.** Checking the 18 original entries with a bounded LZO1X
reader reproduces the expanded length for every one of the 5,256 stored
groups and the expected member boundaries. The first 657-byte group
in `CKEEP.WSX+0xC48A84` demonstrates why individual directory row
lengths do not identify separately compressed blocks. Its native label
comes from `LOL3.DAT+0x1480E4`.

## Decoded members

**CONFIRMED from file data.** All 424,288 expanded members begin with
u32 +0 equal to 0 or 1. The u16 fields at +4 and +6 fit the length rule
`size = 44 + 2 × u16(+4) × u16(+6)` in every member. At
`CKEEP.WSX+0xC48A84`, expanded offset zero contains a 76-byte member
with +0 = 0, +4 = 4, +6 = 4 and u32 +8 = 0.

**CONFIRMED.** The render helper at `0x44EB40` gets the member via
world +0x9C for a positive ID below world +0xDC, passing ID − 1
(`0x44EB50–0x44EB73`). Both conversion loops start their samples
at member +0x2C. The preceding 32 bytes therefore belong to the
header extent used by these paths. With a nonzero mode, the helper
tests runtime bit 1 at `0x44EB8A`, and sets it after conversion
at `0x44EC4F–0x44EC52`. Mode 1 maps each input u16 through byte
table `0x631340`, stores one byte per sample in place, clears bit 5
(`and 0xFFFFFFDF` at `0x44EBF9`) and extends
the output by a copy of the last `u16(+6)` bytes. The other
nonzero mode maps that byte through word table `0x629290`,
stores two bytes per sample, and sets bit 5
(`0x44EB93–0x44EC4D`).

**CONFIRMED.** The native caller at `0x4C00DD–0x4C0119` reads
member dword +8 and accumulates its three low bytes as separate
16.16 values. The helper also tests whether +8 is nonzero when
selecting an additional processing path (`0x44EC54–0x44EC75`).

**CONFIRMED.** Disk bit 0 marks per-vertex normals. The surface
renderer tests member +0 bit 0 at `0x4980D8`; when it is set it reads
three s16 values per vertex from +0x14 + 6 × vertex, doubles them and
passes each vector to `0x44E090` and the vertex-light routine
`0x4BFBE0` (`0x498102–0x49815F`). When it is clear it uses the
surface's own words +0x32/+0x36 instead (`0x498167–0x49818D`). So
+0x14–+0x2B hold four vectors of three s16. In the original files the
131,217 members with bit 0 set carry 524,865 vectors of length
32,767–32,769 (unit normals scaled by 32,767) and 3 zero vectors; in
all 293,071 members with bit 0 clear the four vectors are one vector
repeated. `walk_lmf_leaves.py --check --decode` recounts these.

**CONFIRMED.** Dword +8 is a colour stored as `0x00RRGGBB`. The
routine `0x4C0030` averages bytes 0, 1 and 2 of +8 over the light maps
of the surfaces it visits (row slots +0x20 and +0x22, base ID +0x2A,
`0x4C00A7–0x4C01BF`) and keeps byte 2 at `0x7D7740`, byte 1 at
`0x7D7744` and byte 0 at `0x7D7748` (`0x4C01D6–0x4C04AB`). Its caller
adds a dynamic light's RGB555 word +0x14 to that triple component by
component: bits 10–14 to the byte-2 value, bits 5–9 to byte 1 and
bits 0–4 to byte 0 (`0x4C06DE–0x4C072A`). `0x4BFF00` turns the
triple into one intensity (largest plus a quarter of the other two).

The render size path `0x47451E → 0x479D90` reads only +4 and +6,
rounding each up to a power of two no larger than 256 with an aspect
limit of 8 (`0x479D90–0x479E2E`).

**CONFIRMED from file data.** The four words at +0x0C–+0x13 are all
zero in 214,743 members. Every one of the 610,325 nonzero words in the
remaining 209,545 members has bit 15 clear and occurs verbatim in its
own member's sample grid at +0x2C. For example, `BUPP1.WSX+0x1699822`,
expanded offset +0x2634 (LMF row 23), holds `(24256, 0, 9472, 23200)`
in these words, and all four appear in the 16 × 32 grid. For the
column-major index `x × u16(+6) + y` and corner order `(0,0)`,
`(width−1,0)`, `(width−1,height−1)`, `(0,height−1)`, 340,718 nonzero
words match a sample within the 2 × 2 square extending inward from
the corresponding corner. At the opposite corner, 107,136 match. For comparison, a random 2 × 2
square of the member's own grid matches 158,693 words, and the previous
member's grid holds 260,804 of them, so the corner figures are a
measured tendency, not a rule. Of the same 610,325 words, the
nearest match to the assigned corner (counted in texels along the
longer axis) is the corner texel for 108,537, one texel away for
232,181, two to seven away for 139,039, and 130,568 do not occur
within the 8 × 8 texels at that corner. 287,177 match the texel one
step inward on both axes (55,848 of them also match the corner
texel). The grid colour nearest the numeric mean of the packed words
in that inward 2 × 2 matches 307,470. A quadrant (the quarter of the
grid at that corner; an odd middle row or column belongs to both)
minimum, maximum, most common colour, or colour nearest the numeric
mean of its packed words matches 46,912, 171,206, 182,804 and
154,018. The best single point on a 5 × 5 lattice of the rectangle,
rounded to a texel, matches at most 58,260 for any one of the four
words. `walk_lmf_leaves.py --check --decode` (which `check_all.py`
runs when liblzo2 is installed) rechecks all of these counts.

**UNCONFIRMED.** The exact sample selection rule and any consumer that
interprets these words. The corner texel, the inward texel, the 2 × 2
mean and the quadrant summaries above do not reproduce the words. The `0x474D85` and `0x47596D` render paths call
`0x479D90` for dimensions and `0x479E60` for surface form and projection.
The `0x47F833`, `0x47FD11` and `0x480438` paths use the parallel pair
`0x4857C0` and `0x485840`. Their dimension reads are at
`0x479D90–0x479E2E` and `0x4857C0–0x485833`. The sampler at
`0x485FD0` passes +0x2C at `0x485FFB` or `0x48601E`. The `0x499C42`
and `0x498D51` paths send the member to `0x44EED0`, which tests a bit
in its first dword and takes its projection inputs from a separate
argument (`0x44EED6–0x44EF40`). The subsequent normal reads start
at +0x14 (`0x499C79`, `0x498BA4–0x498BC2`). The resampler copies the
whole 44-byte header, including the four words, at `0x44ED16` and
returns the scratch copy through `0x44EEAB–0x44EEC3`.

Checked without a hit: `0x44EB40` itself, `0x44EC90`, the first 45
instructions after each of the 15 calls to `0x44EB40`, the size path
`0x479D90` and the surface renderer around `0x4980D8`. A future read watch on the two dwords +0x0C/+0x10 of a nonzero member
returned by `0x44EB40` (`EAX` at `0x44EC7D` or `0x44EC83`) can isolate
the consumer. If `0x44ED16` or
`0x44EEA2` copies the member, move the watch to the same offsets in the
scratch result (`EAX` at `0x44EEC3`) and render its surface. A typed read
of those words, or a shipped writer that supplies their sample indices,
would settle their purpose.
