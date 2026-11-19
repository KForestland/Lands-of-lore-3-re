#!/usr/bin/env python3
"""Check original LoL3 pickup, texture and spell-counter witnesses.

  lol3_native_checks.py --data DAT --check
  lol3_native_checks.py --data DAT --check --decode-copy   # shipped banks, liblzo2
  lol3_native_checks.py --data DAT --list
  lol3_native_checks.py --data DAT --spells
"""
from cli_errors import run_cli
from collections import Counter
from hashlib import sha256
from pathlib import Path
from struct import error as StructError, pack, unpack_from

import lol3_cli
from lol3_combat_census import DATA_BIAS, HANDLERS, ITEM_STRIDE, ITEM_TABLE, global_wsx
from lol3_script_framing import CODE_BIAS, RETAIL_PE
from lol3_texture_archive import chunks, texture_entries
from lol3_texture_png import UNCONFIRMED_FLAGS, cache_textures, texture_payload
from walk_lmf_leaves import lzo_decoder

COPY_BANKS = {"BUPP1", "EWOD1", "QWOD0", "RVOL0"}
COPY_MISMATCHES = (500, 244, 116, 52, 24)
FIRST_COUNTER_IDS = {0x54, 0x59, 0x5E, 0x63, 0x68, 0x6D, 0x72, 0x77, 0x7C,
                     0x81, 0x86, 0x8B, 0x9C, 0x9D, 0x9E, 0x9F, 0x15A}


def opcode(image, address, encoding):
    expected = bytes.fromhex(encoding)
    at = address - CODE_BIAS
    if image[at:at + len(expected)] != expected:
        raise ValueError(f"native instruction differs at {address:#x}")


def direct_call(image, address, target):
    at = address - CODE_BIAS
    if image[at] != 0xE8 or address + 5 + unpack_from("<i", image, at + 1)[0] != target:
        raise ValueError(f"wrong call target at {address:#x}")


def pickup_and_renderer(image):
    vtable = 0x540580 - 0x401800
    if (unpack_from("<I", image, vtable + 0x68)[0],
            unpack_from("<I", image, vtable + 0x114)[0]) != (0x4D83A0, 0x4D7370):
        raise ValueError("wrong world item vtable entries")
    if unpack_from("<I", image, 0x538400 - 0x401800)[0] != 0x40B850:
        raise ValueError("wrong player item receive vtable entry")
    for address, target in (
        (0x4D83AC, 0x42EF50), (0x4D8496, 0x40B9B0), (0x40BA1F, 0x49ED50),
        (0x49ED89, 0x4503E0), (0x49EDA0, 0x49E560), (0x4D7373, 0x4D7520),
        (0x4D75F8, 0x441380), (0x40B999, 0x422480), (0x482311, 0x4E0BA0),
    ):
        direct_call(image, address, target)
    for address, encoding in (
        (0x45041F, "88 16"),  # pool bitmap write
        (0x49EDC3, "ff 90 14 01 00 00"),  # release through vtable
        (0x4D75CB, "80 c9 80 89 4e 1c"),  # retired world row
        (0x441383, "c7 06 c0 9a 53 00"),  # base vtable
        (0x4224C6, "89 be 90 00 00 00"), (0x4224F3, "89 8e b0 00 00 00"),
        (0x438CDE, "a1 24 78 7d 00 e9 d6 00 00 00"),
        (0x4E0BAC, "a8 20 74 06 b8 a0 0c 4e 00"),
        (0x4E0CC0, "66 8b 42 04 8b 54 24 04 0f af d0 89 01 a1 30 78 7d 00 8d 44 02 0c c3"),
    ):
        opcode(image, address, encoding)
    if unpack_from("<I", image, 0x439460 - CODE_BIAS + 25 * 4)[0] != 0x438CDE:
        raise ValueError("wrong level save selector 25")


