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
contradictory storage and dispatch evidence. **CONFIRMED.** The PNG tool
`--check` counts those 20 records as unconfirmed (`0x02ac=15, 0x82ac=5`) and does not render them.

**CONFIRMED.** Device texture-format enumeration tests RGB555
masks 0x7C00/0x03E0/0x001F and an alternate RGB444 mask set
0x0F00/0x00F0/0x000F (`0x495040–0x4950C6`).
The returned masks affect transfer choice at
`0x49518F–0x4951BA` and `0x495E8D–0x495ECA`.

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

## Live Direct3D texture format

**CONFIRMED.** On Wine 9.0 with the built-in DirectDraw library and a
`1024x768` Xvfb display at 16-bit depth, the English retail `LOL3.DAT` (SHA-256 prefix
`9a9eb04c8f40`) reached its menu with the native `-WINDOW -MIJAS`
options. `-WINDOW` sets the flag at `0x4083CE`. `-MIJAS` skips the
logo call at `0x407574`. In Video Controls, the run chose `Direct3D: display`
and accept the `1024x768x32` mode that Wine offered in that run (on the 16-bit X display). It then loaded the
game-written player autosave (not shipped, not tracked) with SHA-256 prefix `df50eda48c27` (slot +0x498 = 5).
The trace used GDB through `winedbg --gdb` and Wine's
`WINEDEBUG=-all,+ddraw` log.

| Native observation | Measured value |
|---|---|
| Enumeration call `0x4950F7` and callback `0x495040` | The first two RGB candidates had masks `7C00/03E0/001F`. Flags and alpha were `0x40/0` and `0x41/0x8000`. |
| Return at `0x495199` and selected descriptor `0x661608` | Result 1 (an alpha-capable RGB format was found and copied: ctx+0x20 at `0x49508F`), pixel size 16, mask quartet `7C00/03E0/001F/8000`; selector 0 (R mask bit 15 clear and not `0xF00`, i.e. 555; 1 would be 565, 2 = 444). |
| Loaded level, selector at `0x66163C` and result at `0x661640` | Selector 0 and result 1 persisted, with a live device pointer in `0x65F434`. |
| Texture copy in Wine's DirectDraw trace | `IDirect3DTexture2::Load` copied between two 32×32 surfaces. Both `CreateSurface` descriptors requested the same 16-bit `7C00/03E0/001F/8000` format. |

**CONFIRMED (derived, not read in the debugger).** `[0x65F460]` was
zero when the callback accepted the RGB555 candidate. This follows
from the observed 555 descriptor and the only 555 copy path at
`0x495070–0x495092`, which skips the candidate when the flag is
nonzero. The flag is cleared at `0x472A6F` and read only at
`0x495072`. Four command-line options set it: `-D3DUSEARGB4444`
(string at `0x54AB60`) directly at `0x472AC1–0x472AD8`, and
`-D3DMONOLIGHTMAPS`, `-D3DNOVERTEXCOLOR` or `-D3DPERMEDIA2` (strings
at `0x54ABC4`, `0x54ABB0`, `0x54AB80`) through `[0x65F45C]`, which
`0x472A6A–0x472A79` copies into the flag. An enumerated RGB444
candidate reaches `0x4950B1–0x4950C6` without a flag test and does
not stop the enumeration (the callback returns 1).
**UNCONFIRMED.** Whether Wine's DirectDraw list contains an
`F00/0F0/00F` format, and whether a texture upload succeeds with the
flag set. To settle it, repeat the Wine run with `-D3DUSEARGB4444`.
Break at `0x4950B1` to see whether a 444 candidate arrives. After
`0x4951BA`, read the result `[0x661640]` and selector `[0x66163C]`
(2 means 444). Then check the `CreateSurface` masks and the
`IDirect3DTexture2::Load` result in the `+ddraw` log.

This is one device: Wine's DirectDraw translation layer enumerates
its own format list. **UNCONFIRMED.** A native Windows driver could
omit the 1555 format (result 0) or offer only 4444 (selector 2).
To settle it for a given driver, run the game on that Windows device
and read `[0x661640]` and `[0x66163C]` after `0x4951BA`.

