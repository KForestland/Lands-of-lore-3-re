"""LoL3 WSX placement fields used by the level editor."""
from functools import lru_cache
from struct import unpack_from

from extract_wsx_entries import wsx_name_hash
from lol3_cli import wsx_files
from lol3_media_check import read_at, wsx_rows
from lol3_text_writer import read_trr
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


def entry(data, archive_name, *, key):
    files = (path for path in wsx_files(data) if path.name.upper() == archive_name)
    for path in files:
        with path.open("rb") as archive:
            for current, at, size in wsx_rows(archive):
                if current == key:
                    return read_at(archive, at, size)
    return None


def item_catalogue(data):
    odf = entry(data, "GLOBAL.WSX", key=wsx_name_hash("GLOBAL\\GLOBAL.ODF"))
    trr = entry(data, "LOCALLNG.WSX", key=wsx_name_hash("itemjt.trr"))
    if odf is None:
        return
    names = {key: value[4:].split(b"\x02", 1)[0].decode("cp437").strip()
             for key, value in read_trr(trr)} if trr is not None else {}
    start, = unpack_from("<I", odf, 4)
    count, = unpack_from("<I", odf, 0x34)
    for index in range(count):
        at = start + 139 * index
        identity, = unpack_from("<I", odf, at + 0x18)
        text_key, = unpack_from("<I", odf, at + 0x73)
        yield identity, text_key, names.get(text_key), odf[at + 0x3F]


@lru_cache(maxsize=1)
def item_names(data):
    return {identity: title or f"Item definition {index}"
            for index, (identity, _, title, _) in enumerate(item_catalogue(data))}


def placement_name(data, raw, kind, row, at):
    if kind == "item":
        identity, = unpack_from("<I", raw, at + 0x20)
        label = item_names(data).get(identity, f"Item identity {identity:#010x}")
    elif kind in ("type 3", "type 16"):
        definition, = unpack_from("<H" if kind == "type 3" else "<B", raw, at + 0x20)
        label = f"Prop {kind} · definition {definition}"
    else:
        return None
    return f"{label} · row {row}"
