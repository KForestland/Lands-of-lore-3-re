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
| `check_all.py` | all checks below | prints each line, then `ALL 22 CHECKS PASSED`, or `19 CHECKS PASSED, 3 SKIPPED` when the game-written cache is missing |
| `doc_links.py` | `README.md`, `tools/README.md`, `CONTRIBUTING.md`, `docs/`, and `examples/`/`evidence/` when present | checks links and anchors only (runs no command): every relative link, image link, `<a href>` and GitHub heading anchor resolves; fenced examples are skipped |
| `repo_guard.py` | the repository | no game files, media, stray images, machine paths, words from the optional local word list; with `--release` also foreign commit identities |
| `extract_wsx_entries.py` | `DAT/*.WSX` | parses every WSX and writes nothing (51/52; `cdcache.wsx` is open question Q1) |
| `walk_lmf_leaves.py` | the LMF entries inside the WSX files | checks directory coverage for all 18. Optional `--decode` with liblzo2 checks every member header, counts the bit-0 vertex normals and re-counts the +0x0C–+0x13 header words against each member's grid. |
| `lol3_level_schematic.py` | a level archive's MAP entry | overhead SVG of surface edges, waypoint squares, path runs and numbered placement dots, with a legend. Give a level stem and `--out` (inside the repository only `docs/images/` or `examples/`); `--check` regenerates `docs/images/qwod0-schematic.svg` and compares it byte for byte. For QWOD0 it prints `QWOD0.WSX+0x72e28b: 1308 vertices, 1430 surfaces, waypoints 1, paths 0, type 3 472, type 16 53, creature 1, item 6`. |
| `lol3_level_report.py` | the 18 level archives and their sound sidecars | with `--out DIR` writes the sheets (the repository's are in `docs/levels/`); checks the four named entries per level, the MAP section-1 rule, the surface and waypoint joins, that every sidecar entry is WAVE, and that the scripts are 54,940 object records and 4,040 region records with 25 movie indexes and no music or other-level name |
| `lol3_texture_spans.py` | the game-written `cdcache.wsx` in the game folder | every row-span texture record consumes exactly its height rows inside its width (854 of 854 in our game-written cache; yours may differ); SKIP if the cache is missing |
| `lol3_texture_palettes.py` | the same cache | every texture joins one palette source through selector arm 3; prints offsets only; SKIP if the cache is missing |
| `lol3_texture_png.py` | the same cache | bakes one indexed record with `--offset` and writes a PNG only to `--out`. `--check` decodes all supported records and reports the other classes. A missing cache reports SKIP. Add `--decode-slices` to `--check` to validate the original SMD runs with liblzo2 (`check_all` runs it without `--decode-slices`) |
| `lol3_script_framing.py` | `LOL3.DAT` and the 18 MAP entries | all script streams frame exactly with the native size table; counts only |
| `lol3_texture_archive.py` | the 18 `.TE_` entries in the level archives | every LZO1X-wrapped bank frames (465 chunks); with `--decode` (liblzo2) expands each, checks the palette joins (692 / 4,635 / 44,357 = 49,684 descriptors) and compares the 4 cached copies, SKIPPED if the cache is missing; counts only (`check_all` runs it without `--decode`) |
| `lol3_script_notes.py` | `LOL3.DAT` and the 18 MAP entries | `--check` re-derives the tracked summaries; `--out DIR` (outside the repository) writes the full per-record listings for your own copy; `--summary DIR` writes the summaries |
| `lol3_media_check.py` | the `MOVIES1..4`, `MUSIC1..4` and level sound archives, and `LOL3.DAT` | the 19 named movies and their frame index, the 38 music tracks and 6,696 level sounds; counts only |
| `lol3_map_spans.py` | `LOL3.DAT` and the 18 MAP entries | waypoint byte +6, the 2,330/39/15 name slots, the 36 path labels, the 1,784 bytes before field 16 and the 167,942 section-1 rows |
| `lol3_combat_census.py` | `LOL3.DAT`, the 18 level ODFs and `GLOBAL.WSX` | the 334 creature mitigation records (57 distinct, selector counts) and the 258 regular item definitions on 114 handler indexes |
| `lol3_native_checks.py` | `LOL3.DAT` (and with `--decode-copy` the shipped archives, needs liblzo2) | the world-pickup and copy-dispatch anchors; `--decode-copy` replays the 20 copy-mip index reads |
| `rating.py` | the `DAT` folder and the pages | prints the four rating lines ([how we rate](../docs/HOW_WE_RATE.md)); `--check` requires README and STATUS to carry them |
| `lol3_claimed_edges.py` | `LOL3.DAT`, `QWOD0.WSX` and `swod4.wsx` | where the bytes named by the old QWOD0 and SWOD4 edges occur; `--decode` also checks the light-map sample high bytes |
| `lol3_name_hash.py` | `LOL3.DAT`, `LOL3.EXE` and the size-checked archives | 40 music stems, the 37/38 music join, and that stored C strings name 53 directory keys and not key `0x1D4F73DA` |
| `lol3_cache_seed.py` | shipped `DAT/cdcache.wsx`, `cdcache.hdr`, `LOL3.DAT`, and the game-written cache when it is present | 51 copies of the 64,000-byte block; row byte +0x17 has no code address; the witness's 8 occupied rows hold 0x67 |
| `lol3_pht.py` | the four `.PHT` files, `LOL3.DAT` and `LOL3.EXE` | each file is a prefix of one 0x1010000-byte cycle; the two programs do not contain the names |
| `lol3_odf_companions.py` | `LOL3.DAT`, the 18 level ODFs and `GLOBAL.WSX` | 630 section-0 names and the skip past them; five AI files, 60 tags join all five; the zero-lookup arm |
| `lol3_save_header.py` | one save slot you name (a player save, not a game file) | prints the preview, 61 global and 18 level offsets and lengths as JSON; writes nothing; no `--check` |

`lol3_cli.py` is a shared library for the options above, not a command.

## Reader parity

Each row is one current format page or one rules table. Older notes are not separate rows when the current page is linked here. The two comparison pages, `series-formats.md` and `engine-evolution.md`, describe all three games and are not rows.

Check means the tool's `--check` is in the `check_all.py` list above. Inspect is text the tool prints, or a picture it draws, from your own files. A row marked **gap** has no such output yet. Tools still write only where an output path is given, and they do not copy game bytes into this repository.

| Documented format or rules table | Reader | Check | Inspect |
|---|---|---|---|
| [WSX directory](../docs/formats/wsx.md#layout) | `extract_wsx_entries.py` | yes | **gap.** `--check` counts archives. Any other run writes the entry blobs and one `OK` line; it does not print key, offset and size. |
| [Shipped `cdcache.wsx`](../docs/formats/wsx.md#cdcachewsx) and `cdcache.hdr` | `lol3_cache_seed.py` | yes | **gap.** The check line states the repeated block. There is no header listing. These bytes stay outside the files-read count. |
| [Game-written cache records](../docs/formats/textures.md#the-cache-file) | `lol3_texture_spans.py`, `lol3_texture_palettes.py` | yes; both skip when that cache is absent | text. `--list N` prints span offset, flags and size. Without `--check`, palettes print every arm-3 join as one JSON object. |
| [Cache record to PNG](../docs/lol3-texture-bake.md#cache-record-to-png) | `lol3_texture_png.py` | yes; skips when the cache is absent. `--decode-slices` is not part of `check_all` | one PNG of game pixels, written only to `--out`. The repository does not keep that picture. |
| [SMD slice frames](../docs/lol3-texture-bake.md#smd-slice-frame-references) | `lol3_texture_png.py --decode-slices` | optional flag only | **gap.** The flag checks frames. It does not list one slice directory. |
| [PHT files](../docs/formats/pht.md) | `lol3_pht.py` | yes | **gap.** Check line only. These four files stay outside the files-read count. |
| [LMF directory](../docs/formats/lmf.md#layout) | `walk_lmf_leaves.py` | yes. `--decode` is optional and is not what `check_all` runs | JSON of groups for one loose `.LMF` file, on standard output or `-o`. **gap:** a level archive in the DAT folder cannot be printed until the entry is peeled out. |
| [MAP header, vertices and surfaces](../docs/formats/map-odf.md#map-sections) | `lol3_level_report.py`, `lol3_level_schematic.py` | yes, both | text: one sheet per level (`--out`), with the header fields. Picture: surface edges, waypoint squares, path runs and numbered placement dots, with a legend ([QWOD0 schematic](../docs/images/qwod0-schematic.svg)). |
| [Waypoints, paths and name slots](../docs/lol3-map-odf-readers.md#map-section-0) | `lol3_map_spans.py`, `lol3_level_schematic.py` | yes, both | picture: the schematic draws each waypoint and each path. **gap:** no text listing of the name slots or of each row's bytes. |
| [Section 1 rows and surface fields](../docs/lol3-map-odf-readers.md#map-sections-1-and-2) | `lol3_level_report.py`, `lol3_map_spans.py` | yes, both | sheets name the surface count. **gap:** section-1 rows are not listed. |
| [Shared block before the vertices](../docs/lol3-map-odf-readers.md#shared-block-before-the-vertices) | `lol3_claimed_edges.py` | yes | **gap.** The check counts one repeated pattern. There is no hex listing. The retail loader skips this span, so a listing must not name fields inside it. |
| [ODF names, AI files and placements](../docs/lol3-map-odf-readers.md#odf-header-and-primary-tables) | `lol3_odf_companions.py` | yes | **gap.** Check line only. Sheets give header sizes, not names or placement rows. |
| [Level texture banks (`.TE_`)](../docs/formats/textures.md#compressed-level-wrapper) | `lol3_texture_archive.py` | yes, without `--decode` | text: one chunk-count line per level when not checking. **gap:** no descriptor listing. Shared `.TEX` banks are counted only when `--decode` is passed. |
| [VQA movies](../docs/formats/vqa.md) | `lol3_media_check.py` | yes | text, only when not checking: one line per movie (offset, key, stem, frame count) and chunk-type totals. **gap:** no chunk listing inside one movie. |
| [Music streams](../docs/formats/audio.md#music-streams) | `lol3_media_check.py`, `lol3_name_hash.py` | yes, both | **gap.** Both checks are counts. No per-track offset, format tag or stored name. |
| [Level samples](../docs/formats/audio.md#level-sample-data) | `lol3_media_check.py`, `lol3_level_report.py` | yes, both | a sheet gives the family count for one sidecar. **gap:** no per-entry offset list. |
| [Opcode sizes and effects](../docs/lol3-script-opcodes.md) | `lol3_script_framing.py`, `lol3_script_notes.py` | yes, both | text: each opcode's size and how often it occurs, across all 18 maps, when framing is not checking. Summaries are stream and event-pool tables. Full listings are one line per record and are written only outside the repository. **gap:** no summary for one level that groups commands by opcode and prints the one-line meaning. |
| [Opcode subtables](../docs/lol3-script-opcodes.md#per-class-effects-of-the-indirect-commands) (class, creature `0x0D`, effect `0x0F`, `0x1C`, `0xC4`, arrays) | none | framing's check compares three selector totals and does not print them | **gap.** |
| [Event pools, predicates and timers](../docs/lol3-script-events.md) | `lol3_script_notes.py` | yes | text: `--summary` writes pool, kind and one predicate count (the copies in `docs/levels/notes/`). **gap:** timers are not in that summary. |
| [Object dispatch](../docs/lol3-object-dispatch.md) | none beyond the full script listing | no separate check | **gap.** |
| [Item definitions and handlers](../docs/lol3-item-dispatch.md#definition-directory) | `lol3_combat_census.py` | yes | text, when not checking: handler index, how many definitions use it, and the handler address. **gap:** definition fields are not printed. |
| [Spell tables](../docs/lol3-spell-dispatch.md#definition-tables) | `lol3_native_checks.py` (counter anchors only) | yes | **gap.** The check line does not list definitions or costs. |
| [Dialogue and message tables](../docs/lol3-dialogue-dispatch.md) (`.TRR`) | none. [Quick reference](../docs/QUICK_REFERENCE.md) runs one inline read of a single count | no | **gap.** No directory tool. A listing must not print payload text. |
| [Combat mitigation and hit modes](../docs/lol3-combat-dispatch.md) | `lol3_combat_census.py` | yes | text: selector counts, plus the item-handler lines above. **gap:** mitigation fields and hit-mode rows are not printed. |
| [Save slot header and directories](../docs/lol3-native-saves.md#slot-header-and-stream) | `lol3_save_header.py` | **gap.** No `--check`, and `check_all` does not run it. It takes a positional file, not `--data` | JSON of the preview span, 61 global spans and 18 level spans. **gap:** display name, version, stamps, the two position groups and the current level are not printed, and unnamed header bytes are not shown as hex with offsets. |
| [Level blocks and `.LSV`](../docs/lol3-native-saves.md#level-blocks-and-chunking) | the same header tool, offsets only | no | **gap.** A block's 75 section starts and lengths are not printed. |
| [Name to directory key](../docs/lol3-wsx-reader.md#resource-name-key) | `lol3_name_hash.py`; level sheets print four level keys | yes | sheets cover one level's four names. **gap:** no listing of music stems, or of an arbitrary archive. |
| Program witnesses in `LOL3.DAT` (pickup, copy mips, spell counter) | `lol3_native_checks.py` | yes. `--decode-copy` is optional and is not what `check_all` runs | **gap.** Check line only. |
| [QWOD0 and SWOD4 byte-pattern counts](../docs/lol3-semantic-phase.md) | `lol3_claimed_edges.py` | yes | **gap.** Check line only. No picture: drawings of those labels were removed because they match no field the readers use. |
