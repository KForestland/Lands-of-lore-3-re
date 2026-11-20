"""LoL3 WSX placement fields used by the level editor."""
from struct import unpack_from

from extract_wsx_entries import wsx_name_hash
from lol3_cli import wsx_files
from lol3_level_schematic import PLACEMENTS, map_geometry
from lol3_script_framing import level_map_entries

MARKER = "QWOD0.WSX"
ANCHOR = "Surface"
AXIS = "Z"
KINDS = {"P", "C", "I"}
PREFIX = {"type 3": "P", "type 16": "C", "item": "I"}


def levels(data):
    return sorted(stem for stem, _, _ in level_map_entries(data))


def archive(data, level):
    if level in levels(data):
        return next(path for path in wsx_files(data) if path.stem.upper() == level)
    raise ValueError(f"{level} is not an original level archive.")


def map_index(level, _original, rows):
    key = wsx_name_hash(f"LEVELS\\{level}\\{level}.MAP")
    matches = [i for i, (value, _, _) in enumerate(rows) if value == key]
    if len(matches) != 1:
        raise ValueError(f"{level} does not contain one original MAP entry.")
    return matches[0]


def fields(raw):
    vertices, surfaces, _, _, _ = map_geometry(raw)
    outline = [[vertices[point] for point in row] for row in surfaces]
    records = []
    for name, start, count_at, stride, _ in PLACEMENTS:
        if name in PREFIX:
            offset, = unpack_from("<I", raw, start)
            count, = unpack_from("<I", raw, count_at)
            records.extend((f"{PREFIX[name]}-{i + 1}", offset + i * stride) for i in range(count))
    return outline, records
