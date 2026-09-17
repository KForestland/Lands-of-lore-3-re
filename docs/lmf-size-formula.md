# LMF chunk size ladder

Observed discrete blob sizes in LoL3 `.LMF` files:

| size | n | payload records | payload bytes |
|------|---|-----------------|---------------|
| 76 | 1 | 4 | 64 |
| 108 | 2 | 6 | 96 |
| 172 | 3 | 10 | 160 |
| 300 | 4 | 18 | 288 |
| 556 | 5 | 34 | 544 |
| 1068 | 6 | 66 | 1056 |
| 2092 | 7 | 130 | 2080 |
| 4140 | 8 | 258 | 4128 |
| 8236 | 9 | 514 | 8224 |
| 16428 | 10 | 1026 | 16416 |

Formula: `size = (2^n + 2) * 16 + 12` for `n = 1..10`.

Interpretation so far:
- 12-byte header + `(2^n + 2)` records of 16 bytes each.
- Many blobs are **directory nodes**: sequences of `(offset, size, 0xCDCDCDCD, 0)` pointing at other same-ladder blobs.
- Non-`0xCDCDCDCD` blobs cluster in the geometry pool (`header field[1]` .. `field[3]`).
- Exact 16-byte leaf record layout (vertices vs BSP/octree vs compressed) is still open.
- Primary table at `0x100` holds 38 `(rel, size, marker, aux)` entries; markers are often `0xCDCDCDCD` (MSVC fill).

Header (`u32@0=0`, `u32@4=38`, then fields):
- `field[0] = 0x100` (record table base)
- `field[1]` / `field[2]` ≈ geometry-pool start
- `field[3]` ≈ geometry-pool end / large payload bound
- `field[4]` ≈ end of primary payload span
