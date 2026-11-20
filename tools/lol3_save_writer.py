#!/usr/bin/env python3
"""Read the save selector flags in LOL3.DAT and the game-written save slots in SAVEGAME, and rebuild each slot in memory.

  lol3_save_writer.py --data DAT --check              # every slot in the SAVEGAME folder next to DAT
  lol3_save_writer.py --data DAT --check SLOT_OR_DIR  # one slot, or another folder of slots

The slots are player saves the game wrote, not shipped files. The check reads
each slot into fields (header, both directories, level-block headers and the
chunk frames of every section whose selector flag has bit 4), writes it again
and requires the same bytes. The compression flags come from the descriptor
arms that lol3_save_selectors.py reads in the retail LOL3.DAT. Stored LZO
packets are copied unchanged, so the check proves the container layout, not a
compressor. With liblzo2 every stored packet is also decoded to its expanded
length; without it the check reports SKIP. It then changes one header field
in memory and requires lol3_save_header.py to read the changed field back.
Nothing is written.
"""
from dataclasses import dataclass, replace
from ctypes.util import find_library
from pathlib import Path
import re
import struct

from cli_errors import run_cli, game_path
import lol3_cli
from lol3_save_header import BLOCK_HEADER, HEADER_SIZE, LEVEL_SECTIONS, parse_header, report
from walk_lmf_leaves import lzo_decoder

GLOBAL_SECTIONS = 61
LEVELS = 18
STAMPS = struct.Struct("<27I")
POSITIONS = struct.Struct("<IiiIHiiIH")
COMPRESSED = 4
SYNTHETIC_FLAGS = ((COMPRESSED,) + (0,) * (GLOBAL_SECTIONS - 1), (0, COMPRESSED) + (0,) * (LEVEL_SECTIONS - 2))


@dataclass(frozen=True)
class Packed:
    chunks: tuple

    @property
    def expanded_size(self):
        return sum(length for length, _ in self.chunks)

    def write(self):
        return b"".join(struct.pack("<2I", length, len(body)) + body for length, body in self.chunks)


@dataclass(frozen=True)
class Level:
    header_words: tuple
    gap: bytes
    sections: tuple


@dataclass(frozen=True)
class Slot:
    name_area: bytes
    stamps: tuple
    palette: bytes
    dimensions: tuple
    positions: tuple
    unknown: tuple
    gap: bytes
    preview: object
    sections: tuple
    levels: tuple


def read_packed(blob, decode=None):
    """Split one compressed section into (expanded length, stored packet) chunks."""
    chunks = []
    at = 0
    while at < len(blob):
        if at + 8 > len(blob):
            raise ValueError("short save chunk header")
        expanded, stored = struct.unpack_from("<2I", blob, at)
        start, end = at + 8, at + 8 + stored
        if not (0 < expanded <= 0x2000 and stored > 0 and end <= len(blob)):
            raise ValueError(f"invalid save chunk extent at section +{at:#x}")
        packed = blob[start:end]
        if decode:
            decode(packed, expanded)
        chunks.append((expanded, packed))
        at = end
    return Packed(tuple(chunks))


def read_part(blob, compressed, decode):
    return read_packed(blob, decode) if compressed else blob


def write_part(part):
    return (part.write(), part.expanded_size) if isinstance(part, Packed) else (part, len(part))


def read_level(blob, flags, decode):
    if len(blob) < BLOCK_HEADER or struct.unpack_from("<I", blob)[0] != len(blob):
        raise ValueError("level span and block length disagree")
    start = struct.unpack_from(f"<{LEVEL_SECTIONS}I", blob, 0xF4) + (len(blob),)
    lengths = struct.unpack_from(f"<{LEVEL_SECTIONS}I", blob, 0x220)
    if start[0] < BLOCK_HEADER or any(a > b for a, b in zip(start, start[1:])):
        raise ValueError("level section offsets do not follow the block header")
    sections = []
    for a, b, length, mode in zip(start, start[1:], lengths, flags):
        part = read_part(blob[a:b], mode & COMPRESSED, decode)
        expanded = part.expanded_size if isinstance(part, Packed) else len(part)
        if expanded != length:
            raise ValueError(f"level span at +{a:#x} disagrees with expanded length")
        sections.append(part)
    return Level(struct.unpack_from("<60I", blob, 4), blob[BLOCK_HEADER:start[0]], tuple(sections))


