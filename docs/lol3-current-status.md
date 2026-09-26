# LoL3 Current Status

This file summarizes the current public LoL3 checkpoint.

## Asset pipeline status (2026-09-26)

- WSX peel: 51/52 DAT files ([wsx-extraction.md](wsx-extraction.md)).
- Textures: CONVERT `028E`/`828E` row-span decode is exact (26/26 payloads; silhouettes
  verified). Colour is open: indices address per-texture colour tables, not a shared
  palette ([texture-028e-evidence.md](texture-028e-evidence.md)). LEVED `+1` packs are a
  separate format ([tex-format.md](tex-format.md)).
- Geometry: LMF directory and size ladder decoded ([lmf-size-formula.md](lmf-size-formula.md));
  leaf vertex semantics unresolved. MAP `field0` outlines are usable for triage
  ([map-format.md](map-format.md)).

## Proven

- `LMF` uses a fixed record table at `0x100`
- sampled `LMF` record shape:
  - `u32 rel_offset`
  - `u32 size`
  - `u32 marker`
  - `u32 aux`
- runtime is clearly `WSX`-driven
- `QWOD0` is a quiet baseline family
- `QWOD0S` is a higher-activity sidecar
- `SWOD4` is a quiet baseline family and the strongest low-byte/control witness
- the outer layer is best modeled as:
  - shared typed region
  - shared regime vocabulary
  - different driver paths through that vocabulary

## Strong Structural Read

- `SWOD4` = immediate branch-owner
- `QWOD0` = staged branch-owner
- `CKEEP` = hybrid feeder

Driver types:

- `QWOD0` = staged high-family takeover
- `SWOD4` = ordering-first, then low-collapse
- `CKEEP` = mixed feeder

## Strong Semantic Read

- `QWOD0`
  - `ad` = entry-high feeder
  - `a5` = settled high carrier
  - `c5` = secondary settled carrier
  - `eb` = mixed high carrier
  - persistent spine:
    - `ad -> c5 -> a5`
  - strict note:
    - `c5 -> a5` is the cleanest repo-grade settled edge
    - the full body is not one simple monotonic takeover curve
    - `ad` is still the best entry-side anchor, but it should not be overread as a full-body master switch

- `SWOD4`
  - `00` = broad lock hub
  - `06` = early-body reinforcement lane
  - `02` = soft co-reinforcement lane
  - `0b` = mixed lock member
  - persistent spine:
    - early `0b -> 02 -> 06`
    - later `0b -> 00`
    - `00 -> 00`
  - strict note:
    - `00` first clearly beats `02+06+0b` across `0768-1280`
    - `06/02` are early-body-local, not durable mid-body anchors
    - the durable lock result is `0b -> 00` and `00 -> 00`, not the full early local family by itself

## Still Open

- higher in-engine meaning above the byte-behavior layer
- broader semantic naming without overclaiming
- future patch/rebuild consequences
