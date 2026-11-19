# PHT files

**What:** four loose files in `DAT`: `CYGNUS.PHT` (112,519,732 bytes),
`RAIDER.PHT` (61,616,890), `quann.pht` (57,732,590) and `yupa.pht`
(46,182,770). Tool: `tools/lol3_pht.py`.

**CONFIRMED.** Each file is longer than 0x1010000 bytes (16,842,752).
Every later byte equals the byte that far into the first 0x1010000
bytes, and the four files share that first block. `CYGNUS.PHT` is six
full copies plus a remainder; the other three are shorter prefixes of
the same stream. `lol3_pht.py --check` reads each file through its last
byte.

**UNCONFIRMED** (what the game does with them). `LOL3.DAT` (1,643,520
bytes) and `LOL3.EXE` (77,824 bytes) contain none of `CYGNUS`, `QUANN`,
`RAIDER`, `YUPA`, `.PHT` or `.pht`. Settling test: a file-open trace
that shows whether the game opens any of the four names.
