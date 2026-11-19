#!/usr/bin/env python3
"""Check the native LoL3 texture archive wrapper and its optional LZO expansion.

  lol3_texture_archive.py --data DAT --check
  lol3_texture_archive.py --data DAT --check --decode   # liblzo2
  lol3_texture_archive.py --data DAT --list QWOD0 --decode   # one bank's descriptors
"""
from cli_errors import run_cli
from pathlib import Path
from struct import error as struct_error, iter_unpack, unpack_from

import lol3_cli
from extract_wsx_entries import parse_wsx, wsx_name_hash
from lol3_texture_spans import cache_path
from walk_lmf_leaves import lzo_decoder

CHUNK = 0x100000


def texture_entries(data_dir):
    for path in lol3_cli.wsx_files(data_dir):
        with path.open("rb") as source:
            count, size = unpack_from("<HI", source.read(6))
            if count != 4:
                continue
            name = path.stem.upper()
            key = wsx_name_hash(f"LEVELS\\{name}\\{name}.TE_")
            for stored, offset, length in iter_unpack("<III", source.read(48)):
                if stored == key:
                    if offset + length > size:
                        raise ValueError(f"{path.name}: .TE_ range exceeds WSX data")
                    source.seek(54 + offset)
                    packed = source.read(length)
                    if len(packed) != length:
                        raise ValueError(f"{path.name}: truncated .TE_ entry")
                    yield name, packed
                    break


def chunks(data):
    total = unpack_from("<I", data)[0]
    remaining, offset = total, 4
    while offset + 4 <= len(data):
        packed = unpack_from("<I", data, offset)[0]
        offset += 4
        if not packed:
            if remaining or offset != len(data):
                raise ValueError("texture terminator does not match stored and decoded lengths")
            return
        if remaining <= 0 or packed > 0x104010 or offset + packed > len(data):
            raise ValueError(f"invalid packed texture chunk at {offset:#x}")
        expanded = min(CHUNK, remaining)
        yield data[offset:offset + packed], expanded
        remaining -= expanded
        offset += packed
    raise ValueError("missing zero-length texture terminator")


def cache_rows(data_dir, explicit=None):
    path = cache_path(data_dir, explicit)
    if path is None:
        raise ValueError("missing game-folder cdcache.wsx")
    with Path(path).open("rb") as source:
        source.seek(0x72)
        if unpack_from("<I", source.read(4))[0] != 0xF1E2D3C4:
            raise ValueError("missing installed cache marker")
        rows = {key: (offset, size) for offset, size, key, _, _, occupied, _, _, _
                in iter_unpack("<5I4B", source.read(0x3C0)) if occupied}
    return Path(path), rows


def joined_palettes(data, expected_arm):
    """Count descriptors whose native arm and u16 key select an in-bank palette."""
    if unpack_from("<I", data)[0] != 38 or len(data) < 0x6A2:
        raise ValueError("bad texture bank header")
    directory, payload = unpack_from("<II", data, 0x10)
    palettes, = unpack_from("<I", data, 0x34)
    directory_size, = unpack_from("<I", data, 0x4C)
    palette_bytes, = unpack_from("<I", data, 0x70)
    count, = unpack_from("<I", data, 0x2A8)
    palette_count, remainder = divmod(palette_bytes, 512)
    if not (0x6A2 <= directory <= directory + count * 58 <= payload <= palettes
            and count * 58 <= directory_size and not remainder
            and palettes + palette_bytes <= len(data)):
        raise ValueError("texture bank sections exceed their declared ranges")
    if count == 0 or any(data[directory:directory + 14]):
        raise ValueError("missing arm-0 texture sentinel")
    for index in range(1, count):
        at = directory + 58 * index
        key, = unpack_from("<H", data, at + 2)
        if data[at + 0xD] != expected_arm or key >= palette_count:
            raise ValueError(f"unbound native palette at descriptor {at:#x}")
    return count - 1


