# LoL3 questions to test in the original Windows game

Use a disposable copy of your own English retail installation
(`LOL3.DAT` is 1,643,520 bytes). `LOL3.EXE` is a launcher that starts
`LOL3.DAT` as a child process, so enable child-process debugging
(WinDbg `.childdbg 1`) or attach x32dbg to the `LOL3.DAT` process
after launch. Record the renderer, display mode and whether a
compatibility wrapper is in use. `LOL3.DAT` has no relocations and
always loads at `0x400000`, so the addresses here are used as they
are; if the module base differs, you are in the wrong process.

Some probes were also tried on edited saves: copies of a game-written save with a few bytes changed. [Edited saves](EDITED_SAVES.md) lists those runs and what a game-written save would still add.

## Remaining probes

### Q6. Which bytes does the texture renderer consume?

The [SMD test](lol3-texture-bake.md#slice-directory-and-run-decoder) and
[projection test](lol3-texture-bake.md#projection-and-depth-within-one-slice)
give shipped frame offsets for all four slice flags and, from six captured
coefficients, the predicted indexed output rows. The
[row-flag test](lol3-texture-bake.md#two-ambiguous-row-flags) gives the
first-pixel predictions for the two unresolved row flags. Use those tests to
identify the source buffer and output words before testing display conversion.

Parked (not run); see [Parked probes](#parked-probes-not-run).

### Q12. Which live cast consumes an alternate resource?

Question: [Q12 in OPEN_QUESTIONS](OPEN_QUESTIONS.md).

**CONFIRMED.** Spell IDs 0x54 and 0x59 can call `0x4329C0(-1)`
when `[0x570AB9]` selects that path. The other bypass can call
`0x432AD0(-1)` when `[0x581A21]` selects it
(`0x4A46C1–0x4A46F3`, `0x4A5BB0–0x4A5BCE`,
`0x4A5A0D–0x4A5A54`). [Cast and cost evidence](lol3-spell-dispatch.md#player-cast-and-cost)

**CONFIRMED, setup result.** A copied level-5 autosave had 20 mana,
zero for both alternate selectors and all five cast slots empty
(`0x4282FA–0x42830C`). The loader stayed in the progress-sound
wait at `0x46F68F–0x46F69B` so the configured cast keys did not reach the payment branch. The wait
does not depend on the sound result: `0x46F55B` sets the flag whatever
happens; set `[0x65BD64]` to 0 in the debugger to continue (a patched run).
[Live cast setup](lol3-spell-dispatch.md#live-cast-setup)

**CONFIRMED, resource producers.** Ancient's Stone and Force Pod
add one to `0x570AB9` through `0x49FB23`. Mana Cluster adds one to
`0x581A21` through `0x4A6133`.
[Original item definitions and counters](lol3-spell-dispatch.md#producers-of-the-alternate-counters)

**CONFIRMED, live first-counter debit.** With a private null sink,
spell `0x59` spent one charge (35 → 34) via `0x4329D0`, with mana
still 437. A separate cast of `0x57` spent 22 mana via `0x410014`.
The DLOW1 placement was constructed live, but the counter trial from
the lower floor left the cursor and `0x581A21` at zero.
[Live casts and original Mana Cluster locations](lol3-spell-dispatch.md#casts-with-a-null-sink)

**CONFIRMED, level-4 approach.** The null-sink retry restored
the DLOW1 placement (X −635, Z 4913, height 110, surface 1287).
Native save writes at `0x43766F` sampled the player at (−637, 4895, 52)
during a jump and (−638, 4927, 10) afterward on the lower
surface. Normal clicks left the cursor and second counter zero.
This probe is blocked until a run takes the item: the runner could not
reach the placement's height. The linked section names the
FLAIR placement on surface 3243 as the other route.
[Placement, trial values and alternate route](lol3-spell-dispatch.md#dlow1-approach-with-the-native-placement-live)

**UNCONFIRMED.** Native acquisition control and exact HUD feedback. Save with
fixed equipment, sufficient mana and spell 0x54 or 0x59 selected.
Watch `0x570AB9` while using a first-counter item, then cast. For
the second counter use Mana Cluster and spell ID 0x57 (`GLOBAL.WSX+0x67F2`), whose
admission reaches `0x4A46E2`. Compare the same cast before and after each
consumable. Record the producer, the new selector value, the
next accounting routine and the visible HUD change. A hit at `0x4329C0` or `0x432AD0` with
a −1 argument identifies the alternate counter to follow.
A negative debit at `0x40FFE0` and changed player +0x1B8
are the ordinary mana control. Keep any run where admission
fails separate from a successful alternate payment.

**CONFIRMED, edited-save run.** Ancient's Stone supplied the first
charge and `0x59` spent one. Mana Cluster supplied the second charge
at `0x4A6133`. Spell `0x57` then took the second counter from 1 to 0
at `0x432AE0`. The ordinary mana writer recorded a 22-mana cost
for `0x57` with the selector zero and no negative write in the
charged cast. A native acquisition control and exact HUD indicator
remain open.
[Exact bytes and native debit trace](lol3-spell-dispatch.md#casts-with-edited-quick-slots)

Parked (not run); see [Parked probes](#parked-probes-not-run).

## Parked probes (not run)

These running-game tests were planned and then parked. No one will run
them here. Each one is "not run": it has no result and the question it
belongs to keeps its state. A reader with the original game and a
debugger can do it. Addresses are `LOL3.DAT` virtual addresses, used as
they are (see the top of this page).

Common setup: load a game-written slot, for example the level-5
autosave of the [controlled save setup](lol3-native-saves.md#controlled-save-setup).
The loader waits on the progress sound at `0x46F68F–0x46F69B`; use a
null sound sink, or set `[0x65BD64]` to 0 there (a patched run).

The first three tests look for a reader of bytes the level loaders skip.
The loaders seek over these bytes, so first find out whether they
reach memory at all. Log every read the level load makes (file,
position and length; for a MAP through the handle at `0x4357A0`, seeks
through `0x435A90`). A read that covers the bytes gives its caller. If
a copy of the bytes is in memory, set read watchpoints on it and play;
a hit gives the reader. No read and no hit over a stated stretch of
play bounds that stretch only.

- **The 2,873 rows at MAP +0x244 (not run).** Settles
  [Q8](OPEN_QUESTIONS.md). Bytes: MAP +0x244 to +0x2F2C, the leading
  u32 `0xB39` and 2,873 four-byte rows (in `QWOD0.WSX` from
  +0x72E4CF). The loader `0x43E6B0` reads 0x244 header bytes and its
  next read follows a seek to header +0x28. A reader of the span at
  header +0xCC is the answer; follow one row to its first typed use.
  [Shared block](lol3-map-odf-readers.md#shared-block-before-the-vertices).
- **The 630 section-0 names in the ODF (not run).** Settles the names
  in [Q5](OPEN_QUESTIONS.md). Bytes: the 22-byte slots after the
  counted 24-byte rows of section 0 (CKEEP's first, `Floor39`, at entry
  +0x5DC). `0x4AB420` reads exactly 24 × count (`0x4AB42E`). A read of
  a 22-byte slot, or a search for `Floor39` in memory followed by a
  read watch, is the test.
  [ODF header](lol3-map-odf-readers.md#odf-header-and-primary-tables).
- **The two MAP label spans (not run).** Settles the labels in
  [Q4](OPEN_QUESTIONS.md). Bytes: the 26-byte names at
  `u32(+0xC8) + 8 * u32(+0xC4)` and the 31-byte labels at
  `u32(+0xDC) + 4 * u32(+0xD8)` (the first label at
  `BUPP1.WSX+0x181E90C`). A reader that reaches either start and
  steps by 26 or 31 bytes is the answer.
  [Tail after the vertices](lol3-map-odf-readers.md#tail-after-the-vertices).
- **The PHT stream (not run).** Not a numbered question; it settles
  what reads the four [PHT files](formats/pht.md). Log every file the
  game opens from start to a level load. An open of `CYGNUS.PHT`,
  `QUANN.PHT`, `RAIDER.PHT` or `YUPA.PHT` gives the caller; then read
  watches on the loaded bytes show how a byte of the 0x1010000-byte
  cycle is picked. No open means these files are not read in that play.
- **Music key `0x1D4F73DA` (not run).** Settles
  [Q10](OPEN_QUESTIONS.md). Watch: the lookup entry `0x435880`
  (log the name and the returned archive row) and the call at
  `0x44A7F5` (its argument is the string at `EBX`). Play: start the
  game and travel through levels so the music changes; also try the
  `-SCORE` option. Result: a stop that returns the `music4.wsx` row
  with this key (directory at `music4.wsx+0x8A`) names the track.
  No such stop leaves the key unnamed for that play.
  [Music streams](formats/audio.md#music-streams).
- **The shipped `cdcache.wsx` (not run).** Settles
  [Q1](OPEN_QUESTIONS.md). Use an install where `DAT/cdcache.wsx` and
  the game-folder `CDCACHE.wsx` are both present. Watch: every file
  open, with its path, and the game-folder probe at `0x4E4C00`. Result:
  an open of the `DAT` copy, with the reads that follow (position and
  length), shows what the game takes from it. To tell which screen the
  block holds, lock the same surface at the fill loop (`0x4E4E34`,
  loop `0x4E4E61–0x4E4E95`) and compare its first 64,000 bytes with
  the shipped block.
  [Cache reader](lol3-wsx-reader.md#cache-index-lifecycle).
- **The second player-side actor at `0x5860F0` (not run).** Settles
  that part of [Q11](OPEN_QUESTIONS.md). Setup: a slot in BUPP1, near
  the opcode-0x1A record at `BUPP1.WSX+0x18C7FD3`. Watch: the call at
  `0x448316` (`ecx = 0x5860F0`) and `0x48EBE0`. Play: let that script
  run. Result: match the object's +4/+8 position to the character on
  screen, and note which character does action +4. That character is
  the answer.
  [Opcode 0x1A](lol3-script-opcodes.md).
- **Final colour of one textured wall pixel (not run).** Settles the
  final composition in [Q6](OPEN_QUESTIONS.md). Watch: record the
  texture handle stored at `0x4965CE` for one upload, as in the
  [level-5 upload test](lol3-texture-bake.md#live-level-5-indexed-row-and-upload).
  Follow that handle to a level draw and pick one pixel inside a wall.
  Record its UV, the texture word, the light-map word or vertex colour,
  filtering and blend state. Result: compare the render-target word
  before presentation with the same pixel on the presented screen.
  A match with the uploaded texture word means the draw added nothing;
  a difference is what the light map, filtering or blending added.
- **Remaining native casts (not run).** Settles native acquisition and
  the HUD feedback in [Q12](OPEN_QUESTIONS.md). Full test:
  [Q12](#q12-which-live-cast-consumes-an-alternate-resource). Setup:
  a slot with spell 0x54 or 0x59 ready and enough mana; for the item,
  the edited quick-slot recipe of the
  [edited-save run](lol3-spell-dispatch.md#casts-with-edited-quick-slots)
  if no game-written slot has it. Watch: `0x570AB9` and `0x581A21`,
  breaks at `0x4329C0` and `0x432AD0`, and the mana debit at
  `0x40FFE0`. Play: take a first-counter item and a Mana Cluster in
  ordinary play, then cast before and after each. Result: the producer,
  the new counter value and the visible HUD change. A −1 call at
  `0x4329C0` or `0x432AD0` shows which counter paid.

## Answered probes

### Q6. Which packed format does the live device select?

Question: [Q6 in OPEN_QUESTIONS](OPEN_QUESTIONS.md).

**CONFIRMED.** The original bake joins the cache palette to indexed
pixels and can expand 10,669 records to PNG. A device callback
accepts an RGB555 mask triple `7C00/03E0/001F` or an RGB444 triple
`0F00/00F0/000F`. It copies the format structure at
`0x495088` or `0x4950BF`. [Bake and presentation boundary](lol3-texture-bake.md)

**CONFIRMED, device selection answered for the Wine witness.** The
Direct3D display option selected 16-bit `7C00/03E0/001F/8000`, and
both sides of a traced texture copy used that descriptor.
[Live selection and texture-copy evidence](lol3-texture-bake.md#live-direct3d-texture-format)

**CONFIRMED, level-5 indexed upload.** At `0x495635` all 128
measured output words agree with lookups in the live table
`[0x54AAB8]` at `0x495290`. Index `0xDF` produced `0xDAB4`, and
`0x49658F` returned 0 with the same selected RGB555-alpha descriptor.
[Matched colour words and exact next test](lol3-texture-bake.md#live-level-5-indexed-row-and-upload)

**UNCONFIRMED.** Final composited colour for an identified texel.
Follow the texture handle stored at `0x4965CE` into a level
draw. Record one pixel's source texel, lighting and blend
inputs, then read the composed render target and the same
pixel after presentation. For a different device use
`0x495040` to record the candidate masks and check which
descriptor is passed on to the upload.

### Q9. What colours does the VQA frame callback present?

Question: [Q9 in OPEN_QUESTIONS](OPEN_QUESTIONS.md).

**ANSWERED, CONFIRMED for the Wine Direct3D run on a 16-bit display.** A private audio
null sink (no sound reaches the host) let the original intro play. The RGB565 surface received
`0x0841` at frame 16 pixel (3, 0), converted from archive word
`0x0421`. The offscreen, intermediate and primary DirectDraw
surfaces used the same masks.
[Native conversion and live presentation evidence](formats/vqa.md#live-introduction-opener)

**UNCONFIRMED.** Exact full-frame correspondence with the host
window capture, and the behaviour of other renderers or display formats.
The surface takes the display mode's format. The format reader
`0x409C70` counts the red, green and blue mask bits
(`0x409CAD–0x409CF1`). It picks mode 0 for 5/5/5 (`0x409D3D`),
1 for 5/5/6 (`0x409D36`), 2 for 5/6/5 (`0x409D27`) and 3 for
6/5/5 (`0x409D11`). To settle, in the RGB565 run dump the primary
surface after frame 16 is submitted (`0x47011B`) and compare every
pixel with the host window capture of the same frame. Then repeat on
a 15-bit desktop, break at `0x409D45` and check that `esi` is 0.

### Q13. Which original save bytes follow one controlled action?

Question: [Q13 in OPEN_QUESTIONS](OPEN_QUESTIONS.md).

**CONFIRMED, turn, step and quick-slot transfer.** A private null sink
let the progress sound return 0 at `0x46F59F` and the copied level-5
slot (a player save written by the game) restore at `0x436F7F`. Four F10 saves reached `0x43766F`, each
from the same source. A right turn changed player heading `+0x4A4`
from `0x8000` to `0x8D7D`. A forward input changed player Z at
`+0x4A0` from `0xF6F20000` to `0xF6EF7335`. The second position group
and both region words stayed fixed. Clicking the first quick slot
moved its reference from global selector 11 +0 to selector 7 +0x44,
leaving both position groups unchanged.
[Autosave offsets, hashes and writer traces](lol3-native-saves.md#controlled-saves-with-a-null-sink)

**ANSWERED for a controlled floor pickup, CONFIRMED.** One
instance ran from a disposable game copy with a private 16-bit
Xvfb display and null audio. A copied original level-2 player
slot restored at `0x43703E`. An item was
placed on the ground using normal input, then picked up with an
empty-hand left click. The native transfer at `0x49EDA0` copied
world row 489 to player row 4. Native saves before and after agree
with the predicted retirement mask, definition dword, allocation
bit and cursor transfer. The first position group agrees.
[Live values and slot offsets](lol3-native-saves.md#controlled-floor-pickup-in-bupp1)
