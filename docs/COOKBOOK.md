# Cookbook

Each recipe uses the tools on your own copy of the original game. Run them from the clone after:

```bash
export LOL3_DAT=/path/to/your/LoL3/DAT
```

The schematic goes outside the clone. A save slot is a game-written player save: a file the game wrote when you saved.

## Write a full report

```bash
python3 tools/full_report.py --data "$LOL3_DAT" --out ../lol3-out/report
```

The tool writes `inventory.tsv` with the files in `DAT`, their sizes, the reader used and its result. For an archive, `complete` describes its directory and payload spans. The report labels the shipped cache seed and PHT files as repeated blocks when the byte-pattern checks pass. Open `levels/README.md` for the level sheets. `text-counts.tsv` gives one count per table from the four event and dialogue TRRs in `LOCALLNG.WSX`.

Choose an output folder outside the game and clone. Use a fresh folder for each report.

## Draw a level schematic

```bash
mkdir -p ../lol3-out
python3 tools/lol3_level_schematic.py QWOD0 --out ../lol3-out/qwod0.svg
```

```text
QWOD0.WSX+0x72e28b: 1308 vertices, 1430 surfaces, waypoints 1, paths 0, type 3 472, type 16 53, creature 1, mover (type 32) 0, item 6; numbers are 1-based table rows; 327 overlapping numbers left out
```

The SVG is an overhead line drawing: surface edges, one hollow waypoint square, and numbered placement dots (type 3, type 16, creature, mover, item); 327 overlapping numbers are left out. No game pixels.

## Check the texture cache

The original game writes a texture cache named `cdcache.wsx` in its game folder, beside `DAT`, when it first runs. To get one, start the game once from your installation; the checks then find the file there. The 3 MB `DAT/cdcache.wsx` the game ships is only the seed and holds no texture records. Without the game-written file the other 25 checks still run. [Cache and row spans](formats/textures.md#the-cache-file)

```bash
python3 tools/check_all.py
# If your matching game-written cache is stored elsewhere:
python3 tools/check_all.py --cache /path/to/game-written/cdcache.wsx
```

The following checks each print a single `SKIP` line when the game-written cache is absent. Run them individually with `--check` and, if needed, the same `--cache` option.

| Tool | What it checks |
|---|---|
| `lol3_texture_spans.py` | For flags 0x028E and 0x828E, each payload consumes exactly the stored number of rows, every row fits within the width, and the final row ends at the payload boundary. [Row spans](formats/textures.md) |
| `lol3_texture_palettes.py` | Each of those span records is named by exactly one texture descriptor whose palette arm is 3 and whose palette key is in range, and, as in the documented cache, the four texture banks hold 191, 243, 395 and 25 of them. [Palette source](formats/textures.md) |
| `lol3_texture_png.py` | The full cache directory joins record positions and arm-3 palettes. It decodes supported raw and span formats, validates SMD references, checks the remaining unconfirmed flags against the measured full-width row layout, and counts them. `--decode-slices` also checks original SMD runs with liblzo2. [Cache-to-PNG checks](lol3-texture-bake.md#cache-record-to-png) |

## Read your position from a save

```bash
python3 tools/lol3_save_header.py /path/to/your/slot
```

The first lines on one autosave slot were:

```text
display name +0: **AUTOSAVE**
display name bytes after the NUL +0xd..+0x2c:
(two hex rows)
file length +0x2c: 298876
version +0x30/+0x34: 38 310
```

The position lines, later in the same listing, were:

```text
current level +0x498: 2
player +0x49c: x 1769472 (27.0000) z -126353408 (-1928.0000) heading 0x8000 region 0x1839
second object +0x4aa: x 1769472 (27.0000) z -126353408 (-1928.0000) heading 0x8000 region 0x1839
```

## See what a level's commands do

```bash
python3 tools/lol3_script_browser.py QWOD0
```

```text
QWOD0 object commands: 164
0x02 11: For +4 = 2 or 3, resolves the object from +1/u16 +2 and calls player helper 0x415540 or 0x415620. Other values route to player command 0x410AA0.
0x03 6: Calls target vtable +0xC0 and keeps its result.
```

One line per opcode follows, then `QWOD0 region commands: 42`.

## List a level's creatures

```bash
python3 tools/lol3_odf_companions.py --list QWOD0
```

The command first lists the section-0 names. The creature lines are:

```text
QWOD0 field-3 rows 1
creature 1: tag SPIDER +0x59 0 +0x5b 100 +0x81 0x5
ai SPIDER: stat.csv, goals.csv, actions.csv, effector.csv, spells.csv
```

## List one archive

```bash
python3 tools/extract_wsx_entries.py --list --stems QWOD0
```

```text
QWOD0.WSX
count 4 data_base 0x36
key 0xe128e119 offset 0x36 size 6871261
```

Three more key lines follow.

## Read waypoints

```bash
python3 tools/lol3_map_spans.py --list QWOD0
```

```text
QWOD0 waypoints 1 paths 0
waypoint 1: x 11063 z -2943 surface 0xe7 +6 0x2 +7 0x4
```

A further line prints the first slot's raw bytes.

## List the music tracks

```bash
python3 tools/lol3_media_check.py --tracks
```

```text
MUSIC1.WSX+0x36 size 4157978 key BD4CB6E0 tag 0x55 channels 2 rate 44100 align 1 bits 0 stem uewoods0
```

One line per music entry follows.
