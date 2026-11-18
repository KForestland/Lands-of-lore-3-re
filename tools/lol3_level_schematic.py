#!/usr/bin/env python3
"""Draw an overhead SVG from one original LoL3 MAP.

  lol3_level_schematic.py --data DAT QWOD0 --out ../qwod0.svg

The drawing uses MAP coordinates and surface indices. No texture, sprite,
light map or game image is opened for drawing.
"""
import struct
from collections import Counter
from html import escape
from pathlib import Path

import lol3_cli
from extract_wsx_entries import parse_wsx, wsx_name_hash
from lol3_level_report import geometry_check


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
    return vertices, surfaces


def schematic_svg(stem, vertices, surfaces):
    outlines = Counter()
    for indices in surfaces:
        points = [vertices[index] for index in indices]
        for start, end in zip(points, points[1:] + points[:1]):
            if start != end:
                outlines[tuple(sorted((start, end)))] += 1
    if not outlines:
        raise ValueError("MAP has no nonzero surface edges")
    used = {point for pair in outlines for point in pair}
    x0 = min(x for x, _ in used)
    x1 = max(x for x, _ in used)
    z0 = min(z for _, z in used)
    z1 = max(z for _, z in used)

    width, height = 900, 620
    scale = min((width - 64) / max(1, x1 - x0), (height - 64) / max(1, z1 - z0))
    left = (width - scale * (x1 - x0)) / 2
    top = (height - scale * (z1 - z0)) / 2
    projected = {point: f"{left + (point[0] - x0) * scale:.2f},{top + (z1 - point[1]) * scale:.2f}"
                 for point in used}

    groups = ("#1e4c56", "#87acae")
    segments = [[], []]
    for (start, end), count in sorted(outlines.items()):
        segments[count > 1].append(f"M{projected[start]}L{projected[end]}")
    paths = [f'<path fill="none" stroke="{stroke}" stroke-width="{weight}" d="{"".join(segment)}"/>'
             for stroke, weight, segment in zip(groups, ("1.35", "0.55"), segments)]
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img">',
        f'<title>{escape(stem)} MAP surface schematic</title>',
        '<desc>Overhead X/Z projection. Dark lines mark edges used once, and pale lines mark shared edges.</desc>',
        f'<rect width="{width}" height="{height}" fill="#f5f7f6"/>',
        paths[1], paths[0], '</svg>', '',
    ])


def main():
    parser = lol3_cli.tool_args(__doc__, out_help="write the SVG to this path")
    parser.add_argument("level", nargs="?", help="level archive stem, for example QWOD0")
    args = parser.parse_args()
    if args.check:
        args.level = "QWOD0"
    elif not args.out or not args.level:
        parser.error("give a level stem and --out to write the schematic, or --check")
    try:
        stem = args.level.upper()
        archive = next((file for file in lol3_cli.wsx_files(args.data) if file.stem.upper() == stem), None)
        if archive is None:
            raise ValueError(f"no archive for level {stem}")
        key = wsx_name_hash(f"LEVELS\\{stem}\\{stem}.MAP")
        matches = [entry for entry in parse_wsx(archive)["entries"] if entry["hash"] == key]
        if len(matches) != 1:
            raise ValueError(f"expected one MAP with key {key:#010x} in {archive.name}")
        vertices, surfaces = map_geometry(matches[0]["blob"])
        svg = schematic_svg(stem, vertices, surfaces)
        if args.check:
            tracked = Path(__file__).resolve().parents[1] / "docs" / "images" / "qwod0-schematic.svg"
            same = tracked.read_text(encoding="utf-8") == svg
            print(f"CHECK level_schematic: QWOD0 {len(vertices)} vertices, {len(surfaces)} surfaces; "
                  f"docs/images/qwod0-schematic.svg {'regenerates byte-identical' if same else 'DIFFERS'}")
            return 0 if same else 1
        output = Path(args.out).resolve()
        game = Path(args.data).resolve().parent
        repo = Path(__file__).resolve().parents[1]
        if output == game or game in output.parents:
            parser.error("--out must be outside the game tree")
        if (output == repo or repo in output.parents) and not any(
                folder in output.parents for folder in (repo / "docs" / "images", repo / "examples")):
            parser.error("inside the repository, --out may only point into docs/images/ or examples/")
        output.write_text(svg, encoding="utf-8")
        print(f"{archive.name}+{matches[0]['offset']:#x}: {len(vertices)} vertices, {len(surfaces)} surfaces")
        return 0
    except (OSError, ValueError, struct.error) as error:
        parser.exit(1, f"level schematic: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
