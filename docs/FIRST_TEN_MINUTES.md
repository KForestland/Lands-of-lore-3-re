# First ten minutes

Draw a level from your own installed copy of Lands of Lore III.
You need Python 3.10 or later, a web browser, and the
game's `DAT` folder. Find the folder containing `QWOD0.WSX`.


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

Paste these lines, replacing the path after `$data =` with
the folder you found above. Keep the quotation marks around paths.

```powershell
Set-Location "$HOME\Downloads\Lands-of-lore-3-re-main"
$data = 'C:\Games\Lands of Lore III\DAT'
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
Paste these lines, replacing the path after `data=` with the folder you
found above.

```sh
cd "$HOME/Downloads/Lands-of-lore-3-re-main"
data="$HOME/Games/Lands of Lore III/DAT"
out="$HOME/Downloads/LoL3 output"
mkdir -p "$out"
python3 tools/lol3_level_schematic.py --data "$data" --level QWOD0 --out "$out/first-level.svg"
xdg-open "$out/first-level.svg"
```

You should see an overhead plan of QWOD0 with surface edges and numbered placements.
If the tool cannot find a game file, check that the path points to the
folder containing `QWOD0.WSX`. If the open command fails, open
`first-level.svg` from the output folder in your browser.

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

Import `model/QWOD0.obj` in a 3D viewer that can open Wavefront OBJ.
QWOD0 has 1,430 faces. The file includes texture references from your
copy and opens as an untextured model. [Model export and checks](COOKBOOK.md#export-a-level-to-obj)

## Find another job

Use the same Python command with `tools/lol.py` to list the jobs.
Add a job name and `--help` for its options.
[Interactive plans](COOKBOOK.md#open-an-interactive-level-plan)
