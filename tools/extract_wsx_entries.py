#!/usr/bin/env python3
"""Read original LoL3 WSX archives and list or export entries.

WSX layout (docs/formats/wsx.md; the same as Westwood MIX):
  - u16 count, u32 data size (bytes after the index)
  - count x 12-byte rows: u32 key, u32 offset from the start of the data, u32 size
  - the entries; rows are sorted by signed key

Works for witness families (count=4) and most DAT/*.WSX including *S sidecars,
GLOBAL, movies, music, and slice CDs. cdcache.wsx is a known exception.
"""
from __future__ import annotations

from cli_errors import ReaderArgumentParser, output_refusal, run_cli
import argparse
import hashlib
import json
import struct
from pathlib import Path

HEADER_PREFIX = 6
RECORD_SIZE = 12


def sha1(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def wsx_name_hash(name: str) -> int:
    """Hash an ASCII resource name as the retail WSX lookup does."""
    value = 0
    for char in name.encode("ascii").upper():
        rotated = ((value >> 6) | (value << 26)) & 0xFFFFFFFF
        value = (rotated + ((char - 0x30) & 0x3F)) & 0xFFFFFFFF
    return value


def parse_wsx(path: Path) -> dict:
    return parse_wsx_bytes(path.read_bytes(), path)


def parse_wsx_bytes(data: bytes, path="<memory>") -> dict:
    """Parse WSX bytes already in memory; `path` only names them in errors."""
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
    data_size = struct.unpack_from("<I", data, 2)[0]
    if payload_base + data_size != len(data):
        raise ValueError(f"{path}: data size field {data_size} does not match the file ({len(data) - payload_base})")
    entries = []
    for rec in sorted(records, key=lambda r: r["unk"]):
        # The second u32 of a row is the entry's offset from the start of the data (docs/formats/wsx.md).
        start = payload_base + rec["unk"]
        blob = data[start : start + rec["size"]]
        if len(blob) != rec["size"]:
            raise ValueError(f"{path}: entry {rec['hash_hex']} runs past the end of the file")
        is_lmf = len(blob) >= 0x100 and struct.unpack_from("<3I", blob) == (0, 38, 0x100)
        entries.append({**rec, "offset": start, "sha1": sha1(blob), "is_lmf": is_lmf, "blob": blob})
    spans = [(e["offset"], e["offset"] + e["size"]) for e in entries]
    if any(a[1] > b[0] for a, b in zip(spans, spans[1:])):
        raise ValueError(f"{path}: overlapping entries")
    return {
        "path": str(path),
        "file_size": len(data),
        "count": count,
        "prefix_hex": data[:HEADER_PREFIX].hex(),
        "payload_base": payload_base,
        "entries": entries,
    }


def directory_lines(parsed):
    """Key, file offset and size for each entry. No entry bytes."""
    lines = [f"count {parsed['count']} data_base {parsed['payload_base']:#x}"]
    for entry in parsed["entries"]:
        lines.append(f"key {entry['hash']:#010x} offset {entry['offset']:#x} size {entry['size']}")
    return "\n".join(lines) + "\n"


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


# The one DAT file whose header does not match its size (docs/OPEN_QUESTIONS.md).
KNOWN_OPEN = {"CDCACHE.WSX"}

USAGE = """
  extract_wsx_entries.py --data DAT --out DIR [--stems CKEEP ...]   # write entry blobs and a manifest
  extract_wsx_entries.py --data DAT --list [--stems QWOD0]          # print key, offset and size; write nothing
  extract_wsx_entries.py --data DAT --check                         # parse every WSX, write nothing
"""


def check(data_dir: Path) -> int:
    import lol3_cli
    files = lol3_cli.wsx_files(data_dir)
    ok = lmf = entries = matched_names = 0
    failed = []
    global_names = {
        "GLOBAL.WSX": ("GLOBAL\\GLOBAL.ODF", "GLOBAL\\SPELL.ODF"),
        "LOCAL.WSX": ("GLOBAL\\GLOBAL.TEX", "GLOBAL\\SPELL.TEX"),
    }
    for f in files:
        try:
            p = parse_wsx(f)
        except ValueError as exc:
            failed.append((f.name, str(exc).split(": ", 1)[-1]))
            continue
        ok += 1
        entries += len(p["entries"])
        level_maps = [entry for entry in p["entries"] if entry["is_lmf"]]
        lmf += len(level_maps)
        keys = {entry["hash"] for entry in p["entries"]}
        names = global_names.get(f.name.upper(), ())
        if level_maps:
            stem = f.stem.upper()
            prefix = f"LEVELS\\{stem}\\{stem}."
            names = tuple(prefix + ext for ext in ("LMF", "MAP", "ODF", "TE_"))
            if wsx_name_hash(names[0]) not in {entry["hash"] for entry in level_maps}:
                failed.append((f.name, "LMF key does not identify a Light Map entry"))
        for name in names:
            if wsx_name_hash(name) in keys:
                matched_names += 1
            else:
                failed.append((f.name, f"missing key for {name}"))
    unexpected = [n for n, _ in failed if n.upper() not in KNOWN_OPEN]
    print(f"CHECK wsx: {ok}/{len(files)} WSX files parse (count, 12-byte records, payload sizes sum to the file); "
          f"{entries} entries, {lmf} Light Maps; {matched_names}/76 native resource names match; failing: "
          f"{'; '.join(f'{n} ({m})' for n, m in failed) or 'none'}; unexpected failures: {unexpected or 'none'}")
    return int(bool(unexpected) or matched_names != 76)


def main() -> int:
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    ap = ReaderArgumentParser(description=(__doc__ or "") + USAGE, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", "--game-dat", dest="game_dat", type=Path, default=os.environ.get("LOL3_DAT"),
                    help="the game's DAT folder (default: $LOL3_DAT)")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--check", action="store_true", help="parse every WSX of --data, print one CHECK line, write nothing")
    ap.add_argument("--list", action="store_true", help="print key, file offset and size; write nothing")
    ap.add_argument("--stems", nargs="*", default=None, help="If omitted, peel every *.WSX in DAT")
    ap.add_argument("--manifest", type=Path)
    ap.add_argument(
        "--max-blob-write",
        type=int,
        default=None,
        help="Skip writing blobs larger than this many bytes (still listed in manifest)",
    )
    args = ap.parse_args()
    if args.game_dat is None:
        ap.error("give --data (the game's DAT folder) or set LOL3_DAT")
    if args.check:
        if args.list:
            ap.error("--check does not list")
        return check(args.game_dat)
    import lol3_cli
    files = lol3_cli.wsx_files(args.game_dat)
    if args.list:
        if args.out is not None or args.manifest is not None:
            ap.error("--list writes nothing")
        if args.stems:
            wanted = {stem.upper() for stem in args.stems}
            files = [path for path in files if path.stem.upper() in wanted]
            if not files:
                ap.error("no archive matches --stems")
        for path in files:
            try:
                listing = directory_lines(parse_wsx(path))
                print(path.name)
                print(listing, end="")
            except ValueError as exc:
                if args.stems or path.name.upper() not in KNOWN_OPEN:
                    raise ValueError(f"{path.name}: {exc}") from exc
                print(f"FAIL {path.name}")
        return 0
    if args.out is None:
        ap.error("--out is required unless --check or --list is given")
    # The entries are original game bytes: they never land in the game folders or this repository.
    refusal = output_refusal(args.out, args.game_dat, repository=True)
    if refusal:
        ap.error(refusal)

    results = []
    if args.stems:
        from cli_errors import game_path

        entries = [(stem, game_path(args.game_dat, stem + ".WSX")) for stem in args.stems]
    else:
        entries = [(path.stem, path) for path in files]
    for stem, path in entries:
        if not path.is_file():
            results.append({"stem": stem, "error": "WSX not found"})
            continue
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
    raise SystemExit(run_cli(main))