def spell_counter(image, original):
    # The executable's .text virtual bytes (file offsets 0x400 through 0x1366E4).
    start, end = 0x400, 0x1366E5
    target = 0x432AD0
    callers = tuple(at + CODE_BIAS for at in range(start, end - 4)
                    if image[at] == 0xE8
                    and at + CODE_BIAS + 5 + unpack_from("<i", image, at + 1)[0] == target)
    if callers != (0x4A5A3A, 0x4A6133) or pack("<I", target) in image:
        raise ValueError("unexpected references to the second-counter writer")
    for address, encoding in (
        (0x432AD8, "8b 8e 21 11 01 00 03 cf 89 8e 21 11 01 00"),
        (0x432AED, "85 ff 7e 61"),
        (0x432B52, "8b 86 21 11 01 00 85 c0 75 0d 8b 46 28 c7 80 58 03 00 00 1f 00 00 00"),
        (0x42E759, "89 be 21 11 01 00"), (0x4326B7, "89 be 21 11 01 00"),
        (0x43470B, "a1 21 1a 58 00 85 c0 74 02"), (0x4A46E2, "a1 21 1a 58 00 85 c0 74 0a"),
        (0x4A5A33, "6a ff b9 00 09 57 00"), (0x4A612C, "6a 01 b9 00 09 57 00"),
    ):
        opcode(image, address, encoding)
    direct_call(image, 0x432AE8, 0x432CC0)
    if unpack_from("<I", image, 0x54BAD8 - 0x401800)[0] != 0x4A6120:
        raise ValueError("wrong regular item handler 112")

    for selector, targets, expected_first in (
        (0x4A5E20, 0x4A5DEC, 0x4A5BB0),
        (0x434790, 0x43475C, 0x43474F),
    ):
        table = unpack_from("<13I", image, targets - CODE_BIAS)
        begin = selector - CODE_BIAS
        first = {0x54, 0x59} | {
            index + 0x5E for index, case in enumerate(image[begin:begin + 0xFD])
            if table[case] == expected_first
        }
        if first != FIRST_COUNTER_IDS:
            raise ValueError(f"unexpected first-counter route at {selector:#x}")

    odf = 0x3866
    item_offset, = unpack_from("<I", original, odf + 4)
    count, = unpack_from("<I", original, odf + 0x34)
    if (item_offset, count) != (0x1F0, 343):
        raise ValueError("wrong original item directory")
    producers, special = [], set()
    for at in range(odf + item_offset, odf + item_offset + 139 * count, 139):
        identity, = unpack_from("<I", original, at + 0x73)
        if original[at + 0x3F] & 2:
            special.add(identity)
        elif unpack_from("<I", original, at + 0x4B)[0] == 112:
            producers.append((at, identity, unpack_from("<I", original, at + 0x18)[0]))
    if not FIRST_COUNTER_IDS <= special or 0x57 not in special:
        raise ValueError("missing original spell definition")
    if producers != [(0xCB4F, 0x110, 0xE2F77FE7)]:
        raise ValueError("unexpected original second-counter producers")
    spell_frames(image, original)


def spell_frames(image, archive):
    """447 spell frames follow the 87-byte rows; every word +8 is zero."""
    opcode(image, 0x490A03, "66 8b 48 08")
    opcode(image, 0x4FD57C, "c1 e1 04")
    opcode(image, 0x4B43AE, "c1 e2 04")
    base = 0x16BE53
    offset, count = unpack_from("<II", archive, base + 4)
    if (offset, count) != (412, 28):
        raise ValueError("wrong spell table")
    table = base + offset
    frames = 0
    for index in range(count):
        row = table + 87 * index
        frames += archive[row + 0x2E]
        if unpack_from("<I", archive, row + 0x14)[0] != 0:
            raise ValueError("spell row +0x14 is set in the file")
    end = table + 87 * count
    stored, = unpack_from("<I", archive, end)
    if (stored, frames) != (447, 447):
        raise ValueError(f"spell frame count {stored} vs row bytes {frames}")
    blob = archive[end + 4:end + 4 + frames * 16]
    pool = 0
    for index in range(frames):
        word, = unpack_from("<H", blob, index * 16 + 8)
        if word:
            raise ValueError(f"spell frame {index} word +8 is {word:#x}")
        step = blob[index * 16 + 0xD]
        if step >= 0x80:
            raise ValueError(f"spell frame {index} byte +0xD is negative")
        pool += step
    pool_count, = unpack_from("<I", archive, end + 4 + frames * 16)
    if (pool_count, pool) != (545, 545):
        raise ValueError(f"spell frame pool {pool_count} vs byte +0xD sum {pool}")
    if archive[base + 0x43EC:base + 0x43EC + 8] != bytes(8):
        raise ValueError("spell auxiliary row is not eight zero bytes")


