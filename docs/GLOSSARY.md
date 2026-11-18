# Glossary

| Term | Meaning |
|---|---|
| Original | The released game's own files and program. Every fact in this repository is about the original game. |
| CONFIRMED / UNCONFIRMED | Checked on the game files or in the program / not yet. |
| `DAT/` | The game folder's data directory, holding the WSX archives. Tools take it as `--data` or `$LOL3_DAT`. |
| WSX | The game's archive format: a `u16` entry count, 12-byte records (hash, a second `u32`, size) and the payloads, largest first. |
| Entry | One payload inside a WSX archive. |
| LMF | A geometry index inside the level archives: a record table at `0x100` and blocks whose sizes follow `(2^n + 2) * 16 + 12`. |
| Index block / leaf block | LMF blocks that point to other blocks / that hold data (format open, Q3). |
| MAP, ODF | Level files named by the executable's strings; MAP holds 2D point runs and records, ODF object definitions (partly decoded). |
| `0x028E` / `0x828E` | Flags of the row-span texture records decoded on the [texture page](tex-format.md). |
| QWOD0, SWOD4 | Two level archives used as reference samples for byte-pattern statistics. |
| Byte-pattern label | A name for a recurring byte sequence found by statistics, without a known game meaning (Q8). |
| `LOL3.EXE`, `LOL3.DAT` | The game program; addresses in the pages are its virtual addresses unless a file offset is named. |
