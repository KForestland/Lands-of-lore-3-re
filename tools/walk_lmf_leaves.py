#!/usr/bin/env python3
"""Walk a LoL3 .LMF nested index and list non-directory leaves.

  walk_lmf_leaves.py FILE.LMF [-o report.json]   # one LMF file (for example peeled by extract_wsx_entries.py)
  walk_lmf_leaves.py --check --data DAT          # walk every LMF entry inside the WSX files, write nothing

Record table at 0x100, 16-byte records; block sizes follow (2^n + 2) * 16 + 12 (SIZES below).
What a leaf block holds is open (docs/OPEN_QUESTIONS.md).
"""
from __future__ import annotations
import argparse, json, struct
from collections import Counter
from pathlib import Path

SIZES = {76:1, 108:2, 172:3, 300:4, 556:5, 1068:6, 2092:7, 4140:8, 8236:9, 16428:10}

def walk(path: Path):
    return walk_bytes(path.read_bytes(), path.name)


def walk_bytes(data: bytes, name: str):
    count = struct.unpack_from('<I', data, 4)[0]
    pb = 0x100 + count * 16
    fields = [struct.unpack_from('<I', data, 8 + i * 4)[0] for i in range(count)]
    queue = []
    for i in range(count):
        rel, size, marker, aux = struct.unpack_from('<IIII', data, 0x100 + i * 16)
        queue.append((pb + rel, size))
    seen=set(); leaves=[]; indexes=0
    while queue:
        off, sz = queue.pop(0)
        if (off, sz) in seen or sz not in SIZES: continue
        if off < 0 or off + sz > len(data): continue
        seen.add((off, sz))
        blob = data[off:off+sz]
        if b'\xcd\xcd\xcd\xcd' in blob or b'\xcc\xcd\xcd\xcd' in blob:
            indexes += 1
            for pos in range(0, len(blob)-15, 4):
                a,b,c,d = struct.unpack_from('<IIII', blob, pos)
                if c == 0xCDCDCDCD and d == 0 and b in SIZES:
                    queue.append((a,b))
                elif a == 0xCDCDCDCD and b == 0 and d in SIZES:
                    queue.append((c,d))
        else:
            leaves.append({'offset': off, 'size': sz, 'n': SIZES[sz]})
    return {
        'file': name,
        'size': len(data),
        'count': count,
        'fields0_11': fields[:12],
        'indexes': indexes,
        'leaves': len(leaves),
        'leaf_size_hist': dict(Counter(x['size'] for x in leaves)),
        'leaf_sample': leaves[:50],
    }

def check(data_dir):
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import lol3_cli
    from extract_wsx_entries import parse_wsx
    n = leaves = indexes = 0
    hist = Counter()
    for f in lol3_cli.wsx_files(data_dir):
        try:
            p = parse_wsx(f)
        except ValueError:
            continue
        for e in p["entries"]:
            if e["is_lmf"]:
                rep = walk_bytes(e["blob"], f"{f.name}#{e['index']}")
                n += 1; leaves += rep["leaves"]; indexes += rep["indexes"]
                hist.update({int(k): v for k, v in rep["leaf_size_hist"].items()})
    off_ladder = sorted(k for k in hist if k not in SIZES)
    print(f"CHECK lmf: {n} LMF entries walked; {indexes} index blocks, {leaves} leaf blocks; leaf sizes "
          f"{dict(sorted(hist.items()))}; sizes off the ladder: {off_ladder or 'none'}")
    return 0 if n and not off_ladder else 1


def main():
    import os
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('lmf', type=Path, nargs='?')
    ap.add_argument('-o', type=Path)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--data', type=Path, default=os.environ.get('LOL3_DAT'))
    args = ap.parse_args()
    if args.check:
        if args.data is None:
            ap.error("give --data (the game's DAT folder) or set LOL3_DAT")
        return check(args.data)
    if args.lmf is None:
        ap.print_help(); return 2
    rep = walk(args.lmf)
    text = json.dumps(rep, indent=2)
    if args.o:
        args.o.write_text(text)
    print(text[:2000])
    print('...')
    print('leaves', rep['leaves'], 'indexes', rep['indexes'], 'hist', rep['leaf_size_hist'])

if __name__ == '__main__':
    raise SystemExit(main())
