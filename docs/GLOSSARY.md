# Glossary

| Term | Meaning |
|---|---|
| Original | The released game's own files and program. Every fact in this repository is about the original game. |
| CONFIRMED / UNCONFIRMED | Checked on the game files or in the program / not yet. |
| `DAT/` | The game folder's data directory, holding the WSX archives. Tools take it as `--data` or `$LOL3_DAT`. |
| WSX | The game's archive format: a `u16` entry count, 12-byte records (hash, a second `u32`, size) and the payloads, largest first. |
| Entry | One payload inside a WSX archive. |
| LMF | The level light maps (the executable calls the asset "Light Map"): a 38-row directory at `0x100` and LZO1X-compressed groups of members of 44 + 2 × w × h bytes ([LMF page](formats/lmf.md)). |
| Light-map member | One decoded LMF member: a 44-byte head (u32 +0 = 0 or 1, u16 +4 and +6, u32 +8) and 2 × u16(+4) × u16(+6) more bytes; field meanings beyond the length rule are open ([reader page](lol3-lmf-reader.md)). |
| MAP, ODF | Level files named by the executable's strings; MAP holds 2D point runs and records, ODF object definitions (partly decoded). |
| `0x028E` / `0x828E` | Flags of the row-span texture records decoded on the [texture page](tex-format.md). |
| QWOD0, SWOD4 | Two level archives used as reference samples for byte-pattern statistics. |
| Byte-pattern label | A name for a recurring byte sequence found by statistics, without a known game meaning (Q8). |
| `LOL3.EXE`, `LOL3.DAT` | The game program; addresses in the pages are its virtual addresses unless a file offset is named. |