def read_slot(blob, global_flags, level_flags, decode=None):
    if (len(global_flags), len(level_flags)) != (GLOBAL_SECTIONS, LEVEL_SECTIONS):
        raise ValueError("slot needs the 61 global and 75 level selector flags")
    header = parse_header(blob, len(blob))
    stamps = STAMPS.unpack_from(blob, 0x30)
    at, length = header["preview"]
    preview = read_part(blob[at:at + length], stamps[-1] != 0, decode)
    if isinstance(preview, Packed) and preview.expanded_size != header["width"] * header["height"]:
        raise ValueError("preview chunks disagree with the dimensions")
    global_parts = tuple(read_part(blob[start:start + size], flags & COMPRESSED, decode)
                         for (start, size), flags in zip(header["sections"], global_flags))
    levels = tuple(read_level(blob[start:start + size], level_flags, decode) if size else None
                   for start, size in header["levels"])
    unknown = (blob[0x3A8:0x498], blob[0x5AC:0x5B0], blob[0x5F8:0x600], blob[0x648:0x64C])
    return Slot(blob[:0x2C], stamps, blob[0x9C:0x39C], (header["width"], header["height"]),
                POSITIONS.unpack_from(blob, 0x498), unknown, blob[HEADER_SIZE:at], preview, global_parts, levels)


def write_level(level):
    at = BLOCK_HEADER + len(level.gap)
    starts, expanded, parts = [], [], []
    for part in level.sections:
        body, length = write_part(part)
        starts.append(at)
        expanded.append(length)
        parts.append(body)
        at += len(body)
    return (struct.pack("<61I", at, *level.header_words)
            + struct.pack(f"<{LEVEL_SECTIONS}I", *starts) + struct.pack(f"<{LEVEL_SECTIONS}I", *expanded)
            + level.gap + b"".join(parts))


def write_slot(slot):
    """Lay out a slot from fields: offsets, lengths and the file size are recomputed."""
    preview_at = HEADER_SIZE + len(slot.gap)
    preview, _ = write_part(slot.preview)
    at = preview_at + len(preview)
    globals_at, bodies = [], []
    for part in slot.sections:
        encoded, _ = write_part(part)
        globals_at.append(at)
        bodies.append(encoded)
        at += len(encoded)
    levels_at, level_lengths = [], []
    for level in slot.levels:
        encoded = b"" if level is None else write_level(level)
        levels_at.append(at)
        level_lengths.append(len(encoded))
        bodies.append(encoded)
        at += len(encoded)
    unknown1, unknown2, unknown3, unknown4 = slot.unknown
    return (slot.name_area + struct.pack("<I", at) + STAMPS.pack(*slot.stamps)
            + slot.palette + struct.pack("<3I", *slot.dimensions, preview_at)
            + unknown1 + POSITIONS.pack(*slot.positions)
            + struct.pack(f"<{GLOBAL_SECTIONS}I", *globals_at) + unknown2
            + struct.pack(f"<{LEVELS}I", *levels_at) + unknown3
            + struct.pack(f"<{LEVELS}I", *level_lengths) + unknown4
            + slot.gap + preview + b"".join(bodies))


def synthetic_slot():
    """A tiny slot with one packed preview, one packed and one raw section."""
    lzo_example = Packed(((1, b"\x12A\x11\0\0"),))
    level = Level(tuple(range(60)), b"", (b"raw", lzo_example) + (b"",) * (LEVEL_SECTIONS - 2))
    return Slot(b"Fixture\0".ljust(44, b"\xee"), (38, 310) + (0,) * 24 + (1,),
                bytes(768), (1, 1), (2, 7, -15, 0x4000, 3, 0, 0, 0x8000, 0xFFFF),
                (bytes(240), b"test", bytes(8), bytes(4)), b"", lzo_example,
                (lzo_example,) + (b"",) * (GLOBAL_SECTIONS - 1), (level,) + (None,) * (LEVELS - 1))


