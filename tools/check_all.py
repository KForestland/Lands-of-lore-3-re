#!/usr/bin/env python3
"""Run every LoL3 tool that has a --check against a game DAT folder; one line each.

  check_all.py --data /path/to/LoL3/DAT     # or set $LOL3_DAT
Exit code 0 when all pass.
"""
from cli_errors import ReaderArgumentParser, run_cli
import argparse
from ctypes.util import find_library
import os
import subprocess
import sys

CACHE_CHECKS = {"lol3_texture_spans", "lol3_texture_palettes", "lol3_texture_png"}
TOOLS = ["repo_guard", "extract_wsx_entries", "walk_lmf_leaves", "lol3_texture_spans", "lol3_texture_palettes", "lol3_texture_png",
         "lol3_script_framing", "lol3_texture_archive", "lol3_script_notes", "lol3_level_report", "lol3_progression", "lol3_media_check", "lol3_level_schematic", "lol3_map_spans", "lol3_combat_census", "lol3_claimed_edges", "lol3_name_hash", "rating", "lol3_cache_seed", "lol3_odf_companions", "lol3_native_checks", "lol3_pht", "lol3_save_header", "lol3_script_browser", "lol3_numbers", "doc_links"]


def main():
    ap = ReaderArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default=os.environ.get("LOL3_DAT"), help="the game's DAT folder (default: $LOL3_DAT)")
    ap.add_argument("--cache", help="game-written cdcache.wsx (default: next to DAT)")
    a = ap.parse_args()
    if not a.data:
        ap.error("give --data or set LOL3_DAT")
    here = os.path.dirname(os.path.abspath(__file__))
    failed = []
    skipped = []
    # With liblzo2 the light-map check also decodes every member and counts the header-word census.
    extra = {"walk_lmf_leaves": ["--decode"]} if find_library("lzo2") else {}
    for t in TOOLS:
        options = ["--cache", a.cache] if t in CACHE_CHECKS and a.cache else extra.get(t, [])
        p = subprocess.run([sys.executable, os.path.join(here, t + ".py"), "--check", "--data", a.data, *options],
                           capture_output=True, text=True)
        line = (p.stdout.strip().splitlines() or [p.stderr.strip()[-300:]])[-1]
        print(line)
        if p.returncode != 0:
            failed.append(t)
        elif t in CACHE_CHECKS and line.startswith(f"CHECK {t[5:]}: SKIP:"):
            skipped.append(t)
    if failed:
        print(f"{len(failed)} of {len(TOOLS)} checks FAILED: {', '.join(failed)}")
    elif skipped:
        print(f"{len(TOOLS) - len(skipped)} CHECKS PASSED, {len(skipped)} SKIPPED (no game-written cache): {', '.join(skipped)}")
    else:
        print(f"ALL {len(TOOLS)} CHECKS PASSED")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
