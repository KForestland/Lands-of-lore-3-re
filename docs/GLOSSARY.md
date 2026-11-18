# Glossary

| Term | Meaning |
|---|---|
| Original | The released game's own files and program. Every fact in this repository is about the original game. |
| CONFIRMED / UNCONFIRMED | Checked on the game files or in the program / not yet. |
| `DAT/` | The game folder's data directory, holding the WSX archives. Tools take it as `--data` or `$LOL3_DAT`. |
| WSX | The game's archive format: a `u16` entry count, 12-byte records (hash, payload offset, size) and payload data. [Native lookup](lol3-wsx-reader.md). |
| Entry | One payload inside a WSX archive. |
| LMF | The level light maps (the executable calls the asset "Light Map"): a header (dword 0 = 0, dword +4 = 38), a directory of 16-byte rows at `0x100` (12,176 rows in CKEEP; the count is a header field) and LZO1X-compressed groups of members of 44 + 2 × w × h bytes ([LMF page](formats/lmf.md)). |
| LMF storage group | One LZO1X range expanding to consecutive light-map members. See the [native reader](lol3-lmf-reader.md). |
| Light-map member | One decoded LMF member: a 44-byte head (u32 +0 = 0 or 1, u16 +4 and +6, u32 +8) and 2 × u16(+4) × u16(+6) more bytes; field meanings beyond the length rule are open ([reader page](lol3-lmf-reader.md)). |
| MAP, ODF | Level files named by the executable's strings; MAP holds 2D point runs and records, ODF object definitions (partly decoded). |
| `0x028E` / `0x828E` | Flags of the row-span texture records decoded on the [texture page](formats/textures.md). |
| QWOD0, SWOD4 | Two level archives used as reference samples for byte-pattern statistics. |
| Byte-pattern label | A name for a recurring byte sequence found by statistics, without a known game meaning (Q8). |
| `LOL3.DAT`, `LOL3.EXE` | `LOL3.DAT` is the game program (a 1.6 MB Windows PE file); addresses in the pages are its virtual addresses (VA) unless a file offset is named, convert with VA − 0x400C00 for code (`.text`) and VA − 0x401800 for data (`.rdata`/`.data`). `LOL3.EXE` is a 77 KB launcher. |
| Witness | A concrete sample (a record, file or capture) used to test a claim. |
| Sidecar | The `<STEM>S.WSX` archive next to a level archive; it holds the level's sounds. |
| `.TE_` | The name under which a level's texture pack is stored in its WSX (`.tex` with the last letter replaced, `0x4E45D1–0x4E463A`). |
| LZO1X | A standard fast compressor; the game calls its decoder at `0x4ECDB0`. |
| MIX | Westwood's archive format in Lands of Lore II; WSX uses the same layout ([series page](series-formats.md)). |
| Arm (palette selector) | One branch of the texture palette selector `0x44B6E0`; the cache textures all use arm 3 ([palette sources](lol3-texture-palette-sources.md)). |
| Mip | A smaller copy of a texture (half the width and height of the one before). |
| 16.16 | A fixed-point number: a 32-bit value whose high 16 bits are the whole part. |
| PE, VA | PE is the Windows program format of `LOL3.DAT`; a VA is an address in the loaded program. |
| LEVED | The name in the original level-editor paths stored in the art packs (`Q:\PROJECTS\LOL3\LEVED\...`). |
| Map region | A 56-byte region row in the level; script opcode 0xCC writes its +0x22. See the [opcode page](lol3-script-opcodes.md). |
| Region descriptor (region-group row) | A 44-byte row selected by script events and opcode 0xD1; the [events page](lol3-script-events.md) and the [opcode page](lol3-script-opcodes.md) use both names for it. |
| Predicate | A five-byte MAP +0xBC row (operation, two typed operands) that the program evaluates before a script group runs ([events page](lol3-script-events.md)). |
| Waypoint | An 8-byte MAP row (signed X/Z) that creature paths step through; paths are 4-byte records (base index, count, flag) ([readers](lol3-map-odf-readers.md#tail-after-the-vertices)). |
| Surface | A 56-byte row of MAP section 2: four neighbour indices, four vertex indices and a height ([readers](lol3-map-odf-readers.md)). |
| Field *n*, section *n* | Field *n* is the *n*-th dword after the format tag 38 in a MAP or ODF header; a section is a span of the entry those fields point to ([MAP and ODF](formats/map-odf.md)). "table38" is the older pages' name for this header. |
| LCW | Westwood's byte-oriented compression ("format 80"), used inside VQA frames ([series formats](series-formats.md)). |
| VQA | Westwood's vector-quantized movie format ([VQA](formats/vqa.md)). |
| Miles | The Miles Sound System, the audio library the program imports ([audio](formats/audio.md)). |
| Witness family | A group of byte samples from the older statistics pages that share one pattern ([history](lol3-semantic-phase.md)). |