def shared_joins(data_dir):
    local = next(path for path in lol3_cli.wsx_files(data_dir) if path.stem.upper() == "LOCAL")
    names = {wsx_name_hash(f"GLOBAL\\{name}.TEX"): arm for name, arm in (("GLOBAL", 1), ("SPELL", 2))}
    counts = {}
    for entry in parse_wsx(local)["entries"]:
        arm = names.get(entry["hash"])
        if arm is not None:
            counts[arm] = joined_palettes(entry["blob"], arm)
    if counts != {1: 692, 2: 4635}:
        raise ValueError("missing or altered shared texture banks")
    return counts


def descriptor_lines(data, stem):
    """One line per 58-byte descriptor: directory offset, u16 key and arm byte."""
    if len(data) < 0x2AC:
        raise ValueError(f"{stem}: texture bank header is short")
    directory, = unpack_from("<I", data, 0x10)
    count, = unpack_from("<I", data, 0x2A8)
    if directory + 58 * count > len(data):
        raise ValueError(f"{stem}: descriptors exceed the bank")
    lines = [f"{stem} descriptors {count}"]
    for index in range(count):
        at = directory + 58 * index
        key, = unpack_from("<H", data, at + 2)
        lines.append(f"descriptor {index + 1}: +{at:#x} key {key:#x} arm {data[at + 0xD]}")
    return "\n".join(lines) + "\n"


def main():
    parser = lol3_cli.tool_args(__doc__, writes=False)
    parser.add_argument("--decode", action="store_true", help="expand each bank and compare the installed copies")
    parser.add_argument("--list", help="print one level's descriptors; requires --decode")
    args = parser.parse_args()
    if args.out:
        parser.error("this check reports counts on standard output")
    if args.list:
        if args.check or not args.decode:
            parser.error("--list needs --decode and does not check")
        try:
            stem = args.list.upper()
            found = [item for item in texture_entries(args.data) if item[0] == stem]
            if len(found) != 1:
                raise ValueError(f"expected one .TE_ for {stem}")
            decode = lzo_decoder()
            expanded = b"".join(decode(blob, size) for blob, size in chunks(found[0][1]))
            joined_palettes(expanded, 3)
            print(descriptor_lines(expanded, stem), end="")
        except (OSError, ValueError, struct_error, StopIteration) as error:
            parser.exit(1, f"texture archive: {error}\n")
        return 0
    try:
        data_dir = Path(args.data)
        decode = lzo_decoder() if args.decode else None
        path, cache = None, None
        if decode and cache_path(data_dir) is not None:
            path, cache = cache_rows(data_dir)
        files = blocks = matches = descriptors = 0
        for name, packed in texture_entries(data_dir):
            sections = list(chunks(packed))
            files += 1
            blocks += len(sections)
            if decode:
                expanded = b"".join(decode(data, size) for data, size in sections)
                descriptors += joined_palettes(expanded, 3)
                key = wsx_name_hash(f"LEVELS\\{name}\\{name}.TEX")
                if cache is not None and key in cache:
                    offset, length = cache[key]
                    with path.open("rb") as source:
                        source.seek(offset)
                        if source.read(length) != expanded:
                            raise ValueError(f"{name}: cached .TEX differs")
                    matches += 1
            if not args.check:
                print(f"{name}: {len(sections)} chunks")
        if (files, blocks) != (18, 465) or (decode and cache is not None and matches != 4):
            raise ValueError("texture aggregate counts do not match the English retail corpus")
        detail = ""
        if decode:
            if descriptors != 44357:
                raise ValueError("retail level texture descriptor count disagrees")
            counts = shared_joins(data_dir)
            detail = (f", all decoded and {matches} byte-identical cache banks" if cache is not None
                      else ", all decoded; cache comparison SKIPPED (no game-folder cdcache.wsx, which the game writes when it runs)")
            detail += f"; palette joins {counts[1]:,}/{counts[2]:,}/{descriptors:,} for arms 1/2/3"
        print(f"CHECK texture_archive: {files} .TE_ entries, {blocks} packed chunks{detail}")
        return 0
    except (OSError, ValueError, struct_error, StopIteration) as error:
        parser.exit(1, f"texture archive: {error}\n")


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
