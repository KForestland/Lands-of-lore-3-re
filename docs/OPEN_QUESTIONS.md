# Open questions

Numbered so pages and the [STATUS table](STATUS.md) can point to them. Each says what is known and what would settle it.

For debugger procedures that use the original game, see [Needs a running game](NEEDS_A_RUNNING_GAME.md).

## At a glance

One line per question: its state and what would settle what is left. Device colour output (Q6, Q9), save pairs (Q13) and some trigger conditions (Q12) need a running original game; the other next steps need only the original files.

| # | State | What would settle the rest |
|---|---|---|
| Q1 | Partly | Explain the origin of the shipped compact `DAT/cdcache.wsx` and byte +0x17 of the allocator rows |
| Q2 | Answered | Names of the remaining entries: find their name strings in the program |
| Q3 | Partly | Renderer helper `0x44EB40` and samples at +0x2C confirmed; trace disk bit 0, header +0x0C–+0x2B and the +8 channel roles from `0x47451E` and `0x4C00DD` |
| Q4 | Partly | Waypoints, paths and surfaces are confirmed; trace waypoint byte +6, the 26-byte names, the 31-byte path slots, the extra bytes before field 16 and the section-1 fields |
| Q5 | Partly | Type tags select four AI resources (60 of 68 tags join all four); trace the section-0 companions and the failed-resource branch `0x420300 → 0x4FD780` |
| Q6 | Answered for supported cache records | PNG colour derived for 10,669 records of the game-written cache; 4,429 more reference SMD frames in the shipped SLICECD1–4. Frame and run decoding covers all 4,429 SMD references (optional `--decode-slices`). Compare the mapped SMD projection and the 20 copy cases with the live renderer, then identify the display format |
| Q7 | Mostly | The editor-name branch (`0x43FFE4–0x44000D`) converges on the retail reader; only a differently framed standalone file remains unwitnessed |
| Q8 | Partly | MAP/ODF entries joined; recover the window start and stride of one claimed edge and its native consumer |
| Q9 | Partly | VQA tables, LCW and the 4×4 pointer callback are confirmed; follow the display pixel-format masks to RGB output |
| Q10 | Mostly | Stem initializer traced, 37 of 38 entries join; find an original name witness for key `0x1D4F73DA` |
| Q11 | Partly | Trace the UNCONFIRMED opcode effects one by one |
| Q12 | Partly | Six regular indexes (138 definitions) traced; trace the other 108 indexes, the two alternate cast resources, discount selectors and mitigation mask names |
| Q13 | Partly | Compare original save pairs written before and after one known action |

## Questions

