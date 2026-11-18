#!/usr/bin/env python3
"""Verify LoL3 MAP script framing using the English retail PE size table.

  lol3_script_framing.py --data DAT          # per-level and per-opcode counts
  lol3_script_framing.py --data DAT --check  # check the retail corpus
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from struct import error as struct_error, iter_unpack, unpack_from

import lol3_cli
from extract_wsx_entries import wsx_name_hash

# English retail PE, docs/lol3-lmf-reader.md.
RETAIL_PE = "9a9eb04c8f404ebf68f439df4ec7dc6ad5cc230235d0f853059f636ff720ccea"
CODE_BIAS = 0x400C00
GROUP_HEADER = 0xF0
RESUME_COMMAND = 0x1B
EXPECTED = (18, 431_495, 54_966, 54_940, 12_306, 33, 14, 1_654)


def u32(data, at):
    return unpack_from("<I", data, at)[0]


def native_sizes(image):
    if sha256(image).hexdigest() != RETAIL_PE:
        raise ValueError("LOL3.DAT does not match the documented English retail executable")
    sizes = {}
    for opcode in range(1, 0xF1):
        index = image[0x4E5790 - CODE_BIAS + opcode - 1]
        target = u32(image, 0x4E56F0 - CODE_BIAS + 4 * index)
        if target == 0x4E56EF:
            continue
        start = target - CODE_BIAS
        if image[start] != 0xB8 or image[start + 5] != 0xC3:
            raise ValueError(f"unexpected size-return arm for opcode {opcode:#x}")
        sizes[opcode] = u32(image, start + 1)
    return sizes


def level_maps(data_dir):
    for path in lol3_cli.wsx_files(data_dir):
        with path.open("rb") as source:
            count, size = unpack_from("<HI", source.read(6))
            if count != 4:
                continue
            stem = path.stem.upper()
            key = wsx_name_hash(f"LEVELS\\{stem}\\{stem}.MAP")
            directory = tuple(iter_unpack("<III", source.read(48)))
            for stored_key, offset, length in directory:
                if stored_key != key:
                    continue
                if offset + length > size:
                    raise ValueError(f"{path.name}: MAP entry outside its archive")
                source.seek(54 + offset)
                payload = source.read(length)
                if len(payload) != length:
                    raise ValueError(f"{path.name}: truncated MAP entry")
                yield stem, payload
                break


def map_range(payload, location_field, size_field):
    start, size = u32(payload, location_field), u32(payload, size_field)
    if start + size > len(payload):
        raise ValueError(f"MAP range at header field {location_field:#x} crosses entry end")
    return memoryview(payload)[start:start + size]


def frame(payload, sizes):
    stream = map_range(payload, 0x44, 0x8C)
    index = map_range(payload, 0x4C, 0x98)
    offsets = [row[0] for row in iter_unpack("<I", index)]
    starts, opcodes = [], Counter()
    pos = 0
    while pos < len(stream):
        opcode = stream[pos]
        size = sizes.get(opcode, 0)
        if not size or pos + size > len(stream):
            raise ValueError(f"unsupported or incomplete opcode {opcode:#x} at stream offset {pos:#x}")
        starts.append(pos)
        opcodes[opcode] += 1
        pos += size
    if set(offsets) != set(starts):
        raise ValueError("the index and framed command boundaries disagree")
    embedded_headers = zero_resume_counts = 0
    for i, start in enumerate(starts):
        opcode = stream[start]
        if opcode == GROUP_HEADER:
            end = i + 1 + stream[start + 4]
            if end > len(starts):
                raise ValueError(f"group at {start:#x} crosses the end of the stream")
            embedded_headers += any(stream[child] == GROUP_HEADER for child in starts[i + 1:end])
        if opcode == RESUME_COMMAND:
            zero_resume_counts += stream[start + 9] == 0
    return len(stream), len(offsets), len(starts), opcodes, embedded_headers, zero_resume_counts


def main():
    parser = lol3_cli.tool_args(__doc__)
    args = parser.parse_args()
    if args.out:
        parser.error("use standard output for the aggregate counts")
    try:
        data_dir = Path(args.data).resolve()
        sizes = native_sizes((data_dir.parent / "LOL3.DAT").read_bytes())
        maps = total_bytes = refs = records = embedded = resume = 0
        opcodes = Counter()
        for stem, payload in level_maps(data_dir):
            try:
                length, entries, count, frequency, has_header, zero_resume = frame(payload, sizes)
            except (ValueError, struct_error) as error:
                raise ValueError(f"{stem}.WSX: {error}") from error
            maps += 1
            total_bytes += length
            refs += entries
            records += count
            embedded += has_header
            resume += zero_resume
            opcodes.update(frequency)
            if not args.check:
                print(f"{stem}: {length:,} bytes, {entries:,} index entries, {count:,} record boundaries")
        metrics = (maps, total_bytes, refs, records, opcodes[GROUP_HEADER], len(opcodes), embedded, resume)
        if args.check:
            if metrics != EXPECTED:
                raise ValueError(f"retail corpus totals {metrics} differ from {EXPECTED}")
            print(f"CHECK script_framing: {maps} MAPs, {total_bytes:,} bytes, {refs:,} index entries on "
                  f"{records:,} boundaries, {opcodes[GROUP_HEADER]:,} group headers, {len(opcodes)} opcodes")
        else:
            for opcode, size in sizes.items():
                print(f"0x{opcode:02X}: {size} bytes, {opcodes[opcode]:,} occurrences")
        return 0
    except (OSError, ValueError, struct_error) as error:
        parser.exit(1, f"script framing: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
