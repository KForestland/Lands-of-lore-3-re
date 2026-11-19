# Re-deriving a sample of confirmed statements

A sample of 30 statements labelled confirmed was taken from the current
pages and checked again from the original bytes: the archives in `DAT/`
and beside the game, `LOL3.DAT` disassembled at code address = file offset
plus `0x400C00` (data at file offset plus `0x401800`), the game-written
cache and the game-written saves. No game, emulator or debugger was run,
so the running-game part of a statement is listed as not repeated. The
list was fixed before any statement on it was checked.

"Held" means the bytes give the same values as the page. "Part held"
means the checked part held and a broader part of the same statement
was not re-checked. "Wrong" and "Overstated" statements were corrected
on the page.

## Second sample (19–20 November 2026)

Every third page from the second page on, the last statement on it that
names an address or offset; a table gives its last row. Too few current
pages qualify, so the list goes on with one page marked as history and
four single sentences, each the last one naming an address in a
paragraph that a first-sample rule would pick. The list was fixed at
23:01 UTC on 19 November; the first byte for it was read at 23:10. A
first sample, taken by a different rule, is not recorded here yet, so
overlap with it is not checked. 30 statements: **17 held, 10 part held,
2 wrong and 1 overstated (all three corrected).**

| Page | Statement | Result |
| --- | --- | --- |
| [LMF](formats/lmf.md) | `CKEEP` framing and member sizes | Held (5,256 groups, 424,288 members, all 18 entries) |
| [Textures](formats/textures.md) | Palette selector and builder | Part held: the selector byte and the call; not the 854 cache spans or the editor paths |
| [Hit resolution](lol3-combat-dispatch.md) | Mitigation record census | Wrong, corrected: the 334 complete 147-byte rows are all distinct; 57 is the count of distinct 20-byte mitigation prefixes |
| [Items](lol3-item-dispatch.md) | Index 123 handler | Wrong, corrected: `0x4A6590–0x4A659C` is five instructions with the return (load, clear, compare, set, return), not four |
| [Native saves](lol3-native-saves.md) | Edited-save growth | Part held: the three files exist with the stated lengths and digests, and each header stores its own length and versions 38 and 310; the loader run and the restored references not repeated |
| [Script opcodes](lol3-script-opcodes.md) | Opcode 0x1A | Part held: the setup calls and the mode dispatch; not the full damage, save and screen trace |
| [Palette sources](lol3-texture-palette-sources.md) | Shared palette banks | Part held: both resolver arms and their keys; not the join over all 20 banks |
| [MAP and ODF](formats/map-odf.md) | QWOD0 schematic inputs | Held |
| [VQA](formats/vqa.md) | DirectDraw frame handoff | Part held: the tile copy and the display call; the pixel count is from a running capture |
| [Dialogue tables](lol3-dialogue-dispatch.md) | 53 stored tables | Held |
| [Light-map reader](lol3-lmf-reader.md) | Light-map corner words | Held |
| [Object dispatch](lol3-object-dispatch.md) | `CKEEP` group index 0 | Held |
| [Spell inputs](lol3-spell-dispatch.md) | DLOW1 reachability trial | Part held: the item row (X −635, Z 4913, height 110, surface 1287, key `0xE2F77FE7` at +0x20) and tile 1287 at field 2 + 1287 × 56 with height 110; the restored mana and counters not repeated |
| [WSX reader](lol3-wsx-reader.md) | Unnamed directory keys | Overstated, corrected: the counts held (2,374, 222 and 3,701,411 strings, 53 path-like names, 7,364 other keys), but one of those keys does have a printable string (the collision at `LOCAL.WSX+0x147CF1F`); the page now says what the search covers. The [open questions](OPEN_QUESTIONS.md) and [status](STATUS.md) wording was bounded the same way |
| [Tutorial](tutorial-one-event.md) | Queued floor movement | Part held: the queue test and the height arm; no movement watched |
| [Running game](NEEDS_A_RUNNING_GAME.md) | Controlled floor pickup | Part held: the transfer call; the pickup itself not repeated |
| [Progression](PROGRESSION.md) | First accepted event | Part held: the dispatch and return sites; not the generated census |
| [Round trip](ROUND_TRIP.md) | TRR layout and edited boundaries | Held |
| [Tour](TOUR.md) | QWOD0 creature inputs | Held |
| [Music and sound](formats/audio.md) | Level IMA sample layouts | Held |
| [PHT](formats/pht.md) | Name and file-search scan | Held |
| [WSX](formats/wsx.md) | Installed cache directory | Held; wording clarified: the row at +0x12 is in the cache's own first directory, the 114-byte header it shares with the shipped `DAT/cdcache.wsx` |
| [MAP and ODF readers](lol3-map-odf-readers.md) | `CKEEP` label span listing | Held |
| [Event lists](lol3-script-events.md) | Frame loop threshold and cap | Held |
| [Colour bake](lol3-texture-bake.md) | Texture remap arm | Part held: the branch and flag write; its use on a live texture is open on the page |
| [Semantic phase](lol3-semantic-phase.md) (history) | Byte pair `C5 A5` | Held |
| [Level assembly](HOW_A_LEVEL_IS_PUT_TOGETHER.md) | Object dialogue call sites | Held |
| [Numbers](NUMBERS.md) | Attack-derived definition byte | Held (the fixed sentence is a test; the last confirmed sentence before it was checked) |
| [Level notes](levels/notes/README.md) | Untraced per-class slots | Held |
| [Dispatch search](lol3-dispatch-search.md) | Damage delta call | Held |

A review re-derived five of these from the bytes again (picked at random,
seed 147): the edited-save growth, the DLOW1 trial, the IMA sample
layouts, the PHT scan and the damage delta call. The IMA layouts, the
damage delta call and the DLOW1 trial gave the result above. The review
found the edited copy and the later autosave of the save statement,
which the first pass had not, and checked their lengths, digests and
header fields. The PHT scan held in full on the review (the first pass
re-used the existing check for part of it, so it was listed as part
held): no decoding of the code section ends in `0x1010000` as an
immediate, the wrapper's five callers and their pushed strings, and none
of the eight name keys in any of the 53 directories or the two programs.
The review also re-derived the four corrections: 57 distinct prefixes in
334 distinct rows, the five instructions at `0x4A6590`, 7,364 keys left
after 53 path-like joins with one printable collision among them, and
the cache's own row at +0x12.