### Live level-5 indexed row and upload

**CONFIRMED.** On the same English retail executable and Direct3D
device choice, one null-sink instance ran from a disposable
copy on private 16-bit Xvfb. Before launch, the copied autosave
was `df50eda48c27` (+0x498 = 5). The trace did not log a
slot identity at restore. During the selected Load Autosave
path, the debugger sampled the first `0x495290` invocation with
live level byte `[0x5708DB]` equal to 5, at least eight input
indices and a non-grey first palette word. The original call
at `0x495630` passed 128 indices. The indexed helper uses the low word
of `[[0x54AAB8] + 4*index]` (`0x4952B4–0x4952D6`).
In this sample the table was at `0x65D3F0`, the input at
`0x02045918` and the destination at `0x02191AD0`.
At return `0x495635`, all 128 destination words agreed
with their individual lookups in memory. The trace printed
the first 16 input bytes and output words and the match count for
all 128. The live table has no confirmed join to a particular
cache record or documented palette source.

| Row index byte | First observed staging word | Alpha bit and RGB555 channels |
|---|---|---|
| `0xDF` | `0xDAB4` | 1, 22/21/20 |
| `0x82` | `0xDEF6` | 1, 23/23/22 |
| `0x46` | `0xEB5B` | 1, 26/26/27 |
| `0x84` | `0xB18C` | 1, 12/12/12 |

The staging path checks the static lock-pointer cell
`0x66164C` (`0x4955CF–0x4955D9`). The following texture load
(`0x49658C`) returned 0 at `0x49658F` with selected
16-bit masks `7C00/03E0/001F/8000`.
An earlier load sample with the same call and descriptor
gave the sequence `0x70/0x5F/0x95/0x68` mapping to
`0x8421/0x9084/0x9CE7/0x98C6`.

**UNCONFIRMED.** Final composition for an identified texel.
The source and locked staging bytes establish the indexed
colour conversion and the upload result. To measure the draw,
record the texture handle stored at `0x4965CE` for this upload.
Follow that handle to a level draw and choose an interior
pixel with recorded UV, base word, light-map word or vertex
colour, filtering, and blend state. Compare the render-target
word before presentation and the same pixel in the presented
surface. The device-selection test above covers other formats.
The SMD raster and row flags below have separate tests.

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

### Projection and depth within one slice

**CONFIRMED.** The step table at `0x7D8D98` stores two signed bytes per
code. The low nibble is the delta added to the first coordinate byte (x,
used with `a` and `d`) and the high nibble the delta added to the
second (y, used with `b` and `e`). Each nibble uses the signed range −8 through 7
(`0x4E2DB0–0x4E2DEB`). The callback adds the deltas to the initial
unsigned byte coordinates using dword addition (`0x4E3E63–0x4E3E7A`,
`0x4E3EAD–0x4E3EC8`). In the four frames above and the direct-read frame
at `SLICECD1.WSX+0x82A082`, all 148,320 steps stayed within the
0–255 range of both tables (a one-off measurement; not part of `--check`). At expanded `cqb4.smd` frame +0x130 the four
steps reach (15, 154), (13, 154), (13, 152) and (15, 152).

**CONFIRMED.** The projection setup stores six dwords `a` through `f`
at `0x7D8550` through `0x7D8564`, using the x87 conversion that truncates
toward zero (`0x4E3947–0x4E399E`, `0x518450–0x518476`). Four 256-entry
tables store `i*a`, `i*b`, `i*d` and `i*e` at `0x7D7950`, `0x7D7D50`,
`0x7D8150` and `0x7D8F98`, respectively
(`0x4E39A3–0x4E3A0A`). The callback treats dword sums modulo 2³².

