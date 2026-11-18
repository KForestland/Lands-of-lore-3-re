#!/usr/bin/env python3
"""Check original LoL3 movie names, VQA chunk framing and WAVE audio in place."""
import argparse
from collections import Counter
import hashlib
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=os.environ.get("LOL3_DAT"),
                        required="LOL3_DAT" not in os.environ, help="original game's DAT folder")
    parser.add_argument("--check", action="store_true", help="verify all entries in place")
    args = parser.parse_args()
    try:
        return check(args.data, summary=not args.check)
    except (OSError, ValueError, KeyError, struct.error) as exc:
        print(f"CHECK media failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
