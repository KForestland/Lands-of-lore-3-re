#!/usr/bin/env python3
"""Write interactive LoL3 map pages from your original WSX archives."""
from collections import defaultdict
from functools import lru_cache
import struct

from cli_errors import run_cli
from level_html import Plan, main
from level_move_ui import sections
from level_edit_data import placement_name
from lol3_level_schematic import PLACEMENTS, map_geometry
from lol3_progression import collect
from lol3_script_framing import level_map_entries

MARKS = {
    "type 3": ("Type 3 placements", "#b6a4ff", "P"),
    "type 16": ("Type 16 placements", "#95dcb1", "C"),
    "creature": ("Creatures", "#ffacbd", "A"),
    "mover (type 32)": ("Movers", "#9bbcff", "M"),
    "item": ("Items", "#ffcf81", "I"),
}


@lru_cache(maxsize=1)
def maps(data):
    return {stem: (offset, blob) for stem, offset, blob in level_map_entries(data)}


def levels(data, selection):
    stems = sorted(maps(data))
    if selection == "ALL":
        return stems
    if selection not in stems:
        raise ValueError(f"Level {selection} was not found. Choose {', '.join(stems)} or all.")
    return [selection]


def progression(data, _selected):
    result = defaultdict(list)
    for row in collect(data, full_corpus=False)[0]:
        result[row[0]].append(row)
    return result


def source_event(row):
    event = row[7].split()
    return int(event[1]) if event[0] == "region" else None


def view(data, stem, gates):
    base, payload = maps(data)[stem]
    vertices, surfaces, waypoints, routes, placed = map_geometry(payload)
    plan = Plan(f"{stem} level plan", vertices,
                f"The map comes from {stem}.WSX. Source offsets show where records start in the archive. "
                "Exit conditions come from the stored scripts.")
    plan.legend.update({"Surface": "#587888", "Exit surface": "var(--exit)", "Waypoint path": "#83a6ff"})
    exit_surfaces = {source_event(row) for row in gates}
    start, = struct.unpack_from("<I", payload, 0x0C)
    for i, row in enumerate(surfaces):
        at = start + i * 56
        low, high, partition = struct.unpack_from("<hhH", payload, at + 0x18)
        neighbors = struct.unpack_from("<4H", payload, at + 8)
        plan.polygon([vertices[j] for j in row], f"surface-{i}", f"Surface {i}", "Surfaces",
                     {"Low / high": f"{low} / {high}", "Region table index": partition,
                      "Neighbors": ", ".join(str(j) if j != 0xFFFF else "none" for j in neighbors),
                      "Source": f"{stem}.WSX +{base+at:#x}"},
                     style="region exit-region" if i in exit_surfaces else "region")
    for path in routes:
        plan.line(path, "route")
    for i, (x, z) in enumerate(waypoints, 1):
        start, = struct.unpack_from("<I", payload, 0xC8)
        plan.dot((x, z), f"waypoint-{i}", f"Waypoint {i}", "Waypoints",
                 {"X / Z": f"{x >> 16} / {z >> 16}",
                  "Source": f"{stem}.WSX +{base + start + 8 * (i-1):#x}"}, "#d3e8f1", f"W{i}")
    tables = {name: (struct.unpack_from("<I", payload, offset)[0], stride)
              for name, offset, _, stride, _ in PLACEMENTS}
    for name, i, x, z, _ in placed:
        kind, color, prefix = MARKS[name]
        start, stride = tables[name]
        title = placement_name(data, payload, name, i, start + stride * (i - 1))
        plan.dot((x, z), f"{prefix}-{i}", title or f"{name.capitalize()} {i}", kind,
                 {"Row (starts at 1)": i, "X / Z": f"{x >> 16} / {z >> 16}",
                  "Source": f"{stem}.WSX +{base + start + stride * (i - 1):#x}"}, color, f"{prefix}{i}")
    for i, row in enumerate(gates, 1):
        _, dest, arm, arg, stream, group, command, event, predicate, earlier, guard = row
        surface = source_event(row)
        target = f"surface-{surface}" if surface is not None and 0 <= surface < len(surfaces) else None
        plan.note(f"exit-{i}", f"Exit {i} to {dest}", "Exits",
                  {"Gate": guard, "Event": event, "Predicate": predicate, "Tried first": earlier,
                   "Script": f"{stream} group {group}, command {command}, subcommand {arm}, arg {arg}"}, target)
    plan.edit_controls, plan.edit_script = sections(plan, stem, payload)
    return plan


if __name__ == "__main__":
    raise SystemExit(run_cli(main, __doc__, "DAT", "QWOD0.WSX", "QWOD0", levels, view, progression))
