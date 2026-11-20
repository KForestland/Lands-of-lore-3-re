#!/usr/bin/env python3
"""Read an original LoL3 MAP and draw an overhead SVG.

  lol3_level_schematic.py --data DAT --level QWOD0 --out ../qwod0.svg

Give --data the game folder or its DAT folder.

The drawing uses MAP coordinates: surface edges, hollow waypoint squares,
path runs and numbered dots for the rows of all five placement tables
(type 3, type 16, creature, mover, item), plus a legend. The scale fits the
surface edges; waypoints and placements outside them, and numbers that would
overlap one already drawn, are left out and counted in the footer
(--no-labels draws no numbers). Large levels give SVGs over the repository's
300 KB file limit (BUPP1 650 KB, FLAIR 670 KB, DLOW1 370 KB with numbers), so
write those outside the repository.
No texture, sprite, light map or game image is opened for drawing.
"""
from cli_errors import run_cli
from level_html import find_data, new_picture
import struct
from collections import Counter
from html import escape
from pathlib import Path

import lol3_cli
from extract_wsx_entries import parse_wsx, wsx_name_hash
from lol3_level_report import geometry_check


# Disk rows whose first two s16 values 0x4411F0 shifts left 16 into object +4/+8
# (all five constructors reach it; the mover through 0x4D58F0 -> 0x4698D0).
# Header offsets are the MAP loader seeks at 0x43EEB6-0x43EF6F; the strides are
# the reads at 0x44FCEB (0x25), 0x4699A2 (0x21), 0x4B4553 (0x38),
# 0x4D5A1C (0x29) and 0x4D74AC (0x25). Drawn numbers are 1-based table rows.
PLACEMENTS = (
    ("type 3", 0x14, 0x60, 0x25, "#6b3fa0"),
    ("type 16", 0x18, 0x64, 0x21, "#2f6f4e"),
    ("creature", 0x1C, 0x68, 0x38, "#a33b3b"),
    ("mover (type 32)", 0x24, 0x70, 0x29, "#1f5fa8"),
    ("item", 0x20, 0x6C, 0x25, "#c47b12"),
)
MAP_W, MAP_H, LEGEND_H = 900, 620, 116


def map_geometry(data):
    if len(data) < 0x244 or struct.unpack_from("<I", data)[0] != 38:
        raise ValueError("invalid MAP header")
    fields = struct.unpack_from("<38I", data, 4)
    vertex_start, surface_start = fields[0], fields[2]
    vertex_count, _, surface_count = fields[19:22]
    vertex_end = vertex_start + 8 * vertex_count
    if not (0x244 <= vertex_start <= vertex_end <= surface_start
            and vertex_count and surface_count and geometry_check(data, fields)):
        raise ValueError("invalid MAP geometry tables")
    vertices = list(struct.iter_unpack("<ii", data[vertex_start:vertex_end]))
    surfaces = [struct.unpack_from("<4H", data, surface_start + 56 * index + 0x10)
                for index in range(surface_count)]
    point_count, point_start = struct.unpack_from("<II", data, 0xC4)
    waypoints = [(x << 16, z << 16) for x, z, _, _ in struct.iter_unpack(
        "<hhHH", data[point_start:point_start + 8 * point_count])]
    path_count, path_start = struct.unpack_from("<II", data, 0xD8)
    routes = []
    for first, count, _ in struct.iter_unpack("<HBB", data[path_start:path_start + 4 * path_count]):
        if count:
            routes.append(waypoints[first:first + count])
    placed = []
    for name, off_at, count_at, stride, color in PLACEMENTS:
        offset, count = struct.unpack_from("<I", data, off_at)[0], struct.unpack_from("<I", data, count_at)[0]
        end = offset + stride * count
        if count and (offset < 0x244 or end > len(data)):
            raise ValueError(f"{name} table runs outside the MAP")
        for index in range(count):
            x, z = struct.unpack_from("<hh", data, offset + stride * index)
            placed.append((name, index + 1, x << 16, z << 16, color))
    return vertices, surfaces, waypoints, routes, placed


