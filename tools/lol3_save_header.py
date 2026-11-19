#!/usr/bin/env python3
"""Print a LoL3 save slot: named header fields, directories, and other header bytes as hex.

  lol3_save_header.py --data DAT SLOT
  lol3_save_header.py --data DAT --check

The slot is a player save, not a file from the DAT folder. --check builds a
synthetic slot and compares the version checks in LOL3.DAT. Nothing is written
unless --out is given, and that path must be outside the game tree and this
repository. Section payloads are spans only; they are not expanded.

Slot fields are the ones named on the save page. Version compares: LOL3.DAT
file +0x3BE0B (VA 0x43CA0B, cmp immediate 310) and +0x3BE17 (VA 0x43CA17,
cmp immediate 38). A level block header is 0x34C bytes: size at +0, 75
relative starts at +0xF4, 75 expanded lengths at +0x220.
"""
import struct
from pathlib import Path

import lol3_cli

HEADER_SIZE = 0x64C
BLOCK_HEADER = 0x34C
LEVEL_SECTIONS = 75
LAYOUT_CMP_AT = 0x3BE0B
LAYOUT_CMP = bytes.fromhex("817c242436010000")
VERSION_CMP_AT = 0x3BE17
VERSION_CMP = bytes.fromhex("837c241026")


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


def synthetic_slot():
    """One in-memory slot with named fields and a single 75-section block.

    No game file is read. The bytes after the block header are a marker the
    report must not print.
    """
    block = bytearray(BLOCK_HEADER + 8)
    struct.pack_into("<I", block, 0, len(block))
    block[4:8] = b"\x11\x22\x33\x44"
    starts = [BLOCK_HEADER] + [len(block)] * (LEVEL_SECTIONS - 1)
    expanded = [16] + [0] * (LEVEL_SECTIONS - 1)
    struct.pack_into(f"<{LEVEL_SECTIONS}I", block, 0xF4, *starts)
    struct.pack_into(f"<{LEVEL_SECTIONS}I", block, 0x220, *expanded)
    block[BLOCK_HEADER:] = b"PAYLOAD!"

    preview_at = HEADER_SIZE
    global_at = HEADER_SIZE + 4
    level_at = HEADER_SIZE + 8
    end = level_at + len(block)
    header = bytearray(HEADER_SIZE)
    header[:7] = b"Reader\0"
    struct.pack_into("<3I", header, 0x2C, end, 38, 310)
    struct.pack_into("<3I", header, 0x38, 0x11111111, 0x22222222, 0x33333333)
    struct.pack_into("<20I", header, 0x44, *range(20))
    header[0x94:0x98] = b"\xAA\xBB\xCC\xDD"
    struct.pack_into("<I", header, 0x98, 1)
    header[0x9C:0x9F] = b"\x01\x02\x03"
    struct.pack_into("<3I", header, 0x39C, 8, 4, preview_at)
    header[0x3A8:0x3AC] = b"\xDE\xAD\xBE\xEF"
    struct.pack_into("<I", header, 0x498, 2)
    struct.pack_into("<iiIH", header, 0x49C, 0x00010000, -0x00020000, 0x8000, 0x0018)
    struct.pack_into("<iiIH", header, 0x4AA, 0x00030000, 0x00040000, 0x0100, 0xFFFF)
    struct.pack_into("<61I", header, 0x4B8, global_at, *([level_at] * 60))
    struct.pack_into("<18I", header, 0x5B0, level_at, *([end] * 17))
    struct.pack_into("<18I", header, 0x600, len(block), *([0] * 17))
    header[0x648:0x64C] = b"\x10\x20\x30\x40"
    return bytes(header) + b"prev" + b"glob" + bytes(block)


def _hex_lines(blob, start, end, prefix=""):
    lines = []
    for offset in range(start, end, 16):
        chunk = blob[offset:min(offset + 16, end)]
        lines.append(prefix + f"+{offset:#x}: " + " ".join(f"{byte:02x}" for byte in chunk))
    return lines


