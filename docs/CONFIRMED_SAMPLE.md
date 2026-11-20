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
place of the colour bake. Four statements were also on the second
sample's initial list (level assembly, numbers, level notes and dispatch
search); the second sample replaced them, so the two samples count 60
different statements. 30 statements: **24 held and 6 part
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
statements on this list were also on the list frozen for the first
sample (level assembly, numbers, level notes and dispatch search). They
are counted in the first sample only, and their results here are kept
below the table. No further page qualifies, so four more single
statements replace them (rows 27–30): going on through the list from the
history page, the confirmed paragraph naming an address just before the
listed one on the running-game, round-trip, tour and music and sound
pages (on the progression page that paragraph is on the first sample's
list). That list was fixed at 23:42 UTC; the earliest record of a check
on it is from 23:58. Line numbers are those of the pages when the first
list was fixed (commit `5cba3b1`). 30 counted statements: **15 held,
12 part held, 2 wrong and 1 overstated (all three corrected).**

| # | Page (line at `5cba3b1`) | Statement | Result | Evidence and limits |
| ---: | --- | --- | --- | --- |
| 1 | [LMF](formats/lmf.md), line 40 | `CKEEP` framing and member sizes | Held (5,256 groups, 424,288 members, all 18 entries) | CKEEP.WSX+0xC19084 supplies the five fields and its first row at +0xC19184 selects 657 bytes, expanding to 35,584 for 256 members. Walking group starts and decoding all 18 archives confirms 5,256 groups, 424,288 members and the size formula. |
| 2 | [Textures](formats/textures.md), line 82 | Palette selector and builder | Part held: the selector byte and the call; not the 854 cache spans or the editor paths | 0x44B6E7 reads selector byte +0x0D, and 0x4826D6 calls that selector. Each arm reads the indicated resource object and adds its base to descriptor u16 +2. The 854 cached spans and every editor path were outside this independent check. |
| 3 | [Hit resolution](lol3-combat-dispatch.md), line 271 | Mitigation record census | Wrong, corrected: the 334 complete 147-byte rows are all distinct; 57 is the count of distinct 20-byte mitigation prefixes | Following ODF header +0x10/+0x48 in 18 levels gives 334 complete 147-byte rows, all distinct. Exactly 57 of their first 20-byte mitigation prefixes are distinct. The page now states which length was counted at BUPP1.WSX+0x1B5E178 and its peers. |
| 4 | [Items](lol3-item-dispatch.md), line 395 | Index 123 handler | Wrong, corrected: `0x4A6590–0x4A659C` is five instructions with the return (load, clear, compare, set, return), not four | 0x4A6590–0x4A659C contains MOV, XOR, CMP, SETE and RET: five instructions. It returns one only for operation 0x11. The table's count is corrected. |
| 5 | [Native saves](lol3-native-saves.md), line 442 | Edited-save growth | Part held: the three files exist with the stated lengths and digests, and each header stores its own length and versions 38 and 310; the loader run and the restored references not repeated | The available original 1,807,734-byte slot matches digest prefix 5ae559b2cabe. The first pass did not find the two other files; the review located them and confirmed their sizes, digest prefixes and header fields. The loader run was not repeated. |
| 6 | [Script opcodes](lol3-script-opcodes.md), line 355 | Opcode 0x1A | Part held: the setup calls and the mode dispatch; not the full damage, save and screen trace | 0x4482DB checks 0x600854, 0x4482F8 calls 0x41EDE0 and 0x448311 loads 0x5860F0 before the 0x448316 call to 0x48EBE0. That setup and the mode dispatch were checked, without repeating the full damage, save and presentation trace. |
| 7 | [Palette sources](lol3-texture-palette-sources.md), line 70 | Shared palette banks | Part held: both resolver arms and their keys; not the join over all 20 banks | The resolver arms at 0x44B714 and 0x44B731 both load 0x570218. They add descriptor +2 to 0x570248 or 0x570240. The loader's complete 20-bank archive join was outside these code windows. |
| 8 | [MAP and ODF](formats/map-odf.md), line 62 | QWOD0 schematic inputs | Held | MAP +0x04/+0x0C at QWOD0.WSX+0x72E28B select +0x7311B7 and +0x7384B9. Counts at +0x50/+0x58 are 1,308 and 1,430. The existing SVG check also passes byte for byte. |
| 9 | [VQA](formats/vqa.md), line 250 | DirectDraw frame handoff | Part held: the tile copy and the display call; the pixel count is from a running capture | The PE has the tile copy call at 0x476275 to 0x476440 and the indirect display path at 0x47011B. The pixel agreement count comes from a running capture and was outside this audit. |
| 10 | [Dialogue tables](lol3-dialogue-dispatch.md), line 118 | 53 stored tables | Held | An independent directory walk finds 26 members and 13,065 records per locallng.wsx. Both archives match bytes. Loose PROMPT.TRR matches member 0x623224A4 at +0x5986BB5, giving total 53 copies and 26,170 rows. The writer check also passes. |
| 11 | [Light-map reader](lol3-lmf-reader.md), line 107 | Light-map corner words | Held | Independent expanded-grid comparison at member +0x0C and +0x2C finds 214,743 zero quartets, all 610,325 nonzero words in their own grids, and none with bit 15 set. It reproduces 340,718 matching the assigned corner's square and 107,136 matching the opposite square. |
| 12 | [Object dispatch](lol3-object-dispatch.md), line 50 | `CKEEP` group index 0 | Held | CKEEP.WSX+0xD07270 reads zero. At +0xD036F4 the group is 0xF0 with one child, and +0xD036FA decodes opcode 9, selector 3, index 53 and property 21. 0x447E84 calls 0x447680. |
| 13 | [Spell inputs](lol3-spell-dispatch.md), line 359 | DLOW1 reachability trial | Part held: the item row (X −635, Z 4913, height 110, surface 1287, key `0xE2F77FE7` at +0x20) and tile 1287 at field 2 + 1287 × 56 with height 110; the restored mana and counters not repeated | DLOW1.WSX+0x155A349 contains X -635, Z 4913, stored height 110, surface 1287 and the defined identity at +0x20. The corresponding surface +0x18 is 110. The restored mana and behavior on load remain prior runtime observations. |
| 14 | [WSX reader](lol3-wsx-reader.md), line 175 | Unnamed directory keys | Overstated, corrected: the counts held (2,374, 222 and 3,701,411 strings, 53 path-like names, 7,364 other keys), but one of those keys does have a printable string (the collision at `LOCAL.WSX+0x147CF1F`); the page now says what the search covers. The [open questions](OPEN_QUESTIONS.md) and [status](STATUS.md) wording was bounded the same way | The established check still joins 53 path-like names. The claim about the other keys is now explicitly about the printable NUL-terminated search across the named files. A negative in that scope cannot say whether a key has a name elsewhere or in another representation. |
| 15 | [Tutorial](tutorial-one-event.md), line 46 | Queued floor movement | Part held: the queue test and the height arm; no movement watched | The queue's test follows its call at 0x4F08DD–0x4F08F1. The height arm subtracts or adds the step and clamps remaining displacement at 0x4E61A8–0x4E61D2. No rendered movement was exercised. |
| 16 | [Running game](NEEDS_A_RUNNING_GAME.md), line 257 | Controlled floor pickup | Part held: the transfer call; the pickup itself not repeated | The static call at 0x49EDA0 passes the source record to 0x49E560. The physical pickup and before/after row numbers are prior observations and were not repeated. |
| 17 | [Progression](PROGRESSION.md), line 7 | First accepted event | Part held: the dispatch and return sites; not the generated census | The region path calls 0x4E5880 at 0x4AC45D, and the object path calls it at 0x4A8344 then exits at 0x4A8351. The dispatch and return sites for the sampled walkers were read, without repeating the generated Earlier-column census. |
| 18 | [Round trip](ROUND_TRIP.md), line 36 | TRR layout and edited boundaries | Held | The original count, IDs and boundaries independently resolve the same 53 entries. Running the writer and its synthetic length mutation rechecks later boundaries and ID order. The stored first boundary describes file +8+8N after adding four. |
| 19 | [Tour](TOUR.md), line 36 | QWOD0 creature inputs | Held | QWOD0.WSX+0x7515BD stores 11063, -2943, and slot 0 at +0x20. Its ODF row at +0x778124 contains 25 at +0x63 and 5 at +0x81. The PE copies the ceiling and halves the attack input at 0x4B479E and 0x4F1220. |
| 20 | [Music and sound](formats/audio.md), line 107 | Level IMA sample layouts | Held | Parsing each original RIFF fmt chunk independently gives 6,596 mono and 100 stereo and the documented rates and block sizes. Both block counts yield 1,017 frames. |
| 21 | [PHT](formats/pht.md), line 32 | Name and file-search scan | Held | The two original images have no listed names in ASCII or UTF-16, and scanning relative E8 targets to 0x51A410 finds the five calls. The existing PHT check reproduces the immediate and string pushes. This establishes the encoded search scope. Independent review also decoded the immediate scan and the searched call-site arguments. |
| 22 | [WSX](formats/wsx.md), line 113 | Installed cache directory | Held; wording clarified: the row at +0x12 is in the cache's own first directory, the 114-byte header it shares with the shipped `DAT/cdcache.wsx` | The cached extent at file +0x76 begins +0x436 and the free row at +0x136 ends at +0x6400000. The ordinary WSX-format row at +0x12 is in that cache itself, with relative offset 0x2794C41. The format page now names this scope explicitly. |
| 23 | [MAP and ODF readers](lol3-map-odf-readers.md), line 462 | `CKEEP` label span listing | Held | The MAP starts at +0xCBB182. From header +0xC4/+0xC8, 15 eight-byte points are followed by labels at absolute +0xCC59A6, matching --list. Other copied spans are identified by their offsets and hashes. |
| 24 | [Event lists](lol3-script-events.md), line 150 | Frame loop threshold and cap | Held | At 0x409930–0x409943 the difference from 0x5385E0 produces 24 when zero and 16 otherwise. 0x46D8A6 compares with 480 and the next arm caps it. This is static timing arithmetic. |
| 25 | [Colour bake](lol3-texture-bake.md), line 424 | Texture remap arm | Part held: the branch and flag write; its use on a live texture is open on the page | 0x421331 masks 0x211 and the compares select 0x42136E on 0x200. 0x4213C6 ORs bit 0x100 and 0x4213CA stores the flags. The branch itself is verified. No claim is made about its live binding to a texture. |
| 26 | [Semantic phase](lol3-semantic-phase.md) (history), line 97 | Byte pair `C5 A5` | Held | The check matches 195 texture hits, the two MAP offsets +0x730744/+0x730748, one light-map hit at +0x694783, none in ODF, and one PE hit at file +0xBC607. The same texture residues modulo 8 are reproduced. No original reader is inferred. |
| 27 | [Running game](NEEDS_A_RUNNING_GAME.md), line 246 | Turn, step and quick-slot transfer | Part held: the writer's two actor tests; the input sequence not repeated | The code under 0x43766F tests the two actor addresses at 0x4376A5 and 0x437723. The original branches were checked. The turn, step and quick-slot input sequence was not repeated. |
| 28 | [Round trip](ROUND_TRIP.md), line 28 | Native save rebuilding | Held | The original slot with digest prefix 5ae559b2cabe has a file length of 1,807,734 at +0x2C and starts global section 0 at +0x1A247. The writer comparison from the original slots and its player-X mutation was re-run and their directory fields compared. |
| 29 | [Tour](TOUR.md), line 28 | QWOD0 portal commands | Held | QWOD0.WSX+0x74BE4B and +0x74BE7B both contain the same six-byte command. At 0x410F98–0x410FC3 the native arm computes destination (0x20 AND 31)+2 and arrival 0x20 shifted right five. The original command therefore requests level 2, BUPP1, and arrival 1 on the ordinary path. |
| 30 | [Music and sound](formats/audio.md), line 91 | Unmatched WAVE chunks and tags | Part held: the chunk walk and the absent tags; not every side-file name search | The member with key 0x1D4F73DA starts at MUSIC4.WSX+0x11FD49A. A fresh RIFF walk yields only fmt, fact and data bodies at +0x14/+0x3A/+0x46. No leading ID3 or trailing TAG marker is present. Not every side-file name search was repeated. |

