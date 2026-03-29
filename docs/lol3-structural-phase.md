# LoL3 Structural Phase

This note captures the current public structural checkpoint.

## Outer Layer

The current best model is:

- shared typed region
- shared regime vocabulary
- witness-specific paths through that vocabulary

Useful regime states:

- low-boundary-local
- mixed-transition
- high-takeover-side

## Branch Owners

- `SWOD4`
  - immediate branch-owner
- `QWOD0`
  - staged branch-owner
- `CKEEP`
  - hybrid feeder

## Driver Types

- `QWOD0`
  - high-family takeover driven
- `SWOD4`
  - ordering-first, later low-collapse driven
- `CKEEP`
  - mixed feeder / support branch

## Why This Matters

- this killed the earlier “one neat mirrored parser” idea
- it let the semantic lane split cleanly:
  - `QWOD0` semantic side
  - `SWOD4` semantic side
  - `CKEEP` as feeder/support

## Visual Aid

- see [`../examples/lol3-typed-region-regime-path.svg`](../examples/lol3-typed-region-regime-path.svg)
