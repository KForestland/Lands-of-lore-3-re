#!/usr/bin/env python3
"""Check original LoL3 movie names, VQA chunk framing and WAVE audio in place."""
from cli_errors import ReaderArgumentParser, run_cli
from collections import Counter
import hashlib
import argparse
import os
from pathlib import Path
import struct
import sys

from extract_wsx_entries import wsx_name_hash
from lol3_script_framing import RETAIL_PE

MOVIE_TABLE = 0x148BD0
MOVIE_NAME_FMT = 0x148D28
MOVIE_PATH_FMT = 0x148D60
DATA_VA_BIAS = 0x401800


def cstring(image, at):
    return image[at:image.index(b"\0", at)].decode("ascii")


def movie_names(image):
    if hashlib.sha256(image).hexdigest() != RETAIL_PE:
        raise ValueError("LOL3.DAT differs from the documented English retail executable")
    name_format = cstring(image, MOVIE_NAME_FMT)
    path_format = cstring(image, MOVIE_PATH_FMT)
    names = {}
    for i in range(20):
        pointer, = struct.unpack_from("<I", image, MOVIE_TABLE + 4 * i)
        stem = cstring(image, pointer - DATA_VA_BIAS)
        if stem == "-----":
            break
        name = path_format % (name_format % stem)
        names[wsx_name_hash(name)] = name
    if len(names) != 19:
        raise ValueError("expected 19 named movie keys")
    return names


def read_at(stream, offset, size):
    stream.seek(offset)
    return stream.read(size)


def wsx_rows(stream):
    count, data_size = struct.unpack("<HI", stream.read(6))
    base = 6 + 12 * count
    stream.seek(0, 2)
    end = stream.tell()
    if base + data_size != end:
        raise ValueError("WSX declared size disagrees with file size")
    directory = read_at(stream, 6, 12 * count)
    next_pos = 0
    rows = []
    for key, offset, size in struct.iter_unpack("<III", directory):
        if offset + size > data_size:
            raise ValueError("WSX entry is out of range")
        rows.append((key, base + offset, size))
    for _, start, size in sorted(rows, key=lambda row: row[1]):
        if start != base + next_pos:
            raise ValueError("gap or overlap in WSX payload")
        next_pos += size
    if next_pos != data_size:
        raise ValueError("WSX directory does not cover the payload")
    return rows


def chunks(stream, start, end, order):
    while start + 8 <= end:
        tag, size = struct.unpack(order + "4sI", read_at(stream, start, 8))
        body = start + 8
        upper = body + size + (size & 1)
        if upper > end or not all(0x20 <= char < 0x7F for char in tag):
            raise ValueError(f"invalid chunk at 0x{start:X}")
        yield tag, body, size
        start = upper
    if start != end:
        raise ValueError(f"incomplete chunk at 0x{start:X}")


def form(stream, start, size, tag, codec, order):
    magic, length, kind = struct.unpack(order + "4sI4s", read_at(stream, start, 12))
    if (magic, kind, length + 8) != (tag, codec, size):
        raise ValueError(f"wrong container type or size at 0x{start:X}")
    return chunks(stream, start + 12, start + size, order)


def read_movie_table(stream, start, size, header_tag, data_tag, header_size, record_format):
    rows = list(chunks(stream, start, start + size, ">"))
    if len(rows) != 2 or (rows[0][0], rows[1][0]) != (header_tag, data_tag):
        raise ValueError(f"unexpected {header_tag!r} table layout at 0x{start:X}")
    _, header_at, header_length = rows[0]
    _, data_at, data_length = rows[1]
    if header_length != header_size:
        raise ValueError(f"unexpected {header_tag!r} header size at 0x{header_at:X}")
    count, = struct.unpack("<H", read_at(stream, header_at, 2))
    if data_length != count * struct.calcsize(record_format):
        raise ValueError(f"{data_tag!r} length disagrees with row count at 0x{data_at:X}")
    return list(struct.iter_unpack(record_format, read_at(stream, data_at, data_length)))


