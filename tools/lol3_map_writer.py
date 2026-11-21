#!/usr/bin/env python3
"""Read the 18 level MAP entries in the WSX archives and the opcode sizes in LOL3.DAT, and rebuild each MAP in memory.

  lol3_map_writer.py --data DAT --check         # all 18 MAPs
  lol3_map_writer.py --data DAT --list CKEEP    # copied spans: offsets, sizes, SHA-256

The check regenerates the typed header, geometry, event and placement
fields described in docs/lol3-map-odf-readers.md. It also verifies every
retained range and changes a few fields in memory to test read-back.
--list reports four named copied spans. --coverage reports every copied
byte by range, using offsets in both the MAP and the containing WSX.
Neither option prints stored bytes or writes files.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import re
import struct

from cli_errors import run_cli, game_path
import lol3_cli
from lol3_level_schematic import PLACEMENTS, map_geometry
from lol3_native_checks import opcode
from lol3_script_framing import level_map_entries, native_sizes, u32
from lol3_script_notes import STREAMS, walk

WAYPOINT = struct.Struct("<hhHBB")
PATH = struct.Struct("<HBB")
# Fields after the opcode, selector and index. "s" fields and the bytes after
# the listed fields are carried in order as unclassified storage.
COMMAND_FORMATS = {
    0x01: "B", 0x02: "BB", 0x03: "IIB", 0x05: "BB", 0x06: "BB",
    0x07: "BB", 0x09: "BB", 0x0B: "H", 0x0D: "B", 0x0E: "BBB",
    0x0F: "BBH", 0x10: "B", 0x11: "b", 0x12: "6sH",
    0x13: "HHBB", 0x14: "H", 0x15: "BB", 0x16: "I4s", 0x17: "B",
    0x18: "H", 0x19: "III", 0x1A: "IIII", 0x1B: "IBB",
    0xC4: "h", 0xC5: "B", 0xC6: "BB", 0xC7: "BB", 0xC8: "BB",
    0xC9: "BB", 0xCC: "hH", 0xCE: "Bb", 0xCF: "Bb", 0xD0: "BBB",
    0xD1: "hhh", 0xD2: "BB", 0xF0: "B",
}
# Each loader reads one stored row into a stack buffer (0x4357A0) and its
# constructor calls 0x4411F0 with that buffer.
PLACEMENT_BASE = "hhHh2shHHI8sB1sB1s"
PLACEMENT_TAILS = {
    "type 3": "HBBB",           # 0x44FBC2–0x44FC28
    "type 16": "B",             # 0x4698E7
    "creature": "B23s",         # 0x4B4579: dword load, low byte kept
    "mover (type 32)": "9B",    # 0x4698E7 and 0x4D591B–0x4D5994
    "item": "IB",               # 0x4D7390–0x4D73A2
}


# (seek field, count field, row layout). Storage marked "s" is carried
# without assigning its component fields a width or meaning. Only fields
# with a native read of the stored value are typed: region byte +0x16
# (only cleared at 0x4F5A8C), byte +9 of the +0x48 rows (cleared on load
# at 0x46C5E8) and header +0xCC (no loader read) stay retained.
TABLES = {
    "vertices": (0x04, 0x50, "ii"),                          # 0x4F01E0
    "section 1": (0x08, 0x54, "h6B"),                       # 0x4EFDC0, 0x4E6425
    "surfaces": (0x0C, 0x58, "4sI8HhhHH4B6sHB4s7B"),      # 0x4A65F0, 0x4F6010
    "section +0x34": (0x34, 0x7C, "HHHBB"),                 # 0x4E73FA, 0x4EFED1, 0x4F0126
    "section +0x30": (0x30, 0x78, "HH"),                    # 0x4EFF14, 0x4EFF21
    "section +0x2C": (0x2C, 0x74, "4sH1sBB3s"),            # 0x4EFAF0–0x4EFB3C
    "region descriptors": (0xA4, 0xAC, "I3H4sHH8s2B"),     # 0x4E737A, 0x4E7934, 0x4E7787
    "predicates": (0xBC, 0xB8, "5B"),                       # 0x4F0240, 0x4F02B0
    "level bytes": (0xB4, 0xB0, "B"),                       # 0x440A20
    "section +0x48": (0x48, 0x90, "8sB3s"),                 # 0x46C5E3, 0x46C61A
}
# Tuple index, stored offset and byte width for the fields changed by --check.
SURFACE_EDITS = ((15, 0x21, 1), (17, 0x23, 1), (19, 0x2A, 2),
                 (20, 0x2C, 1), (22, 0x31, 1), (24, 0x33, 1))
HEADER_WORDS = tuple(sorted({
    0, 0x28, 0x2C, 0x30, 0x34, 0x74, 0x78, 0x7C, 0x4C, 0x98,
    0xC4, 0xC8, 0xD8, 0xDC,
    *(at for seek, count, _ in TABLES.values() for at in (seek, count)),
    *(at for stream in STREAMS.values() for at in stream),
    *(at for _, seek, count, _, _ in PLACEMENTS for at in (seek, count)),
}))

# Values consumed by the native event matchers after length and kind.
# The matching reference at +2 is a stream offset for regions and index
# for objects. Kind 19 uses this word as a guard index.
EVENT_FORMATS = {
    0: "", 1: "H2sHHB1sb1sbB", 2: "HBB2sH", 3: "HB", 4: "HB",
    5: "HBB", 6: "HBB", 7: "HBB", 8: "HH", 9: "HHHBB", 10: "HBBH",
    11: "HHB", 12: "HHBB", 15: "HHBBH", 19: "H", 21: "HB", 22: "H",
}


def field_bytes(fmt):
    """Bytes of a struct format that are named fields (not "s" storage)."""
    return sum(end - start for start, end in format_ranges(fmt))


def read_command(raw):
    opcode, selector, index = struct.unpack_from("<BBH", raw)
    layout = struct.Struct("<" + COMMAND_FORMATS.get(opcode, ""))
    return dict(opcode=opcode, selector=selector, index=index,
                operands=layout.unpack_from(raw, 4), tail=bytes(raw[4 + layout.size:]))


def write_command(command, lengths):
    opcode = command["opcode"]
    body = struct.pack("<BBH", opcode, command["selector"], command["index"])
    body += struct.pack("<" + COMMAND_FORMATS.get(opcode, ""), *command["operands"])
    body += command["tail"]
    if len(body) != lengths[opcode]:
        raise ValueError(f"command {opcode:#x} has wrong length")
    return body


def read_rows(raw, location, count, layout):
    start, size = u32(raw, location), layout.size * u32(raw, count)
    if size and (start < 0x244 or start + size > len(raw)):
        raise ValueError(f"row array at MAP+{location:#x} exceeds the payload")
    return start, list(layout.iter_unpack(raw[start:start + size]))


def waypoints(raw):
    return read_rows(raw, 0xC8, 0xC4, WAYPOINT)


def paths(raw):
    return read_rows(raw, 0xDC, 0xD8, PATH)


def write_rows(rows, layout):
    return b"".join(layout.pack(*row) for row in rows)


def placement_layout(name):
    return struct.Struct("<" + PLACEMENT_BASE + PLACEMENT_TAILS[name])


def retained_spans(raw):
    """The spans copied as stored bytes: shared block, both label ranges, gap."""
    wp_count, wp_at = struct.unpack_from("<II", raw, 0xC4)
    path_count, path_at = struct.unpack_from("<II", raw, 0xD8)
    shared_at, shared_end = u32(raw, 0xCC), u32(raw, 4)
    surface_end = u32(raw, 0x0C) + 56 * u32(raw, 0x58)
    if (path_at != wp_at + 34 * wp_count or
            u32(raw, 8) != path_at + 35 * path_count or
            not 0x244 <= shared_at <= shared_end <= wp_at <= path_at <= len(raw) or
            not surface_end <= u32(raw, 0x44) <= len(raw)):
        raise ValueError("MAP retained ranges disagree with the header")
    return [
        ("shared block", shared_at, raw[shared_at:shared_end]),
        ("waypoint labels", wp_at + 8 * wp_count, raw[wp_at + 8 * wp_count:path_at]),
        ("path labels", path_at + 4 * path_count, raw[path_at + 4 * path_count:u32(raw, 8)]),
        ("surface-to-script gap", surface_end, raw[surface_end:u32(raw, 0x44)]),
    ]


def check_tail_layout(raw):
    """Verify the stored tail's label and annotation slots without typing them."""
    start = u32(raw, 0xC0)
    label_row = struct.Struct("<5x40s")
    annotation_row = struct.Struct("<16x100s")
    labels_end = start + 256 * label_row.size
    notes_start = labels_end + 55
    notes_end = len(raw) - 17
    if start < 0x244 or notes_start > notes_end or (notes_end - notes_start) % annotation_row.size:
        raise ValueError("MAP +0xC0 tail does not fit the label and annotation rows")
    label_count = 0
    for (slot,) in label_row.iter_unpack(raw[start:labels_end]):
        label, terminator, _ = slot.partition(b"\0")
        if not terminator or not all(32 <= value < 127 for value in label):
            raise ValueError("MAP +0xC0 label is not a terminated printable string")
        label_count += bool(label)
    for (slot,) in annotation_row.iter_unpack(raw[notes_start:notes_end]):
        note, terminator, _ = slot.partition(b"\0")
        if not note or not terminator or not all(32 <= value < 127 for value in note):
            raise ValueError("MAP +0xC0 annotation is not a terminated printable string")
    return label_count, (notes_end - notes_start) // annotation_row.size


