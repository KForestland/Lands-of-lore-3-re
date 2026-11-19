#!/usr/bin/env python3
"""Re-prove the ODF section-0 names and the AI-file failure arm.

  lol3_odf_companions.py --data DAT --check
"""
from hashlib import sha256
from pathlib import Path
from struct import unpack_from

import lol3_cli
from extract_wsx_entries import wsx_name_hash
from lol3_script_framing import CODE_BIAS, RETAIL_PE

DATA_BIAS = 0x401800

LEAVES = ("stat.csv", "goals.csv", "actions.csv", "effector.csv", "spells.csv")
LEAF_VA = {
    "stat.csv": 0x551BE4,
    "goals.csv": 0x551BD8,
    "actions.csv": 0x551BCC,
    "effector.csv": 0x551BBC,
    "spells.csv": 0x551BB0,
}
# call 0x420300, then call 0x4FD780, for the five leaves in order.
JOIN_AT = (0x4FD99F, 0x4FD9C1, 0x4FD9E3, 0x4FDA05, 0x4FDA30)
LOAD_AT = (0x4FD9A8, 0x4FD9CA, 0x4FD9EC, 0x4FDA0E, 0x4FDA39)
# (address, rows, address, columns) of the two size pushes for each leaf.
SIZES = (
    (0x4FD975, 1, 0x4FD977, 0x20),
    (0x4FD9B4, 0x0E, 0x4FD9B6, 0x2E),
    (0x4FD9D6, 0x0F, 0x4FD9D8, 0x2E),
    (0x4FD9F8, 0x20, 0x4FD9FA, 0x3A),
    (0x4FDA16, 0x95, 0x4FDA21, 0x2E),
)
EMPTY = {"B_HUMAN", "JADIN", "LUTHER", "RIX", "RUCOLL", "VICTIM"}
PARTIAL = {
    "NONE": {"stat.csv", "goals.csv", "spells.csv"},
    "Spire": {"stat.csv", "goals.csv", "actions.csv"},
}


def call_to(image, va, target):
    raw = image[va - CODE_BIAS:va - CODE_BIAS + 5]
    if raw[0] != 0xE8:
        return False
    rel = unpack_from("<i", raw, 1)[0]
    return va + 5 + rel == target


def push_imm(image, va, value):
    raw = image[va - CODE_BIAS:va - CODE_BIAS + 5]
    if value < 0x80 and raw[0] == 0x6A and raw[1] == value:
        return 2
    if raw[0] == 0x68 and unpack_from("<I", raw, 1)[0] == value:
        return 5
    return 0


def level_odfs(data):
    found = []
    for path in lol3_cli.wsx_files(data):
        raw = path.read_bytes()
        count, _ = unpack_from("<HI", raw)
        if count != 4:
            continue
        stem = path.stem.upper()
        key = wsx_name_hash(f"LEVELS\\{stem}\\{stem}.ODF")
        for index in range(count):
            stored, offset, length = unpack_from("<III", raw, 6 + 12 * index)
            if stored == key:
                found.append((stem, raw[54 + offset:54 + offset + length]))
    return found