def check_movie(stream, start, size):
    header = None
    index = []
    counts = Counter()
    samples = Counter()
    seek_targets = {}
    seek_counts = Counter()
    loop_rows = codebook_rows = None
    codebooks = {}
    frame_index = 0
    for tag, at, length in form(stream, start, size, b"FORM", b"WVQA", ">"):
        counts[tag] += 1
        if tag == b"VQHD":
            header = read_at(stream, at, length)
        elif tag == b"FINF":
            index = [word for word, in struct.iter_unpack("<I", read_at(stream, at, length))]
        elif tag == b"SN2J":
            if length != 12:
                raise ValueError(f"SN2J must contain two state records at 0x{at:X}")
            seek_targets[at - 8 - start] = tag
        elif tag == b"SND2":
            samples[length] += 1
        elif tag == b"LINF":
            loop_rows = read_movie_table(stream, at, length, b"LINH", b"LIND", 6, "<HH")
        elif tag == b"CINF":
            codebook_rows = read_movie_table(stream, at, length, b"CINH", b"CIND", 8, "<HI")
        elif tag in (b"VQFR", b"VQFL"):
            offset = at - 8 - start
            payloads = Counter()
            for subtype, body, payload_length in chunks(stream, at, at + length, ">"):
                payloads[subtype] += 1
                if subtype == b"CBFZ":
                    if frame_index in codebooks:
                        raise ValueError(f"duplicate codebook at 0x{body:X}")
                    codebooks[frame_index] = (payload_length, offset)
            if tag == b"VQFL":
                if payloads != {b"CBFZ": 1}:
                    raise ValueError(f"unexpected VQFL payload at 0x{at:X}")
                seek_targets[offset] = tag
            else:
                if (payloads.keys() - {b"CBFZ", b"VPTR", b"VPRZ"}
                        or payloads[b"VPTR"] + payloads[b"VPRZ"] != 1):
                    raise ValueError(f"unexpected VQFR payload at 0x{at:X}")
                frame_index += 1
    if header is None or len(header) != 42 or counts[b"VQHD"] != 1 or counts[b"FINF"] != 1:
        raise ValueError("expected one 42-byte VQHD and one FINF")
    version, flags, frames, width, height = struct.unpack_from("<5H", header)
    if (version, flags, width, height, header[10:13], header[24:28]) != (
            3, 0x1D, 640, 480, b"\x04\x04\x0f", b"\x22\x56\x02\x10"):
        raise ValueError(f"inconsistent VQHD at 0x{start + 20:X}")
    if len(index) != frames or counts[b"VQFR"] != frames:
        raise ValueError("FINF or VQFR count disagrees with VQHD")
    offsets = [(word & 0x0FFFFFFF) * 2 for word in index]
    for word, offset in zip(index, offsets):
        if offset not in seek_targets:
            raise ValueError(f"FINF target 0x{word:X} has no SN2J or VQFL header")
        seek_counts[seek_targets[offset]] += 1
    if (counts[b"LINF"] != 1 or counts[b"CINF"] != 1
            or not loop_rows or not codebook_rows or len(loop_rows) != len(codebook_rows)):
        raise ValueError("expected one matching pair of LINF and CINF tables")
    if set(codebooks) != {first for first, _ in codebook_rows}:
        raise ValueError("CIND frame markers disagree with the codebook chunks")
    for (first, last), (frame, length) in zip(loop_rows, codebook_rows):
        stored_length, offset = codebooks[frame]
        if not (first == frame <= last < frames and length == stored_length
                and (frame == 0 or offset == offsets[frame])):
            raise ValueError(f"loop/codebook table mismatch at frame {frame}")
    return frames, counts, samples, seek_counts


def first_mp3_frames(stream, start, size):
    """Check the first 2 MPEG-1 Layer III frames, including their spacing."""
    at = start
    for _ in range(2):
        if at + 4 > start + size:
            raise ValueError("short MPEG stream")
        head, = struct.unpack(">I", read_at(stream, at, 4))
        if head & 0xFFFEFC00 != 0xFFFA9000:
            raise ValueError(f"expected MPEG-1 Layer III, 128 kb/s, 44,100 Hz at 0x{at:X}")
        at += 144 * 128000 // 44100 + ((head >> 9) & 1)
    if at > start + size:
        raise ValueError("MPEG frame exceeds its data chunk")


