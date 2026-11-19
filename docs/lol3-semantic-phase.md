# LoL3 Semantic Phase

> **History (September 2026).** Kept as a record of an earlier pass. The current state, with the check behind each claim, is in [STATUS.md](STATUS.md); open points are in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md).

This note captures the current public semantic checkpoint.

Fast read:

- the strongest durable `QWOD0` edge is `c5 -> a5`
- the strongest durable `SWOD4` edges are `0b -> 00` and `00 -> 00`
- everything else in this note should be read around those anchors

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
- `06` = `early-body reinforcement band`
- `02` = soft `co-reinforcement_band`
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

## Repo-Grade Anchor Table

See also:

- [`../evidence/lol3-semantic-anchor-table.md`](../evidence/lol3-semantic-anchor-table.md)

## CKEEP

- `CKEEP` remains a real hybrid feeder and support witness
- it does not cleanly land on the durable `QWOD0` semantic spine
- it does not expose its own small persistent shared high-byte core across sampled windows
- do not treat it as a third byte-level semantic anchor

## Visual Aids

- [`../examples/lol3-qwod0-semantic-spine.svg`](../examples/lol3-qwod0-semantic-spine.svg)
- [`../examples/lol3-swod4-semantic-spine.svg`](../examples/lol3-swod4-semantic-spine.svg)

## Native MAP and ODF cross-check

**CONFIRMED.** The two archives contain distinct MAP and ODF resources.
The native loader at `0x43EAB2–0x43EC92` reads the MAP's vertices,
waypoints and surfaces from separate sections. The ODF loader at
`0x43FDE2 → 0x4F0CE0` reads the field-3 definitions. Joining the actual
entries by their native name keys gives these original file offsets.

| Archive | MAP start | Vertex rows | Attached rows | Surface rows | ODF field-3 definitions |
|---|---:|---:|---:|---:|---|
| `QWOD0.WSX` | `0x72E28B` | 1,308 at `0x7311B7` | 2,368 at `0x733AB9` | 1,430 at `0x7384B9` | `SPIDER` at row `0x778124` |
| `swod4.wsx` | `0x5A79CA` | 2,526 at `0x5AA8F6` | 4,892 at `0x5B1124` | 2,636 at `0x5BAA04` | `JERON` and `BOAR_M` beginning at `0x622AD9` |

The vertex, neighbor and attached-row indices pass their bounds checks
in both MAP entries. The repeated QWOD0 values `AD/C5/A5/EB`
never occur in surface byte +4 in these two files. SWOD4 has 2,393
surface rows with +4 equal to zero, 14 equal to 2, 29 equal to 6 and
zero equal to 0x0B. These counts come from the 56-byte surface
stride at `0x43EADF–0x43EB04`.

**CONFIRMED (where the named bytes occur). UNCONFIRMED (a window
the program reads).** The adjacent bytes `C5 A5` occur 195 times in
the texture entry at `QWOD0.WSX+0x36` (6,871,261 bytes), twice in the
MAP at `QWOD0.WSX+0x730744` and `+0x730748`, once in the light map at
`QWOD0.WSX+0x694783`, and not at all in the ODF. The texture and light-map hits are in
LZO-compressed bytes, which carry no field meaning. The retail executable
image contains that byte pair once, at file `0xBC607`. Residues 0 through 7 of those 195 texture offsets hold 22, 24, 27,
28, 24, 21, 20 and 29, and no distance between them repeats more
than twice. No byte
column of the MAP's 8-byte vertices, 8-byte section-1 rows, 56-byte
surfaces or 8-byte waypoints steps from `C5` to `A5`.

The two MAP copies sit four bytes apart inside a 64-byte run of
4-byte groups at `QWOD0.WSX+0x730738`, within the unidentified fixed
block from MAP +0x244 (header end) to +0x2F2C (field 0). No header dword in that MAP
equals the run's start. Decoding both light maps (5,364 QWOD0 members
and 10,232 SWOD4 members; each member is 44 bytes plus two bytes per
sample) finds none of `0x0B`, `0xC5`, `0xA5`, `0xAD` or `0xEB` as a
sample's high byte. The largest high byte is 82 in QWOD0 and 127 in
SWOD4, so only `0x0B` is a test the data could have passed.

Whole-archive mode changes (the most frequent byte of each
non-overlapping window from the file start, ties to the lowest
byte) were counted for windows of 64, 256, 1,024, 4,096 and
16,384 bytes. The SWOD4 change `0B` to `00` is common at 64 bytes
(69 in SWOD4, 108 in QWOD0), so it does not single out an edge. `C5` to `A5` occurs once, at the 64-byte size
in `QWOD0.WSX`, and at none of the larger sizes. The history note's
span `0768-1280` is not a field stored in either MAP header.

`lol3_claimed_edges.py --check` re-counts the archive placements, the
MAP columns and the SWOD4 surface byte +4 histogram above. Adding
`--decode` re-checks the light-map high bytes. The window start, the
window length and the step used when these edges were named are not
in the files. Those three numbers are the settling test. The MAP, ODF
and light-map readers cited on the format pages consume the structured
fields, and none of those fields is this transition.
