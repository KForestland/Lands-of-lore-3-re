#!/usr/bin/env python3
"""Run every LoL3 tool that has a --check against a game DAT folder; one line each.

  check_all.py --data /path/to/LoL3/DAT     # or set $LOL3_DAT
Exit code 0 when all pass.
"""
import argparse
import os
import subprocess
import sys

TOOLS = ["repo_guard", "extract_wsx_entries", "walk_lmf_leaves", "lol3_texture_spans", "lol3_texture_palettes", "lol3_texture_png",
         "lol3_script_framing", "lol3_texture_archive", "lol3_script_notes", "lol3_level_report", "lol3_media_check", "lol3_level_schematic", "lol3_map_spans"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default=os.environ.get("LOL3_DAT"), help="the game's DAT folder (default: $LOL3_DAT)")
    a = ap.parse_args()
    if not a.data:
        ap.error("give --data or set LOL3_DAT")
    here = os.path.dirname(os.path.abspath(__file__))
    failed = []
    skipped = []
    for t in TOOLS:
        p = subprocess.run([sys.executable, os.path.join(here, t + ".py"), "--check", "--data", a.data],
                           capture_output=True, text=True)
        line = (p.stdout.strip().splitlines() or [p.stderr.strip()[-300:]])[-1]
        print(line)
        if p.returncode != 0:
            failed.append(t)
        elif "SKIP" in line:
            skipped.append(t)
    if failed:
        print(f"{len(failed)} of {len(TOOLS)} checks FAILED: {', '.join(failed)}")
    elif skipped:
        print(f"{len(TOOLS) - len(skipped)} CHECKS PASSED, {len(skipped)} SKIPPED (no game-written cache): {', '.join(skipped)}")
    else:
        print(f"ALL {len(TOOLS)} CHECKS PASSED")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