def check_wave(stream, start, size, music):
    fmt = None
    data = None
    for tag, at, length in form(stream, start, size, b"RIFF", b"WAVE", "<"):
        if tag == b"fmt ":
            fmt = read_at(stream, at, length)
        if tag == b"data":
            data = (at, length)
    if fmt is None or len(fmt) < 16 or data is None:
        raise ValueError("missing WAVE format or data chunk")
    tag, channels, rate, byterate, align, bits = struct.unpack_from("<HHIIHH", fmt)
    if music:
        if (tag, channels, rate, byterate, align, bits, len(fmt)) != (0x55, 2, 44100, 16000, 1, 0, 30):
            raise ValueError("unexpected WAVE fields in music entry")
        first_mp3_frames(stream, *data)
    else:
        if tag != 0x11 or channels not in (1, 2) or rate != 22050 or bits != 4 or len(fmt) != 20:
            raise ValueError("unexpected WAVE fields in level sidecar")
        extension, samples = struct.unpack_from("<HH", fmt, 16)
        if extension != 2 or samples != 1 + (align - 4 * channels) * 2 // channels:
            raise ValueError("IMA sample count disagrees with the block alignment")
    return channels, align, byterate


def keys(path):
    """Collect header keys to identify level archives in the DAT folder."""
    with path.open("rb") as stream:
        head = stream.read(6)
        if len(head) != 6:
            return set()
        count, size = struct.unpack("<HI", head)
        if size + 6 + 12 * count != path.stat().st_size:
            return set()
        return {key for key, _, _ in struct.iter_unpack("<III", stream.read(12 * count))}


TRR_AT = {
    "qevent.trr": 0x5987786,
    "qtext.trr": 0x5987AF5,
    "devent.trr": 0x58E4F95,
    "dtext.trr": 0x58F7444,
}
STEMS_AT = 0x148180


def movie_chunk_lines(stream, start, size):
    """Top-level chunk tag, header offset and size. Frame pixels are not read out."""
    lines = []
    for tag, at, length in form(stream, start, size, b"FORM", b"WVQA", ">"):
        lines.append(f"{tag.decode('ascii')} +{at - 8:#x} size {length}")
    return lines


def wave_fields(stream, start, size):
    fmt = None
    for tag, at, length in form(stream, start, size, b"RIFF", b"WAVE", "<"):
        if tag == b"fmt ":
            fmt = read_at(stream, at, length)
    if fmt is None or len(fmt) < 16:
        raise ValueError("missing WAVE format chunk")
    return struct.unpack_from("<HHIIHH", fmt)


def trr_directory(blob, name):
    """Read ids and relative boundaries and verify that they fit the entry."""
    count, = struct.unpack_from("<I", blob)
    bound_at = 4 + 4 * count
    directory = bound_at + 4 * (count + 1)
    if count > 100000 or directory > len(blob):
        raise ValueError(f"{name} directory exceeds the entry")
    ids = struct.unpack_from(f"<{count}I", blob, 4) if count else ()
    bounds = struct.unpack_from(f"<{count + 1}I", blob, bound_at)
    if bounds[0] != directory - 4 or bounds[-1] != len(blob) - 4:
        raise ValueError(f"{name} boundaries disagree with the directory or entry size")
    if any(start > end for start, end in zip(bounds, bounds[1:])):
        raise ValueError(f"{name} has out-of-order boundaries")
    return ids, bounds


def trr_lines(blob, name):
    """Count, ids and stored boundaries. Payload bytes are not printed."""
    ids, bounds = trr_directory(blob, name)
    lines = [f"{name} count {len(ids)} directory {8 + 8 * len(ids)} bytes"]
    for ident, boundary in zip(ids, bounds):
        lines.append(f"id {ident} boundary {boundary:#x}")
    lines.append(f"end boundary {bounds[-1]:#x}")
    return "\n".join(lines) + "\n"


def display_trr_text(field):
    """Label formatting bytes whose effect is outside this text view."""
    lines = field.decode("latin-1").replace("\r\n", "\n").replace("\r", "\n").replace("\t", "    ")
    return "".join(f"[control {ord(ch):#04x}]" if (ch < " " and ch != "\n") or "\x7f" <= ch <= "\x9f" else ch
                   for ch in lines).strip()