def check_region_surfaces(raw):
    """Check the region runs against each surface's reverse region index."""
    at = u32(raw, 0xA4)
    region_count = u32(raw, 0xAC)
    surface_at = u32(raw, 0x0C)
    surface_count = u32(raw, 0x58)
    seen_surfaces = 0
    for index in range(region_count):
        row = at + 28 * index
        first, = struct.unpack_from("<H", raw, row + 4)
        count = raw[row + 0x1A]
        if not count or first + count > surface_count:
            raise ValueError(f"Region {index} has an invalid surface run")
        for surface in range(first, first + count):
            owner, = struct.unpack_from("<H", raw, surface_at + 56 * surface + 0x1C)
            if owner != index:
                raise ValueError(f"Surface {surface} does not point back to region {index}")
        seen_surfaces += count
    if seen_surfaces != surface_count:
        raise ValueError("Region runs do not cover all MAP surfaces")


def surface_storage_counts(raw):
    """Count retained +0x30 bytes against the stored surface flag at +4."""
    start, count = u32(raw, 0x0C), u32(raw, 0x58)
    return Counter((bool(u32(raw, at + 4) & 0x200), raw[at + 0x30])
                   for at in range(start, start + 56 * count, 56))


def event_fields(raw, start, end):
    at = start
    while at < end:
        length, kind = struct.unpack_from("<BB", raw, at)
        if kind not in EVENT_FORMATS or at + length > end:
            raise ValueError(f"invalid event at MAP+{at:#x}")
        fmt = "BB" + EVENT_FORMATS[kind]
        if kind == 22:
            stop = raw.find(b"\0", at + 4, at + length)
            if stop < 0:
                raise ValueError(f"unterminated audio name at MAP+{at:#x}")
            fmt += f"{stop - at - 3}c"
        tail = length - struct.calcsize("<" + fmt)
        if tail < 0:
            raise ValueError(f"truncated event at MAP+{at:#x}")
        if tail:
            fmt += f"{tail}s"
        yield at, fmt, struct.unpack_from("<" + fmt, raw, at)
        at += length


