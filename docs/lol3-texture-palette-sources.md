# Texture cache palette sources

**CONFIRMED.** All 854 exact row-span records in the game-folder
`cdcache.wsx` each have one 58-byte bank descriptor and one 512-byte
source palette. They all use arm 3 of the [native palette lookup](lol3-texture-bake.md),
as shown by descriptor byte +0xD. Offsets in this page are in that cache.
Native VAs refer to the retail `LOL3.DAT`.

## Bank to palette join

| Location | Meaning and native evidence |
|---|---|
| Bank +0 | The loader reads 0x6A2 header bytes and checks that header dword 0 equals 38 (0x26) (`0x43F70F–0x43F73F`). Further header checks at `0x43F75D–0x43F79E`: +0x54 = 0x4200, +0x58 = 0x20000, +0x4C and +0x50 nonzero. The +0x40 = 0x300 compare is always true, because `0x43F73B` stores 0x300 there first; the tool's +0x40 filter is a data heuristic, not a native rule. |
| Bank +0x10, +0x4C, +0x2A8 | Descriptor table offset, byte length, and count. The seek/read is `0x43F859` for the separate 768-byte palette and `0x43F8F1–0x43F90B` for descriptors. The loop copies the first 14 descriptor bytes, advancing the source by 58 and destination by 14 (`0x43F925–0x43F940`). |
| Bank +0x14, descriptor +0x12 + 4*mip | Payload base and relative mip offset. Descriptor +0x26 + 4*mip supplies its nonzero byte length (`0x43F9A2–0x43FA1D`). Within that range, `0x43F9C7–0x43F9EB` registers mip 0 with length 0 when byte `[0x5D4ECE]` is 0, desc+0xC > 1, desc+4 or +6 > 0x80 and flag bit 0x8000 is clear (131 of the 178 mip-0 joins, including the worked example); the palette source is unchanged. What `[0x5D4ECE]` means is UNCONFIRMED. For these records the length equals 12 plus the span body length. |
| Bank +0x34, +0x70 | Offset and byte length of the 512-byte source palettes. The loader divides the length by 512, saves the first palette key, and registers each palette as a separate resource (`0x43F7E0–0x43F808`, `0x43FA4D–0x43FA9F`). |
| Descriptor +2, +0xD | Palette number u16 and arm u8. Arm 3 calls the level bank's vtable +8 at `0x44B70F` with key `[0x570238]+u16(+2)`. |

**CONFIRMED.** At `0x4369BD–0x4369CC` the world pointer is
`0x570170`. The level-load entry keeps it in EBP (`0x43D7BA`), passes it on at
`0x43DCB4–0x43DCB6` (`call 0x43DCF0`), which keeps it in EBP (`0x43DCF8`) and calls the texture
loader at `0x43E11F–0x43E121`. Every caller of `0x43D7B0` (`0x4078B1`, `0x4369CC`, `0x436CD4`) and of
the loader's other caller `0x43CBE0` (from `0x460354`) passes `0x570170`. The texture
loader saves the bank object at world +0x94 and its first palette key
at +0xC8 (`0x43F7ED`, `0x43F808`). These fields are the same globals
`0x570204` and `0x570238` read by the arm-3 selector. The native
palette file offset is therefore
`bank + u32(bank+0x34) + 512*u16(descriptor+2)`.

| Cache bank base | Source palette table | Span records |
|---:|---:|---:|
| `0x436` | `0x9ED197` | 191 |
| `0xAA5138` | `0x301844F` | 243 |
| `0x3239974` | `0x4C2DE97` | 395 |
| `0x52D6662` | `0x561CF4B` | 25 |

**CONFIRMED.** The 128×256 span at +`0x12C6E2` is mip 0 of
descriptor 7 at +`0x10876E`. Byte +0xD is 3 and word +2 is 6,
giving the 512-byte palette starting at +`0x9EDD97`.
The origin of the baked colour for these cache records is resolved.
Further graphics-device presentation is **UNCONFIRMED**.

```bash
python3 tools/lol3_texture_palettes.py --data DAT --check
python3 tools/lol3_texture_palettes.py --data DAT
```

The second form prints one JSON object of offsets and selector values
per texture. The check verifies each source range, every descriptor
join and the expected count of 854.

## Shared retail banks and the editor path

**CONFIRMED.** The shared loader at `0x43FF30` branches on
byte `[0x5D5380]`. The nonzero arm substitutes editor file
names ending `-global.tex` and `-spell.tex`
(`0x43FFE4–0x44000D`, original strings at
`LOL3.DAT+0x148060, +0x148020`). The zero arm uses
`global\global.tex` and `global\spell.tex`
(`0x44000F–0x44002F`). Both paths converge on the same
0x6A2-byte reads and check first dword 38 in both files
(`0x44002F–0x4400A0`). The analogous check for the
level bank includes +0x54 and +0x58 (`0x43F755–0x43F79E`).
Those fields are zero in both shipped shared banks. The optional
`-CONVERT_TEST` guard at `0x43F741–0x43F750` can bypass
the level reader's leading-dword comparison. Its following
bounds checks still run.

**CONFIRMED.** The shared loader reads both 58-byte descriptor
tables (`0x440164–0x4401BE`) and copies 14 bytes from each
row (`0x4401D0–0x4401E3`). Both palette classes share the
resource object at world +0xA8 (`0x570218`). World +0xD0 is
the first global palette key. World +0xD8 is that key plus
the global palette count. The loader derives the counts by
shifting header +0x70 right nine and registers 512-byte
palettes for each class (`0x4400E0–0x44012E`,
`0x440386–0x44041E`). Selectors 1 and 2 add descriptor
u16 +2 to those keys, respectively (`0x44B714–0x44B74C`).

| Retail source | Descriptor selector | Bound rows | Palette count | Example descriptor → source |
|---|---:|---:|---:|---|
| `DAT/LOCAL.WSX+0x1CE`, global bank | 1 | 692 | 691 | `+0x2BE5BE → +0x497815` (key 0) |
| `DAT/LOCAL.WSX+0x4F5E16`, spell bank | 2 | 4,635 | 419 | `+0x6DA227 → +0x22D1BFF` (key 0) |
| The 18 expanded level banks, e.g. `CKEEP.WSX+0x36` before expansion | 3 | 44,357 | Bank-specific | CKEEP expanded +0x1C2AD4 → +0x136022D (key 0) |

All twenty banks have an all-zero first 14-byte descriptor
prefix at index zero, including CKEEP expanded +0x1C2A9A
and the global bank at `LOCAL.WSX+0x2BE584`. All other
descriptors match the expected arm and select an in-bounds
palette via `bank + u32(+0x34) + 512 × u16(descriptor+2)`.
The census uses `tools/lol3_texture_archive.py --check --decode`.

**UNCONFIRMED.** A differently framed standalone LEVED
texture file remains open. The verified editor name branch
expects the same shared-bank header. The 18 retail level
entries all expand to ordinary banks, and the old CKEEP
`+1` lead was inside LZO bytes. A surviving editor output
with a different leading word or an execution trace of
`-CONVERT_TEST` accepting such a file would settle the alternate
layout. The shipped `-LEVED` string at `LOL3.DAT+0x144608`
is checked at `0x40E84C–0x40E859`, separately from the
shared loader's flag read.
