# PHT files

**What:** four loose files in `DAT`: `CYGNUS.PHT` (112,519,732 bytes),
`RAIDER.PHT` (61,616,890), `quann.pht` (57,732,590) and `yupa.pht`
(46,182,770). Tool: `tools/lol3_pht.py`.

**CONFIRMED.** Each file is longer than 0x1010000 bytes (16,842,752).
Every later byte equals the byte that far into the first 0x1010000
bytes, and the four files share that first block. `CYGNUS.PHT` is six
full copies plus a remainder; the other three are shorter prefixes of
the same stream. In the first 65,536 bytes, every lag from 1 through
512 matches fewer than 1 percent of the bytes (a random byte matches
about 1 in 256). `lol3_pht.py --check` reads each file through its last
byte, pins the SHA-256 of the first cycle and repeats that lag test.

Nothing is known about what the bytes mean: the 0x1010000-byte block has
no header or internal structure and its entropy is 7.998 bits per byte.
No reader is known.

## Worked example

`CYGNUS.PHT`, first bytes at three offsets one or more cycles apart:

| File offset | Bytes |
|---|---|
| `0x0000000` | `29 23 BE 84 E1 6C D6 AE` |
| `0x1010000` (one cycle on) | `29 23 BE 84 E1 6C D6 AE` |
| `0x6060000` (six cycles on) | `29 23 BE 84 E1 6C D6 AE` |

`quann.pht`, `RAIDER.PHT` and `yupa.pht` start with the same eight bytes.

**CONFIRMED.** `LOL3.DAT` (1,643,520 bytes) and `LOL3.EXE` (77,824 bytes)
contain none of `CYGNUS`, `QUANN`, `RAIDER`, `YUPA`, `.PHT` or `.pht`, in
either letter case, as ASCII or as UTF-16. The code section of `LOL3.DAT`
(file `+0x400` for `0x136400` bytes) does not use `0x1010000` as the
immediate of a one-byte opcode or of opcode `0x81`. The file-search wrapper
`0x51A410` has five callers. Three (`+0x5A3A9`, `+0x5A441`, `+0x5A554`) push
`+0x1488A0`, the string `$*.*`, which sits between `$AUTOSAV.XXX` and
`.\SAVEGAME`. `+0x675A9` pushes `.\SAVEGAME` itself. The call at `+0x34074`
searches a drive root with `*` (`+0x14709C`) appended, before the
free-space query. None names a `DAT` file. The name keys of `CYGNUS.PHT`,
`DAT\CYGNUS.PHT` and the other three names (with and without the folder) are
in no WSX directory and not in either program.

**UNCONFIRMED** (what the game does with them). No stored name and no stored
search pattern in those two programs names the four files, and nothing there
shows how a byte of the cycle would be indexed. Settling test: a file-open
trace that shows whether the game opens any of the four names.
