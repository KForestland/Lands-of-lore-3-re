# Tools

<!-- suite-counts:begin -->
- **Original game files.** 42 checks with the required files and dependencies. Quick mode selects 38.
- **Synthetic data.** 113 unit tests.
<!-- suite-counts:end -->

Run `python tools/suite_counts.py --write` to refresh these counts after changing either suite.

Read the original LoL3 data files and replay the checks cited in the reference pages. Format pages are listed in the [docs index](../docs/README.md); terms: [glossary](../docs/GLOSSARY.md).

[Translation guide](../docs/TRANSLATION.md) covers `translate.py` , the FNT reader `translate_fonts.py`, and its game-specific `translate_data.py`.

[Move placements](../docs/LEVEL_EDITOR.md) with `level_edit.py`, `level_edit_data.py` and `level_move_ui.py`.

The `lol.py` job menu opens with `python tools/lol.py`. Add `JOB --help`
to see the job's options. `level_viewer.py` writes an offline HTML plan with clickable details using `level_html.py`.
Use `level_viewer.py --check` to write and read back one plan in a temporary folder.
`level_export.py` writes a Wavefront OBJ surface model with the source texture references.
Add `--textures` to export separate PNGs from your own copy.
[First ten minutes](../docs/FIRST_TEN_MINUTES.md) ·
[Interactive plans](../docs/COOKBOOK.md#open-an-interactive-level-plan)

`edition.py` reads names, file sizes and SHA-256 to identify a measured game copy. `--check` verifies the full fingerprint in `check_all.py`. [Edition fingerprints](../docs/EDITIONS.md)

## Reader tool examples

Run these from the repository folder. Set the data variable as shown under Setup. Create `../lol3-out` before using the save or patch example, and set `LOL3_SLOT` to your save file.

| Tool | Example | Output |
|---|---|---|
| Job menu | `python tools/lol.py --help` | level, text, translate, music, model, movie, sound, save, patch, mod |
| Interactive map | `python tools/level_viewer.py --data "$LOL3_DAT" --check` | QWOD0 page with 1,965 entries |
| Level copy editor | `python tools/level_edit.py --data "$LOL3_DAT" --check` | 18 original archives copied byte-identically and 3 placement kinds verified |
| Translation tables | `python tools/translate.py --data "$LOL3_DAT" --check` | 27 tables, 13,105 rows, 6 indexed fonts |
| Edition fingerprints | `python tools/edition.py --data "$LOL3_DAT" --check` | English GOG release, 1.07a, all 6 fingerprints match |
| Fields from a save | `python tools/lol.py save page "$LOL3_SLOT" --out ../lol3-out/save.html` | Writes save.html with stored values and commands for making an edited copy |
| Archive workspace | `python tools/modkit.py --data "$LOL3_DAT" --check` | Byte-identical rebuild of 22 files from 73 editable entries |
| Patch maker | `python tools/patch.py make --data "$LOL3_DAT" "my mod output" --title "My edit" --out ../lol3-out/edit.json` | Writes a version 3 patch and reports the changed files |
| Level models | `python3 tools/lol.py model --data "$LOL3_DAT" --level QWOD0 --out "../LoL3 model"` | `QWOD0.obj` with 1,430 faces and 1,430 texture reference rows |
| Movie and sound | [Conversion commands](../docs/FIRST_TEN_MINUTES.md#convert-a-movie-or-sound) | `MOVIES2-1.mkv` with 166 frames and `QWOD0S-0.wav` with 49,655 sample frames |
| Program sections | `python tools/lol3_pe_layout.py --data "$LOL3_DAT" --check` | 8 sections and 3 debug payloads, with both file ends reached |

The commands also exercise these Python modules through their user-facing tools.

| Modules | Command above | What they produce |
|---|---|---|
| `level_html.py` | Interactive map | Searchable entries and drawing in one offline page |
| `level_edit_data.py` reads placement fields for the editor, and `level_move_ui.py` supplies the move controls | Level copy editor | Controls in the offline map and placement data for the editor |
| `media_convert.py` | Movie and sound | Writes a selected movie to MKV or sound to WAV |
| `cli_errors.py` | File tools | Formats errors and resolves user-supplied paths |
| `save_edit.py`, `save_page.py` | Fields from a save | An offline field page with one command per editable field |
| `modkit_core.py` | Archive workspace | Manifest, editable entries and verified archive copies |
| `translate_data.py`, `translate_fonts.py` | Translation tables | Counts for the rebuilt text tables and indexed fonts |

The [reader tool check audit](../docs/TOOL_CHECK_AUDIT.md) lists the mistakes tested on generated files.

## Setup

For game data, give `--data` either your installation folder or its `DAT` folder. The readers accept mixed, uppercase or lowercase filenames and keep the spelling of files they copy.

- Python 3.10 or later. The readers and the synthetic tests need only the standard library.
- The optional system LZO library (`apt install liblzo2-2` on Debian or Ubuntu) for the light-map decode and the LZO checks; without it those checks print one SKIP line.
- Your own copy of the English GOG release; point `--data` or `$LOL3_DAT` at its `DAT` folder.
- Three checks need the texture cache the game writes beside `DAT` on its first run, and the save writer needs the game's own saves; without them they report SKIP ([cookbook](../docs/COOKBOOK.md)).

To write the inventory, level sheets and text counts together, use `full_report.py`. [Cookbook](../docs/COOKBOOK.md#write-a-full-report)

Run `python3 tools/lol3_numbers.py --check` to compare the original item, spell and creature numbers with the generated page. It prints `CHECK lol3_numbers: LoL3 tables match docs/NUMBERS.md`. [Numbers at a glance](../docs/NUMBERS.md)

## Common options

The tools follow one set of rules:
- `--help` changes nothing.
- The game's `DAT` folder comes from `--data` or `$LOL3_DAT`; there is no built-in path.
- Nothing is written unless you pass `--out` (or `-o`), or `--summary DIR` to `lol3_script_notes.py` (it writes the per-level summaries, as in `docs/levels/notes/`).
- `--check` prints one `CHECK` line and exits 0 when it passes.

Run examples outside the repository.

| Tool | Reads | `--check` |
|---|---|---|
| `check_all.py` | all checks below | prints each result and a summary, including skips on a never-run copy (no game-written cache: 3 SKIP; no game-written saves: `lol3_save_writer` SKIP). Without liblzo2, `lol3_lzo_writer` and `lol3_save_writer` also SKIP |
| `doc_links.py` | `README.md`, `tools/README.md`, `CONTRIBUTING.md`, `docs/`, and `examples/`/`evidence/` when present | checks links and anchors only (runs no command): every relative link, image link, `<a href>` and GitHub heading anchor resolves; fenced examples are skipped |
| `modkit.py` | the game folder (see [`modkit.py`](#modkitpy)) | unpacks, rebuilds and verifies every supported table in a temporary folder; unchanged files must match byte for byte |
| `repo_guard.py` | the repository | no game files, media, stray images, machine paths, words from the optional local word list; with `--release` also foreign commit identities |
| `extract_wsx_entries.py` | `DAT/*.WSX`. `--list` prints key, offset and size and writes nothing | parses every WSX and writes nothing (51/52; `cdcache.wsx` is open question Q1) |
| `lol3_wsx_writer.py` | the WSX archives in `DAT` (not the `cdcache.wsx` seed) and the loose `LOCAL.WSX` and `locallng.wsx` beside `DAT` | rebuilds each archive in memory from its parsed rows (directory, then the data pool) and compares it byte for byte with the file: 51 DAT and 2 loose archives, 7,614 rows. One member is changed in memory first: the output must differ and re-read with the change. Writes nothing; `cdcache.wsx` is left out ([Q1](../docs/OPEN_QUESTIONS.md)) |
| `walk_lmf_leaves.py` | the LMF entries inside the WSX files. `--stem LEVEL` prints that archive's directory | checks directory coverage for all 18. Optional `--decode` with liblzo2 checks every member header, counts the bit-0 vertex normals and re-counts the +0x0C–+0x13 header words against each member's grid, and prints the distance split (108,537 / 232,181 / 139,039 / 130,568 at 0, 1, 2–7 and 8 or more texels from the corner), 287,177 one-texel insets, 307,470 colours nearest the 2x2 numeric mean, the four quarter summaries and the best 5 × 5 lattice point (58,260). `check_all.py` adds `--decode` when liblzo2 is installed. |
| `lol3_lzo_writer.py` | the 18 LMF and 18 `.TE_` entries in the level archives, the two shared banks `GLOBAL\GLOBAL.TEX` and `GLOBAL\SPELL.TEX` in `LOCAL.WSX`, and the packed SMD frames in `SLICECD1`–`4.WSX` that their mips point at; also the references in the game-written `cdcache.wsx` when present | compresses again with liblzo2 (`lzo1x_1_compress`), a real encoder, not a copy of the stored groups: the new packed bytes differ from the original in every group and block, and each decoded group must be identical. 424,288 LMF members in 5,256 rebuilt groups (new group lengths and member offsets), 465 texture blocks and 15,990 distinct packed SMD frames from 33,068 packed references in the 20 shipped banks (the SMD frames are compared after decoding only and not written back into an archive); one changed member must re-read. The game-written cache's 4,428 packed references, when present, reach no further frame; without the cache the line says so and the check still passes; without liblzo2 the whole check prints one SKIP line. Writes nothing |
| `lol3_level_schematic.py` | a level archive's MAP entry | overhead SVG of surface edges, hollow waypoint squares, path runs and dots for the rows of all five placement tables (type 3, type 16, creature, mover, item), numbered from 1, with a legend. The scale fits the surface edges; waypoints and placements outside them and numbers that would overlap are left out and counted in the footer; `--no-labels` draws no numbers. Give the page name with `--level` and a new SVG file with `--out` (inside the repository only `docs/images/` or `examples/`; large levels such as BUPP1, about 650 KB, exceed the 300 KB repository file limit, so write them outside); `--check` regenerates `docs/images/qwod0-schematic.svg` and compares it byte for byte. The tool prints the path to the SVG. |
| `lol3_level_report.py` | the 18 level archives and their sound sidecars | with `--out DIR` writes the sheets (the repository's are in `docs/levels/`), including commands per opcode, waypoint and path counts, and placement tables by type with row ids; `--check` requires those sheets to match `docs/levels`, and checks the four named entries per level, the MAP section-1 rule, the surface and waypoint joins, that every sidecar entry is WAVE, and that the scripts are 54,940 object records and 4,040 region records with 25 movie indexes and no music or other-level name |
| `lol3_progression.py` | the 18 MAP scripts and `LOL3.DAT` | regenerates [progression](../docs/PROGRESSION.md) (131 portal commands, 82 predicates, earlier rows in walker order, level-to-level graph and steps from QWOD0) and compares it byte for byte; prints `CHECK progression: 131 portals, 82 predicates; docs/PROGRESSION.md matches` |
| `lol3_texture_spans.py` | the game-written `cdcache.wsx` in the game folder | every row-span texture record consumes exactly its height rows inside its width (854 of 854 in our game-written cache; yours may differ); SKIP if the cache is missing |
| `lol3_texture_palettes.py` | the same cache | every texture joins one palette source through selector arm 3; prints offsets only; SKIP if the cache is missing |
| `lol3_texture_png.py` | the same cache. `--list-slices` prints one slice directory and writes nothing | bakes one indexed record with `--offset` and writes a PNG only to `--out`. `--check` decodes all supported records and reports the other classes. A missing cache reports SKIP. Add `--decode-slices` to `--check` to validate the original SMD runs with liblzo2 (`check_all` runs it without `--decode-slices`) |
| `lol3_script_framing.py` | `LOL3.DAT` and the 18 MAP entries. `--subcommands` and `--dispatch` print the opcode-page tables | all script streams frame exactly with the native size table; the check still prints counts only |
| `lol3_texture_archive.py` | the 18 `.TE_` entries in the level archives. `--list LEVEL --decode` prints that bank's descriptors | every LZO1X-wrapped bank frames (465 chunks); with `--decode` (liblzo2) expands each, checks the palette joins (692 / 4,635 / 44,357 = 49,684 descriptors) and compares the 4 cached copies, SKIPPED if the cache is missing (`check_all` runs it without `--decode`) |
| `lol3_script_notes.py` | `LOL3.DAT` and the 18 MAP entries. `--timers LEVEL` prints kind-2 timer counts | `--check` re-derives the tracked summaries; `--out DIR` (outside the repository) writes the full per-record listings for your own copy; `--summary DIR` writes the summaries |
| `lol3_script_browser.py` | one level's MAP object and region streams | groups that level's commands by opcode and prints the opcode page's one-line meaning. It does not list each command. `--out` writes the summary outside the game tree and this repository. For QWOD0 it prints `QWOD0 object commands: 164` and `QWOD0 region commands: 42`. `--check` prints `CHECK script_browser: QWOD0 object 164 commands in 14 opcodes, region 42 commands in 2 opcodes; each line is that opcode's page meaning` |
| `lol3_media_check.py` | the `MOVIES1..4`, `MUSIC1..4` and level sound archives, and `LOL3.DAT`. `--movie`, `--tracks`, `--samples` and `--trr` print one entry's fields; `--trr` does not print payload text | the 19 named movies and their frame index, the 38 music tracks and 6,696 level sounds |
| `lol3_map_spans.py` | `LOL3.DAT` and the 18 MAP entries. `--list` and `--rows` print one level; name slots and path labels stay hex | waypoint byte +6, the 2,330/39/15 name slots, the 36 path labels, the 1,784 bytes before field 16 and the 167,942 section-1 rows |
| `lol3_map_writer.py` | `LOL3.DAT` and the 18 MAP entries. `--coverage STEM` lists every retained range by MAP and WSX offset. `--list STEM` gives offsets, sizes and hashes for four fixed spans | regenerates 18,035,541 of 21,232,680 bytes from fields with a native read. `--check` counts the remaining 3,197,139 bytes in 16 retained classes, compares every MAP byte and reads back edits to a command operand, waypoint, vertex, surface and placements. [Field and range evidence](../docs/lol3-map-odf-readers.md#retained-span-classes) |
| `lol3_text_writer.py` | the TRR tables: every TRR-shaped member of `DAT/locallng.wsx` and of the `locallng.wsx` beside `DAT`, and loose `.trr` files in both folders. `--list` prints each table's file, offset, key, size and row count, never its text | reads all 53 tables (26 members in each `locallng.wsx`, plus loose `PROMPT.TRR`; 26 distinct tables) into (ID, field) rows and writes each again in memory; the bytes must be identical. 26,170 rows counting every copy. Requires the four quest and dialogue tables at the offsets `lol3_media_check.py --trr` reads. Writes nothing |
| `lol3_combat_census.py` | `LOL3.DAT`, the 18 level ODFs and `GLOBAL.WSX`. `--items`, `--mitigation` and `--modes` print the named fields | the 334 creature mitigation records (57 distinct, selector counts) and the 258 regular item definitions on 114 handler indexes |
| `lol3_native_checks.py` | `LOL3.DAT` (and with `--decode-copy` the shipped archives, needs liblzo2). `--list` prints the anchor values; `--spells` prints spell rows and special-definition costs | the world-pickup and copy-dispatch anchors, and the 447 spell-frame words at +8; `--decode-copy` replays the copy-mip index reads for the five flagged mips in each of the 18 shipped banks (90) |
| `rating.py` | the `DAT` folder and the pages | prints the four rating lines ([how we rate](../docs/HOW_WE_RATE.md)); `--check` requires README and STATUS to carry them |
| `lol3_claimed_edges.py` | `LOL3.DAT`, `QWOD0.WSX` and `swod4.wsx`. `--counts` prints the two histograms; `--span LEVEL` prints the unidentified span as hex and names no field inside it | where the bytes named by the old QWOD0 and SWOD4 edges occur; `--decode` also checks the light-map sample high bytes |
| `lol3_name_hash.py` | `LOL3.DAT`, `LOL3.EXE` and the size-checked archives. `--list` prints the 40 music stems and their keys | 40 music stems, the 37/38 music join, and that stored C strings name 53 directory keys and not key `0x1D4F73DA` |
| `lol3_cache_seed.py` | shipped `DAT/cdcache.wsx`, `cdcache.hdr`, `LOL3.DAT`, the other programs and DLLs beside the game, and the game-written cache when it is present. Without `--check` it prints the 114 header bytes and the second directory | 51 copies of the 64,000-byte block; 6,344 of 63,360 pairs 640 apart match, more than at any other distance 1–2,000, and the block holds 209 values; that block's head is absent from those programs; row byte +0x17 has no code address; the witness's 8 occupied rows hold 0x67; the fill loop writes 64,000-byte passes from the locked surface |
| `lol3_pe_layout.py` | `LOL3.DAT` and `LOL3.EXE` beside `DAT`. Without `--check` it prints the PE header, section rows, debug payloads and final padding | both images: section rows, a zero header tail, stored section ranges, the three `LOL3.DAT` debug payloads and the zero padding reach each file's last byte ([PE images](../docs/formats/executable.md)) |
| `lol3_pht.py` | the four `.PHT` files, `LOL3.DAT` and `LOL3.EXE`. Without `--check` it prints each file's size and first 16 bytes | each file is a prefix of one 0x1010000-byte cycle, and that cycle equals the low bytes of the seed-1 generator at `LOL3.DAT` `0x51B655` with LF written as CR LF; lags 1 through 512 in the first 65,536 bytes each match under 1 percent; the two programs do not contain the names as ASCII or UTF-16 in any case; the cycle length is not a code immediate; the stored `$*.*` search is the save-game folder; the COFF timestamp field at LOL3.DAT+0xD0 is 0x37332C6E |
| `lol3_odf_companions.py` | `LOL3.DAT`, the 18 level ODFs and `GLOBAL.WSX`. `--list LEVEL` prints section-0 names, field-3 tags and which AI leaves join | 630 section-0 names and the skip past them; five AI files, 60 tags join all five; the zero-lookup arm |
| `lol3_save_header.py` | one save slot you name (a player save the game wrote, not a shipped file), plus the DAT folder | prints the named header fields, both directories, level-block section spans, and the other header bytes as hex with offsets: +0x94..+0x98, +0x3A8..+0x498, +0x5AC..+0x5B0, +0x5F8..+0x600, +0x648..+0x64C and the display-name bytes after the NUL. `--out` writes that report outside the game tree and this repository. `--check` prints `CHECK save_header: synthetic slot names version +0x30/+0x34: 38 310, both position groups, 61 global spans, 18 level spans and one 75-section block; unnamed header bytes are hex; LOL3.DAT+0x3BE0B is the version 310 compare and +0x3BE17 is the version 38 compare` |
| `lol3_save_selectors.py` | `LOL3.DAT` | `--check` reads the 61 global, 75 level and 90 nested dispatch addresses and verifies the 136 stored flags against the page. Install optional Capstone to decode and compare the selector and adjuster instructions or list their fields. |
| `lol3_save_writer.py` | the game-written slots in the `SAVEGAME` folder next to `DAT` (or a slot or folder you name), and the selector flags that `lol3_save_selectors.py` reads in `LOL3.DAT` | reads each slot into fields (header, both directories, level-block headers, the chunk frames of every section whose flag has bit 4) and writes it again in memory; the bytes must be identical. The stored LZO packets are copied, not compressed again, so this checks the container layout, not a compressor. With liblzo2 each packet must also decode to its expanded length. In our copy: 47 slots, 416 level blocks, 59,654 packets (yours differ). One header field (player x) is changed in memory: only its 4 bytes change and `lol3_save_header.py` reads the new value. SKIP without liblzo2 (the layout still runs and is printed) or without game-written slots. Writes nothing |
| `lol3_numbers.py` | `LOL3.DAT`, `GLOBAL.WSX` and the 18 level ODFs. Without `--check` it prints the page; `--out FILE` writes it | regenerates `docs/NUMBERS.md` (343 item definitions, 28 spell effect rows, the nine first-hit magnitudes and 334 field-3 creature definitions) and compares it byte for byte; prints `CHECK lol3_numbers: LoL3 tables match docs/NUMBERS.md` |

`lol3_cli.py` is a shared library for the options above, not a command.

## Reader parity

Each row is one current format page or one rules table. Older notes are not separate rows when the current page is linked here. The two comparison pages, `series-formats.md` and `engine-evolution.md`, describe all three games and are not rows.

Check means the tool's `--check` is in the `check_all.py` list above. Inspect is text the tool prints, or a picture it draws, from your own files. A row marked **gap** has no such output yet. Listing commands write nothing. A line taken from the game-written cache can differ when that cache differs. Tools still write only where an output path is given, and they do not copy game bytes into this repository.

| Documented format or rules table | Reader | Check | Inspect |
|---|---|---|---|
| [WSX directory](../docs/formats/wsx.md#layout) | `extract_wsx_entries.py` | yes | text. `python3 tools/extract_wsx_entries.py --data DAT --list --stems QWOD0` writes nothing and prints `QWOD0.WSX`, `count 4 data_base 0x36`, `key 0xe128e119 offset 0x36 size 6871261`. `--out DIR --manifest FILE` writes a manifest of key, offset, size and SHA-1 per entry (`--max-blob-write 0` skips the entry blobs); both paths must be outside this repository. |
| [Shipped `cdcache.wsx`](../docs/formats/wsx.md#cdcachewsx) and `cdcache.hdr` | `lol3_cache_seed.py` | yes | text. Without `--check`: `cdcache.hdr matches the first 114 bytes`, `shipped 3264114 bytes`, `header 114 bytes`, `dword +0x72 0xd0bcd8be`, `51 copies of 64000 bytes`, then the 114 header bytes with no field names, beginning `+0x0: 09 00 7f 95 23 03 e6 eb 97 be d1 03 00 00 0d 00`. What these bytes mean and what reads them is unknown ([Q1](../docs/OPEN_QUESTIONS.md)). These bytes stay outside the files-read count. When the game-written cache is present the same command prints its second directory; those row offsets can differ. |
| [Game-written cache records](../docs/formats/textures.md#the-cache-file) | `lol3_texture_spans.py`, `lol3_texture_palettes.py` | yes; both skip when that cache is absent | text. `--list N` prints span offset, flags and size. Without `--check`, palettes print every arm-3 join as one JSON object. |
| [Texture cache palette sources](../docs/lol3-texture-palette-sources.md) | `lol3_texture_palettes.py` | yes; skips when the cache is absent | text. `python3 tools/lol3_texture_palettes.py --data DAT` prints one JSON object per texture, the first is `{"texture_offset":1222718,"bank_offset":1078,"descriptor_offset":1083188,"descriptor_index":6,"mip":0,"palette_arm":3,"palette_key":5,"palette_offset":10410903}` (offsets in the game-written cache, which can differ). |
| [Cache record to PNG](../docs/lol3-texture-bake.md#cache-record-to-png) | `lol3_texture_png.py` | yes; skips when the cache is absent. `--decode-slices` is not part of `check_all` | one PNG of game pixels, written only to `--out`. The repository does not keep that picture. |
| [SMD slice frames](../docs/lol3-texture-bake.md#smd-slice-frame-references) | `lol3_texture_png.py` | yes; `--list-slices` and `--decode-slices` are not what `check_all` runs | text. `python3 tools/lol3_texture_png.py --data DAT --list-slices` writes nothing. On the cache present for the check it prints `rqwoman.smd slices 296` and `slice 0 +0x4b0`. Another cache can differ. |
| [PHT files](../docs/formats/pht.md) | `lol3_pht.py` | yes | text. Without `--check`, each file's size and first 16 bytes. `CYGNUS.PHT 112519732 bytes +0: 29 23 be 84 e1 6c d6 ae 52 90 49 f1 f1 bb e9 eb`. What the bytes mean and what reads them is unknown ([Q1](../docs/OPEN_QUESTIONS.md)). These four files stay outside the files-read count. |
| [LMF directory](../docs/formats/lmf.md#layout) | `walk_lmf_leaves.py` | yes. `--decode` is optional and is not what `check_all` runs | text. `python3 tools/walk_lmf_leaves.py --data DAT --stem QWOD0` prints `QWOD0.WSX: 657784 bytes, directory rows 5364, groups 49` and the header words. A loose `.LMF` file can still be printed as JSON: the counts and the first 8 groups. |
| [Native Light Map reader](../docs/lol3-lmf-reader.md) (member flag, vertex normals, size rule, +0x0C–+0x13 words) | `walk_lmf_leaves.py` | yes; `--decode` is optional and is not what `check_all` runs | text. `python3 tools/walk_lmf_leaves.py --data DAT --check --decode` prints one CHECK line with the member counts on that page: 131,217 members with bit 0 set and unit normals, 293,071 with one repeated vector, and the 610,325 +0x0C–+0x13 words found in their own grids. The size rule (+4 and +6 rounded up to a power of two) is not printed. |
| [MAP header, vertices and surfaces](../docs/formats/map-odf.md#map-sections) | `lol3_level_report.py`, `lol3_level_schematic.py` | yes, both | text: one sheet per level (`--out`), with the header fields. Picture: surface edges, hollow waypoint squares, path runs and the rows of all five placement tables, numbered from 1, with a legend ([QWOD0 schematic](../docs/images/qwod0-schematic.svg)). |
| [Waypoints, paths and name slots](../docs/lol3-map-odf-readers.md#map-section-0) | `lol3_map_spans.py`, `lol3_level_schematic.py` | yes, both | text and picture. `python3 tools/lol3_map_spans.py --data DAT --list QWOD0` prints `QWOD0 waypoints 1 paths 0` and `waypoint 1: x 11063 z -2943 surface 0xe7 +6 0x2 +7 0x4`. Each name slot and path label is hex and is not decoded. The schematic draws the same marks. |
| [Section 1 rows and surface fields](../docs/lol3-map-odf-readers.md#map-sections-1-and-2) | `lol3_level_report.py`, `lol3_map_spans.py` | yes, both | text. `python3 tools/lol3_map_spans.py --data DAT --rows QWOD0` prints `QWOD0 section-1 rows 2368` and `row 1: +0 0xf3 +2 0xd6 +3 0x0 +4 0x80 +5 0x4 +5&0x1f 0x4 +6 0x8 +7 0x0`. What bytes +5 and +6 mean stays open on that page. |
| [Shared block before the vertices](../docs/lol3-map-odf-readers.md#shared-block-before-the-vertices) | `lol3_claimed_edges.py` | yes | text. `python3 tools/lol3_claimed_edges.py --data DAT --span QWOD0` prints `span +0x244..+0x2f2c: 11496 bytes` and then those bytes as hex. The listing names no field inside the span. The check line states `18 identical 0x2CE8-byte MAP blocks fit 2,873 four-byte rows; all 23 native post-header seeks (22 direct, 1 nested) start at the vertices or later`. |
| [ODF names, AI files and placements](../docs/lol3-map-odf-readers.md#odf-header-and-primary-tables) | `lol3_odf_companions.py` | yes | text. `python3 tools/lol3_odf_companions.py --data DAT --list QWOD0` prints `QWOD0 section-0 names 17`, `name 1: Floor28` and `ai SPIDER: stat.csv, goals.csv, actions.csv, effector.csv, spells.csv`. |
| [Level texture banks (`.TE_`)](../docs/formats/textures.md#compressed-level-wrapper) | `lol3_texture_archive.py` | yes, without `--decode` | text. One chunk-count line per level when not checking. `python3 tools/lol3_texture_archive.py --data DAT --list QWOD0 --decode` prints `QWOD0 descriptors 421` and `descriptor 1: +0x1081a2 key 0x0 arm 0`. |
| [VQA movies](../docs/formats/vqa.md) | `lol3_media_check.py` | yes | text. Without `--check`, one line per movie and the chunk-type totals. `python3 tools/lol3_media_check.py --data DAT --movie mvolc` prints `movies3.wsx+0x2A outtakes\mvolc.vqa chunks 504` and `VQHD +0x36 size 42`. |
| [Music streams](../docs/formats/audio.md#music-streams) | `lol3_media_check.py`, `lol3_name_hash.py` | yes, both | text. `--tracks` prints `MUSIC1.WSX+0x36 size 4157978 key BD4CB6E0 tag 0x55 channels 2 rate 44100 align 1 bits 0 stem uewoods0`. The unnamed track prints `music4.wsx+0x11FD49A size 6530290 key 1D4F73DA tag 0x55 channels 2 rate 44100 align 1 bits 0 stem absent`. `--list` prints `stems 40` and `stem 9: uhfrozen key 0x1d4f90da`. |
| [Level samples](../docs/formats/audio.md#level-sample-data) | `lol3_media_check.py`, `lol3_level_report.py` | yes, both | text. `--samples QWOD0` prints `QWOD0S.WSX samples 26` and `+0x64886 size 25224 key C78AB18C tag 0x11 channels 1 rate 22050 align 512 bits 4`. |
| [Opcode sizes and effects](../docs/lol3-script-opcodes.md) | `lol3_script_framing.py`, `lol3_script_notes.py`, `lol3_script_browser.py` | yes, all three | text: one level grouped by opcode, each line the page's meaning. Framing prints sizes and counts across all 18 maps. Notes are stream and event-pool tables; full listings stay outside the repository. |
| [Opcode subtables](../docs/lol3-script-opcodes.md#per-class-effects-of-the-indirect-commands) (class, creature `0x0D`, effect `0x0F`, `0x1C`, `0xC4`, arrays) | `lol3_script_framing.py` | yes. The check compares the seven (opcode, selector) counts and prints only their total | text. `--subcommands` counts the object stream the opcode page tabulates: `opcode 0x0D selector 2: 5213`, `opcode 0x0D selector 3: 56`, `subcommand 2: 3145`, `effect opcode 0x0F actions 219`, `action 59: 60`, `opcode 0x1C records 217 u16+4 bit0 27 bit1 217`, `opcode 0xC4 records 453 speed +7 zero 2`, `opcode 0xC4 byte+6 bit 0: 46`. |
| [Event pools, predicates and timers](../docs/lol3-script-events.md) | `lol3_script_notes.py` | yes | text. `--summary` writes pool, kind and one predicate count (the copies in `docs/levels/notes/`). `python3 tools/lol3_script_notes.py --data DAT --timers QWOD0` prints `object kind 2 timer expires: 2` and `region kind 2 timer expires: 0`: the timer rows are counted as kind 2 (matcher `0x4F1AD0`); their flags, reload and countdown values are not printed. |
| [Object dispatch](../docs/lol3-object-dispatch.md) | `lol3_script_framing.py` | no separate check. Framing's check does not print the slots | text. `--dispatch` prints `object opcode slots 28` and `slot 1 opcode 0x01: 0x447f31`. **gap:** the length of the region byte-index table is not printed. Settle it from the bound that `0x4E59A0` uses when it indexes `0x4E5AB4`. |
| [Item definitions and handlers](../docs/lol3-item-dispatch.md#definition-directory) | `lol3_combat_census.py` | yes | text. Without `--check`, handler index, how many definitions use it, and the handler address. `--items` prints `regular definitions 258` and `definition 0: +0x73 0x1 +0x3f 0x44 +0x4b 0x0 +0x4f 0x200 +0x7d 0x3`. |
| [Spell tables](../docs/lol3-spell-dispatch.md#definition-tables) | `lol3_native_checks.py` | yes. `--spells` is not what `check_all` runs | text. `--spells` prints `spell rows 28`, `row 1: +0x18 0x375133ee +0x2e 0x8`, `auxiliary: 00 00 00 00 00 00 00 00`, `special definition costs 85` and `definition 77: +0x73 0x50 +0x5b 50`. |
| [Dialogue and message tables](../docs/lol3-dialogue-dispatch.md) (`.TRR`) | `lol3_media_check.py` | yes. `--trr` is not what `check_all` runs | text. `--trr qevent.trr` prints `qevent.trr count 67 directory 544 bytes` and `id 0 boundary 0x21c`. Payload bytes are not printed. |
| [Combat mitigation and hit modes](../docs/lol3-combat-dispatch.md) | `lol3_combat_census.py` | yes | text. Selector counts, plus the item-handler lines above. `--mitigation` prints `mitigation records 334 distinct 57` and `selectors 0x0 0x0 0x0 0x0 masks 0x0/0x0 0x0/0x0 0x0/0x0 0x0/0x0 rows 103`. `--modes` prints `behavior 0: 0x4b4d7e`. |
| [Save slot header and directories](../docs/lol3-native-saves.md#slot-header-and-stream) | `lol3_save_header.py` | yes | text: display name, version +0x30/+0x34: 38 310, stamps, preview, current level, both position groups, 61 global spans and 18 level spans. Unnamed header bytes are hex with offsets. |
| [Level blocks and `.LSV`](../docs/lol3-native-saves.md#level-blocks-and-chunking) | `lol3_save_header.py` | yes | text: a block of at least 0x34C bytes lists its size, 75 relative starts, 75 expanded lengths and each stored span. A shorter block is named and is not read as a header. Payloads are not expanded. |
| [Selector payloads](../docs/lol3-native-saves.md#selector-payloads) | `lol3_save_selectors.py` | yes | text: one row per global and level selector, with the live address, byte count, unit, flags, adjuster and the dwords passed to the pointer helper. |
| [Name to directory key](../docs/lol3-wsx-reader.md#resource-name-key) | `lol3_name_hash.py`; level sheets print four level keys; `extract_wsx_entries.py --list` prints any archive's keys | yes | text. `--list` prints `stems 40`, `stem 9: uhfrozen key 0x1d4f90da` and `stem 11: uhfroze2 key 0x1d4f74da`. An archive's keys are the WSX listing above. |
| Program witnesses in `LOL3.DAT` ([pickup](../docs/lol3-item-dispatch.md), [copy mips](../docs/lol3-texture-bake.md), [spell counter](../docs/lol3-spell-dispatch.md)) | `lol3_native_checks.py` | yes. `check_all` adds `--decode-copy` when liblzo2 is available | text. `--list` prints `world item +0x68 0x4d83a0`, `call 0x4d83ac targets 0x42ef50` and `handler 112 0x4a6120`. |
| [QWOD0 and SWOD4 byte-pattern counts](../docs/lol3-semantic-phase.md) | `lol3_claimed_edges.py` | yes | text. `--counts` prints `QWOD0 C5 A5: texture 195, MAP 2, light map 1, ODF 0` and `SWOD4 surface +4: 0x0 on 2393, 0x2 on 14, 0x6 on 29, 0xb on 0`. No picture: drawings of those labels were removed because they match no field the readers use. |

## `modkit.py`

The mod kit changes game text and numbers in copies; your game folder is only read. Run it from any folder and put quotes around paths with spaces:

```bash
python3 tools/modkit.py unpack "/path/to/LoL3" "my mod work"
# change the files in "my mod work/edits", then:
python3 tools/modkit.py build "/path/to/LoL3" "my mod work" "my mod output"
python3 tools/modkit.py verify "/path/to/LoL3" "my mod work" "my mod output"
```

- `modkit.py` names the LoL3 tables; `modkit_core.py`, the same file in the three repositories, does the unpack, build, verify and folder checks.
- The game folder is the LoL3 game folder holding `LOL3.DAT` and `DAT`, or its `DAT` folder (then the folder above it is read too).
- `unpack` creates the work folder with `manifest.json`, a `README.txt` and one JSON file per table in `edits/`: the TRR text tables (`PROMPT.TRR` and the 26 tables of `locallng.wsx`, both the copy beside `DAT` and the one in it; change both), the item fields `special_cast_cost` (meaningful for items with flag 2) and `step_input` and the spell field `frame_count` of `GLOBAL.WSX`, and the creature fields `health_cap` and `attack_input` of the 18 level archives ([numbers](../docs/NUMBERS.md)). Change only `"value"`; keep the number of rows, the field names and codes such as `\r` or `\u0002`.
- `build` creates the output folder and writes every unpacked file into it, changed or not (about 520 MB), and names the changed files. `verify` reads the output back with the archive and table readers and checks it against the work folder. Copy the changed files over a backup copy of your game to try them.
- Refused, with one line saying why: a work or output folder that already exists, lies inside the game folder, inside a folder holding WSX archives or `LOL3.DAT`, or inside this repository, and an output inside the work folder.
- An unchanged work folder rebuilds byte for byte: 22 files (`PROMPT.TRR` and 21 WSX archives) from 73 entries. `--check` does unpack, build and verify in a temporary folder (`--data` or `$LOL3_DAT`) and is part of `check_all.py`:

```
$ python3 tools/modkit.py --check
CHECK modkit: 22 archives or loose tables rebuilt byte-identically from 73 unpacked entries; outputs in the game, work, archive and repository folders refused
```

## `patch.py`

Makes, applies and undoes small patches for your own copy of the game ([format, rules and limits](../docs/formats/patch.md)). `patch.py` is the same file in the three repositories. Your game folder is only read. Run it from any folder and put quotes around paths with spaces:

```bash
python3 tools/patch.py make --data "/path/to/LoL3" "my mod output" --title "Dearer cast" --out "dearer cast.json"
python3 tools/patch.py apply --data "/path/to/LoL3 test copy" "dearer cast.json" --out "patched files"
python3 tools/patch.py apply --data "/path/to/LoL3 test copy" "patched files/undo.json" --out "restored files"
```

- `--data` is the game folder holding `LOL3.DAT` and `DAT`; given the `DAT` folder, the tool reads the folder above it (default: `$LOL3_DAT`). It may also be given as the first path, as `modkit.py` takes it.
- `make` writes a new patch file from the differences between the game folder and a folder of changed files, such as the output of `modkit.py build`. `--title` is required; `--description` is optional; `--kind data` or `--kind program` is found from the changed files when left out.
- `apply` checks each replaced span's SHA-256, the program's whole-file SHA-256 for a program patch and the undo before it writes anything, then writes the patched files and `undo.json` into the new `--out` folder. Copy the files except `undo.json`, with their folders, into a copy of the game. Applying `undo.json` to that copy gives the original bytes back. Keep the undo file private because it holds those bytes.
- Refused, with one sentence saying why: a missing or unchanged changed folder, a patch for another game, edition or version, a patch already applied, a patch over the size limits (data: 256 bytes per change and 4,096 per patch; program: 16 and 256), an output that already exists, whose folder does not exist, or that lies inside the game folder, a folder holding game archives or this repository.
- Tests on synthetic files: `tests/test_patch.py` (the same file in the three repositories).

```
$ python3 tools/patch.py make --data "/path/to/LoL3" "my mod output" --title "Dearer cast" --out "dearer cast.json"
make: data patch with 1 change in 1 file (DAT/GLOBAL.WSX) written to /path/to/dearer cast.json
Data patches are for the original Windows game.
```

## `save_edit.py`

`save_page.py` renders the offline page produced by `lol.py save page`. See [the save guide](../docs/EDITED_SAVES.md#see-the-fields-in-an-offline-page).

Writes a copy of an original save with one field changed; the save itself is only read. Each run prints the old and the new value and one line saying whether the game has been shown to load such an edit (CONFIRMED) or not yet (UNCONFIRMED). Fields and their status: [cookbook](../docs/COOKBOOK.md#change-a-saved-game-a-copy).

```
$ python3 tools/save_edit.py set '/path/to/LoL3/SAVEGAME/$1234___.000' heading 0x4000 --out "my edited save.000"
set: heading OLD -> 0x4000; copy written to /path/to/my edited save.000; the original save was only read
UNCONFIRMED: no edited copy of this field has been loaded by the game yet; keep a backup of your saves
```

- Fields: `name` (the display name), `heading` (0–65535) and `position-from` (another save of the same level), for version 38/310 slots; all three are UNCONFIRMED. Save names begin with `$`; on Linux and macOS put them in single quotes. Numbers can be decimal or start with `0x`.
- Refused, with one sentence saying why: a missing or damaged save, a value out of range, a name that is not plain ASCII, a donor save from another level or version, and an output that already exists, lies in the save's own folder, in the game folder or in this repository. Tests on synthetic slots: `tests/test_save_edit.py`.

## Command-line conventions

Set `LOL3_DAT` or pass `--data` for the original game's DAT directory. Run `--help` for the tool's inputs and modes. Use `--check` for the available read-only validation and `--out` to write a result to a path you choose. Read-only listings print to stdout. `check_all.py` runs the whole suite by default. `doc_links.py` and `repo_guard.py` use repository files and need no game data.

| Difference | Why it remains |
|---|---|
| `LOL3_DAT`, where LoL1 uses `LOL1_DATA` and LoL2 uses `LOL2_DAT` | Each name follows the game's own folder: LoL1 keeps its files in `DATA`, LoL2 and LoL3 in `DAT`. Shells and scripts already set these names. |
| A positional save or LMF file | A single player slot or extracted light map is an explicit input. Corpus checks use DAT to find their other witnesses. |
| `--cache FILE` | This supplies the texture cache the game wrote beside DAT. The three texture cache checks can use an archived cache stored elsewhere. [Cache recipe](../docs/COOKBOOK.md#check-the-texture-cache) |
| `--summary` for script notes and `--manifest` for WSX export | These select the small notes and a secondary directory listing, respectively. `--out` selects the extracted or full listing output. |
| `--game-dat` in the WSX tool and `-o` in the LMF tool | Old spellings are kept as aliases and shown in `--help`, so earlier scripts that call the tools keep working. `--game-dat` is the same as `--data`, `-o` the same as `--out`. |

## Documentation index

`doc_index.py` reads the repository's Markdown pages and generates [docs/index.json](../docs/index.json).
Its `pages` records include the title, original path, question IDs and cited tool source paths.
`answers` uses the Page or Where column of [Open questions](../docs/OPEN_QUESTIONS.md).
`question_references` records other references to the same IDs. The top-level `questions`
object preserves the published state and lists each question's answer pages. Tool citations
include command examples. The index covers the Markdown files shipped in the repository,
including the root pages, example and evidence notes, and issue templates. In a git checkout
it reads only tracked pages, so local untracked notes do not change the check.

```bash
python3 tools/doc_index.py --out docs/index.json
python3 tools/doc_index.py --check
```

The check also runs in `check_all.py` and GitHub Actions. It needs no game data.

`doc_format_offsets.py` checks six format-page offsets against the readers that decode those fields, using small synthetic files. It runs in `check_all.py` and needs no game data. [Check audit](../docs/CHECK_AUDIT.md)

`check_all.py --quick` skips the LMF member walk, LZO writer, name-hash scan and WSX writer. It lists each skip and reports the total elapsed time for the checks it ran.
