# LoL3 `.map` (WSX entry1) notes

CKEEP candidate: `CKEEP.WSX_entry1_h637A230E.bin` (~504KB).

## Header

Same `table38` family as `.odf`:

- `u32 count = 38`
- then 38× `u32` fields (mix of section offsets and counts)

Observed CKEEP offsets:

| field | value | role (working) |
|-------|-------|----------------|
| 0 | 12076 | 2D point / outline samples |
| 1 | 43434 | 8-byte records (n=`field[20]`=5066) |
| 2 | 83962 | large payload with `0xFFFF` markers (~212KB) |
| 20 | 5066 | count of field1 8-byte records |

## field0

Repeating 8-byte records that decode cleanly as `(u16 0, i16 x, u16 0, i16 z)`.

CKEEP yields ~341 points; main cluster roughly `x∈[-2000,3000]`, `z∈[-5600,-500]`.

Artifacts: `lol3_out/analysis/ckeep_map_f0_only.png`, `meshes_map/ckeep_map_f0_points.obj`.

## field1

5066×8-byte records. Trailing `u16` is often `16`. Third `u16` clusters on multiples of 128 (`128,384,640,...,2688`). First `u16` looks id-like (`122,158,170,282,...`). Exact wall/sector semantics still open.

## field2

Large stream with frequent `u16 0xFFFF`. Candidate polygon header `(n, a, b, 0xFFFF)` + `n×(i16,i16)` — only a handful of strict triangles survive sanity filters; many hits look like indices or mixed control words, not world XYZ. Needs PE-backed parser.

## Relation to `.lmf`

`.lmf` remains the nested size-ladder index + opaque leaf pool. Prefer MAP/ODF for walk scaffolding until leaf records are bound in the PE.
