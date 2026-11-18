# Start here, by goal

You need Python 3.8+ (optional: the system LZO library, `apt install liblzo2-2`) and your own copy of *Lands of Lore III* (the English GOG release). Point the tools at its `DAT` folder once; some tools also read the program `LOL3.DAT` and the game-written `cdcache.wsx` from the folder above it:

```bash
export LOL3_DAT=/path/to/your/LoL3/DAT
python3 tools/check_all.py         # 12 checks; the last line should read ALL 12 CHECKS PASSED
```

Words you do not know are in the [glossary](GLOSSARY.md). What is known and what is open: [STATUS](STATUS.md) and [open questions](OPEN_QUESTIONS.md). Write tool output outside the repository.

Follow the engine from startup to saving in [How Lands of Lore III works](HOW_THE_GAME_WORKS.md).

## I want to open the archives

1. Read [formats/wsx.md](formats/wsx.md): the WSX layout, the name hash and a worked example.
2. Extract the entries of one archive: `python3 tools/extract_wsx_entries.py --data $LOL3_DAT --stems CKEEP --out ../wsx-out`. Without `--stems` it writes every archive (about 2.3 GB).
3. How the program reads them: [lol3-wsx-reader.md](lol3-wsx-reader.md).

## I want to understand a level

1. Start with the level's sheet in [levels/](levels/README.md): its named entries, light map, MAP/ODF header and sounds (`python3 tools/lol3_level_report.py --data $LOL3_DAT --out ../sheets`).
2. Read [formats/map-odf.md](formats/map-odf.md) and the [native MAP and ODF readers](lol3-map-odf-readers.md).
3. Light maps: [formats/lmf.md](formats/lmf.md), `python3 tools/walk_lmf_leaves.py --check --data $LOL3_DAT` (add `--decode` with liblzo2 installed).

## I want to follow the scripts

1. The level's [script summary](levels/notes/README.md): counts of triggers, effects and targets, and one worked excerpt.
2. Every opcode with its native effect: [lol3-script-opcodes.md](lol3-script-opcodes.md); events, predicates and timers: [lol3-script-events.md](lol3-script-events.md); dispatch: [lol3-object-dispatch.md](lol3-object-dispatch.md).
3. Full per-record listings for your own copy: `python3 tools/lol3_script_notes.py --data $LOL3_DAT --out ../lol3-notes`.
4. [Follow one region event](tutorial-one-event.md) from entry to a moving floor.

## I want to know how items, spells, dialogue and combat work

[Items](lol3-item-dispatch.md), [spells](lol3-spell-dispatch.md), [dialogue and quests](lol3-dialogue-dispatch.md), [combat](lol3-combat-dispatch.md). Each claim cites the program address; UNCONFIRMED marks what is still a reading.

## I want to look at textures

1. [formats/textures.md](formats/textures.md): the `.TE_` wrapper and the row-span records.
2. `python3 tools/lol3_texture_archive.py --check --data $LOL3_DAT` (the 18 wrappers) and `python3 tools/lol3_texture_spans.py --check --data $LOL3_DAT` (the cache records; skipped if the game has not written its cache).
3. Colours: [texture palette sources](lol3-texture-palette-sources.md) and the [texture bake](lol3-texture-bake.md).
4. Export one texture with `python3 tools/lol3_texture_png.py --data "$LOL3_DAT" --offset 0x12C6E2 --out ../texture.png`. The offset is from the worked cache example. Use `--check` for the records and flags in your own cache.

## I want to read save files

[lol3-native-saves.md](lol3-native-saves.md): slot names, header, directories and compression in the original program.

## I want to help

Pick an open question in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md); each says what would settle it. See [CONTRIBUTING.md](../CONTRIBUTING.md).
