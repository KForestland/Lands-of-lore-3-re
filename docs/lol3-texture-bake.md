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
| SMD slice frame references | 0x021A, 0x021E, 0x0252, 0x0256 | 4,429 |
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

The [two ambiguous row flags](#two-ambiguous-row-flags) have
contradictory storage and dispatch evidence. The PNG tool reports
those records as **UNCONFIRMED**.

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
python3 tools/lol3_texture_png.py --data DAT --check --decode-slices
```

The default check decodes indexed records in memory and verifies
linked SMD frame headers. Add `--decode-slices` with liblzo2 to
expand the SMD frames and validate every run. The tool reports the
palette arm, bank count, open flags and malformed records. Both
checks write no files.

## SMD slice frame references

**CONFIRMED.** In the game-folder `cdcache.wsx` (written by the game
when it runs), the 4,429 short payloads describe frames from the
slice archives. All carry bit 0x10 in bank descriptor +8. The
consumer at `0x44B3B6–0x44B3D8` tests that bit and supplies record
+0xC to the SMD resolver at `0x4E12D0`, subject to the caller and
renderer gates at `0x44B39D–0x44B3C8`. The remap dispatcher
`0x421320` masks the flags with 0x211 and calls `0x4E1660` when the result
is 0x210, unless bit 0x100 is already set (`0x421326–0x42135C`). That routine adds 0xC before the
same resolver and invokes the slice remapper at `0x4E16AA`.
See the [WSX hash and lookup](lol3-wsx-reader.md#resource-name-key).

| Offset from record +0xC | Field and native use |
|---|---|
| +0x00 | Type 3, tested by the remapper at `0x4E3341`. |
| +0x04/+0x08 | Identity and frame. The resolver compares both with a loaded SMD header and combines them for the frame cache (`0x4E130C–0x4E134D`). |
| +0x10 | NUL-terminated SMD filename. The reader formats `slice\%s` through the string at `0x549744` (`0x4E1389–0x4E13A7`). |
| +0x20 | Offset within the named archive member (`0x4E1549`, `0x4E15FB`). |
| +0x24 | Expanded byte count for allocation at `0x4E14D7–0x4E14E3`. |
| +0x28 | Stored byte count. Zero uses the direct read. A nonzero value carries a 16-byte header before the compressed bytes, with LZO at `0x4E1588–0x4E159F`. |
| +0x2C | Number of slice directory entries visited by the colour remap (`0x4E3330–0x4E333B`, `0x4E33CB–0x4E3419`). |

**CONFIRMED.** All 4,429 records (game-written cache) join 53 names via the WSX
`slice\` path in `SLICECD1..4.WSX`. Each linked source has
the matching first three frame dwords and a span inside its
entry. The first example, game-folder `cdcache.wsx+0x9D0F4B`, refers to
frame 0 of `cqb4.smd`, identity 0x3625618E. Its 30,260-byte
stored span starts at `SLICECD1.WSX+0x1A2CEF`; the 16-byte
prefix and the LZO expansion give 45,314 bytes. Slice table
entry 0 at expanded +0x10 points to +0x130, and entry 71
points to +0xB0A0. The 4,428 other sources consist of 4,427
compressed references and one direct reference. The direct
case is the first frame of `rbrbbush.smd` at
game-folder `cdcache.wsx+0x22C26D8`, expanded length 44,484 with stored
length zero, matching `SLICECD1.WSX+0x82A082`.

### Slice directory and run decoder

**CONFIRMED.** Each expanded frame starts with its 16-byte
header. At +0x10 is an array of u32 offsets from the frame start,
with the count from reference +0x2C (`0x4E30D8–0x4E30E3`,
`0x4E3E3C–0x4E3E46`). At each offset the first u32 gives the
run count. Each run stores u32 count `n`, u8 initial X, u8 initial
Y, then `n` step codes and `n` palette indexes. The callback
uses the two initial bytes in its projection tables, uses each
step code to index a signed byte pair, and reads its colour
from the second `n`-byte vector
(`0x4E3E5E–0x4E3EC8`, `0x4E3F19–0x4E3F42`).
The remapper changes that second vector in place
(`0x4E33F2–0x4E340C`).

**CONFIRMED.** Each of the four flags sets bit 0x20 and
clears bit 0x10 in the reference dword at payload +0xC.
With the zero argument passed from `0x4E1154`,
`0x4E2E5C–0x4E2E73` selects `0x4E3E30`.
The optional decoder expanded all 4,429 references and framed
1,979,019 runs. Each slice starts where the previous one ends.
The frame length equals the end of the last slice in every case.

| Flag | Frames checked | Runs framed | Game-folder cache example | Shipped frame offset | Expanded bytes | Slices |
|---|---:|---:|---|---|---:|---:|
| `0x021A` | 8 | 23,298 | `cdcache.wsx+0x14B9DB7` | `SLICECD1.WSX+0x7CF46C` | 49,852 | 244 |
| `0x021E` | 64 | 73,602 | `cdcache.wsx+0x2552CA` | `SLICECD1.WSX+0x1FE` | 93,100 | 296 |
| `0x0252` | 786 | 250,726 | `cdcache.wsx+0x21CBB28` | `SLICECD2.WSX+0x377D9` | 89,114 | 173 |
| `0x0256` | 3,571 | 1,631,393 | `cdcache.wsx+0x9D0F4B` | `SLICECD1.WSX+0x1A2CEF` | 45,314 | 72 |

For example, in the expanded `0x0256` witness, +0x130
starts one run of four steps at (15, 152). The step bytes are
`20 0E E0 02` and the colour indexes are `37 B2 B2 1C`.
The next slice starts at +0x142.

**UNCONFIRMED.** Exact rasterization still needs the per-draw
projection, palette remap and depth comparisons. For any of
the four witnesses, match its filename and frame number in the
resolve call at `0x4E1149`. At `0x4E3118` record the
projection inputs. When the callback executes at `0x4E3161`
or `0x4E3242`, record its source slice, destination row and
the active tables at `0x7D7950`, `0x7D7D50`,
`0x7D8D98`, `0x7D8150` and `0x7D8F98`.
For the first visible run, compare its stored indexes to those
after remap at `0x4E3409` and the writes at `0x4E3F22`.
At `0x4E3306`, compare the completed destination to the
projection from those inputs. The recorded tables and output
settle which projected pixels and colours a renderer must reproduce.

## Two ambiguous row flags

**CONFIRMED.** The 20 remaining records are five mip levels each
of four descriptors. Every payload has `height × (width + 4)`
bytes and every row starts with u16 column 0 and u16 count equal
to the mip width. The same four banks match their expanded
original `.TE_` entries byte for byte.
[Shipped bank comparison](formats/textures.md#compressed-level-wrapper)

| Flag | Level and bank key word | Descriptor in game-folder `cdcache.wsx` | Mip 0 | First palette word for index 3 |
|---|---|---|---|---|
| `0x02AC` | QWOD0, 1 | `+0x108612` | `+0x10E53A` | `+0x9ED19D` |
| `0x82AC` | BUPP1, 11 | `+0xDB14DD` | `+0xE08EC5` | `+0x3018855` |
| `0x02AC` | EWOD1, 1 | `+0x3426DA2` | `+0x3441E24` | `+0x4C2DE9D` |
| `0x02AC` | RVOL0, 1 | `+0x53823FB` | `+0x5387809` | `+0x561CF51` |

**CONFIRMED.** The selected native helper for the original flag
word is `0x4E0CA0` in both cases. The dispatch tests mask 0x20
before mask 0x04 (`0x4E0BAA–0x4E0BC0`). The helper returns
`record + 0xC + width × row` and count `width`
(`0x4E0CA8–0x4E0CD6`). The span candidate would instead
return `record + 0x10 + (width + 4) × row` for these records.
At row 0 of every witness (all 20 start `00 00`, width, then index 3) the original
bytes at those positions are 0 and 3, respectively. The
palette bake maps these to `0x8000` and `0x83C0`
(`0x4826DB–0x482720`). The two alternatives therefore
give different output even at the first pixel.

**UNCONFIRMED.** Which bytes reach a draw or upload for this
resource class. Load QWOD0 and BUPP1 separately. Break on
`0x44B130` for the arm-3 descriptor whose initial key word is
1 or 11, respectively. Record the resource pointer after the
vtable lookup at `0x44B2B2`, then its flag word and row-0
address at `0x4E0BA0` and the first output word of the
type-11 bake at `0x48253E–0x48254A`. A draw that keeps bit
0x20 and returns +0xC should produce `0x8000`. A draw
that passes the span bytes should produce `0x83C0`.
If the returned pointer or flags change before the row helper,
record that writer and re-evaluate the first stored index.
This distinguishes the two storage interpretations from an intervening
conversion before enabling PNG export for these flags.
