# LoL3 reverse-engineering status

**As of:** 2026-11-18. What is documented about the original game, which tool reads it, what the tools check on the game files, and what is open. This table replaces the earlier "closure" wording; the older pages are kept as history.

Run the checks: `python3 tools/check_all.py --data <DAT>` (6 checks; all pass on the English GOG copy).

**Columns:** *Pages* = where it is described. *Tool check* = what `--check` measures on the game files. *Open* = numbered in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md).

| Area | Pages | Tool check (re-run 2026-11-18) | Open |
|---|---|---|---|
| WSX archives | [format page](formats/wsx.md), [wsx-extraction](wsx-extraction.md), [container inventory](container-inventory.md) | `extract_wsx_entries`: 51 of 52 `DAT/*.WSX` parse (count, 12-byte records, payload sizes sum to the file), 7,549 entries and 76 native names match their keys. The `DAT/cdcache.wsx` size fails the ordinary archive check | Q1 |
| LMF light maps | [format page](formats/lmf.md), [native reader](lol3-lmf-reader.md) | 18 LMF entries, 5,256 stored LZO1X groups, 424,288 decoded member lengths checked with `--decode` | Q3 |
| MAP and ODF level files | [format page](formats/map-odf.md), [native readers](lol3-map-odf-readers.md), [map-format](map-format.md), [level catalog notes](level-catalog-notes.md), [level file types](level-file-types.md) | measured: 18 MAP and 18 ODF entries; MAP section 1 = 8 × field 20 in all 18 | Q4, Q5 |
| Textures | [format page](formats/textures.md), [tex-format](tex-format.md), [texture 028E evidence](texture-028e-evidence.md) | `lol3_texture_spans`: all 854 row-span records in the game-folder `cdcache.wsx` consume exactly (815 with flags 0x028E, 39 with 0x828E). [Palette sources](lol3-texture-palette-sources.md) verifies all 854 joins | Q1, Q6, Q7 |
| Byte-pattern labels (QWOD0, SWOD4) | [structural phase](lol3-structural-phase.md), [semantic phase](lol3-semantic-phase.md), [witness map](../evidence/lol3-witness-map.md) | — | Q8 |
| Level sheets | [levels/](levels/README.md) | `lol3_level_report`: 18 level archives, each with its four named entries (.LMF .MAP .ODF .TE_ by hash); 6,696 sidecar sounds, all RIFF WAVE format 17 (IMA ADPCM) | Q11 |
| Movies, music, sound | [container inventory](container-inventory.md) | — | Q9, Q10 |
| Executable (`LOL3.DAT`) | [MAP and ODF readers](lol3-map-odf-readers.md), [texture palette sources](lol3-texture-palette-sources.md), [WSX](lol3-wsx-reader.md), [LMF](lol3-lmf-reader.md), [texture bake](lol3-texture-bake.md), [dispatch search](lol3-dispatch-search.md) | — | Q11 |
| Game logic: script dispatch, objects, items, spells, dialogue, combat | [object and script dispatch](lol3-object-dispatch.md), [items](lol3-item-dispatch.md), [spells](lol3-spell-dispatch.md), [dialogue](lol3-dialogue-dispatch.md), [combat](lol3-combat-dispatch.md) | measured: all 18 MAP command streams (54,966 offsets) frame exactly with the native size decoder; native entry points traced | Q11, Q12 |
| Saves | [native saves](lol3-native-saves.md) | measured on the 47 files of the original SAVEGAME folder: 417 level blocks, every section and LZO chunk decodes to its stated length | Q13 |

A row is done when it has a page, a working reader, a passing check and no open point. Today none of the rows meets that; WSX, LMF and the row-span textures have readers with checks.