def localized_trr(data, names):
    path = next((path for path in data.iterdir() if path.name.lower() == "locallng.wsx"), None)
    if path is None:
        raise FileNotFoundError("LOCALLNG.WSX is missing from the DAT folder")
    tables = {}
    with path.open("rb") as stream:
        directory = {start: size for _, start, size in wsx_rows(stream)}
        for name in names:
            start = TRR_AT[name]
            if start not in directory:
                raise ValueError(f"{name} is not at the documented offset")
            tables[name] = read_at(stream, start, directory[start])
    return path, tables


def check(data, summary):
    names = movie_names((data.parent / "LOL3.DAT").read_bytes())
    files = {path.stem.upper(): path for path in data.iterdir() if path.suffix.upper() == ".WSX"}
    level_sounds = {
        stem + "S" for stem, path in files.items() if stem + "S" in files
        and wsx_name_hash(f"LEVELS\\{stem}\\{stem}.LMF") in keys(path)
    }
    found = set()
    movie_count = music_count = total_frames = 0
    chunks_seen = Counter()
    samples_seen = Counter()
    seek_counts = Counter()
    level_formats = Counter()
    for stem in sorted({f"{prefix}{index}" for prefix in ("MOVIES", "MUSIC") for index in range(1, 5)} | level_sounds):
        path = files[stem]
        with path.open("rb") as stream:
            for key, start, size in wsx_rows(stream):
                if stem.startswith("MOVIES"):
                    frames, chunks, samples, targets = check_movie(stream, start, size)
                    if key in found or key not in names:
                        raise ValueError(f"{path.name}+0x{start:X}: duplicate or unnamed movie key")
                    found.add(key)
                    movie_count += 1
                    total_frames += frames
                    chunks_seen.update(chunks)
                    samples_seen.update(samples)
                    seek_counts.update(targets)
                    if summary:
                        print(f"{path.name}+0x{start:X} {key:08X} {names[key]} {frames} frames")
                else:
                    music = stem.startswith("MUSIC")
                    result = check_wave(stream, start, size, music)
                    if music:
                        music_count += 1
                    else:
                        level_formats[result] += 1
    if found != names.keys() or music_count != 38 or sum(level_formats.values()) != 6696 or len(level_sounds) != 18:
        raise ValueError("archive counts disagree with the English retail corpus")
    if summary:
        print(f"Movie chunk counts {dict(chunks_seen)}, SND2 byte sizes {dict(samples_seen)}, FINF targets {dict(seek_counts)}")
        print(f"Level WAVE families (channels, block align, byte rate) {dict(level_formats)}")
    print(f"CHECK media: {movie_count} named VQA movies, {total_frames:,} indexed frames, "
          f"{music_count} MP3/WAVE tracks and {sum(level_formats.values()):,} IMA/WAVE sounds")
    return 0


def show_text(data, table, record_id):
    name = table.lower()
    if name not in TRR_AT:
        raise ValueError(f"trr name must be one of {', '.join(TRR_AT)}")
    _, tables = localized_trr(data, (name,))
    blob = tables[name]
    if record_id is None:
        print(trr_lines(blob, name), end="")
    else:
        ids, bounds = trr_directory(blob, name)
        if record_id not in ids:
            raise ValueError(f"Record ID {record_id} was not found. Omit --id to see available IDs.")
        for row, identifier in enumerate(ids):
            if identifier == record_id:
                field = blob[bounds[row]+4:bounds[row+1]+4]
                if not field.endswith(b"\0"):
                    raise ValueError(f"Record ID {record_id} is missing its terminator.")
                print(f"{name} ID {identifier}\n{display_trr_text(field[:-1])}")
    return 0


def music_tracks(data):
    image = (data.parent / "LOL3.DAT").read_bytes()
    from lol3_level_report import c_strings
    stems = c_strings(image, STEMS_AT, 40)
    by_key = {}
    for stem in stems:
        by_key.setdefault(wsx_name_hash("MUSIC\\%s.aud" % stem), []).append(stem)
    files = {path.stem.upper(): path for path in data.iterdir() if path.suffix.upper() == ".WSX"}
    for stem in sorted(path for path in files if path.startswith("MUSIC")):
        with files[stem].open("rb") as stream:
            for key, start, size in wsx_rows(stream):
                tag, channels, rate, _byterate, align, bits = wave_fields(stream, start, size)
                stored = ",".join(by_key.get(key, ())) or "absent"
                print(f"{files[stem].name}+0x{start:X} size {size} key {key:08X} "
                      f"tag {tag:#x} channels {channels} rate {rate} align {align} bits {bits} "
                      f"stem {stored}")
    return 0


