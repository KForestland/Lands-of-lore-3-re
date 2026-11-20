# Re-deriving a sample of confirmed statements

Two samples of 30 statements labelled confirmed were taken from the current
pages, each by its own rule, and checked again from the original bytes: the archives in `DAT/`
and beside the game, `LOL3.DAT` disassembled at code address = file offset
plus `0x400C00` (data at file offset plus `0x401800`), the game-written
cache and the game-written saves. No game, emulator or debugger was run,
so the running-game part of a statement is listed as not repeated. Each
list was fixed before any statement on it was checked.

"Held" means the bytes give the same values as the page. "Part held"
means the checked part held and a broader part of the same statement
was not re-checked. "Wrong" and "Overstated" statements were corrected
on the page.

## First sample (19–20 November 2026)

Pages in the order the rating counts them; every third page from the
third page on, the first paragraph on it that carries a confirmed label
and names an address or offset (in a table, the labelled cell). Those
pages gave 11 statements, so the list went on with pages 1, 4, 7, … (12
statements) and then pages 2, 5, 8, … until it had 30. The rule was
written into the picking script and the list was fixed at 23:27 UTC on
19 November, on the 80 pages before this page and the
[check audit](CHECK_AUDIT.md) were added; the checking scripts are from
23:29 on. The same rule on the current pages finds the same paragraphs
on 29 of the 30 pages and takes the [tutorial](tutorial-one-event.md) in
place of the colour bake. Four statements are also on the second
sample's list (level assembly, numbers, level notes and dispatch
search), so 26 are new to it. 30 statements: **24 held and 6 part
held.** The first check had 21 held, 8 part held and the numbers
statement wrong; the review below re-walked two of the part-held
statements in full and found the numbers statement right.

| Page | Statement | Result |
| --- | --- | --- |
| [Running game](NEEDS_A_RUNNING_GAME.md) | Spell bypass calls | Held |
| [Progression](PROGRESSION.md) | Portal arm and level table | Held (the portal census, the `0x11` store and the call chain were re-walked in the review below) |
| [Round trip](ROUND_TRIP.md) | LMF and `.TE_` writing | Held (the writer and the zero-length end were re-walked in the review below) |
| [Tour](TOUR.md) | QWOD0 map counts | Part held: the entry, 1,308 vertices, 1,430 surfaces and the archive's members; the drawing was not re-rendered |
| [Music and sound](formats/audio.md) | MUSIC wave layout | Held (38 entries) |
| [PHT](formats/pht.md) | Repeating stream | Held |
| [WSX](formats/wsx.md) | Name hash | Part held: the formula at `0x509EC3`; the 76 name witnesses were not re-counted |
| [Dispatch search](lol3-dispatch-search.md) | Level-load and filename calls | Part held: the code and the strings; the CSV row walk and the directory-hash census were not re-walked |
| [MAP and ODF readers](lol3-map-odf-readers.md) | Shared header block | Held |
| [Event lists](lol3-script-events.md) | Region-event pool | Held |
| [Colour bake](lol3-texture-bake.md) | Bake callers and entry | Held |
| [Cookbook](COOKBOOK.md) | First waypoint X | Held |
| [Level assembly](HOW_A_LEVEL_IS_PUT_TOGETHER.md) | Sound archive and reader order | Held |
| [Numbers](NUMBERS.md) | Creature health and derived bytes | Held (the first check marked it wrong; see the review below) |
| [Quick reference](QUICK_REFERENCE.md) | PHT row | Held |
| [LMF](formats/lmf.md) | Light-map name and label | Held |
| [Textures](formats/textures.md) | Row-span records | Part held: the span layout on all 854 records; the palette-source offsets were not re-walked |
| [Level notes](levels/notes/README.md) | Object and region stream positions | Part held: the code sites; the 16,876 and 2,201 reference counts were not re-walked |
| [Hit resolution](lol3-combat-dispatch.md) | Opcode 19 hit request | Held |
| [Items](lol3-item-dispatch.md) | Item-slot input names | Held |
| [Native saves](lol3-native-saves.md) | Save name constructor | Held |
| [Script opcodes](lol3-script-opcodes.md) | Command length function | Held |
| [Palette sources](lol3-texture-palette-sources.md) | Texture resolution setting | Part held: the setting and the mip window; the 131 of 178 count was not re-walked |
| [MAP and ODF](formats/map-odf.md) | Header fields 0, 1, 2, 20 and 21 | Held |
| [VQA](formats/vqa.md) | Movie stem table | Held (all 19 keys) |
| [Dialogue tables](lol3-dialogue-dispatch.md) | `.trr` table loads | Held |
| [Light-map reader](lol3-lmf-reader.md) | LMF open and header check | Held |
| [Object dispatch](lol3-object-dispatch.md) | Command stream and group offsets | Held |
| [Spell inputs](lol3-spell-dispatch.md) | Cast-spell input names | Held |
| [WSX reader](lol3-wsx-reader.md) | Archive header reader | Held |

A review re-derived six of these from the bytes again with its own
readers (picked at random, seed 86, from the 26 not on the second list):
the spell bypass calls, the first waypoint X, the command length
function, the command stream and group offsets, the cast-spell input
names and the archive header reader. All six gave the result above; the
39 opcodes with a positive length equal the size column of the opcode
table. The review also re-walked two part-held statements. Progression:
both command streams of the 18 MAPs hold 131 portal commands, all with
selector 1 and index 0 and none selecting row 1 or row 17, the same
count as `lol3_progression.py`; the immediate `0x11` is stored at
`0x4075C1–0x4075C9`; and `0x46CC2B` → `0x46CCB0` → `0x436890` →
`0x43D7B0` reaches the store at context +0x76B (`0x43D7CB`). Round
trip: the writer keeps +0 and the header, writes each length before its
block and ends with a zero length, and the native reader
(`0x4E477D–0x4E48C1`) loops until it reads a zero length. Both now hold
in full. The first check had read the store at `0x4F0E76` as byte
+0x4B of the 139-byte row and marked the numbers statement wrong. The
loop's pointer is the row plus 0x37 (`0x4F0D74`), so the bytes are
+0x81 and +0x82 as the page says; the helper at `0x4F1220` reads +0x81
of the same row. No page changed.

## Second sample (19–20 November 2026)

Every third page from the second page on, the last statement on it that
names an address or offset; a table gives its last row. Too few current
pages qualify, so the list goes on with one page marked as history and
four single sentences, each the last one naming an address in a
paragraph that a first-sample rule would pick. The list was fixed at
23:01 UTC on 19 November; the first byte for it was read at 23:10. Four
statements are also on the first sample's list (see above). 30 statements: **17 held, 10 part held,
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
