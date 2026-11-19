#!/usr/bin/env python3
"""Count the creature mitigation records and the item-use handler indexes in the original files.

  lol3_combat_census.py --data DAT          # print the two census tables
  lol3_combat_census.py --data DAT --check  # check the English retail counts
  lol3_combat_census.py --data DAT --mitigation
  lol3_combat_census.py --data DAT --items
  lol3_combat_census.py --data DAT --modes

Mitigation records: bytes +0x00-+0x13 of each 147-byte field-3 row of the 18 level ODFs
(four selector bytes, then four u16 mask pairs), which the creature hit receiver passes to
the resolver (docs/lol3-combat-dispatch.md#where-the-mitigation-records-come-from).
Item indexes: definition dword +0x4B of the 343 GLOBAL.ODF item rows with +0x3F bit 1
clear, and the 124 handler pointers at 0x54B918 in LOL3.DAT
(docs/lol3-item-dispatch.md#regular-handler-examples). The census prints counts.
The other flags print the named fields.
"""
from cli_errors import run_cli
from collections import Counter
from pathlib import Path
from struct import iter_unpack, unpack_from

import lol3_cli
from extract_wsx_entries import wsx_name_hash
from lol3_script_framing import CODE_BIAS, RETAIL_PE, native_sizes

DATA_BIAS = 0x401800
ITEM_TABLE, ITEM_ROWS, ITEM_STRIDE = 0x3A56, 343, 139
HANDLERS, HANDLER_COUNT = 0x54B918, 124
EXPECTED_SELECTORS = {2: 58, 3: 52, 4: 35, 5: 71, 6: 26, 7: 176, 8: 2, 9: 9, 10: 35}


def level_odf_rows(data_dir):
    for path in lol3_cli.wsx_files(data_dir):
        raw = path.read_bytes()
        count, _ = unpack_from("<HI", raw)
        if count != 4:
            continue
        stem = path.stem.upper()
        key = wsx_name_hash(f"LEVELS\\{stem}\\{stem}.ODF")
        for stored, offset, length in iter_unpack("<III", raw[6:54]):
            if stored == key:
                odf = raw[54 + offset:54 + offset + length]
                start, rows = unpack_from("<I", odf, 0x10)[0], unpack_from("<I", odf, 0x48)[0]
                for i in range(rows):
                    yield odf[start + 147 * i:start + 147 * i + 20]


def global_wsx(data_dir):
    for path in lol3_cli.wsx_files(data_dir):
        if path.name.upper() == "GLOBAL.WSX":
            return path.read_bytes()
    raise ValueError("GLOBAL.WSX not found")


def census(data_dir, image):
    rows, records, selectors = 0, Counter(), Counter()
    for rec in level_odf_rows(data_dir):
        rows += 1
        records[bytes(rec)] += 1
        for j in range(4):
            if rec[j] > 1:
                selectors[rec[j]] += 1
    glob = global_wsx(data_dir)
    indexes = Counter()
    for i in range(ITEM_ROWS):
        row = glob[ITEM_TABLE + ITEM_STRIDE * i:ITEM_TABLE + ITEM_STRIDE * (i + 1)]
        if not row[0x3F] & 2:
            indexes[unpack_from("<I", row, 0x4B)[0]] += 1
    pointers = [unpack_from("<I", image, HANDLERS - DATA_BIAS + 4 * k)[0] for k in range(HANDLER_COUNT)]
    return rows, records, selectors, indexes, pointers


def mitigation_lines(records):
    """Four selector bytes and four mask pairs for each distinct 20-byte record."""
    lines = [f"mitigation records {sum(records.values())} distinct {len(records)}"]
    ordered = sorted(records.items(), key=lambda item: (-item[1], item[0]))
    for record, count in ordered:
        selectors = " ".join(f"{byte:#x}" for byte in record[:4])
        pairs = unpack_from("<8H", record, 4)
        masks = " ".join(f"{pairs[index]:#x}/{pairs[index + 1]:#x}" for index in range(0, 8, 2))
        lines.append(f"selectors {selectors} masks {masks} rows {count}")
    return "\n".join(lines) + "\n"


