#!/usr/bin/env python3
"""Read an original LoL3 DAT folder and run the repository checks.

  check_all.py --data /path/to/LoL3/DAT     # or set $LOL3_DAT
Exit code 0 when all pass.
"""
from cli_errors import ReaderArgumentParser, run_cli
import argparse
from ctypes.util import find_library
import os
import subprocess
import sys
from time import monotonic

CACHE_CHECKS = {"lol3_texture_spans", "lol3_texture_palettes", "lol3_texture_png"}
TOOLS = ["repo_guard", "edition", "level_export", "extract_wsx_entries", "lol3_wsx_writer", "walk_lmf_leaves", "lol3_lzo_writer", "lol3_texture_spans", "lol3_texture_palettes", "lol3_texture_png",
         "lol3_script_framing", "lol3_texture_archive", "lol3_script_notes", "level_viewer", "level_edit", "lol3_level_report", "lol3_progression", "lol3_media_check", "lol3_text_writer", "lol3_level_schematic", "lol3_map_spans", "lol3_map_writer", "lol3_combat_census", "lol3_claimed_edges", "lol3_name_hash", "rating", "lol3_cache_seed", "lol3_odf_companions", "lol3_native_checks", "lol3_pe_layout", "lol3_pht", "lol3_save_header", "lol3_save_writer", "lol3_save_selectors", "lol3_script_browser", "lol3_numbers", "doc_index", "doc_links", "doc_format_offsets", "modkit", "translate"]

QUICK_SKIP = {"walk_lmf_leaves", "lol3_lzo_writer",
              "lol3_name_hash", "lol3_wsx_writer"}


def main():
    ap = ReaderArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default=os.environ.get("LOL3_DAT"), help="the game's DAT folder (default: $LOL3_DAT)")
    ap.add_argument("--cache", help="game-written cdcache.wsx (default: next to DAT)")
    ap.add_argument("--check", action="store_true", help="run all checks (the default)")
    ap.add_argument("--quick", action="store_true", help="skip the slow corpus checks and list each skip")
    a = ap.parse_args()
    started = monotonic()
    quick_skipped = QUICK_SKIP if a.quick else set()
    if not a.data:
        ap.error("give --data or set LOL3_DAT")
    here = os.path.dirname(os.path.abspath(__file__))
    failed = []
    skipped = []
    last_line = {}
    # With liblzo2 the light-map check also decodes every member and counts the header-word census.
    extra = ({"walk_lmf_leaves": ["--decode"], "lol3_native_checks": ["--decode-copy"]}
             if find_library("lzo2") else {})
    for t in TOOLS:
        if t in quick_skipped:
            print(f"SKIP {t}: quick mode")
            continue
        before = monotonic()
        options = ["--cache", a.cache] if (t in CACHE_CHECKS or t == "lol3_lzo_writer") and a.cache else extra.get(t, [])
        p = subprocess.run([sys.executable, os.path.join(here, t + ".py"), "--check", "--data", a.data, *options],
                           capture_output=True, text=True)
        out = p.stdout.strip().splitlines()
        fallback = f"{t}: exit {p.returncode}" if p.returncode else p.stderr.strip()[-300:]
        line = out[-1] if out else fallback
        print(f"{line} [{monotonic() - before:.2f}s]")
        last_line[t] = line
        if p.returncode != 0:
            for detail in p.stderr.splitlines()[-20:]:
                print(f"  {detail}")
            failed.append(t)
        elif t in CACHE_CHECKS and line.startswith(f"CHECK {t[5:]}: SKIP:"):
            skipped.append(t)
        elif t == "lol3_lzo_writer" and line.startswith("CHECK LZO write: SKIP:"):
            skipped.append(t)
        elif t == "lol3_save_writer" and line.startswith("CHECK save_write: SKIP:"):
            skipped.append(t)
    print(f"Total elapsed: {monotonic() - started:.2f}s")
    if failed:
        print(f"{len(failed)} of {len(TOOLS) - len(quick_skipped)} attempted checks FAILED: {', '.join(failed)}")
    elif skipped or quick_skipped:
        reasons = ["quick mode"] if quick_skipped else []
        if CACHE_CHECKS.intersection(skipped):
            reasons.append("no game-written cache")
        if "lol3_lzo_writer" in skipped:
            reasons.append("no liblzo2")
        if "lol3_save_writer" in skipped:
            reasons.append("no liblzo2" if "no liblzo2" in last_line["lol3_save_writer"] else "no game-written saves")
        skipped += sorted(quick_skipped)
        print(f"{len(TOOLS) - len(skipped)} CHECKS PASSED, {len(skipped)} SKIPPED "
              f"({', '.join(dict.fromkeys(reasons))}): {', '.join(skipped)}")
    else:
        print(f"ALL {len(TOOLS)} CHECKS PASSED")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
