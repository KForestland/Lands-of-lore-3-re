#!/usr/bin/env python3
"""Bake one cached LoL3 texture to PNG or check the cache in memory.

  lol3_texture_png.py --data DAT --offset 0x12C6E2 --out ../texture.png
  lol3_texture_png.py --data DAT --check
  lol3_texture_png.py --data DAT --check --decode-slices   # liblzo2

An offset is an absolute texture-record position in the game-folder cdcache.wsx.
--check counts every occupied bank's populated mip records, checks linked SMD
frame headers, requires the full-width span shape for flags 0x02AC and 0x82AC
(a mismatch counts as a failure), and reports classes whose pixel route is open.
It writes no images.
"""
import struct
import zlib
from collections import Counter, defaultdict
from contextlib import ExitStack
from pathlib import Path

import lol3_cli
from extract_wsx_entries import wsx_name_hash
from lol3_texture_archive import cache_rows
from lol3_texture_palettes import bank_directory, u32
from lol3_texture_spans import cache_path
from walk_lmf_leaves import lzo_decoder

RAW_FLAGS = frozenset((0x008B, 0x00A9, 0x00C3, 0x00E1,
                       0x808B, 0x80A9, 0x80C3, 0x80E1))
SPAN_FLAGS = frozenset((0x028E, 0x02C6, 0x828E))
SLICE_FLAGS = frozenset((0x021A, 0x021E, 0x0252, 0x0256))
UNCONFIRMED_FLAGS = frozenset((0x02AC, 0x82AC))


def cache_textures(data, allocations):
    """Follow the allocator and the bank's descriptor/mip directory."""
    for bank, length in sorted(allocations):
        end = bank + length
        if bank < 0 or length < 12 or end > len(data):
            raise ValueError(f"invalid allocation at {bank:#x}")
        if struct.unpack_from("<III", data, bank) == (0, 38, 0x100):
            continue  # LMF allocation
        _, directory, pixels, palettes, palette_count, count = bank_directory(data, bank, end)
        for index in range(count):
            descriptor = bank + directory + 58 * index
            arm = data[descriptor + 0xD]
            key, = struct.unpack_from("<H", data, descriptor + 2)
            for mip in range(5):
                size = u32(data, descriptor + 0x26 + 4 * mip)
                if size == 0:
                    continue
                offset = bank + pixels + u32(data, descriptor + 0x12 + 4 * mip)
                if size < 12 or offset + size > bank + palettes:
                    raise ValueError(f"mip {mip} at descriptor {descriptor:#x} exceeds the payload")
                if arm != 3 or key >= palette_count:
                    raise ValueError(f"unbound palette for descriptor {descriptor:#x}")
                yield offset, size, bank, descriptor, mip, key, bank + palettes + 512 * key


def rgba_palette(source, transparent_zero):
    """Project the type-11 scratch words to RGBA using their RGB555 bits."""
    words = struct.unpack("<256H", source)
    baked = [0 if transparent_zero else 0x8000]
    baked.extend((word or 1) | 0x8000 for word in words[1:])
    return tuple(bytes((((word >> 10) & 31) << 3, ((word >> 5) & 31) << 3,
                        (word & 31) << 3, 255 if word & 0x8000 else 0)) for word in baked)


def texture_payload(record):
    flags, width, height, length = struct.unpack_from("<IHHI", record)
    if not (1 <= width <= 1024 and 1 <= height <= 1024 and length == len(record) - 12):
        raise ValueError("invalid texture header or payload length")
    return flags, width, height, record[12:]


def slice_directory(data_dir, stack):
    entries = defaultdict(list)
    for path in lol3_cli.wsx_files(data_dir):
        if path.stem.upper() not in ("SLICECD1", "SLICECD2", "SLICECD3", "SLICECD4"):
            continue
        source = stack.enter_context(path.open("rb"))
        count, size = struct.unpack("<HI", source.read(6))
        base = 6 + 12 * count
        if base + size != path.stat().st_size:
            raise ValueError(f"{path.name}: incorrect WSX length")
        for key, start, length in struct.iter_unpack("<III", source.read(12 * count)):
            if start + length > size:
                raise ValueError(f"{path.name}: entry outside WSX data")
            entries[key].append((source, base + start, length))
    return entries


