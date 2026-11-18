# Open questions

Numbered so pages and the [STATUS table](STATUS.md) can point to them. Each says what is known and what would settle it.

| # | Question | Where |
|---|---|---|
| Q1 | `cdcache.wsx`: two different files carry this name. The one in `DAT/` (3,264,114 bytes) and the one in the game folder (104,896,114 bytes) both have a 9-entry header covering 52,663,793 bytes. The game-folder copy holds the 854 texture records, 420 of them after the area the header covers ([formats/textures.md](formats/textures.md)). Native expansion, marker and secondary row stride confirmed. Individual slot lifecycle remains open | [Native WSX reader](lol3-wsx-reader.md) |
| Q2 | **Answered.** Native rotate-right name hash, case normalization and 76 exact name/key joins. Names of other entries remain unconfirmed | [Native WSX reader](lol3-wsx-reader.md#resource-name-key) |
| Q3 | LMF light maps: native directory, grouped LZO1X and decoded member sizes confirmed. Member flags, header +8 and the extra 32 bytes remain open | [Native LMF reader](lol3-lmf-reader.md) |
| Q4 | MAP field 0 confirmed as counted 16.16 X/Z coordinates. Its tail and fields 1 and 2 remain open | [Native MAP reader](lol3-map-odf-readers.md) |
| Q5 | ODF readers, table strides and the fields of the type-tagged field-3 definitions mapped (most tags read as creatures or actors, e.g. RHOUND, ORC, SPIDER; a few are object ids, so the creature reading is UNCONFIRMED). Other per-row meanings remain open | [Native ODF reader](lol3-map-odf-readers.md) |
| Q6 | **Answered for cache spans.** All 854 spans join to arm-3 source palettes. Device presentation after the bake remains open | [Palette source inventory](lol3-texture-palette-sources.md) |
| Q7 | The LEVED `+1` `.tex` packs: a second texture format, not decoded | [tex-format.md](tex-format.md) |
| Q8 | What the QWOD0 and SWOD4 byte-pattern labels mean in the game; needs an executable reader | [lol3-semantic-phase.md](lol3-semantic-phase.md) |
| Q9 | Movies: the format of the `MOVIES1..4` entries and the 10 unidentified entries | [container-inventory.md](container-inventory.md) |
| Q10 | Music and sound: the format of the `MUSIC1..4` and sound entries | [container-inventory.md](container-inventory.md) |
| Q11 | The native WSX, LMF and texture bake readers are mapped. Archive-backed script or event dispatch remains open | [Dispatch search](lol3-dispatch-search.md) |
| Q12 | Items, spells, dialogue, saves and combat: not yet searched in the data or the executable | — |
