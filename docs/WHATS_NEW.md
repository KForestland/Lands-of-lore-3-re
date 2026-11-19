# What's new

Newest first. One line per answered question, new tool or visible change. Details are on the linked pages; the counts are in the [rating](../README.md#rating).

## 19 November 2026

- **Counted rating.** The README and [STATUS](STATUS.md) show four counted lines instead of a percentage; [how we rate](HOW_WE_RATE.md) explains them.
- **Script commands (Q11, now mostly answered).** Each object command is traced for every kind of object it can target; floors and ceilings that move under script control are described ([opcodes](lol3-script-opcodes.md)).
- **Light maps (Q3, now mostly answered).** One flag marks smooth per-vertex lighting, and a colour field is identified ([LMF reader](lol3-lmf-reader.md)).
- **Spells and items (Q12).** The two spell-cost discounts, the creature damage resistances, the second spell-charge counter and fourteen item-use handlers are traced ([spells](lol3-spell-dispatch.md), [items](lol3-item-dispatch.md), [combat](lol3-combat-dispatch.md)).
- **Level data (Q4, Q5 now mostly answered).** The remaining map spans and the level-object name table are tabulated; two old claims about byte patterns (Q8) were tested and found not to hold.
- **Shipped cache file (Q1).** It is 51 copies of one block; the program, the game-written cache and the other data files are ruled out as its source.
- **Music names (Q10).** Every stored string was hashed against the one unnamed music track; none matches.
- **Pictures.** Three misleading diagrams were removed; the one map drawing is regenerated and compared by its check.
- **New checks:** `rating.py`, `lol3_combat_census.py`, `lol3_map_spans.py`, `lol3_claimed_edges.py`, `lol3_name_hash.py`, `lol3_cache_seed.py`, `lol3_odf_companions.py`, `lol3_native_checks.py`.

## 18 November 2026

- **Running-game results.** The texture colour format under Wine, the movie colour conversion, one spell's charge cost and three save fields were observed in the original game ([NEEDS_A_RUNNING_GAME](NEEDS_A_RUNNING_GAME.md)).
- **Guides.** [Start here](START_HERE.md), [how the game works](HOW_THE_GAME_WORKS.md), a [quick reference](QUICK_REFERENCE.md) and a [worked example](tutorial-one-event.md).
- **Format and program pages** for archives, light maps, textures, scripts, items, spells, dialogue, combat, saves, movies and music, each with a `--check`.
- **Level sheets and script summaries** for all 18 levels.
