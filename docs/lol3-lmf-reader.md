# Native Light Map reader

Addresses refer to the English retail `LOL3.DAT` PE32. Its SHA-256 is
`9a9eb04c8f404ebf68f439df4ec7dc6ad5cc230235d0f853059f636ff720ccea`.
The PE header at file `0xC8` gives image base `0x400000`. The code
section in the table at `0x1C0` begins at RVA `0x1000`, file `0x400`,
so for the VAs in this page file offset is VA minus `0x400C00`.

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

**UNCONFIRMED.** The four s16 values at +0x0C–+0x13. They are all zero
in 214,743 members and vary in the rest; no reader on the member has
been found yet. Checked without a hit: `0x44EB40` itself, `0x44EC90`
(it copies the 0x2C-byte header as 11 dwords at `0x44ED0A–0x44ED16`,
but reads no field there), the first 45 instructions after each of the
15 calls to `0x44EB40`, the size path `0x479D90` and the surface
renderer around `0x4980D8`. Settling test: in a running level, set a
read watchpoint on +0x0C of a member returned by `0x44EB40` (eax at
`0x44EC7D`) whose +0x0C is nonzero, then look at that surface. A hit
other than the copy at `0x44ED16` names the reader.