def item_lines(archive):
    """Named fields of each regular definition. Special rows are not in this list."""
    lines = []
    for index in range(ITEM_ROWS):
        row = archive[ITEM_TABLE + ITEM_STRIDE * index:ITEM_TABLE + ITEM_STRIDE * (index + 1)]
        if row[0x3F] & 2:
            continue
        key, = unpack_from("<I", row, 0x73)
        flags, = unpack_from("<I", row, 0x3F)
        handler, = unpack_from("<I", row, 0x4B)
        state, = unpack_from("<I", row, 0x4F)
        step, = unpack_from("<H", row, 0x7D)
        lines.append(
            f"definition {index}: +0x73 {key:#x} +0x3f {flags:#x} +0x4b {handler:#x} "
            f"+0x4f {state:#x} +0x7d {step:#x}")
    return f"regular definitions {len(lines)}\n" + "\n".join(lines) + "\n"


def mode_lines(image):
    """Behavior table at 0x4B5C44 (15 slots) and action table at 0x4B757C (18 slots)."""
    lines = ["behavior slots 15", "action slots 18"]
    for index in range(15):
        value, = unpack_from("<I", image, 0x4B5C44 - CODE_BIAS + 4 * index)
        lines.append(f"behavior {index}: {value:#x}")
    for index in range(18):
        value, = unpack_from("<I", image, 0x4B757C - CODE_BIAS + 4 * index)
        lines.append(f"action {index}: {value:#x}")
    return "\n".join(lines) + "\n"


def main():
    parser = lol3_cli.tool_args(__doc__, writes=False)
    parser.add_argument("--items", action="store_true", help="print regular definition fields")
    parser.add_argument("--mitigation", action="store_true", help="print mitigation selector and mask fields")
    parser.add_argument("--modes", action="store_true", help="print behavior and action slot values")
    args = parser.parse_args()
    if args.out:
        parser.error("use standard output for the counts")
    chosen = [name for name in ("items", "mitigation", "modes") if getattr(args, name)]
    if chosen:
        if args.check or len(chosen) != 1:
            parser.error("pass only one of --items, --mitigation, --modes or --check")
    try:
        data_dir = Path(args.data).resolve()
        image = (data_dir.parent / "LOL3.DAT").read_bytes()
        native_sizes(image)  # checks the retail executable by its hash
        if args.modes:
            print(mode_lines(image), end="")
            return 0
        rows, records, selectors, indexes, pointers = census(data_dir, image)
        if args.mitigation:
            print(mitigation_lines(records), end="")
            return 0
        if args.items:
            print(item_lines(global_wsx(data_dir)), end="")
            return 0
        distinct = len(records)
        code = all(0x401000 <= p < 0x538000 for p in pointers)
        if args.check:
            got = (rows, distinct, dict(selectors), sum(indexes.values()), len(indexes), indexes[0],
                   max(indexes), code)
            want = (334, 57, EXPECTED_SELECTORS, 258, 114, 117, 123, True)
            if got != want:
                raise ValueError(f"census {got} differs from {want}")
            print(f"CHECK combat_census: {rows} creature rows, {distinct} distinct mitigation records, "
                  f"{sum(selectors.values())} selector entries; {sum(indexes.values())} regular items on "
                  f"{len(indexes)} handler indexes ({indexes[0]} on the stub), {HANDLER_COUNT} code pointers")
        else:
            print(f"{rows} creature rows, {distinct} distinct mitigation records")
            for sel, n in sorted(selectors.items()):
                print(f"selector {sel}: {n} entries")
            for k, n in sorted(indexes.items()):
                print(f"index {k}: {n} definitions, handler 0x{pointers[k]:X}")
        return 0
    except (OSError, ValueError, IndexError) as error:
        parser.exit(1, f"combat census: {error}\n")


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
