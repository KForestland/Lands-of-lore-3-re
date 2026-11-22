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
python3 tools/lol3_level_schematic.py --level QWOD0 --out ../lol3-out/qwod0.svg
```

```text
Wrote schematic for QWOD0 to ../lol3-out/qwod0.svg.
```

The SVG is an overhead line drawing: surface edges, one hollow waypoint square, and numbered placement dots (type 3, type 16, creature, mover, item); 327 overlapping numbers are left out. No game pixels.

## Check the texture cache

The original game writes a texture cache named `cdcache.wsx` in its game folder, beside `DAT`, when it first runs. To get one, start the game once from your installation; the checks then find the file there. The 3 MB `DAT/cdcache.wsx` the game ships is only the seed and holds no texture records. Without the game-written file checks that use other files still run (the LZO writer check then skips only its SMD part). [Cache and row spans](formats/textures.md#the-cache-file)

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

## Change text or numbers with the mod kit

The [mod kit](../tools/README.md#modkitpy) writes the game's text tables and numbers as files you can edit, and builds changed archives into a new folder. The game folder is only read.

```bash
python3 tools/modkit.py unpack "/path/to/LoL3" "my mod work"
```

Open the file in `my mod work/edits/` whose name ends in `_PROMPT.TRR_text.json` (the number in front may differ on your copy) in a text editor and change one line inside `"value"`. Then build and verify:

```bash
python3 tools/modkit.py build "/path/to/LoL3" "my mod work" "my mod output"
python3 tools/modkit.py verify "/path/to/LoL3" "my mod work" "my mod output"
```

Each command ends with one summary line; build and verify print `22 archives or loose tables, 1 changed (PROMPT.TRR)`. Copy `PROMPT.TRR` from the output folder over a backup copy of your game to try it.

## Change one thing safely

This example adds one to the X coordinate of the first waypoint in
`QWOD0.MAP` in a copied `QWOD0.WSX`. **CONFIRMED.** The s16 X is
the first word of that row at archive `+0x733A97` (MAP
`+0x580C`, located by header `+0xC8`). See the
[waypoint layout](lol3-map-odf-readers.md#tail-after-the-vertices).

The result is a modified copy for your own tests, not the original game.
This repository ships no game files and no changed files. The script only
reads your installation and writes only inside the new folder, so your
original stays untouched. Keep the changed copy to yourself and do not
share modified game files.

From this repository's root, set `source` to your game folder containing
`DAT`. Set `out` to a new directory outside the installation and the
repository. The script refuses an output folder inside either and needs
room for a full copy.

```bash
source="/path/to/LoL3"
out="/path/to/my-lol3-copy"
PYTHONPATH=tools python3 - "$source" "$out" <<'PY'
from pathlib import Path
import shutil
import sys

from extract_wsx_entries import parse_wsx, wsx_name_hash
from lol3_map_writer import WAYPOINT, waypoints, write_rows
from lol3_wsx_writer import rows_of, write_wsx

source, out = (Path(arg).resolve() for arg in sys.argv[1:])
repo = Path.cwd()
if any(root == out or root in out.parents for root in (source, repo)):
    raise SystemExit("choose a new output directory outside the source and repo")
archive = Path("DAT/QWOD0.WSX")
members = rows_of(parse_wsx(source / archive))
map_key = wsx_name_hash(r"LEVELS\QWOD0\QWOD0.MAP")
index, = (i for i, (key, _, _) in enumerate(members) if key == map_key)
key, offset, body = members[index]
start, points = waypoints(body)
x, z, surface, field6, mask = points[0]
if x != 11063:
    raise SystemExit("this is not the expected first QWOD0 waypoint")
