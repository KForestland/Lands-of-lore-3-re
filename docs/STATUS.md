# LoL3 reverse-engineering status

**As of:** 2026-11-18. What is documented about the original game, which tool reads it, what the tools check on the game files, and what is open. This table replaces the earlier "closure" wording; the older pages are kept as history.

Run the checks: `python3 tools/check_all.py --data <DAT>` (3 checks; all pass on the English GOG copy).

**Columns:** *Pages* = where it is described. *Tool check* = what `--check` measures on the game files. *Open* = numbered in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md).

| Area | Pages | Tool check (re-run 2026-11-18) | Open |
|---|---|---|---|
| WSX archives | [format page](formats/wsx.md), [wsx-extraction](wsx-extraction.md), [container inventory](container-inventory.md) | `extract_wsx_entries`: 51 of 52 `DAT/*.WSX` parse (count, 12-byte records, payload sizes sum to the file), 7,549 entries; `cdcache.wsx` does not | Q1, Q2 |
| LMF geometry index | [lmf-size-formula](lmf-size-formula.md) | `walk_lmf_leaves`: 18 LMF entries, 45,836 index blocks, 311,934 leaf blocks, every block size on the `(2^n + 2) * 16 + 12` ladder | Q3 |
| MAP and ODF level files | [map-format](map-format.md), [level catalog notes](level-catalog-notes.md), [level file types](level-file-types.md) | — | Q4, Q5 |
| Textures | [tex-format](tex-format.md), [texture 028E evidence](texture-028e-evidence.md) | — (26-payload exact consume to be re-run by a repo tool) | Q6, Q7 |
| Byte-pattern labels (QWOD0, SWOD4) | [structural phase](lol3-structural-phase.md), [semantic phase](lol3-semantic-phase.md), [witness map](../evidence/lol3-witness-map.md) | — | Q8 |
| Movies, music, sound | [container inventory](container-inventory.md) | — | Q9, Q10 |
| Executable (`LOL3.EXE`, `LOL3.DAT`) | [level file types](level-file-types.md) (names only) | — | Q11 |
| Items, spells, dialogue, saves, combat | not documented | — | Q12 |

A row is done when it has a page, a working reader, a passing check and no open point. Today none of the rows meets that; WSX and LMF have readers with checks.
