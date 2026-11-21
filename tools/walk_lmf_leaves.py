#!/usr/bin/env python3
"""Read the native LoL3 Light Map (LMF) directory and its storage groups.

  walk_lmf_leaves.py FILE.LMF [--out report.json]
  walk_lmf_leaves.py --data DAT --stem QWOD0       # that level's LMF directory, from the archive
  walk_lmf_leaves.py --data DAT --check            # check all original WSX entries
  walk_lmf_leaves.py --data DAT --check --decode   # also decode and check members (liblzo2)
"""
from __future__ import annotations

from cli_errors import ReaderArgumentParser, run_cli, game_path
import argparse
import json
import os
from collections import Counter
from pathlib import Path
from struct import iter_unpack, unpack_from

from hashlib import sha256

from extract_wsx_entries import parse_wsx
from lol3_cli import wsx_files
from lol3_script_framing import CODE_BIAS, RETAIL_PE

# The 15 calls of the member loader, and the 11-dword copy of its 44-byte header.
MEMBER_CALLS = (
    0x47451E, 0x474D85, 0x47596D, 0x47F833, 0x47FD11, 0x480438, 0x4982BA,
    0x498D51, 0x499C42, 0x4C00D1, 0x4C0154, 0x4C02D4, 0x4C02EB, 0x4C0321, 0x4C0345,
)
MEMBER_LOADER = 0x44EB40
HEADER_COPY = bytes.fromhex(
    "b90b0000008bf325ffff0000f3a58b0d149c540089542410d1e066894104a1149c54008d732c"
)


def lmf_groups(data):
    """Yield the source extent and expanded row lengths of each stored group."""
    if len(data) < 0x100:
        raise ValueError("short LMF header")
    zero, version, table, pool, table_size, pool_size, count = unpack_from("<7I", data)
    if (zero, version, table) != (0, 38, 0x100):
        raise ValueError("unrecognized LMF signature")
    if table_size != count * 16 or pool != table + table_size or pool_size != len(data) - pool:
        raise ValueError("inconsistent LMF directory or pool size")

    stored_end, group = pool, None
    for index, (offset, size, flags, packed) in enumerate(iter_unpack("<4I", data[table:pool])):
        if flags & 1 == 0:
            if group:
                yield group
            start = pool + offset
            length = packed & 0x3FFFF
            if start != stored_end or not length or start + length > len(data):
                raise ValueError(f"row {index}: invalid stored group range")
            stored_end = start + length
            group = dict(first_row=index, offset=start, packed=length, expanded=size, lengths=[size])
        else:
            if (not group or offset != group["offset"] - pool + group["expanded"]
                    or len(group["lengths"]) >= 256 or group["expanded"] + size > 0x40000):
                raise ValueError(f"row {index}: invalid group continuation")
            group["lengths"].append(size)
            group["expanded"] += size
    if group:
        yield group
    if stored_end != len(data):
        raise ValueError("stored groups do not cover the LMF pool")


def lzo_decoder():
    """Use the system's bounded LZO1X reader for the optional content check."""
    from ctypes import CDLL, POINTER, byref, c_size_t, c_void_p, create_string_buffer
    from ctypes.util import find_library

    library = find_library("lzo2")
    if not library:
        raise ValueError("--decode requires liblzo2")
    decode = CDLL(library).lzo1x_decompress_safe
    decode.argtypes = [c_void_p, c_size_t, c_void_p, POINTER(c_size_t), c_void_p]

    def read(data, size):
        output, written = create_string_buffer(size), c_size_t(size)
        if decode(data, len(data), output, byref(written), None) or written.value != size:
            raise ValueError("invalid LZO1X group or decoded size")
        return output.raw

    return read


