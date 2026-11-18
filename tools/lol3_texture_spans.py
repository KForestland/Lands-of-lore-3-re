#!/usr/bin/env python3
"""Find and check the row-span texture records (flags 0x028E / 0x828E) in LoL3's texture cache.

The runtime texture banks sit in cdcache.wsx in the game folder (the parent of
DAT/). A texture record is u32 flags, u16 width, u16 height, u32 size, then
`size` bytes of rows: u16 A, u16 B, B bytes of palette indices placed at
column A & 0x3FFF (A & 0xC000: 0 = opaque copy, 0x4000 = skip index 0).
A record counts only if exactly `height` rows end exactly at the payload end
and every row fits inside the width. Nothing is written: no pixels leave the
game files.

  lol3_texture_spans.py --check --data DAT          # one CHECK line
  lol3_texture_spans.py --data DAT --list 10        # first records: offset, flags, size
"""
import os
import re
import struct
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lol3_cli  # noqa: E402

FLAGS = (0x028E, 0x828E)


def records(blob):
    """Yield (offset, flags, width, height, size, exact) for every plausible span record header."""
    for flag in FLAGS:
        for m in re.finditer(re.escape(struct.pack("<I", flag)), blob):
            o = m.start()
            if o + 12 > len(blob):
                continue
            w, h, size = struct.unpack_from("<HHI", blob, o + 4)
            if not (1 <= w <= 1024 and 1 <= h <= 1024 and 4 <= size <= w * h * 2 + 4 * h and o + 12 + size <= len(blob)):
                continue
            p, end, ok = o + 12, o + 12 + size, True
            for _ in range(h):
                if p + 4 > end:
                    ok = False
                    break
                a, n = struct.unpack_from("<HH", blob, p)
                if (a & 0xC000) not in (0, 0x4000) or (a & 0x3FFF) + n > w:
                    ok = False
                    break
                p += 4 + n
            yield o, flag, w, h, size, ok and p == end


def cache_path(data_dir):
    for name in ("cdcache.wsx", "CDCACHE.WSX"):
        p = os.path.join(os.path.dirname(os.path.abspath(data_dir)), name)
        if os.path.exists(p):
            return p
    return None


def main():
    ap = lol3_cli.tool_args(__doc__)
    ap.add_argument("--list", type=int, default=0)
    a = ap.parse_args()
    path = cache_path(a.data)
    if path is None:
        print("CHECK texture_spans: no cdcache.wsx next to the DAT folder")
        return 1
    blob = open(path, "rb").read()
    recs = list(records(blob))
    if a.list:
        for r in recs[:a.list]:
            print(f"offset {r[0]:,}  flags 0x{r[1]:04X}  {r[2]}x{r[3]}  size {r[4]:,}  exact {r[5]}")
    exact = sum(1 for r in recs if r[5])
    by = Counter(f"0x{r[1]:04X}" for r in recs if r[5])
    if a.check or not a.list:
        print(f"CHECK texture_spans: {os.path.basename(path)} ({len(blob):,} bytes): {len(recs)} span-record candidates, "
              f"{exact} consume exactly height rows inside the width ({dict(by)})")
    return 0 if recs and exact == len(recs) else 1


if __name__ == "__main__":
    sys.exit(main())
