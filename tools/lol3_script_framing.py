#!/usr/bin/env python3
"""Verify LoL3 MAP script framing using the English retail PE size table.

  lol3_script_framing.py --data DAT          # per-level and per-opcode counts
  lol3_script_framing.py --data DAT --check  # check the retail corpus
  lol3_script_framing.py --data DAT --subcommands
  lol3_script_framing.py --data DAT --dispatch
"""
from cli_errors import run_cli
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
# Stored indirect object commands by (opcode, selector byte +1); the selector is the object type
# (docs/lol3-script-opcodes.md#per-class-effects-of-the-indirect-commands).
EXPECTED_SELECTORS = {(0x01, 32): 1_175, (0x03, 1): 1_021, (0x03, 2): 346, (0x03, 16): 16, (0x03, 192): 416,
                      (0x0D, 2): 5_213, (0x0D, 3): 56}


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


def level_map_entries(data_dir):
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
                yield stem, 54 + offset, payload
                break


def level_maps(data_dir):
    for stem, _, payload in level_map_entries(data_dir):
        yield stem, payload


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


def selector_counts(payload, sizes):
    """(opcode, selector) counts for the +0xC0 commands 0x01, 0x03 and 0x0D in one MAP's stream."""
    stream, counts, pos = map_range(payload, 0x44, 0x8C), Counter(), 0
    while pos < len(stream):
        if stream[pos] in (0x01, 0x03, 0x0D):
            counts[stream[pos], stream[pos + 1]] += 1
        pos += sizes[stream[pos]]
    return counts


OBJECT_SLOTS = 0x449A1C
ARRAY_OPCODES = (0xC6, 0xC7, 0xCE, 0xCF)


def object_slot_lines(image):
    """The 28 object-opcode slots. Region byte-index length is not a named constant here."""
    lines = ["object opcode slots 28"]
    base = OBJECT_SLOTS - CODE_BIAS
    for index in range(28):
        value, = unpack_from("<I", image, base + 4 * index)
        lines.append(f"slot {index + 1} opcode 0x{index + 1:02X}: {value:#x}")
    return "\n".join(lines) + "\n"


def subcommand_lines(pairs, sizes):
    """Class selectors, creature and effect subcommands, 0xC4 flag bits and array indexes.

    Counts are the object stream at header +0x44, the stream the opcode page tabulates.
    """
    selectors, creature, effect = Counter(), Counter(), Counter()
    arrays = Counter()
    c4_bits, c4_n, c4_speed0 = Counter(), 0, 0
    effect_n = n1c = bit0 = bit1 = 0
    for _stem, payload in pairs:
        selectors.update(selector_counts(payload, sizes))
        stream, pos = map_range(payload, 0x44, 0x8C), 0
        while pos < len(stream):
            opcode = stream[pos]
            row = stream[pos:pos + sizes[opcode]]
            if opcode == 0x0D and row[1] == 2:
                creature[row[4]] += 1
            elif opcode == 0x0F:
                effect[row[4]] += 1
                effect_n += 1
            elif opcode == 0x1C:
                n1c += 1
                word, = unpack_from("<H", row, 4)
                bit0 += word & 1
                bit1 += (word >> 1) & 1
            elif opcode == 0xC4:
                c4_n += 1
                for bit in (0, 2, 3, 5, 6):
                    c4_bits[bit] += (row[6] >> bit) & 1
                c4_speed0 += row[7] == 0
            elif opcode in ARRAY_OPCODES:
                arrays[opcode, row[4]] += 1
            pos += sizes[opcode]
    lines = ["selectors"]
    for (opcode, selector), count in sorted(selectors.items()):
        lines.append(f"opcode 0x{opcode:02X} selector {selector}: {count}")
    lines.append("creature opcode 0x0D selector 2 subcommand +4")
    for value in range(33):
        lines.append(f"subcommand {value}: {creature[value]}")
    lines.append(f"effect opcode 0x0F actions {effect_n}")
    for value, count in sorted(effect.items()):
        lines.append(f"action {value}: {count}")
    lines.append(f"opcode 0x1C records {n1c} u16+4 bit0 {bit0} bit1 {bit1}")
    lines.append(f"opcode 0xC4 records {c4_n} speed +7 zero {c4_speed0}")
    for bit in (0, 2, 3, 5, 6):
        lines.append(f"opcode 0xC4 byte+6 bit {bit}: {c4_bits[bit]}")
    lines.append("array byte +4")
    for (opcode, index), count in sorted(arrays.items()):
        lines.append(f"opcode 0x{opcode:02X} index {index}: {count}")
    return "\n".join(lines) + "\n"


def main():
    parser = lol3_cli.tool_args(__doc__, writes=False)
    parser.add_argument("--subcommands", action="store_true", help="print selector and subcommand counts")
    parser.add_argument("--dispatch", action="store_true", help="print the 28 object opcode slots")
    args = parser.parse_args()
    if args.out:
        parser.error("use standard output for the aggregate counts")
    if args.subcommands or args.dispatch:
        if args.check or (args.subcommands and args.dispatch):
            parser.error("pass only one of --subcommands, --dispatch or --check")
    try:
        if args.dispatch or args.subcommands:
            data_dir = Path(args.data).resolve()
            image = (data_dir.parent / "LOL3.DAT").read_bytes()
            if args.dispatch:
                if sha256(image).hexdigest() != RETAIL_PE:
                    raise ValueError("LOL3.DAT does not match the documented English retail executable")
                print(object_slot_lines(image), end="")
                return 0
            sizes = native_sizes(image)
            print(subcommand_lines(level_maps(data_dir), sizes), end="")
            return 0
        data_dir = Path(args.data).resolve()
        sizes = native_sizes((data_dir.parent / "LOL3.DAT").read_bytes())
        maps = total_bytes = refs = records = embedded = resume = 0
        opcodes, selectors = Counter(), Counter()
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
            selectors.update(selector_counts(payload, sizes))
            if not args.check:
                print(f"{stem}: {length:,} bytes, {entries:,} index entries, {count:,} record boundaries")
        metrics = (maps, total_bytes, refs, records, opcodes[GROUP_HEADER], len(opcodes), embedded, resume)
        if args.check:
            if metrics != EXPECTED:
                raise ValueError(f"retail corpus totals {metrics} differ from {EXPECTED}")
            if dict(selectors) != EXPECTED_SELECTORS:
                raise ValueError(f"indirect command selectors {dict(selectors)} differ from {EXPECTED_SELECTORS}")
            print(f"CHECK script_framing: {maps} MAPs, {total_bytes:,} bytes, {refs:,} index entries on "
                  f"{records:,} boundaries, {opcodes[GROUP_HEADER]:,} group headers, {len(opcodes)} of 39 opcodes occur; "
                  f"opcodes 0x01/0x03/0x0D by target type match ({sum(selectors.values()):,} records)")
        else:
            for opcode, size in sizes.items():
                print(f"0x{opcode:02X}: {size} bytes, {opcodes[opcode]:,} occurrences")
        return 0
    except (OSError, ValueError, struct_error) as error:
        parser.exit(1, f"script framing: {error}\n")


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
