#!/usr/bin/env python3
"""Edit LoL3 text and original item, spell and creature definition fields."""
from pathlib import Path
from struct import error as StructError, unpack_from
import sys

from cli_errors import run_cli
from extract_wsx_entries import parse_wsx_bytes, wsx_name_hash
from lol3_text_writer import read_trr, write_trr
from lol3_wsx_writer import relayout, write_wsx
import modkit_core as core

GAME = "lol3"
FOLDER = "the LoL3 game folder holding LOL3.DAT and DAT, or its DAT folder"
DATA_ENV = "LOL3_DAT"
ITEMS_KEY = wsx_name_hash("GLOBAL\\GLOBAL.ODF")
SPELLS_KEY = wsx_name_hash("GLOBAL\\SPELL.ODF")
ITEM = (("special_cast_cost", 0x5B, "I"), ("step_input", 0x7D, "H"))
SPELL = (("frame_count", 0x2E, "B"),)
CREATURE = (("health_cap", 0x63, "H"), ("attack_input", 0x81, "B"))


def sources(root):
    return core.game_files(root, {".WSX", ".TRR"})


def is_loose(name):
    return name.upper().endswith(".TRR")


def members(raw):
    rows = parse_wsx_bytes(raw)["entries"]
    return [(row["hash"], row["offset"], row["blob"])
            for row in sorted(rows, key=lambda row: row["index"])]


def repack(rows, previous, _size):
    base = 6 + 12 * len(rows)
    relative = [(key, at - base, blob) for key, at, blob in rows]
    return write_wsx(relayout(relative) if rows is not previous else relative)


def layout(name, key, blob):
    stem = Path(name).stem.upper()
    if stem == "GLOBAL" and key == ITEMS_KEY:
        return "items", (unpack_from("<I", blob, 4)[0], unpack_from("<I", blob, 0x34)[0], 139, ITEM)
    if stem == "GLOBAL" and key == SPELLS_KEY:
        start, count = unpack_from("<II", blob, 4)
        return "spells", (start, count, 87, SPELL)
    if key == wsx_name_hash(f"LEVELS\\{stem}\\{stem}.ODF"):
        return "creatures", (unpack_from("<I", blob, 0x10)[0], unpack_from("<I", blob, 0x48)[0], 147, CREATURE)
    return None


def view(name, key, blob):
    table = layout(name, key, blob)
    if table:
        kind, fields = table
        return kind, core.number_view(blob, *fields)
    if len(blob) >= 16 and 0 < unpack_from("<I", blob)[0] <= (len(blob) - 8) // 8:
        try:
            rows = read_trr(blob)
            if write_trr(rows) == blob:
                return "text", core.text_view(rows)
        except (ValueError, StructError):
            if is_loose(name):
                raise
    return None


def encode(name, key, blob, kind, value):
    if kind == "text":
        return write_trr(core.text_rows(read_trr(blob), value))
    _, fields = layout(name, key, blob)
    return core.number_write(blob, *fields, value)


if __name__ == "__main__":
    raise SystemExit(run_cli(core.main, sys.modules[__name__]))
