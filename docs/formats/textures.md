# Textures

The retail level archives wrap texture banks in a compressed `.TE_` stream. The installed cache stores expanded texture banks.

| Format | Where | State |
|---|---|---|
| Row-span records, flags `0x028E` / `0x828E` | the texture banks in `cdcache.wsx` in the game folder | layout and palette source CONFIRMED on all 854 records |
| Shared global and spell banks | `DAT/LOCAL.WSX` | native arms 1 and 2 confirmed |
| LZO1X-wrapped level banks | `LEVELS\<STEM>\<STEM>.TE_` inside the 18 WSX level archives | all 465 chunks decoded. The older LEVED `+1` witness was inside the compressed wrapper. |

Older notes: [tex-format](../tex-format.md), [texture 028E evidence](../texture-028e-evidence.md). Tools: `tools/lol3_texture_spans.py` (cache records) and `tools/lol3_texture_archive.py` (the 18 `.TE_` wrappers). They write nothing and make no pictures.

## Compressed level wrapper

**CONFIRMED.** The cache preparation path changes `.TEX` to
`.TE_` at `0x4E462C–0x4E463A`. At
`0x4E4775–0x4E4793` it reads the u32 decoded file length
and first u32 packed length. For each positive packed length it
reads that many bytes and calls LZO1X decoder `0x4ECDB0`
(`0x4E47E9–0x4E4839`), writes the decoded bytes
(`0x4E4850–0x4E4861`), and reads the next packed length.
Zero terminates the stream (`0x4E4896–0x4E48C1`). Each
full chunk decodes to 1 MiB, with a shorter final chunk.
The executable allocates 0x104010 and 0x100000 bytes for
the input and output buffers (`0x4E46FB–0x4E4712`).

**CONFIRMED.** The original `CKEEP.WSX+0x36` texture
entry starts with decoded length 20,463,678 and first packed
length 604,394. Its 20 blocks expand into a bank with dword
38 at +0 and 0x300 at +0x40. The same layout validates in
all 18 entries. The expanded QWOD0, BUPP1, EWOD1 and RVOL0
banks match the 40-row cache directory payloads byte for byte.
Use `python3 tools/lol3_texture_archive.py --data DAT --check --decode`
to repeat the test with liblzo2. The tool emits counts.

**CONFIRMED.** The older CKEEP door-name witness at file
+0x869BA is inside a compressed packet. It expands to a
name in the ordinary bank, with alphabetic bytes following
at expanded bank +0xE8A8F. The supposed `+1` subtype and
size fields are an interpretation of byte positions in the
packed stream. A standalone LEVED `+1` texture layout
in original retail data remains **UNCONFIRMED**. A separate
source entry and a native reader for its header would settle it.

## Row-span record

```
u32 flags            0x028E or 0x828E
u16 width, u16 height
u32 size             bytes of rows that follow
height rows of:
    u16 A            A & 0xC000: 0 = opaque copy, 0x4000 = skip palette index 0; A & 0x3FFF = start column
    u16 B            number of bytes in this row
    B bytes          palette indices placed from the start column
```

`lol3_texture_spans.py --check --data <DAT>` re-ran on 2026-11-18 over the whole `cdcache.wsx` in the game folder (104,896,114 bytes). It found 854 record headers with these flags. All 854 consume exactly `height` rows, every row fits inside the width, and the last row ends at the payload end: 815 with flags `0x028E` and 39 with `0x828E`. CONFIRMED. The older pages tested 26 samples; this check covers every record.

## Worked example

At file offset 1,230,562 of `cdcache.wsx`:

```
8e 02 00 00   80 00   00 01   35 20 00 00   80 00 00 00 …
```

| Bytes | Meaning |
|---|---|
| `8e 02 00 00` | flags 0x028E |
| `80 00`, `00 01` | 128 × 256 |
| `35 20 00 00` | 8,245 bytes of rows |
| `80 00 00 00` | row 0: column 128, 0 bytes (an empty row) |

The next records follow directly, each half the size of the one before: 64 × 128 at 1,238,819 (= 1,230,562 + 12 + 8,245), then 32 × 64, 16 × 32 and 8 × 16. Together they form a chain of five mip levels.

## Colour

**CONFIRMED.** The executable selects a per-descriptor source through
`0x44B6E0` and builds 256 output words at `0x4826D0`. The native
[texture colour bake](../lol3-texture-bake.md) gives the source selector,
zero handling and indexed writes. The [palette inventory](../lol3-texture-palette-sources.md) gives source file offsets for all 854 cache spans and verifies the palette selector and key across all 20 original banks. Its shared-reader section traces the editor filenames to the same header parser.

## The cache file

The texture records live in the game-folder `cdcache.wsx`, a cache the game writes when it runs (our copy: last written 2026-03-27). The counts on this page (854 records, 4 banks) describe this installation's cache; the two texture checks report SKIP if it is absent.

The `cdcache.wsx` in the game folder has a WSX header for 9 entries and 52,663,679 bytes of data. The file is 104,896,114 bytes, and its storage is laid out by a second, 40-row allocation index at +0x76 ([WSX cache rows](wsx.md#cdcachewsx)): the 854 records lie inside the four occupied texture spans (191, 243, 395 and 25 records), 420 of them past file offset 52,663,793. The `cdcache.wsx` in `DAT/` is a different, 3,264,114-byte file with the same kind of header, and it holds no span records. The allocator and its rows are documented on the WSX page; the origin of the smaller `DAT/` copy is open ([Q1](../OPEN_QUESTIONS.md)).
