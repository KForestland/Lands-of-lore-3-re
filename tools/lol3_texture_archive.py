#!/usr/bin/env python3
"""Check the native LoL3 texture archive wrapper and its optional LZO expansion.

  lol3_texture_archive.py --data DAT --check
  lol3_texture_archive.py --data DAT --check --decode   # liblzo2
"""
from pathlib import Path
from struct import error as struct_error, iter_unpack, unpack_from

import lol3_cli
from extract_wsx_entries import wsx_name_hash
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


def cache_rows(data_dir):
    path = cache_path(data_dir)
    if path is None:
        raise ValueError("missing game-folder cdcache.wsx")
    with Path(path).open("rb") as source:
        source.seek(0x72)
        if unpack_from("<I", source.read(4))[0] != 0xF1E2D3C4:
            raise ValueError("missing installed cache marker")
        rows = {key: (offset, size) for offset, size, key, _, _, occupied, _, _, _
                in iter_unpack("<5I4B", source.read(0x3C0)) if occupied}
    return Path(path), rows


def main():
    parser = lol3_cli.tool_args(__doc__)
    parser.add_argument("--decode", action="store_true", help="expand each bank and compare the installed copies")
    args = parser.parse_args()
    if args.out:
        parser.error("this check reports counts on standard output")
    try:
        data_dir = Path(args.data)
        decode = lzo_decoder() if args.decode else None
        if decode:
            path, cache = cache_rows(data_dir)
        files = blocks = matches = 0
        for name, packed in texture_entries(data_dir):
            sections = list(chunks(packed))
            files += 1
            blocks += len(sections)
            if decode:
                expanded = b"".join(decode(data, size) for data, size in sections)
                if unpack_from("<I", expanded)[0] != 38 or unpack_from("<I", expanded, 0x40)[0] != 0x300:
                    raise ValueError(f"{name}: unexpected expanded texture header")
                key = wsx_name_hash(f"LEVELS\\{name}\\{name}.TEX")
                if key in cache:
                    offset, length = cache[key]
                    with path.open("rb") as source:
                        source.seek(offset)
                        if source.read(length) != expanded:
                            raise ValueError(f"{name}: cached .TEX differs")
                    matches += 1
            if not args.check:
                print(f"{name}: {len(sections)} chunks")
        if (files, blocks) != (18, 465) or (decode and matches != 4):
            raise ValueError("texture aggregate counts do not match the English retail corpus")
        detail = f", all decoded and {matches} byte-identical cache banks" if decode else ""
        print(f"CHECK texture_archive: {files} .TE_ entries, {blocks} packed chunks{detail}")
        return 0
    except (OSError, ValueError, struct_error) as error:
        parser.exit(1, f"texture archive: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
