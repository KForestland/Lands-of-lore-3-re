"""Shared command line for the LoL3 tools: --data (or $LOL3_DAT), --out, --check.

The game's DAT folder is never assumed; tools that read game files need
--data /path/to/DAT or the LOL3_DAT environment variable. Nothing is written
unless an output path is given.
"""
import argparse
import os
from pathlib import Path

DEFAULT_DATA = os.environ.get("LOL3_DAT")


def tool_args(doc, data=True, out_help="write the result here (default: print only)"):
    ap = argparse.ArgumentParser(description=doc, formatter_class=argparse.RawDescriptionHelpFormatter)
    if data:
        ap.add_argument("--data", default=DEFAULT_DATA, required=DEFAULT_DATA is None,
                        help="the game's DAT folder (default: $LOL3_DAT)")
    ap.add_argument("--out", help=out_help)
    ap.add_argument("--check", action="store_true", help="run the tool's check and print one CHECK line; exit 1 on failure")
    return ap


def wsx_files(data_dir):
    """All *.WSX / *.wsx files of a folder, sorted case-insensitively."""
    d = Path(data_dir)
    return sorted({p for p in d.iterdir() if p.suffix.lower() == ".wsx"}, key=lambda p: p.name.upper())