points[0] = x + 1, z, surface, field6, mask
updated = write_rows(points, WAYPOINT)
members[index] = key, offset, body[:start] + updated + body[start + len(updated):]
rebuilt = write_wsx(members)
shutil.copytree(source, out)
(out / archive).write_bytes(rebuilt)
PY
python3 tools/lol3_map_spans.py --data "$out/DAT" --list QWOD0 | sed -n '1,2p'
```

Expect `waypoint 1: x 11064 z -2943 surface 0xe7 +6 0x2 +7 0x4`.
The copied archive is the same size as the original, with one byte
changed at `QWOD0.WSX+0x733A97`.

## Share a change as a patch

The [README](../README.md#change-a-number-in-your-own-copy) walks through the whole route on your own copy: unpack, change one number, build, make a patch, apply it to a copy, read it back and undo it. The [patch format](formats/patch.md) page gives every rule and limit.

- `make` compares the game folder (`--data`) with a folder of changed files. The output folder of `modkit.py build` works as it is, and so does a copy of the game folder in which only some files changed.
- File names in the patch start at the game folder holding `LOL3.DAT` and `DAT`, whether you give that folder or its `DAT` folder, so a patch made from one applies to the other. A change made in `DAT` is named `DAT/...`, never a copy of the same archive beside `DAT`.
- `apply` writes nothing until every check has passed: each replaced span's SHA-256, the whole-file SHA-256 for a program patch, and the undo. Keep `undo.json` private because it holds original game bytes.
- Program patches: copy the program file (`LOL3.DAT` or `LOL3.EXE`) into a new folder, at the same path it has in the game folder, change a byte with a hex editor, for example one letter of a message, and run `make` with that folder. The patch records the program's SHA-256 and applies only to that exact file. A program change may replace at most 16 bytes at a time and 256 in all, never changes the file length, and never touches copy-protection code.

## Change a saved game (a copy)

```bash
python3 tools/save_edit.py set '/path/to/LoL3/SAVEGAME/$1234___.000' heading 0x4000 --out "my edited save.000"
python3 tools/lol3_save_header.py --data "/path/to/LoL3/DAT" "my edited save.000"
```

Save names begin with `$`; on Linux and macOS put them in single quotes as above (on Windows, double quotes are fine). The first command prints `set: heading OLD -> 0x4000; copy written to ...`, with your save's old value for OLD, then one line saying how far the field is proven. The save itself is only read, and the copy must go outside the game and save folders. Copy it over a slot in the `SAVEGAME` folder of a **copy** of your game to load it.

| Field | Value | Proven |
| --- | --- | --- |
| `position-from` | another save of the same level and version; copies the player's 14-byte position group at +0x49C (X, Z, heading, region) | not yet tested: no edited copy loaded yet |
| `heading` | 0–65535, the low word of the player's heading at +0x4A4 | not yet tested: no edited copy loaded yet |
| `name` | the display name, printable ASCII | not yet tested: no edited copy loaded yet |

Not yet tested. The only edited-save runs the game has loaded changed item rows and quick-cast references; no position, heading or name edit has been loaded yet. A turn made in the game changes the heading in both saved position groups (the player's at +0x49C and the second one at +0x4AA, whose object the pages do not yet name), so a heading-only edit writes a state the game itself never writes. Keep a backup of your saves. A donor from another level or version, or with no region, is refused.
[Slot offsets](lol3-native-saves.md#slot-header-and-stream) ·
[What an edited copy must keep](lol3-native-saves.md#editing-a-copy-of-an-original-slot)

Map viewer and editor notes for tool makers: [tool makers](TOOL_MAKERS.md).

## Open an interactive level plan

```sh
python3 tools/level_viewer.py --data "$LOL3_DAT" --level QWOD0 --out "../LoL3 plans"
```

Open `QWOD0.html` in the new folder. Click a surface, waypoint or
placement to read its row and source offset. Choose **Exits** under **Show**
to see portal commands, gates and earlier events that can take priority.
**Zoom to selection** works for exits attached to a surface. An exit
in an object event still has a list entry even when its location is open.
Placement row numbers start at 1. Use `--level all` for the 18 maps.
[MAP fields](formats/map-odf.md) · [Portal conditions](PROGRESSION.md)

## Export a level to OBJ

```sh
python3 tools/lol.py model --data "$LOL3_DAT" --level QWOD0 --out "../LoL3 model"
```

Import `QWOD0.obj` into a model viewer that supports Wavefront OBJ.
For example, in Blender choose **File → Import → Wavefront (.obj)**,
select the file, then use **View → Frame Selected**. The example writes
one OBJ with 1,430 faces and 2,854 vertices.

The OBJ includes a `# texture-ref` comment before each face. It lists
the first and second material as `index:selector`, then the stored
light-map base number. `none` marks an absent material. The index is
the zero-based row in the level's ODF material table. The signed
selector is its starting texture reference. A negative selector
uses the game's animated lookup. A standard OBJ viewer displays the
untextured model.

The optional `--textures` operation exports pixels separately to
your output folder. Use `--textures all` for
each descriptor with a supported pixel route, or give a positive limit.
Texture export uses an existing matching cache bank or expands the shipped
level bank with liblzo2. The `textures.tsv` index gives each image's
descriptor, mip and size.

The mesh uses the MAP's X/Z positions and the stored surface height at
row +0x18. It splits a shared vertex when two surface heights differ.
OBJ coordinates are (X, height, −Z). Face order is reversed to preserve
the normals after changing the sign of Z. With the model's height axis
pointing up, the top view matches the level plan. In QWOD0, waypoint 1 at
MAP +0x580C selects surface 231 through its word at +0x5810. Its four
corners match the OBJ face in the plan orientation.

The UVs map each face to a unit square. The mesh shows the stored lower
surface heights. Rendering the native walls, slopes and animated
textures needs additional game data. Run
`python3 tools/lol.py model --data "$LOL3_DAT" --check` to verify the vertices,
face indices, UVs and texture references for all 18 levels and compare
their face counts with the published level sheets. The check writes no files.
The same options work with `tools/level_export.py` directly.

[MAP coordinates and heights](lol3-map-odf-readers.md#map-section-0) ·
[Surface texture references](lol3-map-odf-readers.md#surface-texture-references) ·
[Texture palettes and supported flags](formats/textures.md#colour)

## Convert a movie or sound

The [first ten minutes guide](FIRST_TEN_MINUTES.md#convert-a-movie-or-sound)
has steps for Windows and Linux. The movie job reads WSX entries
containing the original VQA format. It writes lossless FFV1 video and
PCM audio in an MKV container. The sound job writes 16-bit PCM WAV
from WAVE entries in the level sound or music archives. Both jobs
use FFmpeg and write only to the new output folder you name.

```sh
python3 tools/lol.py movie --data "$LOL3_DAT" --list
python3 tools/lol.py movie --data "$LOL3_DAT" --list --file MOVIES2.WSX
python3 tools/lol.py sound --data "$LOL3_DAT" --list --file QWOD0S.WSX
```

Replace `--list` with `--entry` and the zero-based number you
want, then add `--out` and a new folder name. To convert a loose VQA or
WAVE file from your own copy, pass its path as `--file` and omit
`--entry`. The same options work with `tools/media_convert.py`
when you put `movie` or `sound` before the options.

The movie check compares the output's frame count with VQHD and the
stereo sample count with the source SND2 packets. The sound converter
uses the source WAVE sample count to trim final block padding and
reads the result back. These checks verify counts and format. The
movie plays with the FFmpeg decoder's rendering and audio.

## Find a tool by job

Run `python3 tools/lol.py` to see the job names. This example reads one
row of a text table.

```sh
python3 tools/lol.py text --data "$LOL3_DAT" dtext.trr --id 0
```

Use `python3 tools/lol.py level --help` to see the level viewer's options.
The original tool filenames also work.
