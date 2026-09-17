# LoL3 retail container inventory

Source: `/media/bob/Arikv/REFERENCE/game_files/lol3` (linked as `lol3_out/game`).

## Top-level
| Path | Role |
|------|------|
| `LOL3.EXE` | Game binary (Wine: `wine LOL3.EXE -CD. -16MB -NO_ASSERTS`) |
| `LOL3.DAT` | PE/helper blob (~1.6M), not level WSX |
| `LOCAL.WSX` / `locallng.wsx` | Localization |
| `cdcache.wsx` (+ root `cdcache.wsx`) | CD cache |
| `DAT/` | Primary content WSX/PHT set (~2.6G listed) |

## `DAT/` stems (unique base names)
Witness / semantic anchors (RE focus so far):
- `QWOD0` / `QWOD0S` — quiet baseline + sidecar
- `SWOD4` / `SWOD4S` — quiet baseline / control witness
- `CKEEP` / `CKEEPS` — hybrid feeder / Gladstone keep art candidate
- `RVOL0` / `RVOL0S` — volcanic world candidate (portal slice)

Likely Gladstone / hub / interiors (letter-prefixed WSX pairs):
- `BUPP1`, `DLOW1`, `LUPP2`, `MLOW2`, `OLOW3` (+ `*S` sidecars)

Likely woods / outdoor:
- `EWOD1`, `NWOD2`, `PWOD3` (+ `*S`)

Likely portal / set pieces (from Classic reference names — confirm in-game):
- `KVOLC` — volcanic
- `FLAIR`, `GRULO`, `HWHIT`, `ISHAT`, `JUNDR` — set pieces / NPCs?
- `GLOBAL` — shared

Cinematics / audio / bulk:
- `MOVIES1..4`, `MUSIC1..4`
- `SLICECD1..4` — large slice payloads
- `CYGNUS.PHT`, `QUANN.PHT`, `RAIDER.PHT`, `YUPA.PHT` — photo/video-style

## Extracted witnesses (done)
Peelable with `extract_wsx_entries.py`: `QWOD0`, `SWOD4`, `RVOL0`, `CKEEP`.

## Next inventory pass
Run the same peeler across every `DAT/*.WSX`, emit a size/hash table, and
label stems against Gladstone + five portal worlds for the Classic coverage board.
