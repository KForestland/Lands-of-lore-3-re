# Open questions

Numbered so pages and the [STATUS table](STATUS.md) can point to them. Each says what is known and what would settle it.

| # | Question | Where |
|---|---|---|
| Q1 | `cdcache.wsx`: its header (9 entries) promises 52,663,793 bytes of payload, but the file is 3,264,114 bytes. Is it a cache written at run time, like LoL2's `CDCACHE.MIX`, and how is it indexed? | [wsx-extraction.md](wsx-extraction.md) |
| Q2 | WSX records: the hash function behind the `u32 hash`, and the meaning of the `u32` field between hash and size | [wsx-extraction.md](wsx-extraction.md) |
| Q3 | LMF leaf blocks: what a leaf holds (not raw i16 vertices, not LZO1X as a whole); needs the reader in the executable | [lmf-size-formula.md](lmf-size-formula.md) |
| Q4 | MAP fields 1 and 2: the 8-byte records and the `0xFFFF`-terminated placement headers | [map-format.md](map-format.md) |
| Q5 | ODF and table38: field meanings and how levels use them | [level-catalog-notes.md](level-catalog-notes.md) |
| Q6 | Texture colour: the per-texture colour table and the u16 bake lookup at `0x6601B8` / `0x44B6E0` | [texture-028e-evidence.md](texture-028e-evidence.md) |
| Q7 | The LEVED `+1` `.tex` packs: a second texture format, not decoded | [tex-format.md](tex-format.md) |
| Q8 | What the QWOD0 and SWOD4 byte-pattern labels mean in the game; needs an executable reader | [lol3-semantic-phase.md](lol3-semantic-phase.md) |
| Q9 | Movies: the format of the `MOVIES1..4` entries and the 10 unidentified entries | [container-inventory.md](container-inventory.md) |
| Q10 | Music and sound: the format of the `MUSIC1..4` and sound entries | [container-inventory.md](container-inventory.md) |
| Q11 | The executable: readers for WSX, LMF leaves and textures, and any script or event dispatch table | [level-file-types.md](level-file-types.md) |
| Q12 | Items, spells, dialogue, saves and combat: not yet searched in the data or the executable | — |
