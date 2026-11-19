# LoL3 reverse-engineering status

**As of:** 2026-11-19. What is documented about the original game, which tool reads it, what the tools check on the game files, and what is open. This table replaces the earlier "closure" wording; the older pages are kept as history.

Run the checks: `python3 tools/check_all.py --data <DAT>` (17 checks; all pass on the English GOG copy).

**Rating** (counted by `tools/rating.py`; see [how we rate](HOW_WE_RATE.md)):

<!-- rating:begin -->
- **Files read:** 51 of 56 files in `DAT` (2,306.1 of 2,574.4 MiB) are accounted for to the last byte by a reader here.
- **Rules traced:** 243 statements labelled CONFIRMED against the program or the files, 76 labelled UNCONFIRMED, on 71 current pages.
- **Seen in the running game:** 3 of 5 probes that need the original game running are answered.
- **Open questions:** 13: 3 answered, 5 mostly, 5 partly.
<!-- rating:end -->

**Columns:** *Pages* = where it is described. *Tool check* = what `--check` measures on the game files. *Open* = numbered in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md).

**Running-game results** (original program under Wine with a debugger and a silent audio device, one run each; [procedures and results](NEEDS_A_RUNNING_GAME.md)): the texture format (Q6) and the movie colour conversion (Q9) are answered for one display; a spell that spends an item charge instead of mana (Q12) and the save fields of a turn, a step and an item move (Q13) are partly answered.

| Area | Pages | Tool check (re-run 2026-11-18) | Open |
|---|---|---|---|
| WSX archives | [format page](formats/wsx.md), [wsx-extraction](wsx-extraction.md) (history), [container inventory](container-inventory.md) (history) | `extract_wsx_entries`: 51 of 52 `DAT/*.WSX` parse (count, 12-byte records, payload sizes sum to the file), 7,549 entries and 76 native names match their keys. Both cache copies fail the ordinary exact-size check (`check_all` tests the shipped `DAT/` copy). The game-folder copy, written by the game when it runs, has a separate directory of 40 allocation rows | Q1 |
| LMF light maps | [format page](formats/lmf.md), [native reader](lol3-lmf-reader.md) | 18 LMF entries, 5,256 stored LZO1X groups, 424,288 decoded member lengths checked with `--decode` | Q3 |
| MAP and ODF level files | [format page](formats/map-odf.md), [native readers](lol3-map-odf-readers.md), [map-format](map-format.md) (history), [level catalog notes](level-catalog-notes.md) (history), [level file types](level-file-types.md) (history) | measured: 18 MAP and 18 ODF entries; MAP section 1 = 8 × field 20 in all 18. `lol3_level_report` checks the surface and waypoint joins (118,951 surfaces, 2,384 waypoints, 36 paths). `lol3_map_spans` re-counts waypoint byte +6, the name classes, the path labels, the 1,784 bytes before field 16 and the 167,942 section-1 rows. | Q4, Q5 |
| Textures | [Texture formats](formats/textures.md), [texture bake and PNG](lol3-texture-bake.md#cache-record-to-png), [tex-format](tex-format.md) (history), [texture 028E evidence](texture-028e-evidence.md) (history) | The census of the game-folder `cdcache.wsx` (written by the game when it runs) joins all 15,118 mip records to arm-3 palettes. The PNG tool decodes 10,669 and verifies 4,429 records as SMD frame references and reports the 20 unconfirmed ones by flag. All 18 level wrappers frame. Optional LZO expansion checks all 49,684 palette joins and matches the four installed banks. | Q1, Q6, Q7 |
| Byte-pattern labels (QWOD0, SWOD4) | [structural phase](lol3-structural-phase.md) (history), [semantic phase](lol3-semantic-phase.md), [witness map](../evidence/lol3-witness-map.md) | `lol3_claimed_edges`: QWOD0 `C5 A5` counts 195/2/1/0, no MAP column steps from `C5` to `A5`, SWOD4 surface byte +4 is 0/2/6/`0x0B` on 2,393/14/29/0 rows. `--decode` checks the light-map sample high bytes | Q8 |
| Level sheets | [levels/](levels/README.md) | `lol3_level_report`: 18 level archives, each with its four named entries (.LMF .MAP .ODF .TE_ by hash); 6,696 sidecar sounds, all RIFF WAVE format 17 (IMA ADPCM) | Q4, Q10 |
| Movies, music, sound | [movies (VQA)](formats/vqa.md), [music and sound](formats/audio.md), [container inventory](container-inventory.md) (history) | `lol3_media_check`: 19 named VQA movies, 26,357 indexed frames, 38 MP3-in-WAVE music tracks, 6,696 IMA ADPCM level sounds; LINF/CINF rows join all 270 codebooks, and each frame holds one pointer stream. `lol3_name_hash`: 31 stem keys join 37 of those tracks; no stored C string hashes to the remaining key | Q9, Q10 |
| Executable (`LOL3.DAT`) | [MAP and ODF readers](lol3-map-odf-readers.md), [texture palette sources](lol3-texture-palette-sources.md), [WSX](lol3-wsx-reader.md), [LMF](lol3-lmf-reader.md), [texture bake](lol3-texture-bake.md), [dispatch search](lol3-dispatch-search.md) | — | Q11 |
| Game logic: script dispatch, objects, items, spells, dialogue, combat | [script opcodes and framing](lol3-script-opcodes.md), [object and script dispatch](lol3-object-dispatch.md), [items](lol3-item-dispatch.md), [spells](lol3-spell-dispatch.md), [dialogue](lol3-dialogue-dispatch.md), [combat](lol3-combat-dispatch.md), [events, predicates and timers](lol3-script-events.md), [level script summaries](levels/notes/README.md) | measured: all 18 MAP command streams (54,966 offsets) frame exactly with the native size decoder; native entry points traced; `lol3_script_notes`: 18 summaries, 54,940 object and 4,040 region records, 16,876/2,201 direct references; 2,641 of 2,642 dialogue commands join a dialogue tag | Q11, Q12 |
| Saves | [native saves](lol3-native-saves.md) | Native slot directories measured in 47 original saves with 417 level blocks. Four further autosaves isolate the first position group's heading and Z coordinate and one item transfer from the quick slot to the cursor. [Writer traces and offsets](lol3-native-saves.md#controlled-saves-with-a-null-sink) | Q13 |

A row is done when it has a page, a working reader, a passing check and no open point. Today none of the rows meets that; WSX, LMF and the row-span textures have readers with checks.
