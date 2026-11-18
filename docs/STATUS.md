# LoL3 reverse-engineering status

**As of:** 2026-11-18. What is documented about the original game, which tool reads it, what the tools check on the game files, and what is open. This table replaces the earlier "closure" wording; the older pages are kept as history.

Run the checks: `python3 tools/check_all.py --data <DAT>` (4 checks; all pass on the English GOG copy).

**Columns:** *Pages* = where it is described. *Tool check* = what `--check` measures on the game files. *Open* = numbered in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md).

| Area | Pages | Tool check (re-run 2026-11-18) | Open |
|---|---|---|---|
| WSX archives | [format page](formats/wsx.md), [wsx-extraction](wsx-extraction.md), [container inventory](container-inventory.md) | `extract_wsx_entries`: 51 of 52 `DAT/*.WSX` parse (count, 12-byte records, payload sizes sum to the file), 7,549 entries; `cdcache.wsx` does not | Q1, Q2 |
| LMF light maps | [format page](formats/lmf.md), [reader](lol3-lmf-reader.md), [lmf-size-formula](lmf-size-formula.md) | `walk_lmf_leaves`: 18 LMF entries, 5,256 stored LZO1X groups decode, 424,288 light-map members all fit `44 + 2 × w × h` | Q3 |
| MAP and ODF level files | [format page](formats/map-odf.md), [map-format](map-format.md), [level catalog notes](level-catalog-notes.md), [level file types](level-file-types.md) | measured: 18 MAP and 18 ODF entries; MAP section 1 = 8 × field 20 in all 18 | Q4, Q5 |
| Textures | [format page](formats/textures.md), [tex-format](tex-format.md), [texture 028E evidence](texture-028e-evidence.md) | `lol3_texture_spans`: all 854 row-span records in the game-folder `cdcache.wsx` consume exactly (815 with flags 0x028E, 39 with 0x828E) | Q1, Q6, Q7 |
| Byte-pattern labels (QWOD0, SWOD4) | [structural phase](lol3-structural-phase.md), [semantic phase](lol3-semantic-phase.md), [witness map](../evidence/lol3-witness-map.md) | — | Q8 |
| Movies, music, sound | [container inventory](container-inventory.md) | — | Q9, Q10 |
| Executable (`LOL3.EXE`, `LOL3.DAT`) | [level file types](level-file-types.md) (names only) | — | Q11 |
| Items, spells, dialogue, saves, combat | not documented | — | Q12 |

A row is done when it has a page, a working reader, a passing check and no open point. Today none of the rows meets that; WSX, LMF and the row-span textures have readers with checks.