def schematic_svg(stem, vertices, surfaces, waypoints, routes, placed, labels=True, notes=None):
    outlines = Counter()
    for indices in surfaces:
        points = [vertices[index] for index in indices]
        for start, end in zip(points, points[1:] + points[:1]):
            if start != end:
                outlines[tuple(sorted((start, end)))] += 1
    if not outlines:
        raise ValueError("MAP has no nonzero surface edges")
    # The scale fits the surface edges only; marks outside them are counted, not drawn.
    used = {point for pair in outlines for point in pair}
    x0 = min(x for x, _ in used)
    x1 = max(x for x, _ in used)
    z0 = min(z for _, z in used)
    z1 = max(z for _, z in used)

    def inside(point):
        return x0 <= point[0] <= x1 and z0 <= point[1] <= z1

    width, height = MAP_W, MAP_H + LEGEND_H
    scale = min((width - 64) / max(1, x1 - x0), (MAP_H - 64) / max(1, z1 - z0))
    left = (width - scale * (x1 - x0)) / 2
    top = (MAP_H - scale * (z1 - z0)) / 2

    def project(point):
        return left + (point[0] - x0) * scale, top + (z1 - point[1]) * scale

    def pair(point):
        px, py = project(point)
        return f"{px:.2f},{py:.2f}"

    groups = ("#1e4c56", "#87acae")
    segments = [[], []]
    for (start, end), count in sorted(outlines.items()):
        segments[count > 1].append(f"M{pair(start)}L{pair(end)}")
    edge_paths = [f'<path fill="none" stroke="{stroke}" stroke-width="{weight}" d="{"".join(segment)}"/>'
                  for stroke, weight, segment in zip(groups, ("1.35", "0.55"), segments)]
    route_paths = []
    for route in routes:
        shown = [point for point in route if inside(point)]
        if len(shown) > 1:
            route_paths.append('<path fill="none" stroke="#c45c26" stroke-width="1.4" stroke-dasharray="5 3" d="%s"/>'
                               % "".join(("M" if i == 0 else "L") + pair(point) for i, point in enumerate(shown)))
    squares = []
    waypoints_out = 0
    for point in waypoints:
        if not inside(point):
            waypoints_out += 1
            continue
        px, py = project(point)
        squares.append(f'<rect x="{px - 3.2:.2f}" y="{py - 3.2:.2f}" width="6.4" height="6.4" '
                       f'fill="none" stroke="#14343b" stroke-width="1.3"/>')
    dots, texts, taken = [], [], []
    placed_out = labels_dropped = 0
    for name, index, x, z, color in placed:
        if not inside((x, z)):
            placed_out += 1
            continue
        px, py = project((x, z))
        dots.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="2.3" fill="{color}"/>')
        if not labels:
            continue
        box = (px + 2.6, py - 7.4, px + 3.8 + 3.6 * len(str(index)), py - 1.2)
        if any(box[0] < b[2] and b[0] < box[2] and box[1] < b[3] and b[1] < box[3] for b in taken):
            labels_dropped += 1
            continue
        taken.append(box)
        texts.append(f'<text x="{px + 3.2:.2f}" y="{py - 2.4:.2f}" fill="{color}" font-family="sans-serif" '
                     f'font-size="6" stroke="#f5f7f6" stroke-width="2" paint-order="stroke">{index}</text>')
    counts = Counter(name for name, _, _, _, _ in placed)
    font = 'font-family="sans-serif" font-size="12" fill="#14343b"'
    legend = [
        f'<rect x="0" y="{MAP_H}" width="{width}" height="{LEGEND_H}" fill="#e7eeec"/>',
        f'<line x1="16" y1="{MAP_H + 16}" x2="46" y2="{MAP_H + 16}" stroke="#1e4c56" stroke-width="1.35"/>',
        f'<text x="52" y="{MAP_H + 20}" {font}>edge used once</text>',
        f'<line x1="180" y1="{MAP_H + 16}" x2="210" y2="{MAP_H + 16}" stroke="#87acae" stroke-width="1.6"/>',
        f'<text x="216" y="{MAP_H + 20}" {font}>shared edge</text>',
        f'<rect x="340" y="{MAP_H + 11}" width="8" height="8" fill="none" stroke="#14343b" stroke-width="1.3"/>',
        f'<text x="354" y="{MAP_H + 20}" {font}>waypoint ({len(waypoints)})</text>',
        f'<line x1="500" y1="{MAP_H + 16}" x2="540" y2="{MAP_H + 16}" stroke="#c45c26" stroke-width="1.4" stroke-dasharray="5 3"/>',
        f'<text x="546" y="{MAP_H + 20}" {font}>path ({len(routes)})</text>',
    ]
    for slot, (name, _, _, _, color) in enumerate(PLACEMENTS):
        column, row = divmod(slot, 2)
        lx, ly = 16 + column * 290, MAP_H + 44 + row * 22
        legend.append(f'<circle cx="{lx + 5}" cy="{ly - 4}" r="4" fill="{color}"/>')
        legend.append(f'<text x="{lx + 16}" y="{ly}" {font}>{escape(name)} ({counts[name]}){", numbered" if labels else ""}</text>')
    footer = ["numbers are 1-based table rows" if labels else "row numbers not drawn (--no-labels)"]
    if labels_dropped:
        footer.append(f"{labels_dropped} overlapping numbers left out")
    if waypoints_out or placed_out:
        footer.append(f"outside the bounding box of the surface edges, not drawn: {waypoints_out} waypoints, {placed_out} placements")
    if notes is not None:
        notes.extend(footer)
    legend.append(f'<text x="16" y="{MAP_H + 102}" font-family="sans-serif" font-size="11" fill="#14343b">'
                  f'{escape("; ".join(footer))}</text>')
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img">',
        f'<title>{escape(stem)} MAP schematic</title>',
        '<desc>Overhead X/Z projection. Dark lines are edges used once, pale lines are shared edges, '
        'hollow squares are waypoints, dashed lines are paths, and ' + ('numbered ' if labels else '')
        + 'dots are the rows of the five placement tables (type 3, type 16, creature, mover, item).</desc>',
        f'<rect width="{width}" height="{MAP_H}" fill="#f5f7f6"/>',
        edge_paths[1], edge_paths[0], *route_paths, *dots, *texts, *squares, *legend, '</svg>', '',
    ])


