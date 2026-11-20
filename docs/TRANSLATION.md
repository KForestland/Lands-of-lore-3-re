# Translate the original text

Use Python 3.10 or newer. These commands read the installation you supply and
write to new folders you name. Run them from this repository. Give `--data`
the same original game folder each time.

```sh
python3 tools/lol.py translate export --data "/path/to/game" --out "/path/to/private tables"
python3 tools/lol.py translate build --data "/path/to/game" --work "/path/to/private tables" --out "/path/to/translated files"
python3 tools/lol.py translate verify --data "/path/to/game" --work "/path/to/private tables" --out "/path/to/translated files"
```

Open a CSV from the export and import all four columns as text. Set only the
`new` column. A blank cell keeps the current string. Type `\e` for an empty
string. Copy codes such as `\x0D` when they appear in the original and use
`\\` for a literal backslash. Keep UTF-8 CSV, the column names, the row order
and the manifest. A locked row has another use in the game. Keep its new cell
blank. Build rereads each changed archive. Verify compares every output byte to
the result computed from the original and your CSVs. To try the output, copy it
over a separate copy of your game.

**The CSVs contain original game text. Keep them, the export manifest and the
rebuilt archives private. Share only a patch made from your own changes.**

**CONFIRMED.** The export includes loose TRRs and matching tables in the WSX
directories. `LOCALLNG.WSX+0x58F7444` and `+0x5987AF5` hold the dialogue and
quest text. `+0x58E4F95` and `+0x5987786` hold lookup tags and are locked.
See [dialogue dispatch](lol3-dialogue-dispatch.md) and the
[round-trip page](ROUND_TRIP.md). “No limit” means there is no fixed per-string
field size. The file and archive offset ranges still apply.

## Check characters before building

```sh
python3 tools/lol.py translate fonts --data "/path/to/game"
```

The list comes from the installed bitmap fonts. Build warns if a replacement
uses a character absent from any listed font. Shorten or reword the translation
with characters the fonts have, or leave the original row. A glyph warning
still allows a copy to build. An input character the writer cannot encode stops
the build. A drawn glyph can look different across fonts.

**CONFIRMED.** `LOL3.DAT+0x143990`, `+0x143AD8` and `+0x143AE4`
name three of the fonts. In `DAT/LOCAL.WSX`, the standard fonts start at
`+0x251C540` and `+0x251CF11`, the Ned font at `+0x240D10B`, and the
option fonts at `+0x24ACF1A` and `+0x24B0781`. Each has signature
`0x0500` at `+0x02` and last glyph index `0xB8` at `+0x11`.
An additional FNT with this signature starts at `DAT/LOCAL.WSX+0x24AC75C`
and is listed by its key, `214918EA`. The standard and option fonts use
the same indexed accents as LoL2.
The editor keeps bytes from `0xB0` onward as escapes. Leave those escapes
in place when unsure what they mean in the original text.

## Make a small translation patch

```sh
python3 tools/lol.py patch make "/path/to/translated files" --data "/path/to/game" --title "My translation" --out "/path/to/translation.json"
python3 tools/lol.py patch apply "/path/to/translation.json" --data "/path/to/game" --out "/path/to/test copy"
```

The patch checks old bytes and makes a matching undo file. It carries the old
and new bytes for the changes, so keep it small and share it only where you
have permission to share those bytes. If the size limit rejects the patch,
use smaller batches or keep replacements the same encoded size. A single
longer early row can shift enough offsets to hit the limit. You can still
keep the rebuilt files for your private copy.
See the [shared patch format](formats/patch.md).
