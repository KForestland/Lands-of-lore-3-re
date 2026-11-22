#!/usr/bin/env python3
"""Read the LoL3 executable's names and match them to WSX keys.

The music stems are the 40 pointers at file 0x148180. Every other
name below is a NUL-terminated printable string already stored in
LOL3.DAT, LOL3.EXE or an archive. Nothing is written.

  lol3_name_hash.py --data DAT --check
  lol3_name_hash.py --data DAT --list     # 40 music stems and their directory keys
"""
from cli_errors import run_cli, game_path
import mmap
import re
from hashlib import sha256
from pathlib import Path
from struct import pack, unpack, unpack_from

import lol3_cli
from extract_wsx_entries import wsx_name_hash
from lol3_level_report import DATA_BIAS, c_strings
from lol3_media_check import form, read_at
from lol3_script_framing import CODE_BIAS, RETAIL_PE

TARGET = 0x1D4F73DA
STEMS_AT = 0x148180
UHFROZE2_AT = 0x148330
UHFROZEN_AT = 0x148348
FORMAT_AT = 0x1483C4
# mov eax, dword ptr [0x549980] at VA 0x44A290.
STEM_LOAD = bytes.fromhex("A180995400")
STRING = re.compile(rb"[\x20-\x7e]{4,180}(?=\x00)")
UTF16_NEEDLE = "uhfroze1".encode("utf-16le")


def kind(text):
    if "\\" in text or "/" in text:
        return "path"
    if re.search(r"\.[A-Za-z0-9]{1,4}$", text):
        return "dotted"
    return "bare"


def directory(path):
    with path.open("rb") as handle:
        count, data_size = unpack("<HI", handle.read(6))
        raw = handle.read(12 * count)
        handle.seek(0, 2)
        size = handle.tell()
    base = 6 + 12 * count
    rows = []
    for index in range(count):
        key, offset, length = unpack_from("<III", raw, 12 * index)
        rows.append((key, 6 + 12 * index, base + offset, length))
    return base + data_size == size, rows


def find_all(blob, needle):
    found = []
    start = 0
    while True:
        at = blob.find(needle, start)
        if at < 0:
            return found
        found.append(at)
        start = at + 1


def strings_in(blob):
    return [(match.start(), match.group().decode("ascii")) for match in STRING.finditer(blob)]


def check_music_lookup(image):
    table = find_all(image, pack("<I", 0x629070))
    if table != [va - CODE_BIAS for va in (0x44A2A2, 0x44A778, 0x44A7E0)]:
        raise ValueError("music stem references changed")
    default_at = 0x44A775 - CODE_BIAS
    override_at = 0x44A7DD - CODE_BIAS
    if image[default_at:default_at + 15] != bytes.fromhex("8b0485709062005068c49b540053e8"):
        raise ValueError("default music formatter changed")
    if image[override_at:override_at + 29] != bytes.fromhex(
        "8b148d70906200525068b09b540053e84fe60c0083c41053e886b0feff"
    ):
        raise ValueError("score override or music lookup changed")
    if image[0x1483B0:0x1483BA] != b"%s\\%s.wav\0":
        raise ValueError("score override template changed")
    if image[0x1483BC:0x1483C3] != b"-SCORE\0":
        raise ValueError("score override switch changed")


def stem_lines(stems):
    """Stored stem and the MUSIC\\\\stem.aud key. No archive bytes."""
    lines = [f"stems {len(stems)}"]
    for index, stem in enumerate(stems):
        key = wsx_name_hash("MUSIC\\%s.aud" % stem)
        lines.append(f"stem {index}: {stem} key {key:#010x}")
    return "\n".join(lines) + "\n"


