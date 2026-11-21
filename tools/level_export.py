#!/usr/bin/env python3
"""Export LoL3 MAP surfaces and texture references to Wavefront OBJ."""
from collections import defaultdict
from math import isclose
from pathlib import Path
import re
import struct

from cli_errors import ReaderArgumentParser, run_cli
from extract_wsx_entries import wsx_name_hash
from level_edit_data import entry
from level_html import counted, find_data, installation_root
from level_viewer import levels, maps
from lol3_cli import DEFAULT_DATA
from lol3_level_schematic import map_geometry
from lol3_texture_archive import cache_rows, chunks, texture_entries
from lol3_texture_png import RAW_FLAGS, SPAN_FLAGS, cache_textures, decode_texture, png_bytes, rgba_palette
from modkit_core import output_folder
from walk_lmf_leaves import lzo_decoder

UVS = ("vt 0 0", "vt 1 0", "vt 1 1", "vt 0 1")


def mesh(payload):
    """Keep source X/Z indices and split each reused index at a different stored height."""
    vertices, surfaces, _, _, _ = map_geometry(payload)
    start, = struct.unpack_from("<I", payload, 0x0C)
    heights = [struct.unpack_from("<h", payload, start + i * 56 + 0x18)[0] for i in range(len(surfaces))]
    use = defaultdict(set)
    for corners, height in zip(surfaces, heights):
        for index in corners:
            use[index].add(height)
    points = [(x / 65536, min(use[i], default=0), -z / 65536)
              for i, (x, z) in enumerate(vertices)]
    extra = {}
    for index, (x, z) in enumerate(vertices):
        for height in sorted(use[index])[1:]:
            extra[index, height] = len(points) + 1
            points.append((x / 65536, height, -z / 65536))
    # Negating Z mirrors the horizontal plane. Reverse each face to keep its normal.
    faces = [tuple(extra.get((corners[i], height), corners[i] + 1) for i in (0, 3, 2, 1))
             for corners, height in zip(surfaces, heights)]
    counted = len(vertices) + sum(max(0, len(values) - 1) for values in use.values())
    if len(points) != counted or len(faces) != len(surfaces):
        raise ValueError("OBJ mesh counts disagree with the MAP reader")
    return len(vertices), points, faces


def texture_references(payload, odf, face_count):
    """Read each MAP surface's two ODF material references and light-map base."""
    if odf is None or len(odf) < 0x40:
        raise ValueError("The level ODF is missing or truncated. Use an intact level archive.")
    start, = struct.unpack_from("<I", odf, 4)
    count, = struct.unpack_from("<I", odf, 0x3C)
    if (count and start < 0x40) or start + 24 * count > len(odf):
        raise ValueError("The ODF material table is out of range. Use an intact level archive.")
    materials = [struct.unpack_from("<h", odf, start + 24 * index + 4)[0]
                 for index in range(count)]

    surface_start, = struct.unpack_from("<I", payload, 0x0C)
    references = []
    for index in range(face_count):
        at = surface_start + 56 * index
        first, second = payload[at + 0x20], payload[at + 0x22]
        light, = struct.unpack_from("<H", payload, at + 0x2A)
        if any(value != 0xFF and value >= count for value in (first, second)):
            raise ValueError(f"Surface {index + 1} refers to a missing ODF material. Use an intact level archive.")
        references.append(" ".join(
            "none" if value == 0xFF else f"{value}:{materials[value]}"
            for value in (first, second)) + f" {light}")
    return references


def level_references(data, stem, payload, face_count):
    key = wsx_name_hash(f"LEVELS\\{stem}\\{stem}.ODF")
    return texture_references(payload, entry(data, f"{stem}.WSX", key=key), face_count)


