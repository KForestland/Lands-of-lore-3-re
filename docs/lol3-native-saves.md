# Native LoL3 save slots

VAs refer to the [English retail PE](lol3-lmf-reader.md). The
witnesses are 47 slots written by the original program, including the autosave: a player's own saves in the game's `SAVEGAME` folder (2024–2026), not shipped game data. Another player's saves reproduce the layout, not these exact counts.

Run [`lol3_save_header.py`](../tools/lol3_save_header.py) on a slot file to list preview, global and level offsets and lengths. It reads the header and writes its report to standard output.

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

**UNCONFIRMED, pickup from the world.** Left clicks on the bridge
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
slot within reach of a visible loose item, restore it for both
trials, and save after clicking only the item in the second trial.
At `0x4378C0` and `0x437F79`, identify the outgoing and incoming
rows by definition identity before decompression and file comparison.
Account for the selector's base XOR and pointer relocations before
attributing the decoded differences to the pickup.
