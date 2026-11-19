# LMF light maps

**CONFIRMED.** `LOL3.DAT` appends `.lmf` at VA `0x43E179` and passes
the resulting name to `0x440B40` at `0x43E1BD`. The loader uses the
label `Light Map` at file offset `0x1480E4` (`0x440CD7–0x440CE5`).
The directory indexes groups of light-map data. The reader and the
**UNCONFIRMED** member fields are on the [native LMF page](../lol3-lmf-reader.md). That page names the read watch on +0x0C/+0x10 of a member returned by `0x44EB40` that would settle them.

## Layout

All fields below are little-endian u32s. Offsets are relative to the
beginning of the LMF unless indicated otherwise.

| Offset | Field | Evidence |
|---|---|---|
| `+0x00`, `+0x04` | 0 and 38 on all 18 originals | Default acceptance tests at `0x440BDE–0x440BEF` |
| `+0x08` | Directory offset, `0x100` on all 18 | Seek at `0x440C2F` |
| `+0x0C` | Stored group pool offset | Added to directory +0 at `0x440C6A` |
| `+0x10` | Directory byte size | Directory read at `0x440C34–0x440C3E` |
| `+0x14` | Pool byte extent as measured in all 18 | Equals entry size minus pool offset. **CONFIRMED** not read by the game: `0x440B40` keeps the 0x100-byte header in a stack buffer at `esp+0x24` and reads only +0x00, +0x04, +0x08, +0x0C, +0x10 and +0x18 (`0x440BDE–0x440C66`). |
| `+0x18` | Directory row count | Used at `0x440BF5–0x440C04` and `0x440C7D–0x440C89` |

**CONFIRMED.** Each 16-byte row gives a pool-relative offset, expanded
member byte length, a dword at row +8 masked with 1 (`0x440C55–0x440C5D`), whose low bit requests continuation, and a
field whose low 18 bits give the stored group length at the group start
(`0x440C55–0x440C84`, `0x4E1902–0x4E196E`, `0x4E21C6–0x4E21FD`).
Run the structural check or add `--decode` with liblzo2 installed.

```bash
python3 tools/walk_lmf_leaves.py --data DAT --check
python3 tools/walk_lmf_leaves.py --data DAT --check --decode
```

## Writing

`tools/lol3_lzo_writer.py --check --data DAT` (needs liblzo2) expands each stored group, compresses it again with liblzo2's `lzo1x_1_compress`, and writes new group lengths (the low 18 bits at the group's first row), member offsets and pool size. This is a real encoder, not a copy: the new packed bytes differ from the original in all 5,256 groups, so the 18 rebuilt light maps differ from the files, while the 424,288 decoded members are identical. The same check re-encodes the 465 `.TE_` texture blocks and the 15,990 packed SMD frames that the level and shared texture banks point at (33,068 references); the game-written cache is not needed ([round trip](../ROUND_TRIP.md)). Without liblzo2 it prints one SKIP line. Nothing is written to disk.

## Worked example

**CONFIRMED.** `CKEEP.WSX+0xC19084` starts a 663,806-byte LMF.
At entry +0x08/+0x0C/+0x10/+0x14/+0x18 it has `0x100`, `0x2FA00`,
`0x2F900`, `0x726FE`, `0x2F90` respectively. Thus 12,176 rows
span `[0x100, 0x2FA00)`. The first row at `CKEEP.WSX+0xC19184`
has offset 0, expanded member size 76, flags `0xCDCDCDCC` and
encoded group length 657. At `+0xC48A84` the 657 stored bytes decode
to 35,584 bytes for rows 0–255. The first member has dimensions 4×4.
Across all 18 LMF entries, 5,256 groups cover their pools exactly and
decode to 424,288 members. Every member measures
`44 + 2 × u16(+4) × u16(+6)` bytes.