def job_parser(description):
    parser = ReaderArgumentParser(description=description)
    dat = os.environ.get("LOL3_DAT")
    parser.add_argument("--data", required=dat is None, default=dat, help="your game folder or its DAT folder")
    return parser


def text_job():
    from level_html import find_data

    parser = job_parser("Read original game text from a LoL3 dialogue table.")
    parser.add_argument("table", nargs="?", metavar="TABLE", help=", ".join(TRR_AT))
    parser.add_argument("--trr", help=argparse.SUPPRESS)
    parser.add_argument("--id", type=int, help="show the text for one record ID")
    args = parser.parse_args()
    if bool(args.table) == bool(args.trr):
        parser.error(f"Choose one table: {', '.join(TRR_AT)}.")
    return show_text(find_data(args.data, "DAT", "LOCALLNG.WSX"), args.table or args.trr, args.id)


def music_job():
    from level_html import find_data

    parser = job_parser("List the MP3 and WAVE tracks in LoL3 music archives.")
    parser.add_argument("--tracks", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    return music_tracks(find_data(args.data, "DAT", "MUSIC1.WSX"))


def main():
    parser = ReaderArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=os.environ.get("LOL3_DAT"),
                        required="LOL3_DAT" not in os.environ, help="original game's DAT folder")
    parser.add_argument("--check", action="store_true", help="verify all entries in place")
    parser.add_argument("--movie", help="print one movie's top-level chunks")
    parser.add_argument("--tracks", action="store_true", help="print each music entry's format and stem")
    parser.add_argument("--samples", help="print one level sidecar's sample offsets and format fields")
    parser.add_argument("--trr", help="print one dialogue directory: ids and boundaries, no payload")
    parser.add_argument("--id", type=int, help="with --trr, show the text of one record")
    args = parser.parse_args()
    if args.id is not None and not args.trr:
        parser.error("Use --id with --trr, such as --trr dtext.trr --id 0.")
    chosen = [name for name in ("movie", "tracks", "samples", "trr") if getattr(args, name)]
    if chosen and (args.check or len(chosen) != 1):
        parser.error("pass only one of --movie, --tracks, --samples, --trr or --check")
    try:
        if not chosen:
            return check(args.data, summary=not args.check)
        data = Path(args.data)
        if args.trr:
            return show_text(data, args.trr, args.id)
        if args.movie:
            names = movie_names((data.parent / "LOL3.DAT").read_bytes())
            wanted = args.movie.upper()
            found = [(key, name) for key, name in names.items() if wanted in name.upper()]
            if len(found) != 1:
                raise ValueError(f"{args.movie} matches {len(found)} movie names")
            key, name = found[0]
            files = {path.stem.upper(): path for path in data.iterdir() if path.suffix.upper() == ".WSX"}
            hit = None
            for stem in sorted(path for path in files if path.startswith("MOVIES")):
                with files[stem].open("rb") as stream:
                    for row_key, start, size in wsx_rows(stream):
                        if row_key == key:
                            hit = (files[stem], stream.name, start, size)
                            chunks = movie_chunk_lines(stream, start, size)
                            break
                if hit:
                    break
            if hit is None:
                raise ValueError(f"no archive entry for {name}")
            print(f"{hit[0].name}+0x{hit[2]:X} {name} chunks {len(chunks)}")
            print("\n".join(chunks))
            return 0
        if args.tracks:
            return music_tracks(data)
        stem = args.samples.upper()
        files = {path.stem.upper(): path for path in data.iterdir() if path.suffix.upper() == ".WSX"}
        path = files.get(stem + "S")
        if path is None:
            raise ValueError(f"no sidecar for {stem}")
        with path.open("rb") as stream:
            rows = wsx_rows(stream)
            print(f"{path.name} samples {len(rows)}")
            for key, start, size in rows:
                tag, channels, rate, _byterate, align, bits = wave_fields(stream, start, size)
                print(f"+0x{start:X} size {size} key {key:08X} tag {tag:#x} "
                      f"channels {channels} rate {rate} align {align} bits {bits}")
        return 0
    except (OSError, ValueError, KeyError, struct.error, StopIteration) as exc:
        print(f"CHECK media failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
