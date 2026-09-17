#!/usr/bin/env python3
"""Peel LoL3 .WSX containers into entry blobs + LMF candidates.

Reproduces the staged layout under lol3_extracted for the four witness
families (QWOD0, SWOD4, RVOL0, CKEEP) from retail DAT/*.WSX files.

WSX layout (verified 2026-09-17 against staged peels):
  - 6-byte prefix
  - 4x 12-byte records: <u32 hash><u32 unk><u32 size>  (little-endian)
  - concatenated payloads in size-descending order (sum(sizes) == file_size-54)

Does not ship or require anything outside the retail install + output dir.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path


HEADER_PREFIX = 6
RECORD_SIZE = 12
RECORD_COUNT = 4
PAYLOAD_BASE = HEADER_PREFIX + RECORD_COUNT * RECORD_SIZE  # 54


def sha1(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def parse_wsx(path: Path) -> dict:
    data = path.read_bytes()
    if len(data) < PAYLOAD_BASE:
        raise ValueError(f"{path}: too small for WSX header")
    records = []
    for i in range(RECORD_COUNT):
        off = HEADER_PREFIX + i * RECORD_SIZE
        h, unk, size = struct.unpack_from("<III", data, off)
        records.append({"index": i, "hash": h, "hash_hex": f"{h:08X}", "unk": unk, "size": size})
    total = sum(r["size"] for r in records)
    if PAYLOAD_BASE + total != len(data):
        raise ValueError(
            f"{path}: size mismatch header_sum={PAYLOAD_BASE+total} file={len(data)}"
        )
    # Payloads packed largest-first
    ordered = sorted(records, key=lambda r: r["size"], reverse=True)
    cursor = PAYLOAD_BASE
    entries = []
    for rec in ordered:
        blob = data[cursor : cursor + rec["size"]]
        if len(blob) != rec["size"]:
            raise ValueError(f"{path}: truncated entry {rec['hash_hex']}")
        # LMF heuristic used by lol3_re_toolkit: u32@4 == 38
        is_lmf = len(blob) >= 8 and struct.unpack_from("<I", blob, 4)[0] == 38
        entries.append({**rec, "offset": cursor, "sha1": sha1(blob), "is_lmf": is_lmf, "blob": blob})
        cursor += rec["size"]
    return {
        "path": str(path),
        "file_size": len(data),
        "prefix_hex": data[:HEADER_PREFIX].hex(),
        "entries": entries,
    }


def write_entries(parsed: dict, out_dir: Path, stem: str) -> list[dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for e in parsed["entries"]:
        tag = "LMF" if e["is_lmf"] else "entry"
        name = f"{stem}.WSX_{tag}{e['index']}_h{e['hash_hex']}.bin"
        # Stable Classic names for the four known witnesses
        if e["is_lmf"]:
            # Prefer LEVELS_* style when multiple LMF-like; also write stem.LMF for largest LMF
            name = f"{stem}.LMF"
        else:
            name = f"{stem}.WSX_entry{e['index']}_h{e['hash_hex']}.bin"
        dest = out_dir / name
        # Avoid clobbering if two LMF heuristics fire: keep hash in name for non-primary
        if e["is_lmf"] and dest.exists() and sha1(dest.read_bytes()) != e["sha1"]:
            dest = out_dir / f"{stem}.LMF_h{e['hash_hex']}.bin"
        dest.write_bytes(e["blob"])
        manifest.append(
            {
                "file": dest.name,
                "hash_hex": e["hash_hex"],
                "size": e["size"],
                "offset": e["offset"],
                "sha1": e["sha1"],
                "is_lmf": e["is_lmf"],
                "record_index": e["index"],
            }
        )
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--game-dat", type=Path, required=True, help="Path to retail DAT/ directory")
    ap.add_argument("--out", type=Path, required=True, help="Output directory for peels")
    ap.add_argument(
        "--stems",
        nargs="*",
        default=["QWOD0", "SWOD4", "RVOL0", "CKEEP"],
        help="WSX stems to peel (case-insensitive search)",
    )
    ap.add_argument("--manifest", type=Path, help="Optional JSON manifest path")
    args = ap.parse_args()

    results = []
    for stem in args.stems:
        matches = (
            list(args.game_dat.glob(f"{stem}.WSX"))
            + list(args.game_dat.glob(f"{stem}.wsx"))
            + list(args.game_dat.glob(f"{stem.lower()}.wsx"))
            + list(args.game_dat.glob(f"{stem.lower()}.WSX"))
            + list(args.game_dat.glob(f"{stem.upper()}.WSX"))
        )
        # dedupe
        seen = set()
        paths = []
        for m in matches:
            rp = m.resolve()
            if rp not in seen:
                seen.add(rp)
                paths.append(m)
        if not paths:
            results.append({"stem": stem, "error": "WSX not found"})
            continue
        path = paths[0]
        parsed = parse_wsx(path)
        # strip blobs for manifest serialization
        thin = {
            "stem": stem,
            "source": str(path),
            "file_size": parsed["file_size"],
            "prefix_hex": parsed["prefix_hex"],
            "written": write_entries(parsed, args.out, stem),
        }
        results.append(thin)
        print(f"OK {stem} <- {path.name}: {len(thin['written'])} blobs")

    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(results, indent=2) + "\n")
        print(f"manifest -> {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
