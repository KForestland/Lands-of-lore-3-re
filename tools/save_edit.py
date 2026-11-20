#!/usr/bin/env python3
"""Change one documented field in a new copy of an original LoL3 save; the save itself is only read."""
from pathlib import Path
import struct

from cli_errors import ReaderArgumentParser, run_cli
from lol3_save_header import BLOCK_HEADER, LEVEL_SECTIONS, parse_header
from modkit_core import output_path

FIELDS = ("name", "heading", "position-from")
# The player's 14-byte position group: X and Z (16.16), heading dword, region index.
GROUP = 0x49C
LEVEL = 0x498


def name_bytes(value, width):
    try:
        raw = value.encode("ascii")
    except UnicodeEncodeError:
        raise ValueError("the name must use plain ASCII letters, digits and punctuation") from None
    if not raw or len(raw) >= width or not all(32 <= byte <= 126 for byte in raw):
        raise ValueError(f"the name must have 1 to {width - 1} printable ASCII characters")
    return raw + b"\0"


def integer(value, low, high):
    try:
        number = int(value, 16) if value.lower().startswith("0x") else int(value, 10)
    except ValueError:
        raise ValueError(f"the value must be a whole number from {low} to {high}, not {value!r}") from None
    if not low <= number <= high:
        raise ValueError(f"the value must be a whole number from {low} to {high}, not {number}")
    return number


def directory(raw, what="the save"):
    try:
        header = parse_header(raw, len(raw))
        for at, size in header["levels"]:
            if not size:
                continue
            if size < BLOCK_HEADER or struct.unpack_from("<I", raw, at)[0] != size:
                raise ValueError
            starts = struct.unpack_from(f"<{LEVEL_SECTIONS}I", raw, at + 0xF4)
            if starts[0] < BLOCK_HEADER or starts[-1] > size or any(a > b for a, b in zip(starts, starts[1:])):
                raise ValueError
    except (ValueError, struct.error, IndexError):
        raise ValueError(f"{what} could not be read; it may be damaged or not an original "
                         "LoL3 save (version 38/310)") from None
    return header


def shown(field, raw):
    if field == "name":
        return repr(raw[:44].split(b"\0")[0].decode("latin-1"))
    x, y, heading, region = struct.unpack_from("<iiIH", raw, GROUP)
    if field == "heading":
        return f"{heading & 0xFFFF:#06x}"
    return f"(x {x / 65536:g}, z {y / 65536:g}, heading {heading & 0xFFFF:#06x}, region {region})"


def edit(raw, field, value):
    """The edited copy and a line 'field old -> new'."""
    before = directory(raw)
    result = bytearray(raw)
    if field == "name":
        expected = name_bytes(value, 44)
        start = 0
    elif field == "heading":
        start = GROUP + 8
        expected = struct.pack("<H", integer(value, 0, 65535))
    elif field == "position-from":
        path = Path(value)
        if not path.is_file():
            raise ValueError(f"donor save not found: {value}")
        donor = path.read_bytes()
        directory(donor, "the donor save")
        if donor[0x30:0x94] != raw[0x30:0x94] or donor[LEVEL:GROUP] != raw[LEVEL:GROUP]:
            raise ValueError("the donor save must come from the same level and game version")
        if donor[GROUP + 12:GROUP + 14] == b"\xff\xff":
            raise ValueError("the donor save has no player region")
        start, expected = GROUP, donor[GROUP:GROUP + 14]
    else:
        raise ValueError(f"unknown field {field}; give one of {', '.join(FIELDS)}")
    result[start:start + len(expected)] = expected
    changed = bytes(result)
    if directory(changed) != before or changed[start:start + len(expected)] != expected:
        raise ValueError("the edited copy did not read back as requested; nothing was written")
    return changed, f"{field} {shown(field, raw)} -> {shown(field, changed)}"


def status(field):
    # The only confirmed edited-save runs changed item rows and quick-cast references
    # (docs/lol3-native-saves.md). A turn in the game also changes the second group's heading.
    return ("UNCONFIRMED: no edited copy of this field has been loaded by the game yet; "
            "keep a backup of your saves")


def main():
    try:
        return run()
    except OSError as error:
        reason = (error.strerror or "the system refused").lower()
        raise ValueError(f"cannot use {error.filename or 'a file'}: {reason}") from None


def run():
    parser = ReaderArgumentParser(
        description=__doc__,
        epilog="Example: save_edit.py set '/path/to/SAVEGAME/$1234___.000' heading 0x4000 --out 'my edited save.000' (save names begin with $; on Linux and macOS use single quotes).")
    commands = parser.add_subparsers(dest="command", metavar="set")
    commands.required = True
    setter = commands.add_parser("set", help="write a copy of the save with one field changed",
                                 description="Write a copy of the save with one field changed.")
    setter.add_argument("save", type=Path, help="an original save file; only read")
    setter.add_argument("field", choices=FIELDS)
    setter.add_argument("value", help="the new value: a name, a heading 0-65535, "
                                      "or for position-from another save of the same level")
    setter.add_argument("--out", required=True, type=Path, help="the new save file to write, outside the game and save folders")
    args = parser.parse_args()
    if not args.save.is_file():
        raise ValueError(f"save not found: {args.save}")
    path = output_path(args.out, args.save.resolve().parent, args.save)
    if not path.parent.is_dir():
        raise ValueError(f"the folder {path.parent} does not exist; create it first or choose another place")
    changed, change = edit(args.save.read_bytes(), args.field, args.value)
    with path.open("xb") as target:
        target.write(changed)
    print(f"set: {change}; copy written to {path}; the original save was only read")
    print(status(args.field))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