def _text(raw):
    return "".join(chr(byte) if 32 <= byte < 127 else f"\\x{byte:02x}" for byte in raw)


def _position(label, blob, offset):
    horizontal_x, horizontal_z, heading, region = struct.unpack_from("<iiIH", blob, offset)
    return (f"{label} +{offset:#x}: x {horizontal_x} ({horizontal_x / 65536:.4f}) "
            f"z {horizontal_z} ({horizontal_z / 65536:.4f}) "
            f"heading {heading:#x} region {region:#x}")


def report(data):
    """Text report of one slot. Payloads stay as spans."""
    parsed = parse_header(data[:HEADER_SIZE], len(data))
    header = data[:HEADER_SIZE]
    lines = []
    name = bytes(header[:0x2C])
    if b"\0" in name:
        shown = _text(name.split(b"\0", 1)[0])
    else:
        shown = _text(name) + " (no NUL in the 44-byte slot)"
    lines.append(f"display name +0: {shown}")
    lines.append(f"file length +0x2c: {parsed['size']}")
    version, layout = struct.unpack_from("<2I", header, 0x30)
    lines.append(f"version +0x30: {version}")
    lines.append(f"layout +0x34: {layout}")
    stamps = struct.unpack_from("<3I", header, 0x38)
    lines.append("stamps +0x38 +0x3c +0x40: " + " ".join(f"{stamp:#010x}" for stamp in stamps))
    level_stamps = struct.unpack_from("<20I", header, 0x44)
    lines.append("level stamps +0x44: " + " ".join(f"{stamp:#x}" for stamp in level_stamps))
    lines.append("unnamed +0x94..+0x98:")
    lines.extend(_hex_lines(header, 0x94, 0x98))
    lines.append(f"preview flag +0x98: {struct.unpack_from('<I', header, 0x98)[0]}")
    lines.append("preview palette +0x9c: 768 bytes")
    lines.extend(_hex_lines(header, 0x9C, 0x39C))
    lines.append(f"preview width +0x39c: {parsed['width']}")
    lines.append(f"preview height +0x3a0: {parsed['height']}")
    lines.append(f"preview offset +0x3a4: {parsed['preview'][0]:#x}")
    lines.append(f"preview length: {parsed['preview'][1]}")
    lines.append("unnamed +0x3a8..+0x498:")
    lines.extend(_hex_lines(header, 0x3A8, 0x498))
    lines.append(f"current level +0x498: {struct.unpack_from('<I', header, 0x498)[0]}")
    lines.append(_position("player", header, 0x49C))
    lines.append(_position("second object", header, 0x4AA))
    lines.append("global sections +0x4b8:")
    for index, (start, length) in enumerate(parsed["sections"]):
        lines.append(f"global {index} +{start:#x} length {length}")
    lines.append("level directory +0x5b0 +0x600:")
    for index, (start, length) in enumerate(parsed["levels"]):
        ident = index + 2
        if length == 0:
            lines.append(f"level index {index} (id {ident}): empty")
        elif length < BLOCK_HEADER:
            lines.append(f"level index {index} (id {ident}) +{start:#x}: {length} bytes, "
                         "shorter than the 0x34c block header")
        else:
            lines.append(f"level index {index} (id {ident}) +{start:#x}: {length} bytes")
    lines.append("unnamed +0x648..+0x64c:")
    lines.extend(_hex_lines(header, 0x648, 0x64C))
    preview_at = parsed["preview"][0]
    if preview_at > HEADER_SIZE:
        gap = preview_at - HEADER_SIZE
        lines.append(f"unnamed +{HEADER_SIZE:#x}..+{preview_at:#x}: {gap} bytes")
        if gap <= 64:
            lines.extend(_hex_lines(data, HEADER_SIZE, preview_at))
        else:
            lines.extend(_hex_lines(data, HEADER_SIZE, HEADER_SIZE + 16))
            lines.append(f"middle {gap - 32} bytes omitted")
            lines.extend(_hex_lines(data, preview_at - 16, preview_at))
    else:
        lines.append(f"header ends at +{HEADER_SIZE:#x}, where the preview starts")
    for index, (start, length) in enumerate(parsed["levels"]):
        if length < BLOCK_HEADER:
            continue
        block = data[start:start + length]
        stored = struct.unpack_from("<I", block, 0)[0]
        lines.append(f"level index {index} block +0 size: {stored}")
        if stored != length:
            lines.append(f"level index {index} block +0 size differs from the directory length {length}")
        lines.append(f"level index {index} block +0..+0xf4:")
        lines.extend(_hex_lines(block, 0, 0xF4, prefix="block "))
        starts = struct.unpack_from(f"<{LEVEL_SECTIONS}I", block, 0xF4)
        expanded = struct.unpack_from(f"<{LEVEL_SECTIONS}I", block, 0x220)
        if any(left > right for left, right in zip(starts, starts[1:])) or starts[-1] > length:
            raise ValueError(f"invalid LoL3 level block section directory at level index {index}")
        for number, (relative, end, size) in enumerate(zip(starts, starts[1:] + (length,), expanded)):
            lines.append(f"level index {index} section {number}: stored +{relative:#x} "
                         f"length {end - relative}, expanded {size}, not expanded")
    return "\n".join(lines) + "\n"


