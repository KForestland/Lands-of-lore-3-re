#!/usr/bin/env python3
"""Read the level archives' light maps and texture banks in DAT and the packed SMD frames those banks name, re-encode LZO1X with liblzo2 and re-read.

This is a real compressor (liblzo2 lzo1x_1_compress), not a copy of the stored
groups: the new packed bytes differ from the original ones, and the check
requires the decoded bytes to be identical. The SMD frames are found from the
mip directories of the 18 level banks and the two shared banks in LOCAL.WSX;
a game-written cdcache.wsx beside DAT (or --cache) is optional and only adds
its own references. Without liblzo2 the check prints one SKIP line. Writes
nothing.
"""
from contextlib import ExitStack
from ctypes import CDLL, POINTER, byref, c_size_t, c_void_p, create_string_buffer
from ctypes.util import find_library
from pathlib import Path
import struct

from cli_errors import run_cli
from extract_wsx_entries import parse_wsx, wsx_name_hash
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
    return rebuilt, decoded


def check_slices(data, allocations, arm, directory, seen, encode, decode):
    """Follow shipped or cache mip references to their source frame spans."""
    count = 0
    for at, length, *_ in cache_textures(data, allocations, expected_arm=arm):
        flags = struct.unpack_from("<I", data, at)[0]
        if flags not in SLICE_FLAGS:
            continue
        _, _, _, payload = texture_payload(data[at:at + length])
        name, header, start, expanded, stored = slice_reference(payload)
        if not stored:
            continue
        source, position = find_slice_frame(directory, name, header, start, stored)
        count += 1
        key = source.name, position, stored, expanded
        if key in seen:
            continue
        seen.add(key)
        source.seek(position + 16)
        raw = decode(source.read(stored - 16), expanded - 16)
        if decode(encode(raw), len(raw)) != raw:
            raise ValueError("rebuilt SMD frame bytes differ")
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
    banks = blocks = references = 0
    checked_frames = set()
    with ExitStack() as stack:
        directory = slice_directory(data, stack)
        for _, original in texture_entries(data):
            _, decoded_blocks = write_texture(original, encode, decode)
            bank = b"".join(decoded_blocks)
            banks += 1
            blocks += len(decoded_blocks)
            references += check_slices(bank, [(0, len(bank))], 3, directory, checked_frames, encode, decode)
        shared_arms = {wsx_name_hash(f"GLOBAL\\{name}.TEX"): arm for name, arm in (("GLOBAL", 1), ("SPELL", 2))}
        local = next(path for path in lol3_cli.wsx_files(data) if path.stem.upper() == "LOCAL")
        shared = [(shared_arms[row["hash"]], row["blob"])
                  for row in parse_wsx(local)["entries"] if row["hash"] in shared_arms]
        if sorted(arm for arm, _ in shared) != [1, 2]:
            raise ValueError("shared texture banks are absent")
        for arm, bank in shared:
            references += check_slices(bank, [(0, len(bank))], arm, directory, checked_frames, encode, decode)
        shipped_frames = len(checked_frames)
        if cache_file is not None:
            path, allocations = cache_rows(data, cache_file)
            from_cache = check_slices(path.read_bytes(), allocations.values(), 3, directory,
                                      checked_frames, encode, decode)
    if (light_maps, groups, members, banks, blocks, references, shipped_frames) != (
            18, 5256, 424288, 18, 465, 33068, 15990):
        raise ValueError("LoL3 LZO1X corpus counts differ")
    cache_note = (f"; the game-written cache's {from_cache:,} packed references reach "
                  f"{len(checked_frames) - shipped_frames} further frames" if cache_file is not None
                  else "; no game-written cache, its references not followed")
    print(f"CHECK LZO write: liblzo2 re-encodes {members:,} LMF members in {groups:,} groups "
          f"({light_maps - same} of {light_maps} light maps differ from the original packed bytes) "
          f"and {blocks} texture blocks; {references:,} packed SMD references in the 20 shipped texture banks, "
          f"{shipped_frames:,} distinct frames{cache_note}; decoded bytes identical; a changed member re-reads")


def main():
    parser = lol3_cli.tool_args(__doc__, writes=False)
    parser.add_argument("--cache", help="optional game-written cdcache.wsx whose packed SMD references are also followed")
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
