#!/usr/bin/env python3
"""Walk a LoL3 .LMF nested index and list non-directory leaves."""
from __future__ import annotations
import argparse, json, struct
from collections import Counter
from pathlib import Path

SIZES = {76:1, 108:2, 172:3, 300:4, 556:5, 1068:6, 2092:7, 4140:8, 8236:9, 16428:10}

def walk(path: Path):
    data = path.read_bytes()
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
        'file': path.name,
        'size': len(data),
        'count': count,
        'fields0_11': fields[:12],
        'indexes': indexes,
        'leaves': len(leaves),
        'leaf_size_hist': dict(Counter(x['size'] for x in leaves)),
        'leaf_sample': leaves[:50],
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('lmf', type=Path)
    ap.add_argument('-o', type=Path)
    args = ap.parse_args()
    rep = walk(args.lmf)
    text = json.dumps(rep, indent=2)
    if args.o:
        args.o.write_text(text)
    print(text[:2000])
    print('...')
    print('leaves', rep['leaves'], 'indexes', rep['indexes'], 'hist', rep['leaf_size_hist'])

if __name__ == '__main__':
    main()