def format_ranges(fmt):
    """Get the row-relative ranges that are regenerated from typed fields."""
    pos = start = 0
    for count, code in re.findall(r"(\d*)(.)", fmt):
        size = struct.calcsize("<" + count + code)
        if code == "s":
            if pos > start:
                yield start, pos
            start = pos + size
        pos += size
    if pos > start:
        yield start, pos


def parsed_ranges(fields):
    for at in fields["header"]:
        yield at, at + 4
    for entries in fields["events"].values():
        for at, fmt, _ in entries:
            for lo, hi in format_ranges(fmt):
                yield at + lo, at + hi
    for start, fmt, rows in fields["tables"].values():
        size = struct.calcsize("<" + fmt)
        ranges = tuple(format_ranges(fmt))
        if ranges == ((0, size),):
            yield start, start + size * len(rows)
            continue
        for i in range(len(rows)):
            at = start + i * size
            for lo, hi in ranges:
                yield at + lo, at + hi
    for layout, key in ((WAYPOINT, "waypoints"), (PATH, "paths")):
        start, rows = fields[key]
        yield start, start + layout.size * len(rows)
    for name, _, _, stride, _ in PLACEMENTS:
        start, rows = fields["placements"][name]
        spans = tuple(format_ranges(PLACEMENT_BASE + PLACEMENT_TAILS[name]))
        for i in range(len(rows)):
            at = start + i * stride
            for lo, hi in spans:
                yield at + lo, at + hi
    for start, rows in fields["commands"].values():
        at = start
        for row in rows:
            fmt = "BBH" + COMMAND_FORMATS.get(row["opcode"], "")
            for lo, hi in format_ranges(fmt):
                yield at + lo, at + hi
            at += struct.calcsize("<" + fmt) + len(row["tail"])


