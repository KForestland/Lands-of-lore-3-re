# Native texture colour bake

Addresses are English retail `LOL3.DAT` PE32 VAs. Subtract `0x400C00`
for the file offset of an instruction. The [PE and image identification](lol3-lmf-reader.md)
applies here.

## Per-descriptor colour source

**CONFIRMED.** The two callers at `0x482308` and `0x484870` build
the lookup when their destination descriptor dword +0x20 is 11.
They pass a texture descriptor to the bake entry `0x4826D0`
(file `0x81AD0`). That entry obtains the u16 source through
`0x44B6E0` (file `0x4AAE0`), which selects by descriptor byte +0xD.

| Descriptor byte +0xD | Source selection | Evidence |
|---:|---|---|
| 1 | Object pointer `[0x570218]`, key `[0x570240] + u16(descriptor+2)` | `0x44B731–0x44B749` |
| 2 | Object pointer `[0x570218]`, key `[0x570248] + u16(descriptor+2)` | `0x44B714–0x44B72C` |
| 3 | Object pointer `[0x570204]`, key `[0x570238] + u16(descriptor+2)` | `0x44B6F7–0x44B70F` |
| Other | Returns zero | `0x44B6F3` |

The three source arms call vtable +8 with that key and a zero argument.
The descriptor therefore selects the table by both its resource class and
its u16 key. The [cache palette inventory](lol3-texture-palette-sources.md) joins every indexed cache span to its original palette bytes.

## Bake and consumers

**CONFIRMED.** Let `S` be the source array returned above and
`T` the 256-word scratch table at VA `0x6601B8`. The bake at
`0x4826DB–0x482720` computes

| Index | Written word |
|---:|---|
| 0 | `0` if descriptor byte +8 has bit `0x02`, otherwise `0x8000` |
| 1–255 | `(S[index] if nonzero else 1) OR 0x8000` |

For example a nonzero source `0x003F` becomes `0x803F`, while a
source zero at a nonzero index becomes `0x8001`. These are direct
examples of the code rule at `0x482700–0x482710`.

**CONFIRMED.** The straight copy at `0x48253E–0x48254A` reads each
input byte as an index and writes the selected word. The resampling
arm at `0x4825E0–0x4825F7` picks an input byte by the integer part of
a 16.16 stepping accumulator and uses the same table. Both write
words into the buffer pointed to by `[0x6606B8]`. A related path at
`0x47E168–0x47E18D` unpacks the low 15 bits of each source word as
three five-bit components at shifts 10, 5 and 0. That path writes dwords
`((r << 8 | g) << 8 | b) << 3` (zero becomes 1) to its own array at `0x65FDB8`: index 0 is set to 0 at
`0x47E156`, and the entries follow from `0x65FDBC`.

**CONFIRMED.** A row-span case dispatches from `0x4E0BA0` to
`0x4E0BD0` when the resource flag has bit 2 set and bit 5 clear.
For a witness, the record at game-folder `cdcache.wsx+0x12C6E2` has
flags `0x028E`. The row helper starts at resource +0xC and advances
by `4 + u16(row+2)` (`0x4E0BE0–0x4E0C0F`). It returns pointer
row +4 and splits the first word into position and the two high bits
(`0x4E0C20–0x4E0C53`). The caller uses these row operands at
`0x48238C–0x4823B8` and reaches the word bake output at `0x48245C`.

**CONFIRMED.** The worked span uses arm 3 and palette 6 at game-folder
`cdcache.wsx+0x9EDD97`. See the [bank descriptor evidence](lol3-texture-palette-sources.md).

## Cache record to PNG

**CONFIRMED.** File-to-PNG colour is solved for the 10,669 raw and
span records listed below. The exporter follows the 40-row native cache
directory, then the four texture banks' descriptor and mip offsets
(`0x4FE4C2–0x4FE4FA`, `0x43F8F1–0x43F90B`,
`0x43F9A2–0x43FA1D`). It visits every nonempty mip entry.
All 15,118 entries in the game-folder `cdcache.wsx` (written by the game when it runs) have a unique record position
and an in-range arm-3 palette. The four other occupied allocations
are light maps.

| Pixel route | Flags | Records in the game-folder `cdcache.wsx` (written by the game when it runs) |
|---|---|---:|
| Raw indexed rows | 0x008B, 0x00A9, 0x00C3, 0x00E1, 0x808B, 0x80A9, 0x80C3, 0x80E1 | 4,194 |
| Indexed row spans | 0x028E, 0x02C6, 0x828E | 6,475 |
| Unconfirmed pixel route | 0x021A, 0x021E, 0x0252, 0x0256 | 4,429 |
| Unconfirmed copy branch | 0x02AC, 0x82AC | 20 |

**CONFIRMED.** The raw records contain exactly width × height bytes.
The native row selection is `0x4E0C60` or `0x4E0CA0`, with
both indexing from record +0xC by row × width. The 5,621 records
with 0x02C6 also select the span arm at `0x4E0BC0` and use the same
row header and index bytes as the 854 previously checked spans.
The native type-11 bake looks up every index within its span
(`0x48253E–0x48254A`) and zero-fills areas outside the span
(`0x482650–0x482690`). The PNG projects the unscaled scratch words
to RGB with the native five-bit component positions and ×8 expansion.
It sets alpha to 255 for bit 15 set and zero otherwise.

**CONFIRMED.** At cache file +0x12C776, index 4 is the first
nonzero index in the worked record at +0x12C6E2. Its little-endian
palette word at +0x9EDD9F is 0x1C67. The bake sets bit 15,
yielding 0x9C67. The exported 128×256 PNG reads
(56, 24, 56, 255) at (71, 33). The transparent gap at (0, 0)
has an all-zero scratch word.

**UNCONFIRMED.** The 4,429 entries in the first open group fail
the bounds or length rule for the generic row route. For example,
`cdcache.wsx+0x9D0F4B` starts a 49×31 record with a 1,380-byte
payload. Trace its resource type from the descriptor to the first
consumer that uses its +0xC word. The 20 entries in the second
group have a structurally valid span at +0xC, for example the
128×128 record at +0x10E53A. Flag bit 0x20 instead selects the
fixed-width helper at `0x4E0BAC–0x4E0BB5`. Trace the higher-level
branch that admits this class before treating those bytes as rows.

**CONFIRMED.** Device texture-format enumeration tests RGB555
masks 0x7C00/0x03E0/0x001F and an alternate RGB444 mask set
0x0F00/0x00F0/0x000F (`0x495040–0x4950C6`).
The returned masks affect transfer choice at
`0x49518F–0x4951BA` and `0x495E8D–0x495ECA`. This gives
the program's accepted formats. The selected device and final
composited colour remain **UNCONFIRMED** without a runtime witness.

```bash
python3 tools/lol3_texture_png.py --data DAT --offset 0x12C6E2 --out ../texture.png
python3 tools/lol3_texture_png.py --data DAT --check
```

The check decodes supported records in memory. It reports the palette
arm and bank count, all unconfirmed flags and individual malformed
records. It writes no files.
