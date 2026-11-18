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
