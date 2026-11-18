#!/usr/bin/env python3
"""Run every LoL3 tool that has a --check against a game DAT folder; one line each.

  check_all.py --data /path/to/LoL3/DAT     # or set $LOL3_DAT
Exit code 0 when all pass.
"""
import argparse
import os
import subprocess
import sys

TOOLS = ["repo_guard", "extract_wsx_entries", "walk_lmf_leaves"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default=os.environ.get("LOL3_DAT"), help="the game's DAT folder (default: $LOL3_DAT)")
    a = ap.parse_args()
    if not a.data:
        ap.error("give --data or set LOL3_DAT")
    here = os.path.dirname(os.path.abspath(__file__))
    failed = []
    for t in TOOLS:
        p = subprocess.run([sys.executable, os.path.join(here, t + ".py"), "--check", "--data", a.data],
                           capture_output=True, text=True)
        line = (p.stdout.strip().splitlines() or [p.stderr.strip()[-300:]])[-1]
        print(line)
        if p.returncode != 0:
            failed.append(t)
    print(f"ALL {len(TOOLS)} CHECKS PASSED" if not failed else f"{len(failed)} of {len(TOOLS)} checks FAILED: {', '.join(failed)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
