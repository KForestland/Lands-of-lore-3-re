# LoL3 level `.tex` / art blob (notes)

## What the retail blob is
- Per-level art packs from WSX peels (e.g. CKEEP entry3, SWOD4.TEX).
- LEVED provenance paths (`Q:\PROJECTS\LOL3\LEVED\...`).
- Shared u32 constants at +0x08..+0x14; `u16@0x0A == 38`.
- VGA-style palette at **offset 184** (768 bytes).
- Embedded `*.pcx` **names** are references; payloads are not stock PCX.
- Some payloads begin with `+1` / `+0` markers; door example `xtb5door2` has sane `227×169` and a likely compressed size field.

## Engine
- Level load appends `.tex` and can call a bank loader that expects a **`-CONVERT_TEST`** layout (table count 38, palette `0x300`, blocks `0x4200` / `0x20000`) — not the raw LEVED pack layout.
- `0xecdb0` is **LZO1X** used on convert-path chunk buffers. Retail art packs are **not** whole-file LZO (verified with minilzo against SWOD4/CKEEP).
- RemapTab names include `_Uncompress_Texture_Column` and `_UncompressBuff` (names only; no bind table).

## SMCACHE
- Retail `SMCACHE.ICF` + `SMCache.ICI` cache `SLICE\*.SMD` assets (sprites/FX), not level wall `.tex` art.

## CONVERT bank flag `0x028E` (runtime art)

Cdcache CONVERT banks (count 38, pal `0x300`, blocks `0x4200`/`0x20000`) store mip payloads **as-is**. Flag `0x008B` is raw 8bpp (`size==w×h`). Flag `0x028E`/`0x828E` is a **span** encoding, not LZO/Format80:

```text
per row:  u16 A, u16 B, u8 data[B]
mode = A & 0xC000     # 0 = opaque copy; 0x4000 = skip palette index 0
x0   = A & 0x3FFF
place data[B] at column x0  (B==0 is an empty row)
```

On 26 sampled mips the payload is exactly `h` records (full consume). Grey-index placement yields identifiable sprites/props (figures, sword, rocks). Gold-color lock still needs the bake RGB555 LUT; Gladstone `.tex` packs are a different LEVED `+1` layout and are **not** this bank.

## Status
CONVERT `0x028E` row ABI is bound; trusted **color** PNGs and the CKEEP Gladstone door bank are still open. LEVED `+1` door `xtb5door2` remains a source-pack unit test, not the runtime bank.

Detailed reproducible evidence for the 26 exact-consume row-span witnesses and
the remaining palette/bake boundary is in
[texture-028e-evidence.md](texture-028e-evidence.md).


## Embedded `*.pcx` name framing (CKEEP art)

Names appear **before** the subtype tag:

```text
xtb5door2.pcx \0 +1 \0\0  u16 width  u16 height  u16 csize  <payload>
```

Best unit test remains `xtb5door2`: 227×169, csize 19220 (~0.50× raw). Other `.pcx` hits in the blob often have nonsense `height` fields when parsed this way (likely name collisions inside compressed data).

Runtime CONVERT banks (see PE `0x43f680`) want count 38 + `0x300` + `0x4200` + `0x20000` — not this LEVED pack layout.
