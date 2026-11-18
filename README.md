# Lands of Lore III: file formats and game data

*Lands of Lore III* is a first-person role-playing game by Westwood Studios (1999). This repository documents what is known about its original data files and gives you Python tools that read them from your own copy of the game.

It contains documentation, tools and small diagrams. It contains no game files and no extracted game pictures, sounds, movies or text.

LoL3 is much less understood than the first two games. Many pages say what was measured, what was tried, and what would settle the rest. That is a result too.

## What you get

- **Format pages** in [`docs/formats/`](docs/formats): [WSX](docs/formats/wsx.md), [LMF](docs/formats/lmf.md), [MAP and ODF](docs/formats/map-odf.md), [textures](docs/formats/textures.md), each with a worked example from the game files.
- **Level sheets** in [`docs/levels/`](docs/levels/README.md): one per level, generated from the archives.
- **Tools** in [`tools/`](tools/README.md): a WSX reader, an LMF light-map checker, a texture-record checker, `check_all.py` and `repo_guard.py`.
- **Guides:**
  - [Start here, by goal](docs/START_HERE.md)
  - [glossary](docs/GLOSSARY.md)
  - [open questions](docs/OPEN_QUESTIONS.md)

## Quick start

You need Python 3.8+ and your own copy of the game.

```bash
git clone https://github.com/KForestland/Lands-of-lore-3-re.git
cd Lands-of-lore-3-re
export LOL3_DAT=/path/to/your/LoL3/DAT      # the game's DAT folder
python3 tools/check_all.py                  # 5 checks, ends with ALL 5 CHECKS PASSED
python3 tools/extract_wsx_entries.py --data "$LOL3_DAT" --check
```

## Status

Full table with evidence: [`docs/STATUS.md`](docs/STATUS.md).

| Area | State |
|------|-------|
| WSX archives | Layout documented; 51 of 52 `DAT/*.WSX` parse; `cdcache.wsx` does not (Q1) |
| LMF light maps | The native directory yields 5,256 stored groups and 424,288 members in 18 entries ([LMF](docs/formats/lmf.md), Q3). |
| MAP, ODF | Header and one section layout measured on all 18 levels; the rest open (Q4, Q5) |
| Textures | Row-span records: all 854 in the texture cache decode exactly; colour and the second format open (Q6, Q7) |
| Movies, music, sound | Containers listed; formats open (Q9, Q10) |
| Executable, items, spells, dialogue, saves, combat | Not yet documented (Q11, Q12) |

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
