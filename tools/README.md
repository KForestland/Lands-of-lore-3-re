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
| `check_all.py` | all checks below | prints each line, then `ALL 9 CHECKS PASSED` |
| `repo_guard.py` | the repository | no game files, media, stray images, machine paths, words from the optional local word list; with `--release` also foreign commit identities |
| `extract_wsx_entries.py` | `DAT/*.WSX` | parses every WSX and writes nothing (51/52; `cdcache.wsx` is open question Q1) |
| `walk_lmf_leaves.py` | the LMF entries inside the WSX files | checks directory coverage for all 18. Optional `--decode` with liblzo2 checks every member header. |
| `lol3_level_report.py` | the 18 level archives and their sound sidecars | with `--out DIR` writes the sheets (the repository's are in `docs/levels/`); checks the four named entries per level, the MAP section-1 rule and that every sidecar entry is WAVE |
| `lol3_texture_spans.py` | the game-written `cdcache.wsx` in the game folder | every row-span texture record consumes exactly (854 of 854 in our cache); SKIP if the cache is missing |
| `lol3_texture_palettes.py` | the same cache | every texture joins one palette source through selector arm 3; prints offsets only; SKIP if the cache is missing |
| `lol3_script_framing.py` | `LOL3.DAT` and the 18 MAP entries | all script streams frame exactly with the native size table; counts only |
| `lol3_texture_archive.py` | the 18 `.TE_` entries in the level archives | every LZO1X-wrapped bank frames (465 chunks); with `--decode` (liblzo2) expands each and compares the 4 cached copies, SKIPPED if the cache is missing; counts only |
| `lol3_script_notes.py` | `LOL3.DAT` and the 18 MAP entries | `--check` re-derives the tracked summaries; `--out DIR` (outside the repository) writes the full per-record listings for your own copy; `--summary DIR` writes the summaries |

`lol3_cli.py` is a shared library for the options above, not a command.
