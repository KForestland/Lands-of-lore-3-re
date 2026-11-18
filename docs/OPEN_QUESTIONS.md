# Open questions

Numbered so pages and the [STATUS table](STATUS.md) can point to them. Each says what is known and what would settle it.

| # | Question | Where |
|---|---|---|
| Q1 | `cdcache.wsx`: two different files carry this name. The one in `DAT/` (3,264,114 bytes) and the one in the game folder (104,896,114 bytes) both have a 9-entry header covering 52,663,793 bytes. The game-folder copy holds the 854 texture records, 420 of them after the area the header covers ([formats/textures.md](formats/textures.md)). Native expansion, marker and secondary row stride confirmed. Individual slot lifecycle remains open | [Native WSX reader](lol3-wsx-reader.md) |
| Q2 | WSX keys: which name hash and which names produce them (not the LoL2 MIX hashes). **Partly answered:** the second `u32` of a row is the entry offset ([formats/wsx.md](formats/wsx.md)) | [formats/wsx.md](formats/wsx.md) |
| Q3 | LMF light maps: native directory, grouped LZO1X and decoded member sizes confirmed. Member flags, header +8 and the extra 32 bytes remain open | [Native LMF reader](lol3-lmf-reader.md) |
| Q4 | MAP fields 1 and 2: the 8-byte records and the `0xFFFF`-terminated placement headers | [map-format.md](map-format.md) |
| Q5 | ODF and table38: field meanings and how levels use them | [level-catalog-notes.md](level-catalog-notes.md) |
| Q6 | Texture colour: native lookup construction mapped. The source palette for an individual archive texture is open | [Texture bake](lol3-texture-bake.md) |
| Q7 | The LEVED `+1` `.tex` packs: a second texture format, not decoded | [tex-format.md](tex-format.md) |
| Q8 | What the QWOD0 and SWOD4 byte-pattern labels mean in the game; needs an executable reader | [lol3-semantic-phase.md](lol3-semantic-phase.md) |
| Q9 | Movies: the format of the `MOVIES1..4` entries and the 10 unidentified entries | [container-inventory.md](container-inventory.md) |
| Q10 | Music and sound: the format of the `MUSIC1..4` and sound entries | [container-inventory.md](container-inventory.md) |
| Q11 | The native WSX, LMF and texture bake readers are mapped. Archive-backed script or event dispatch remains open | [Dispatch search](lol3-dispatch-search.md) |
| Q12 | Items, spells, dialogue, saves and combat: not yet searched in the data or the executable | — |
