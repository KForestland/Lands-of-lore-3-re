"""Synthetic containers for the readers that share directory and record code."""
import io
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from extract_wsx_entries import wsx_name_hash
from lol3_level_report import read_level
from lol3_media_check import form, trr_directory, wave_fields, wsx_rows
from lol3_native_checks import CODE_BIAS, direct_call, opcode
from lol3_script_notes import STREAMS, walk
from lol3_texture_palettes import bank_directory, palette_sources
from lol3_texture_spans import records
from walk_lmf_leaves import lmf_groups


def archive(rows):
    directory = bytearray()
    payload = bytearray()
    for key, value in rows:
        directory.extend(struct.pack("<III", key, len(payload), len(value)))
        payload.extend(value)
    return struct.pack("<HI", len(rows), len(payload)) + directory + payload


def chunk(tag, data):
    return struct.pack("<4sI", tag, len(data)) + data + bytes(len(data) % 2)


def map_with_one_command():
    data = bytearray(0x244)
    struct.pack_into("<I", data, 0, 38)
    struct.pack_into("<III", data, 4, 0x244, 0x244, 0x244)
    struct.pack_into("<I", data, 4 + 16 * 4, 0x244)
    struct.pack_into("<I", data, 0xC8, 0x244)
    struct.pack_into("<I", data, 0xDC, 0x244)
    stream = bytes((0x01, 0, 0, 0, 1, 0))
    stream_at, stream_size, _, _ = STREAMS["object"]
    struct.pack_into("<I", data, stream_at, len(data))
    struct.pack_into("<I", data, stream_size, len(stream))
    data.extend(stream)
    struct.pack_into("<I", data, 0x4C, len(data))
    struct.pack_into("<I", data, 0x98, 4)
    data.extend(bytes(4))
    return data


class BinaryFormats(unittest.TestCase):
    def test_dialogue_directory_reaches_entry_end(self):
        data = struct.pack("<4I", 1, 5, 12, 14) + b"T\0"
        self.assertEqual(trr_directory(data, "sample"), ((5,), (12, 14)))
        with self.assertRaises(ValueError):
            trr_directory(data[:-1], "sample")

    def test_streamed_wsx_one_member(self):
        data = archive([(0x11223344, b"end")])
        self.assertEqual(wsx_rows(io.BytesIO(data)), [(0x11223344, 18, 3)])
        with self.assertRaises(ValueError):
            wsx_rows(io.BytesIO(data[:-1]))

    def test_level_sheet_reads_map_member_and_stream(self):
        data = map_with_one_command()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "SYN.WSX"
            data = archive([(wsx_name_hash("LEVELS\\SYN\\SYN.MAP"), data)])
            path.write_bytes(data)
            level = read_level("SYN", path, None, dict(sizes={1: 6}, movies={}, music=[], levels=[]))
            self.assertEqual(level["roles"], [".MAP"])
            self.assertEqual(level["script"]["opcodes"]["object"], {1: 1})
            self.assertTrue(level["geometry_ok"])
            self.assertEqual(level["rows"][0][2] + level["rows"][0][3], len(data))
            path.write_bytes(data[:-1])
            with self.assertRaises(ValueError):
                read_level("SYN", path, None, {})

    def test_note_walk_checked_against_index_and_eof(self):
        data = map_with_one_command()
        stream, starts, base, counts, _, aliases = walk(data, 12, "object", {1: 6})
        self.assertEqual((bytes(stream), starts, base, counts, dict(aliases)),
                         (b"\x01\0\0\0\x01\0", [0], 0x250, {}, {0: [0]}))
        with self.assertRaises(ValueError):
            walk(data[:-1], 12, "object", {1: 6})

    def test_wave_one_record_and_declared_file_end(self):
        fmt = struct.pack("<HHIIHH", 1, 1, 8000, 16000, 2, 16)
        wave = chunk(b"RIFF", b"WAVE" + chunk(b"fmt ", fmt) + chunk(b"data", b"\x32\0"))
        self.assertEqual(wave_fields(io.BytesIO(wave), 0, len(wave)), (1, 1, 8000, 16000, 2, 16))
        with self.assertRaises(ValueError):
            list(form(io.BytesIO(wave[:-1]), 0, len(wave) - 1, b"RIFF", b"WAVE", "<"))

    def test_one_light_map_group_at_eof(self):
        header = struct.pack("<7I", 0, 38, 0x100, 0x110, 16, 4, 1).ljust(0x100, b"\0")
        data = header + struct.pack("<4I", 0, 4, 0, 4) + b"end!"
        row, = lmf_groups(data)
        self.assertEqual((row["offset"], row["lengths"], row["offset"] + row["packed"]),
                         (0x110, [4], len(data)))
        with self.assertRaises(ValueError):
            list(lmf_groups(data[:-1]))

    def test_span_and_one_palette_join(self):
        descriptor, pixels, palettes = 0x6A2, 0x6DC, 0x6F0
        data = bytearray(palettes + 512)
        at = struct.pack_into
        for offset, value in ((0, 38), (0x10, descriptor), (0x14, pixels),
                              (0x34, palettes), (0x40, 0x300), (0x4C, 58),
                              (0x54, 0x4200), (0x58, 0x20000), (0x70, 512),
                              (0x2A8, 1), (descriptor + 0x26, 17)):
            at("<I", data, offset, value)
        data[descriptor + 0xD] = 3
        at("<IHHIHHB", data, pixels, 0x28E, 1, 1, 5, 0x4000, 1, 0)
        self.assertEqual(list(records(data)), [(pixels, 0x28E, 1, 1, 5, True)])
        rows = palette_sources(data)
        self.assertEqual(rows[pixels]["palette_offset"] + 512, len(data))
        with self.assertRaises(ValueError):
            bank_directory(data[:-1], 0, len(data) - 1)

    def test_native_anchor_checks_a_whole_call(self):
        address = CODE_BIAS + 3
        target = address + 19
        program = b"\0" * 3 + b"\xe8" + struct.pack("<i", target - address - 5)
        opcode(program, address, "e8")
        self.assertIsNone(direct_call(program, address, target))
        with self.assertRaises(struct.error):
            direct_call(program[:-1], address, target)
