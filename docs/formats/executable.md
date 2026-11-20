# LoL3 PE images

**CONFIRMED.** `LOL3.DAT` and `LOL3.EXE` in the retail game directory are
x86 PE32 images with image base `0x400000`. Their DOS headers at `+0x3C`
point to PE headers at `+0xC8` and `+0xE0` respectively. The 40-byte section
rows begin at file `+0x1C0` and `+0x1D8`. Each gives an eight-byte name,
virtual size at row `+8`, RVA at `+0xC`, file size at `+0x10` and file
offset at `+0x14`. The bytes from the end of the four rows (`+0x260`,
`+0x278`) to the first section (`+0x400`, `+0x1000`) are zero.

| File | Section | RVA | Virtual bytes | File start | File bytes |
|---|---|---:|---:|---:|---:|
| `LOL3.DAT` | `.text` | `0x1000` | `0x1362E5` | `0x400` | `0x136400` |
| | `.rdata` | `0x138000` | `0xCE6A` | `0x136800` | `0xD000` |
| | `.data` | `0x145000` | `0x2B1B18` | `0x143800` | `0x17A00` |
| | `RemapTab` | `0x3F7000` | `0x24200` | `0x15B200` | `0x24200` |
| `LOL3.EXE` | `.text` | `0x1000` | `0xC8DA` | `0x1000` | `0xD000` |
| | `.rdata` | `0xE000` | `0x14AE` | `0xE000` | `0x2000` |
| | `.data` | `0x10000` | `0x27D8` | `0x10000` | `0x1000` |
| | `.rsrc` | `0x13000` | `0x1540` | `0x11000` | `0x2000` |

**CONFIRMED.** Subtract the image base and section RVA from a native
address and add the section's file start for a stored byte. For example,
`LOL3.DAT` entry RVA `0x1190A0` at file `+0xF0` becomes VA `0x5190A0`
and file offset `0x1184A0`. For `.data`, the virtual extent is larger
than its stored extent, so the offset formula applies only within the
file-backed range.

**CONFIRMED.** The section ranges in `LOL3.EXE` end at EOF `+0x13000`.
The corresponding end in `LOL3.DAT` is `+0x17F400`. Its debug directory
slot at `+0x170` gives RVA `0x1382F0` and size `0x54`, locating three
28-byte rows at file `+0x136AF0`. The rows' type, size, RVA and file
offset start at row `+0xC`. Their file ranges are adjacent:

| Type | File start | Bytes | Observed contents |
|---:|---:|---:|---|
| 4 | `0x17F400` | `0x110` | Image name begins at `+0x17F40C` |
| 3 | `0x17F510` | `0x11CD0` | Payload identified by type and extent |
| 2 | `0x1911E0` | `0x2A` | `NB10` starts the payload |

The remaining `0x1F6` bytes from `+0x19120A` to EOF `+0x191400` are
zero. The tool checks the section and debug-payload extents through EOF.
It prints addresses and sizes from the original files.

```sh
python3 tools/lol3_pe_layout.py --data DAT
python3 tools/lol3_pe_layout.py --data DAT --check
```
