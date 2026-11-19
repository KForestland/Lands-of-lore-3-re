#!/usr/bin/env python3
"""Re-prove where the claimed QWOD0 and SWOD4 edge bytes sit in the archives.

  lol3_claimed_edges.py --data DAT --check
  lol3_claimed_edges.py --data DAT --check --decode   # also the light-map samples
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from struct import unpack_from

import lol3_cli
from lol3_script_framing import CODE_BIAS, RETAIL_PE, level_map_entries

# Entry hashes of LEVELS\<stem>\<stem>.<suffix>, file offsets of the QWOD0 C5 A5 bytes.
QWOD0_C5A5 = {
    0xE128E119: 195,  # texture
    0xD0B8E10A: 2,    # MAP
    0x00A8E101: 1,    # light map
    0xDCD8E100: 0,    # ODF
}
QWOD0_AT = (0x694783, 0x730744, 0x730748)
TE_MOD8 = {0: 22, 1: 24, 2: 27, 3: 28, 4: 24, 5: 21, 6: 20, 7: 29}
SWOD4_PLUS4 = {0: 2393, 2: 14, 6: 29, 0x0B: 0}
MAP_HEADER = 0x244
MAP_VERTICES = 0x2F2C
SHARED_MAP_DIGEST = "5a4e63f1dd12c59cb726c3a133e2acfbdb366a5149a71a0a72bfcbf88631218a"
MAP_SEEKS = {
    0x43E884: 0x28, 0x43E927: 0xB4, 0x43E953: 0xBC, 0x43E97D: 0x38,
    0x43E9BD: 0x3C, 0x43E9FD: 0x40, 0x43EA3D: 0x4C, 0x43EA79: 0x44,
    0x43EAB9: 0x04, 0x43EAE6: 0x0C, 0x43EB16: 0xA4, 0x43EB46: 0x34,
    0x43EB83: 0x08, 0x43EBB0: 0x2C, 0x43EBE3: 0xC8, 0x43EC57: 0xDC,
    0x43EEB6: 0x14, 0x43EEE0: 0x18, 0x43EF0A: 0x1C, 0x43EF34: 0x24,
    0x43EF5E: 0x20, 0x43EF9A: 0x48,
}


def u32(buf, at):
    return unpack_from("<I", buf, at)[0]


def archive(path):
    blob = path.read_bytes()
    count = unpack_from("<H", blob, 0)[0]
    entries = []
    for index in range(count):
        key, off, length = unpack_from("<III", blob, 6 + 12 * index)
        entries.append((key, 54 + off, blob[54 + off:54 + off + length]))
    return entries


def column_hits(payload, start, count, stride, pair):
    a, b = pair
    hits = 0
    for phase in range(stride):
        col = payload[start + phase:start + phase + count * stride:stride]
        hits += sum(1 for left, right in zip(col, col[1:]) if left == a and right == b)
    return hits


def check_shared_map_block(image, maps):
    header_read = 0x43E7DA - CODE_BIAS
    if image[header_read:header_read + 21] != bytes.fromhex(
        "8d 54 24 14 8b f8 68 44 02 00 00 52 57 e8 b4 6f ff ff 83 c4 0c"
    ):
        raise ValueError("MAP header read changed")
    seeks = set()
    for va in range(0x43E6B0, 0x43F1F4):
        at = va - CODE_BIAS
        if image[at] == 0xE8 and va + 5 + unpack_from("<i", image, at + 1)[0] == 0x435A90:
            seeks.add(va)
    if seeks != MAP_SEEKS.keys():
        raise ValueError("MAP loader seek sites changed")
    for va, field in MAP_SEEKS.items():
        at = va - CODE_BIAS - 3
        stack_slot = field + 0x14
        register = image[at + 1] - 0x50  # push eax, ecx or edx
        if not 0 <= register <= 2:
            raise ValueError(f"MAP seek {va:#x} register changed")
        width = 1 if stack_slot < 0x80 else 4
        form = 0x44 if width == 1 else 0x84
        load = bytes((0x8B, form | register << 3, 0x24)) + stack_slot.to_bytes(width, "little")
        if va == 0x43E884:
            load += b"\x33\xdb"  # first seek also zeros ebx (origin)
        if image[at - len(load):at + 3] != load + bytes((0x53, 0x50 + register, 0x57)):
            raise ValueError(f"MAP seek {va:#x} no longer uses header +{field:#x}")
    if len(maps) != 18:
        raise ValueError(f"expected 18 MAPs, found {len(maps)}")
    for stem, payload in maps.items():
        if (u32(payload, 0xCC), u32(payload, 4)) != (MAP_HEADER, MAP_VERTICES):
            raise ValueError(f"{stem}: shared MAP block bounds changed")
        if any(u32(payload, field) < MAP_VERTICES for field in MAP_SEEKS.values()):
            raise ValueError(f"{stem}: native seek before MAP vertices")
        block = payload[MAP_HEADER:MAP_VERTICES]
        if len(block) != 4 + 4 * u32(block, 0) or sha256(block).hexdigest() != SHARED_MAP_DIGEST:
            raise ValueError(f"{stem}: shared MAP block contents changed")


def file_facts(data_dir):
    image = (Path(data_dir).resolve().parent / "LOL3.DAT").read_bytes()
    if sha256(image).hexdigest() != RETAIL_PE:
        raise ValueError("LOL3.DAT does not match the documented English retail executable")
    qw = archive(Path(data_dir) / "QWOD0.WSX")
    counts = {}
    te_pos = []
    at = []
    for key, file_at, payload in qw:
        found = []
        start = 0
        while True:
            hit = payload.find(b"\xC5\xA5", start)
            if hit < 0:
                break
            found.append(file_at + hit)
            start = hit + 1
        counts[key] = len(found)
        if key == 0xE128E119:
            te_pos = [pos - file_at for pos in found]
        else:
            at.extend(found)
    maps = {stem: payload for stem, _, payload in level_map_entries(data_dir)}
    check_shared_map_block(image, maps)
    qw_map = maps["QWOD0"]
    column = 0
    for start, count, stride in (
        (u32(qw_map, 4), u32(qw_map, 0x50), 8),
        (u32(qw_map, 0x08), u32(qw_map, 0x54), 8),
        (u32(qw_map, 0x0C), u32(qw_map, 0x58), 56),
        (u32(qw_map, 0xC8), u32(qw_map, 0xC4), 8),
    ):
        column += column_hits(qw_map, start, count, stride, (0xC5, 0xA5))
    sw = maps["SWOD4"]
    plus4 = Counter()
    surface_at, surfaces = u32(sw, 0x0C), u32(sw, 0x58)
    for index in range(surfaces):
        plus4[sw[surface_at + index * 56 + 4]] += 1
    qw_surface = Counter()
    surface_at, surfaces = u32(qw_map, 0x0C), u32(qw_map, 0x58)
    for index in range(surfaces):
        qw_surface[qw_map[surface_at + index * 56 + 4]] += 1
    return {
        "pe": image.count(b"\xC5\xA5"),
        "counts": counts,
        "at": tuple(sorted(at)),
        "te_mod8": Counter(pos % 8 for pos in te_pos),
        "te_gap": Counter(b - a for a, b in zip(te_pos, te_pos[1:])).most_common(1),
        "column": column,
        "plus4": plus4,
        "qw_marked": sum(qw_surface[v] for v in (0xAD, 0xC5, 0xA5, 0xEB)),
    }


def decode_facts(data_dir):
    from extract_wsx_entries import parse_wsx
    from walk_lmf_leaves import lmf_groups, lzo_decoder

    decode = lzo_decoder()
    out = {}
    for filename in ("QWOD0.WSX", "swod4.wsx"):
        archive_entries = parse_wsx(Path(data_dir) / filename)
        blob = next(entry["blob"] for entry in archive_entries["entries"] if entry["is_lmf"])
        members = highs = marked = 0
        for group in lmf_groups(blob):
            raw = decode(blob[group["offset"]:group["offset"] + group["packed"]], group["expanded"])
            at = 0
            for size in group["lengths"]:
                _, width, height, _ = unpack_from("<IHHI", raw, at)
                grid = raw[at + 44:at + 44 + 2 * width * height]
                highs += sum(1 for i in range(1, len(grid), 2) if grid[i] in (0x0B, 0xC5, 0xA5, 0xAD, 0xEB))
                marked += 1
                members += 1
                at += size
        out[filename] = (members, highs)
    return out


def main():
    ap = lol3_cli.tool_args(__doc__)
    ap.add_argument("--decode", action="store_true", help="also decode the two light maps")
    a = ap.parse_args()
    if not a.check:
        ap.error("this tool only checks; pass --check")
    try:
        got = file_facts(a.data)
        bad = []
        if got["pe"] != 1 or got["counts"] != QWOD0_C5A5 or got["at"] != QWOD0_AT:
            bad.append(f"placements pe {got['pe']} counts {got['counts']} at {got['at']}")
        if dict(got["te_mod8"]) != TE_MOD8 or not got["te_gap"] or got["te_gap"][0][1] != 2:
            bad.append("texture alignment")
        if got["column"] != 0 or got["qw_marked"] != 0:
            bad.append(f"map columns {got['column']} marked surface bytes {got['qw_marked']}")
        if any(got["plus4"][value] != count for value, count in SWOD4_PLUS4.items()):
            bad.append(f"SWOD4 surface +4 { {k: got['plus4'][k] for k in SWOD4_PLUS4} }")
        decoded = ""
        if a.decode:
            lights = decode_facts(a.data)
            if lights != {"QWOD0.WSX": (5364, 0), "swod4.wsx": (10232, 0)}:
                bad.append(f"light maps {lights}")
            decoded = "; decoded sample high bytes 0"
    except (OSError, ValueError) as exc:
        print(f"CHECK claimed_edges FAILED: {exc}")
        return 1
    if bad:
        print("CHECK claimed_edges FAILED: " + "; ".join(bad))
        return 1
    print("CHECK claimed_edges: QWOD0 C5 A5 is 195/2/1/0 across texture, MAP, light map and ODF; "
          f"no MAP column steps from C5 to A5; SWOD4 surface +4 is 0/2/6/0x0B on 2393/14/29/0 rows{decoded}")
    print("CHECK claimed_edges: 18 identical 0x2CE8-byte MAP blocks fit 2,873 four-byte rows; "
          "all 22 native post-header seeks start at the vertices or later")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