def walk_bytes(data, name, decode=None):
    groups = list(lmf_groups(data))
    member_count = sum(len(group["lengths"]) for group in groups)
    stats = Counter()
    if decode:
        for group in groups:
            source = group["offset"]
            members = decode(data[source:source + group["packed"]], group["expanded"])
            at = 0
            for size in group["lengths"]:
                flags, width, height, _ = unpack_from("<IHHI", members, at)
                if flags not in (0, 1) or size != 44 + 2 * width * height:
                    raise ValueError(f"{name}: unexpected decoded member at {source:#x}+{at:#x}")
                stats[flags] += 1
                words = unpack_from("<4H", members, at + 0x0C)
                if any(words):
                    grid = unpack_from(f"<{width * height}H", members, at + 0x2C)
                    colors = set(grid)
                    perimeter = set(grid[:height])
                    perimeter.update(grid[-height:], grid[::height], grid[height - 1::height])
                    lattice = {}
                    for i in range(5):
                        base = round(i * (width - 1) / 4) * height
                        for j in range(5):
                            lattice.setdefault(grid[base + round(j * (height - 1) / 4)], []).append(i * 5 + j)
                    stats["members_with_header_samples"] += 1
                    for slot, (word, (x, y)) in enumerate(zip(words, ((0, 0), (1, 0), (1, 1), (0, 1)))):
                        if not word:
                            continue
                        stats["nonzero_header_samples"] += 1
                        if word & 0x8000 or word not in colors:
                            raise ValueError(f"{name}: header word outside sample colors at {source:#x}+{at:#x}")
                        stats["perimeter_header_samples"] += word in perimeter
                        near = [
                            (width - 1 - col if x else col) * height + (height - 1 - row if y else row)
                            for col in range(min(2, width)) for row in range(min(2, height))
                        ]
                        stats["matching_corner"] += any(grid[index] == word for index in near)
                        stats["opposite_corner"] += any(grid[-1 - index] == word for index in near)
                        corner_x = (width - 1) if x else 0
                        corner_y = (height - 1) if y else 0
                        stats["exact_corner"] += grid[corner_x * height + corner_y] == word
                        inset_x = 1 if corner_x == 0 else width - 2
                        inset_y = 1 if corner_y == 0 else height - 2
                        if 0 <= inset_x < width and 0 <= inset_y < height:
                            inset = grid[inset_x * height + inset_y] == word
                            stats["inset_corner"] += inset
                            stats["inset_and_corner"] += inset and grid[corner_x * height + corner_y] == word
                        cells = [grid[index] for index in near]
                        mean = sum(cells) / len(cells)
                        picked = min(set(cells), key=lambda value: (abs(value - mean), value))
                        stats["mean_corner"] += picked == word
                        low, high = max(0, corner_y - 7), min(height, corner_y + 8)
                        stats["corner_far"] += not any(
                            word in grid[column * height + low:column * height + high]
                            for column in range(max(0, corner_x - 7), min(width, corner_x + 8)))
                        # The quarter of the grid at that corner (the middle row or column, when odd,
                        # belongs to both halves), then four summaries of it.
                        cols = range(width // 2, width) if x else range((width + 1) // 2)
                        top, bottom = (height // 2, height) if y else (0, (height + 1) // 2)
                        quarter = []
                        for column in cols:
                            quarter.extend(grid[column * height + top:column * height + bottom])
                        stats["quarter_min"] += min(quarter) == word
                        stats["quarter_max"] += max(quarter) == word
                        stats["quarter_common"] += Counter(quarter).most_common(1)[0][0] == word
                        mean = sum(quarter) / len(quarter)
                        stats["quarter_mean"] += min(set(quarter), key=lambda value: (abs(value - mean), value)) == word
                        # Fixed points of a 5 x 5 lattice over the rectangle, counted per word slot.
                        for point in lattice.get(word, ()):
                            stats[f"point_{slot}_{point}"] += 1
                vectors = [unpack_from("<3h", members, at + 0x14 + 6 * j) for j in range(4)]
                unit = sum(abs(x * x + y * y + z * z - 32767 * 32767) < 1 << 18 for x, y, z in vectors)  # length 32767-32769
                if flags:
                    stats["vertex_unit"] += unit          # bit 0: four per-vertex normals at +0x14
                    stats["vertex_zero"] += vectors.count((0, 0, 0))
                elif len(set(vectors)) == 1:
                    stats["face_repeated"] += 1           # bit 0 clear: one vector, repeated
                at += size
    samples = [
        {**{key: value for key, value in group.items() if key != "lengths"},
         "members": len(group["lengths"])}
        for group in groups[:8]
    ]
    return dict(file=name, size=len(data), members=member_count, groups=len(groups),
                decoded_flags=dict(stats), group_sample=samples)


def walk(path: Path):
    return walk_bytes(path.read_bytes(), path.name)


def directory_text(data, name):
    """Header fields and one line per stored group. Member bytes are not printed."""
    groups = list(lmf_groups(data))
    zero, version, table, pool, table_size, pool_size, count = unpack_from("<7I", data)
    lines = [
        f"{name}: {len(data)} bytes, directory rows {count}, groups {len(groups)}",
        f"+0 {zero} +4 {version} +8 {table:#x} +0xc {pool:#x} +0x10 {table_size:#x} +0x14 {pool_size:#x} +0x18 {count}",
    ]
    for group in groups:
        lines.append(f"group row {group['first_row']} offset {group['offset']:#x} "
                     f"packed {group['packed']} expanded {group['expanded']} members {len(group['lengths'])}")
    return "\n".join(lines) + "\n"


def check_header_copy(data_dir):
    """The 44-byte header copy and the 15 calls of the member loader."""
    image = game_path(Path(data_dir).resolve().parent, "LOL3.DAT").read_bytes()
    if sha256(image).hexdigest() != RETAIL_PE:
        raise ValueError("LOL3.DAT does not match the documented English retail executable")
    if image[0x44ED0A - CODE_BIAS:0x44ED30 - CODE_BIAS] != HEADER_COPY:
        raise ValueError("light-map header copy is not 11 dwords ending at the grid")
    found = []
    blob = image[0x401000 - CODE_BIAS:0x5372E5 - CODE_BIAS]  # all of .text (virtual size 0x1362E5)
    for index in range(len(blob) - 5):
        if blob[index] != 0xE8:
            continue
        rel = int.from_bytes(blob[index + 1:index + 5], "little", signed=True)
        src = 0x401000 + index
        if (src + 5 + rel) & 0xFFFFFFFF == MEMBER_LOADER:
            found.append(src)
    if tuple(found) != MEMBER_CALLS:
        raise ValueError(f"member loader calls are {found}, not the 15 documented sites")


def check(data_dir, decode):
    check_header_copy(data_dir)
    files = groups = members = 0
    stats = Counter()
    for path in wsx_files(data_dir):
        try:
            archive = parse_wsx(path)
        except ValueError:
            continue
        for entry in archive["entries"]:
            if entry["is_lmf"]:
                result = walk_bytes(entry["blob"], f"{path.name}#{entry['index']}", decode)
                files += 1
                groups += result["groups"]
                members += result["members"]
                stats.update(result["decoded_flags"])
    extra = ", every group decoded and every member header checked" if decode else ""
    if decode:
        extra += (f"; bit 0 set on {stats[1]:,} members whose {stats['vertex_unit']:,} vertex normals are unit length "
                  f"({stats['vertex_zero']} zero), one repeated vector on {stats['face_repeated']:,} of {stats[0]:,} others")
        extra += (f"; {stats['nonzero_header_samples']:,} nonzero +0x0C..+0x13 words occur in their own grids "
                  f"({stats['perimeter_header_samples']:,} on their perimeter, "
                  f"{stats['matching_corner']:,} near their corresponding corners, "
                  f"{stats['opposite_corner']:,} near their opposite corners)")
        nonzero, exact, near, far = (stats["nonzero_header_samples"], stats["exact_corner"],
                                     stats["matching_corner"], stats["corner_far"])
        quarters = tuple(stats[key] for key in ("quarter_min", "quarter_max", "quarter_common", "quarter_mean"))
        best_point = max((value for key, value in stats.items() if str(key).startswith("point_")), default=0)
        extra += (f"; from the assigned corner: {exact:,} at the corner texel, {near - exact:,} one texel away, "
                  f"{nonzero - near - far:,} two to seven away, {far:,} eight or more away; "
                  f"{stats['inset_corner']:,} match the texel one step inward ({stats['inset_and_corner']:,} of them also the corner), "
                  f"{stats['mean_corner']:,} the 2 x 2 colour nearest its numeric mean; quarter min/max/most common/nearest mean "
                  f"{quarters[0]:,}/{quarters[1]:,}/{quarters[2]:,}/{quarters[3]:,}; best 5 x 5 lattice point {best_point:,}")
        print(f"CHECK lmf: {files} LMF entries, {groups:,} stored groups, {members:,} light-map members{extra}")
        return int((files, groups, members, stats[1], stats["vertex_unit"], stats["vertex_zero"], stats[0],
                    stats["face_repeated"], stats["members_with_header_samples"], stats["nonzero_header_samples"],
                    stats["perimeter_header_samples"], stats["matching_corner"], stats["opposite_corner"],
                    stats["exact_corner"], stats["inset_corner"], stats["mean_corner"], stats["corner_far"],
                    quarters, best_point)
                   != (18, 5256, 424288, 131217, 524865, 3, 293071, 293071, 209545, 610325, 599684, 340718, 107136,
                       108537, 287177, 307470, 130568, (46912, 171206, 182804, 154018), 58260))
    print(f"CHECK lmf: {files} LMF entries, {groups:,} stored groups, {members:,} light-map members{extra}")
    return int((files, groups, members) != (18, 5256, 424288))


def main():
    parser = ReaderArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("lmf", type=Path, nargs="?")
    parser.add_argument("--out", "-o", dest="o", metavar="FILE", type=Path, help="write the report JSON to this file")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--decode", action="store_true")
    parser.add_argument("--data", type=Path, default=os.environ.get("LOL3_DAT"), help="the game's DAT folder (default: $LOL3_DAT)")
    parser.add_argument("--stem", help="print this level's LMF directory from its archive")
    args = parser.parse_args()
    try:
        decode = lzo_decoder() if args.decode else None
        if args.stem:
            if args.check or args.decode or args.lmf is not None:
                parser.error("--stem only prints the directory")
            if args.data is None:
                parser.error("give --data (the game's DAT folder) or set LOL3_DAT")
            stem = args.stem.upper()
            archive = next((path for path in wsx_files(args.data) if path.stem.upper() == stem), None)
            if archive is None:
                raise ValueError(f"no archive for level {stem}")
            lights = [entry for entry in parse_wsx(archive)["entries"] if entry["is_lmf"]]
            if len(lights) != 1:
                raise ValueError(f"{archive.name} has {len(lights)} light-map entries")
            print(directory_text(lights[0]["blob"], archive.name), end="")
            return 0
        if args.check:
            if args.data is None:
                parser.error("give --data (the game's DAT folder) or set LOL3_DAT")
            return check(args.data, decode)
        if args.lmf is None:
            parser.error("give one LMF file or --check")
        result = walk_bytes(args.lmf.read_bytes(), args.lmf.name, decode)
        output = json.dumps(result, indent=2) + "\n"
        if args.o:
            args.o.write_text(output, encoding="utf-8")
        else:
            print(output, end="")
        return 0
    except (OSError, ValueError) as error:
        parser.exit(1, f"LMF: {error}\n")


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
