#!/usr/bin/env python3
"""List the native palette source of each LoL3 cache texture span.

  lol3_texture_palettes.py --data DAT            # one JSON line per span
  lol3_texture_palettes.py --data DAT --check    # verify the native joins

Offsets are relative to the game-folder cdcache.wsx. No palette or pixel
bytes are emitted.
"""
import json
import re
import struct
from collections import Counter
from pathlib import Path

import lol3_cli
from lol3_texture_spans import cache_path, records


def u32(data, at):
    return struct.unpack_from("<I", data, at)[0]


def bank_directory(data, begin, end):
    if begin < 0 or begin + 0x6A2 > end or end > len(data):
        raise ValueError(f"truncated texture bank at {begin:#x}")
    if (u32(data, begin) != 38 or u32(data, begin + 0x40) != 0x300
            or struct.unpack_from("<II", data, begin + 0x54) != (0x4200, 0x20000)):
        raise ValueError(f"invalid texture bank header at {begin:#x}")
    directory, pixels = struct.unpack_from("<II", data, begin + 0x10)
    palettes, palette_size = u32(data, begin + 0x34), u32(data, begin + 0x70)
    directory_size, count = u32(data, begin + 0x4C), u32(data, begin + 0x2A8)
    if not (0x6A2 <= directory <= pixels < palettes
            and count * 58 <= directory_size
            and directory + count * 58 <= pixels
            and palette_size % 512 == 0
            and begin + palettes + palette_size <= end):
        raise ValueError(f"invalid texture bank ranges at {begin:#x}")
    return begin, directory, pixels, palettes, palette_size // 512, count


def banks(data):
    """Find texture-bank candidates in file data."""
    for match in re.finditer(rb"\x26\x00\x00\x00", data):
        begin = match.start()
        if begin + 0x6A2 > len(data) or u32(data, begin + 0x40) != 0x300:
            continue
        try:
            yield bank_directory(data, begin, len(data))
        except ValueError:
            continue


def palette_sources(data):
    spans = {}
    for at, _, _, _, length, valid in records(data):
        if not valid or at in spans:
            raise ValueError(f"invalid or duplicate texture span at {at:#x}")
        spans[at] = length
    rows = {}
    for bank, directory, payload, palettes, palette_count, count in banks(data):
        for index in range(count):
            at = bank + directory + index * 58
            key = struct.unpack_from("<H", data, at + 2)[0]
            for mip in range(5):
                size = u32(data, at + 0x26 + 4 * mip)
                source = bank + payload + u32(data, at + 0x12 + 4 * mip)
                if size == 0 or source not in spans:
                    continue
                if size != spans[source] + 12 or source in rows:
                    raise ValueError(f"ambiguous or mismatched descriptor at {at:#x} for span {source:#x}")
                arm = data[at + 0xD]
                if arm != 3 or key >= palette_count:
                    raise ValueError(f"unbound palette arm or key at descriptor {at:#x}")
                rows[source] = dict(texture_offset=source, bank_offset=bank, descriptor_offset=at,
                                    descriptor_index=index, mip=mip, palette_arm=arm,
                                    palette_key=key, palette_offset=bank + palettes + 512 * key)
    missing = spans.keys() - rows.keys()
    if not spans or missing:
        raise ValueError(f"{len(missing)} of {len(spans)} texture spans lack a native descriptor")
    return rows


def main():
    parser = lol3_cli.tool_args(__doc__)
    args = parser.parse_args()
    try:
        path = cache_path(args.data)
        if path is None:
            print("CHECK texture_palettes: SKIP: no game-folder cdcache.wsx next to the DAT folder (the game writes this cache when it runs; the shipped DAT/cdcache.wsx holds no texture records)")
            return 0
        rows = palette_sources(Path(path).read_bytes())
        if args.check:
            by_bank = Counter(row["bank_offset"] for row in rows.values())
            print(f"CHECK texture_palettes: {len(rows)} unique arm-3 joins across {len(by_bank)} banks")
            return int(list(sorted(by_bank.values())) != [25, 191, 243, 395])
        for at in sorted(rows):
            print(json.dumps(rows[at], separators=(",", ":")))
        return 0
    except (OSError, ValueError, struct.error) as error:
        parser.exit(1, f"texture palettes: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
