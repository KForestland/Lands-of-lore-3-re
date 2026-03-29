# LoL3 Witness Map

This note gives the short public map of the main LoL3 witnesses used in the current checkpoint.

## Primary Witnesses

- `QWOD0`
  - main high-side semantic anchor
  - strongest for the staged high-family takeover side
  - durable local semantic spine:
    - `ad -> c5 -> a5`
  - mixed side member:
    - `eb`

- `SWOD4`
  - main low-side semantic anchor
  - strongest for the ordering-first / lock-collapse side
  - durable late lock result:
    - `0b -> 00`
    - `00 -> 00`
  - early-body local family:
    - `0b -> 02 -> 06`

## Support Witness

- `CKEEP`
  - hybrid feeder / support witness
  - useful for the structural branch split and outer regime path
  - not promoted as a third byte-level semantic anchor

## Runtime Provenance

- `QWOD0`
  - quiet baseline family
- `QWOD0S`
  - higher-activity sidecar
- `SWOD4`
  - quiet baseline family and strongest low-byte/control witness

## Structural Role Summary

- `SWOD4`
  - immediate branch-owner
- `QWOD0`
  - staged branch-owner
- `CKEEP`
  - hybrid feeder

## Where To Read Next

- [`../docs/lol3-current-status.md`](../docs/lol3-current-status.md)
- [`../docs/lol3-structural-phase.md`](../docs/lol3-structural-phase.md)
- [`../docs/lol3-semantic-phase.md`](../docs/lol3-semantic-phase.md)