The four statements also on the first list, checked with this one:

| Page (line at `5cba3b1`) | Statement | Result |
| --- | --- | --- |
| [Level assembly](HOW_A_LEVEL_IS_PUT_TOGETHER.md), line 19 | Object dialogue call sites | Held |
| [Numbers](NUMBERS.md), line 406 | Attack-derived definition byte | Held (the fixed sentence is a test; the last confirmed sentence before it was checked) |
| [Level notes](levels/notes/README.md), line 33 | Untraced per-class slots | Held |
| [Dispatch search](lol3-dispatch-search.md), line 14 | Damage delta call | Held |

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
the cache's own row at +0x12. A later review re-derived two of the four
replacements with its own readers: the portal commands
(`02 01 00 00 1B 20` at `QWOD0.WSX+0x74BE4B` and `+0x74BE7B`; table entries 27 and 76 at
`0x4117D4` both reach `0x410F98`, which stores `(0x20 & 31) + 2` = 2 and
`0x20 >> 5` = 1; row 2 of the level table at `0x548938` names
`levels\bupp1`) and the unmatched WAVE (`RIFF` at
`music4.wsx+0x11FD49A` with only `fmt `, `fact` and `data` bodies at
+0x14, +0x3A and +0x46, the `data` chunk ending the RIFF). Both gave the
result above.
