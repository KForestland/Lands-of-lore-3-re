# Glossary

Words used across these pages, in plain terms.

## Shared words

These words mean the same thing in the notes for all three Lands of Lore games.

| Term | Meaning |
|------|---------|
| Original | The released game's own files and program. Every fact in this repository is about the original game. |
| CONFIRMED / UNCONFIRMED | CONFIRMED: proved from the program code or the files. UNCONFIRMED: a reading not yet proved. |
| Answered / Mostly answered / Partly answered | The state words of [open questions](OPEN_QUESTIONS.md). *Answered*: nothing is left to settle from the files or the program. *Mostly answered*: the main question is settled; named details remain. *Partly answered*: part is settled; the main point is open. A row that says 'answered for' a setup (one renderer, one device) counts as answered for that setup only. |
| Native | In or from the original game program, as opposed to a reimplementation. |
| Open question | A numbered question on the [open-questions page](OPEN_QUESTIONS.md). |
| Archive | A file that holds many pieces of game data. |
| Entry | One piece of data stored inside an archive. |
| Level | One place the player walks through, stored as its own set of files. |
| Level sheet | One page per level, written by a tool from that level's files. |
| Schematic | A top-down line drawing of a level from its map data, with no game pixels. |
| Script | Commands the game runs for a level, an item, or a cut-scene. |
| Opcode | The number that begins one script command and selects what it does. |
| Event | A script that runs when something happens, such as a click, a step, or a timer. |
| Item | An object the player can carry, or that a level places in the world. |
| Creature | A living opponent or other character placed in a level. Monster means the same on these pages. |
| Placement | One recorded place where a level puts an item, a creature, or another object. |
| Save slot | One file the original game wrote for a game in progress. Tools may read it; this repository does not store it. |
| Probe | One check that needs the original game running. |
| Rating | The four counted lines near the top of the README, written by `tools/rating.py`. |
| Files read | A file whose every byte a tool here assigns to a known header, directory, entry or other named part; what is inside an entry may still be only partly understood. Files the game writes into the data folder while it runs are added to the total and count as read only if a reader walks them. Which folder is counted: [how we rate](HOW_WE_RATE.md). |
| History page | A page marked **History** at its top: an older note kept as a record. The rating does not count it; where it differs, the current pages are right. |
| File offset | The position of a byte in a file on disk. |
| Spell | A magic effect the player casts. Its cost is stored in the game's tables. |
| Dialogue | Lines a character says, or that the game prints. |
| Music | The game's songs. A music tool can list or convert them. The tools do not play sound. |
| Combat | How an attack is resolved: whether it hits, and what the hit changes. |
| Hash | A number computed from other bytes. A file hash identifies a whole file. A name hash stands in for a file name. |
| LCW, format 80 | Westwood's byte-oriented compression, also called format 80. |
| Mod kit | `tools/modkit.py`: it unpacks the game's text and number tables into files you can edit and builds changed copies of the archives into a new folder ([tools](../tools/README.md)). |
| Patch | A small file (`lol-patch-2`) listing changed bytes, the bytes they replace and the game it is for, made and applied by `tools/patch.py` ([patch format](formats/patch.md)). A *data patch* changes archives and tables; a *program patch* changes the game program and fits only the file with the recorded SHA-256. |
| Undo patch | The `undo.json` that `patch.py apply` writes beside the patched files; applied to the patched copy it gives back the original bytes. |
| Copy of the game | A separate copy of your game folder for trying changes. The tools never write into the game folder you give them. |

## This game

