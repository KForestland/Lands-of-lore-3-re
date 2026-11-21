#!/usr/bin/env python3
"""Convert original LoL3 VQA movies to MKV and WAVE sounds to PCM WAV."""
from io import BytesIO
import json
from pathlib import Path
import shutil
import struct
import subprocess
from tempfile import TemporaryDirectory
import wave

from cli_errors import ReaderArgumentParser, game_path, input_path, run_cli
from level_html import counted, installation_root
from lol3_cli import DEFAULT_DATA, wsx_files
from lol3_media_check import check_movie, form, read_at, wave_fields, wsx_rows
from modkit_core import output_folder


def find_source(data, name):
    supplied = Path(name).expanduser()
    if supplied.is_absolute() or supplied.parent != Path("."):
        candidates = (input_path(supplied),)
    else:
        candidates = (game_path(folder, supplied.name) for folder in (data, data.parent))
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise ValueError(f"Give --file the name or path of an existing media file because {name} was not found.")


def media_entries(path, mode):
    expected = (b"FORM", b"WVQA") if mode == "movie" else (b"RIFF", b"WAVE")
    with path.open("rb") as stream:
        for index, (_, at, length) in enumerate(wsx_rows(stream)):
            if length >= 12:
                header = read_at(stream, at, 12)
                if (header[:4], header[8:12]) == expected:
                    yield index, at, length


def list_archives(data, mode):
    archives = 0
    for archive in wsx_files(data):
        stem = archive.stem.upper()
        if mode == "movie" and not stem.startswith("MOVIES"):
            continue
        if mode == "sound" and not (stem.startswith("MUSIC") or stem.endswith("S")):
            continue
        count = sum(1 for _ in media_entries(archive, mode))
        if count:
            print(f"{archive.name}: {counted(count, mode + ' entry', mode + ' entries')}")
            archives += 1
    if not archives:
        raise ValueError(f"Give --data the original game folder because no {mode} entries were found in {data}.")
    print("Add --file and an archive name to list entry numbers.")


def ffmpeg_programs():
    encoder = shutil.which("ffmpeg")
    probe = shutil.which("ffprobe")
    if not encoder or not probe:
        raise ValueError("Install FFmpeg with FFprobe and reopen the terminal to use this conversion.")
    return encoder, probe


def exported_counts(probe, path):
    result = subprocess.run(
        [probe, "-v", "error", "-count_frames", "-show_entries",
         "stream=codec_type,nb_read_frames:frame=nb_samples", "-of", "json", str(path)],
        capture_output=True, text=True, check=False,
    )
    if result.returncode:
        raise ValueError("Check the FFmpeg installation because FFprobe could not read the converted movie.")
    report = json.loads(result.stdout)
    frames = sum(int(row["nb_read_frames"]) for row in report.get("streams", [])
                 if row["codec_type"] == "video")
    samples = sum(int(row["nb_samples"]) for row in report.get("frames", []) if "nb_samples" in row)
    return frames, samples


def wave_sample_count(source, size):
    tag, channels, rate, _, align, _ = wave_fields(source, 0, size)
    payload_size = fact = None
    for kind, at, length in form(source, 0, size, b"RIFF", b"WAVE", "<"):
        if kind == b"fact" and length >= 4:
            fact, = struct.unpack("<I", read_at(source, at, 4))
        elif kind == b"data":
            payload_size = length
    if payload_size is None or not align or not channels or not rate:
        raise ValueError("Choose an intact WAVE file with a format and audio data.")
    if tag == 1 and payload_size % align == 0:
        return channels, rate, payload_size // align
    if tag in (0x11, 0x55) and fact:
        return channels, rate, fact
    raise ValueError("Choose a supported PCM, IMA ADPCM or MP3 WAVE with a valid sample count.")