def main():
    parser = lol3_cli.tool_args(__doc__, out_help="write the SVG to this path")
    parser.add_argument("--level", help="level page name such as QWOD0")
    parser.add_argument("--no-labels", action="store_true", help="draw placement dots without row numbers")
    args = parser.parse_args()
    if args.check and args.out:
        parser.error("--check prints to stdout")
    if not args.check and (not args.out or not args.level):
        parser.error("Use --level and --out to write the schematic, or --check.")
    try:
        data = find_data(args.data, "DAT", "QWOD0.WSX")
        stem = "QWOD0" if args.check else args.level.upper()
        archive = next((file for file in lol3_cli.wsx_files(data) if file.stem.upper() == stem), None)
        if archive is None:
            raise ValueError(f"Level {stem} was not found in {data}. Give --level the name of a level page.")
        key = wsx_name_hash(f"LEVELS\\{stem}\\{stem}.MAP")
        matches = [entry for entry in parse_wsx(archive)["entries"] if entry["hash"] == key]
        if len(matches) != 1:
            raise ValueError(f"expected one MAP with key {key:#010x} in {archive.name}")
        vertices, surfaces, waypoints, routes, placed = map_geometry(matches[0]["blob"])
        svg = schematic_svg(stem, vertices, surfaces, waypoints, routes, placed,
                            labels=args.check or not args.no_labels)
        counts = ", ".join(f"{name} {sum(item[0] == name for item in placed)}" for name, *_ in PLACEMENTS)
        summary = (f"{len(vertices)} vertices, {len(surfaces)} surfaces, "
                   f"waypoints {len(waypoints)}, paths {len(routes)}, {counts}")
        if args.check:
            tracked = Path(__file__).resolve().parents[1] / "docs" / "images" / "qwod0-schematic.svg"
            same = tracked.read_text(encoding="utf-8") == svg
            print(f"CHECK level_schematic: QWOD0 {summary}; "
                  f"docs/images/qwod0-schematic.svg {'regenerates byte-identical' if same else 'DIFFERS'}")
            return 0 if same else 1
        output = Path(args.out).resolve()
        game = data.parent
        repo = Path(__file__).resolve().parents[1]
        if output == game or game in output.parents:
            parser.error("--out must be outside the game tree")
        if (output == repo or repo in output.parents) and not any(
                folder in output.parents for folder in (repo / "docs" / "images", repo / "examples")):
            parser.error("inside the repository, --out may only point into docs/images/ or examples/")
        new_picture(Path(args.out), ".svg")
        with output.open("x", encoding="utf-8", newline="\n") as file:
            file.write(svg)
        print(f"Wrote schematic for {stem} to {args.out}.")
        return 0
    except (OSError, ValueError, struct.error) as error:
        parser.exit(1, f"level schematic: {error}\n")


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