def slice_reference(payload):
    if len(payload) not in (344, 1380):
        raise ValueError("unexpected SMD reference length")
    kind, identity, frame = struct.unpack_from("<III", payload)
    name = payload[0x10:0x20].split(b"\x00", 1)[0].decode("ascii")
    start, expanded, stored = struct.unpack_from("<III", payload, 0x20)
    if kind != 3 or not name.lower().endswith(".smd") or expanded < 16 or 0 < stored < 16:
        raise ValueError("invalid SMD frame reference")
    return name, (kind, identity, frame), start, expanded, stored


def find_slice_frame(directory, name, header, start, length):
    candidates = directory.get(wsx_name_hash(f"slice\\{name}"), ())
    if not candidates:
        raise ValueError(f"slice\\{name} is absent from SLICECD archives")
    for source, base, size in candidates:
        if start + length <= size:
            source.seek(base + start)
            if struct.unpack("<III", source.read(12)) == header:
                return source, base + start
    raise ValueError(f"no matching SMD frame header in slice\\{name}")


def slice_run_count(frame, slices):
    """Check the row directory and the native bit-0x20 run layout."""
    cursor = 16 + 4 * slices
    runs = 0
    for index in range(slices):
        if u32(frame, 16 + 4 * index) != cursor:
            raise ValueError(f"slice {index} does not start at the preceding boundary")
        count = u32(frame, cursor)
        cursor += 4
        runs += count
        for _ in range(count):
            length = u32(frame, cursor)
            cursor += 6 + 2 * length
            if cursor > len(frame):
                raise ValueError(f"slice {index} run exceeds the frame")
    if cursor != len(frame):
        raise ValueError("slice directory and runs do not cover the frame")
    return runs


def check_slice_reference(payload, directory, decode=None):
    name, header, start, expanded, stored = slice_reference(payload)
    length = stored or expanded
    source, position = find_slice_frame(directory, name, header, start, length)
    runs = 0
    if decode is not None:
        if (u32(payload, 0x0C) & 0x30) != 0x20:
            raise ValueError("SMD reference does not select the bit-0x20 run layout")
        source.seek(position)
        frame = source.read(length)
        if len(frame) != length:
            raise ValueError("truncated SMD frame")
        if stored:
            frame = frame[:16] + decode(frame[16:], expanded - 16)
        runs = slice_run_count(frame, u32(payload, 0x2C))
    return name, runs


def decode_texture(record, palette):
    flags, width, height, payload = texture_payload(record)
    if flags in RAW_FLAGS:
        if len(payload) != width * height:
            raise ValueError("indexed texture length differs from width × height")
        return width, height, b"".join(map(palette.__getitem__, payload))
    if flags in SLICE_FLAGS:
        name, (_, _, frame), _, _, _ = slice_reference(payload)
        raise ValueError(f"SMD reference to slice\\{name} frame {frame}; slice rendering is open")
    if flags not in SPAN_FLAGS:
        raise ValueError(f"pixel route for flags {flags:#06x} is unconfirmed")

    rgba = bytearray(4 * width * height)
    cursor = 0
    for y in range(height):
        if cursor + 4 > len(payload):
            raise ValueError(f"row {y} has no complete header")
        column_flags, count = struct.unpack_from("<HH", payload, cursor)
        column = column_flags & 0x3FFF
        cursor += 4
        if column + count > width or cursor + count > len(payload):
            raise ValueError(f"row {y} exceeds its bounds")
        start = 4 * (y * width + column)
        # The unscaled type-11 bake reads each stored byte through its lookup.
        rgba[start:start + 4 * count] = b"".join(map(palette.__getitem__, payload[cursor:cursor + count]))
        cursor += count
    if cursor != len(payload):
        raise ValueError("unread bytes after the final row")
    return width, height, bytes(rgba)


def png_bytes(width, height, rgba):
    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload))

    stride = 4 * width
    if len(rgba) != stride * height:
        raise ValueError("RGBA output does not match the frame size")
    scanlines = b"".join(b"\0" + rgba[start:start + stride] for start in range(0, len(rgba), stride))
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(scanlines)) + chunk(b"IEND", b"")


