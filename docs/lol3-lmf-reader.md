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

**UNCONFIRMED.** The renderer's interpretation of the member flag, dword
+8 and the 32 bytes beyond a 12-byte header and a two-byte-per-sample
extent remains open. The directory conversion, decoder and returned
member pointer were traced. To settle the remaining field meanings,
follow the vtable +8 reader `0x4E2140` from the level's +0x9C light-map
object to the renderer and inspect its first loads from each decoded member.
