# Lands of Lore III: file formats and game data

*Lands of Lore III* is a first-person role-playing game by Westwood Studios (1999). This repository documents what is known about its original data files and gives you Python tools that read them from your own copy of the game.

It contains documentation, tools and small diagrams. It contains no game files and no extracted game pictures, sounds, movies or text.

LoL3 is less fully documented than the first two games. Every page says what was measured, which program address or file offset proves it (CONFIRMED) or what is still a reading (UNCONFIRMED), and what would settle the rest.

## What you get

- **Format pages** in [`docs/formats/`](docs/formats): [WSX](docs/formats/wsx.md), [LMF](docs/formats/lmf.md), [MAP and ODF](docs/formats/map-odf.md), [textures](docs/formats/textures.md), each with a worked example from the game files.
- **Level sheets** in [`docs/levels/`](docs/levels/README.md): one per level, generated from the archives.
- **Executable pages** in [`docs/`](docs/README.md): the WSX, LMF, texture, MAP/ODF, script, item, spell, dialogue, combat and save readers in the game program `LOL3.DAT`.
- **Tools** in [`tools/`](tools/README.md): nine checks (`check_all.py`), a WSX reader, an LMF light-map checker, texture record, palette and `.TE_` wrapper checkers, a script framing check, the level-sheet writer, the script-notes writer and `repo_guard.py`.
- **Script summaries** in [`docs/levels/notes/`](docs/levels/notes/README.md): per level, counts of triggers, effects and targets, with one worked excerpt.
- **Guides:**
  - [Start here, by goal](docs/START_HERE.md)
  - [glossary](docs/GLOSSARY.md)
  - [open questions](docs/OPEN_QUESTIONS.md)

## Quick start

You need Python 3.8+ and your own copy of the game, the English GOG release (the script check pins `LOL3.DAT` by its hash). The tools read `DAT/` and, for `LOL3.DAT` and the texture cache, its parent folder. The game program is `LOL3.DAT` (a 1.6 MB Windows PE file); `LOL3.EXE` is a small launcher. The large `cdcache.wsx` in the game folder is a cache the game writes when it runs: the two texture checks report SKIP if it is missing.

```bash
git clone https://github.com/KForestland/Lands-of-lore-3-re.git
cd Lands-of-lore-3-re
export LOL3_DAT=/path/to/your/LoL3/DAT      # the game's DAT folder
python3 tools/check_all.py                  # 9 checks, ends with ALL 9 CHECKS PASSED
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
| MAP, ODF | Header, section 1, the point table and the ODF type-tagged definitions (334) read through the native readers; the rest open (Q4, Q5) |
| Textures | Row-span records: all 854 in this installation's texture cache decode exactly and join to palette sources; the 18 `.TE_` wrappers decode (465 LZO1X chunks); a standalone editor format is unconfirmed (Q7) |
| Movies, music | Containers listed; formats open (Q9, Q10) |
| Level sounds | RIFF WAVE, format 17 (IMA ADPCM) in the 18 sidecar archives ([level sheets](docs/levels/README.md)) |
| Scripts | All 18 levels' scripts frame exactly with the 39 native opcode lengths; every opcode, event pool, predicate and timer formula traced, effects marked CONFIRMED or UNCONFIRMED; per-level summaries (Q11) |
| Items, spells, dialogue, combat | 343 item rows, 28 spell definitions, the dialogue and quest tag lookup (2,641 of 2,642 commands join) and the creature hit resolver traced in the program; cast entry, per-item use and mitigation open (Q12) |
| Saves | Header, directories and compression mapped on 47 original-program saves; payload meanings open (Q13) |

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
- a machine path or an assistant name.

The release procedure also checks every commit identity (`repo_guard.py --check --release`, see [CONTRIBUTING](CONTRIBUTING.md)).

## The other Lands of Lore games

Formats the three games share, with links to the LoL1 and LoL2 repositories: [docs/series-formats.md](docs/series-formats.md).

## Sources

Facts are checked against the original files and the original program (`LOL3.DAT`), with addresses or file offsets cited on each page. This is independent documentation. See [`CONTRIBUTING.md`](CONTRIBUTING.md) to help.
