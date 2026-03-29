# Contributing

Thanks for contributing to the public *Lands of Lore III* reverse-engineering repo.

## Scope

Good contributions for this repo:

- promoted writeup fixes
- wording/clarity improvements backed by evidence
- public-safe tooling cleanup
- machine-readable summaries that match the promoted docs
- diagram or example improvements that clarify the current checkpoint

Out of scope for this repo:

- raw retail game files
- large raw trace dumps
- private scratch ledgers
- speculative semantic claims presented as settled fact

## Working Rules

- Keep public claims narrower than your private confidence.
- Separate:
  - measured facts
  - practical interpretation
  - still-open hypotheses
- Prefer updating existing promoted docs over adding new scattered notes.
- If a result is phase-local, say so directly.
- If a result only holds for one witness or one window, do not silently generalize it.

## Evidence Standard

Before promoting a new LoL3 claim, try to include:

1. the witness or witnesses involved
2. the exact scale of the result:
   - whole stream
   - pre-body region
   - body window
   - local byte neighborhood
3. whether the result replicated in another window or witness
4. what competing readings were ruled out

## Repo Shape

- `docs/` holds promoted public writeups.
- `examples/` holds diagrams and explanatory visuals.
- `evidence/` holds short witness/evidence indexes.
- `data/` holds machine-readable summaries once stable.
- `tools/` holds public-safe helpers only.

## Pull Requests

Small, focused PRs are preferred.

Good PR shape:

- one promoted result
- one doc polish pass
- one tooling cleanup pass

If you are unsure whether something belongs in the public repo, err on the side of keeping it out until the claim and material are cleaned.
