# LoL3 Semantic Phase

This note captures the current public semantic checkpoint.

## QWOD0

Promoted byte-level behavior labels:

- `ad` = `entry_high_feeder`
- `a5` = `settled_high_carrier`
- `c5` = `secondary_settled_carrier`
- `eb` = `mixed_high_carrier`

Current persistent spine:

- `ad -> c5 -> a5`
- `eb` self-holds as the mixed side branch

Strict read:

- `ad` is the strongest entry-side anchor
- `c5 -> a5` is the cleanest settled-side durable edge
- `eb` is not noise; it is the mixed self-holding branch
- `QWOD0` does not show one simple global left-to-right takeover curve
  - `a5` is already strong in early bins
  - `c5` surges later in specific bins
  - the durable checkpoint is the local persistent spine, not one monotonic full-body crossover

## SWOD4

Promoted byte-level behavior labels:

- `00` = `broad_lock_hub`
- `06` = `early-body reinforcement lane`
- `02` = soft `co-reinforcement_lane`
- `0b` = `mixed_lock_member`

Current persistent spine:

- early `0b -> 02 -> 06`
- later `0b -> 00`
- `00 -> 00`

Strict read:

- `00` is the only durable mid-body lock hub
- `06/02` are real, but early-body-local
- `0b` is the useful resolver back into `00`
- strongest coarse takeover span:
  - `00` first clearly beats `02+06+0b` across `0768-1280`

## CKEEP

- `CKEEP` remains a real hybrid feeder and support witness
- it does not cleanly land on the durable `QWOD0` semantic spine
- it does not expose its own small persistent shared high-byte core across sampled windows
- do not treat it as a third byte-level semantic anchor
