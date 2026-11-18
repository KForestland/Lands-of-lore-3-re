# Lands of Lore III: file formats and game data

*Lands of Lore III* is a first-person role-playing game by Westwood Studios (1999). This repository documents what is known about its original data files and gives you Python tools that read them from your own copy of the game.

It contains documentation, tools and small diagrams. It contains no game files and no extracted game pictures, sounds, movies or text.

LoL3 is much less understood than the first two games. Many pages say what was measured, what was tried, and what would settle the rest. That is a result too.

## What you get

- **Format pages** in [`docs/formats/`](docs/formats): [WSX](docs/formats/wsx.md), [LMF](docs/formats/lmf.md), [MAP and ODF](docs/formats/map-odf.md), [textures](docs/formats/textures.md), each with a worked example from the game files.
- **Level sheets** in [`docs/levels/`](docs/levels/README.md): one per level, generated from the archives.
- **Executable pages** in [`docs/`](docs/README.md): the WSX, LMF, texture, MAP/ODF, script, item, spell, dialogue, combat and save readers in the game program `LOL3.DAT`.
- **Tools** in [`tools/`](tools/README.md): seven checks (`check_all.py`), a WSX reader, an LMF light-map checker, texture record and palette checkers, a script framing check, the level-sheet writer and `repo_guard.py`.
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
python3 tools/check_all.py                  # 7 checks, ends with ALL 7 CHECKS PASSED
python3 tools/extract_wsx_entries.py --data "$LOL3_DAT" --check
```

## Status

Full table with evidence: [`docs/STATUS.md`](docs/STATUS.md).

| Area | State |
|------|-------|
| WSX archives | Layout documented; 51 of 52 `DAT/*.WSX` parse; `cdcache.wsx` does not (Q1) |
| LMF light maps | The native directory yields 5,256 stored groups and 424,288 members in 18 entries ([LMF](docs/formats/lmf.md), Q3). |
| MAP, ODF | Header and one section layout measured on all 18 levels; the rest open (Q4, Q5) |
| Textures | Row-span records: all 854 in this installation's texture cache decode exactly and join to palette sources; the second format open (Q7) |
| Movies, music | Containers listed; formats open (Q9, Q10) |
| Level sounds | RIFF WAVE, format 17 (IMA ADPCM) in the 18 sidecar archives ([level sheets](docs/levels/README.md)) |
| Executable, scripts, items, spells, dialogue, combat, saves | Native readers and dispatch traced; scripts frame exactly with the native size table; many effects open (Q11–Q13, [STATUS](docs/STATUS.md)) |

## Repository layout

- [`docs/`](docs): format pages, status, open questions, glossary. Older checkpoint notes are kept as history.
- [`tools/`](tools/README.md): readers and checks.
- [`evidence/`](evidence): evidence indexes for the byte-pattern statistics.
- [`examples/`](examples/README.md): three diagrams of those statistics, drawn without game pixels.

## Asset policy

No game files and no dumps of extracted game media are included; short byte excerpts appear in the documentation as examples. `tools/check_all.py` includes `repo_guard.py`, which fails on:
- a committed game file, media file or stray image;
- a machine path;
- any commit identity other than the project's.

## Sources

Facts are checked against the original files and the original program (`LOL3.EXE`), with addresses or file offsets cited on each page. This is independent documentation.
