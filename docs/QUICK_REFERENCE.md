# Format quick reference

Run the commands from the repository root with `LOL3_DAT` set to your
original installation's `DAT` folder. `LOL3_SLOT` is a slot you saved
while playing. Cache checks use the game-folder cache (written by the game, one folder above `DAT`) when it exists.
Texture expansion and SMD run checks use liblzo2. See [Start here](START_HERE.md).

| File or entry | What it contains | Format and evidence | Tool | Command |
|---|---|---|---|---|
| `.WSX` | Keyed resource archive | [WSX](formats/wsx.md), [name lookup](lol3-wsx-reader.md#resource-name-key) | WSX directory checker | `python3 tools/extract_wsx_entries.py --check` |
| `cdcache.wsx`, `cdcache.hdr` | `DAT/cdcache.wsx`: shipped cache seed; `cdcache.hdr`: header copy; game-folder `cdcache.wsx`: written by the game at run time (allocator rows and texture banks), not shipped | [Native cache reader](lol3-wsx-reader.md#cache-index-lifecycle), [texture bake](lol3-texture-bake.md) | Texture PNG checker | `python3 tools/lol3_texture_png.py --check` |
| `.MAP` | Points, surfaces, paths and event and command pools | [MAP and ODF](formats/map-odf.md) | Level report | `python3 tools/lol3_level_report.py --check` |
| MAP event and command pools | Region and object scripts | [Script events](lol3-script-events.md), [opcodes](lol3-script-opcodes.md) | Script checker | `python3 tools/lol3_script_framing.py --check` |
| `.ODF` | Definition and placement tables for level objects, including creature definitions | [ODF reader](lol3-map-odf-readers.md), [item definitions](lol3-item-dispatch.md#definition-directory) | Level report checks the level's named member | `python3 tools/lol3_level_report.py --check` |
| `.LMF` | Grouped and compressed light-map samples | [LMF](formats/lmf.md) | LMF checker | `python3 tools/walk_lmf_leaves.py --check` |
| `.TE_`, `.TEX` | Packed level texture banks and expanded/shared texture data | [Texture banks](formats/textures.md), [palette sources](lol3-texture-palette-sources.md) | Bank expansion checker | `python3 tools/lol3_texture_archive.py --check --decode` |
| `.SMD` | Slice resources loaded from SLICECD archives | [SMD frame references](lol3-texture-bake.md#smd-slice-frame-references) | Cache checker verifies and expands referenced frames | `python3 tools/lol3_texture_png.py --check --decode-slices` |
| `.VQA` | Indexed movie frames, codebooks and sound chunks | [VQA](formats/vqa.md) | Media checker | `python3 tools/lol3_media_check.py --check` |
| RIFF WAVE members, including music named `.AUD` | IMA ADPCM level samples and MPEG Layer III music streams | [Audio](formats/audio.md) | Media checker | `python3 tools/lol3_media_check.py --check` |
| `.PHT` | Four loose files. Every byte is the one cycle of 0x1010000 bytes. The programs do not name them; whether the game opens them is open | [PHT](formats/pht.md) | PHT checker | `python3 tools/lol3_pht.py --check` |
| `.TRR` | Keyed localized dialogue and quest tables | [Dialogue and message tables](lol3-dialogue-dispatch.md) | Python reads the original qevent count | `python3 -c 'import sys; f=open(sys.argv[1], "rb"); f.seek(0x5987786); print(int.from_bytes(f.read(4), "little"))' "$LOL3_DAT/locallng.wsx"` |
| Numbered save slots and `$AUTOSAV.XXX` | Header, preview, global data and saved levels | [Native saves](lol3-native-saves.md#slot-header-and-stream) | Save header reader | `python3 tools/lol3_save_header.py "$LOL3_SLOT"` |
| `.LSV`, `global.img` | Native level block and XOR base resource for selected global sections | [Save writer](lol3-native-saves.md#level-blocks-and-chunking) | Save reader locates the copied level blocks in a slot | `python3 tools/lol3_save_header.py "$LOL3_SLOT"` |
| `LOL3.EXE`, `LOL3.DAT` | Launcher and original Windows PE32 game image | [Image and address convention](lol3-lmf-reader.md), [launcher](NEEDS_A_RUNNING_GAME.md) | Script checker uses the original native opcode table | `python3 tools/lol3_script_framing.py --check` |