def convert(blob, mode, out, stem, ffmpeg, ffprobe):
    source = BytesIO(blob)
    if mode == "movie":
        frames, _, packet_sizes, _ = check_movie(source, 0, len(blob))
        samples = sum(size * count for size, count in packet_sizes.items())
        suffix, output_suffix = ".vqa", ".mkv"
        encoding = ["-map", "0:v:0", "-map", "0:a:0", "-c:v", "ffv1", "-c:a", "pcm_s16le"]
    else:
        channels, rate, samples = wave_sample_count(source, len(blob))
        suffix = output_suffix = ".wav"
        encoding = ["-map", "0:a:0", "-af", f"atrim=end_sample={samples}", "-c:a", "pcm_s16le"]

    output = out / (stem + output_suffix)
    with TemporaryDirectory(prefix="lol3-media-") as scratch:
        original = Path(scratch) / ("source" + suffix)
        original.write_bytes(blob)
        result = subprocess.run(
            [ffmpeg, "-nostdin", "-v", "error", "-n", "-i", str(original), *encoding, str(output)],
            capture_output=True, check=False,
        )
        if result.returncode or not output.exists():
            raise ValueError("Check the FFmpeg installation or use another source entry because conversion failed.")
    if mode == "movie":
        if exported_counts(ffprobe, output) != (frames, samples):
            raise ValueError("Choose an intact original movie because the converted frame or sample count differs.")
        summary = f"{frames:,} frames and {samples:,} stereo sample frames"
    else:
        with wave.open(str(output), "rb") as converted:
            if (converted.getnchannels(), converted.getframerate(), converted.getnframes()) != (channels, rate, samples):
                raise ValueError("Choose an intact original sound because the converted WAVE format or sample count differs.")
        summary = f"{samples:,} sample frames at {rate:,} Hz"
    return output.name, summary


def main(mode=None):
    parser = ReaderArgumentParser(description=__doc__)
    if mode is None:
        parser.add_argument("mode", choices=("movie", "sound"))
    else:
        parser.set_defaults(mode=mode)
    parser.add_argument("--data", default=DEFAULT_DATA, required=DEFAULT_DATA is None,
                        help="your game folder or its DAT folder (default: $LOL3_DAT)")
    parser.add_argument("--file", help="WSX archive or loose media file name or path")
    parser.add_argument("--entry", type=int, help="zero-based WSX entry number from --list")
    parser.add_argument("--list", action="store_true", help="list matching archives or entries without writing")
    parser.add_argument("--out", help="new folder for the converted file")
    args = parser.parse_args()
    data = Path(args.data).resolve()
    if args.list and (args.entry is not None or args.out):
        parser.error("Use --list without --entry or --out.")
    if args.list and not args.file:
        list_archives(data, args.mode)
        return 0
    if not args.file:
        parser.error("Give --file an archive or media file name or use --list to find one.")
    path = find_source(data, args.file)
    archive = path.suffix.upper() == ".WSX"
    if args.list:
        if not archive:
            parser.error("Give --file a WSX archive to list entry numbers.")
        entries = list(media_entries(path, args.mode))
        for index, _, length in entries:
            print(f"Entry {index:>4}: {length:,} bytes")
        print(f"{path.name}: {counted(len(entries), args.mode + ' entry', args.mode + ' entries')}")
        return 0
    if not args.out or archive != (args.entry is not None):
        parser.error("Give --out a new folder and use --entry only with a WSX archive.")
    if archive:
        match = next((row for row in media_entries(path, args.mode) if row[0] == args.entry), None)
        if match is None:
            parser.error(f"Use --list to select a {args.mode} because entry {args.entry} does not contain one.")
        with path.open("rb") as stream:
            raw = read_at(stream, *match[1:])
    else:
        raw = path.read_bytes()
    stem = path.stem + (f"-{args.entry}" if archive else "")
    with output_folder(args.out, installation_root(data), args.data, path) as folder:
        name, summary = convert(raw, args.mode, folder, stem, *ffmpeg_programs())
    print(f"Wrote {name} to {args.out}: {summary}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