| # | Question | Where |
|---|---|---|
| Q1 | `cdcache.wsx`: two different files carry this name. Only the one in `DAT/` (3,264,114 bytes) ships; the one in the game folder (104,896,114 bytes) is written by the game when it runs. They both have a 9-entry header covering 52,663,793 bytes. The game-folder copy holds the 854 texture records, 420 of them after the area the header covers ([formats/textures.md](formats/textures.md)). Native expansion and the secondary allocator directory are confirmed, including eight occupied spans. Open: the origin of the shipped compact `DAT/` copy and row byte +0x17 | [Native WSX reader](lol3-wsx-reader.md) |
| Q2 | **Answered.** Native rotate-right name hash, case normalization and 76 exact name/key joins. Names of other entries remain unconfirmed | [Native WSX reader](lol3-wsx-reader.md#resource-name-key) |
| Q3 | LMF light maps: native directory, grouped LZO1X and decoded member sizes confirmed. Native consumer reads +8 and begins samples at +0x2C. Remaining disk flag and header meanings are open | [Native LMF reader](lol3-lmf-reader.md) |
| Q4 | MAP field 0 confirmed as counted 16.16 X/Z coordinates. Its tail holds the waypoints, paths and surfaces, all read natively ([readers](lol3-map-odf-readers.md)). Open: waypoint byte +6, the 26-byte names, the 31-byte path slots, the extra bytes before field 16 and the section-1 fields | [Native MAP reader](lol3-map-odf-readers.md) |
| Q5 | ODF readers, table strides and the fields of the type-tagged field-3 definitions mapped (most tags read as creatures or actors, e.g. RHOUND, ORC, SPIDER; a few are object ids, so the creature reading is UNCONFIRMED). Four AI resource paths resolve from the tags. Other per-row meanings remain open | [Native ODF reader](lol3-map-odf-readers.md) |
| Q6 | **Answered for supported cache records.** In the game-written cache, 10,669 records decode to PNG. Another 4,429 resolve to SMD frames in the shipped SLICECD1–4. All 1,979,019 slice runs frame exactly, and the native row projection and depth test are mapped ([projection](lol3-texture-bake.md#projection-and-depth-within-one-slice)). SMD rasterization and the last 20 copy paths still need the witness comparisons. Device presentation remains open | [Palette source inventory](lol3-texture-palette-sources.md), [Texture checks and witnesses](lol3-texture-bake.md#slice-directory-and-run-decoder), [running-game test](NEEDS_A_RUNNING_GAME.md#q6-which-packed-format-does-the-live-device-select) |
| Q7 | **Mostly answered:** all 18 original `.TE_` banks expand through LZO1X. The former `+1` witness is inside a compressed block. The editor-name branch `0x43FFE4–0x44000D` converges on the same reader; only a differently framed standalone file remains unwitnessed | [Texture formats](formats/textures.md) |
| Q8 | What the QWOD0 and SWOD4 byte-pattern labels mean in the game. MAP and ODF entries mapped. The old labels require recoverable file positions and a native consumer | [lol3-semantic-phase.md](lol3-semantic-phase.md) |
| Q9 | Movies. **Partly answered:** the 19 `MOVIES1..4` entries are named VQA files read by `0x50DF70`; frame index and sound chunks checked. LINF/CINF tables, LCW payloads and 4×4 tile pointers confirmed ([vqa](formats/vqa.md)). Open: display pixel-format masks and RGB output | [formats/vqa.md](formats/vqa.md), [running-game test](NEEDS_A_RUNNING_GAME.md#q9-what-colours-does-the-vqa-frame-callback-present) |
| Q10 | Music and sound. **Mostly answered:** the 6,696 level sounds in the 18 sidecar archives are RIFF WAVE, format 17 (IMA ADPCM) ([level sheets](levels/README.md)). The 38 `MUSIC1..4` tracks and their Miles stream path are documented ([formats/audio.md](formats/audio.md)). The stem initializer was traced and 37 entries join. One name remains open | [formats/audio.md](formats/audio.md) |
| Q11 | Scripts. **Partly answered:** all original MAP scripts frame exactly with the 39 native opcode lengths; the dispatch tables, event pools, predicates, timers and the 480 Hz host frame clock are mapped ([events](lol3-script-events.md)); each opcode row on the [opcode page](lol3-script-opcodes.md) is marked CONFIRMED or UNCONFIRMED. The UNCONFIRMED effects remain open | [Script opcodes](lol3-script-opcodes.md), [object dispatch](lol3-object-dispatch.md) |
| Q12 | Items, spells, dialogue and combat. **Partly answered:** the 343-row item table, 28 spell definitions, the dialogue and quest tag lookup (2,641 of 2,642 dialogue commands join), the creature hit resolver, item-use dispatch, cast cost and mana debit are traced. Six regular handlers are mapped. Open: the remaining handler effects, two alternate cast resources, discount selectors and mitigation mask names | [Items](lol3-item-dispatch.md), [spells](lol3-spell-dispatch.md), [dialogue](lol3-dialogue-dispatch.md), [combat](lol3-combat-dispatch.md), [running-game test](NEEDS_A_RUNNING_GAME.md#q12-which-live-cast-consumes-an-alternate-resource) |
| Q13 | Native save header, global and level directories, and compression are mapped. Remaining payload meanings are open | [Native saves](lol3-native-saves.md), [running-game test](NEEDS_A_RUNNING_GAME.md#q13-which-original-save-bytes-follow-one-controlled-action) |
