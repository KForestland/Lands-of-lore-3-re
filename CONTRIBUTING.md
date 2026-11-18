# Contributing

Thanks for contributing to the public *Lands of Lore III* reverse-engineering repo.

## Scope

Good contributions for this repo:

- documentation fixes
- wording/clarity improvements backed by evidence
- tool fixes (tools read your own game files and write nothing into the repository)
- machine-readable summaries that match the documentation
- diagram or example improvements that clarify a page

Out of scope for this repo:

- raw retail game files
- large raw trace dumps
- speculative semantic claims presented as settled fact

## Working Rules

- Keep claims narrower than your confidence; mark them CONFIRMED or UNCONFIRMED with an address or file offset.
- Separate:
  - measured facts
  - practical interpretation
  - still-open hypotheses
- Prefer updating an existing format page over adding a new note.
- If a result only holds for one witness or one window, do not silently generalize it.

## Evidence Standard

Before adding a new LoL3 claim, try to include:

1. the witness or witnesses involved
2. the exact scope of the result: a whole file or entry, one region of it, or a few bytes
3. whether the result replicated in another window or witness
4. what competing readings were ruled out

## Repo Shape

- `docs/` holds the format pages, the program pages, status and open questions.
- `examples/` holds diagrams and explanatory visuals.
- `evidence/` holds short witness/evidence indexes.
- `data/` holds machine-readable summaries once stable.
- `tools/` holds the readers and checks.

## Pull Requests

Small, focused PRs are preferred.

Good PR shape:

- one result
- one doc polish pass
- one tooling cleanup pass

If you are unsure whether something belongs in the public repo, err on the side of keeping it out until the claim and material are cleaned.

## Checks without game files

Run `python3 -m unittest` and `python3 tools/repo_guard.py --check`
from the repository root. The tests build their own fixtures in memory or
in a temporary directory. GitHub Actions runs these same commands on
pushes and pull requests. CI uses the runner's Python (3.12); the minimum version in the README is not tested there.

## Release procedure (maintainers)

Every commit that reaches a public branch carries the project's noreply identity as author and committer:

```bash
git -c user.name=KForestland -c user.email=261564562+KForestland@users.noreply.github.com commit ...
```

1. Contributor work is squash-merged and committed with the identity above.
2. In a fresh clone of the release branch, with `$LOL3_DAT` set, `python3 tools/check_all.py` must end with `ALL ... CHECKS PASSED` and `python3 -m unittest` must pass, and `python3 tools/repo_guard.py --check --release` must pass (it also checks every commit identity). Contributors do not need `--release`.
3. The tree must be clean after the checks; tools write nothing into the repository.
