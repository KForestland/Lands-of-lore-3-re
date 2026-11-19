#!/usr/bin/env python3
"""Read the 18 level MAP entries in the WSX archives and the opcode sizes in LOL3.DAT, and rebuild each MAP in memory.

  lol3_map_writer.py --data DAT --check         # all 18 MAPs
  lol3_map_writer.py --data DAT --list CKEEP    # copied spans: offsets, sizes, SHA-256

The check regenerates from parsed fields: the opcode, selector, index and
typed operands of every region and object command, the 8-byte waypoint rows,
the 4-byte path rows, the X/Z words of every placement and the mover's eight
state bytes. Everything else is copied as stored bytes: command operand
bytes without a field name, the other placement bytes, the shared block,
the waypoint and path labels, the surface-to-script gap and every MAP table
this tool does not parse. The CHECK line gives both byte totals. The check
then changes one command operand, one waypoint and one placement in memory
and requires the existing readers to read the new values back.
--list prints offsets, sizes and hashes only, never the bytes. Nothing is
written.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import re
import struct

from cli_errors import run_cli
import lol3_cli
from lol3_level_schematic import PLACEMENTS, map_geometry
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
MOVER = 0x29


def field_bytes(fmt):
    """Bytes of a struct format that are named fields (not "s" storage)."""
    stored = sum(int(count or 1) for count in re.findall(r"(\d*)s", fmt))
    return struct.calcsize("<" + fmt) - stored


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


def placement_layout(stride):
    # Coordinates at +0/+2. The mover also has eight typed state bytes at
    # +0x21. The other per-class bytes are copied at their offsets.
    return struct.Struct("<hh29s8B" if stride == MOVER else f"<hh{stride - 4}s")


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


def read_fields(raw, lengths):
    """Parse the writable fields: commands per stream, waypoints, paths, placements."""
    fields = {"commands": {}, "placements": {}}
    for space, (location, _, _, _) in STREAMS.items():
        stream, starts, _, _, _, _ = walk(raw, 0, space, lengths)
        fields["commands"][space] = (u32(raw, location), [
            read_command(stream[start:start + lengths[stream[start]]]) for start in starts])
    fields["waypoints"] = waypoints(raw)
    fields["paths"] = paths(raw)
    for name, location, count, stride, _ in PLACEMENTS:
        fields["placements"][name] = read_rows(raw, location, count, placement_layout(stride))
    return fields


def emit(raw, fields, lengths):
    """Write the fields over the original; every other byte is copied."""
    spans = list(retained_spans(raw))
    for space, (start, rows) in fields["commands"].items():
        spans.append((space + " commands", start, b"".join(write_command(row, lengths) for row in rows)))
    spans.append(("waypoints", fields["waypoints"][0], write_rows(fields["waypoints"][1], WAYPOINT)))
    spans.append(("paths", fields["paths"][0], write_rows(fields["paths"][1], PATH)))
    for name, _, _, stride, _ in PLACEMENTS:
        start, rows = fields["placements"][name]
        spans.append((name, start, write_rows(rows, placement_layout(stride))))
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
        counts["field bytes"] += sum(4 + field_bytes(COMMAND_FORMATS.get(row["opcode"], "")) for row in rows)
    counts["waypoints"], counts["paths"] = len(fields["waypoints"][1]), len(fields["paths"][1])
    counts["field bytes"] += WAYPOINT.size * counts["waypoints"] + PATH.size * counts["paths"]
    for name, _, _, stride, _ in PLACEMENTS:
        rows = fields["placements"][name][1]
        counts["placements"] += len(rows)
        counts["field bytes"] += (12 if stride == MOVER else 4) * len(rows)
    return emit(raw, fields, lengths), counts, observed


def edit_check(raw, lengths):
    """Change one command operand, one waypoint and one placement; the readers must see them."""
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
    changed = emit(raw, fields, lengths)
    command_at = stream_at + offset + 4
    differ = [at for at in range(len(raw)) if raw[at] != changed[at]]
    expected = {command_at, wp_at, wp_at + 1, creature_at + 2, creature_at + 3}
    if len(changed) != len(raw) or not differ or not set(differ) <= expected:
        raise ValueError(f"edit changed bytes outside the edited fields: {[hex(at) for at in differ[:8]]}")
    stream, starts, _, _, _, _ = walk(changed, 0, "object", lengths)
    _, _, old_points, _, old_placed = map_geometry(raw)
    _, _, new_points, _, new_placed = map_geometry(changed)
    old_creature = next(row for row in old_placed if row[0] == "creature")
    new_creature = next(row for row in new_placed if row[0] == "creature")
    if (read_command(stream[starts[target]:])["operands"][0] != operands[0] or
            new_points[0][0] != old_points[0][0] + (1 << 16) or
            new_creature[3] != old_creature[3] + (1 << 16)):
        raise ValueError("an edited field does not read back through the existing readers")
    return True


def check(data):
    sizes = native_sizes((data.resolve().parent / "LOL3.DAT").read_bytes())
    if len(sizes) != 39:
        raise ValueError("expected 39 native opcode lengths")
    counts, seen, maps, total, edited = Counter(), set(), 0, 0, 0
    for stem, _, raw in level_map_entries(data):
        rebuilt, totals, opcodes = rebuild(raw, sizes)
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
    regenerated = counts.pop("field bytes")
    print(f"CHECK MAP write: {maps} byte-identical MAPs, {len(seen)}/{len(sizes)} opcodes stored; " +
          ", ".join(f"{value:,} {name}" for name, value in counts.items()) +
          f"; {regenerated:,} of {total:,} bytes from parsed fields, {total - regenerated:,} copied; "
          "a command, waypoint and placement edit reads back")


def main():
    parser = lol3_cli.tool_args(__doc__, writes=False)
    parser.add_argument("--list", metavar="STEM", help="list the copied spans of one MAP: offsets, sizes and SHA-256")
    args = parser.parse_args()
    data = Path(args.data)
    if args.check:
        check(data)
    elif args.list:
        for stem, base, raw in level_map_entries(data):
            if stem == args.list.upper():
                for name, start, body in retained_spans(raw):
                    print(f"{stem}.WSX+{base + start:#x} MAP+{start:#x} {name} "
                          f"size={len(body)} sha256={sha256(body).hexdigest()}")
                return 0
        raise ValueError(f"unknown level {args.list}")
    else:
        parser.error("give --check or --list STEM")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
