#!/usr/bin/env python3
"""Re-prove the shipped cdcache body and that allocator byte +0x17 has no address.

  lol3_cache_seed.py --data DAT            # header bytes and, when present, the second directory
  lol3_cache_seed.py --data DAT --check
"""
from hashlib import sha256
from pathlib import Path
from struct import unpack_from

import lol3_cli
from lol3_script_framing import RETAIL_PE

BLOCK = 64000
COPIES = 51
HEADER = 114
BLOCK_SHA = "bba1aa5f85ce13bfe9a493a445bea858c270db9bea543bac83d6df6d35730fad"


HEADER_SHA = "9b66af6f5ca8880f5b44efc3f87d36f69c4348ff42dd25871cb81b820591e829"
FILL_MARKER = 0xD0BCD8BE


def body_covers(data, header_sha=HEADER_SHA, block_sha=BLOCK_SHA, block_size=BLOCK, copies=COPIES):
    """True when data is the pinned 114-byte header, dword +0x72 is the fill marker and the rest is
    `copies` copies of the pinned block, as the --check run requires."""
    if len(data) != HEADER + copies * block_size:
        return False
    if sha256(data[:HEADER]).hexdigest() != header_sha:
        return False
    if unpack_from("<I", data, 0x72)[0] != FILL_MARKER:
        return False
    block = data[HEADER:HEADER + block_size]
    if sha256(block).hexdigest() != block_sha:
        return False
    return all(
        data[HEADER + index * block_size:HEADER + (index + 1) * block_size] == block
        for index in range(copies))


def shipped_body_covers(path):
    """True when the shipped cdcache.wsx is the pinned header plus 51 copies of the pinned block."""
    path = Path(path)
    if path.stat().st_size != HEADER + COPIES * BLOCK:
        return False
    return body_covers(path.read_bytes())


# Little-endian address of row 0's bytes +0x14 through +0x17 in the code section.
FLAG_ADDRESSES = {0x7F3A0C: 7, 0x7F3A0D: 6, 0x7F3A0E: 5, 0x7F3A0F: 0}


def code_section(image):
    # .text, raw 0x400, 0x136400 bytes. Same file identified by RETAIL_PE.
    return image[0x400:0x400 + 0x136400]


def hex_lines(blob, origin=0):
    lines = []
    for offset in range(0, len(blob), 16):
        chunk = blob[offset:offset + 16]
        lines.append(f"+{origin + offset:#x}: " + " ".join(f"{byte:02x}" for byte in chunk))
    return lines


def shipped_listing(data):
    """Page facts for the shipped file, then the 114 header bytes with no field names."""
    if len(data) < 0x76:
        raise ValueError("shipped cache does not reach the marker at +0x72")
    marker = unpack_from("<I", data, 0x72)[0]
    lines = [
        f"shipped {len(data)} bytes",
        f"header {HEADER} bytes",
        f"dword +0x72 {marker:#x}",
    ]
    if body_covers(data):
        lines.append(f"{COPIES} copies of {BLOCK} bytes")
    lines.extend(hex_lines(data[:HEADER]))
    return "\n".join(lines) + "\n"


def written_listing(prefix):
    """Forty rows of 0x18 at +0x76. Names are the page's; byte +0x17 stays a byte offset."""
    need = 0x76 + 40 * 0x18
    if len(prefix) < need:
        raise ValueError("game-written cache prefix does not cover the second directory")
    marker = unpack_from("<I", prefix, 0x72)[0]
    lines = [f"game-written marker +0x72 {marker:#x}", "second directory +0x76: 40 rows of 0x18"]
    for index in range(40):
        at = 0x76 + index * 0x18
        position, span, key, clock, generation = unpack_from("<5I", prefix, at)
        allocated, generation_index, pin, tail = prefix[at + 0x14:at + 0x18]
        lines.append(
            f"row {index} +{at:#x}: position {position:#x} span {span:#x} key {key:#x} "
            f"clock {clock:#x} generation {generation:#x} allocated {allocated} "
            f"generation index {generation_index} pin {pin} +0x17 {tail:#x}")
    return "\n".join(lines) + "\n"


