#!/usr/bin/env python3
"""Rebuild stored LoL3 TRR tag and text tables, keeping on-disk byte values."""
from pathlib import Path
import struct

from cli_errors import run_cli
import lol3_cli
from lol3_media_check import TRR_AT, read_at, trr_directory, wsx_rows


def read_trr(blob, name="TRR"):
    ids, offsets = trr_directory(blob, name)
    rows = []
    for key, start, end in zip(ids, offsets, offsets[1:]):
        field = blob[start + 4:end + 4]
        if not field.endswith(b"\0") or field.count(b"\0") != 1:
            raise ValueError(f"{name}: invalid text or tag at +{start + 4:#x}")
        rows.append((key, field[:-1]))
    return rows


def write_trr(rows):
    rows = tuple(rows)
    offsets = [8 * len(rows) + 4]
    payload = bytearray()
    for _, field in rows:
        if b"\0" in field:
            raise ValueError("TRR field contains NUL")
        payload.extend(field + b"\0")
        offsets.append(offsets[0] + len(payload))
    header = (len(rows), *(key for key, _ in rows), *offsets)
    return struct.pack(f"<{len(header)}I", *header) + payload


def trr_sources(data, indexed=False):
    for folder in (data, data.parent):
        for path in sorted(folder.iterdir()):
            if path.suffix.lower() == ".trr":
                blob = path.read_bytes()
                yield (path, 0, None, 0, blob) if indexed else (path, None, 0, blob)
        for path in lol3_cli.wsx_files(folder):
            if path.name.upper() == "CDCACHE.WSX":
                continue
            with path.open("rb") as source:
                for index, (key, start, size) in enumerate(wsx_rows(source)):
                    if size < 16:
                        continue
                    count = int.from_bytes(read_at(source, start, 4), "little")
                    if not 0 < count <= min(100000, (size - 8) // 8):
                        continue
                    first = int.from_bytes(read_at(source, start + 4 + 4 * count, 4), "little")
                    if first != 8 * count + 4:
                        continue
                    last = int.from_bytes(read_at(source, start + 4 + 8 * count, 4), "little")
                    if last != size - 4:
                        continue
                    blob = read_at(source, start, size)
                    try:
                        read_trr(blob, path.name)
                    except ValueError:
                        continue
                    yield (path, index, key, start, blob) if indexed else (path, key, start, blob)


def check(data, listing=False):
    files = messages = 0
    required = set(TRR_AT.values())
    for path, key, start, blob in trr_sources(data):
        rows = read_trr(blob, f"{path.name}+{start:#x}")
        if write_trr(rows) != blob:
            raise ValueError(f"{path.name}+{start:#x}: rebuilt TRR differs")
        if path.name.upper() == "LOCALLNG.WSX":
            required.discard(start)
        files += 1
        messages += len(rows)
        if listing:
            identifier = f"key={key:08X}" if key is not None else "loose"
            print(f"{path.name}+{start:#x} {identifier} size={len(blob)} rows={len(rows)}")
    if required:
        raise ValueError(f"missing dialogue or quest TRR offsets: {sorted(required)}")
    print(f"CHECK text write: {files} byte-identical TRR tables, {messages} text or tag records")
    return files, messages


def main():
    parser = lol3_cli.tool_args(__doc__, writes=False)
    parser.add_argument("--list", action="store_true", help="list offsets, keys and counts")
    args = parser.parse_args()
    if not (args.check or args.list):
        parser.error("give --check or --list to compare the original tables in memory")
    count, _ = check(Path(args.data), args.list)
    if count != 53:
        raise ValueError(f"expected 53 original TRR copies, found {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
