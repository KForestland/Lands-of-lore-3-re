#!/usr/bin/env python3
"""Check original LoL3 pickup and texture witnesses.

  lol3_native_checks.py --data DAT --check
  lol3_native_checks.py --data DAT --check --decode-copy   # shipped banks, liblzo2
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from struct import error as StructError, unpack_from

import lol3_cli
from lol3_script_framing import CODE_BIAS, RETAIL_PE
from lol3_texture_archive import chunks, texture_entries
from lol3_texture_png import UNCONFIRMED_FLAGS, cache_textures, texture_payload
from walk_lmf_leaves import lzo_decoder

COPY_BANKS = {"BUPP1", "EWOD1", "QWOD0", "RVOL0"}
COPY_MISMATCHES = (500, 244, 116, 52, 24)


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
    return sum(seen.values())


def main():
    parser = lol3_cli.tool_args(__doc__)
    parser.add_argument("--decode-copy", action="store_true", help="compare all 20 shipped copy mips")
    args = parser.parse_args()
    if args.out:
        parser.error("this check writes counts to standard output")
    try:
        data_dir = Path(args.data).resolve()
        image = (data_dir.parent / "LOL3.DAT").read_bytes()
        if sha256(image).hexdigest() != RETAIL_PE:
            raise ValueError("LOL3.DAT does not match the documented English retail executable")
        pickup_and_renderer(image)
        detail = f"; {verify_copy_banks(data_dir)} shipped copy mips" if args.decode_copy else ""
        print(f"CHECK native: pickup and renderer anchors{detail}")
    except (OSError, ValueError, StructError, RuntimeError) as error:
        parser.exit(1, f"native checks: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
