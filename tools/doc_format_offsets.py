#!/usr/bin/env python3
"""Check selected format-page offsets against the readers that decode them."""
from pathlib import Path
import re
import struct

from cli_errors import ReaderArgumentParser, run_cli
from doc_links import prose_lines
from extract_wsx_entries import parse_wsx_bytes
from lol3_map_spans import section1_listing
from lol3_map_writer import paths, waypoints
from lol3_save_header import HEADER_SIZE, parse_header
from walk_lmf_leaves import directory_text, lmf_groups

DOCS = Path(__file__).resolve().parents[1] / "docs"
NUMBER = re.compile(r"0x[0-9a-f]+|[0-9]+", re.I)


def offsets(cell):
    return tuple(int(token, 16 if token.lower().startswith("0x") else 10)
                 for token in NUMBER.findall(cell))


def documented(page, label_column, starts_with):
    lines = prose_lines((DOCS / page).read_text(encoding="utf-8"))
    rows = [tuple(cell.strip() for cell in line.strip().strip("|").split("|"))
            for line in lines if line.lstrip().startswith("|")]
    matches = [row for row in rows
               if len(row) > label_column and row[label_column].startswith(starts_with)]
    if len(matches) != 1:
        raise ValueError(f"{page}: expected one layout row for {starts_with}")
    observed = offsets(matches[0][0])
    if not observed:
        raise ValueError(f"{page}: {starts_with}: no documented offset")
    return observed[0]


def probe(page, field, offset, read):
    """Build a synthetic file around the documented offset and ask the reader
    for the field. A wrong offset on the page, or a reader that reads the
    field elsewhere, gives something other than the expected value."""
    try:
        result = read(offset)
    except (ValueError, IndexError, KeyError, struct.error) as error:
        result = f"error: {error}"
    if result is not True:
        raise ValueError(f"{page}: {field}: documented +{offset:#x}, but the reader does not read it there"
                         + (f" ({result})" if result is not False else ""))


def wsx_key(offset):
    raw = bytearray(18)
    struct.pack_into("<I", raw, offset, 0xA1B2C3D4)
    struct.pack_into("<HI", raw, 0, 1, 0)
    return parse_wsx_bytes(bytes(raw))["entries"][0]["hash"] == 0xA1B2C3D4


def lmf(field, offset):
    """One stored 0x40-byte group after a one-row directory at 0x100."""
    raw = bytearray(0x150)
    values = {0: 0, 4: 38, 8: 0x100, 0x0C: 0x110, 0x10: 16, 0x14: 0x40, 0x18: 1}
    for at, value in values.items():
        if at != field:
            struct.pack_into("<I", raw, at, value)
    struct.pack_into("<I", raw, offset, values[field])
    struct.pack_into("<4I", raw, 0x100, 0, 0x40, 0, 0x40)
    groups = list(lmf_groups(bytes(raw)))
    return [(group["offset"], group["packed"]) for group in groups] == [(0x110, 0x40)] and (
        "+8 0x100 +0xc 0x110 +0x10 0x10 +0x14 0x40 +0x18 1" in directory_text(bytes(raw), "probe"))


def map_section1(field):
    raw = bytearray(0x100)
    struct.pack_into("<I", raw, 4 + 4 * field, 0x80)
    struct.pack_into("<I", raw, 0x54, 1)
    struct.pack_into("<H", raw, 0x80, 0xBEEF)
    return "row 1: +0 0xbeef " in section1_listing(bytes(raw), "probe")


def map_rows(found):
    raw = bytearray(0x300)
    for count_at, start_at, row_at in ((found[0], found[1], 0x260), (found[2], found[3], 0x280)):
        struct.pack_into("<I", raw, count_at, 1)
        struct.pack_into("<I", raw, start_at, row_at)
    struct.pack_into("<hhHBB", raw, 0x260, -8, 6, 0xFFFF, 2, 5)
    struct.pack_into("<HBB", raw, 0x280, 7, 0xFF, 0x80)
    return (waypoints(raw) == (0x260, [(-8, 6, 0xFFFF, 2, 5)])
            and paths(raw) == (0x280, [(7, 0xFF, 0x80)]))


def save_globals(offset):
    header = bytearray(HEADER_SIZE)
    size = HEADER_SIZE + 0x100 + 18
    struct.pack_into("<3I", header, 0x2C, size, 38, 310)
    struct.pack_into("<3I", header, 0x39C, 1, 1, HEADER_SIZE)
    struct.pack_into("<18I", header, 0x5B0, *range(HEADER_SIZE + 0x100, size))
    struct.pack_into("<18I", header, 0x600, *([1] * 18))
    struct.pack_into("<61I", header, 0x4B8, *([HEADER_SIZE + 0x100] * 61))
    struct.pack_into("<61I", header, offset, *range(HEADER_SIZE + 1, HEADER_SIZE + 62))
    sections = parse_header(bytes(header), size)["sections"]
    return [start for start, _ in sections] == list(range(HEADER_SIZE + 1, HEADER_SIZE + 62))


def check():
    page = "formats/wsx.md"
    probe(page, "rows", documented(page, 2, "rows:"), wsx_key)
    page = "formats/lmf.md"
    probe(page, "directory offset", documented(page, 1, "Directory offset,"), lambda at: lmf(8, at))
    probe(page, "pool byte extent", documented(page, 1, "Pool byte extent"), lambda at: lmf(0x14, at))
    page = "formats/map-odf.md"
    probe(page, "start of section 1 (field index)", documented(page, 1, "start of section 1"), map_section1)
    text = (DOCS / page).read_text(encoding="utf-8")
    found = re.search(r"dwords at (\+0x[0-9a-f]+/\+0x[0-9a-f]+) and (\+0x[0-9a-f]+/\+0x[0-9a-f]+)", text, re.I)
    if not found:
        raise ValueError(f"{page}: waypoint and path header fields not found")
    pairs = offsets(" ".join(found.groups()))
    try:
        agrees = len(pairs) == 4 and map_rows(pairs)
    except (ValueError, IndexError, struct.error):
        agrees = False
    if not agrees:
        raise ValueError(f"{page}: waypoint and path header fields " + ", ".join(f"+{v:#x}" for v in pairs)
                         + " are not where lol3_map_writer reads them")
    page = "lol3-native-saves.md"
    probe(page, "global save directory", documented(page, 1, "61 u32 absolute offsets"), save_globals)
    print("CHECK format offsets: six documented WSX, LMF, MAP and save fields are where the readers read them")

def main():
    parser = ReaderArgumentParser(description=__doc__)
    parser.add_argument("--data", help="accepted for check_all compatibility")
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    check()
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
