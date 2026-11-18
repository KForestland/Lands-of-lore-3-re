# Open questions

Numbered so pages and the [STATUS table](STATUS.md) can point to them. Each says what is known and what would settle it.

## At a glance

One line per question: its state and what would settle what is left.

| # | State | What would settle the rest |
|---|---|---|
| Q1 | Partly | The game writes the large cache when it runs; trace the cache writer to explain the records after the header's range |
| Q2 | Answered | Names of the remaining entries: find their name strings in the program |
| Q3 | Partly | Trace the renderer's reads of a light-map member (flags, header +8, the extra 32 bytes) |
| Q4 | Partly | Trace the readers of MAP fields 1 and 2 and section 2 |
| Q5 | Partly | Trace the companion reader of the field-3 rows and resolve the tags that are object ids |
| Q6 | Answered for cache spans | Trace what happens to the baked colours on the display device |
| Q7 | Mostly | Find a loader for a standalone editor texture pack; none is known in the retail program |
| Q8 | Open | Apply the MAP/ODF readers to the QWOD0 and SWOD4 bytes |
| Q9 | Open | Find the movie reader in `LOL3.DAT` and the 10 unidentified entries |
| Q10 | Partly | Find the music reader in `LOL3.DAT` for `MUSIC1..4` |
| Q11 | Partly | Trace the UNCONFIRMED opcode effects one by one |
| Q12 | Partly | Trace the spell cast entry and mana debit, per-item use effects and mitigation masks |
| Q13 | Partly | Compare original save pairs written before and after one known action |

## Questions

| # | Question | Where |
|---|---|---|
| Q1 | `cdcache.wsx`: two different files carry this name. The one in `DAT/` (3,264,114 bytes) and the one in the game folder (104,896,114 bytes) both have a 9-entry header covering 52,663,793 bytes. The game-folder copy holds the 854 texture records, 420 of them after the area the header covers ([formats/textures.md](formats/textures.md)). Native expansion and the secondary allocator directory are confirmed, including eight occupied spans. The compact seed’s origin and row byte +0x17 remain open | [Native WSX reader](lol3-wsx-reader.md) |
| Q2 | **Answered.** Native rotate-right name hash, case normalization and 76 exact name/key joins. Names of other entries remain unconfirmed | [Native WSX reader](lol3-wsx-reader.md#resource-name-key) |
| Q3 | LMF light maps: native directory, grouped LZO1X and decoded member sizes confirmed. Member flags, header +8 and the extra 32 bytes remain open | [Native LMF reader](lol3-lmf-reader.md) |
| Q4 | MAP field 0 confirmed as counted 16.16 X/Z coordinates. Its tail has a native point table (indexed by actor +0xD4) and a three-part file layout. Remaining point fields and readers for the two other spans remain open | [Native MAP reader](lol3-map-odf-readers.md) |
| Q5 | ODF readers, table strides and the fields of the type-tagged field-3 definitions mapped (most tags read as creatures or actors, e.g. RHOUND, ORC, SPIDER; a few are object ids, so the creature reading is UNCONFIRMED). Other per-row meanings remain open | [Native ODF reader](lol3-map-odf-readers.md) |
| Q6 | **Answered for cache spans.** All 854 spans join to arm-3 source palettes. Device presentation after the bake remains open | [Palette source inventory](lol3-texture-palette-sources.md) |
| Q7 | All 18 original `.TE_` banks expand through LZO1X. The former `+1` witness is inside a compressed block. A standalone editor format remains unconfirmed | [Texture formats](formats/textures.md) |
| Q8 | What the QWOD0 and SWOD4 byte-pattern labels mean in the game. Open: the MAP/ODF readers now exist but have not been applied to these labels | [lol3-semantic-phase.md](lol3-semantic-phase.md) |
| Q9 | Movies: the format of the `MOVIES1..4` entries and the 10 unidentified entries | [container-inventory.md](container-inventory.md) |
| Q10 | Music and sound. **Partly answered:** the 6,696 level sounds in the 18 sidecar archives are RIFF WAVE, format 17 (IMA ADPCM) ([level sheets](levels/README.md)). The `MUSIC1..4` entries and the other sound entries remain open | [container-inventory.md](container-inventory.md) |
| Q11 | Scripts. **Partly answered:** all original MAP scripts frame exactly with the 39 native opcode lengths; the dispatch tables, event pools, predicates and timers are mapped ([events](lol3-script-events.md)); each opcode row on the [opcode page](lol3-script-opcodes.md) is marked CONFIRMED or UNCONFIRMED. The UNCONFIRMED effects remain open | [Script opcodes](lol3-script-opcodes.md), [object dispatch](lol3-object-dispatch.md) |
| Q12 | Items, spells, dialogue and combat. **Partly answered:** the 343-row item table, 28 spell definitions, the dialogue and quest tag lookup (2,641 of 2,642 dialogue commands join) and the creature hit resolver are traced. Open: the spell cast entry and mana debit, per-item use effects, mitigation masks | [Items](lol3-item-dispatch.md), [spells](lol3-spell-dispatch.md), [dialogue](lol3-dialogue-dispatch.md), [combat](lol3-combat-dispatch.md) |
| Q13 | Native save header, global and level directories, and compression are mapped. Remaining payload meanings are open | [Native saves](lol3-native-saves.md) |
