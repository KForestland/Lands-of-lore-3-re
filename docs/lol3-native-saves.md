# Native LoL3 save slots

VAs refer to the [English retail PE](lol3-lmf-reader.md). The
witnesses are 47 slots written by the original program, including the autosave: a player's own saves in the game's `SAVEGAME` folder (2024–2026), not shipped game data. Another player's saves reproduce the layout, not these exact counts.

## Names and entry points

**CONFIRMED.** The manual name constructor at `0x45B230` sets
the first byte to `$` and selects seven input bytes from the slot
name. It substitutes underscore for a missing or rejected byte
and uppercases through `0x5197A0` (`0x45B24A–0x45B29F`).
It forms `.000` through `.999` by splitting the candidate number
into three decimal digits and checks existing names
(`0x45B2A1–0x45B362`). The prefix is the `.\SAVEGAME` literal
at `LOL3.DAT+0x1488A8`. The automatic path uses the fixed
`.\SAVEGAME\$AUTOSAV.XXX` at +0x1489EC (`0x4681D0`).

**CONFIRMED.** Writer `0x4375E0` is called by the regular and
automatic paths at `0x45D4DB` and `0x4682EC`. The validation helper
at `0x43C910` requires a 0x64C-byte header, verifies full file
length against slot +0x2C and calls `0x43C9D0` for version/stamp
checks. The main loader `0x436BC0` redoes those checks and invokes
the level reader with the saved current ID
(`0x436C4F–0x436CD4`). It then reads global sections by the table at
`0x438848` (`0x436D27–0x436D75`).

## Slot header and stream

**CONFIRMED** offsets and writer/reader addresses; labels marked UNCONFIRMED are readings, not traced uses.

| Slot offset | Native interpretation and evidence |
|---|---|
| +0 | Selected display name, copied as a NUL-terminated string at `0x4377B2–0x4377DD`. |
| +0x2C | Exact file length, stored before rewriting the header at `0x437A77–0x437A9B`. |
| +0x30/+0x34 | Version u32s 38 and 310, checked at `0x43CA0B–0x43CA1C`. |
| +0x38/+0x3C/+0x40 | Three u32 consistency stamps compared with `[0x5FE2E0]`, `[0x5FE280]`, `[0x5FE2DC]` at `0x43CA20–0x43CA4C`. |
| +0x44 | 20 level stamp dwords copied at `0x437630–0x437664`. The loader conditionally compares the 18 values used by levels 2–19 (`0x43CA4E–0x43CA7E`). |
| +0x9C | 768 bytes (a preview palette: UNCONFIRMED) copied by `0x437804–0x43782C`. Their palette role is **UNCONFIRMED** from this writer alone. |
| +0x39C/+0x3A0/+0x3A4 | Preview width, height, and data offset. Writer fills these fields and compresses the source at `0x4377FF–0x437854`. |
| +0x498 | Current level ID from `[0x5708DB]` (`0x4377EB–0x4377F8`, restored through `0x436CC1–0x436CD4`). |
| +0x49C–+0x4B7 | Two sets of dwords (X/Z coordinates and an orientation: UNCONFIRMED readings) and a region u16. Writer fills these from object bases `0x5D4EE0` and `0x5860F0`, dividing the region-pointer difference by 56 (`0x43766F–0x43776D`). |
| +0x4B8 | 61 u32 absolute offsets, global selectors 0–60 (`0x437881–0x4378AF`, `0x4379C3–0x4379CA`). The next offset gives the end of each section. The first level offset ends the last global section. |
| +0x5B0, +0x600 | 18 u32 start offsets and 18 u32 byte lengths, indexed by level ID minus 2. The writer records the start and copies a per-level `.lsv` if available (`0x437A2B–0x437A68`, `0x43C660–0x43C72B`). |

**CONFIRMED.** Global selector 0 uses object `0x5D4EE0`, size
0x464 and flags 7 (`0x438154–0x43817C`). Selector 1 uses the
byte array `[0x5D54C0]` and its length `[0x5D54C8]`
(`0x43817D–0x4381A9`). Loader flag 1 permits reading and bit
4 selects compressed input (`0x436D57`, `0x436DB1–0x436DCE`).
Bit 2 requests a base-backed section using `global.img`
(file string at `LOL3.DAT+0x1470C8`). The writer reads the base
and XORs it with the live section (`0x43C480`: dword loop at `0x43C4A3–0x43C4A6`, then a byte tail; CONFIRMED), then applies its
section-specific adjustment (`0x43778B–0x4377A6`,
`0x4378C0–0x437928`).

## Level blocks and chunking

**CONFIRMED.** The standalone level writer at `0x437DC0` builds
the stem plus `.lsv` (file string at `LOL3.DAT+0x14712C`).
It reserves a 0x34C-byte block header and iterates 75 selectors
through `0x438940` (`0x437F0E–0x437F55`, `0x43806C–0x438073`).
At block +0 it stores total size. At +0xF4 it stores 75 relative
section starts. At +0x220 it stores 75 expanded lengths, with zero
for omitted sections. The final size and header write are at
`0x43808E–0x4380BA`. For each section, use the next offset or
the block length to determine the span.

**CONFIRMED.** Compression `0x43C830` takes up to 0x2000 source
bytes per chunk. It writes u32 expanded size, u32 packed size and
packed bytes (`0x43C875`, `0x43C8B2`, `0x43C8CA`). The reader
`0x43C790` reads the same frame, calls the LZO1X-compatible
decoder `0x4ECDB0` (called at `0x43C7F7`), and checks that the decoded lengths sum
to the required size.

**CONFIRMED.** All 47 files have matching total length and version,
monotonic global and level directories, and consistent level lengths.
Their 1,786 preview chunks decode to 640×480 bytes per slot. The
417 nonempty level blocks contain 27,038 nonempty sections, whose
stored spans and declared expanded lengths are in the block directory. For the slot
with SHA-256 prefix `704994e52a84`, its preview starts at +0x64C and
its first global section at +0x2214E. The 38 preview chunks expand
to 0x4B000 bytes. Its first level block begins at +0x2493A and
contains 130,702 bytes.

**UNCONFIRMED.** Meaning of every global and level payload and the
remaining header fields. The native selector entry points and
archive boundaries above give the starting sites. Name the saved
state from the individual selector's writers and confirm it on two
slots with a comparable state change.
