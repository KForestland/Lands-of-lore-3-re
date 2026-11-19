# Lands of Lore III: file formats and game data

*Lands of Lore III* is a first-person role-playing game by Westwood Studios (1999). This repository documents what is known about its original data files and gives you Python tools that read them from your own copy of the game.

It contains documentation, tools and small diagrams. It contains no game files and no extracted game pictures, sounds, movies or text.

## At a glance

- **What this is:** documentation of the original 1999 Windows game's data files and engine, checked against the game files and the original program `LOL3.DAT`. It is less complete than the LoL1 and LoL2 repositories.
- **What you can do today:** unpack every archive the game ships with, read level geometry, light maps and scripts, export textures to PNG (after running the game once, which writes its texture cache), check movies, music and sounds, draw a level plan with waypoints and placements, and follow one level event from entry to effect.
- **Start in five minutes:** the [Quick start](#quick-start) below, then [Start here, by goal](docs/START_HERE.md), [How the game works](docs/HOW_THE_GAME_WORKS.md) or the [worked example](docs/tutorial-one-event.md).
- **Recipes:** [cookbook](docs/COOKBOOK.md), seven short runs with the command and the first lines it prints.
- **What is still unknown:** the [open questions](docs/OPEN_QUESTIONS.md), counted in the [rating](#rating). Open points include some item effects, how the second spell counter is filled in ordinary play, and final screen composition; two answers were checked on one display setting only. Some questions can only be settled by watching the original game run. Answered probes are counted in the rating; which ones and how: [NEEDS_A_RUNNING_GAME](docs/NEEDS_A_RUNNING_GAME.md#answered-probes). Some probes were also tried on [edited saves](docs/EDITED_SAVES.md), copies of a game-written save with a few bytes changed.
- **What changed lately:** [what's new](docs/WHATS_NEW.md), newest first.
- **The three games:** [LoL1](https://github.com/KForestland/lands-of-lore-1-re) · [LoL2](https://github.com/KForestland/lands-of-lore-2-re) · [LoL3](https://github.com/KForestland/Lands-of-lore-3-re) ([what they share](docs/series-formats.md), [how the engine changed](docs/engine-evolution.md), [how they gate progress and scale numbers](docs/series-progress-and-numbers.md)).

## Rating

These are counts of work done, not a percentage of how complete the project is. They are produced by `tools/rating.py` on the English GOG copy; [how we rate](docs/HOW_WE_RATE.md) explains each line and what it does not claim.

<!-- rating:begin -->
- **Files read:** 51 of 56 files in `DAT` (2,306.1 of 2,574.4 MiB) have their whole layout read by a tool here: every byte belongs to a known header, directory or entry (what is inside an entry may still be only partly understood). 5 more (268.3 MiB: the four `.PHT` files and the shipped `cdcache.wsx`) are shown byte for byte to be one block repeated (not counted as read); what those bytes mean and what reads them is unknown.
- **Rules traced:** the pages mark 425 statements CONFIRMED (proved from the program code or the files) and 65 UNCONFIRMED (a reading not yet proved), on 80 current pages; old notes kept as history are not counted.
- **Seen in the running game:** 3 of 5 probes that need the original game running are answered (a question can have more than one probe); 0 of them rest on edited saves only.
- **Open questions:** 13 numbered questions: 3 answered, 7 mostly answered, 3 partly answered.
<!-- rating:end -->

![Overhead QWOD0 schematic from MAP edges, waypoints and placements](docs/images/qwod0-schematic.svg)

The level QWOD0 seen from above, drawn from its map file: each line is an edge of a surface; dark edges belong to one surface and pale edges are shared. Hollow squares are waypoints, dashed lines are paths (this level has none), and dots are the rows of the five placement tables (type 3, type 16, creature, mover, item), numbered from 1; numbers that would overlap are left out and counted under the legend. Heights are not drawn. [MAP evidence and drawing command](docs/formats/map-odf.md#overhead-schematic).

## Tools at a glance

[How a level is put together](docs/HOW_A_LEVEL_IS_PUT_TOGETHER.md) · [Numbers at a glance](docs/NUMBERS.md)

What you can look at with your own copy of the game. Run from the clone with `export LOL3_DAT=/path/to/your/LoL3/DAT` (and `LOL3_SLOT` set to one of your own save files for the last line); pictures and files go only where you point them (here `../lol3-out`, outside the clone; make it first with `mkdir -p ../lol3-out`). The texture line needs the cache the game writes when it first runs. Every tool and option is in [`tools/README.md`](tools/README.md), with a table of every format and how to look at it.

| To see | Command |
|---|---|
| A level drawn from above, with waypoints and placements | `python3 tools/lol3_level_schematic.py --data "$LOL3_DAT" QWOD0 --out ../lol3-out/qwod0.svg` |
| Level sheets | `python3 tools/lol3_level_report.py --data "$LOL3_DAT" --out ../lol3-out/levels` |
| A level's script commands by opcode, with their meaning | `python3 tools/lol3_script_browser.py --data "$LOL3_DAT" QWOD0` |
| A level's waypoints and paths | `python3 tools/lol3_map_spans.py --data "$LOL3_DAT" --list QWOD0` |
| A level's object names and AI files | `python3 tools/lol3_odf_companions.py --data "$LOL3_DAT" --list QWOD0` |
| An archive's directory | `python3 tools/extract_wsx_entries.py --data "$LOL3_DAT" --list --stems QWOD0` |
| A light-map directory | `python3 tools/walk_lmf_leaves.py --data "$LOL3_DAT" --stem QWOD0` |
| Item definitions and their handlers | `python3 tools/lol3_combat_census.py --data "$LOL3_DAT" --items` |
| Spell rows | `python3 tools/lol3_native_checks.py --data "$LOL3_DAT" --spells` |
| A movie's chunks | `python3 tools/lol3_media_check.py --data "$LOL3_DAT" --movie mvolc` |
| Music tracks | `python3 tools/lol3_media_check.py --data "$LOL3_DAT" --tracks` |
| A texture as PNG (after the game has run once) | `python3 tools/lol3_texture_png.py --data "$LOL3_DAT" --offset 1222718 --out ../lol3-out/texture.png` |
| A saved game you made | `python3 tools/lol3_save_header.py --data "$LOL3_DAT" "$LOL3_SLOT"` |

## What you get

[Walk through one level from its map to its exit](docs/TOUR.md). Search the [JSON documentation index](docs/index.json) by page, question or tool. What each format writer proves, byte-identical or decode-identical, is on one page: [round trip](docs/ROUND_TRIP.md).

- **Format pages** in `docs/formats/` ([docs index](docs/README.md)): [WSX](docs/formats/wsx.md), [LMF](docs/formats/lmf.md), [MAP and ODF](docs/formats/map-odf.md), [textures](docs/formats/textures.md), [movies (VQA)](docs/formats/vqa.md), [music and sound](docs/formats/audio.md), [PHT](docs/formats/pht.md), each with a worked example from the game files.
- **Level sheets** in [`docs/levels/`](docs/levels/README.md): one per level, generated from the archives.
- **Program pages** in [`docs/`](docs/README.md): how the game program `LOL3.DAT` itself reads archives, light maps, textures, maps, scripts, items, spells, dialogue, combat and saves.
- **Tools** in [`tools/`](tools/README.md): readers and checks for every format above, directory and table listings, a texture-to-PNG exporter, a level drawer, a save inspector and the level-sheet and script-notes writers; `check_all.py` runs all thirty-one checks.
- **Script summaries** in [`docs/levels/notes/`](docs/levels/notes/README.md): per level, counts of triggers, effects and targets, with one worked excerpt.
- **Guides:**
  - [Start here, by goal](docs/START_HERE.md)
  - [glossary](docs/GLOSSARY.md)
  - [open questions](docs/OPEN_QUESTIONS.md)

## Quick start

Use Python 3.8 or later and your own copy of the English GOG release (`LOL3.DAT`, SHA-256 starting `9a9eb04c8f404ebf`; the tools that read the program check it by its hash). The quick start and synthetic tests use the Python standard library. The optional `--decode` checks use the system LZO library (`apt install liblzo2-2` on Debian or Ubuntu).

The tools read the `DAT/` folder and two files in the game folder above it:
- `LOL3.DAT`, the game program (a 1.6 MB Windows PE file; `LOL3.EXE` is only a small launcher);
- `cdcache.wsx`, a large cache the game writes there when it runs. The three cache texture checks report SKIP if it is missing.

Do not confuse it with the 3 MB `DAT/cdcache.wsx` the game ships (the seed the cache starts from), which `lol3_cache_seed.py` reads. The duplicate copies of `LOCAL.WSX` and `locallng.wsx` next to `LOL3.DAT` are not read by the tools (the copies in `DAT/` are).

```bash
git clone https://github.com/KForestland/Lands-of-lore-3-re.git
cd Lands-of-lore-3-re
export LOL3_DAT="/path/to/your/LoL3/DAT"
python3 tools/check_all.py                  # 31 passed with a matching cache and your own saves; a never-run copy: 27 passed, 4 skipped
python3 -m unittest discover -s tests
python3 tools/extract_wsx_entries.py --data "$LOL3_DAT" --check
python3 tools/lol3_script_notes.py --data "$LOL3_DAT" --out ../lol3-notes   # full script listings, outside the repository
python3 tools/full_report.py --out "../lol3-out/report"
```

The `check_all` line prints `51/52 WSX files parse … failing: cdcache.wsx`. That file is a cache, not an archive ([Q1](docs/OPEN_QUESTIONS.md)), and `unexpected failures: none` means the check passed.

The script check prints, for example:

```text
CHECK script_notes: 18 level summaries, 54,940 object and 4,040 region records, 16,876/2,201 direct object/region references
```

The script command writes two listings per level (object and region), 36 in all, with record offsets, opcodes, operands and the native effect. The report command writes an inventory, level sheets and text counts to the named folder. On Windows, use `py -3` in place of `python3`. Set `$env:LOL3_DAT = 'D:\Games\LoL3\DAT'` in PowerShell, or pass `--data` with a quoted folder path to each tool.

## Status

Full table with evidence: [`docs/STATUS.md`](docs/STATUS.md). "Q11" and the like are numbered questions in [`docs/OPEN_QUESTIONS.md`](docs/OPEN_QUESTIONS.md).

| Area | State |
|------|-------|
| WSX archives | Layout documented; all 51 shipped WSX archives in `DAT/` parse; the 52nd, `cdcache.wsx`, does not parse as an archive. Its body is 51 copies of one block, listed separately in the rating (Q1: what writes the block) |
| Loose PHT files | Four files, each a prefix of one repeating block, listed separately in the rating ([PHT](docs/formats/pht.md)). What the bytes mean and what reads them is open |
| LMF light maps | The native directory yields 5,256 stored groups and 424,288 members in 18 entries ([LMF](docs/formats/lmf.md), Q3). |
| MAP, ODF | Header, section 1, waypoints, paths, surfaces and the ODF type-tagged definitions (334) read through the native readers. Section-1 bytes each have a reader; waypoint byte +6, the label spans and the bytes before field 16 are measured (Q4, Q5 mostly) |
| Textures | [Cache to PNG](docs/lol3-texture-bake.md#cache-record-to-png): 10,669 of 15,118 mip records in the game-written cache decode using native palette sources; six flag values are still open. All 18 `.TE_` wrappers decode (Q1, Q6, Q7). |
| Movies, music | Movie files (VQA) decoded; on a 16-bit display under Wine the intro's colours are converted from 15-bit to 16-bit (Q9); the 38 music tracks are MP3 inside WAV files, played through the Miles sound library (Q10) |
| Level sounds | WAV files using IMA ADPCM compression, in the 18 per-level sound archives ([level sheets](docs/levels/README.md)) |
| Scripts | All 18 levels' scripts frame exactly with the 39 native opcode lengths; every opcode, event pool, predicate and timer formula traced, the object commands resolved per target class (only the on-screen look of effect objects is open); per-level summaries (Q11) |
| Items, spells, dialogue, combat | Traced in the program: 343 item rows, all 113 nonzero regular item handlers read one by one, 28 spell definitions, the dialogue and quest tag lookup (2,641 of 2,642 commands join), the creature hit resolver, cast cost and mana debit. Open: what the objects the handlers build do on screen, and mitigation names (Q12) |
| Saves | Header, directories and compression mapped from 47 of our own saved games, written by the original program (not included; `lol3_save_writer.py --check` rebuilds your own byte for byte); a running-game comparison isolates the fields of a turn, a step and an item move; other payload meanings open (Q13) |

## Repository layout

- [`docs/`](docs/README.md): format pages, program pages, status, open questions, glossary. Older checkpoint notes are kept as history and marked so.
- [`docs/levels/`](docs/levels/README.md): one sheet per level; [`docs/levels/notes/`](docs/levels/notes/README.md): script summaries.
- [`tools/`](tools/README.md): readers and checks.
- [`evidence/`](evidence): lists of program addresses and files that back up the pages.
- [`examples/`](examples/README.md): where the level drawing above comes from and how it is checked.

## Asset policy

No game files and no dumps of extracted game media are included; short byte excerpts appear in the documentation as examples. `tools/check_all.py` includes `repo_guard.py`, which fails if a game file, media file, stray image, large file or machine path is committed.

## The other Lands of Lore games

Formats the three games share, with links to the LoL1 and LoL2 repositories: [docs/series-formats.md](docs/series-formats.md).

## Sources

Facts are checked against the original files and the original program (`LOL3.DAT`), with addresses or file offsets cited on each page. This is independent documentation. See [`CONTRIBUTING.md`](CONTRIBUTING.md) to help.