def check_line(data_dir):
    """Prove the report on a synthetic slot, then the two version compares."""
    blob = synthetic_slot()
    text = report(blob)
    parsed = parse_header(blob[:HEADER_SIZE], len(blob))
    globals_printed = sum(line.startswith("global ") and line[7].isdigit() for line in text.splitlines())
    sections_printed = sum(line.startswith("level index 0 section ") for line in text.splitlines())
    if (parsed["size"] != len(blob) or len(parsed["sections"]) != 61 or len(parsed["levels"]) != 18
            or globals_printed != 61 or sections_printed != LEVEL_SECTIONS
            or "version +0x30: 38" not in text or "layout +0x34: 310" not in text
            or "+0x94: aa bb cc dd" not in text or "player +0x49c:" not in text
            or "second object +0x4aa:" not in text or "PAYLOAD" in text
            or "50 41 59 4c" in text):
        raise ValueError("synthetic slot report is wrong")
    image = (Path(data_dir).resolve().parent / "LOL3.DAT").read_bytes()
    if image[LAYOUT_CMP_AT:LAYOUT_CMP_AT + len(LAYOUT_CMP)] != LAYOUT_CMP:
        raise ValueError("LOL3.DAT layout compare at file +0x3BE0B differs")
    if image[VERSION_CMP_AT:VERSION_CMP_AT + len(VERSION_CMP)] != VERSION_CMP:
        raise ValueError("LOL3.DAT version compare at file +0x3BE17 differs")
    return ("CHECK save_header: synthetic slot names version 38, layout 310, "
            "both position groups, 61 global spans, 18 level spans and one 75-section block; "
            "unnamed header bytes are hex; LOL3.DAT+0x3BE0B is the layout 310 compare and "
            "+0x3BE17 is the version 38 compare")


def main():
    parser = lol3_cli.tool_args(
        __doc__, out_help="write the report to this file, outside the game tree and this repository")
    parser.add_argument("file", nargs="?", type=Path, help="one save slot (not used with --check)")
    args = parser.parse_args()
    if args.check and args.out:
        parser.error("--check writes nothing")
    if args.check:
        try:
            print(check_line(args.data))
        except (OSError, ValueError, struct.error) as error:
            parser.exit(1, f"CHECK save_header FAILED: {error}\n")
        return 0
    if args.file is None:
        parser.error("give a slot file, or --check")
    try:
        data = args.file.read_bytes()
        text = report(data)
    except (OSError, ValueError, struct.error) as error:
        parser.exit(1, f"save header: {error}\n")
    if args.out:
        output = Path(args.out).resolve()
        game = Path(args.data).resolve().parent
        repo = Path(__file__).resolve().parents[1]
        if output == game or game in output.parents:
            parser.error("--out must be outside the game tree")
        if output == repo or repo in output.parents:
            parser.error("--out must be outside the repository")
        output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