def obj_lines(stem, points, faces, references):
    yield f"# {stem}: MAP surface heights and unit-square UVs per face"
    yield "# Each face follows a texture-ref comment: first material:selector, second material:selector, light-map base"
    yield "# ODF material indices and initial selectors; texture pixels and native UVs are separate."
    yield f"o {stem}"
    for x, y, z in points:
        yield f"v {x:.8f} {y} {z:.8f}"
    yield from UVS
    for face, reference in zip(faces, references, strict=True):
        yield f"# texture-ref {reference}"
        yield "f " + " ".join(f"{vertex}/{i}" for i, vertex in enumerate(face, 1))


def verify_obj(lines, points, faces, references):
    seen_v = seen_uv = seen_f = 0
    reference = None
    for line in lines:
        line = line.strip()
        if line.startswith("# texture-ref "):
            if reference is not None:
                raise ValueError("OBJ has two texture references for one face")
            reference = line.removeprefix("# texture-ref ")
            continue
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "v":
            if seen_v >= len(points) or len(parts) != 4 or any(
                    not isclose(float(actual), want, abs_tol=1e-8, rel_tol=0)
                    for actual, want in zip(parts[1:], points[seen_v])):
                raise ValueError("OBJ vertex differs from the MAP reader")
            seen_v += 1
        elif parts[0] == "vt":
            if seen_uv >= len(UVS) or line != UVS[seen_uv]:
                raise ValueError("OBJ texture coordinates differ from the unit square")
            seen_uv += 1
        elif parts[0] == "f":
            if seen_f >= len(faces) or reference != references[seen_f]:
                raise ValueError("OBJ texture reference differs from the MAP and ODF reader")
            want = [f"{index}/{i}" for i, index in enumerate(faces[seen_f], 1)]
            if parts[1:] != want or any(not 1 <= index <= seen_v for index in faces[seen_f]):
                raise ValueError("OBJ face references differ from the MAP reader")
            seen_f += 1
            reference = None
    if (seen_v, seen_uv, seen_f) != (len(points), len(UVS), len(faces)) or reference is not None:
        raise ValueError("OBJ vertex, UV or face counts differ from the MAP reader")


def bank(data, stem):
    try:
        path, rows = cache_rows(data)
    except ValueError:
        rows = {}
    key = wsx_name_hash(f"LEVELS\\{stem}\\{stem}.TEX")
    if key in rows:
        start, size = rows[key]
        with path.open("rb") as file:
            file.seek(start)
            blob = file.read(size)
        if len(blob) != size:
            raise ValueError(f"The cached texture bank for {stem} is truncated. Use a matching game folder.")
        return blob
    try:
        decode = lzo_decoder()
    except ValueError as error:
        raise ValueError("Texture export needs liblzo2 or a matching installed texture cache. "
                         "Omit --textures to export the OBJ alone.") from error
    for name, packed in texture_entries(data):
        if name == stem:
            return b"".join(decode(raw, size) for raw, size in chunks(packed))
    raise ValueError(f"No texture bank was found for {stem}. Check the selected game folder.")


def write_textures(data, stem, out, request):
    blob = bank(data, stem)
    chosen = {}
    skipped = set()
    for at, size, _, descriptor, mip, key, source in cache_textures(blob, [(0, len(blob))]):
        record = blob[at:at + size]
        flags, = struct.unpack_from("<I", record)
        if descriptor in chosen:
            continue
        if flags not in RAW_FLAGS and flags not in SPAN_FLAGS:
            skipped.add(descriptor)
            continue
        chosen[descriptor] = (at, record, descriptor, mip, key, source)
    if not chosen:
        raise ValueError(f"No supported indexed textures were found for {stem}. Export the OBJ without --textures.")
    folder = out / "textures"
    folder.mkdir()
    selected = list(chosen.values()) if request == "all" else list(chosen.values())[:int(request)]
    index = ["file\tdescriptor_offset\tmip\tbank_offset\tpalette_key\twidth\theight"]
    for at, record, descriptor, mip, key, source in selected:
        rgba = rgba_palette(blob[source:source + 512], blob[descriptor + 8] & 2)
        width, height, pixels = decode_texture(record, rgba)
        name = f"texture-{descriptor:06x}.png"
        (folder / name).write_bytes(png_bytes(width, height, pixels))
        index.append(f"{name}\t{descriptor:#x}\t{mip}\t{at:#x}\t{key}\t{width}\t{height}")
    (out / "textures.tsv").write_text("\n".join(index) + "\n", encoding="utf-8")
    return len(selected), len(skipped - chosen.keys())


