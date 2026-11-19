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

**UNCONFIRMED.** Live second-counter debit and HUD feedback. Save with
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

**UNCONFIRMED, pickup from the world.** Attempts to drop the held item
on the level-5 bridge left the same cursor reference or produced no
visible loose item. The new-game route to a tutorial item stopped at
the video-memory error. Start from an original slot within reach of
one visible loose item, with space in the player's inventory. Save a
no-action control and one pickup from the same source. At `0x4378C0`
and `0x437F79`, compare the old and new item by definition identity.
A removed world-pool row and a new reference to that identity would
isolate the pickup. Compare the decoded sections after accounting
for the base XOR and pointer relocations.
[Measured controls and remaining pickup procedure](lol3-native-saves.md#controlled-saves-with-a-null-sink)
