# LoL3 Semantic Anchor Table

This table summarizes the safest public byte-level checkpoint claims.

| Witness | Byte / Edge | Public label | Current status | Notes |
|---|---|---|---|---|
| `QWOD0` | `ad` | `entry_high_feeder` | durable entry anchor | strongest entry-side anchor, but not a full-body master switch |
| `QWOD0` | `c5 -> a5` | settled-side durable edge | strongest repo-grade `QWOD0` edge | safest promoted settled relation |
| `QWOD0` | `eb` | `mixed_high_carrier` | durable side branch | mixed self-holding branch, not noise |
| `SWOD4` | `00` | `broad_lock_hub` | durable lock hub | only durable mid-body lock hub |
| `SWOD4` | `0b -> 00` | resolver-to-hub edge | strongest durable edge | survives later collapse cleanly |
| `SWOD4` | `00 -> 00` | self-holding hub edge | strongest durable edge | late lock collapse signature |
| `SWOD4` | `02`, `06` | early reinforcement-side locals | early-body-local only | real, but not durable mid-body anchors |
| `CKEEP` | support witness | hybrid feeder | support-only | do not treat as a third semantic anchor |

Working rule:

- promote the durable edges first
- treat early-body-local relationships as useful support, not as the main public checkpoint
