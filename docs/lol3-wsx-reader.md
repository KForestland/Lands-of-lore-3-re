# Native WSX archive and cache reader

Addresses are English retail `LOL3.DAT` PE32 VAs. Subtract `0x400C00`
for an instruction's file offset. See the [PE identification](lol3-lmf-reader.md).

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

**CONFIRMED.** The native cache has bookkeeping after the 9-row directory.
At `0x4E50F6–0x4E510F` it seeks to the stored archive data base and
reads a dword. If that differs from `0xF1E2D3C4`, it writes the marker
at `0x4E5141–0x4E5157`. The game-folder copy has that marker at
file +0x72. The DAT copy instead has dword `0xD0BCD8BE` there.
The cache initializer at `0x4FE480` captures this start position and
can read or write 0x3C0 bytes there (`0x4FE4C2–0x4FE4FA`,
`0x4FE5BE–0x4FE5D7`). The lookup at `0x4FE7A3–0x4FE7B5`
walks 24-byte rows, comparing each candidate's offsets +0 and +8
against its arguments. The append path at `0x4E4854–0x4E487F`
writes payload bytes on the cache handle and updates it.

**UNCONFIRMED.** The lifecycle of every one of the 40 cache slots and
the origin of the compact DAT seed were not established. The marker,
shared header, append path and cache row stride were verified. To
settle individual cache entries, pair a file-position write at
`0x4E4861` with its normalized name key and the matching cache row
before and after `0x4FE6E0`.