def regular_item_handlers(image, original):
    witnesses = {
        1: (0x49F660, (0x40DA,)),
        3: (0x4A28D0, (0xA5D8,)),
        4: (0x49F7B0, (0x9A71,)),
        5: (0x49F8C0, (0x924C, 0x9EC9)),
        7: (0x49FB60, (0xC80D,)),
        8: (0x49FC40, (0x5833,)),
    }
    for index, (handler, offsets) in witnesses.items():
        if unpack_from("<I", image, HANDLERS - DATA_BIAS + 4 * index)[0] != handler:
            raise ValueError(f"wrong regular item handler {index}")
        for at in offsets:
            if (at - ITEM_TABLE) % ITEM_STRIDE or original[at + 0x3F] & 2:
                raise ValueError(f"invalid regular item row at {at:#x}")
            if unpack_from("<I", original, at + 0x4B)[0] != index:
                raise ValueError(f"wrong regular item index at {at:#x}")
    for address, target in (
        (0x49F6C6, 0x4EAC90), (0x4A29B9, 0x4B1BA0), (0x49F874, 0x431740),
        (0x49FAB0, 0x4EC800), (0x49FC08, 0x4C35E0), (0x49FCBC, 0x4C1DF0),
    ):
        direct_call(image, address, target)
    opcode(image, 0x49F86C, "c7 40 04 3c 00 00 00")
    opcode(image, 0x49FCCC, "89 0d fc 50 5d 00")


def verify_copy_banks(data_dir):
    decode = lzo_decoder()
    seen = Counter()
    for name, packed in texture_entries(data_dir):
        if name not in COPY_BANKS:
            continue
        bank = b"".join(decode(data, size) for data, size in chunks(packed))
        for offset, size, _, _, mip, _, palette in cache_textures(bank, [(0, len(bank))]):
            flags, width, height, payload = texture_payload(bank[offset:offset + size])
            if flags not in UNCONFIRMED_FLAGS:
                continue
            if (width, height) != (128 >> mip, 128 >> mip) or len(payload) != height * (width + 4):
                raise ValueError(f"{name}: wrong copy dimensions at {offset:#x}")
            fixed = payload[:width * height]
            span = bytearray()
            for start in range(0, len(payload), width + 4):
                if unpack_from("<HH", payload, start) != (0, width):
                    raise ValueError(f"{name}: wrong span header at {offset + 12 + start:#x}")
                span.extend(payload[start + 4:start + 4 + width])
            if (fixed[0], span[0], unpack_from("<H", bank, palette + 6)[0]) != (0, 3, 0x03C0):
                raise ValueError(f"{name}: wrong first-pixel witness at {offset:#x}")
            if sum(left != right for left, right in zip(fixed, span)) != COPY_MISMATCHES[mip]:
                raise ValueError(f"{name}: wrong fixed-width comparison at {offset:#x}")
            seen[name, mip] += 1
    if seen != {(name, mip): 1 for name in COPY_BANKS for mip in range(5)}:
        raise ValueError("missing or duplicate shipped copy mips")
    return seen


def data_dword(image, va):
    return unpack_from("<I", image, va - DATA_BIAS)[0]


