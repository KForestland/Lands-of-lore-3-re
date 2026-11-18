# Start here

You need Python 3.8+ and your own copy of the game (English GOG release). Set `LOL3_DAT` to the game's `DAT/` folder; some tools also read `LOL3.DAT` and the game-written `cdcache.wsx` from its parent folder.

```bash
export LOL3_DAT=/path/to/your/LoL3/DAT
python3 tools/check_all.py         # the last line should read ALL 7 CHECKS PASSED
```

| I want to… | Read | Run |
|---|---|---|
| see what is known and what is open | [STATUS](STATUS.md), [open questions](OPEN_QUESTIONS.md) | `tools/check_all.py` |
| read the archives | [WSX](formats/wsx.md) | `tools/extract_wsx_entries.py --data $LOL3_DAT --out <folder outside the repo>` |
| look at level layout and light maps | [MAP and ODF](formats/map-odf.md), [LMF light maps](formats/lmf.md) | `tools/walk_lmf_leaves.py --check --data $LOL3_DAT` |
| look at textures | [textures](formats/textures.md) | `tools/lol3_texture_spans.py --check --data $LOL3_DAT` |
| follow the scripts | [script opcodes](lol3-script-opcodes.md), [object dispatch](lol3-object-dispatch.md) | `tools/lol3_script_framing.py --check --data $LOL3_DAT` |
| understand a term | [glossary](GLOSSARY.md) | — |

Write tool output outside the repository; `repo_guard.py` fails if game files, media or stray images are committed.
