#!/usr/bin/env python3
"""Re-prove the MAP spans tabulated for question Q4.

  lol3_map_spans.py --data DAT --check
  lol3_map_spans.py --data DAT --list QWOD0   # waypoint fields and slot bytes; no label text
  lol3_map_spans.py --data DAT --rows QWOD0   # section-1 bytes the page names
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from struct import unpack_from

import lol3_cli
from lol3_script_framing import RETAIL_PE, level_map_entries

GAPS = {
    "BUPP1": 248, "CKEEP": 104, "DLOW1": 304, "EWOD1": 56, "FLAIR": 80,
    "GRULO": 0, "HWHIT": 152, "ISHAT": 0, "JUNDR": 16, "KVOLC": 0,
    "LUPP2": 168, "MLOW2": 304, "NWOD2": 40, "OLOW3": 272, "PWOD3": 40,
    "QWOD0": 0, "RVOL0": 0, "SWOD4": 0,
}
WP6 = {
    0: 114, 1: 57, 2: 1957, 4: 3, 6: 3, 10: 2, 12: 8, 15: 180, 23: 2,
    31: 3, 37: 1, 46: 27, 78: 4, 125: 20, 255: 3,
}
WP7 = {0: 304, 4: 2067, 5: 13}
ONLY2 = {"CKEEP", "ISHAT", "JUNDR", "MLOW2", "OLOW3", "QWOD0"}
NO_PATH = ONLY2 - {"JUNDR"} | {"GRULO"}
WAYPOINT_CD = {
    "BUPP1": 1, "DLOW1": 1, "EWOD1": 3, "FLAIR": 2, "HWHIT": 1, "KVOLC": 21,
    "LUPP2": 1, "NWOD2": 3, "PWOD3": 3, "SWOD4": 3,
}
BADNAME = b"BadName\x00" + b"\x00\x00\x00\x00" + b"\x01\x00\x00\x00" * 3 + b"\x00\x00"
BAD_AT = {
    ("BUPP1", 35), ("FLAIR", 1), ("FLAIR", 3),
    ("LUPP2", 3), ("LUPP2", 5), ("LUPP2", 6), ("LUPP2", 7), ("LUPP2", 8),
    ("LUPP2", 9), ("LUPP2", 10), ("LUPP2", 11), ("LUPP2", 12), ("LUPP2", 13),
    ("LUPP2", 14), ("LUPP2", 35),
}
# The 36 path labels are level-author text: the check compares counts and a digest, never the strings.
# 19 distinct labels; the most common one occurs 13 times; two labels carry one extra NUL (in two levels each).
PATHS_DIGEST = "2880ef4cf848bf11"
EXTRA_NUL_DIGEST = "bedbfd1d6ab612d8"


def label_digest(counter):
    """sha256 prefix of the sorted 'label<TAB>count' lines."""
    return sha256("\n".join(f"{k}\t{v}" for k, v in sorted(counter.items())).encode()).hexdigest()[:16]


ABSENT = (b"WayPoint", b"BadName")


def u32(buf, at):
    return unpack_from("<I", buf, at)[0]


def census(data_dir):
    image = (Path(data_dir).resolve().parent / "LOL3.DAT").read_bytes()
    if sha256(image).hexdigest() != RETAIL_PE:
        raise ValueError("LOL3.DAT does not match the documented English retail executable")
    wp6, wp7 = Counter(), Counter()
    names = Counter()
    bad_at = set()
    waypoint_cd = Counter()
    zero_len = []
    paths = Counter()
    extra_nul = Counter()
    no_path = set()
    gaps = {}
    quads = share0 = out_of_range = 0
    header_hit = set()
    rows = under = ffff = 0
    word_min = word_max = None
    b4_128 = b4_values = b7_zero = 0
    b4_seen, b5_seen, b6_seen, b7_seen = set(), set(), set(), set()
    b5_top, b6_top = Counter(), Counter()
    pair_min, pair_max = None, None
    only2 = set()
    n_maps = 0
    for stem, _, payload in level_map_entries(data_dir):
        n_maps += 1
        f1, f2 = u32(payload, 0x08), u32(payload, 0x0C)
        f16, f19 = u32(payload, 0x44), u32(payload, 0x50)
        f20, f21 = u32(payload, 0x54), u32(payload, 0x58)
        c4, c8 = u32(payload, 0xC4), u32(payload, 0xC8)
        d8, dc = u32(payload, 0xD8), u32(payload, 0xDC)
        f0 = u32(payload, 4)
        if c8 != f0 + 8 * f19 or dc != c8 + 34 * c4 or f1 - c8 != 34 * c4 + 35 * d8:
            raise ValueError(f"{stem}: waypoint partition does not hold")
        level6 = Counter()
        for i in range(c4):
            row = payload[c8 + 8 * i:c8 + 8 * i + 8]
            wp6[row[6]] += 1
            wp7[row[7]] += 1
            level6[row[6]] += 1
            slot = payload[c8 + 8 * c4 + 26 * i:c8 + 8 * c4 + 26 * i + 26]
            if slot == BADNAME:
                names["bad"] += 1
                bad_at.add((stem, i))
            elif slot[:9] == b"WayPoint\x00" and slot[25] == 0 and all(b == 0xCD for b in slot[9:25]):
                names["waypoint"] += 1
                waypoint_cd[stem] += 1
            else:
                nul = slot.find(0)
                text, rest = slot[:nul], slot[nul + 1:]
                if nul < 1 or any(b != 0 for b in rest) or any(c < 32 or c > 126 for c in text):
                    names["other"] += 1
                else:
                    names["zero"] += 1
                    zero_len.append(nul)
        if set(level6) == {2}:
            only2.add(stem)
        if d8 == 0:
            no_path.add(stem)
        for i in range(d8):
            slot = payload[dc + 4 * d8 + 31 * i:dc + 4 * d8 + 31 * i + 31]
            nul = slot.find(0)
            text, rest = slot[:nul], slot[nul + 1:]
            z = 0
            while z < len(rest) and rest[z] == 0:
                z += 1
            if (nul < 1 or any(c < 32 or c > 126 for c in text)
                    or any(b != 0xCD for b in rest[z:])):
                paths["<bad>"] += 1
            else:
                paths[text.decode("ascii")] += 1
                if z:
                    extra_nul[text.decode("ascii")] += 1
        gap_at = f2 + 56 * f21
        gaps[stem] = f16 - gap_at
        if any(u32(payload, off) == gap_at for off in range(0, 0x244, 4)):
            header_hit.add(stem)
        blob = payload[gap_at:f16]
        for q in range(len(blob) // 8):
            words = unpack_from("<4H", blob, q * 8)
            quads += 1
            if any(w >= f19 or w >= f21 for w in words):
                out_of_range += 1
            sets = [set(unpack_from("<4H", payload, f2 + w * 56 + 0x10)) for w in words]
            shares = tuple(len(a & b) for a, b in zip(sets, sets[1:] + sets[:1]))
            if shares == (0, 0, 0, 0):
                share0 += 1
        for i in range(f20):
            row = payload[f1 + 8 * i:f1 + 8 * i + 8]
            word = unpack_from("<H", row, 0)[0]
            pair = unpack_from("<H", row, 4)[0]
            rows = 0 if rows is None else rows
            rows += 1
            word_min = word if word_min is None else min(word_min, word)
            word_max = word if word_max is None else max(word_max, word)
            pair_min = pair if pair_min is None else min(pair_min, pair)
            pair_max = pair if pair_max is None else max(pair_max, pair)
            if word == 0xFFFF:
                ffff += 1
            elif word < f19 and word < f21:
                under += 1
            b4_seen.add(row[4])
            b5_seen.add(row[5] & 0x1F)
            b6_seen.add(row[6])
            b7_seen.add(row[7])
            if row[4] == 128:
                b4_128 += 1
            if row[7] == 0:
                b7_zero += 1
            b5_top[row[5] & 0x1F] += 1
            b6_top[row[6]] += 1
    absent = [n for n in ABSENT if n in image]
    return {
        "maps": n_maps, "wp6": wp6, "wp7": wp7, "only2": only2, "names": names,
        "bad_at": bad_at, "waypoint_cd": waypoint_cd, "zero_len": zero_len,
        "paths": paths, "extra_nul": extra_nul, "no_path": no_path,
        "gaps": gaps, "quads": quads,
        "share0": share0, "out_of_range": out_of_range, "header_hit": header_hit,
        "rows": rows, "under": under, "ffff": ffff, "word_min": word_min,
        "word_max": word_max, "pair_min": pair_min, "pair_max": pair_max,
        "b4_128": b4_128, "b4n": len(b4_seen), "b5n": len(b5_seen),
        "b6n": len(b6_seen), "b7n": len(b7_seen), "b7_zero": b7_zero,
        "b5_top": b5_top, "b6_top": b6_top, "absent": absent,
    }


def mismatches(got):
    bad = []
    expect = {
        "maps": 18, "quads": 223, "share0": 113, "out_of_range": 0,
        "rows": 167942, "under": 165745, "ffff": 213, "word_min": 1, "word_max": 65535,
        "pair_min": 10, "pair_max": 8191, "b4_128": 162397, "b4n": 161, "b5n": 32,
        "b6n": 21, "b7n": 128, "b7_zero": 160071,
    }
    for key, value in expect.items():
        if got[key] != value:
            bad.append(f"{key} {got[key]} != {value}")
    if dict(got["wp6"]) != WP6:
        bad.append("waypoint +6")
    if dict(got["wp7"]) != WP7:
        bad.append("waypoint +7")
    if got["only2"] != ONLY2:
        bad.append("levels with only +6 = 2")
    if got["names"] != Counter({"zero": 2330, "waypoint": 39, "bad": 15}):
        bad.append(f"names {got['names']}")
    if got["bad_at"] != BAD_AT or dict(got["waypoint_cd"]) != WAYPOINT_CD:
        bad.append("name placement")
    if not got["zero_len"] or min(got["zero_len"]) != 3 or max(got["zero_len"]) != 25:
        bad.append("name lengths")
    if (sum(got["paths"].values()) != 36 or len(got["paths"]) != 19 or label_digest(got["paths"]) != PATHS_DIGEST
            or label_digest(got["extra_nul"]) != EXTRA_NUL_DIGEST):
        bad.append("path labels")
    if got["no_path"] != NO_PATH:
        bad.append(f"levels with no path {sorted(got['no_path'])}")
    if got["gaps"] != GAPS:
        bad.append("gap lengths")
    empty = {stem for stem, length in GAPS.items() if length == 0}
    if got["header_hit"] != empty:
        bad.append(f"header points at gap start on {sorted(got['header_hit'])}")
    if got["b5_top"][4] != 26616 or got["b5_top"][5] != 32254 or got["b5_top"][6] != 33511 or got["b5_top"][7] != 27297:
        bad.append("section-1 byte +5")
    if got["b6_top"][16] != 83014 or got["b6_top"][8] != 74591 or got["b6_top"][0] != 6811:
        bad.append("section-1 byte +6")
    if got["absent"]:
        bad.append("executable contains a label")
    return bad


def row_listing(payload, stem):
    """Waypoint fields, and the following slots as hex. Label text is not decoded."""
    count, start = u32(payload, 0xC4), u32(payload, 0xC8)
    paths, path_at = u32(payload, 0xD8), u32(payload, 0xDC)
    slot_at = start + 8 * count
    label_at = path_at + 4 * paths
    need = max(slot_at + 26 * count, label_at + 31 * paths)
    if need > len(payload):
        raise ValueError(f"{stem}: waypoint rows run past the MAP")
    lines = [f"{stem} waypoints {count} paths {paths}"]
    for index in range(count):
        row = payload[start + 8 * index:start + 8 * index + 8]
        horizontal_x, horizontal_z, surface = unpack_from("<hhH", row)
        lines.append(f"waypoint {index + 1}: x {horizontal_x} z {horizontal_z} "
                     f"surface {surface:#x} +6 {row[6]:#x} +7 {row[7]:#x}")
        slot = payload[slot_at + 26 * index:slot_at + 26 * index + 26]
        lines.append(f"slot {index + 1}: " + " ".join(f"{byte:02x}" for byte in slot))
    for index in range(paths):
        first, path_count, flags = unpack_from("<HBB", payload, path_at + 4 * index)
        lines.append(f"path {index + 1}: first {first} count {path_count} flags {flags:#x}")
        label = payload[label_at + 31 * index:label_at + 31 * index + 31]
        lines.append(f"path slot {index + 1}: " + " ".join(f"{byte:02x}" for byte in label))
    return "\n".join(lines) + "\n"


def section1_listing(payload, stem):
    """Section-1 bytes named on the reader page. No names for the bits whose meaning is open."""
    start, count = u32(payload, 0x08), u32(payload, 0x54)
    if start + 8 * count > len(payload):
        raise ValueError(f"{stem}: section-1 rows run past the MAP")
    lines = [f"{stem} section-1 rows {count}"]
    for index in range(count):
        row = payload[start + 8 * index:start + 8 * index + 8]
        word, = unpack_from("<H", row)
        lines.append(
            f"row {index + 1}: +0 {word:#x} +2 {row[2]:#x} +3 {row[3]:#x} "
            f"+4 {row[4]:#x} +5 {row[5]:#x} +5&0x1f {row[5] & 0x1F:#x} "
            f"+6 {row[6]:#x} +7 {row[7]:#x}")
    return "\n".join(lines) + "\n"


def main():
    ap = lol3_cli.tool_args(__doc__, writes=False)
    ap.add_argument("--list", help="print one level's waypoint rows and slot bytes")
    ap.add_argument("--rows", help="print one level's section-1 rows")
    a = ap.parse_args()
    if a.out:
        ap.error("prints only")
    if a.list and a.rows:
        ap.error("pass only one of --list and --rows")
    if a.rows:
        if a.check:
            ap.error("--check does not list")
        try:
            stem = a.rows.upper()
            found = [item for item in level_map_entries(a.data) if item[0] == stem]
            if len(found) != 1:
                raise ValueError(f"expected one MAP for {stem}")
            print(section1_listing(found[0][2], stem), end="")
        except (OSError, ValueError) as exc:
            ap.exit(1, f"map spans: {exc}\n")
        return 0
    if a.list:
        if a.check:
            ap.error("--check does not list")
        try:
            stem = a.list.upper()
            found = [item for item in level_map_entries(a.data) if item[0] == stem]
            if len(found) != 1:
                raise ValueError(f"expected one MAP for {stem}")
            print(row_listing(found[0][2], stem), end="")
        except (OSError, ValueError) as exc:
            ap.exit(1, f"map spans: {exc}\n")
        return 0
    if not a.check:
        ap.error("pass --check, --list LEVEL or --rows LEVEL")
    try:
        bad = mismatches(census(a.data))
    except (OSError, ValueError) as exc:
        print(f"CHECK map_spans FAILED: {exc}")
        return 1
    if bad:
        print("CHECK map_spans FAILED: " + "; ".join(bad))
        return 1
    print("CHECK map_spans: 18 maps; 2,384 waypoints; name slots 2,330/39/15; "
          "36 path labels; 1,784 gap bytes in 223 groups; 167,942 section-1 rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
