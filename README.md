# Lands of Lore III RE

Reverse-engineering and documentation for *Lands of Lore III*.

This repository contains:

- promoted reverse-engineering writeups
- structural and semantic checkpoint documentation
- evidence indexes and witness notes
- curated tooling notes

It does not aim to redistribute raw game data.

## Start Here

If you are new to this repo, read these in order:

1. [`closure-summary.md`](docs/closure-summary.md) — plain-English summary of what is closed and what remains open
2. [`final-closure-memo.md`](docs/final-closure-memo.md) — short public handoff memo for the current LoL3 state
3. [`lol3-current-status.md`](docs/lol3-current-status.md) — what is currently proven, what is still open, and where the LoL3 lane stands now
4. [`lol3-structural-phase.md`](docs/lol3-structural-phase.md) — the shared typed-region, regime-path, and driver-type result
5. [`lol3-semantic-phase.md`](docs/lol3-semantic-phase.md) — the current byte-level semantic checkpoint
6. [`repo-scope.md`](docs/repo-scope.md) — what this repo includes and excludes
7. [`provenance.md`](docs/provenance.md) — where the current public claims came from
8. [`tooling-catalog.md`](docs/tooling-catalog.md) — what tooling and workflows were actually used

## Status

RE closure: late-stage semantic checkpoint

- `LMF` containers and `WSX`/opaque blob extraction are structurally understood enough for public documentation
- runtime provenance is solid:
  - LoL3 is `WSX`-driven at runtime
  - `QWOD0` and `SWOD4` are quiet baseline families
  - `QWOD0S` is a higher-activity sidecar
- shared outer typed-region / regime-path model is promoted
- current semantic anchors are promoted:
  - `QWOD0`: `ad`, `c5`, `a5`, `eb`
  - `SWOD4`: `00`, `0b`, with `06/02` as earlier reinforcement-side locals
- strongest current persistent spine:
  - `QWOD0`: `ad -> c5 -> a5`, with `eb` as mixed side branch
  - `SWOD4`: early `0b -> 02 -> 06`, then collapse into `0b -> 00` and `00 -> 00`
- strongest durable repo-grade edges:
  - `QWOD0`: `c5 -> a5`
  - `SWOD4`: `0b -> 00`, `00 -> 00`

## Repository Layout

- [`docs/`](docs) — promoted writeups and checkpoint notes
- [`evidence/`](evidence) — evidence indexes and witness summaries
- [`data/`](data) — machine-readable summaries and catalogs
- [`tools/`](tools) — curated tooling notes and future public tools
- [`future-patches/`](future-patches) — future patch planning kept separate from RE canon

## Asset Policy

This repo intentionally avoids shipping full copyrighted asset dumps.

Included:

- documentation
- evidence maps
- workflow/tooling notes
- structured summaries

Not included:

- raw retail game files
- full extracted media dumps
- raw private working ledgers