def main():
    parser = lol3_cli.tool_args(__doc__, writes=False)
    parser.add_argument("--list", action="store_true", help="print the 40 music stems and their keys")
    args = parser.parse_args()
    if args.list:
        if args.check:
            parser.error("--check does not list")
        try:
            image = game_path(Path(args.data).resolve().parent, "LOL3.DAT").read_bytes()
            if sha256(image).hexdigest() != RETAIL_PE:
                raise ValueError("LOL3.DAT does not match the executable from the English GOG release (1.07a)")
            if image[FORMAT_AT:FORMAT_AT + 12] != b"MUSIC\\%s.aud":
                raise ValueError("music format string changed")
            print(stem_lines(c_strings(image, STEMS_AT, 40)), end="")
        except (OSError, ValueError) as exc:
            parser.exit(1, f"name hash: {exc}\n")
        return 0
    if not args.check:
        parser.error("this tool only checks; pass --check")
    data = Path(args.data)
    try:
        image = game_path(data.resolve().parent, "LOL3.DAT").read_bytes()
        exe = game_path(data.resolve().parent, "LOL3.EXE").read_bytes()
        if sha256(image).hexdigest() != RETAIL_PE:
            raise ValueError("LOL3.DAT does not match the executable from the English GOG release (1.07a)")
        if len(exe) != 77824:
            raise ValueError(f"LOL3.EXE is {len(exe)} bytes")
        if image[0x44A290 - CODE_BIAS:0x44A290 - CODE_BIAS + 5] != STEM_LOAD:
            raise ValueError("stem load at 0x44A290 is not the pointer table")
        if image[FORMAT_AT:FORMAT_AT + 12] != b"MUSIC\\%s.aud":
            raise ValueError("music format string changed")
        check_music_lookup(image)
        stems = c_strings(image, STEMS_AT, 40)
        if stems[9] != "uhfrozen" or stems[11] != "uhfroze2":
            raise ValueError(f"slots 9 and 11 are {stems[9]!r} and {stems[11]!r}")
        if image[UHFROZEN_AT:UHFROZEN_AT + 8] != b"uhfrozen" or image[UHFROZE2_AT:UHFROZE2_AT + 8] != b"uhfroze2":
            raise ValueError("frozen stem bytes moved")
        pointers = unpack_from("<40I", image, STEMS_AT)
        if pointers[9] - DATA_BIAS != UHFROZEN_AT or pointers[11] - DATA_BIAS != UHFROZE2_AT:
            raise ValueError("stem pointers do not land on the stored spellings")

        files = [path for path in lol3_cli.wsx_files(data) if path.name.lower() != "cdcache.wsx"]
        keys = set()
        music = {}
        missing_row = None
        entries = 0
        for path in files:
            ok, rows = directory(path)
            if not ok:
                raise ValueError(f"{path.name} failed the size check")
            entries += len(rows)
            music_file = path.name.upper().startswith("MUSIC")
            for key, row_at, payload_at, length in rows:
                keys.add(key)
                if music_file:
                    music.setdefault(key, []).append((path.name.lower(), row_at, payload_at, length))
                if key == wsx_name_hash("missing.aud") and path.name.upper() == "LOCAL.WSX":
                    missing_row = (row_at, payload_at, length, path)
        if entries != 7549 or len(keys) != 7417:
            raise ValueError(f"directory is {entries} entries and {len(keys)} keys")
        if missing_row != (0x11A, 0x240FF66, 1160, missing_row[3]):
            raise ValueError(f"missing.aud row is {missing_row}")
        with missing_row[3].open("rb") as handle:
            handle.seek(0x240FF66)
            if handle.read(16) != b"RIFF\x80\x04\x00\x00WAVEfmt ":
                raise ValueError("missing.aud payload is not the 1,160-byte WAVE")

        if (wsx_name_hash("MUSIC\\uhfroze2.aud") != 0x1D4F74DA
                or wsx_name_hash("MUSIC\\uhfrozen.aud") != 0x1D4F90DA
                or wsx_name_hash("MUSIC\\uhfroze1.aud") != TARGET):
            raise ValueError("music candidate hash changed")
        stem_hashes = {wsx_name_hash("MUSIC\\%s.aud" % stem) for stem in stems}
        joined = {wsx_name_hash("MUSIC\\%s.aud" % stem)
                  for stem in stems if stem.isalnum() and stem not in ("None", "uhfroze2")}
        extra = sorted(key for key in music if key not in stem_hashes)
        absent = [name for name in ("None", "uhfroze2", "-------", "--------")
                  if wsx_name_hash("MUSIC\\%s.aud" % name) in music]
        covered = sum(len(rows) for key, rows in music.items() if key in joined)
        target_rows = music.get(TARGET, [])
        if (len(music) != 32 or extra != [TARGET] or absent or len(joined) != 31
                or covered != 37 or sum(len(rows) for rows in music.values()) != 38
                or target_rows != [("music4.wsx", 0x8A, 0x11FD49A, 6530290)]):
            raise ValueError(
                f"music join keys {len(music)} extra {extra} absent {absent} "
                f"joined {len(joined)} covered {covered} target {target_rows}")
        filename, _, start, length = target_rows[0]
        with game_path(data, filename).open("rb") as stream:
            chunks = list(form(stream, start, length, b"RIFF", b"WAVE", "<"))
            expected_chunks = [
                (b"fmt ", start + 0x14, 30), (b"fact", start + 0x3A, 4),
                (b"data", start + 0x46, length - 0x46),
            ]
            if (chunks != expected_chunks or read_at(stream, start + 0x46, 3) == b"ID3"
                    or read_at(stream, start + length - 128, 3) == b"TAG"):
                raise ValueError("unmatched track unexpectedly carries RIFF or ID3 metadata")

        if find_all(image, b"uhfroze") != [UHFROZE2_AT, UHFROZEN_AT] or find_all(image, b"uhfroze1"):
            raise ValueError("uhfroze spellings in LOL3.DAT changed")
        if any(find_all(exe, needle) for needle in (b"uhfroze", b"UHFROZE", UTF16_NEEDLE)):
            raise ValueError("LOL3.EXE contains a froze spelling")

        dat_strings = strings_in(image)
        exe_strings = strings_in(exe)
        if (len(dat_strings), len(exe_strings)) != (2374, 222):
            raise ValueError(f"program strings {len(dat_strings)} and {len(exe_strings)}")

        def matching(origin, pairs):
            found = []
            for at, text in pairs:
                key = wsx_name_hash(text)
                if key in keys:
                    found.append((origin, at, key, text, kind(text)))
            return found

        hits = matching("LOL3.DAT", dat_strings) + matching("LOL3.EXE", exe_strings)
        archive_strings = 0
        froze = []
        for path in files:
            with path.open("rb") as handle:
                mapping = mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ)
                pairs = strings_in(mapping)
                archive_strings += len(pairs)
                for needle in (b"uhfroze", b"UHFROZE", UTF16_NEEDLE):
                    if mapping.find(needle) >= 0:
                        froze.append((path.name, needle))
                hits.extend(matching(path.name.upper(), pairs))
                mapping.close()
        shipped = game_path(data, "cdcache.wsx")
        if shipped.is_file():
            blob = shipped.read_bytes()
            for needle in (b"uhfroze", b"UHFROZE", UTF16_NEEDLE):
                if blob.find(needle) >= 0:
                    froze.append((shipped.name, needle))
        if froze:
            raise ValueError(f"froze bytes in archives {froze}")
        if archive_strings != 3701411:
            raise ValueError(f"archive strings {archive_strings}")

        path_hits = [hit for hit in hits if hit[4] != "bare"]
        bare = [(hit[0], hit[1]) for hit in hits if hit[4] == "bare"]
        dat_keys = {hit[2] for hit in path_hits if hit[0] == "LOL3.DAT"}
        exe_keys = {hit[2] for hit in path_hits if hit[0] == "LOL3.EXE"}
        all_keys = {hit[2] for hit in path_hits}
        target_hits = [hit for hit in hits if hit[2] == TARGET]
        missing_at = find_all(game_path(data, "locallng.wsx").read_bytes(), b"missing.aud\x00")
        if (len(dat_keys) != 52 or exe_keys - dat_keys or all_keys - dat_keys != {0x2E02FD5E}
                or bare != [("LOCAL.WSX", 0x147CF1F)] or target_hits
                or missing_at != [0x58C6636, 0x58C6646]):
            raise ValueError(
                f"names dat {len(dat_keys)} exe extra {exe_keys - dat_keys} "
                f"added {all_keys - dat_keys} bare {bare} target {len(target_hits)} "
                f"missing {missing_at}")
    except (OSError, ValueError) as exc:
        print(f"CHECK name_hash FAILED: {exc}")
        return 1
    print("CHECK name_hash: 40 stems; 31 keys join 37 of 38 music entries; "
          "neither the default stems nor stored strings name 0x1D4F73DA; "
          "the payload has no name chunk; 53 path-like names join directory keys")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