def main():
    parser = lol3_cli.tool_args(__doc__, writes=False)
    args = parser.parse_args()
    if args.out:
        parser.error("prints only")
    if not args.check:
        data = Path(args.data)
        try:
            shipped_path = data / "cdcache.wsx"
            header_path = data.resolve().parent / "cdcache.hdr"
            shipped = shipped_path.read_bytes()
            header = header_path.read_bytes() if header_path.is_file() else b""
            text = shipped_listing(shipped)
            if header == shipped[:HEADER]:
                text = "cdcache.hdr matches the first 114 bytes\n" + text
            print(text, end="")
            game_path = data.resolve().parent / "cdcache.wsx"
            if game_path.is_file():
                with game_path.open("rb") as handle:
                    prefix = handle.read(0x76 + 40 * 0x18)
                print(written_listing(prefix), end="")
            else:
                print("game-written cache absent")
        except (OSError, ValueError) as exc:
            parser.exit(1, f"cache seed: {exc}\n")
        return 0
    data = Path(args.data)
    try:
        image = (data.resolve().parent / "LOL3.DAT").read_bytes()
        if sha256(image).hexdigest() != RETAIL_PE:
            raise ValueError("LOL3.DAT does not match the documented English retail executable")
        text = code_section(image)
        counts = {}
        for address, expected in FLAG_ADDRESSES.items():
            counts[address] = text.count(address.to_bytes(4, "little"))
            if counts[address] != expected:
                raise ValueError(f"address {address:#x} occurs {counts[address]} times")
        shipped_path = data / "cdcache.wsx"
        header_path = data.resolve().parent / "cdcache.hdr"
        shipped = shipped_path.read_bytes()
        header = header_path.read_bytes()
        if len(header) != HEADER or shipped[:HEADER] != header or len(shipped) != HEADER + COPIES * BLOCK:
            raise ValueError(f"shipped cache {len(shipped)} header {len(header)}")
        if sha256(header).hexdigest() != HEADER_SHA:
            raise ValueError("cdcache.hdr does not match the pinned header")
        if unpack_from("<I", shipped, 0x72)[0] != FILL_MARKER:
            raise ValueError("shipped dword +0x72 is not the fill block")
        block = shipped[HEADER:HEADER + BLOCK]
        if sha256(block).hexdigest() != BLOCK_SHA or any(
                shipped[HEADER + index * BLOCK:HEADER + (index + 1) * BLOCK] != block
                for index in range(COPIES)):
            raise ValueError("shipped body is not 51 copies of the pinned block")
        game_path = data.resolve().parent / "cdcache.wsx"
        witness = ""
        if game_path.is_file():
            game = game_path.read_bytes()
            if game[:HEADER] != header or len(game) != 104896114:
                raise ValueError(f"game-written cache is {len(game)} bytes")
            if unpack_from("<I", game, 0x72)[0] != 0xF1E2D3C4:
                raise ValueError("game-written marker is not 0xF1E2D3C4")
            if game.find(block[:32]) >= 0:
                raise ValueError("the shipped fill block occurs in the game-written cache")
            occupied = empty = same = 0
            for index in range(40):
                at = 0x76 + index * 0x18
                flags = game[at + 0x14:at + 0x18]
                if flags[0]:
                    occupied += 1
                    if flags[3] != 0x67:
                        raise ValueError(f"occupied row {index} byte +0x17 is {flags[3]:#x}")
                elif flags[3] == 0x67:
                    empty += 1
                if flags[2] == flags[3]:
                    same += 1
            if (occupied, empty, same) != (8, 12, 17):
                raise ValueError(f"byte +0x17 census occupied {occupied} empty-0x67 {empty} equal +0x16 {same}")
            witness = "; 8 occupied rows hold 0x67"
        else:
            witness = "; game-written cache absent"
    except (OSError, ValueError) as exc:
        print(f"CHECK cache_seed FAILED: {exc}")
        return 1
    print("CHECK cache_seed: shipped cdcache is 114 bytes plus 51 copies of one 64,000-byte block; "
          f"row byte +0x17 has no code address{witness}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
