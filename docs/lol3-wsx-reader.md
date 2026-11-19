# Native WSX archive and cache reader

Addresses are English retail `LOL3.DAT` PE32 VAs. Subtract `0x400C00`
for an instruction's file offset (and `0x401800` for a data address). See the [PE identification](lol3-lmf-reader.md).

## WSX directory

**CONFIRMED.** The startup reader at `0x43CC60` opens `GLOBAL.wsx`
(string at file `0x147EE8`, open at `0x43CD09`). The level-archive
path uses the same header parsing sequence after `0x43D38D`. On a nonzero
first word (the `jne` at `0x43CD2D`) it reads four bytes, keeps them, and reads two more
at `0x43CD25` and `0x43CD8A–0x43CDA1`. At `0x43CDA4–0x43CDB6`
the first word is the count, the following dword is the data size and
the index allocation is 12 times the count. The equivalent reads in
the level archive path are at `0x43D45B–0x43D48F`. A separate zero-word
path can consume a flag prefix (`0x43CD28–0x43CD79`).

**CONFIRMED.** At `0x4352F2–0x435306`, the file reader binary-searches
a loaded archive's 12-byte rows. Comparator `0x4E41A0` compares the
first dwords as signed values. On a match, `0x43532A` reads row +8
as the byte length. `0x435343–0x435369` uses +4 as the offset, adding
the loaded data base in the stream-backed path. The reader uses that
range at `0x4353C8–0x4353E2`. For example, the CKEEP light-map directory
row at `CKEEP.WSX+0x06` has key `0x936A2304`, and resolves to
`CKEEP.WSX+0xC19084`. The [WSX format page](formats/wsx.md) gives the
original header layout and corpus check.

## Why the size check fails

**CONFIRMED.** Both `cdcache.wsx` copies and game-folder `cdcache.hdr`
have identical first 114 bytes. At +0 and +2 they declare 9 rows and
52,663,679 data bytes. The implied exact file size is 52,663,793.
The `DAT/cdcache.wsx` file is shorter by 49,399,679 bytes. The
game-folder copy is longer by 52,232,321 bytes. Both therefore fail the
length equality check of this repository's WSX reader (`tools/extract_wsx_entries.py`). The native readers at `0x43CC60` and `0x43D38D`
have no such file-length comparison. The game-folder size also follows from the expansion step: the size limit
`[0x545520]` is clamped to 0x6400000–0x1F400000 at `0x4E4CFB–0x4E4D23`, and 114 + 1,639 × 64,000 = 104,896,114.

**CONFIRMED.** The native game-folder path probes `CDCACHE.wsx` at
`0x4E4C00`. It takes the installed/reset path when the paired resources
are absent or the corresponding initialization tests require it
(`0x4E4C08–0x4E4CBE`). The reset branch at `0x4E4C9F–0x4E4CA9`
passes the header and cache names (strings at file `0x14DFD8` and
`0x14DFE4`) to the same file copy helper used immediately above
for the list. The initializer reopens the cache, queries length and
can read `CDCACHE.hdr` and write its bytes to the cache
(`0x4E4D44–0x4E4DC2`). The expansion loop seeks to end at `0x4E4E0A`
and writes blocks of 0xFA00 bytes at `0x4E4E78`.

## Cache index lifecycle

