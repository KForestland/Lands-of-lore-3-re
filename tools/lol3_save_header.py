#!/usr/bin/env python3
"""Read the native LoL3 Windows slot header. Prints offsets and sizes to stdout."""
import argparse
import json
import struct
from pathlib import Path

HEADER_SIZE = 0x64C


def parse_header(header, file_size):
    """Read the preview and both directories without loading save payloads."""
    if len(header) < HEADER_SIZE:
        raise ValueError("short LoL3 slot header")
    size, version, layout = struct.unpack_from("<3I", header, 0x2C)
    if size != file_size or (version, layout) != (38, 310):
        raise ValueError("LoL3 slot size or version mismatch")
    width, height, preview = struct.unpack_from("<3I", header, 0x39C)
    levels = struct.unpack_from("<18I", header, 0x5B0)
    lengths = struct.unpack_from("<18I", header, 0x600)
    offsets = (preview, *struct.unpack_from("<61I", header, 0x4B8), levels[0])
    if preview < HEADER_SIZE or any(start > end for start, end in zip(offsets, offsets[1:])):
        raise ValueError("invalid LoL3 slot global section directory")
    if any(start + length != end for start, length, end in zip(levels, lengths, levels[1:] + (size,))):
        raise ValueError("invalid LoL3 slot level section directory")
    spans = [(start, end - start) for start, end in zip(offsets, offsets[1:])]
    return dict(size=size, preview=spans[0], width=width, height=height,
                sections=spans[1:], levels=list(zip(levels, lengths)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    try:
        with args.file.open("rb") as source:
            header = source.read(HEADER_SIZE)
            size = source.seek(0, 2)
        print(json.dumps(parse_header(header, size), indent=2))
    except (OSError, ValueError) as error:
        parser.exit(1, f"save header: {error}\n")


if __name__ == "__main__":
    main()
