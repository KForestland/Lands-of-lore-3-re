# Open questions

Numbered so pages and the [STATUS table](STATUS.md) can point to them. Each says what is known and what would settle it.

## At a glance

One line per question: its state and what would settle what is left.

| # | State | What would settle the rest |
|---|---|---|
| Q1 | Partly | The game writes the large cache when it runs; trace the cache writer to explain the records after the header's range |
| Q2 | Answered | Names of the remaining entries: find their name strings in the program |
| Q3 | Partly | Trace the renderer's reads of a light-map member (flags, header +8, the extra 32 bytes) |
| Q4 | Partly | Waypoints, paths and surfaces are confirmed; trace waypoint byte +6, the 26-byte names, the 31-byte path slots, the extra bytes before field 16 and the section-1 fields |
| Q5 | Partly | Trace the companion reader of the field-3 rows and resolve the tags that are object ids |
| Q6 | Answered for cache spans | Trace what happens to the baked colours on the display device |
| Q7 | Mostly | The editor-name branch (`0x43FFE4–0x44000D`) converges on the retail reader; only a differently framed standalone file remains unwitnessed |
| Q8 | Open | Apply the MAP/ODF readers to the QWOD0 and SWOD4 bytes |
| Q9 | Partly | VQA tables, LCW and the 4×4 pointer callback are confirmed; follow the display pixel-format masks to RGB output |
| Q10 | Mostly | Music format and the `AIL_open_stream` path are confirmed; trace the initializer of the stem table `0x629070` to join keys to names |
| Q11 | Partly | Trace the UNCONFIRMED opcode effects one by one |
| Q12 | Partly | Trace the per-index item effect handlers, the two alternate cast resources and discount selectors, and the mitigation mask names |
| Q13 | Partly | Compare original save pairs written before and after one known action |

## Questions

| # | Question | Where |
|---|---|---|
| Q1 | `cdcache.wsx`: two different files carry this name. The one in `DAT/` (3,264,114 bytes) and the one in the game folder (104,896,114 bytes) both have a 9-entry header covering 52,663,793 bytes. The game-folder copy holds the 854 texture records, 420 of them after the area the header covers ([formats/textures.md](formats/textures.md)). Native expansion and the secondary allocator directory are confirmed, including eight occupied spans. The compact seed’s origin and row byte +0x17 remain open | [Native WSX reader](lol3-wsx-reader.md) |
| Q2 | **Answered.** Native rotate-right name hash, case normalization and 76 exact name/key joins. Names of other entries remain unconfirmed | [Native WSX reader](lol3-wsx-reader.md#resource-name-key) |
| Q3 | LMF light maps: native directory, grouped LZO1X and decoded member sizes confirmed. Member flags, header +8 and the extra 32 bytes remain open | [Native LMF reader](lol3-lmf-reader.md) |
| Q4 | MAP field 0 confirmed as counted 16.16 X/Z coordinates. Its tail holds the waypoints, paths and surfaces, all read natively ([readers](lol3-map-odf-readers.md)). Open: waypoint byte +6, the 26-byte names, the 31-byte path slots, the extra bytes before field 16 and the section-1 fields | [Native MAP reader](lol3-map-odf-readers.md) |
| Q5 | ODF readers, table strides and the fields of the type-tagged field-3 definitions mapped (most tags read as creatures or actors, e.g. RHOUND, ORC, SPIDER; a few are object ids, so the creature reading is UNCONFIRMED). Other per-row meanings remain open | [Native ODF reader](lol3-map-odf-readers.md) |
| Q6 | **Answered for cache spans.** All 854 spans join to arm-3 source palettes. Device presentation after the bake remains open | [Palette source inventory](lol3-texture-palette-sources.md) |
| Q7 | All 18 original `.TE_` banks expand through LZO1X. The former `+1` witness is inside a compressed block. The editor-name branch `0x43FFE4–0x44000D` converges on the same reader; only a differently framed standalone file remains unwitnessed | [Texture formats](formats/textures.md) |
| Q8 | What the QWOD0 and SWOD4 byte-pattern labels mean in the game. Open: the MAP/ODF readers now exist but have not been applied to these labels | [lol3-semantic-phase.md](lol3-semantic-phase.md) |
| Q9 | Movies. **Partly answered:** the 19 `MOVIES1..4` entries are named VQA files read by `0x50DF70`; frame index and sound chunks checked. LINF/CINF tables, LCW payloads and 4×4 tile pointers confirmed ([vqa](formats/vqa.md)). Open: display pixel-format masks and RGB output | [formats/vqa.md](formats/vqa.md) |
| Q10 | Music and sound. **Partly answered:** the 6,696 level sounds in the 18 sidecar archives are RIFF WAVE, format 17 (IMA ADPCM) ([level sheets](levels/README.md)). The 38 `MUSIC1..4` tracks and their Miles stream path are documented ([formats/audio.md](formats/audio.md)). Open: the stem table `0x629070` | [formats/audio.md](formats/audio.md) |
| Q11 | Scripts. **Partly answered:** all original MAP scripts frame exactly with the 39 native opcode lengths; the dispatch tables, event pools, predicates, timers and the 480 Hz host frame clock are mapped ([events](lol3-script-events.md)); each opcode row on the [opcode page](lol3-script-opcodes.md) is marked CONFIRMED or UNCONFIRMED. The UNCONFIRMED effects remain open | [Script opcodes](lol3-script-opcodes.md), [object dispatch](lol3-object-dispatch.md) |
| Q12 | Items, spells, dialogue and combat. **Partly answered:** the 343-row item table, 28 spell definitions, the dialogue and quest tag lookup (2,641 of 2,642 dialogue commands join) the creature hit resolver, item-use dispatch, cast cost and mana debit are traced. Open: per-index item effect handlers, the two alternate cast resources and discount selectors, mitigation mask names | [Items](lol3-item-dispatch.md), [spells](lol3-spell-dispatch.md), [dialogue](lol3-dialogue-dispatch.md), [combat](lol3-combat-dispatch.md) |
| Q13 | Native save header, global and level directories, and compression are mapped. Remaining payload meanings are open | [Native saves](lol3-native-saves.md) |