def retained_ranges(total, fields):
    """Yield end-exclusive gaps in the parsed ranges, rejecting overlaps."""
    at = 0
    for start, end in sorted(parsed_ranges(fields)):
        if start == end:
            continue
        if start < at or end > total:
            raise ValueError(f"typed field overlaps or crosses the MAP at +{start:#x}")
        if start > at:
            yield at, start
        at = end
    if at < total:
        yield at, total


def read_fields(raw, lengths):
    """Parse typed fields and retain the remaining storage at its source offset."""
    fields = {"commands": {}, "placements": {}, "events": {}, "tables": {},
              "header": {at: u32(raw, at) for at in HEADER_WORDS}}
    for name, (location, count, fmt) in TABLES.items():
        start, rows = read_rows(raw, location, count, struct.Struct("<" + fmt))
        fields["tables"][name] = start, fmt, rows
    start = u32(raw, 0x28)
    if start:
        fmt = "12sIIII396sh110s"
        row = struct.unpack_from("<" + fmt, raw, start)
        fields["tables"]["section +0x28"] = start, fmt, [row]
    start, size = u32(raw, 0x4C), u32(raw, 0x98)
    fields["tables"]["object command index"] = start, "I", list(
        struct.iter_unpack("<I", raw[start:start + size]))
    for space, (location, _, events, event_size) in STREAMS.items():
        at, size = u32(raw, events), u32(raw, event_size)
        fields["events"][space] = list(event_fields(raw, at, at + size))
        stream, starts, _, _, _, _ = walk(raw, 0, space, lengths)
        fields["commands"][space] = (u32(raw, location), [
            read_command(stream[start:start + lengths[stream[start]]]) for start in starts])
    fields["waypoints"] = waypoints(raw)
    fields["paths"] = paths(raw)
    for name, location, count, stride, _ in PLACEMENTS:
        layout = placement_layout(name)
        if layout.size != stride:
            raise ValueError(f"{name} placement layout differs from its native stride")
        fields["placements"][name] = read_rows(raw, location, count, layout)
    return fields


def emit(raw, fields, lengths):
    """Write the fields over the original; every other byte is copied."""
    spans = list(retained_spans(raw))
    for at, value in fields["header"].items():
        spans.append(("header", at, struct.pack("<I", value)))
    for name, (start, fmt, rows) in fields["tables"].items():
        spans.append((name, start, write_rows(rows, struct.Struct("<" + fmt))))
    for name, entries in fields["events"].items():
        if entries:
            spans.append((name + " events", entries[0][0], b"".join(
                struct.pack("<" + fmt, *row) for _, fmt, row in entries)))
    for space, (start, rows) in fields["commands"].items():
        spans.append((space + " commands", start, b"".join(write_command(row, lengths) for row in rows)))
    spans.append(("waypoints", fields["waypoints"][0], write_rows(fields["waypoints"][1], WAYPOINT)))
    spans.append(("paths", fields["paths"][0], write_rows(fields["paths"][1], PATH)))
    for name, _, _, stride, _ in PLACEMENTS:
        start, rows = fields["placements"][name]
        spans.append((name, start, write_rows(rows, placement_layout(name))))
    out = bytearray()
    for _, start, body in sorted((span for span in spans if span[2]), key=lambda span: span[1]):
        if start < len(out) or start + len(body) > len(raw):
            raise ValueError(f"overlapping or truncated MAP span at +{start:#x}")
        out.extend(raw[len(out):start])
        out.extend(body)
    out.extend(raw[len(out):])
    return bytes(out)


