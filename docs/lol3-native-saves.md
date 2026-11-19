# Native LoL3 save slots

VAs refer to the [English retail PE](lol3-lmf-reader.md). The
witnesses are 47 slots written by the original program, including the autosave: a player's own saves in the game's `SAVEGAME` folder (2024–2026), not shipped game data. Another player's saves reproduce the layout, not these exact counts.

Run [`lol3_save_header.py`](../tools/lol3_save_header.py) on a slot file to print the named header fields, both directories and the other header bytes as hex with offsets. A level block long enough for its header also lists that block's 75 section starts and lengths. The report is written to a file only when `--out` is given.

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

**CONFIRMED** offsets, writer/reader addresses and labels. Each row cites the code that writes or reads the field.

| Slot offset | Native interpretation and evidence |
|---|---|
| +0 | Selected display name, copied as a NUL-terminated string at `0x4377B2–0x4377DD`. |
| +0x2C | Exact file length, stored before rewriting the header at `0x437A77–0x437A9B`. |
| +0x30/+0x34 | Version u32s 38 and 310, checked at `0x43CA0B–0x43CA1C`. |
| +0x38/+0x3C/+0x40 | Three u32 consistency stamps compared with `[0x5FE2E0]`, `[0x5FE280]`, `[0x5FE2DC]` at `0x43CA20–0x43CA4C`. |
| +0x44 | 20 level stamp dwords copied at `0x437630–0x437664`. The loader conditionally compares the 18 values used by levels 2–19 (`0x43CA4E–0x43CA7E`). |
| +0x9C | 768 bytes (the preview's 256-colour RGB palette) copied by `0x437804–0x43782C`. **CONFIRMED.** The writer copies them from the 768-byte table `0x57026E`, which the renderer reads as pixel byte × 3 + 0/1/2 (`0x46ED41–0x46ED84`). The slot reader `0x4366A0` copies +0x9C into a 0x300-byte buffer (`0x43681C–0x436837`), and `0x468A20` passes it to the palette routine `0x420A30` (`0x468AA2`), which walks 256 RGB triplets into `0x5D8748` (`0x420A46–0x420B27`). Header +0x98 holds 1 from the writer (`0x43781E`); the reader decodes the preview image only when it is nonzero (`0x436774–0x43677D`). |
| +0x39C/+0x3A0/+0x3A4 | Preview width, height, and data offset. Writer fills these fields and compresses the source at `0x4377FF–0x437854`. |
| +0x498 | Current level ID from `[0x5708DB]` (`0x4377EB–0x4377F8`, restored through `0x436CC1–0x436CD4`). |
| +0x49C, +0x4AA | Two 14-byte position groups, for the player at `0x5D4EE0` and the object at `0x5860F0`. Writer `0x43766F–0x43776D` reads two horizontal dwords at object +4/+8, zero-extends the heading word at object +0x26 into a dword, and writes a u16 region index. |
| +0x4B8 | 61 u32 absolute offsets, global selectors 0–60 (`0x437881–0x4378AF`, `0x4379C3–0x4379CA`). The next offset gives the end of each section. The first level offset ends the last global section. |
| +0x5B0, +0x600 | 18 u32 start offsets and 18 u32 byte lengths, indexed by level ID minus 2. The writer records the start and copies a per-level `.lsv` if available (`0x437A2B–0x437A68`, `0x43C660–0x43C72B`). |

**CONFIRMED.** Each group is two signed 16.16 horizontal
coordinates, a u32 holding a 16-bit turn angle, and a u16 region
index. `0x436F7F–0x436FC5` and `0x436FF3–0x437039` restore the
first and second groups. The placement routines store the first two
dwords at object +4/+8 and the low 16 angle bits at +0x26
(`0x40AD8D–0x40AD9D`, `0x48B6AA–0x48B6C5`).
`0x4070E6–0x407111` shifts both second-object coordinates by 16
before drawing. `0x40E19F–0x40E1C7` updates the first object's
heading, and `0x42C658–0x42C68B` subtracts the second heading from
a bearing computed from the two position pairs. The native loader
uses `region_base + 56 × index`, with `0xFFFF` selecting a null
pointer (`0x436F86–0x436FA5`, `0x436FFA–0x437019`).

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
Their 1,786 preview chunks decode to 640×480 bytes per slot. In the
`SAVEGAME` folder of our copy, `lol3_save_header.py`
lists 416 nonempty level blocks with 26,964 nonempty sections, whose
stored spans and declared expanded lengths are in the block directory.
The earlier count of 417 blocks and 27,038 sections predates that
autosave rewrite. For the slot
with SHA-256 prefix `704994e52a84`, its preview starts at +0x64C and
its first global section at +0x2214E. The 38 preview chunks expand
to 0x4B000 bytes. Its first level block begins at +0x2493A and
contains 130,702 bytes.

`lol3_save_writer.py --check` reads each game-written slot into
fields, using the compression bit (value 4) of the [selector
flags](#selector-payloads), and writes it again with every directory offset, block
header and length recomputed. All 47 slots come back byte for byte:
416 level blocks and 59,654 stored LZO packets. The packets are
copied, not compressed again, so this checks the container layout,
not a compressor. With liblzo2 each packet must also decode to its
expanded length; the decoded bytes are not compared with anything.

## Selector payloads

**CONFIRMED.** The global descriptor `0x438140` and the level descriptor `0x438940` name each selector. The global loader calls the first at `0x436D43` and the global writer calls it at `0x43789D`. The level reader `0x437340` calls the second at `0x43745B` and the level writer calls it at `0x437F3A`. Each descriptor compares the selector index with its bound (`0x3C` at `0x438144`, `0x4A` at `0x438944`) and jumps through a table of 4-byte arm addresses (`0x438848`, `0x439460`). That gives 61 global and 75 level selectors, and each table is followed by `90 90 90 90` padding. Each arm writes four results: the live address, the byte count, the unit and a flag byte. The table is those four results for all 61 global selectors and all 75 level selectors. `lol3_save_selectors.py --check` requires the table to match the program.

A zero live pointer skips the section (loader `0x436D4F`, global writer `0x4378B8`, level writer `0x437F53`). Flag bit 0 (value 1) is what the global loader (`0x436D57`) and the level reader (`0x43746F`) test before they read the section. The two writers do not test that bit. Flag bit 1 (value 2) selects the baseline XOR through `0x43C480` (loader `0x436D75`, global writer `0x4378C4`, level writer `0x437F7D`). On that path the save writer calls the global adjuster `0x439590` at `0x437928`, or the level adjuster `0x439B30` at `0x437FDC`, with direction 0 (`0x43791B`, `0x437FD2`). The loader calls the global adjuster on the XOR path at `0x436E14` and on the direct path at `0x436E83`. The level reader `0x437340`, called from the loader at `0x436F2E`, calls the level adjuster at `0x437513` and `0x43757A`. Flag bit 2 (value 4) selects compression: save `0x43C830` (`0x43792D`, `0x437980`, `0x437FE1`, `0x438036`), load `0x43C790` (global loader `0x436DB6`, `0x436E26`; level reader `0x4374A9`, `0x437525`). Flag bit 3 (value 8) is tested only by the level writer, together with the writer's second stack argument, at `0x437F61`. If that argument is zero and bit 3 is clear, the stored length is 0 (`0x43805C`).

Both adjusters return before their jump tables when the live pointer is zero, the byte count is zero, or the index is past the bound (`0x439598` and `0x4395A7`, bound `0x3C` at `0x4395B3`; `0x439B39` and `0x439B48`, bound `0x48` at `0x439B54`). Selectors 73 and 74 are past that bound. `0x43C410` copies one dword when its direction argument is 0, so the file stores the absolute value. When the direction is not 0, a source dword of zero is stored as zero (`0x43C46F`). A nonzero value is matched against 30 ranges. Base i is dword i of the direction object, and the end is that base plus dword i of the length row at direction +0x78 (signed compares). The stored result is the source dword plus the difference between this object's base and the direction object's base. If none of the 30 ranges contains the value, the index stays 30 and the addition still runs (`0x43C44C`).

The last column is which dwords that helper receives, as offsets from the live address. `--check` also counts the helper calls written in each arm. An arm that returns without calling it copies the bytes and does not relocate pointers. Level selector 38's arm calls `0x43A4E0` instead. That function switches on byte +0x64 through the table at `0x43AE70`, bound `0x94`, and those arms are not read here.

<!-- selectors:begin -->
| Selector | Descriptor | Live bytes | Byte count | Unit | Flags | Adjuster | Dwords passed to the pointer helper |
|---|---|---|---|---|---|---|---|
| Global 0 | `0x438154` | `0x5d4ee0` | `0x464` | `0x464` | `0x7` | `0x4395cb` | dwords at +0x104, +0x10C, +0x110, +0x190, +0x118, +0x11C, +0x114, +0x144, +0x148, +0x279, +0x27D, +0x12E, +0x132, +0x242 and +0x309; ten dwords from +0x335 step 4; then +0x10 and +0x14 |
| Global 1 | `0x43817d` | `[0x5d54c0]` | `[0x5d54c8]` | `0x1` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 2 | `0x4381aa` | `dword([0x6626bc]+0x0)` | `(dword([0x6626bc]+0x8)*dword([0x6626bc]+0xc))` | `dword([0x6626bc]+0xc)` | `0x7` | `0x43978b` | each record's dwords at +0 and +0xC, stride = the unit, while the record start is below the byte count |
| Global 3 | `0x4381b4` | `dword([0x6626bc]+0x4)` | `(dword([0x6626bc]+0x8)>>3)` | `0x1` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 4 | `0x4381be` | `0x570900` | `0x12fa1` | `0x12fa1` | `0x7` | `0x4397f9` | dwords at +0x205, +0x1115 and +0x12F89 |
| Global 5 | `0x4381e7` | `0x0` | `0x0` | `0x0` | `0x1` | `0x439abb` | returns without calling the pointer helper |
| Global 6 | `0x438210` | `0x570174` | `0x4` | `0x4` | `0x1` | `0x439abb` | returns without calling the pointer helper |
| Global 7 | `0x43821f` | `0x585444` | `0x68` | `0x68` | `0x1` | `0x43984b` | dwords at +0x44 and +0x4C |
| Global 8 | `0x438248` | `[0x662a90]` | `[0x662a94]` | `0x1` | `0x1` | `0x439abb` | returns without calling the pointer helper |
| Global 9 | `0x438274` | `0x58cbe2` | `0x30` | `0x30` | `0x3` | `0x439abb` | returns without calling the pointer helper |
| Global 10 | `0x43829d` | `0x5469b8` | `0xa0` | `0x10` | `0x1` | `0x43987b` | the dword at +0 of each record, stride = the unit, while the record start is below the byte count |
| Global 11 | `0x4382c6` | `0x546a58` | `0x50` | `0x10` | `0x1` | `0x43987b` | the dword at +0 of each record, stride = the unit, while the record start is below the byte count |
| Global 12 | `0x4382ef` | `0x546ef8` | `0x80` | `0x10` | `0x1` | `0x43987b` | the dword at +0 of each record, stride = the unit, while the record start is below the byte count |
| Global 13 | `0x438318` | `0x5479a8` | `0x190` | `0x10` | `0x1` | `0x43987b` | the dword at +0 of each record, stride = the unit, while the record start is below the byte count |
| Global 14 | `0x438341` | `0x548568` | `0x190` | `0x10` | `0x1` | `0x43987b` | the dword at +0 of each record, stride = the unit, while the record start is below the byte count |
| Global 15 | `0x43836a` | `0x5860f0` | `0x3670` | `0x3670` | `0x7` | `0x4398ba` | dwords at +0x10, +0x14, +0x34, +0x48, +0x4C, +0x3498 and +0x3610; then 0x23 groups of five records, record stride 0x48 and group stride 0x178, from +0xA0, dwords at +0 and +4 |
| Global 16 | `0x438393` | `0x5838b8` | `0x1b3a` | `0x1b3a` | `0x7` | `0x4399d9` | the dword at +0x1B2A; then 0x13 steps of 0x16E from +0, and each step also passes address 0x660F48 on both sides |
| Global 17 | `0x4383bc` | `[0x570964]` | `([0x570970]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 18 | `0x4383d2` | `[0x57097c]` | `([0x570988]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 19 | `0x4383e8` | `[0x570994]` | `([0x5709a0]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 20 | `0x4383ff` | `[0x5709ac]` | `([0x5709b8]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 21 | `0x438415` | `[0x5709c4]` | `([0x5709d0]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 22 | `0x43842b` | `[0x570a6c]` | `([0x570a78]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 23 | `0x438442` | `[0x5709dc]` | `([0x5709e8]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 24 | `0x438458` | `[0x5709f4]` | `([0x570a00]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 25 | `0x43846e` | `[0x570a0c]` | `([0x570a18]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 26 | `0x438485` | `[0x570a24]` | `([0x570a30]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 27 | `0x43849b` | `[0x570a54]` | `([0x570a60]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 28 | `0x4384b1` | `[0x570a3c]` | `([0x570a48]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 29 | `0x4384c8` | `[0x570a84]` | `([0x570a90]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 30 | `0x4384de` | `[0x57096c]` | `([0x570970]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 31 | `0x4384f4` | `[0x570984]` | `([0x570988]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 32 | `0x43850b` | `[0x57099c]` | `([0x5709a0]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 33 | `0x438521` | `[0x5709b4]` | `([0x5709b8]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 34 | `0x438537` | `[0x5709cc]` | `([0x5709d0]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 35 | `0x43854e` | `[0x570a74]` | `([0x570a78]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 36 | `0x438564` | `[0x5709e4]` | `([0x5709e8]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 37 | `0x43857a` | `[0x5709fc]` | `([0x570a00]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 38 | `0x438591` | `[0x570a14]` | `([0x570a18]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 39 | `0x4385a7` | `[0x570a2c]` | `([0x570a30]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 40 | `0x4385bd` | `[0x570a5c]` | `([0x570a60]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 41 | `0x4385d4` | `[0x570a44]` | `([0x570a48]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 42 | `0x4385ea` | `[0x570a8c]` | `([0x570a90]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 43 | `0x438600` | `[0x570968]` | `([0x570970]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 44 | `0x438617` | `[0x570980]` | `([0x570988]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 45 | `0x43862d` | `[0x570998]` | `([0x5709a0]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 46 | `0x438643` | `[0x5709b0]` | `([0x5709b8]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 47 | `0x43865a` | `[0x5709c8]` | `([0x5709d0]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 48 | `0x43866d` | `[0x570a70]` | `([0x570a78]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 49 | `0x438683` | `[0x5709e0]` | `([0x5709e8]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 50 | `0x43869a` | `[0x5709f8]` | `([0x570a00]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 51 | `0x4386ad` | `[0x570a10]` | `([0x570a18]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 52 | `0x4386c0` | `[0x570a28]` | `([0x570a30]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 53 | `0x4386d4` | `[0x570a58]` | `([0x570a60]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 54 | `0x438707` | `[0x570a40]` | `([0x570a48]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 55 | `0x43873a` | `[0x570a88]` | `([0x570a90]*0x4)` | `0x4` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 56 | `0x43876e` | `dword([0x6626c4]+0x0)` | `(dword([0x6626c4]+0x8)*dword([0x6626c4]+0xc))` | `dword([0x6626c4]+0xc)` | `0x7` | `0x439a3e` | each record's dwords at +0 and +0xC, stride = the unit, while the record start is below the byte count |
| Global 57 | `0x43879c` | `dword([0x6626c4]+0x4)` | `(dword([0x6626c4]+0x8)>>3)` | `0x1` | `0x7` | `0x439abb` | returns without calling the pointer helper |
| Global 58 | `0x4387cb` | `0x546610` | `0x3a8` | `0x24` | `0x1` | `0x439abb` | returns without calling the pointer helper |
| Global 59 | `0x4387f4` | `0x547308` | `0x69c` | `0x24` | `0x1` | `0x439abb` | returns without calling the pointer helper |
| Global 60 | `0x43881d` | `0x600858` | `0x4` | `0x4` | `0x1` | `0x439aa9` | the dword at +0 |
| Level 0 | `0x438954` | `[0x5898b8]` | `([0x5898bc]*0x12)` | `0x0` | `0x4` | `0x43a408` | returns without calling the pointer helper |
| Level 1 | `0x438984` | `[0x5898d8]` | `0x206c` | `0x0` | `0x9` | `0x43a408` | returns without calling the pointer helper |
| Level 2 | `0x4389ae` | `[0x5898dc]` | `([0x5898e0]*0x6)` | `0x0` | `0x4` | `0x43a408` | returns without calling the pointer helper |
| Level 3 | `0x4389de` | `0x5838a8` | `0xc` | `0xc` | `0x7` | `0x439bd7` | dwords at +0 and +4 |
| Level 4 | `0x438a07` | `[0x5838a8]` | `([0x5838b0]*0x8)` | `0x8` | `0x7` | `0x439b6c` | each record's dwords at +0 and +4, stride = the unit, while the record start is below the byte count |
| Level 5 | `0x438a1d` | `0x589760` | `0xc` | `0xc` | `0x7` | `0x439bd7` | dwords at +0 and +4 |
| Level 6 | `0x438a46` | `[0x589760]` | `([0x589768]*0x8)` | `0x8` | `0x7` | `0x439c00` | each record's dwords at +0 and +4, stride = the unit, while the record start is below the byte count |
| Level 7 | `0x438a5c` | `[0x7dea68]` | `[0x7dee70]` | `0x2` | `0x7` | `0x43a408` | returns without calling the pointer helper |
| Level 8 | `0x438a73` | `[0x7de740]` | `[0x7de744]` | `0x4` | `0x7` | `0x43a408` | returns without calling the pointer helper |
| Level 9 | `0x438a8a` | `[0x600844]` | `[0x600848]` | `0x2` | `0x7` | `0x43a408` | returns without calling the pointer helper |
| Level 10 | `0x438ab6` | `[0x7de738]` | `[0x7de73c]` | `0x4` | `0x7` | `0x43a408` | returns without calling the pointer helper |
| Level 11 | `0x438ae2` | `[0x57018c]` | `([0x5701ac]*0x8)` | `0x8` | `0x7` | `0x43a408` | returns without calling the pointer helper |
| Level 12 | `0x438b15` | `[0x570194]` | `([0x5701b4]*0x38)` | `0x38` | `0x7` | `0x439c6d` | the dword at +0 of each record, stride = the unit, while the record start is below the byte count |
| Level 13 | `0x438b4b` | `[0x570198]` | `([0x5701b8]*0x2c)` | `0x2c` | `0x7` | `0x43a408` | returns without calling the pointer helper |
| Level 14 | `0x438b80` | `[0x570190]` | `([0x5701b0]*0x8)` | `0x8` | `0x7` | `0x43a408` | returns without calling the pointer helper |
| Level 15 | `0x438bb3` | `[0x5701a0]` | `([0x5701c8]*0xc)` | `0x8` | `0x7` | `0x43a408` | returns without calling the pointer helper |
| Level 16 | `0x438be4` | `dword([0x7de720]+0x0)` | `(dword([0x7de720]+0x8)*dword([0x7de720]+0xc))` | `dword([0x7de720]+0xc)` | `0x5` | `0x439ca8` | each record's dwords at +0, +4, +8 and +0xC, stride = the unit, while the record start is below the byte count |
| Level 17 | `0x438c12` | `dword([0x7de720]+0x4)` | `(dword([0x7de720]+0x8)>>3)` | `0x1` | `0x5` | `0x43a408` | returns without calling the pointer helper |
| Level 18 | `0x438c41` | `dword([0x659ef4]+0x0)` | `(dword([0x659ef4]+0x8)*dword([0x659ef4]+0xc))` | `dword([0x659ef4]+0xc)` | `0x7` | `0x439d35` | each record's dwords at +0x34, +0x10 and +0x14, stride = the unit, while the record start is below the byte count |
| Level 19 | `0x438c4b` | `dword([0x65b794]+0x0)` | `(dword([0x65b794]+0x8)*dword([0x65b794]+0xc))` | `dword([0x65b794]+0xc)` | `0x7` | `0x439db1` | each record's dwords at +0x34, +0x38, +0x10 and +0x14, stride = the unit, while the record start is below the byte count |
| Level 20 | `0x438c55` | `[0x65b798]` | `([0x65b79c]*0x4)` | `0x4` | `0x7` | `0x43a408` | returns without calling the pointer helper |
| Level 21 | `0x438c69` | `dword([0x7d7718]+0x0)` | `(dword([0x7d7718]+0x8)*dword([0x7d7718]+0xc))` | `dword([0x7d7718]+0xc)` | `0x7` | `0x439e42` | each record's dwords at +0x44, +0x68, +0x6C, +0x90, +0xCC, +0x34, +0x10 and +0x14, stride = the unit, while the record start is below the byte count |
| Level 22 | `0x438c73` | `dword([0x7d77f0]+0x0)` | `(dword([0x7d77f0]+0x8)*dword([0x7d77f0]+0xc))` | `dword([0x7d77f0]+0xc)` | `0x7` | `0x439f27` | each record's dwords at +0x34, +0x38, +0x10 and +0x14, stride = the unit, while the record start is below the byte count |
| Level 23 | `0x438c7d` | `[0x7d77f4]` | `([0x7d77f8]*0x4)` | `0x4` | `0x7` | `0x43a408` | returns without calling the pointer helper |
| Level 24 | `0x438cb1` | `[0x5d54bc]` | `[0x5d54c4]` | `0x1` | `0x7` | `0x43a408` | returns without calling the pointer helper |
| Level 25 | `0x438cde` | `dword([0x7d7824]+0x0)` | `(dword([0x7d7824]+0x8)*dword([0x7d7824]+0xc))` | `dword([0x7d7824]+0xc)` | `0x7` | `0x439fb8` | each record's dwords at +0x34, +0x10 and +0x14, stride = the unit, while the record start is below the byte count |
| Level 26 | `0x438ce8` | `[0x5701cc]` | `([0x5701ec]*0x18)` | `0x18` | `0x7` | `0x43a408` | returns without calling the pointer helper |
| Level 27 | `0x438d1a` | `[0x5701dc]` | `([0x5701fc]*0x8)` | `0x8` | `0x7` | `0x43a408` | returns without calling the pointer helper |
| Level 28 | `0x438d4e` | `0x60083c` | `0x4` | `0x4` | `0x1` | `0x43a15d` | the dword at +0 |
| Level 29 | `0x438d77` | `0x600840` | `0x4` | `0x4` | `0x1` | `0x43a035` | the dword at +0 |
| Level 30 | `0x438d90` | `0x55d3a0` | `0x30` | `0x30` | `0x7` | `0x43a408` | returns without calling the pointer helper |
| Level 31 | `0x438db9` | `dword([0x6626c0]+0x0)` | `(dword([0x6626c0]+0x8)*dword([0x6626c0]+0xc))` | `dword([0x6626c0]+0xc)` | `0x7` | `0x43a04e` | each record's dwords at +0xC and +0, stride = the unit, while the record start is below the byte count |
| Level 32 | `0x438de7` | `dword([0x6626c0]+0x4)` | `(dword([0x6626c0]+0x8)>>3)` | `0x1` | `0x7` | `0x43a408` | returns without calling the pointer helper |
| Level 33 | `0x438e16` | `0x7d75f8` | `0x4` | `0x4` | `0x1` | `0x43a144` | the dword at +0 |
| Level 34 | `0x438e3f` | `0x7d772c` | `0x4` | `0x4` | `0x1` | `0x43a15d` | the dword at +0 |
| Level 35 | `0x438e58` | `0x7d7690` | `0x80` | `0x8` | `0x5` | `0x43a0b5` | the dword at +0 of each record, stride = the unit, while the record start is below the byte count |
| Level 36 | `0x438e81` | `0x7d7600` | `0x90` | `0x30` | `0x5` | `0x43a0f0` | the dword at +0 of each record, stride = the unit, while the record start is below the byte count |
| Level 37 | `0x438eaa` | `0x7d7710` | `0x4` | `0x4` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 38 | `0x438ec3` | `dword([0x660ca4]+0x0)` | `dword([0x660ca4]+0x4)` | `0x0` | `0x5` | `0x43a12b` | calls 0x43A4E0, which switches on byte +0x64 through the table at 0x43AE70 (bound 0x94). Those arms are not read here |
| Level 39 | `0x438eee` | `0x7d779c` | `0x4` | `0x4` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 40 | `0x438f17` | `0x7d7794` | `0x4` | `0x4` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 41 | `0x438f30` | `0x7d7798` | `0x4` | `0x4` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 42 | `0x438f59` | `0x7d77a0` | `0x4` | `0x4` | `0x1` | `0x43a144` | the dword at +0 |
| Level 43 | `0x438f82` | `0x7d77ac` | `0x4` | `0x4` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 44 | `0x438f9b` | `0x7d77a4` | `0x4` | `0x4` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 45 | `0x438fc4` | `0x7d77a8` | `0x4` | `0x4` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 46 | `0x438fed` | `0x7d77b0` | `0x4` | `0x4` | `0x1` | `0x43a15d` | the dword at +0 |
| Level 47 | `0x439006` | `0x54bbb4` | `0x4` | `0x4` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 48 | `0x43902f` | `0x662aac` | `0x4` | `0x4` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 49 | `0x439058` | `0x54bbb8` | `0x4` | `0x4` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 50 | `0x439071` | `0x662aa8` | `0x4` | `0x4` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 51 | `0x43909a` | `0x7d77dc` | `0x4` | `0x4` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 52 | `0x4390c3` | `0x7d77d0` | `0xc` | `0xc` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 53 | `0x4390ec` | `0x7d77e0` | `0x4` | `0x4` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 54 | `0x439115` | `0x7d77c4` | `0x4` | `0x4` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 55 | `0x43913e` | `0x54bf58` | `0x4` | `0x4` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 56 | `0x439157` | `0x7d77c8` | `0x4` | `0x4` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 57 | `0x439180` | `0x7d77b8` | `0xc` | `0xc` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 58 | `0x4391a9` | `0x7d77e8` | `0x4` | `0x4` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 59 | `0x4391c2` | `0x7d77e4` | `0x4` | `0x4` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 60 | `0x4391eb` | `0x54bf70` | `0x4` | `0x4` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 61 | `0x4393bc` | `0x662ab0` | `0xd000` | `0x34` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 62 | `0x4393e5` | `0x660ea8` | `0x4c` | `0x4` | `0x1` | `0x43a366` | the dword at +0 of each record, stride = the unit, while the record start is below the byte count |
| Level 63 | `0x43940e` | `0x660f48` | `0x4c` | `0x4` | `0x1` | `0x43a3a1` | the dword at +0 of each record, stride = the unit, while the record start is below the byte count |
| Level 64 | `0x439437` | `0x660ef8` | `0x4c` | `0x4` | `0x1` | `0x43a3d8` | the dword at +0 of each record, stride = the unit, while the record start is below the byte count |
| Level 65 | `0x439214` | `0x589998` | `0x2d54` | `0x2d54` | `0x5` | `0x43a176` | 0x13 dwords from +0x34 step 0x28; 0x100 dwords from +0x32C step 0x28; 0x13 dwords from +0x2B2C step 4; 8 dwords from +0x2B78 step 4; 3 dwords from +0x2B98 step 4; then the dwords at +0x2CDC and +0x2BA4 |
| Level 66 | `0x4392c1` | `0x6006a0` | `0xc` | `0xc` | `0x3` | `0x43a408` | returns without calling the pointer helper |
| Level 67 | `0x4392ea` | `[0x6006a0]` | `([0x6006a4]*0x4)` | `0x4` | `0x1` | `0x43a2d1` | the dword at +0 of each record, stride = the unit, while the record start is below the byte count |
| Level 68 | `0x43931e` | `0x6006ac` | `0xc` | `0xc` | `0x3` | `0x43a408` | returns without calling the pointer helper |
| Level 69 | `0x439347` | `[0x6006ac]` | `([0x6006b0]*0x4)` | `0x4` | `0x1` | `0x43a30c` | the dword at +0 of each record, stride = the unit, while the record start is below the byte count |
| Level 70 | `0x43936a` | `0x7e300c` | `0x4` | `0x4` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 71 | `0x439393` | `0x7df0a8` | `0x4` | `0x4` | `0x1` | `0x43a408` | returns without calling the pointer helper |
| Level 72 | `0x43923d` | `0x585cb0` | `0x140` | `0x140` | `0x1` | `0x43a347` | the dword at +0x18 |
| Level 73 | `0x439266` | `[0x65b7c4]` | `([0x65b7c0]*0xc)` | `0xc` | `0x7` | none | index above 0x48, so the adjuster returns before its jump table |
| Level 74 | `0x439298` | `0x58cb8d` | `0x51` | `0x51` | `0x3` | none | index above 0x48, so the adjuster returns before its jump table |
<!-- selectors:end -->

**UNCONFIRMED.** What each selector holds in play. The table gives where its bytes live and how they are copied, not what they mean; only the fields isolated by the controlled saves below have a meaning. Also open: the `0x94` arms of `0x43A4E0` and the unnamed header bytes. Test: save the same load before and after one controlled action and compare that selector's bytes ([test Q13](NEEDS_A_RUNNING_GAME.md#q13-which-original-save-bytes-follow-one-controlled-action)).

## Controlled save setup

**CONFIRMED.** The level-5 source slot (SHA-256 prefix
`df50eda48c27`, 406,041 bytes) holds the following values in
both saved groups (`+0x49C` and `+0x4AA`): dwords `08970000`,
`F6F20000`, `00008000`, then region word `18FD`. This is the
game-written player autosave used as the source, before the trials.

**CONFIRMED.** With audio disabled under Wine, the original
program opened that slot and started its progress meter. On
a fresh launch with the original `-NOSFX` and `-NOMUSIC` options,
the progress-sound call returned −1 at `0x46F59F` with
`[0x7F4DF8] = 0`. `[0x65BD64]` was still 1 at `0x46F68B`
and the thread stayed in the wait at `0x46F68F–0x46F69B`. The
loader did not reach `0x436F7F` and the save writer did not
reach `0x43766F`. Pressing the configured F10 autosave key
before and after the turn and forward inputs left the slot
identical by SHA-256. The meter's completion routine at
`0x46F8A0` clears the wait flag.

## Controlled saves with a null sink

**CONFIRMED.** In Wine 9.0 with `winepulse` directed to a private
44.1 kHz stereo PulseAudio null sink, the original progress sound
returned 0 at `0x46F59F`. The loader reached `0x436F7F` on each
reload of the copied level-5 source slot. F10 reached `0x43766F`
and wrote the following game-generated autosaves (written in this run; not shipped, not tracked). Each trial started
by restoring source `df50eda48c27` through Load Autosave.

| One input before saving | Slot SHA-256 prefix | Player X +0x49C | Player Z +0x4A0 | Player heading +0x4A4 | Region +0x4A8 |
|---|---|---|---|---|---|
| None | `c7d8e3130393` | `08970000` | `F6F20000` | `00008000` | `18FD` |
| Turn right | `19278fe2eca8` | `08970000` | `F6F20000` | `00008D7D` | `18FD` |
| Forward | `be9c5bc25543` | `08970000` | `F6EF7335` | `00008000` | `18FD` |
| Move the first quick-slot item to the cursor | `f755ae73e2ea` | `08970000` | `F6F20000` | `00008000` | `18FD` |

**CONFIRMED.** The dwords and headings match the live values from
`0x5D4EE0` and `0x5860F0` at `0x43766F–0x43776D`. The second group
`+0x4AA–+0x4B7` held `08970000 F6F20000 00008000 18FD` in all four
outputs. The right turn changed only the player's heading in the two
groups. The forward input changed only the player's Z coordinate in
those groups.

**CONFIRMED.** The quick-slot action moved the live item reference
`0x01BF5DD8` from `[0x546A58]` to the cursor at `[0x585488]`.
The first address is the start of global selector 11 (80 raw bytes,
`0x4382C6–0x4382EE`). The second is +0x44 of global selector 7
(104 raw bytes, `0x43821F–0x438247`). At `0x4378C0` both selectors
used flags 1. In both slots `+0x3C8` held the same player-item
pool base `0x01BF5DD8`, so the nonzero reference points to its row 0.

| Field | No-action slot offset and value | Quick-slot click offset and value |
|---|---|---|
| Selector 11 +0, first quick-slot reference | `+0x2204C` = `01BF5DD8` | `+0x21ECC` = `00000000` |
| Selector 11 +4, adjacent dword | `+0x22050` = `00000001` | `+0x21ED0` = `00000000` |
| Selector 7 +0x44, cursor reference | `+0x21E01` = `00000000` | `+0x21C81` = `01BF5DD8` |
| Selector 7 +0x64, dword | `+0x21E21` = `00000000` | `+0x21CA1` = `00000001` |

Selectors 7 and 11 in the turn and forward slots are byte-identical
to the no-action slot. Those two controls and the four table entries
account for all changes in selectors 7 and 11 in the quick-slot trial.

**CONFIRMED, earlier pickup setup.** Left clicks on the bridge
while holding that item did not create a loose item to pick up again.
For example, the crouch-and-click slot `f0289d9cc607` still has the
same cursor reference at `+0x21CA5`. A right click released the
cursor (`a4504f10d6d5`, zero at `+0x21CC5`), but produced no
witness of the item in the world. A new-game attempt to reach the
tutorial's loose item displayed the video-memory error whose text
is at `LOCALLNG.WSX+0x598770B`. The level-5 autosaves above can
be used for position and inventory controls.

**CONFIRMED, pickup test boundary.** In level 5 the writer reports
21,888 bytes in 72-byte rows for level selector 25, from the pool at
`[0x7D7824]` (`0x438CDE`, `0x438DBE–0x438DE6`). Global selectors
2 and 3 use the player-item pool at `[0x6626BC]`
(`0x4381AA–0x4381B9`, `0x438773–0x43879B`,
`0x4387A1–0x4387C4`). To settle the floor pickup, use one original
slot within reach of a visible loose item, restore it once, save with the cursor empty, then save
again after clicking the loose item.
At `0x4378C0` and `0x437F79`, identify the outgoing and incoming
rows by definition identity before decompression and file comparison.
Account for the selector's base XOR and pointer relocations before
attributing the decoded differences to the pickup.

### Predicted differences for one loose-item pickup

**CONFIRMED, native path.** World item vtable `0x540580+0x68`
selects `0x4D83A0`. The handler admits an empty cursor through
`0x4D83AC → 0x42EF50`, then checks world +0x18 bit 15,
`[0x5D5378]`, and the item class returned by `0x49F170`
(`0x4D83FC–0x4D842D`). It sends object event 3 at
`0x4D8479` and calls player receive at `0x4D8496`. With
`[0x545540] = 0` the receive mode is 1. The player can reject
the same world pointer already recorded at player +0x132
(`0x40B9BB`). The accepted path calls `0x49ED50` at
`0x40BA1F`, then passes operation 0x13 to the item's handler
at `0x40BA51`.

**CONFIRMED stores.** For a successful, ordinary
nonstacked pickup with a free player row and empty cursor,
let `i` be the outgoing world row and `j` the allocated
player row. The following offsets are relative to the section's
reconstructed bytes after applying the save's XOR base and
pointer adjustment. The table predicts a save pair if the
item handler and later game updates leave those values in place.

| Selector and decoded offset | Predicted state change | Native witness |
|---|---|---|
| Level 25 + `0x48*i+0x1C` | Set mask 0x80. The world item is skipped by the world lookup and can be reused. | Retirement `0x49EDC3 → 0x4D7370 → 0x4D7520`, store `0x4D75CB–0x4D75CE`, lookup `0x4D770A`, reuse `0x4D7647`. |
| Level 25 + `0x48*i` | In memory the first dword changes from item vtable `0x540580` to base vtable `0x539AC0`. Check this before section adjustment. | `0x4D75F8 → 0x441383`. |
| Level 25 + `0x48*i+0x10,+0x14,+0x1C` | Additional cleanup can update links, clear mask 0x2000, and clear masks 0x40000 and 0x04000000 when set. A neighbouring link can also change. | `0x4D7539`, `0x4464D0–0x4464E8`, `0x445EC0–0x445F0B`, `0x445E60 → 0x445D00–0x445D5E`. |
| Global 2 + `0x10*j` | Destination +0/+4/+8/+9 copy world +0x34/+0x38/+0x3C/+0x3D. Destination +0x0C is a zero dword before item operation 0x13. +0x0A and +0x0B have no store in the copy. | Destination selection `0x49ED81`, copy `0x49ED9A–0x49EDA0 → 0x49E560 → 0x49E910`, +0x0C reset `0x49E56D`. |
| Global 3 + `j >> 3` | Set bit `1 << (j & 7)` in the player-item bitmap. | `0x49ED89 → 0x4503E0`, bit scan/store `0x450402–0x45041F`. |
| Global 7 +0x44 and +0x64 | Cursor reference becomes the address of row `j`. Adjacent cursor dword increases by one. | `0x49EDD3` dispatches player vtable `0x538388+0x78`, empty cursor branch `0x40B8E3–0x40B8EB → 0x40B999`, stores `0x4224C6` and `0x4224F3`. |

The retirement path keeps the world row available to the pool lookup.
The freeing call at `0x445EF5` uses the link pool `[0x7DE720]`.
The world lookup tests `[0x7D7824]` and the retired flag
separately (`0x4D76E6–0x4D770E`). The save writer collects the full
world row range for selector 25, player rows for global 2 and
the player bitmap for global 3 (`0x439460+25*4`, `0x438DBE`,
`0x4381AA–0x4381B9`, `0x438773–0x4387CA`). Its level XOR,
adjustment and compression calls are at `0x437FC0`, `0x437FDC`
and `0x437FEF`. `tools/lol3_native_checks.py --data DAT --check`
verifies the vtable, writer selection, calls and store anchors.

### Controlled floor pickup in BUPP1

**CONFIRMED.** The original English retail game restored a copied
original player slot (SHA-256 prefix `802f83893758`)
in one instance from a disposable game copy. Level ID 2 selects
BUPP1: the second 27-byte entry of the level table, after AGLOB,
holds at `LOL3.DAT+0x14716E` the pointer `0x5496C0` to `levels\bupp1\bupp1`.
The game used a private 16-bit Xvfb display and a PulseAudio null sink. The progress sound
returned 0 at `0x46F59F` and the restore reached `0x43703E`.
In an outdoor area, an item was moved from the first quick slot
to the cursor and placed on the floor with the original left click
while looking down. F10 then wrote the floor control with an empty
cursor. One left click on the visible loose item reached
`0x4D83A0`; F10 saved the result at `0x43766F`.

In this run the live world pool had 1,216 rows of 72 bytes. At `0x49EDA0`,
row 489 (`0x09D03F20`) supplied definition pointer `0x09A96E59`
and three zero dwords from +0x34. The allocator returned player
row 4 (`0x01BF5E18`), initially zero. After the click, its first
dword held the same definition pointer. At `0x4D75CE` world +0x1C
was about to set bit 0x80. By the following save the flags were
`0x00100082` and the world vtable was `0x539AC0`, while
`[0x585488]` held the player row. This isolates the world-to-player
copy, retirement and cursor handoff of one definition.

| Section | Control / picked stored span starts | Decoded difference |
|---|---|---|
| Global 2 | `+0x191FA` / `+0x18FFF` | Only +0x40..+0x43 change, from zero to `59 6E A9 09` in player row 4. |
| Global 3 | `+0x194D7` / `+0x192DD` | Only +0 changes, `0xEF` → `0xFF` in the XOR data. Mask 0x10 corresponds to row 4. |
| Global 7 | `+0x1980A` / `+0x19610` | Raw +0x44 changes 0 → `0x01BF5E18` and +0x64 changes 0 → 1. Also observed +0x24 `0x17` → `0x16` and +0x50 0 → 1. |
| Global 11 | `+0x19A99` / `+0x1989F` | All 80 quick-slot bytes agree. The item is on the cursor after pickup. |
| Level 25 | `+0x408CA` / `+0x40701` | All 13 changed bytes are in world row 489 at decoded +0x8988. At row +0 the changed XOR dword is `0x00079F40`, equal to `0x540580 XOR 0x539AC0`. Row +0x1C changes `0x03` → `0x83` in XOR data. Bytes in the two link dwords +0x10/+0x14 and the flags at +0x1E also change. |

The two native slots were written in sequence from the same
restore. Their SHA-256 prefixes are `64b5d9ec325a` and
`2acfada073b0`. Slot +0x498 is 2 in both, and the first position
group `+0x49C..+0x4A9` agrees. The second position group changes.
The flags byte at world row +0x1E combines two changes: byte
bit 0x04 is flag mask `0x40000` and byte bit 0x10 is mask `0x100000`. The
retirement path clears mask `0x40000`, as predicted, between the entry at
`0x4D83A0` and the retirement store at `0x4D75CE`. The other
changed bit, mask `0x100000`, was already set at the click.
The control-to-click producer of that bit is **UNCONFIRMED**.
To find it, watch that dword between the control save and click.
The decoded values for selectors 2, 3 and 25 are XOR data.
Retirement, allocation and cursor values agree with the predicted
changes above. The new-game route was not needed for this comparison.

## Editing a copy of an original slot

**CONFIRMED, edited-save run.** English retail 1.07a loaded a
copy of the BUPP1 slot `5ae559b2cabe` with two new item rows
and two reassigned quick-cast references. The file grew from
1,807,734 to 1,807,771 bytes. The original loader reached
`0x43703E` and restored the intended references. It later wrote
a new autosave (`6bf815a1e022`, 1,821,427 bytes) through
`0x43766F`. All three headers passed the directory checks.

The source pointer map for this trial uses the definition
base at slot `+0x3B4` and pool base at `+0x3C8`. A definition
pointer uses the 139-byte stride at `0x4ACD17`. An item
reference uses a 16-byte row in global selector 2. Set the
matching bit in selector 3 when adding a row. The quick-cast
slots in selector 10 and quick item pockets in selector 11
contain pointers into that pool (descriptor arms
`0x43829D–0x4382EE`). The two existing pocket entries were
moved into empty pack slots in selector 13, whose arm is
`0x438318–0x438340`. Preserve the original definition and
pool range bases so a stored pointer can be translated on load.

Keep expanded section sizes, LZO chunk lengths and following
directory offsets consistent with the byte stream. A chunk is
two dwords (expanded length, packed length) and LZO1X data. The
trial re-encoded only the edited chunk in each of global
selectors 2 and 3 with liblzo2 `lzo1x_1_compress`, copied the
other chunks unchanged and edited the unpacked selectors 10, 11
and 13 in place. Re-applying the recipe to the source slot this
way gives the same 1,807,771 bytes (`90099b161497`). The trial
updated total length at `+0x2C` and added the combined
37-byte growth to later global and level starts. No level
block or length changed. Preserve version and data stamps
checked at `0x43CA0B–0x43CA7E`, and the saved pointer map.
For XOR-backed cells use the matching `global.img` or level
baseline. In this trial the base bytes for both edited item
rows and both occupancy cells were zero. No separate
payload checksum was recomputed on the accepted copy. The game's
own later autosave cleared the two used item rows and their
occupancy bits and stored the remaining pointers against its new
bases.
[Exact byte changes and original item use](lol3-spell-dispatch.md#casts-with-edited-quick-slots)

## Close-out

### Q13

**What was measured.** All 47 slot files give global selectors 5, 24, 37 and 50 a stored span of 0 bytes. The other 57 global selectors have a nonzero span in every one of those files. The descriptor arms name the live address, byte count, unit and flags of all 61 global selectors and all 75 level selectors, and the adjuster arms name the dwords passed to `0x43C410`.

**What was tried.** This compares the 61 directory offsets in each slot header and reads the descriptor and adjuster arms in the program. The page already records controlled saves for movement, the quick-slot transfer and the floor pickup.

**What would settle it.** The running-game test is not yet run ([test Q13](NEEDS_A_RUNNING_GAME.md#q13-which-original-save-bytes-follow-one-controlled-action), [probes not yet run](NEEDS_A_RUNNING_GAME.md#probes-not-yet-run)). It compares the original save bytes before and after one controlled action for each remaining selector payload. What each selector holds in play and the `0x94` arms of `0x43A4E0` are also still open.