def stored_part_count(slot):
    parts = [slot.preview, *slot.sections]
    levels = 0
    for level in slot.levels:
        if level is not None:
            levels += 1
            parts.extend(level.sections)
    return levels, sum(len(part.chunks) for part in parts if isinstance(part, Packed))


def moved_player(slot, blob):
    """Move the player x at +0x49C by one unit; lol3_save_header must read the new value."""
    positions = list(slot.positions)
    positions[1] += 0x10000
    edited = write_slot(replace(slot, positions=tuple(positions)))
    changed = [at for at in range(len(blob)) if blob[at] != edited[at]] if len(edited) == len(blob) else None
    if not changed or not all(0x49C <= at < 0x4A0 for at in changed):
        raise ValueError("changing the player x did not change only +0x49C..+0x4A0")
    want = f"player +0x49c: x {positions[1]} "
    if want not in report(edited):
        raise ValueError("lol3_save_header does not read the changed player x")
    return edited


def slot_paths(data, slot_path):
    folder = slot_path if slot_path else game_path(Path(data).resolve().parent, "SAVEGAME")
    if slot_path and slot_path.is_file():
        return [slot_path]
    if not folder.is_dir():
        return []
    return sorted(path for path in folder.glob("$*")
                  if path.is_file() and re.fullmatch(r"\.(?:\d{3}|XXX)", path.suffix.upper()))


def check(data, slot_path):
    fixture = synthetic_slot()
    if read_slot(write_slot(fixture), *SYNTHETIC_FLAGS) != fixture:
        raise ValueError("synthetic slot did not read back")
    paths = slot_paths(data, slot_path)
    if not paths:
        return "CHECK save_write: SKIP: no game-written slots in SAVEGAME; the synthetic slot reads back"
    from lol3_save_selectors import GLOBAL_COUNT, LEVEL_COUNT, image_of, selector_flags
    flags = selector_flags(image_of(data))
    if (GLOBAL_COUNT, LEVEL_COUNT, len(flags)) != (GLOBAL_SECTIONS, LEVEL_SECTIONS, GLOBAL_SECTIONS + LEVEL_SECTIONS):
        raise ValueError("selector counts differ from lol3_save_selectors.py")
    decoded = 0
    decoder = None
    if find_library("lzo2"):
        lzo = lzo_decoder()

        def decoder(packet, size):
            nonlocal decoded
            decoded += 1
            return lzo(packet, size)
    levels = chunks_seen = header_blocks = 0
    for number, path in enumerate(paths):
        game_written = path.read_bytes()
        parsed = read_slot(game_written, flags[:GLOBAL_SECTIONS], flags[GLOBAL_SECTIONS:], decoder)
        if write_slot(parsed) != game_written:
            raise ValueError(f"{path.name}: rebuilt slot differs from the game-written slot")
        if number == 0:
            moved_player(parsed, game_written)
        blocks, chunks = stored_part_count(parsed)
        levels += blocks
        chunks_seen += chunks
        header_blocks += sum(1 for _start, length in parse_header(game_written, len(game_written))["levels"] if length)
    if header_blocks != levels:
        raise ValueError(f"{levels} level blocks read, lol3_save_header lists {header_blocks}")
    if decoder and decoded != chunks_seen:
        raise ValueError(f"{decoded} packets decoded of {chunks_seen}")
    plural = "" if len(paths) == 1 else "s"
    layout = (f"{len(paths)} game-written slot{plural}, {levels} level blocks and {chunks_seen:,} stored LZO packets "
              "rebuilt byte-identical from fields (packets copied, no compressor tested); "
              "a player-x edit reads back through lol3_save_header")
    if not decoder:
        return f"CHECK save_write: SKIP: no liblzo2, packets not decoded; {layout}"
    return f"CHECK save_write: {layout}; liblzo2 decoded each packet to its expanded length"


def main():
    parser = lol3_cli.tool_args(__doc__, writes=False)
    parser.add_argument("slot", type=Path, nargs="?",
                        help="one game-written slot, or a folder of them (default: SAVEGAME next to DAT)")
    args = parser.parse_args()
    if not args.check:
        parser.error("give --check to compare rebuilt saves in memory")
    if args.slot and not args.slot.exists():
        parser.error(f"no such slot or folder: {args.slot}")
    print(check(args.data, args.slot))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
