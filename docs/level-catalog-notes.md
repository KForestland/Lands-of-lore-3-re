# Level catalog notes (table38 metadata)

Updated 2026-09-17.

Compact WSX entry payloads with `table38` headers expose named level content:

- Field/chunk 0: material / floor names (`Floor1`…, `Water Baby`, …)
- Secondary chunk: prop / encounter / decoration names (`Lamp`, `Door`, `Pine Tree`, …)
- Entity chunk: spawn / NPC-style names (`Jeron`, `Luther`, `Richard`, `Dash`, `Dawn`, …)
- Field 2: sentinel `0xffffffff` placement records with packed control/coord words

Public tooling still documents structure more than a full placement importer.
Private Classic lane writes per-stem JSON catalogs under the local Godot project’s
`assets/data/level_catalogs/` for UI and upcoming importers.

Do not commit retail blobs.

## Placement records (field2)

Live object descriptors use sentinel `0xffffffff` then an inline name (Door, Gate, …)
and packed `control/coord/state/value` words. Coord byte quads are exported into Classic
`level_catalogs/*.json` as `placements[]` with scale still TBD.

## Related

See also `lmf-size-formula.md` for `.LMF` nested index geometry pools.