| Term | Meaning |
|---|---|
| DAT folder | The directory of this game's data files, which the tools read. Set `LOL3_DAT` to it, or pass `--data`. It holds the WSX archives. |
| WSX | This game's archive. It uses the MIX layout: a u16 count, a u32 data size, 12-byte rows of key, offset and size, then the data ([native lookup](lol3-wsx-reader.md)). |
| MIX | Westwood archive: a u16 count, a u32 data size, 12-byte rows of key, offset and size, then the data. This game's WSX archives use that layout ([series page](series-formats.md)). |
| Key, name hash | The number an archive stores instead of a name. It is a hash of the name. Each WSX row stores one. |
| Cache | A large file the game writes when it runs, separate from the archives it shipped with. The game-written file here is `cdcache.wsx`. The shipped `DAT` copy is a different file: a 114-byte header and one block repeated, not counted as read. |
| Stem | The short archive name without `.WSX`, such as QWOD0. |
| Level archive | One WSX archive for one level. This game has 18, named with stems such as QWOD0. |
| LMF, light map | The level light maps (the executable calls the asset "Light Map"): a header (dword 0 = 0, dword +4 = 38), a directory of 16-byte rows at `0x100` (12,176 rows in CKEEP; the count is a header field) and LZO1X-compressed groups of members of 44 + 2 × w × h bytes ([LMF page](formats/lmf.md)). |
| LMF storage group | One LZO1X range expanding to consecutive light-map members. See the [native reader](lol3-lmf-reader.md). |
| Light-map member | One decoded LMF member: a 44-byte head (u32 +0 = 0 or 1, u16 +4 and +6, u32 +8) and 2 × u16(+4) × u16(+6) more bytes; field meanings beyond the length rule are open ([reader page](lol3-lmf-reader.md)). |
| MAP | The level file of points, surfaces, waypoints, paths and placement tables. |
| ODF | A level's object definitions. The type-tagged rows are partly read ([MAP and ODF](formats/map-odf.md)). |
| Type 3, type 16 | Two MAP placement tables, named by those type numbers. The loader builds one object per row, as it does for creatures, movers and items. |
| Mover | A MAP placement table of type 32. Each row is one object, built like the other placement rows. |
| `0x028E` / `0x828E` | Flags of the row-span texture records decoded on the [texture page](formats/textures.md). |
| QWOD0, SWOD4 | Two level archives used as reference samples for byte-pattern statistics. |
| Byte-pattern label | A name for a recurring byte sequence found by statistics, without a known game meaning (Q8). |
| `LOL3.DAT`, `LOL3.EXE` | `LOL3.DAT` is the game program (a 1.6 MB Windows PE file); addresses in the pages are its virtual addresses (VA) unless a file offset is named, convert with VA − 0x400C00 for code (`.text`) and VA − 0x401800 for data (`.rdata`/`.data`). `LOL3.EXE` is a 77 KB launcher. |
| Witness | A concrete sample (a record, file or capture) used to test a claim. |
| Sidecar, companion archive | The `<STEM>S.WSX` archive next to a level archive; it holds the level's sounds. |
| `.TE_`, wrapper | A level's texture pack, stored under a name ending in `.TE_`. The wrapper is its compressed form: a u32 decoded length, then packed lengths each followed by an LZO1X chunk of up to 1 MiB decoded, ending at a zero length ([textures](formats/textures.md)). In the level WSX the stored name is `.tex` with the last letter replaced (`0x4E45D1–0x4E463A`). |
| LZO, LZO1X | A compression method. Packed textures need the system library `liblzo2` to unpack. This game's decoder is at `0x4ECDB0`. |
| Arm (palette selector) | One branch of the texture palette selector `0x44B6E0`; the cache textures all use arm 3 ([palette sources](lol3-texture-palette-sources.md)). |
| Mip | A smaller copy of a texture (half the width and height of the one before). |
| 16.16 | A fixed-point number: a 32-bit value whose high 16 bits are the whole part. |
| VA, PE | VA: an address in the program after it is loaded. PE: the Windows program format of `LOL3.DAT`. |
| LEVED | The name in the original level-editor paths stored in the art packs (`Q:\PROJECTS\LOL3\LEVED\...`). |
| Trigger, effect, target | A trigger is the record that says when an event starts. In the script notes, *When* names the trigger, *Does* the effects (the actions in stream order) and *Touches* the targets (what those actions change). |
| Region descriptor (region-group row) | A 44-byte row selected by script events and opcode 0xD1; the [events page](lol3-script-events.md) and the [opcode page](lol3-script-opcodes.md) use both names for it. |
| Predicate | A test a script checks before it continues. Here each one is a five-byte MAP row at +0xBC (operation, two typed operands) ([events page](lol3-script-events.md)). |
| Geometry | The shape of a level: its floors, walls and openings. |
| Waypoint | An 8-byte MAP row (signed X/Z) that a path steps through ([readers](lol3-map-odf-readers.md#tail-after-the-vertices)). |
| Path | A 4-byte MAP record (base index, count, flag) naming the waypoints a creature walks. |
| Surface, map region | A 56-byte row of MAP section 2: four neighbour indices, four vertex indices and a height ([readers](lol3-map-odf-readers.md)); the script pages call it a region. Opcode 0xCC with operand +4 = −2 writes its byte +0x22 ([opcode page](lol3-script-opcodes.md)). Scripts also have a separate region-command stream. |
| Field *n*, section *n* | Field *n* is the *n*-th dword after the format tag 38 in a MAP or ODF header; a section is a span of the entry those fields point to ([MAP and ODF](formats/map-odf.md)). "table38" is the older pages' name for this header. |
| VQA | Westwood's vector-quantized movie format. This game uses version 3 ([VQA](formats/vqa.md)). |
| Chunk | A named block inside a larger file. |
| Palette | A table of colours the pictures use. |
| IMA ADPCM | A compressed sound encoding. This game's level sounds are WAV files that use it. |
| PHT | Four large files beside the archives. Each is a prefix of one repeated block, so it is not counted as read; what the bytes mean is open. |
| Miles | The Miles Sound System, the audio library the program imports ([audio](formats/audio.md)). |
| Witness family | A group of byte samples from the older statistics pages that share one pattern ([history](lol3-semantic-phase.md)). |
| Pinned | A tool that checks the SHA-256 of its input and refuses other editions. A pinned header, block or cycle is one whose SHA-256 a tool checks. |
| SKIP | A check result: the check did not run because its input is missing, such as the game-written `cdcache.wsx`. `check_all.py` counts skipped checks apart from passed ones. |
| Mip record | One texture picture in a bank: the record a nonempty mip entry points to. The game-written cache holds 15,118; the record's flags word says how its pixels are stored ([texture bake](lol3-texture-bake.md#cache-record-to-png)). |
| Row-span record | A mip record with flags `0x028E` or `0x828E` whose rows each give a start column and a run of palette indices ([textures](formats/textures.md#row-span-record)). Records with `0x02C6` use the same rows. |
| Edge | In a schematic, one side of a surface, between two of its vertices. A dark edge belongs to one surface; a pale edge is shared by two. |
| Script summary, script notes | A script summary is the page per level in [levels/notes](levels/notes/README.md): record counts of the object and region streams and their event pools. Script notes are the full per-record listing that `tools/lol3_script_notes.py` writes from your own copy. |
| Target class | The kind of object an object command acts on: player (1), creature (2), type 3, item (4), type 16 or mover (32). Command byte +1 selects it, and it equals the object's type number ([opcode page](lol3-script-opcodes.md#per-class-effects-of-the-indirect-commands)). |
| Event pool | One of the two lists of event rows in a MAP entry: the region-event pool (MAP +0x38/+0x80) and the object-event pool (MAP +0x40/+0x88). A matched row names the commands to run ([events page](lol3-script-events.md)). |
| AI files | Five tables the program loads for a creature's type tag from `global\ai\<tag>`: `stat.csv`, `goals.csv`, `actions.csv`, `effector.csv` and `spells.csv`, stored in `GLOBAL.WSX`. 60 of the 68 tags have all five ([readers](lol3-map-odf-readers.md#type-tags-and-ai-resources)). |
| Heading | The direction an object faces: a 16-bit turn angle at object +0x26. A save stores the player's heading and the second object's ([saves](lol3-native-saves.md)). |
| MP3-in-WAV | A RIFF WAVE file with format tag `0x55` whose data is MPEG-1 Layer III (MP3) frames. The 38 music tracks in the four MUSIC archives are stored this way ([audio](formats/audio.md)). |
| Wine | A program that runs Windows programs on Linux. The running-game probes here ran the original program under Wine with a debugger ([probes](NEEDS_A_RUNNING_GAME.md)). |

## Reader tools

| Term | Meaning |
| --- | --- |
| Level plan | An overhead drawing from the level's geometry. The HTML plan opens in a web browser and lets you choose a map feature to read its details. |
| Gate | A script condition that can control a level change. See [Progression](PROGRESSION.md). |
| Output folder | A directory you choose for the files a tool writes. The level and media tools use a new folder outside the game and the repository. |
| Wavefront OBJ | A standard text file for vertices, faces and texture coordinates. Open it with a 3D model viewer. |
| Texture coordinates (UVs) | The place on an image that corresponds to a face corner. The OBJ exporter uses the four corners of a unit square for each surface. |
| Texture bank | The group of texture descriptors, mip records and their palettes read from a level's shipped or cached files. |
| Type 3 / type 16 placement | A row from either of the MAP placement tables with those type numbers. The plan uses the row number to identify each placement. |
| Upstream: no guard here | This command's event record has no condition of its own or earlier matching record to rule out. The event producer can still gate it. |
| Kind 12 event 2 | A region event record with kind byte 12 and event byte 2. The native matcher compares the incoming event value. See [script events](lol3-script-events.md). |
| Stream / group | The object or region command stream and the offset at which the event's commands begin. |
