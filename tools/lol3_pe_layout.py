#!/usr/bin/env python3
"""Read the PE section directories of the original LoL3 programs."""
from pathlib import Path
from struct import unpack_from

from cli_errors import run_cli, game_path
from lol3_cli import tool_args


def layout(image):
    pe = unpack_from("<I", image, 0x3C)[0]
    if image[:2] != b"MZ" or image[pe:pe + 4] != b"PE\0\0":
        raise ValueError("missing MZ or PE header")
    machine, count = unpack_from("<HH", image, pe + 4)
    optional_size = unpack_from("<H", image, pe + 20)[0]
    header = pe + 24
    if (machine, unpack_from("<H", image, header)[0]) != (0x14C, 0x10B):
        raise ValueError("expected an x86 PE32 image")
    entry = unpack_from("<I", image, header + 16)[0]
    base, section_alignment, disk_alignment = unpack_from("<III", image, header + 28)
    image_size, disk_header = unpack_from("<II", image, header + 56)
    table = header + optional_size
    if not (optional_size >= 96 and count and disk_alignment and section_alignment
            and table + 40 * count <= disk_header <= len(image)):
        raise ValueError("invalid PE header extent or alignment")
    if any(image[table + 40 * count:disk_header]):
        raise ValueError("nonzero bytes between the section rows and the first section")
    sections = []
    stored_end, virtual_end = disk_header, disk_header
    entry_offset = None
    for i in range(count):
        name, virtual_size, rva, stored_size, stored = unpack_from("<8s4I", image, table + 40*i)
        if (rva % section_alignment or stored % disk_alignment
                or stored != stored_end or rva < virtual_end):
            raise ValueError("noncontiguous stored PE sections or overlapping virtual sections")
        stored_end = stored + stored_size
        virtual_end = rva + max(virtual_size, stored_size)
        if stored_end > len(image) or virtual_end > image_size:
            raise ValueError("PE section exceeds the file or image")
        if rva <= entry < rva + min(virtual_size, stored_size):
            entry_offset = stored + entry - rva
        sections.append((name.rstrip(b"\0").decode("ascii"), rva, virtual_size, stored, stored_size))
    if entry_offset is None:
        raise ValueError("PE entry point is not stored")

    debug = []
    directory_count = unpack_from("<I", image, header + 92)[0]
    if directory_count > 6 and optional_size >= 96 + 7 * 8:
        debug_rva, debug_size = unpack_from("<II", image, header + 96 + 6 * 8)
        if debug_size:
            for _, rva, _, stored, size in sections:
                if rva <= debug_rva and debug_rva + debug_size <= rva + size:
                    start = stored + debug_rva - rva
                    break
            else:
                raise ValueError("PE debug directory outside stored sections")
            if debug_size % 28:
                raise ValueError("partial PE debug directory record")
            for row in range(start, start + debug_size, 28):
                kind, size, disk_rva, offset = unpack_from("<4I", image, row + 12)
                if disk_rva or offset != stored_end or offset + size > len(image):
                    raise ValueError("unexpected retail PE debug payload extent")
                debug.append((kind, offset, size))
                stored_end = offset + size
    padding = len(image) - stored_end
    if padding >= disk_alignment or any(image[stored_end:]):
        raise ValueError("unaccounted bytes after PE section and debug payloads")
    return pe, base, entry_offset, sections, debug, padding


def main():
    parser = tool_args(__doc__, writes=False)
    args = parser.parse_args()
    root = Path(args.data).resolve().parent
    expected = {
        "LOL3.DAT": (0xC8, 0x400000, 0x1184A0, (".text", ".rdata", ".data", "RemapTab"),
                     [(4, 0x17F400, 0x110), (3, 0x17F510, 0x11CD0), (2, 0x1911E0, 0x2A)], 0x1F6),
        "LOL3.EXE": (0xE0, 0x400000, 0x5E3E, (".text", ".rdata", ".data", ".rsrc"), [], 0),
    }
    for name, witness in expected.items():
        image = game_path(root, name).read_bytes()
        pe, base, entry, sections, debug, padding = layout(image)
        if args.check and (pe, base, entry, tuple(row[0] for row in sections), debug, padding) != witness:
            raise ValueError(f"{name} differs from the documented retail layout")
        if not args.check:
            print(f"{name}: PE +0x{pe:X}, image base 0x{base:X}, entry file +0x{entry:X}")
            for label, rva, virtual, disk, size in sections:
                print(f"  {label:8} RVA +0x{rva:X} size 0x{virtual:X}  file +0x{disk:X} size 0x{size:X}")
            for kind, disk, size in debug:
                print(f"  debug type {kind}, file +0x{disk:X} size 0x{size:X}")
            if padding:
                print(f"  final zero padding: 0x{padding:X} bytes")
    if args.check:
        print("CHECK PE: 8 sections and 3 debug payloads; zero header tail, stored ranges and padding reach both file ends")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