**CONFIRMED.** The last step of the setup scales the first
three floats of the affine transform at `0x7D8570` by 65536
and the next three by 64. `0x4E3883–0x4E3890` supplies those
two floats to `0x4E3B80`, which constructs a diagonal transform
`(65536,0,0,0,64,0)`. The x87 multiplication at
`0x4E3895–0x4E3943` composes it on the left. With source
floats `M[0..5]`, the six dwords are the truncations of
`(65536*M[0], 65536*M[1], 65536*M[2], 64*M[3], 64*M[4], 64*M[5])`.
The first goes directly from the x87 stack to the conversion.
The remaining five first round through float stores at
`0x4E38DC`, `0x4E3904`, `0x4E3927`, `0x4E393F` and
`0x4E3943`.

**CONFIRMED.** Bit 0 of the reference +0x0C folds the input
angle by subtracting the float at `0x540778` when the angle
is at least π, or the float at `0x54077C` otherwise
(`0x4E30D8–0x4E3110`). The second float is −π.
The row loop selects slices in descending order. Equal heights
visit `slice_count - 1` through zero (`0x4E3140–0x4E318C`).
For unequal heights, the setup divides the slice count by the
effective output height, starts the phase at 0.0 (the float at `0x54076C`), and subtracts
1.0 while the phase strictly exceeds 1.0, backing up one slice
each time. It adds the ratio for the next output row
(`0x4E31E4–0x4E3275`; constants `0x540768/0x54076C`).
When `[0x7D93AC]` is nonzero on this path, `0x4E2FD0`
supplies crop fractions `top` and `bottom`. The destination
pointer is advanced by `trunc(original_height * top) * pitch`
and effective height becomes
`trunc(original_height * (1 - (top + bottom)))`
(`0x4E31A2–0x4E31E0`). Row pitch comes from the surface at
`0x4E30B8–0x4E30C9`.

| Quantity | Computation | Native witness |
|---|---|---|
| Column of initial or updated endpoint | `signed32(a*x + b*y + c) >> 16` | `0x4E3E72–0x4E3E8C`, `0x4E3ECA–0x4E3EFA` |
| Depth of updated endpoint | `unsigned32(d*x + e*y + f)` | `0x4E3EDC–0x4E3EF6` |
| Columns visited by each step | `max(0, previous_column)` up to but excluding `current_column`. The next step uses the unclamped current column. | `0x4E3EFD–0x4E3F0D`, `0x4E3F29–0x4E3F35` |
| Index and depth write | The step's palette index and endpoint depth replace the corresponding cells only if the new depth is strictly lower. Depth cells start at `0xFFFFFFFF` for each row. | `0x4E3F14–0x4E3F2F`, `0x4E311D–0x4E313A`, `0x4E316B–0x4E3183`, `0x4E324C–0x4E3264` |

With constructed coefficients `(65536, 0, 0, 0, 1, 0)` and a clear depth
row, the first `cqb4.smd` run alone projects to columns 15, 15, 13, 13,
15 in order. Only the last step writes. Columns 13 and 14 both receive
index `0x1C` from the stored second vector and depth 152. This is a worked example of the mapped formula on original run bytes; the coefficients are constructed, not captured from the game.

**UNCONFIRMED.** A complete original raster still needs a matched runtime
witness. At `0x4E1149`, use the reference pointer at `[ESP]` to match the
filename and frame. Capture the six coefficient dwords at `0x4E39A3`.
Before the callback call at `0x4E3161` or `0x4E3242`, record the slice
index at `[ESP]` and row pointer at `[ESP+4]`. Compare the stored index,
the remapped index at `0x4E3409` if that path ran, and the write at
`0x4E3F22` (index `DL`, depth `ECX`, column `ESI`, row base `EBX`).
At `0x4E3306`, compare the indexed bytes at `ESI+0xC` with the predicted
rows. This would verify the selected frame, remap and row placement
together, before the later display conversion.

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

