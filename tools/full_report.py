#!/usr/bin/env python3
"""Write a file inventory, level sheets and text counts for a local game copy."""
import csv
import os
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

from cli_errors import ReaderArgumentParser, run_cli
from lol3_cache_seed import shipped_body_covers
from lol3_media_check import TRR_AT, localized_trr, trr_directory, wsx_rows
from lol3_pht import pht_covers


def inventory(data):
    rows = []
    for path in sorted(data.iterdir()):
        if not path.is_file():
            continue
        kind = path.suffix.lower()
        reader, result = "", "open"
        if kind == ".wsx":
            reader = "lol3_media_check.wsx_rows"
            try:
                with path.open("rb") as source:
                    wsx_rows(source)
            except (ValueError, struct.error):
                if path.name.lower() == "cdcache.wsx" and shipped_body_covers(path):
                    reader, result = "lol3_cache_seed.shipped_body_covers", "repeated block"
            else:
                result = "complete"
        elif kind == ".pht":
            reader = "lol3_pht.pht_covers"
            if pht_covers(path):
                result = "repeated block"
        rows.append((path.name, path.stat().st_size, reader, result))
    return rows


def text_counts(data):
    path, tables = localized_trr(data, TRR_AT)
    return [(path.name, name, len(trr_directory(blob, name)[0])) for name, blob in tables.items()]


def write_tsv(path, headings, rows):
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output, delimiter="\t", lineterminator="\n")
        writer.writerow(headings)
        writer.writerows(rows)


def main():
    parser = ReaderArgumentParser(description=__doc__)
    default_data = os.environ.get("LOL3_DAT")
    parser.add_argument("--data", type=Path, default=default_data, required=default_data is None,
                        help="the game's DAT folder (default: $LOL3_DAT)")
    parser.add_argument("--out", type=Path, required=True, help="report folder outside the game and repository")
    args = parser.parse_args()
    data = args.data.resolve()
    out = args.out.resolve()
    repository = Path(__file__).resolve().parents[1]
    if any(out == root or root in out.parents for root in (repository, data.parent)):
        parser.error("--out must be outside the game and repository")
    out.mkdir(parents=True, exist_ok=True)
    names = ("inventory.tsv", "text-counts.tsv", "levels")
    # Keep a failed level read from publishing a half-written report.
    with tempfile.TemporaryDirectory(dir=out, prefix=".report-") as staging:
        occupied = [name for name in names if (out / name).exists() or (out / name).is_symlink()]
        if occupied:
            raise ValueError(f"output already contains {', '.join(occupied)}")
        report = Path(staging)
        files = inventory(data)
        text = text_counts(data)
        level_reader = Path(__file__).with_name("lol3_level_report.py")
        result = subprocess.run([sys.executable, str(level_reader), "--data", str(data),
                                 "--out", str(report / "levels")], capture_output=True, text=True)
        if result.returncode:
            raise ValueError((result.stderr or result.stdout).strip() or "level reader failed")
        levels = len(list((report / "levels").glob("*.md"))) - 1  # Exclude the index.
        if levels < 1:
            raise ValueError("no level sheets were generated")
        write_tsv(report / names[0], ("file", "bytes", "reader", "result"), files)
        write_tsv(report / names[1], ("source", "table", "records"), text)
        for name in ("levels", *names[:2]):
            (report / name).rename(out / name)
    print(f"wrote {len(files)} inventory rows, {levels} level sheets and {len(text)} text counts to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
