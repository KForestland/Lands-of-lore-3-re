# Move a placement on a level plan

Open a plan from your own game files. The editor moves existing items and prop
placements. Use Python 3.10 or newer and run the commands from this repository.

```sh
python3 tools/lol.py level --data "/path/to/game" --level QWOD0 --out "/path/to/level plans"
```

Open `QWOD0.html` in the new folder. Click **Move a placement**, then pick
an item or prop in the list. You can also select its marker. The plan outlines
its stored surface. Enter the new X and Z, or click **Pick on the plan** and
click inside the outline. Click **Stage move** to preview the new position.
**Download changes** writes a JSON file with the moves. **Clear moves** resets
the preview.

Give the downloaded file and your original game to the writer. Use a new
output folder whose parent exists. The writer prints the file and number of
verified moves.

```sh
python3 tools/level_edit.py "/path/to/downloaded moves.json" --data "/path/to/game" --out "/path/to/edited level"
python3 tools/level_edit.py "/path/to/downloaded moves.json" --data "/path/to/game" --out "/path/to/edited level" --verify
```

Verification compares every archive byte. An empty move file produces an
identical archive. To try an edited level, put the verified archive in place of
the matching archive in a separate copy of the game.

The available rows have coordinates within their stored surface. Moves stay
inside that same surface and keep height, heading, type, events, and all other
stored fields. Adding or removing placements and moving them to other
areas require their own tools. **UNCONFIRMED.** Changed copies have been
verified by the reader. Their in-game behavior has yet to be observed.

**CONFIRMED.** The MAP loader reads type 3 at VA `0x44FCEB`, type 16 at
`0x4699A2` and items at `0x4D74AC`. It passes each record to the common
placement reader `0x4411F0`, which consumes the signed X/Z words at `+0/+2`
and surface word at `+0x0A`. The editor writes the two coordinates.
See [the native MAP readers](lol3-map-odf-readers.md#surface-and-placement-reads-and-the-largest-retained-ranges).
