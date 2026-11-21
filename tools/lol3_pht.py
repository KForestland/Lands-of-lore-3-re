#!/usr/bin/env python3
"""Read the four loose LoL3 PHT files and check their repeated bytes.

  lol3_pht.py --data DAT            # size and the first 16 bytes of each file
  lol3_pht.py --data DAT --check
  lol3_pht.py --data DAT --file CYGNUS.PHT --check

A file passes when its name and size are one of the four retail files, its
first cycle has the pinned SHA-256 and every later byte equals the byte at
that distance into the first cycle. The check also requires that LOL3.DAT
and LOL3.EXE do not contain the names (ASCII, either case, or UTF-16), that
the cycle length is not a code immediate, and that the stored `$*.*` search
is the save-game folder. The stored bytes are also compared with the full
low-byte cycle of the program's random-number recurrence with LF expanded
to CR LF. The files' purpose and the program path that uses them remain open.
"""
from cli_errors import run_cli, game_path
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
# .text of LOL3.DAT. The cycle length is not an immediate there.
TEXT_RAW = 0x400
TEXT_SIZE = 0x136400
PERIOD_IMM = (0x1010000).to_bytes(4, "little")
# One-byte opcodes whose immediate is the next dword, plus 0x81 (opcode, ModRM, dword).
IMM_OPCODES = set(range(0xB8, 0xC0)) | {0x68, 0x3D, 0x05, 0x0D, 0x15, 0x1D, 0x25, 0x2D, 0x35, 0xA1, 0xA3}
# Save-game search: $*.* between $AUTOSAV.XXX and .\SAVEGAME, pushed at three sites.
WILD_AT = 0x1488A0
WILD = b"$*.*\x00\x00\x00\x00.\\SAVEGAME\x00"
WILD_PUSHES = (0x5A3A9, 0x5A441, 0x5A554)
WILD_PUSH = bytes.fromhex("68a0a05400")
RANDOM_AT = 0x11AA55  # LOL3.DAT VA 0x51B655
RANDOM_CODE = bytes.fromhex(
    "8b48148d14498d1491c1e20403d1c1e2082bd18d8c91c39e2600894814"
    "8bc1c1e81025ff7f0000c3"
)
RANDOM_CALL_SITES = {
    0xFE8D7: "e874c10100888434180f0000",  # generator call and store AL to the stack buffer
    0xFE8FF: "8d8c24180f0000",            # same buffer passed to the first transform
    0xFE91B: "e860000000",
    0xFE944: "e877010000",                # second transform
    0xFE96B: "f3a6",                      # compare bytes with the original buffer
}


def random_cycle():
    """Generate the seed-1 cycle of low output bytes, expanded as DOS text."""
    state = 1
    block = bytearray(1 << 24)
    for i in range(len(block)):
        state = (214013 * state + 2531011) & 0xFFFFFF
        block[i] = state >> 16
    return block.replace(b"\x0a", b"\x0d\x0a")


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


def period_is_immediate(text):
    """True when 0x1010000 is the immediate of a one-byte opcode or of opcode 0x81."""
    start = 0
    while True:
        index = text.find(PERIOD_IMM, start)
        if index < 0:
            return False
        if index and text[index - 1] in IMM_OPCODES:
            return True
        if index >= 2 and text[index - 2] == 0x81:
            return True
        start = index + 1


def names_absent(blob):
    """ASCII names in any case, and the same names as UTF-16 in any case.

    UTF-16 text is decoded at both byte alignments (errors ignored) and lowered.
    """
    lowered = blob.lower()
    for needle in NEEDLES:
        if needle in lowered:
            return needle.decode("ascii")
    for start in (0, 1):
        wide = blob[start:len(blob) - (len(blob) - start) % 2].decode("utf-16le", errors="ignore").lower()
        for needle in NEEDLES:
            if needle.decode("ascii") in wide:
                return needle.decode("ascii") + " (UTF-16)"
    return None


def head_line(path, count=16):
    """File size and the first bytes. No field names."""
    with Path(path).open("rb") as handle:
        head = handle.read(count)
    return f"{Path(path).name} {Path(path).stat().st_size} bytes +0: " + " ".join(f"{byte:02x}" for byte in head)


def extent_line(path):
    size = path.stat().st_size
    copies, tail = divmod(size, PERIOD)
    return f"{path.name}: {copies} full cycles, tail {tail} bytes at +{copies * PERIOD:#x}, EOF {size:#x}"


