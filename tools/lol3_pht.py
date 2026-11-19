#!/usr/bin/env python3
"""Re-prove that the four loose PHT files are prefixes of one repeating block.

  lol3_pht.py --data DAT --check

A file passes when its name and size are one of the four retail files, its
first cycle has the pinned SHA-256 and every later byte equals the byte at
that distance into the first cycle. The check also requires that LOL3.DAT
and LOL3.EXE do not contain the names (compared without case). This shows
the bytes are one block repeated; what they mean and what reads them is
unknown.
"""
from hashlib import sha256
from pathlib import Path

import lol3_cli

PERIOD = 0x1010000
SIZES = {
    "cygnus.pht": 112_519_732,
    "raider.pht": 61_616_890,
    "quann.pht": 57_732_590,
    "yupa.pht": 46_182_770,
}
CYCLE_SHA = "989e39205a5bf3e1aa7856cd9f9bc3191ada4e9ce34cf8811980b2c0c8bb9755"
# Lower case: the programs are searched after lowering their bytes.
NEEDLES = (b"cygnus", b"quann", b"raider", b"yupa", b".pht")
DAT_SIZE = 1_643_520
EXE_SIZE = 77_824


def cycle_covers(path, period=PERIOD, cycle_sha=None):
    """True when the file is longer than one cycle, every byte is a byte of its own first cycle
    and, when cycle_sha is given, that first cycle has that SHA-256."""
    path = Path(path)
    size = path.stat().st_size
    if size <= period:
        return False
    with path.open("rb") as handle:
        block = handle.read(period)
        if len(block) != period:
            return False
        if cycle_sha is not None and sha256(block).hexdigest() != cycle_sha:
            return False
        left = size - period
        while left:
            chunk = period if left >= period else left
            piece = handle.read(chunk)
            if len(piece) != chunk or piece != block[:chunk]:
                return False
            left -= chunk
    return True


def pht_covers(path, sizes=SIZES, period=PERIOD, cycle_sha=CYCLE_SHA):
    """The rating's test: a retail name and size (name compared without case) and the pinned cycle."""
    path = Path(path)
    if sizes.get(path.name.lower()) != path.stat().st_size:
        return False
    return cycle_covers(path, period, cycle_sha)


def main():
    parser = lol3_cli.tool_args(__doc__)
    args = parser.parse_args()
    if args.out:
        parser.error("prints only")
    if not args.check:
        parser.error("this tool only checks; pass --check")
    data = Path(args.data)
    try:
        paths = [p for p in data.iterdir() if p.is_file() and p.suffix.lower() == ".pht"]
        found = {p.name.lower(): p for p in paths}
        if len(paths) != len(SIZES) or set(found) != set(SIZES):
            raise ValueError(f"PHT names {sorted(p.name for p in paths)}")
        ordered = [found[name] for name in SIZES]
        for path in ordered:
            if path.stat().st_size != SIZES[path.name.lower()]:
                raise ValueError(f"{path.name} is {path.stat().st_size} bytes")
            if not cycle_covers(path, PERIOD, CYCLE_SHA):
                raise ValueError(f"{path.name} is not the pinned cycle repeated every {PERIOD:#x} bytes")
        root = data.resolve().parent
        for label, size in (("LOL3.DAT", DAT_SIZE), ("LOL3.EXE", EXE_SIZE)):
            blob = (root / label).read_bytes().lower()
            if len(blob) != size:
                raise ValueError(f"{label} is {len(blob)} bytes")
            for needle in NEEDLES:
                if needle in blob:
                    raise ValueError(f"{label} contains {needle.decode('ascii')}")
    except (OSError, ValueError) as exc:
        print(f"CHECK pht FAILED: {exc}")
        return 1
    shown = ", ".join(f"{path.name} {path.stat().st_size}" for path in ordered)
    print(f"CHECK pht: 4 files are prefixes of one pinned 0x1010000-byte cycle; {shown}; "
          "names absent from LOL3.DAT and LOL3.EXE (any case)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
