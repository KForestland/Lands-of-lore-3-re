#!/usr/bin/env python3
"""Read the level archives' light maps and texture banks in DAT (and the SMD frames the game-written cache names), re-encode LZO1X with liblzo2 and re-read.

This is a real compressor (liblzo2 lzo1x_1_compress), not a copy of the stored
groups: the new packed bytes differ from the original ones, and the check
requires the decoded bytes to be identical. Without liblzo2 the check prints
one SKIP line. Without the game-written cdcache.wsx beside DAT the SMD part is
skipped and the rest still runs. Writes nothing.
"""
from contextlib import ExitStack
from ctypes import CDLL, POINTER, byref, c_size_t, c_void_p, create_string_buffer
from ctypes.util import find_library
from pathlib import Path
import struct

from cli_errors import run_cli
from extract_wsx_entries import parse_wsx
import lol3_cli
from lol3_texture_archive import cache_rows, chunks, texture_entries
from lol3_texture_png import SLICE_FLAGS, cache_textures, find_slice_frame, slice_directory, slice_reference, texture_payload
from lol3_texture_spans import cache_path
from walk_lmf_leaves import lmf_groups, lzo_decoder


def lzo_encoder(library=None):
    library = library or find_library("lzo2")
    if not library:
        raise ValueError("LZO1X encoding needs liblzo2")
    compress = CDLL(library).lzo1x_1_compress
    compress.argtypes = [c_void_p, c_size_t, c_void_p, POINTER(c_size_t), c_void_p]
    # Reserve more than the dictionary workspace on supported 32/64-bit hosts.
    workspace = create_string_buffer(1 << 20)

    def encode(raw):
        output = create_string_buffer(len(raw) + len(raw) // 16 + 67)
        size = c_size_t(len(output))
        if compress(raw, len(raw), output, byref(size), workspace) or size.value > len(output):
            raise ValueError("LZO1X encoding failed")
        return output.raw[:size.value]

    return encode


def write_light_map(original, encode, decode, edit=None):
    """Rebuild group offsets, continuation offsets and the LZO data pool.

    edit(group_index, expanded) may return changed bytes of the same length;
    the rebuilt map must then re-read with those bytes."""
    original_groups = list(lmf_groups(original))
    pool_at, rows_size = struct.unpack_from("<II", original, 0x0C)
    header = bytearray(original[:0x100])
    rows = bytearray(original[0x100:0x100 + rows_size])
    pool = bytearray()
    expected = []
    for number, group in enumerate(original_groups):
        start, packed = group["offset"], group["packed"]
        expanded = decode(original[start:start + packed], group["expanded"])
        if edit:
            expanded = edit(number, expanded)
            if len(expanded) != group["expanded"]:
                raise ValueError("an edit must keep the LMF member lengths")
        expected.append(expanded)
        replacement = encode(expanded)
        if not 0 < len(replacement) <= 0x3FFFF:
            raise ValueError("new LMF packed group exceeds the 18-bit length field")
        relative = len(pool)
        first = group["first_row"] * 16
        old_packed = struct.unpack_from("<I", rows, first + 12)[0]
        struct.pack_into("<I", rows, first + 12, (old_packed & ~0x3FFFF) | len(replacement))
        for index, length in enumerate(group["lengths"]):
            struct.pack_into("<I", rows, first + index * 16, relative)
            relative += length
        pool.extend(replacement)
    struct.pack_into("<I", header, 0x14, len(pool))
    rebuilt = bytes(header + rows + pool)
    if len(header) + len(rows) != pool_at:
        raise ValueError("LMF pool start changed")
    check_groups = list(lmf_groups(rebuilt))
    if len(check_groups) != len(original_groups):
        raise ValueError("LMF group count changed")
    for before, after, wanted in zip(original_groups, check_groups, expected):
        if before["lengths"] != after["lengths"]:
            raise ValueError("LMF member boundaries changed")
        off = after["offset"]
        if decode(rebuilt[off:off + after["packed"]], after["expanded"]) != wanted:
            raise ValueError("rebuilt light-map member bytes differ")
    return rebuilt, len(original_groups), sum(len(group["lengths"]) for group in original_groups)


def write_texture(original, encode, decode):
    """Rebuild the .TE_ chunk lengths while preserving each decoded block."""
    header = original[:4]
    body = bytearray()
    decoded = []
    for packed, size in chunks(original):
        raw = decode(packed, size)
        data = encode(raw)
        body.extend(struct.pack("<I", len(data)))
        body.extend(data)
        decoded.append(raw)
    rebuilt = header + body + b"\0\0\0\0"
    reread = [decode(packed, size) for packed, size in chunks(rebuilt)]
    if reread != decoded:
        raise ValueError("rebuilt texture bank block bytes differ")
    return rebuilt, len(decoded)


def check_slices(data, cache_file, encode, decode):
    """Re-encode each distinct packed SMD frame that a game-written cache record points at."""
    cache_file, allocations = cache_rows(data, cache_file)
    cache = cache_file.read_bytes()
    seen = set()
    count = 0
    with ExitStack() as stack:
        directory = slice_directory(data, stack)
        for at, length, *_ in cache_textures(cache, allocations.values()):
            flags, _, _, payload = texture_payload(cache[at:at + length])
            if flags not in SLICE_FLAGS:
                continue
            name, header, start, expanded, stored = slice_reference(payload)
            if not stored:
                continue
            source, position = find_slice_frame(directory, name, header, start, stored)
            key = source.name, position, stored, expanded
            if key in seen:
                continue
            seen.add(key)
            source.seek(position + 16)
            raw = decode(source.read(stored - 16), expanded - 16)
            if decode(encode(raw), len(raw)) != raw:
                raise ValueError("rebuilt SMD frame bytes differ")
            count += 1
    return count


def mutation_check(original, encode, decode):
    """Flip one decoded byte of the first group: the map must change and re-read with the flip."""
    def flip(number, expanded):
        return bytes([expanded[0] ^ 0xFF]) + expanded[1:] if number == 0 else expanded

    group = next(lmf_groups(original))
    wanted = flip(0, decode(original[group["offset"]:group["offset"] + group["packed"]], group["expanded"]))
    rebuilt, _, _ = write_light_map(original, encode, decode, flip)
    first = next(lmf_groups(rebuilt))
    reread = decode(rebuilt[first["offset"]:first["offset"] + first["packed"]], first["expanded"])
    if rebuilt == write_light_map(original, encode, decode)[0] or reread != wanted:
        raise ValueError("a changed LMF member did not reach the rebuilt light map")


def check(data, cache_file, library):
    encode, decode = lzo_encoder(library), lzo_decoder()
    light_maps = groups = members = same = 0
    for path in lol3_cli.wsx_files(data):
        # Only level main archives pair a light map and a texture bank.
        with path.open("rb") as source:
            if source.read(2) != b"\4\0":
                continue
        for entry in parse_wsx(path)["entries"]:
            if entry["is_lmf"]:
                if not light_maps:
                    mutation_check(entry["blob"], encode, decode)
                rebuilt, group_count, member_count = write_light_map(entry["blob"], encode, decode)
                same += rebuilt == entry["blob"]
                light_maps += 1
                groups += group_count
                members += member_count
    banks = blocks = 0
    for _, original in texture_entries(data):
        _, count = write_texture(original, encode, decode)
        banks += 1
        blocks += count
    if (light_maps, groups, members, banks, blocks) != (18, 5256, 424288, 18, 465):
        raise ValueError("LoL3 LZO1X corpus counts differ")
    slices = (f"{check_slices(data, cache_file, encode, decode):,} distinct packed SMD frames named by the game-written cache"
              if cache_file is not None else "SMD frames SKIPPED (no game-written cache)")
    print(f"CHECK LZO write: liblzo2 re-encodes {members:,} LMF members in {groups:,} groups "
          f"({light_maps - same} of {light_maps} light maps differ from the original packed bytes) "
          f"and {blocks} texture blocks; {slices}; decoded bytes identical; a changed member re-reads")


def main():
    parser = lol3_cli.tool_args(__doc__, writes=False)
    parser.add_argument("--cache", help="optional game-written cdcache.wsx used to identify SMD frames")
    args = parser.parse_args()
    if not args.check:
        parser.error("give --check for LZO1X read-back")
    library = find_library("lzo2")
    if not library:
        print("CHECK LZO write: SKIP: liblzo2 unavailable")
        return 0
    check(args.data, cache_path(args.data, args.cache), library)
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
