#!/usr/bin/env python3
"""Peel LoL3 .WSX containers into entry blobs + LMF candidates.

WSX layout (verified 2026-09-17):
  - u16 count at offset 0 (little-endian)
  - 6-byte prefix total (count + 4 bytes)
  - count × 12-byte records: <u32 hash><u32 unk><u32 size>
  - concatenated payloads in size-descending order
  - sum(sizes) == file_size - payload_base

Works for witness families (count=4) and most DAT/*.WSX including *S sidecars,
GLOBAL, movies, music, and slice CDs. cdcache.wsx is a known exception.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

HEADER_PREFIX = 6
RECORD_SIZE = 12


def sha1(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def parse_wsx(path: Path) -> dict:
    data = path.read_bytes()
    if len(data) < HEADER_PREFIX + RECORD_SIZE:
        raise ValueError(f"{path}: too small for WSX header")
    count = struct.unpack_from("<H", data, 0)[0]
    if not (1 <= count <= 100000):
        raise ValueError(f"{path}: implausible count {count}")
    payload_base = HEADER_PREFIX + count * RECORD_SIZE
    if payload_base > len(data):
        raise ValueError(f"{path}: record table past EOF")
    records = []
    for i in range(count):
        off = HEADER_PREFIX + i * RECORD_SIZE
        h, unk, size = struct.unpack_from("<III", data, off)
        records.append({"index": i, "hash": h, "hash_hex": f"{h:08X}", "unk": unk, "size": size})
    total = sum(r["size"] for r in records)
    if payload_base + total != len(data):
        raise ValueError(
            f"{path}: size mismatch header_sum={payload_base + total} file={len(data)} count={count}"
        )
    ordered = sorted(records, key=lambda r: r["size"], reverse=True)
    cursor = payload_base
    entries = []
    for rec in ordered:
        blob = data[cursor : cursor + rec["size"]]
        if len(blob) != rec["size"]:
            raise ValueError(f"{path}: truncated entry {rec['hash_hex']}")
        is_lmf = len(blob) >= 8 and struct.unpack_from("<I", blob, 4)[0] == 38
        entries.append({**rec, "offset": cursor, "sha1": sha1(blob), "is_lmf": is_lmf, "blob": blob})
        cursor += rec["size"]
    return {
        "path": str(path),
        "file_size": len(data),
        "count": count,
        "prefix_hex": data[:HEADER_PREFIX].hex(),
        "payload_base": payload_base,
        "entries": entries,
    }


def write_entries(parsed: dict, out_dir: Path, stem: str, max_blob_write: int | None) -> list[dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    lmf_written = False
    for e in parsed["entries"]:
        if e["is_lmf"] and not lmf_written:
            name = f"{stem}.LMF"
            lmf_written = True
        elif e["is_lmf"]:
            name = f"{stem}.LMF_h{e['hash_hex']}.bin"
        else:
            name = f"{stem}.WSX_entry{e['index']}_h{e['hash_hex']}.bin"
        dest = out_dir / name
        meta = {
            "file": name,
            "hash_hex": e["hash_hex"],
            "size": e["size"],
            "offset": e["offset"],
            "sha1": e["sha1"],
            "is_lmf": e["is_lmf"],
            "record_index": e["index"],
            "written": False,
        }
        if max_blob_write is not None and e["size"] > max_blob_write:
            meta["skipped_write"] = True
            meta["reason"] = f"size>{max_blob_write}"
        else:
            dest.write_bytes(e["blob"])
            meta["written"] = True
        manifest.append(meta)
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--game-dat", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--stems", nargs="*", default=None, help="If omitted, peel every *.WSX in DAT")
    ap.add_argument("--manifest", type=Path)
    ap.add_argument(
        "--max-blob-write",
        type=int,
        default=None,
        help="Skip writing blobs larger than this many bytes (still listed in manifest)",
    )
    args = ap.parse_args()

    if args.stems:
        stems = args.stems
    else:
        stems = sorted(
            {p.stem for p in list(args.game_dat.glob("*.WSX")) + list(args.game_dat.glob("*.wsx"))},
            key=str.upper,
        )

    results = []
    for stem in stems:
        matches = []
        seen = set()
        for pat in (f"{stem}.WSX", f"{stem}.wsx", f"{stem.lower()}.wsx", f"{stem.lower()}.WSX", f"{stem.upper()}.WSX"):
            for m in args.game_dat.glob(pat):
                rp = m.resolve()
                if rp not in seen:
                    seen.add(rp)
                    matches.append(m)
        # also case-insensitive stem match
        if not matches:
            for m in list(args.game_dat.glob("*.WSX")) + list(args.game_dat.glob("*.wsx")):
                if m.stem.upper() == stem.upper():
                    rp = m.resolve()
                    if rp not in seen:
                        seen.add(rp)
                        matches.append(m)
        if not matches:
            results.append({"stem": stem, "error": "WSX not found"})
            continue
        path = matches[0]
        try:
            parsed = parse_wsx(path)
        except ValueError as exc:
            results.append({"stem": stem, "source": str(path), "error": str(exc)})
            print(f"FAIL {stem}: {exc}")
            continue
        thin = {
            "stem": stem,
            "source": str(path),
            "file_size": parsed["file_size"],
            "count": parsed["count"],
            "prefix_hex": parsed["prefix_hex"],
            "payload_base": parsed["payload_base"],
            "written": write_entries(parsed, args.out / stem.upper(), stem.upper(), args.max_blob_write),
        }
        # drop blobs from memory via thin only
        results.append(thin)
        n = len(thin["written"])
        n_w = sum(1 for x in thin["written"] if x.get("written"))
        print(f"OK {stem} <- {path.name}: count={parsed['count']} entries={n} written={n_w}")

    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(results, indent=2) + "\n")
        print(f"manifest -> {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
