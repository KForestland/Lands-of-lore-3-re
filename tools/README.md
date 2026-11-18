# Tools

## Common options

The tools follow one set of rules:
- `--help` changes nothing.
- The game's `DAT` folder comes from `--data` or `$LOL3_DAT`; there is no built-in path.
- Nothing is written unless you pass `--out` (or `-o`), or `--summary DIR` to `lol3_script_notes.py` (it writes the per-level summaries, as in `docs/levels/notes/`).
- `--check` prints one `CHECK` line and exits 0 when it passes.

Run examples outside the repository.

| Tool | Reads | `--check` |
|---|---|---|
| `check_all.py` | all checks below | prints each line, then `ALL 12 CHECKS PASSED` |
| `repo_guard.py` | the repository | no game files, media, stray images, machine paths, words from the optional local word list; with `--release` also foreign commit identities |
| `extract_wsx_entries.py` | `DAT/*.WSX` | parses every WSX and writes nothing (51/52; `cdcache.wsx` is open question Q1) |
| `walk_lmf_leaves.py` | the LMF entries inside the WSX files | checks directory coverage for all 18. Optional `--decode` with liblzo2 checks every member header. |
| `lol3_level_schematic.py` | a level archive's MAP entry | projects surface edges into an overhead SVG (lines only). Give a level stem and `--out` (inside the repository only `docs/images/` or `examples/`); `--check` regenerates `docs/images/qwod0-schematic.svg` and compares it byte for byte. |
| `lol3_level_report.py` | the 18 level archives and their sound sidecars | with `--out DIR` writes the sheets (the repository's are in `docs/levels/`); checks the four named entries per level, the MAP section-1 rule, the surface and waypoint joins and that every sidecar entry is WAVE |
| `lol3_texture_spans.py` | the game-written `cdcache.wsx` in the game folder | every row-span texture record consumes exactly (854 of 854 in our cache); SKIP if the cache is missing |
| `lol3_texture_palettes.py` | the same cache | every texture joins one palette source through selector arm 3; prints offsets only; SKIP if the cache is missing |
| `lol3_texture_png.py` | the same cache | bakes one indexed record with `--offset` and writes a PNG only to `--out`. `--check` decodes all supported records and reports the other classes; SKIP if the cache is missing. |
| `lol3_script_framing.py` | `LOL3.DAT` and the 18 MAP entries | all script streams frame exactly with the native size table; counts only |
| `lol3_texture_archive.py` | the 18 `.TE_` entries in the level archives | every LZO1X-wrapped bank frames (465 chunks); with `--decode` (liblzo2) expands each, checks the palette joins (692 / 4,635 / 44,357 = 49,684 descriptors) and compares the 4 cached copies, SKIPPED if the cache is missing; counts only (`check_all` runs it without `--decode`) |
| `lol3_script_notes.py` | `LOL3.DAT` and the 18 MAP entries | `--check` re-derives the tracked summaries; `--out DIR` (outside the repository) writes the full per-record listings for your own copy; `--summary DIR` writes the summaries |
| `lol3_media_check.py` | the `MOVIES1..4`, `MUSIC1..4` and level sound archives, and `LOL3.DAT` | the 19 named movies and their frame index, the 38 music tracks and 6,696 level sounds; counts only |
| `lol3_save_header.py` | one save slot you name (a player save, not a game file) | prints the preview, 61 global and 18 level offsets and lengths as JSON; writes nothing; no `--check` |

`lol3_cli.py` is a shared library for the options above, not a command.
