# LoL3 questions to test in the original Windows game

Use a disposable copy of your own English retail installation
(`LOL3.DAT` is 1,643,520 bytes). `LOL3.EXE` is a launcher that starts
`LOL3.DAT` as a child process, so enable child-process debugging
(WinDbg `.childdbg 1`) or attach x32dbg to the `LOL3.DAT` process
after launch. Record the renderer, display mode and whether a
compatibility wrapper is in use. `LOL3.DAT` has no relocations and
always loads at `0x400000`, so the addresses here are used as they
are; if the module base differs, you are in the wrong process.

## Remaining probes

### Q6. Which bytes does the texture renderer consume?

The [SMD test](lol3-texture-bake.md#slice-directory-and-run-decoder) and
[projection test](lol3-texture-bake.md#projection-and-depth-within-one-slice)
give shipped frame offsets for all four slice flags and, from six captured
coefficients, the predicted indexed output rows. The
[row-flag test](lol3-texture-bake.md#two-ambiguous-row-flags) gives the
first-pixel predictions for the two unresolved row flags. Use those tests to
identify the source buffer and output words before testing display conversion.

### Q9. What colours does the VQA frame callback present?

Question: [Q9 in OPEN_QUESTIONS](OPEN_QUESTIONS.md).

**CONFIRMED.** The first raw VPTR in `mintro01.vqa`
(`MOVIES1.WSX+0x42`, pointer words at `+0x1768E`) fills
its first block row with tile 0. The output dispatch at
`0x512AAF` calls the tile routine, which writes packed
pixel words. [Movie and callback evidence](formats/vqa.md#44-block-pointers)

**CONFIRMED, offscreen format.** The native allocation and lock for
this introduction run returned RGB565 (`F800/07E0/001F`): the request
asks for no pixel format (flags 7), so the surface takes the display
mode's format, here a 16-bit Wine display; a native 555 desktop would
give 555. Depth 16
and pitch 1,280. The decoder opener reached FINF but the audio
initialization call at `0x50E404` returned −13, leaving a null
decoder at `0x470048`. Both archive and exact loose-entry trials
stopped before the output callback. To get past it with audio still
disabled, see the [debugger route](formats/vqa.md#live-introduction-opener).
[Offscreen surface and live opener evidence](formats/vqa.md#live-introduction-opener)

**UNCONFIRMED.** The actual tile word and its final conversion.
Frame 16 supplies a nonzero input at pixel (3, 0), tile 1, word
`0x0421` (`MOVIES1.WSX+0x1E60E`, bank `+0x2754`). Let the
intro play and stop at `0x512AAF`. Record the invoked function,
destination and pitch, then compare that pixel after `0x470109`
and `0x47011B`. Follow any change in the word or masks to the
copy which performed it.

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

**UNCONFIRMED.** Live charges, HUD feedback and debits. Save with
fixed equipment, sufficient mana and spell 0x54 or 0x59 selected.
Watch `0x570AB9` while using a first-counter item, then cast. For
the second counter use Mana Cluster and a spell whose admission
reaches `0x4A46E2`. Compare the same cast before and after each
consumable. Record the producer, the new selector value, the
next accounting routine and the visible HUD change. A hit at `0x4329C0` or `0x432AD0` with
a −1 argument identifies the alternate counter to follow.
A negative debit at `0x40FFE0` and changed player +0x1B8
are the ordinary mana control. Keep any run where admission
fails separate from a successful alternate payment.

### Q13. Which original save bytes follow one controlled action?

Question: [Q13 in OPEN_QUESTIONS](OPEN_QUESTIONS.md).

**CONFIRMED.** The header writes the active level at +0x498
and position-associated fields at +0x49C–+0x4B7
(`0x43766F–0x43776D`, `0x4377EB–0x4377F8`).
The global writer uses the table at `0x438848`; the level
writer uses `0x438940`. [Slot layout and chunk reader](lol3-native-saves.md)

**CONFIRMED, setup result.** The native loader reached the progress
sound wait with its flag still 1 (set unconditionally at `0x46F55B`;
clearing `[0x65BD64]` in the debugger is the route past it). `-NOSFX` and `-NOMUSIC` left
the `0x46F59F` return at −1 under the audio-disabled Wine setup.
F10, turn right and forward produced no new writer hit and the
source slot retained its hash.
[Original header and live setup](lol3-native-saves.md#controlled-save-setup)

**CONFIRMED, position group layout.** Both 14-byte groups hold two
16.16 horizontal coordinates, a zero-extended 16-bit heading and
a u16 region index. Readers `0x40AD80` and `0x48B690` apply the
position and heading to their respective objects.
[Header layout and readback](lol3-native-saves.md#slot-header-and-stream)

**UNCONFIRMED.** Which fields and payload rows change independently
after one input. Start from one local slot and make three fresh saves at a stable point,
reloading that starting slot for each trial. In the first save
make no movement. In the second press only turn right. In the
third take one forward step while staying on the same surface.
At `0x43766F`, record the live player and second position-object fields,
then compare both groups of three saved dwords to those inputs.
Turning alone isolates an orientation input; moving alone
isolates horizontal coordinates. If an alleged orientation
moves with a step and stays fixed while turning, the trial
rejects that label. Record the surface index in each save as
a control.

Repeat with one pickup and no movement. At
`0x4378C0–0x437928` and `0x437F0E–0x437F55` log the
affected selector and source record before compression. Compare
the decoded sections with the no-action save, adding back a
base image by XOR where that selector requests it. A changed
item-instance row and reference to the same identity tie the
fields to the pickup. A change present also in the no-action
trial is background state and needs its own observation.

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

**UNCONFIRMED.** Final composited colour, conversion of the individual
words and other devices. To compare another device, load a textured
level and break at the device format enumeration call
`0x4950F7`. In the callback at `0x495040`, record descriptor
dwords +0x58/+0x5C/+0x60 and the alpha mask at +0x64.
After the call capture the selected copy and follow that
descriptor into the first texture upload. RGB555 selects the 5-bit
extraction with the first triple above. RGB444 selects 4-bit
extraction with the second. A different upload descriptor or
pixel word identifies a conversion between selection and display.
If the path enumerates several candidates, keep the upload
descriptor separate from those candidates.