def verify_surface_count(stem, payload, face_count):
    """Compare read-back faces to both the native table and the published level sheet."""
    header_count, = struct.unpack_from("<I", payload, 0x58)
    reader_count = len(map_geometry(payload)[1])
    sheet = Path(__file__).resolve().parents[1] / "docs" / "levels" / f"{stem}.md"
    match = re.search(r"Field 21 counts ([0-9,]+) surface rows", sheet.read_text(encoding="utf-8"))
    if match is None:
        raise ValueError(f"{stem}: the level sheet has no Field 21 surface count")
    sheet_count = int(match[1].replace(",", ""))
    if header_count != reader_count or reader_count != sheet_count or sheet_count != face_count:
        raise ValueError(f"{stem}: OBJ {face_count}, MAP header {header_count}, reader {reader_count}, "
                         f"level sheet {sheet_count} faces differ")


def main():
    parser = ReaderArgumentParser(description=__doc__)
    parser.add_argument("--data", default=DEFAULT_DATA, required=DEFAULT_DATA is None,
                        help="your game folder or its DAT folder (default: $LOL3_DAT)")
    parser.add_argument("--level", default="QWOD0", help="level name (default: QWOD0)")
    parser.add_argument("--out", help="new folder for the OBJ")
    parser.add_argument("--textures", nargs="?", const="all", help="also export textures (all or a positive number)")
    parser.add_argument("--check", action="store_true", help="verify every MAP mesh without writing")
    args = parser.parse_args()
    if args.check and (args.out or args.textures):
        parser.error("Use --check by itself with --data. It writes no files.")
    if not args.check and not args.out:
        parser.error("Give --out a new output folder for the OBJ.")
    if args.textures and args.textures != "all" and not (
            args.textures.isdecimal() and int(args.textures) > 0):
        parser.error("Use --textures all or give --textures a positive number.")
    data = find_data(args.data, "DAT", "QWOD0.WSX")
    if args.check:
        total_v = total_f = 0
        for stem, (_, payload) in maps(data).items():
            _original, points, faces = mesh(payload)
            references = level_references(data, stem, payload, len(faces))
            verify_obj(obj_lines(stem, points, faces, references), points, faces, references)
            verify_surface_count(stem, payload, len(faces))
            total_v += len(points)
            total_f += len(faces)
        print(f"CHECK level_export: {len(maps(data))} maps, {total_v:,} OBJ vertices read back. "
              f"{total_f:,} faces and texture-reference rows match the MAP and ODF readers "
              "and the face counts in the level sheets.")
        return 0
    selected = levels(data, args.level.upper())
    if len(selected) != 1:
        parser.error("Choose one level name to export, such as QWOD0.")
    stem = selected[0]
    payload = maps(data)[stem][1]
    source_count, points, faces = mesh(payload)
    references = level_references(data, stem, payload, len(faces))
    with output_folder(args.out, installation_root(data), args.data) as folder:
        output = folder / f"{stem}.obj"
        output.write_text("\n".join(obj_lines(stem, points, faces, references)) + "\n", encoding="ascii")
        with output.open(encoding="ascii") as file:
            verify_obj(file, points, faces, references)
        textures, skipped = write_textures(data, stem, folder, args.textures) if args.textures else (0, 0)
    print(f"Wrote {stem}.obj to {args.out}: {counted(source_count, 'MAP vertex', 'MAP vertices')}, "
          f"{counted(len(points), 'OBJ vertex', 'OBJ vertices')}, "
          f"{counted(len(faces), 'face')} with texture references, {counted(textures, 'texture PNG')}.")
    if skipped:
        print(f"Skipped {skipped:,} texture descriptors whose available pixel routes are still open.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