def main():
    parser = lol3_cli.tool_args(__doc__)
    args = parser.parse_args()
    if not args.check:
        parser.error("this tool only checks; pass --check")
    data = Path(args.data)
    try:
        image = (data.resolve().parent / "LOL3.DAT").read_bytes()
        if sha256(image).hexdigest() != RETAIL_PE:
            raise ValueError("LOL3.DAT does not match the documented English retail executable")
        if image[0x4AB42E - CODE_BIAS:0x4AB42E - CODE_BIAS + 6] != bytes.fromhex("8d347fc1e603"):
            raise ValueError("section-0 size is not count times 24")
        if image[0x4AB682 - CODE_BIAS:0x4AB682 - CODE_BIAS + 3] != bytes.fromhex("83c618"):
            raise ValueError("section-0 walk stride is not 0x18")
        if (image[0x43FCCE - CODE_BIAS:0x43FCCE - CODE_BIAS + 4] != bytes.fromhex("8b442410")
                or not call_to(image, 0x43FCD6, 0x435A90)):
            raise ValueError("section-0 seek is not field 0")
        if (image[0x43FD3D - CODE_BIAS:0x43FD3D - CODE_BIAS + 4] != bytes.fromhex("8b542414")
                or not call_to(image, 0x43FD45, 0x435A90)):
            raise ValueError("the next seek is not field 1")
        if image[0x4202FC - CODE_BIAS:0x420300 - CODE_BIAS] != b"\x90" * 4:
            raise ValueError("path join is not the function after the nop pad")
        if image[0x4FD77D - CODE_BIAS:0x4FD780 - CODE_BIAS] != bytes.fromhex("c39090"):
            raise ValueError("AI loader does not start after ret and two nops")
        if image[0x4FD7B1 - CODE_BIAS:0x4FD7B7 - CODE_BIAS] != bytes.fromhex("0f842d010000"):
            raise ValueError("failure jump is not 0x4FD7B1 to 0x4FD8E4")
        if image[0x4FD8E4 - CODE_BIAS:0x4FD8E8 - CODE_BIAS] != bytes.fromhex("5f5e5dc3"):
            raise ValueError("failure landing is not the epilogue")
        if image[0x546318 - DATA_BIAS:0x546318 - DATA_BIAS + 2] != b"\\\x00":
            raise ValueError("path separator is not a backslash")
        for leaf, va in LEAF_VA.items():
            if image[va - DATA_BIAS:va - DATA_BIAS + len(leaf) + 1] != leaf.encode("ascii") + b"\x00":
                raise ValueError(f"{leaf} is not at {va:#x}")
        if image[0x551BF0 - DATA_BIAS:0x551BF0 - DATA_BIAS + 13] != b"global\\ai\\%s\x00":
            raise ValueError("AI directory format changed")
        for at, target in zip(JOIN_AT, (0x420300,) * 5):
            if not call_to(image, at, target):
                raise ValueError(f"call at {at:#x} is not the path join")
        for at in LOAD_AT:
            if not call_to(image, at, 0x4FD780):
                raise ValueError(f"call at {at:#x} is not the AI loader")
        for row_at, rows, col_at, columns in SIZES:
            if not push_imm(image, row_at, rows) or not push_imm(image, col_at, columns):
                raise ValueError(f"size pushes at {row_at:#x} are not {rows} by {columns:#x}")

        slots = names = cd = mixed = 0
        seen = set()
        tags = set()
        rows_n = 0
        ckeep = None
        for stem, odf in level_odfs(data):
            off0 = unpack_from("<I", odf, 4)[0]
            off1 = unpack_from("<I", odf, 8)[0]
            count = unpack_from("<I", odf, 0x3C)[0]
            base = off0 + 24 * count
            if off1 - base != 22 * count:
                raise ValueError(f"{stem} name span is {off1 - base} bytes for {count} rows")
            for index in range(count):
                slot = odf[base + 22 * index:base + 22 * index + 22]
                text, _, rest = slot.partition(b"\x00")
                if (not text or any(b < 0x20 or b > 0x7E for b in text)
                        or not set(rest) <= {0, 0xCD} or b"\xcd\x00" in rest):
                    raise ValueError(f"{stem} slot {index} is not a padded name")
                slots += 1
                seen.add(text)
                if rest == b"\xcd" * len(rest):
                    cd += 1
                else:
                    mixed += 1
            if stem == "CKEEP":
                ckeep = odf[0x5DC:0x5DC + 7]
            start, nrows = unpack_from("<I", odf, 0x10)[0], unpack_from("<I", odf, 0x48)[0]
            rows_n += nrows
            for index in range(nrows):
                tag = odf[start + 147 * index + 0x87:start + 147 * index + 0x93].split(b"\x00", 1)[0]
                tags.add(tag.decode("ascii"))
        if (slots, len(seen), cd, mixed, ckeep, len(level_odfs(data)), rows_n, len(tags)) != (
                630, 168, 454, 176, b"Floor39", 18, 334, 68):
            raise ValueError(
                f"names {slots} distinct {len(seen)} pad {cd}/{mixed} "
                f"ckeep {ckeep!r} levels {len(level_odfs(data))} rows {rows_n} tags {len(tags)}")

        global_wsx = next(path.read_bytes() for path in lol3_cli.wsx_files(data) if path.name.upper() == "GLOBAL.WSX")
        directory = unpack_from("<H", global_wsx)[0]
        keys = {unpack_from("<I", global_wsx, 6 + 12 * index)[0] for index in range(directory)}
        empty, partial, full = set(), {}, 0
        for tag in tags:
            got = {leaf for leaf in LEAVES if wsx_name_hash(f"global\\ai\\{tag}\\{leaf}") in keys}
            if len(got) == 5:
                full += 1
            elif not got:
                empty.add(tag)
            else:
                partial[tag] = got
        if full != 60 or empty != EMPTY or partial != PARTIAL:
            raise ValueError(f"AI files full {full} empty {sorted(empty)} partial {partial}")
    except (OSError, ValueError, StopIteration) as exc:
        print(f"CHECK odf_companions FAILED: {exc}")
        return 1
    print("CHECK odf_companions: 630 section-0 names, loader reads 24 bytes times the count; "
          "5 AI files, 60 tags join all five; a zero lookup leaves the buffer zeroed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
