#!/usr/bin/env python3
"""Re-prove that the four loose PHT files are prefixes of one repeating block.

  lol3_pht.py --data DAT --check

A file counts when it is longer than one cycle and every later byte equals
the byte at that distance into the first cycle. The check also requires the
four retail names and sizes, one shared cycle, and that LOL3.DAT and
LOL3.EXE do not contain the names.
"""
from pathlib import Path

import lol3_cli

PERIOD = 0x1010000
SIZES = {
    "cygnus.pht": 112_519_732,
    "raider.pht": 61_616_890,
    "quann.pht": 57_732_590,
    "yupa.pht": 46_182_770,
}
NEEDLES = (b"CYGNUS", b"QUANN", b"RAIDER", b"YUPA", b".PHT", b".pht")
DAT_SIZE = 1_643_520
EXE_SIZE = 77_824


def cycle_covers(path):
    """True when every byte is a byte of the file's own first cycle."""
    path = Path(path)
    size = path.stat().st_size
    if size <= PERIOD:
        return False
    with path.open("rb") as handle:
        block = handle.read(PERIOD)
        if len(block) != PERIOD:
            return False
        left = size - PERIOD
        while left:
            chunk = PERIOD if left >= PERIOD else left
            piece = handle.read(chunk)
            if len(piece) != chunk or piece != block[:chunk]:
                return False
            left -= chunk
    return True


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
        base = None
        for path in ordered:
            if path.stat().st_size != SIZES[path.name.lower()]:
                raise ValueError(f"{path.name} is {path.stat().st_size} bytes")
            if not cycle_covers(path):
                raise ValueError(f"{path.name} does not repeat every {PERIOD:#x} bytes")
            with path.open("rb") as handle:
                block = handle.read(PERIOD)
            if base is None:
                base = block
            elif block != base:
                raise ValueError("the four files do not share one cycle")
        root = data.resolve().parent
        for label, size in (("LOL3.DAT", DAT_SIZE), ("LOL3.EXE", EXE_SIZE)):
            blob = (root / label).read_bytes()
            if len(blob) != size:
                raise ValueError(f"{label} is {len(blob)} bytes")
            for needle in NEEDLES:
                if needle in blob:
                    raise ValueError(f"{label} contains {needle.decode('ascii')}")
    except (OSError, ValueError) as exc:
        print(f"CHECK pht FAILED: {exc}")
        return 1
    shown = ", ".join(f"{path.name} {path.stat().st_size}" for path in ordered)
    print(f"CHECK pht: 4 files are prefixes of one 0x1010000-byte cycle; {shown}; "
          "names absent from LOL3.DAT and LOL3.EXE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
