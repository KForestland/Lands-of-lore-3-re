# LoL3 runtime texture evidence: CONVERT 028E

The runtime `CONVERT` art banks in `CDCACHE.WSX` use a row-span payload for
flags `0x028E` and `0x828E`. The decoded record is:

```text
u16 A, u16 B, u8 data[B]
mode = A & 0xC000
x0   = A & 0x3FFF
```

Each row places `B` bytes at column `x0`. Mode `0` copies the palette indices;
mode `0x4000` is the transparent/skip-index variant. Empty rows (`B == 0`)
are valid. The 26 sampled mip payloads consume exactly `height` records and
the parser reaches the payload end in every case. This closes the span ABI for
the sampled runtime bank.

The grey-index renders are recognizable game objects: EWOD1 silhouettes,
BUPP1 sword and medallion forms, and KVOLC rock/volcano forms. This is strong
evidence that the row placement is the texture decoder, rather than a generic
binary coincidence. The 8×8 BUPP1 sample is an empty-marker case and should
not be used as a visual quality check.

The current rainbow-looking color renders do not indicate a failed row codec.
They result from an unresolved palette/bake stage. The PE `CONVERT` path reads
the 768-byte VGA palette and applies a fade/remap path, while the renderer's
RGB555 bake uses a separate u16 lookup. The available offline palette probes
show that applying the bank's own 6-bit palette produces coherent silhouettes
but does not recover the final gold/color appearance. Cross-bank palettes are
not an accepted fix.

Evidence and reproduction:

- `/home/bob/lol3_out/tools/probe_028e_resume_atlas.py` — exact-consume and
  mode-separated atlas
- `/home/bob/lol3_out/tools/probe_028e_palette.py` — own/cross/fade palette
  comparisons
- `/home/bob/lol3_out/tools/probe_028e_bake_pal.py` — synthetic RGB555 probe
- `/home/bob/lol3_out/analysis/028e_resume_atlas_view/report_20260921T0048.json`
  — 26 witness statistics
- `/home/bob/lol3_out/analysis/028e_palette_view/report.json` — palette metrics

The remaining texture task is to capture or reconstruct the runtime u16 bake
lookup used by `0x6601B8`/`0x44B6E0`, or obtain a runtime `CONVERT` bank dump
after the level loader installs it. The LEVED `+1` `.tex`/PCX-like packs are a
separate source format and should not be decoded with this row-span parser.

This document does not claim trusted final-color PNGs or close the CKEEP door
texture; those remain open.

## CKEEP palette boundary (2026-09-25)

`/home/bob/lol3_out/godot_import/assets/textures_ckeep/ckeep_palette.png` is a 256-entry VGA-style palette visualization. Its channels are predominantly 6-bit values expanded to 8-bit (`0..63` multiplied by four, with minor rounding/low-bit artifacts), matching the bank palette representation. It is therefore useful for indexed previews but is not the renderer's missing RGB555/u16 bake table. The final color stage remains a runtime lookup or remap path; substituting this PNG's colors cannot close that gap.

## Per-texture palette order (2026-09-26)

Adjacent-pixel measurements over all sampled witnesses show that the span
indices are not ordered for any shared palette. The bank's own palette at
`+0x6A2` gives a mean 6-bit colour step of 47–57. Every level art-pack
palette gives about 12–15, and all levels score about the same, because they are
ramp-ordered. Index differences between neighbours peak at 0 and then at
texture-specific fixed jumps (for example ±40/±13/±17), not ±1. Each texture uses
nearly every index in `2..N`. The indices therefore address a per-texture colour
table in quantizer order. Substituting a bank, level, fade or shade palette cannot
recover the original colours.

The bank header regions after the palette are index tables, not colour: `+0x9A2`
holds 66 × 256-byte light-level rows (`0x4200`), and `+0x4BA2` holds two 256×256
byte tables (`0x20000`). Texture records are `u32 flags, u16 w, u16 h, u32 size`
plus the payload, with no inline palette. The remaining task is to locate the
per-texture table through the bank directory or capture the runtime
`0x6601B8` u16 table for one known slot.
