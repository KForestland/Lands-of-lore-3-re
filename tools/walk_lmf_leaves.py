#!/usr/bin/env python3
"""Read the native LoL3 Light Map (LMF) directory and its storage groups.

  walk_lmf_leaves.py FILE.LMF [-o report.json]
  walk_lmf_leaves.py --data DAT --check            # check all original WSX entries
  walk_lmf_leaves.py --data DAT --check --decode   # also decode and check members (liblzo2)
"""
from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path
from struct import iter_unpack, unpack_from

from extract_wsx_entries import parse_wsx
from lol3_cli import wsx_files


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


def check(data_dir, decode):
    files = groups = members = 0
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
    extra = ", every group decoded and every member header checked" if decode else ""
    print(f"CHECK lmf: {files} LMF entries, {groups:,} stored groups, {members:,} light-map members{extra}")
    return int((files, groups, members) != (18, 5256, 424288))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("lmf", type=Path, nargs="?")
    parser.add_argument("-o", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--decode", action="store_true")
    parser.add_argument("--data", type=Path, default=os.environ.get("LOL3_DAT"))
    args = parser.parse_args()
    try:
        decode = lzo_decoder() if args.decode else None
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
    raise SystemExit(main())
