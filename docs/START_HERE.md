# Start here

You need Python 3.8+ and your own copy of the game. Set `LOL3_DAT` to the game's `DAT/` folder.

```bash
export LOL3_DAT=/path/to/your/LoL3/DAT
python3 tools/check_all.py         # the last line should read ALL 4 CHECKS PASSED
```

| I want to… | Read | Run |
|---|---|---|
| see what is known and what is open | [STATUS](STATUS.md), [open questions](OPEN_QUESTIONS.md) | `tools/check_all.py` |
| read the archives | [WSX](wsx-extraction.md) | `tools/extract_wsx_entries.py --data $LOL3_DAT --out <folder outside the repo>` |
| look at level layout and light maps | [MAP and ODF](formats/map-odf.md), [LMF light maps](formats/lmf.md) | `tools/walk_lmf_leaves.py --check --data $LOL3_DAT` |
| look at textures | [texture format](tex-format.md) | — |
| understand a term | [glossary](GLOSSARY.md) | — |

Write tool output outside the repository; `repo_guard.py` fails if game files, media or stray images are committed.