**CONFIRMED.** For the 20 source mips (four banks) of the cache's
flag-`0x02AC`/`0x82AC` records, the selected
helper sets start column and row flags to zero and the count
to the stored width (`0x4E0CA8–0x4E0CD6`). An unscaled bake
uses each returned byte as an index into the 256-word table
(`0x48234C–0x48238F`, `0x482409–0x48245C`,
`0x4824F4–0x48254E`). The byte pointer is earlier than the
span pixel pointer by `4*(row+1)`, and the last `4*height`
bytes of the stored payload are outside the unscaled read.
With scaling, the same helper receives
`min(input_height-1, (step/2 + out_y*step) >> 16)`,
where `step = trunc((input_height << 16)/output_height)`
(`0x482316–0x48238C`, `0x48249A–0x4824AE`).
The original source dimensions are equal in X and Y at
each mip, `128,64,32,16,8` in order. Comparing the indexed
matrices before lookup gives 500, 244, 116, 52 and 24
different positions per bank, in mip order.

| Original .TE_ file offset | Descriptor in expanded bank | Expanded mip offsets, 0–4 |
|---|---|---|
| `QWOD0.WSX+0x36` | +0x1081DC | +0x10E104, +0x112310, +0x11341C, +0x1138A8, +0x1139F4 |
| `BUPP1.WSX+0x36` | +0x30C3A5 | +0x363D8D, +0x367F99, +0x3690A5, +0x369531, +0x36967D |
| `EWOD1.WSX+0x36` | +0x1ED42E | +0x2084B0, +0x20C6BC, +0x20D7C8, +0x20DC54, +0x20DDA0 |
| `RVOL0.WSX+0x36` | +0xABD99 | +0xB11A7, +0xB53B3, +0xB64BF, +0xB694B, +0xB6A97 |

`check_all.py` runs `tools/lol3_native_checks.py --check`, which checks the
pickup and copy-dispatch anchors, and adds `--decode-copy` when liblzo2 is
installed; the SMD scale, slice and crop addresses are cited, not
machine-checked. The command
`tools/lol3_native_checks.py --data DAT --check --decode-copy`
replays the fixed-width and span index reads on the shipped
archives using liblzo2. It checks the dispatch instructions,
all row headers, both first indexes, their palette witness
and the two-matrix difference counts. It needs no game-written
cache and writes no images. **CONFIRMED.** All 18 banks pass the same
structural read for their five flagged mips, 90 in total. The span
interpretation reads index 3 throughout those mips. The difference counts
measure where the row-header bytes fall under the fixed-width helper.

**CONFIRMED.** In the remap dispatcher, both words masked with 0x211
give 0x200, selecting `0x42136E` (`0x421326–0x421345`). This path
selects the same fixed-width helper, then uses its pointer and count
to replace each indexed byte through a remap table (`0x42136E–0x4213C1`).
The final flag write sets 0x100 and preserves 0x20
(`0x4213C3–0x4213CA`). Whether this runs on the live texture instances
before the bake remains **UNCONFIRMED**. The remap routine `0x421320`
has two callers. `0x44B440` is inside the resource resolver `0x44B130`.
It runs only when the resolver's third argument is nonzero, the dword
`[0x549C0C]` is nonzero (stored value 1; other code
rewrites it) and record bit 0x100 is clear (`0x44B39D–0x44B3FC`); it is also skipped when
source word +8 has both bits of 0x4010 set, a path that copies bit 0x100
from the other record (`0x44B3B6–0x44B3F3`).
The other caller, `0x4E7CC3`, remaps the record at `[0x7E3120]`.
A static search did not bind the bake's record to either path.
To settle it, break at `0x421326` and compare `EBX` with the record
pointer recorded at `0x482311` below.

**UNCONFIRMED.** Which bytes reach a draw or upload for this
resource class. Load QWOD0 and BUPP1 separately. Break on
`0x44B130` for the arm-3 descriptor whose initial key word is
1 or 11, respectively. Record the resource pointer after the
vtable lookup at `0x44B2B2`. At `0x482311` record the record pointer
passed to `0x4E0BA0` and its flags. For row 0, capture the helper and
the pointer it returns at `0x48238C–0x48238F`. Follow the first index
into the type-11 bake at `0x48253E–0x48254A`. With the original
indexes and palette, a return of +0xC predicts `0x8000` and a return
of +0x10 predicts `0x83C0`. If the bytes change first, check the
remap write at `0x4213AD` and use the observed index with the active
palette before comparing the output word.