def call_target(image, address):
    at = address - CODE_BIAS
    return address + 5 + unpack_from("<i", image, at + 1)[0]


def witness_lines(image):
    """Values the anchor checks read. Instruction bytes are not dumped."""
    lines = [
        f"world item +0x68 {data_dword(image, 0x5405E8):#x}",
        f"world item +0x114 {data_dword(image, 0x540694):#x}",
        f"player receive {data_dword(image, 0x538400):#x}",
        f"call 0x4d83ac targets {call_target(image, 0x4D83AC):#x}",
        f"second-counter call 0x4a5a3a targets {call_target(image, 0x4A5A3A):#x}",
        f"second-counter call 0x4a6133 targets {call_target(image, 0x4A6133):#x}",
        f"handler 112 {data_dword(image, 0x54BAD8):#x}",
    ]
    return "\n".join(lines) + "\n"


def spell_lines(archive):
    """28 spell rows, the 8-byte auxiliary row, and special-definition costs."""
    offset, count = unpack_from("<II", archive, 0x16BE53 + 4)
    if (offset, count) != (412, 28):
        raise ValueError(f"spell table is offset {offset} count {count}")
    lines = [f"spell rows {count}"]
    base = 0x16BE53 + offset
    for index in range(count):
        row = archive[base + 87 * index:base + 87 * (index + 1)]
        identity, = unpack_from("<I", row, 0x18)
        lines.append(f"row {index + 1}: +0x18 {identity:#x} +0x2e {row[0x2E]:#x}")
    auxiliary = archive[0x16BE53 + 0x43EC:0x16BE53 + 0x43EC + 8]
    lines.append("auxiliary: " + " ".join(f"{byte:02x}" for byte in auxiliary))
    costs = []
    for index in range(343):
        row = archive[0x3A56 + 139 * index:0x3A56 + 139 * (index + 1)]
        if row[0x3F] & 2:
            identity, = unpack_from("<I", row, 0x73)
            cost, = unpack_from("<I", row, 0x5B)
            costs.append(f"definition {index}: +0x73 {identity:#x} +0x5b {cost}")
    lines.append(f"special definition costs {len(costs)}")
    lines.extend(costs)
    return "\n".join(lines) + "\n"


def main():
    parser = lol3_cli.tool_args(__doc__, writes=False)
    parser.add_argument("--decode-copy", action="store_true", help="compare all 20 shipped copy mips")
    parser.add_argument("--list", action="store_true", help="print the anchor values the check reads")
    parser.add_argument("--spells", action="store_true", help="print spell rows and special-definition costs")
    args = parser.parse_args()
    if args.out:
        parser.error("this check writes counts to standard output")
    if args.list and args.spells:
        parser.error("pass only one of --list and --spells")
    if args.check and (args.list or args.spells):
        parser.error("--check does not list")
    try:
        data_dir = Path(args.data).resolve()
        image = (data_dir.parent / "LOL3.DAT").read_bytes()
        if sha256(image).hexdigest() != RETAIL_PE:
            raise ValueError("LOL3.DAT does not match the documented English retail executable")
        if args.spells:
            print(spell_lines(global_wsx(data_dir)), end="")
            return 0
        pickup_and_renderer(image)
        original = global_wsx(data_dir)
        spell_counter(image, original)
        regular_item_handlers(image, original)
        seen = verify_copy_banks(data_dir) if args.decode_copy else None
        if args.list:
            print(witness_lines(image), end="")
            if seen is not None:
                for (name, mip) in sorted(seen):
                    print(f"copy {name} mip {mip}: mismatches {COPY_MISMATCHES[mip]}")
            return 0
        detail = f"; {sum(seen.values())} shipped copy mips" if seen is not None else ""
        print(f"CHECK native: pickup, renderer, second-counter and six item-handler anchors{detail}")
    except (OSError, ValueError, StructError, RuntimeError) as error:
        parser.exit(1, f"native checks: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