def main(stack):
    parser = lol3_cli.tool_args(__doc__, out_help="write one PNG outside the repository and game tree")
    parser.add_argument("--offset", type=lambda value: int(value, 0))
    parser.add_argument("--decode-slices", action="store_true",
                        help="with --check, expand original SMD frames and check every run (liblzo2)")
    args = parser.parse_args()
    if args.check and (args.offset is not None or args.out):
        parser.error("--check takes neither --offset nor --out")
    if not args.check and (args.offset is None or not args.out):
        parser.error("give --offset and --out to export a texture")
    if args.decode_slices and not args.check:
        parser.error("--decode-slices requires --check")
    try:
        if cache_path(args.data) is None:
            if args.check:
                print("CHECK texture_png: SKIP: game-folder cdcache.wsx is absent")
                return 0
            raise ValueError("game-folder cdcache.wsx is absent")
        path, allocations = cache_rows(args.data)
        cache = path.read_bytes()
        decoded = Counter()
        slice_frames = Counter()
        slice_runs = Counter()
        unconfirmed = Counter()
        seen = set()
        banks = set()
        errors = 0
        slices = slice_directory(args.data, stack) if args.check else {}
        decode_slices = lzo_decoder() if args.decode_slices else None
        for offset, size, bank, descriptor, mip, key, source in cache_textures(cache, allocations.values()):
            if offset in seen:
                raise ValueError(f"duplicate texture record at {offset:#x}")
            seen.add(offset)
            if not args.check and offset != args.offset:
                continue
            record = cache[offset:offset + size]
            try:
                flags, width, height, payload = texture_payload(record)
                banks.add(bank)
                if args.check and flags in SLICE_FLAGS:
                    name, runs = check_slice_reference(payload, slices, decode_slices)
                    slice_frames[name] += 1
                    slice_runs[flags] += runs
                    continue
                if args.check and flags in UNCONFIRMED_FLAGS:
                    stride = width + 4
                    if len(payload) != height * stride or any(
                        struct.unpack_from("<HH", payload, row * stride) != (0, width)
                        for row in range(height)
                    ):
                        raise ValueError("record differs from the measured full-width spans")
                    unconfirmed[flags] += 1
                    continue
                palette = rgba_palette(cache[source:source + 512], cache[descriptor + 8] & 2)
                width, height, rgba = decode_texture(record, palette)
            except (ValueError, struct.error) as error:
                if not args.check:
                    raise
                errors += 1
                print(f"{offset:#x}: {error}")
                continue
            if args.check:
                decoded[flags] += 1
                continue
            output = Path(args.out).resolve()
            repo = Path(__file__).resolve().parents[1]
            if any(root in output.parents for root in (repo, path.resolve().parent)):
                parser.error("--out must be outside the repository and game tree")
            with output.open("xb") as destination:
                destination.write(png_bytes(width, height, rgba))
            print(f"{offset:#x}: {width}x{height}, mip {mip}, arm 3 palette {key} at {source:#x}")
            return 0
        if not args.check:
            raise ValueError(f"{args.offset:#x} is not a cached texture-record offset")
        counts = ", ".join(f"{flag:#06x}={count}" for flag, count in sorted(unconfirmed.items()))
        slice_result = f"{sum(slice_frames.values())} SMD references verified ({len(slice_frames)} names)"
        if args.decode_slices:
            per_flag = ", ".join(f"{flag:#06x}={count}" for flag, count in sorted(slice_runs.items()))
            slice_result += f", {sum(slice_runs.values())} SMD runs framed ({per_flag})"
        print(f"CHECK texture_png: {len(seen)} records, {sum(decoded.values())} decoded, "
              f"{slice_result}, "
              f"{sum(unconfirmed.values())} unconfirmed ({counts or 'none'}), {errors} failures; "
              f"arm 3 source palettes in {len(banks)} banks; in the game-written game-folder cdcache.wsx")
        return int(not seen or errors > 0)
    except (OSError, ValueError, struct.error) as error:
        parser.exit(1, f"texture PNG: {error}\n")


if __name__ == "__main__":
    with ExitStack() as stack:
        raise SystemExit(main(stack))
