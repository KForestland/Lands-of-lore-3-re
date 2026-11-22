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

## Launch-record rule and the runs of 20 November

Since 20 November 08:41 UTC every game launch must show four things in its record: (a) any debugger port listens on the local machine only, shown in the run log while it is up; (b) one new folder and one set of logs per launch, nothing overwritten; (c) a process listing after each launch; (d) every launch reported, failed ones included, with every live memory edit listed by address and bytes. The runs of 20 November below were made before that rule and did not meet it; their results stay as recorded observations, and no question state rests on them alone. A later run under the rule can confirm or replace them.

- The DLOW1 run of [20 November](#run-of-2026-11-20-dlow1-autosave-with-two-live-edits) (map rows, names, labels, PHT, music key, cache, second actor): (a) not met, the helper meant to keep the debugger port local failed to load, so the port was not shown to be local only; (b) not met, seven launches shared one folder and logs were overwritten; (c) not met, one listing for seven launches; (d) not met, six early-stopped launches and a third live edit (an audio-start flag set from 0 to 1) were not reported.
- The run for the final colour and the remaining casts: (a) not met, as above; (b) not met, it reused the previous run's game copy and overwrote its logs; (c) not met, one listing for four launches; (d) not met, four launches were reported as two.

## Remaining probes

### Q6. Which bytes does the texture renderer consume?

The [SMD test](lol3-texture-bake.md#slice-directory-and-run-decoder) and
[projection test](lol3-texture-bake.md#projection-and-depth-within-one-slice)
give shipped frame offsets for all four slice flags and, from six captured
coefficients, the predicted indexed output rows. The
[row-flag test](lol3-texture-bake.md#two-ambiguous-row-flags) gives the
first-pixel predictions for the two unresolved row flags. Use those tests to
identify the source buffer and output words before testing display conversion.

**21 November, partial runs (0066 and 0067).** The logged renderer was
`SoFtWaRe`. At (120, 80), the presented RGB565 sample was `0xCDB2` in both
runs. The software table inspected in 0067 supplied no filled bake tied to
that pixel. The [software span](lol3-texture-bake.md#software-wall-span)
gives the exact byte capture before remapping and the indexed destination
to follow through presentation. The final-colour pair remains open. The Direct3D upload has
an exact source-word collection point at `0x495635` just as the caller
returns from filling staging. Use a matched draw and presentation on that
renderer if following that route. [Final wall colour](OPEN_QUESTIONS.md#final-wall-colour)

In folder 0111, the mapping lookup found the engine header page and the instruction bytes were unread. In folder 0113, WineDbg identified the engine process and its command list did not open, so the memory read at the texel instruction could not be made. The final software wall colour stays open. One more thing to try is reading from the `LOL3.DAT` process. The spell and item runs found live values there and read zeros at the same addresses in the launcher. Verify the loaded texel instruction in the engine process, then trace the texel read through the indexed write to the presented pixel. [Process readings](#on-screen-spell-and-item-coverage)
Folders 0119 and 0120 read the expected nine bytes at `0x49D0A1` from the live `LOL3.DAT` process at base `0x400000` and both logged client word `0xCDB2` at (120, 80). Folder 0119 missed the debugger prompt. In 0120 WineDbg listed a hardware-assisted breakpoint, and the driver stopped before the colour trace. The source texel, remap byte and stored colour for that pixel remain unread.

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

**21 November, folder 0068.** Key 1 left mana at 165 and showed no cast
effect. The item click drew a hand and left the quick slots unchanged.
This run did not exercise the successful cast and item-use paths above.

## On-screen spell and item coverage

On 22 November, run 149 loaded the game-written `dsaf` save in Upper
Gladstone separately for each action. Both runs logged `SoFtWaRe` under
Wine and used read-only memory checks. The source save was unchanged.

| Action | Before and after on screen | Before and after in `LOL3.DAT` |
|---|---|---|
| Greater Light (`0x7A`), key **3**, folder 0117 | A light appears and brightens the wall. The mana oval looks the same in the two pictures. | Mana at `0x5D5098` fell from 437 to 420. |
| Vel's Fruit (`0x44`), key **6**, folder 0118 | The fruit stays in pocket 1 and its count falls from 3 to 2. | The pocket count at `0x546A5C` fell from 3 to 2. |

The `LOL3.DAT` child process held both live values. Reading the same
addresses in the `LOL3.EXE` launcher returned zero before and after
each action.

Spell `0x57` has a viewport effect in the charged-cast run on the edited
quick-slot setup. The charged HUD indication is still unseen. The key-3
`0x54` request showed the no-enemy message, so its cast effect is unseen.
The `0x59` trace records the native debit. Outside Greater Light and the
charged `0x57` trial, the [spell tables](lol3-spell-dispatch.md#definition-tables)
still lack matched launch records of the viewport effects.

The edited-slot trials followed Ancient's Stone (handler 6) and Mana
Cluster (handler 112) through their native counter writes and checked
consumption against a new save. No separate on-screen effect was isolated
for those uses. Vel's Fruit gives an on-screen use witness for handler 20.
The remaining [item-handler rows](lol3-item-dispatch.md#use-effects)
still lack an isolated on-screen use witness. The floor pickup in Q13
is an inventory transfer witness.

## Probes not yet run

These running-game tests have no settling result yet. A reader with the original
game and a debugger can run them; the question each belongs to keeps its
state until then. A partial run is recorded under the probe it belongs
to, with its date and labels; it does not move the question. Addresses are `LOL3.DAT` virtual addresses, used as
they are (see the top of this page).

Common setup: load a game-written slot, for example the level-5
autosave of the [controlled save setup](lol3-native-saves.md#controlled-save-setup).
The loader waits on the progress sound at `0x46F68F–0x46F69B`; use a
null sound sink, or set `[0x65BD64]` to 0 there (a patched run).

Before launch, delete `cdcache2.smf` from the game folder of the
disposable copy if it is there. The cache initializer writes that file
(9 bytes, `The game `) at `0x4E4CC0–0x4E4CD7` and deletes it only at a
clean shutdown (`0x4E5316`, `DeleteFileA` through `0x531E10`), so a
session that was killed leaves it behind. When the next start finds it
(`0x4E4C2B–0x4E4C3A`), the initializer calls the two-string notice
`0x47AD50` (string ids `0x12` and `0x24`, five arguments, `ret 0x14`)
and then takes its rebuild branch: `CopyFileA` restores `cdcache.lst`
from `cdcache.ls_` (`0x4E4C97`) and replaces the game-folder
`cdcache.wsx` with the 114-byte `cdcache.hdr` (`0x4E4CA9`); the fill
loop then grows it from screen memory. Without the file, and with a
game-folder cache no more than 0xFA00 bytes short of `[0x545520]`
(clamped to `0x6400000`–`0x1F400000`), the initializer shows no
notice and skips the fill (`0x4E4DD9` jumps to `0x4E4EAF`).

### Run of 2026-11-20: DLOW1 autosave with two live edits

One instance of the English retail game under Wine, on a private
16-bit Xvfb display with no audio driver, loaded a copy of the
game-written DLOW1 autosave `f88f201e77d4` (written during the
[DLOW1 approach](lol3-spell-dispatch.md#dlow1-approach-with-the-native-placement-live);
its SHA-256 was unchanged after the run, and no save was written). The
save bytes were not edited. A `cdcache2.smf` was present at start, so
two **live edits** were made in the cache initializer:

- At `0x4E4C62` the call to the notice `0x47AD50` was skipped
  (`esp + 0x14`, resume at `0x4E4C67`). Its result is not used; the
  rebuild branch above ran (the lookups of `cdcache.ls_` and
  `cdcache.hdr` from `0x420DFB` were logged).
- At `0x4E4E34` execution jumped to `0x4E4EAF`, skipping the surface
  lock `0x5046E0` and the fill loop `0x4E4E61–0x4E4E95`. The local at
  `[esp+0x1C]` is then 0 instead of the 1 set at `0x4E4EA3`.

Both edits change only how the game-folder cache file is built. That
file ended at 35,327,926 bytes, starting with the 114 header bytes,
instead of being filled to about 100 MiB; this says nothing about a
native run. The level-file reads, seeks and name lookups below do not
pass through that code. Reads (`0x4357A0`) and seeks (`0x435A90`) were
logged from the entry of the MAP loader `0x43E6B0`, the first 400 reads
and 250 seeks only; the file-name lookup `0x435880` was logged for its
first 250 calls (from start-up into the first seconds in the level).
No file-open trace ran in this launch. An earlier launch in the same
folder, which stopped at the notice, traced `CreateFileA` from start-up
to the cache check of the same load. The play after loading was about
two seconds of walking, a short turn and one click; no picture of it
was kept. Results are listed under each probe.

The first three tests look for a reader of bytes the level loaders skip.
The loaders seek over these bytes, so first find out whether they
reach memory at all. Log every read the level load makes (file,
position and length; for a MAP through the handle at `0x4357A0`, seeks
through `0x435A90`). A read that covers the bytes gives its caller. If
a copy of the bytes is in memory, set read watchpoints on it and play;
a hit gives the reader. No read and no hit over a stated stretch of
play bounds that stretch only.

- **The 2,873 rows at MAP +0x244 (partly run 2026-11-20; open).** Settles
  [Q8](OPEN_QUESTIONS.md). Bytes: MAP +0x244 to +0x2F2C, the leading
  u32 `0xB39` and 2,873 four-byte rows (in `QWOD0.WSX` from
  +0x72E4CF). The loader `0x43E6B0` reads 0x244 header bytes and its
  next read follows a seek to header +0x28. A reader of the span at
  header +0xCC is the answer; follow one row to its first typed use.
  [Shared block](lol3-map-odf-readers.md#shared-block-before-the-vertices).
  *2026-11-20, running-game observation with the two live edits above:*
  in the DLOW1 load the loader read the 0x244 header bytes at member
  +0, and all 23 of its seeks on that handle (callers `0x43E889`–`0x43EF9F`,
  all logged) went to member +0x2F2C or later; the ninth (`0x43EABE`)
  went to +0x2F2C, the end of the span. Reads only move forward from a
  seek, so this load did not read the span through that handle. Not
  covered: other handles, reads after the 400th, and any later play. No
  memory search for the block was made, so no read watch could be set.
  Next: after a load, search memory for the 2,873 rows; if a copy
  exists, set read watches on it and play.
- **The 630 section-0 names in the ODF (not run; a 2026-11-20 launch did not test it).** Settles the names
  in [Q5](OPEN_QUESTIONS.md). Bytes: the 22-byte slots after the
  counted 24-byte rows of section 0 (CKEEP's first, `Floor39`, at entry
  +0x5DC). `0x4AB420` reads exactly 24 × count (`0x4AB42E`). A read of
  a 22-byte slot, or a search for `Floor39` in memory followed by a
  read watch, is the test.
  [ODF header](lol3-map-odf-readers.md#odf-header-and-primary-tables).
  In the 2026-11-20 launch `0x4AB420` ran once (from `0x43FCE7`, count
  0x19 for DLOW1), before read logging was armed at the MAP loader, so
  none of the ODF reads were logged. Next: arm read logging at the start
  of the level load (before `0x43FCD6`).
- **The two MAP label spans (partly run 2026-11-20; open).** Settles the labels in
  [Q4](OPEN_QUESTIONS.md). Bytes: the 26-byte names at
  `u32(+0xC8) + 8 * u32(+0xC4)` and the 31-byte labels at
  `u32(+0xDC) + 4 * u32(+0xD8)` (the first label at
  `BUPP1.WSX+0x181E90C`). A reader that reaches either start and
  steps by 26 or 31 bytes is the answer.
  [Tail after the vertices](lol3-map-odf-readers.md#tail-after-the-vertices).
  *2026-11-20, running-game observation with the two live edits above:*
  in the DLOW1 MAP (114 waypoints, one path label) the loader seeked
  to +0xC944 (`0x43EBE8`, the waypoint rows) and then to +0xD868
  (`0x43EC5C`), past the 26-byte names at +0xCCD4–+0xD868; its next
  seek went to +0x7A516. The 31-byte label at +0xD86C–+0xD88B lies
  between those two seeks; the read there (static: 4 × u32(+0xD8) bytes)
  came after the 400th read and was not logged. The seeks match the
  page's static seek list. Next: log every read of the MAP load without
  a cap.
- **The PHT stream (partly run 2026-11-20; open).** Not a numbered question; it settles
  what reads the four [PHT files](formats/pht.md). Log every file the
  game opens from start to a level load. An open of `CYGNUS.PHT`,
  `QUANN.PHT`, `RAIDER.PHT` or `YUPA.PHT` gives the caller; then read
  watches on the loaded bytes show how a byte of the 0x1010000-byte
  cycle is picked. No open means these files are not read in that play.
  *2026-11-20:* a `CreateFileA` trace from start-up to the cache check
  of a DLOW1 load (the save, `dlow1.wsx`, `dlow1S.wsx`, `SLICECD3.wsx`
  and `MUSIC3.wsx` were opened) showed none of the four names; that
  launch stopped at the notice above. In the launch that reached the
  level no open trace ran; the four names were not among the first 250
  name lookups and not in one listing of the open files. That bounds
  start-up to the cache check only. Next: trace `CreateFileA` and
  `CreateFileW` without a cap from start-up through a full level load
  and some play.
- **Music key `0x1D4F73DA` (partly run 2026-11-20; open).** Settles
  [Q10](OPEN_QUESTIONS.md). Watch: the lookup entry `0x435880`
  (log the name and the returned archive row) and the call at
  `0x44A7F5` (its argument is the string at `EBX`). Play: start the
  game and travel through levels so the music changes; also try the
  `-SCORE` option. Result: a stop that returns the `music4.wsx` row
  with this key (directory at `music4.wsx+0x8A`) names the track.
  No such stop leaves the key unnamed for that play.
  [Music streams](formats/audio.md#music-streams).
  *2026-11-20, one level, no travel, no `-SCORE`:* the first 30 calls at
  `0x44A7F5` all passed `MUSIC\ubtown1.aud` (stem 3, key `0x206A0547`),
  and the following lookups repeated that name. The key stays unnamed.
- **The shipped `cdcache.wsx` (partly run 2026-11-20; open).** Settles
  [Q1](OPEN_QUESTIONS.md). Use an install where `DAT/cdcache.wsx` and
  the game-folder `CDCACHE.wsx` are both present. Watch: every file
  open, with its path, and the game-folder probe at `0x4E4C00`. Result:
  an open of the `DAT` copy, with the reads that follow (position and
  length), shows what the game takes from it. To tell which screen the
  block holds, lock the same surface at the fill loop (`0x4E4E34`,
  loop `0x4E4E61–0x4E4E95`) and compare its first 64,000 bytes with
  the shipped block.
  [Cache reader](lol3-wsx-reader.md#cache-index-lifecycle).
  *2026-11-20:* the `CreateFileA` trace up to the cache check showed
  `CDCACHE.wsx` opened by its bare name, found in the game folder; no
  `DAT` path was tried for it (for `GLOBAL.wsx`, by contrast, the game
  folder and then `DAT` were tried). The shipped `DAT/cdcache.wsx` kept
  its SHA-256 and date, which shows it was not written, not that it was
  not opened. The game-folder cache was rebuilt by the branch the live
  edits passed through (see the run above), so its size says nothing
  about a native run. Next: in a copy without `cdcache2.smf`, trace
  opens (a) as installed and (b) with the game-folder `cdcache.wsx`
  removed, to see whether the lookup then falls back to the `DAT` copy.
- **The second player-side actor at `0x5860F0` (not run; a 2026-11-20 launch did not test it).** Settles
  that part of [Q11](OPEN_QUESTIONS.md). Setup: a slot in BUPP1, near
  the opcode-0x1A record at `BUPP1.WSX+0x18C7FD3`. Watch: the call at
  `0x448316` (`ecx = 0x5860F0`) and `0x48EBE0`. Play: let that script
  run. Result: match the object's +4/+8 position to the character on
  screen, and note which character does action +4. That character is
  the answer.
  [Opcode 0x1A](lol3-script-opcodes.md).
  The 2026-11-20 launch watched `0x448316` in DLOW1, not in BUPP1, and
  ran no script toward an opcode-0x1A record; the call was not fetched
  in about two seconds of play. A game-written BUPP1 slot
  (`5ae559b2cabe`) was among the copies.
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
  *2026-11-20, edited-save run with two live edits:* a second load of
  the same edited BUPP1 copy (`90099b161497`, no new bytes changed; the
  two cache-initializer edits of the
  [run above](#run-of-2026-11-20-dlow1-autosave-with-two-live-edits)
  were made again) repeated the
  [edited-save results](lol3-spell-dispatch.md#casts-with-edited-quick-slots)
  without using the items. Key 1, spell `0x59`: `0x4329C0` was entered
  with −1 from `0x4A5A20`, the first counter read 34 instead of 35 at
  the next cast and mana stayed 437. Key 2, spell `0x57`: the ordinary
  writer stored 415 at `0x410014` (437 − 22). Key 3, spell `0x54`: the
  cast was entered with mana 415 and counters 34/0, the screen showed
  "No enemy to attack" and no debit was logged before the session was
  stopped seconds later. No new state; native acquisition and the HUD
  indicator stay open.

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