**CONFIRMED.** At `0x4E50F6–0x4E510F` the reader seeks to the
archive data base and consumes a four-byte marker. If the marker
differs, it seeks back and writes `0xF1E2D3C4` at
`0x4E5141–0x4E5157`. Both paths leave the cursor after the
marker when they call `0x4FE480` at `0x4E516E` or
`0x4E5194`. The game-folder marker is at +0x72 and the
allocator index starts at +0x76. The DAT copy has dword
`0xD0BCD8BE` at +0x72. See the [cache rows](formats/wsx.md#cdcachewsx)
for the original sizes, fields and offsets.

**CONFIRMED.** `0x4FE480` records the index position and
loads 0x3C0 bytes (`0x4FE4C2–0x4FE4FA`). On reset it
can create a free span directly after the index
(`0x4FE56C–0x4FE58A`) and persist the rows
(`0x4FE5BE–0x4FE5D7`). The allocation routine at
`0x4FE870` first looks up an existing valid name key, then
checks spare spans by length (`0x4FE884–0x4FE8E3`). The
lookup at `0x4FE7A3–0x4FE81F` checks position and key and
invalidates a row when its generation token changes. The
release path at `0x4FE690–0x4FE6D8` clears the occupied
flag and `0x4FE6E0–0x4FE738` merges neighboring free
spans. Shutdown writes the index back to its stored position
(`0x4FE667–0x4FE680`). Payload writes have their own path
(`0x4E4854–0x4E487F`).

**CONFIRMED** (the shipped body and the missing instruction).
**UNCONFIRMED** (which screen the shipped block holds, and why it has 51 blocks when this build fills at least 100 MiB).
`DAT/cdcache.wsx` is 114 bytes plus 51 copies of one 64,000-byte
block. The block is not present in `LOL3.DAT`, `LOL3.EXE`, or
this installation's game-written cache, and sampled 16-byte pieces of
it are absent from the other `DAT` files and the root `cdcache.lst` /
`CDCACHE.LS_` (stored bytes). The same 16-byte head is absent from
every `.exe`, `.dll`, `.asi` and `.dat` in the install folder.
**CONFIRMED** (where the fill comes from). The initializer's fill loop
`0x4E4E61–0x4E4E95` writes 0xFA00 bytes per pass (`push 0xFA00` at
`LOL3.DAT+0xE4271` = `0x4E4E71`) to the `CDCACHE.wsx` handle
`[0x54F738]` through `0x4357E0`. The source is the pointer `0x5046E0`
returns for the surface `[0x5D5394]`: the lock is the vtable +0x64 call
at `0x504589`, and `0x5045B9–0x5045C7` take `lpSurface` from descriptor
+0x24. The fill is screen surface memory, not a stored resource. This
installation's game-written cache (114 bytes plus 1,639 × 64,000) ends
in identical blocks (1,615 to 1,638 checked) that form one 8-bit picture
with 640-byte rows. The shipped block fits the same row width:
6,344 of the 63,360 byte pairs 640 apart are equal, which is a
larger share than at any other distance from 1 to 2,000, and the
block uses 209 distinct byte values. `0xFA00 / 640` is 100, so at
that width the 64,000 bytes the fill copies are 100 rows. The width
is inferred from the bytes: the fill loop (`push 0xFA00` at
`0x4E4E71`) copies one run from the surface pointer and reads no
pitch. The shipped dword at
+0x72 is `0xD0BCD8BE`, the first dword of that block, not the
live marker `0xF1E2D3C4`. `lol3_cache_seed.py --check` re-counts
every distance from 1 to 2,000 and the 209 values.

Every reference to the index base `0x7F39F8` lies in
`0x4FE390–0x4FED37`, and the address of row 0's byte +0x17
(`0x7F3A0F`) does not occur in the code section. The row loops walk
pointers that start part-way into a row (`0x7F3A0D`, `0x7F3A0E`,
`0x7F3A24`, `0x7F3A3C`, `0x7F39FC`, `0x7F3A04`); read against those
starts, their accesses reach only row bytes +0x0, +0x4, +0x8, +0x10,
+0x14, +0x15 and +0x16 (a manual review of `0x4FE390–0x4FEE7D`; the
tool counts absolute addresses only). The byte travels inside the
0x3C0-byte read at `0x4FE4EF`, the matching write at `0x4FE675`, the
0xF0-dword clears at `0x4FE4AF` (the read then replaces it) and
`0x4FE3C7` (the create path, after which rows 0 and 1 are written
only up to +0x15, so a new index holds 0 at +0x17), and the 6-dword
row copies at `0x4FE9BA` and `0x4FEC0E`. Bytes +0x14, +0x15 and +0x16
have their own stores, listed on the format page. In this
installation all 8 occupied rows hold 0x67 at +0x17, as do 12
empty rows, and 17 of the 40 rows have +0x17 equal to +0x16.
`lol3_cache_seed.py --check` re-counts the copies, the address
tallies and that witness. Which screen the shipped block shows is settled by
locking the same surface at the fill loop (`0x4E4E34`) in a running
game and comparing its first 64,000 bytes with the shipped block, or
by rendering the block with the palette that was active when the
shipped copy was made.

On the first run the read at `0x4FE4FA` loads fill bytes, and the
reset loop `0x4FE596–0x4FE5B4` writes row bytes +0, +4, +8, +0x10,
+0x14 and +0x15 only, so +0x16 and +0x17 keep surface pixels. Every
value seen there on empty rows is a pixel value of that picture, and a
second installation's game-written cache holds 0x42 at +0x17 of an
occupied row (measured on that copy).

## Resource name key

**CONFIRMED.** The lookup obtains a resource name, counts the bytes up
to its first NUL, normalizes it through `0x531E30` and calls the hash
at `0x4352BF → 0x509EC3`. The ASCII path in `0x531E61–0x531E81`
uppercases letters a–z. With an initial word of zero, update it once
per uppercase ASCII byte `b` as follows.

```text
key = (rotate_right_32(key, 6) + ((b - 0x30) & 0x3F)) mod 2^32
```

That is the native loop at `0x509ECD–0x509EE2`. Lookup compares the
result as a signed dword at `0x4E41AC–0x4E41B8`.

**CONFIRMED.** The level stems include `levels\ckeep\ckeep` at
`LOL3.DAT+0x147EAC` and `levels\qwod0\qwod0` at `+0x147D94`.
The cache preparation path passes level texture requests to
`0x4E4580` (call at `0x43E047`). It finds the `.tex` substring at
`0x4E45D1–0x4E45E7` and replaces its final character with an underscore
in the source name at `0x4E462C` and the cache name at `0x4E463A`.
All 18 four-entry level directories contain the keys of the
`LEVELS\<STEM>\<STEM>.LMF`, `.MAP`, `.ODF` and `.TE_` names.

| Resource name | Original directory row | Key |
|---|---|---|
| `LEVELS\CKEEP\CKEEP.LMF` | `CKEEP.WSX+0x06` | `0x936A2304` |
| `LEVELS\CKEEP\CKEEP.MAP` | `CKEEP.WSX+0x12` | `0x637A230E` |
| `LEVELS\CKEEP\CKEEP.ODF` | `CKEEP.WSX+0x1E` | `0x6F9A2304` |
| `LEVELS\CKEEP\CKEEP.TE_` | `CKEEP.WSX+0x2A` | `0x73EA231D` |
| `GLOBAL\GLOBAL.ODF` | `GLOBAL.WSX+0x8A` | `0x8B25F239` |
| `GLOBAL\SPELL.ODF` | `GLOBAL.WSX+0x7B6` | `0xFCA1140B` |
| `GLOBAL\GLOBAL.TEX` | `LOCAL.WSX+0x06` | `0x8F75F24B` |
| `GLOBAL\SPELL.TEX` | `LOCAL.WSX+0xBA` | `0x00F1141E` |

The original global names occur at `LOL3.DAT+0x147FD0–0x14801D`.
`python3 tools/extract_wsx_entries.py --data DAT --check` verifies the
76 name/key pairs in the installed archive directories.

**CONFIRMED.** Hashing every NUL-terminated printable ASCII string of
4–180 characters in
`LOL3.DAT` (2,374), `LOL3.EXE` (222) and the 51 size-checked
archives (3,701,411) joins 53 path-like names to directory keys.
Fifty-two are stored in `LOL3.DAT`. One, `missing.aud`, is stored
in `locallng.wsx` and is the WAVE at `LOCAL.WSX+0x240FF66`. The
other 7,364 distinct keys have no stored C string (the 76 constructed
names are checked separately). The hash is only
32 bits: one printable run at `LOCAL.WSX+0x147CF1F` collides with
a key and is not a path. `lol3_name_hash.py --check` re-counts
this. Music key `0x1D4F73DA` is one of the unnamed keys
([music](formats/audio.md)). To name another entry, follow the
caller that builds its filename.

## Close-out

### Q1

**What was measured.** The eighteen bytes at `LOL3.DAT` file +0xE4241 are `81 C6 FF F9 00 00 B8 D3 4D 62 10 F7 E6 8B F2 C1 EE 0C`. They add 63,999, multiply by `0x10624DD3`, and shift the high half right by 12, which returns 51 for a length of 3,264,000.

**What was tried.** This slice is the pass-count setup immediately before the fill loop at `0x4E4E61`. The page already records that the loop writes 64,000-byte passes from locked screen memory and that the shipped file is 51 copies of one block.

**What would settle it.** Lock the same surface at the fill loop (`0x4E4E61–0x4E4E95`) and compare its first 64,000 bytes with the shipped block; that shows which screen the shipped copy holds. The running-game test is not yet run ([probes not yet run](NEEDS_A_RUNNING_GAME.md#probes-not-yet-run)).