def rebuild(raw, lengths):
    fields = read_fields(raw, lengths)
    counts, observed = Counter(), set()
    for space, (_, rows) in fields["commands"].items():
        counts[space + " commands"] += len(rows)
        observed.update(row["opcode"] for row in rows)
    counts["waypoints"], counts["paths"] = len(fields["waypoints"][1]), len(fields["paths"][1])
    counts["placements"] = sum(len(rows) for _, rows in fields["placements"].values())
    counts.update({name: len(rows) for name, (_, _, rows) in fields["tables"].items()})
    counts["events"] = sum(len(rows) for rows in fields["events"].values())
    counts["field bytes"] = len(raw) - sum(hi - lo for lo, hi in retained_ranges(len(raw), fields))
    return emit(raw, fields, lengths), counts, observed


def edit_check(raw, lengths):
    """Change a command, waypoint, vertex, surface and two placements, then verify the readers see them."""
    fields = read_fields(raw, lengths)
    stream_at, commands = fields["commands"]["object"]
    target = next((n for n, row in enumerate(commands)
                   if row["opcode"] == 0x0E), None)
    if target is None:
        return False
    offset = sum(lengths[row["opcode"]] for row in commands[:target])
    operands = list(commands[target]["operands"])
    operands[0] ^= 1
    commands[target]["operands"] = tuple(operands)
    wp_at, points = fields["waypoints"]
    points[0] = (points[0][0] + 1,) + points[0][1:]
    creature_at, creatures = fields["placements"]["creature"]
    creatures[0] = (creatures[0][0], creatures[0][1] + 1) + creatures[0][2:]
    vertex_at, _, vertices = fields["tables"]["vertices"]
    x, z = vertices[0]
    vertices[0] = (x + 0x10000, z)
    surface_at, _, surfaces = fields["tables"]["surfaces"]
    surface = list(surfaces[0])
    for index, _, width in SURFACE_EDITS:
        surface[index] ^= 0x0101 if width == 2 else 1
    surfaces[0] = tuple(surface)
    item_at, items = fields["placements"]["item"]
    identity = items[0][-2] ^ 1 if items else None  # u32 +0x20
    if items:
        items[0] = items[0][:-2] + (identity, items[0][-1])
    changed = emit(raw, fields, lengths)
    command_at = stream_at + offset + 4
    differ = [at for at in range(len(raw)) if raw[at] != changed[at]]
    expected = {command_at, wp_at, wp_at + 1, creature_at + 2, creature_at + 3,
                vertex_at + 2, vertex_at + 3, item_at + 0x20}
    surface_offsets = {surface_at + at + byte for _, at, width in SURFACE_EDITS
                       for byte in range(width)}
    if len(changed) != len(raw) or not surface_offsets <= set(differ) <= expected | surface_offsets:
        raise ValueError(f"edit changed bytes outside the edited fields: {[hex(at) for at in differ[:8]]}")
    stream, starts, _, _, _, _ = walk(changed, 0, "object", lengths)
    old_vertices, _, old_points, _, old_placed = map_geometry(raw)
    new_vertices, _, new_points, _, new_placed = map_geometry(changed)
    old_creature = next(row for row in old_placed if row[0] == "creature")
    new_creature = next(row for row in new_placed if row[0] == "creature")
    if (read_command(stream[starts[target]:])["operands"][0] != operands[0] or
            new_vertices[0][0] != old_vertices[0][0] + (1 << 16) or
            new_points[0][0] != old_points[0][0] + (1 << 16) or
            new_creature[3] != old_creature[3] + (1 << 16)):
        raise ValueError("an edited field does not read back through the existing readers")
    again = read_fields(changed, lengths)
    if (again["tables"]["surfaces"][2][0] != surfaces[0] or
            (items and again["placements"]["item"][1][0][-2] != identity)):
        raise ValueError("an edited field does not read back through the existing readers")
    return True


