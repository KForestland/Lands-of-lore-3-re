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

| File | Whole cycles at +0 | Last partial cycle starts at | Bytes in last partial cycle | End offset (exclusive) |
|---|---:|---:|---:|---:|
| `CYGNUS.PHT` | 6 | `0x6060000` | 11,463,220 | `0x6B4EA34` |
| `RAIDER.PHT` | 3 | `0x3030000` | 11,088,634 | `0x3AC32FA` |
| `quann.pht` | 3 | `0x3030000` | 7,204,334 | `0x370EDEE` |
| `yupa.pht` | 2 | `0x2020000` | 12,497,266 | `0x2C0B172` |

There is no extra file header between these spans. To read and check a
single file, give its name in any case with `--file`:

```sh
python3 tools/lol3_pht.py --data DAT --file CYGNUS.PHT --check
```

Each selected-file check generates the same cycle, reads that file to EOF
and checks the native program anchors. It needs only that PHT and the
two game programs.

## Byte generation

**CONFIRMED.** Starting with state 1, step
`state = (214013 * state + 2531011) mod 2^32`. Take the low byte of
`(state >> 16) & 0x7FFF`. For each `0x0A`, emit `0x0D 0x0A`.
The first expansion occurs at file `+0x3B`, followed by `0x0A` at
`+0x3C`. This reproduces all four files as prefixes of one repeated
sequence, starting at file byte 0. Only the low 24 state bits affect
the extracted byte. Those bits return to 1 after `0x1000000` steps,
including 65,536 newline bytes. With expansion, the cycle has
`0x1010000` bytes. `lol3_pht.py --check` generates the cycle in memory,
compares it with the first block and checks the four files through EOF.

**CONFIRMED.** `LOL3.DAT` has the same recurrence at
`0x51B655–0x51B67C` (file `+0x11AA55`). The LEA and shift chain
multiplies by `4 * ((13 * 16 + 1) * 256 - 1) + 1 = 214013`, then adds
`0x269EC3`. The code stores the new state at thread data `+0x14` and
returns `(state >> 16) & 0x7FFF`. The caller at `0x4FF4D7–0x4FF4DC`
does store the low byte of this return into a buffer. The link between
that caller and the shipped files is **UNCONFIRMED**. The byte match
establishes the stored sequence and text-mode expansion. Its producer
and its use by the game remain open.

**CONFIRMED.** `LOL3.DAT` has four direct calls to the generator
(`0x4FF4D7`, `0x507890`, `0x50B5E4`, `0x50B5F1`) and one direct call to
the seed setter `0x51B640`, at `0x50787B`. That setter stores the value
returned by `0x51B830(0)` (`0x507870–0x50787B`). A stream that starts
at state 1 is the one produced before any seed is set.

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
identifies a consumer of this cycle. Settling test: a file-open trace of
`LOL3.EXE` and `LOL3.DAT` from start-up through a level load, filtered on
`.PHT`. An open of one of the four names identifies the consumer; no open
leaves the files unread by the game. The original distribution step that
produced the files would also settle why the sequence is present.
