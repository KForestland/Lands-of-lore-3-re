# First ten minutes

Draw a level from your own installed copy of Lands of Lore III.
You need Python 3.10 or later and a web browser.

## Find your game files

Open the folder for the copy you play. Find `LOL3.DAT` in that folder and
open the `DAT` folder next to it. Look for `CKEEP.WSX` and `QWOD0.WSX`
directly inside `DAT`. Lowercase names such as `ckeep.wsx` also work.

If you have several installations or test copies, start with the installation
you normally launch. Copy the full path to its `DAT` folder, with both
marker files inside and `LOL3.DAT` one folder up.

## Download the tools

On the [repository page](https://github.com/KForestland/Lands-of-lore-3-re),
choose **Code**, then **Download ZIP**. Extract the whole ZIP to your
Downloads folder. The tools folder should be inside the extracted
repository folder alongside `README.md`. The commands below assume the
extracted folder is `Lands-of-lore-3-re-main`. Use the folder name you see
if it differs.

## Windows

Open **Windows PowerShell** from the Start menu. Run `py -3 --version`.
If the command is missing or the version is below 3.10, install a
current Python 3 release with the Python launcher, then reopen PowerShell.
[Python for Windows](https://www.python.org/downloads/windows/)

Run this line, then paste the folder path when PowerShell asks for it.

```powershell
$data = (Read-Host 'Paste the path to your game folder').Trim('"')
```

Then paste these lines.

```powershell
Set-Location "$HOME\Downloads\Lands-of-lore-3-re-main"
$out = "$HOME\Downloads\LoL3 output"
New-Item -ItemType Directory -Force "$out" | Out-Null
```

Draw the level and open the picture.

```powershell
py -3 tools/lol3_level_schematic.py --data "$data" --level QWOD0 --out "$out\first-level.svg"
Start-Process "$out\first-level.svg"
```

## Linux

Open a terminal. If `python3 --version` reports a version below 3.10,
install a newer Python with your distribution's package manager.
Run this line, paste the folder path and press Enter again.

```sh
IFS= read -r data
```

Then paste these lines.

```sh
cd "$HOME/Downloads/Lands-of-lore-3-re-main"
out="$HOME/Downloads/LoL3 output"
mkdir -p "$out"
python3 tools/lol3_level_schematic.py --data "$data" --level QWOD0 --out "$out/first-level.svg"
xdg-open "$out/first-level.svg"
```

You should see an overhead plan of QWOD0 with surface edges and numbered placements.
If the tool cannot find a game file, check the markers in
[Find your game files](#find-your-game-files). If no window opens, open
`first-level.svg` from the output folder in a browser on your desktop.

To draw the picture again, choose a new picture file name in both lines.

[More recipes](COOKBOOK.md) · [Terms used in the guides](GLOSSARY.md)

## Open an interactive level plan

Use a new subfolder of the output folder you created above.

Windows PowerShell

```powershell
py -3 tools/lol.py level --data "$data" --out "$out\plans"
Start-Process "$out\plans\QWOD0.html"
```

Linux

```sh
python3 tools/lol.py level --data "$data" --out "$out/plans"
xdg-open "$out/plans/QWOD0.html"
```

Click a region or placement to see its details. Turn on **Map numbers**
to show the placement numbers. To repeat the command, choose a new
subfolder such as `plans-2` in both lines.

## Export a 3D model

Use the same paths as above. Choose a new output folder each time.

Windows PowerShell

```powershell
py -3 tools/lol.py model --data "$data" --level QWOD0 --out "$out\model"
```

Linux

```sh
python3 tools/lol.py model --data "$data" --level QWOD0 --out "$out/model"
```

The last line should report 1,430 faces. To view the export, get Blender for
Windows, macOS or Linux, or run `sudo apt install blender` on Debian or Ubuntu.
[Blender downloads](https://www.blender.org/download/)

In Blender, choose
**File → Import → Wavefront (.obj)**. Open `QWOD0.obj` inside the new
`model` folder you named. If the view is empty, select QWOD0 in the
Outliner and choose **View → Frame Selected** in the 3D Viewport.
The model appears untextured. Its texture references are in the OBJ
as comments. [Model export and checks](COOKBOOK.md#export-a-level-to-obj)

## Convert a movie or sound

Install FFmpeg and check that `ffmpeg -version` and `ffprobe -version`
both work in the same terminal. Use the paths you set above and choose
new output folders for each run.

Windows PowerShell

```powershell
py -3 tools/lol.py movie --data "$data" --file MOVIES2.WSX --entry 1 --out "$out\movie"
py -3 tools/lol.py sound --data "$data" --file QWOD0S.WSX --entry 0 --out "$out\sound"
```

Linux

```sh
python3 tools/lol.py movie --data "$data" --file MOVIES2.WSX --entry 1 --out "$out/movie"
python3 tools/lol.py sound --data "$data" --file QWOD0S.WSX --entry 0 --out "$out/sound"
```

Open the files named in the tool output from the `movie` or `sound` folder.
The filenames keep the archive names' letter case. A lowercase installation
produces `movies2-1.mkv` and `qwod0s-0.wav`. The movie has 166 frames. The sound
has 49,655 sample frames. [How to choose a different entry](COOKBOOK.md#convert-a-movie-or-sound)

## Find another job

Use the same Python command with `tools/lol.py` to list the jobs.
Add a job name and `--help` for its options.
[Interactive plans](COOKBOOK.md#open-an-interactive-level-plan)
