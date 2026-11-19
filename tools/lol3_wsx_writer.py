#!/usr/bin/env python3
"""Read the WSX archives in DAT and the loose WSX beside DAT, rebuild each in memory and compare it with the file.

The shipped DAT/cdcache.wsx seed and the game-written cdcache.wsx are not
ordinary WSX archives (open question Q1) and are left out. Writes nothing.
"""
from pathlib import Path
import struct

from cli_errors import run_cli
from extract_wsx_entries import parse_wsx, parse_wsx_bytes
import lol3_cli

# 51 DAT archives (52 minus the cdcache.wsx seed), LOCAL.WSX and locallng.wsx beside DAT.
EXPECTED = (51, 2, 7614)


def write_wsx(entries):
    """Write ordered (key, data offset, payload) rows over a contiguous data pool."""
    entries = tuple(entries)
    directory = bytearray(struct.pack("<HI", len(entries), sum(len(blob) for _, _, blob in entries)))
    for key, offset, blob in entries:
        directory.extend(struct.pack("<III", key, offset, len(blob)))
    payload = []
    end = 0
    for _, offset, blob in sorted(entries, key=lambda entry: entry[1]):
        if offset != end:
            raise ValueError("WSX entries do not tile the data pool")
        payload.append(blob)
        end += len(blob)
    return b"".join([directory, *payload])


def relayout(entries):
    """Recompute data offsets after payloads change size, keeping row order and pool order."""
    entries = tuple(entries)
    offsets, end = {}, 0
    for index in sorted(range(len(entries)), key=lambda i: entries[i][1]):
        offsets[index] = end
        end += len(entries[index][2])
    return [(key, offsets[i], blob) for i, (key, _, blob) in enumerate(entries)]


def rows_of(parsed):
    return [(row["hash"], row["unk"], row["blob"]) for row in sorted(parsed["entries"], key=lambda row: row["index"])]


def mutation_check(rows):
    """Grow one payload by a byte: the output must differ and re-read with the new payload."""
    original = write_wsx(rows)
    target = min((i for i in range(len(rows)) if rows[i][2]), key=lambda i: rows[i][1])
    changed = list(rows)
    key, offset, blob = changed[target]
    changed[target] = (key, offset, blob[:-1] + bytes([blob[-1] ^ 0xFF]) + b"\0")
    rebuilt = write_wsx(relayout(changed))
    reread = rows_of(parse_wsx_bytes(rebuilt))
    if rebuilt == original or [(k, b) for k, _, b in reread] != [(k, b) for k, _, b in changed]:
        raise ValueError("a changed WSX member did not reach the rebuilt archive")


def check(data):
    root = Path(data)
    files = [p for p in lol3_cli.wsx_files(root) if p.name.upper() != "CDCACHE.WSX"]
    loose = [p for p in lol3_cli.wsx_files(root.parent) if p.name.upper() != "CDCACHE.WSX"]
    if not files:
        raise ValueError("no named WSX archives in DAT")
    count = 0
    for path in files + loose:
        rows = rows_of(parse_wsx(path))
        if count == 0:
            mutation_check(rows)
        rebuilt = write_wsx(rows)
        # Compare against disk incrementally rather than retaining a second image.
        view = memoryview(rebuilt)
        step = 1 << 20
        with path.open("rb") as source:
            for at in range(0, len(view), step):
                if source.read(step) != view[at:at + step]:
                    raise ValueError(f"{path.name}: generated WSX differs at or after file +{at:#x}")
            if source.read(1):
                raise ValueError(f"{path.name}: generated WSX ends before the file")
        view.release()
        count += len(rows)
    if (len(files), len(loose), count) != EXPECTED:
        raise ValueError(f"expected {EXPECTED[0]} DAT and {EXPECTED[1]} loose archives with {EXPECTED[2]:,} rows, "
                         f"found {len(files)}, {len(loose)} and {count:,}")
    print(f"CHECK WSX write: {len(files)} DAT archives and {len(loose)} loose archives, "
          f"{count:,} rows rebuilt from the parsed rows; byte-identical; a changed member re-reads "
          f"(cdcache.wsx left out)")


def main():
    parser = lol3_cli.tool_args(__doc__, writes=False)
    args = parser.parse_args()
    if not args.check:
        parser.error("give --check to regenerate the original WSX archives")
    check(args.data)
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
