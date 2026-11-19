# What's new

Newest first. One line per question worked on, new tool or visible change; each question bullet gives its state. Details are on the linked pages; the counts are in the [rating](../README.md#rating).

## 19 November 2026

- **Level sheets.** Each sheet lists the commands per opcode, the waypoint and path counts, and the five placement tables by type with their row ids. `lol3_level_report.py --check` fails when `docs/levels` differs from what the tool writes. `check_all.py` still runs twenty-four checks.
- **Reader listings.** The checks that already run can also print directory rows, format fields and the named table bytes. Nothing is written unless an output path is given, and `check_all.py` still runs twenty-four checks. The region byte-index table length is still a gap ([tools](../tools/README.md#reader-parity)).
- **Script browser.** `lol3_script_browser.py` groups one level's commands by opcode and prints the one-line meaning from the opcode page. It does not list each command.
- **Save inspector.** `lol3_save_header.py` prints the named slot fields, both directories and the other header bytes as hex with offsets. A level block long enough for a header lists its 75 section starts and lengths. `--check` uses a synthetic slot and the version compares in `LOL3.DAT`.
- **Level schematic.** The QWOD0 drawing adds hollow waypoint squares, path runs and the rows of all five placement tables (type 3, type 16, creature, mover, item), numbered from 1, with a legend. The scale fits the surface edges; marks outside them and overlapping numbers are left out and counted in the footer, and `--no-labels` draws no numbers. `--check` still regenerates that picture and compares it byte for byte.
- **Reader parity.** [tools/README](../tools/README.md#reader-parity) lists every current format and rules table with its reader, its check, and the text or drawing a reader gets. Rows with no such output are marked gap.
- **Link check.** `doc_links.py` resolves every relative link and anchor in the README and the docs, and `check_all.py` runs it.
- **Repeated blocks shown.** `lol3_pht.py` shows the four `.PHT` files are prefixes of one repeating cycle, and `lol3_cache_seed.py` shows the shipped cache body is one block repeated; these five files are listed separately in the rating, not counted as read. What the bytes mean and what reads them stays open ([PHT](formats/pht.md); Q1 is partly answered).
- **Counted rating.** The README and [STATUS](STATUS.md) show four counted lines instead of a percentage; [how we rate](HOW_WE_RATE.md) explains them.
- **Script commands (Q11, now mostly answered).** Each object command is traced for every kind of object it can target; floors and ceilings that move under script control are described ([opcodes](lol3-script-opcodes.md)).
- **Light maps (Q3, now mostly answered).** One flag marks smooth per-vertex lighting, and a colour field is identified ([LMF reader](lol3-lmf-reader.md)).
- **Spells and items (Q12, partly answered).** The two spell-cost discounts, the creature damage resistances, the second spell-charge counter and fourteen item-use handlers are traced ([spells](lol3-spell-dispatch.md), [items](lol3-item-dispatch.md), [combat](lol3-combat-dispatch.md)). Open: the second counter's live debit, each handler's effect and the on-screen names.
- **Level data (Q4, Q5 now mostly answered).** The remaining map spans and the level-object name table are tabulated; no reader of the labels or names is found. Two old claims about byte patterns in the shared MAP block were tested and found not to hold. Q8 stays partly answered: no reader of that block is known.
- **Shipped cache file (Q1, partly answered).** It is 51 copies of one block. The program, the game-written cache and the other data files are ruled out as its source; the real source is still unknown.
- **Music names (Q10, mostly answered).** Every stored string was hashed against the one unnamed music track. None matches, so the track stays unnamed.
- **Pictures.** Three misleading diagrams were removed; the one map drawing is regenerated and compared by its check.
- **New checks:** `rating.py`, `lol3_combat_census.py`, `lol3_map_spans.py`, `lol3_claimed_edges.py`, `lol3_name_hash.py`, `lol3_cache_seed.py`, `lol3_odf_companions.py`, `lol3_native_checks.py`.

## 18 November 2026

- **Running-game results.** The texture colour format under Wine, the movie colour conversion, one spell's charge cost and three save fields were looked at in the original game; the texture and movie colour formats and the save fields answer their probes, while the spell question (Q12) and the save question (Q13) stay partly answered ([NEEDS_A_RUNNING_GAME](NEEDS_A_RUNNING_GAME.md)).
- **Guides.** [Start here](START_HERE.md), [how the game works](HOW_THE_GAME_WORKS.md), a [quick reference](QUICK_REFERENCE.md) and a [worked example](tutorial-one-event.md).
- **Format and program pages** for archives, light maps, textures, scripts, items, spells, dialogue, combat, saves, movies and music, each with a `--check`.
- **Level sheets and script summaries** for all 18 levels.
