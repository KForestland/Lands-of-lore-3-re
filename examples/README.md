# Examples

This folder no longer holds images. Three hand-drawn diagrams of byte-pattern "spines" were removed on 2026-11-19: the labels they drew match no field the native readers consume ([open question Q8](../docs/OPEN_QUESTIONS.md)), so they misled.

The one picture the repository shows, the [QWOD0 schematic](../docs/images/qwod0-schematic.svg), is made by `python3 tools/lol3_level_schematic.py --data DAT QWOD0 --out docs/images/qwod0-schematic.svg`. It draws surface edges, hollow waypoint squares, path runs and the rows of all five placement tables (type 3, type 16, creature, mover, item), numbered from 1, with a legend. Large levels such as BUPP1 (about 650 KB) exceed the repository's 300 KB file limit, so write those outside the repository. Its `--check` (part of `check_all.py`) regenerates it and fails unless the tracked file is byte-identical.