def main():
    parser = lol3_cli.tool_args(__doc__, writes=False)
    parser.add_argument("--file", type=str.lower, choices=SIZES, help="select one retail PHT by name")
    args = parser.parse_args()
    data = Path(args.data)
    try:
        paths = [p for p in data.iterdir() if p.is_file() and p.suffix.lower() == ".pht"]
        if args.file:
            paths = [p for p in paths if p.name.lower() == args.file]
            if len(paths) != 1:
                raise ValueError(f"expected one {args.file}, found {len(paths)}")
        if not args.check:
            if not paths:
                raise ValueError("no .PHT files in the DAT folder")
            for path in sorted(paths, key=lambda path: path.name.lower()):
                print(head_line(path))
                if args.file:
                    print(extent_line(path))
            return 0
        found = {p.name.lower(): p for p in paths}
        expected = (args.file,) if args.file else tuple(SIZES)
        if len(paths) != len(expected) or set(found) != set(expected):
            raise ValueError(f"PHT names {sorted(p.name for p in paths)}")
        ordered = [found[name] for name in expected]
        for path in ordered:
            if path.stat().st_size != SIZES[path.name.lower()]:
                raise ValueError(f"{path.name} is {path.stat().st_size} bytes")
            if not cycle_covers(path, PERIOD, CYCLE_SHA):
                raise ValueError(f"{path.name} is not the pinned cycle repeated every {PERIOD:#x} bytes")
        root = data.resolve().parent
        programs = {}
        for label, size in (("LOL3.DAT", DAT_SIZE), ("LOL3.EXE", EXE_SIZE)):
            blob = game_path(root, label).read_bytes()
            if len(blob) != size:
                raise ValueError(f"{label} is {len(blob)} bytes")
            hit = names_absent(blob)
            if hit:
                raise ValueError(f"{label} contains {hit}")
            programs[label] = blob
        image = programs["LOL3.DAT"]
        if image[RANDOM_AT:RANDOM_AT + len(RANDOM_CODE)] != RANDOM_CODE:
            raise ValueError("LOL3.DAT random-number recurrence differs")
        for at, encoding in RANDOM_CALL_SITES.items():
            expected = bytes.fromhex(encoding)
            if image[at:at + len(expected)] != expected:
                raise ValueError(f"LOL3.DAT in-memory RNG caller differs at +{at:#x}")
        with ordered[0].open("rb") as handle:
            if handle.read(PERIOD) != random_cycle():
                raise ValueError("PHT common cycle differs from the seed-1 byte model")
        if int.from_bytes(image[0xD0:0xD4], "little") != 0x37332C6E:
            raise ValueError("LOL3.DAT COFF timestamp field differs")
        if image[0xE0:0xE2] != b"\x0b\x01":
            raise ValueError("LOL3.DAT optional-header magic differs")
        if image[0xCC:0xCE] != b"\x4c\x01":
            raise ValueError("LOL3.DAT COFF machine word differs")
        if image[0xCE:0xD0] != b"\x04\x00":
            raise ValueError("LOL3.DAT COFF section count differs")
        if image[0xFC:0x100] != b"\x00\x00\x40\x00":
            raise ValueError("LOL3.DAT image base differs")
        if period_is_immediate(image[TEXT_RAW:TEXT_RAW + TEXT_SIZE]):
            raise ValueError("LOL3.DAT code uses 0x1010000 as an immediate")
        with ordered[0].open("rb") as handle:
            head = handle.read(65536)
        if len(head) != 65536:
            raise ValueError("PHT cycle head is short")
        for lag in range(1, 513):
            span = 65536 - lag
            same = sum(head[index] == head[index + lag] for index in range(span))
            if same * 100 >= span:
                raise ValueError(f"PHT lag {lag} repeats {same} of {span} bytes")
        if image[WILD_AT:WILD_AT + len(WILD)] != WILD:
            raise ValueError("save-game search string differs")
        for offset in WILD_PUSHES:
            if image[offset:offset + len(WILD_PUSH)] != WILD_PUSH:
                raise ValueError(f"save-game search push +{offset:#x} differs")
    except (OSError, ValueError) as exc:
        print(f"CHECK pht FAILED: {exc}")
        return 1
    shown = ", ".join(f"{path.name} {path.stat().st_size}" for path in ordered)
    count = "1 file matches" if args.file else "4 files match"
    print(f"CHECK pht: {count} the seed-1 cycle with LF expansion; {shown}; "
          "names absent from LOL3.DAT and LOL3.EXE (any case, ASCII/UTF-16); "
          "0x1010000 not an immediate; `$*.*` pushes at 3 sites")
    if args.file:
        print(extent_line(ordered[0]))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
