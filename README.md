# Lands of Lore III: file formats and game data

*Lands of Lore III* is a first-person role-playing game by Westwood Studios (1999). This repository documents what is known about its original data files and gives you Python tools that read them from your own copy of the game.

It contains documentation, tools and small diagrams. It contains no game files and no extracted game pictures, sounds, movies or text.

## At a glance

- **What this is:** documentation of the original 1999 Windows game's data files and engine, checked against the game files and the original program `LOL3.DAT`. It is less complete than the LoL1 and LoL2 repositories.
- **What you can do today:** unpack every archive, read level geometry, light maps and scripts, export textures to PNG (after running the game once, which writes its texture cache), check movies, music and sounds, draw a level outline, and follow one level event from entry to effect.
- **Start in five minutes:** the [Quick start](#quick-start) below, then [Start here, by goal](docs/START_HERE.md), [How the game works](docs/HOW_THE_GAME_WORKS.md) or the [worked example](docs/tutorial-one-event.md).
- **What is still unknown:** the [open questions](docs/OPEN_QUESTIONS.md) (counts in the [rating](#rating); two of the answers hold for one display or renderer); open points include most item effects, a floor pickup in a save, and other display modes. Some were tried in the [running game](docs/NEEDS_A_RUNNING_GAME.md) (the texture and movie colour formats are answered there); the rest need later-game saves.
- **The three games:** [LoL1](https://github.com/KForestland/lands-of-lore-1-re) · [LoL2](https://github.com/KForestland/lands-of-lore-2-re) · [LoL3](https://github.com/KForestland/Lands-of-lore-3-re) ([what they share](docs/series-formats.md), [how the engine changed](docs/engine-evolution.md)).

## Rating

Counted by `tools/rating.py` on the English GOG copy; [how we rate](docs/HOW_WE_RATE.md) explains each line and what it does not claim.

<!-- rating:begin -->
- **Files read:** 51 of 56 files in `DAT` (2,306.1 of 2,574.4 MiB) are accounted for to the last byte by a reader here.
- **Rules traced:** 255 statements labelled CONFIRMED against the program or the files, 80 labelled UNCONFIRMED, on 71 current pages.
- **Seen in the running game:** 3 of 5 probes that need the original game running are answered.
- **Open questions:** 13: 3 answered, 6 mostly, 4 partly.
<!-- rating:end -->

Every page says what was measured, which program address or file offset proves it (CONFIRMED) or what is still a reading (UNCONFIRMED), and what would settle the rest.

![Overhead QWOD0 schematic from MAP surface edges](docs/images/qwod0-schematic.svg)

QWOD0 seen from above. Dark edges occur once in the surface table and pale edges are shared. [MAP evidence and drawing command](docs/formats/map-odf.md#overhead-schematic).

## What you get

- **Format pages** in [`docs/formats/`](docs/formats): [WSX](docs/formats/wsx.md), [LMF](docs/formats/lmf.md), [MAP and ODF](docs/formats/map-odf.md), [textures](docs/formats/textures.md), each with a worked example from the game files.
- **Level sheets** in [`docs/levels/`](docs/levels/README.md): one per level, generated from the archives.
- **Executable pages** in [`docs/`](docs/README.md): the WSX, LMF, texture, MAP/ODF, script, item, spell, dialogue, combat and save readers in the game program `LOL3.DAT`.
- **Tools** in [`tools/`](tools/README.md): twenty checks (`check_all.py`), a WSX reader, an LMF light-map checker, texture record, palette and `.TE_` wrapper checkers, a texture-to-PNG exporter, a level schematic drawer, a movie and audio check, a shipped-cache check, an ODF name-slot check, a save-header reader, a script framing check, the level-sheet writer, the script-notes writer and `repo_guard.py`.
- **Script summaries** in [`docs/levels/notes/`](docs/levels/notes/README.md): per level, counts of triggers, effects and targets, with one worked excerpt.
- **Guides:**
  - [Start here, by goal](docs/START_HERE.md)
  - [glossary](docs/GLOSSARY.md)
  - [open questions](docs/OPEN_QUESTIONS.md)

## Quick start

You need Python 3.8+ and your own copy of the game: the English GOG release (the script check pins `LOL3.DAT` by its hash). Optional: the system LZO library (`apt install liblzo2-2`) for the `--decode` checks.

The tools read the `DAT/` folder and two files in the game folder above it:
- `LOL3.DAT`, the game program (a 1.6 MB Windows PE file; `LOL3.EXE` is only a small launcher);
- `cdcache.wsx`, a large cache the game writes when it runs. The three cache texture checks report SKIP if it is missing.

The duplicate copies of `LOCAL.WSX` and `locallng.wsx` next to `LOL3.DAT` are not read by the tools (the copies in `DAT/` are).

```bash
git clone https://github.com/KForestland/Lands-of-lore-3-re.git
cd Lands-of-lore-3-re
export LOL3_DAT=/path/to/your/LoL3/DAT      # the game's DAT folder
python3 tools/check_all.py                  # 20 checks, ends with ALL 20 CHECKS PASSED (or 17 passed, 3 skipped if the game has never run)
python3 tools/extract_wsx_entries.py --data "$LOL3_DAT" --check
python3 tools/lol3_script_notes.py --data "$LOL3_DAT" --out ../lol3-notes   # full script listings, outside the repository
```

The script check prints, for example:

```text
CHECK script_notes: 18 level summaries, 54,940 object and 4,040 region records, 16,876/2,201 direct object/region references
```

The `--out` folder then holds one listing per level: every script record with its file offset, opcode, operands and the native effect, for your own copy only.

## Status

Full table with evidence: [`docs/STATUS.md`](docs/STATUS.md).

| Area | State |
|------|-------|
| WSX archives | Layout documented; 51 of 52 `DAT/*.WSX` parse; `cdcache.wsx` does not (Q1) |
| LMF light maps | The native directory yields 5,256 stored groups and 424,288 members in 18 entries ([LMF](docs/formats/lmf.md), Q3). |
| MAP, ODF | Header, section 1, waypoints, paths, surfaces and the ODF type-tagged definitions (334) read through the native readers. Section-1 bytes each have a reader; waypoint byte +6, the label spans and the bytes before field 16 are measured (Q4, Q5 mostly) |
| Textures | [Cache to PNG](docs/lol3-texture-bake.md#cache-record-to-png): 10,669 of 15,118 mip records in the game-written cache decode using native palette sources; six flag values need further work. All 18 `.TE_` wrappers decode (Q1, Q6, Q7). |
| Movies, music | VQA containers, seek tables, LCW and 4×4 pointers traced; under Wine on a 16-bit display the intro converts 5-5-5 codebook words to 5-6-5 (Q9); 38 MP3-in-WAVE music tracks streamed through Miles (Q10) |
| Level sounds | RIFF WAVE, format 17 (IMA ADPCM) in the 18 sidecar archives ([level sheets](docs/levels/README.md)) |
| Scripts | All 18 levels' scripts frame exactly with the 39 native opcode lengths; every opcode, event pool, predicate and timer formula traced, the object commands resolved per target class (only the on-screen look of effect objects is open); per-level summaries (Q11) |
| Items, spells, dialogue, combat | Traced in the program: 343 item rows, fourteen regular item handlers, 28 spell definitions, the dialogue and quest tag lookup (2,641 of 2,642 commands join), the creature hit resolver, cast cost and mana debit. Open: most per-item effects and mitigation names (Q12) |
| Saves | Header, directories and compression mapped on 47 saves the original program wrote in our copy (player saves, not shipped; no tool here re-checks them); a running-game comparison isolates the fields of a turn, a step and an item move; other payload meanings open (Q13) |

## Repository layout

- [`docs/`](docs/README.md): format pages, program pages, status, open questions, glossary. Older checkpoint notes are kept as history and marked so.
- [`docs/levels/`](docs/levels/README.md): one sheet per level; [`docs/levels/notes/`](docs/levels/notes/README.md): script summaries.
- [`tools/`](tools/README.md): readers and checks.
- [`evidence/`](evidence): evidence indexes for the byte-pattern statistics.
- [`examples/`](examples/README.md): three diagrams of those statistics, drawn without game pixels.

## Asset policy

No game files and no dumps of extracted game media are included; short byte excerpts appear in the documentation as examples. `tools/check_all.py` includes `repo_guard.py`, which fails on:
- a committed game file, media file or stray image;
- a file over 300 KB or a generated script listing;
- a machine path, or a word from an optional local word list (`.git/info/private_words`, never tracked).

The release procedure also checks every commit identity (`repo_guard.py --check --release`, see [CONTRIBUTING](CONTRIBUTING.md)).

## The other Lands of Lore games

Formats the three games share, with links to the LoL1 and LoL2 repositories: [docs/series-formats.md](docs/series-formats.md).

## Sources

Facts are checked against the original files and the original program (`LOL3.DAT`), with addresses or file offsets cited on each page. This is independent documentation. See [`CONTRIBUTING.md`](CONTRIBUTING.md) to help.