def check(data):
    image = game_path(data.resolve().parent, "LOL3.DAT").read_bytes()
    sizes = native_sizes(image)
    if len(sizes) != 39:
        raise ValueError("expected 39 native opcode lengths")
    for address, encoding in (
        (0x4F6178, "8a 41 21 88 46 40"), (0x4F627D, "8a 51 23 88 96 82 00 00 00"),
        (0x4FB34A, "8a 41 2c 8b d0 0f bf 41 18 2b c2"),
        (0x4A70FB, "8a 4e 31 84 c8"), (0x4F7059, "8a 51 33 81 ea 80 00 00 00"),
        (0x4A66CF, "66 89 59 04 66 89 59 06"),
        (0x4E7934, "66 8b 41 04"), (0x4E794C, "8a 41 1a"),
        (0x4E7787, "66 8b 4c 95 10 8b 54 24 2c 3b ca"),
    ):
        opcode(image, address, encoding)
    counts, seen, maps, total, edited = Counter(), set(), 0, 0, False
    labels, annotations = 0, 0
    surface_bytes = Counter()
    for stem, _, raw in level_map_entries(data):
        label_count, note_count = check_tail_layout(raw)
        labels += label_count
        annotations += note_count
        rebuilt, totals, opcodes = rebuild(raw, sizes)
        check_region_surfaces(raw)
        surface_bytes.update(surface_storage_counts(raw))
        if rebuilt != raw:
            raise ValueError(f"{stem}: rebuilt MAP differs")
        counts.update(totals)
        seen.update(opcodes)
        maps += 1
        total += len(raw)
        if not edited:
            edited = edit_check(raw, sizes)
    if maps != 18:
        raise ValueError(f"expected 18 shipped MAPs, read {maps}")
    if not edited:
        raise ValueError("no MAP held an opcode 0x0E command for the edit check")
    if (labels, annotations) != (1542, 3429):
        raise ValueError(f"expected 1,542 tail labels and 3,429 annotations, read {labels:,} and {annotations:,}")
    nonzero = {value: count for (flag, value), count in surface_bytes.items() if flag and value}
    if (set(nonzero) != set(range(2, 17)) or sum(nonzero.values()) != 1182
            or sum(count for (flag, value), count in surface_bytes.items() if not flag and value)
            or surface_bytes[True, 0] != 103783 or surface_bytes[False, 0] != 13986):
        raise ValueError("stored surface +0x30 census or its relation to flag 0x200 differs")
    regenerated = counts.pop("field bytes")
    print(f"CHECK MAP write: {maps} byte-identical MAPs, {len(seen)}/{len(sizes)} opcodes stored; " +
          ", ".join(f"{value:,} {name}" for name, value in counts.items()) +
          f"; {regenerated:,} of {total:,} bytes from parsed fields, {total - regenerated:,} copied; "
          "command, waypoint, vertex, surface and placement edits read back; "
          f"region surface runs agree; retained tails frame {labels:,} names and {annotations:,} annotations; "
          "1,182 nonzero retained surface +0x30 values, all with flag 0x200")


def main():
    parser = lol3_cli.tool_args(__doc__, writes=False)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--list", metavar="STEM", help="list the four named copied spans")
    mode.add_argument("--coverage", metavar="STEM", help="list every copied range and its size")
    args = parser.parse_args()
    data = Path(args.data)
    if args.check:
        check(data)
    elif args.list or args.coverage:
        target = (args.list or args.coverage).upper()
        for stem, base, raw in level_map_entries(data):
            if stem != target:
                continue
            if args.coverage:
                sizes = native_sizes(game_path(data.resolve().parent, "LOL3.DAT").read_bytes())
                fields = read_fields(raw, sizes)
                copied = 0
                for lo, hi in retained_ranges(len(raw), fields):
                    print(f"{stem}.WSX+{base + lo:#x}..+{base + hi:#x} "
                          f"MAP+{lo:#x}..+{hi:#x} size={hi - lo} (end exclusive)")
                    copied += hi - lo
                print(f"{stem}: {copied:,} retained bytes, {len(raw) - copied:,} typed bytes")
            else:
                for name, start, body in retained_spans(raw):
                    print(f"{stem}.WSX+{base + start:#x} MAP+{start:#x} {name} "
                          f"size={len(body)} sha256={sha256(body).hexdigest()}")
            return 0
        raise ValueError(f"unknown level {target}")
    else:
        parser.error("give --check, --list STEM or --coverage STEM")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
