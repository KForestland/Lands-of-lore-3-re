import struct
import sys
import tempfile
import unittest
import zlib
from ctypes.util import find_library
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from extract_wsx_entries import parse_wsx, wsx_name_hash
from lol3_save_header import HEADER_SIZE, parse_header
from lol3_script_framing import frame
from lol3_texture_archive import chunks
from lol3_texture_png import decode_texture, png_bytes, rgba_palette
from walk_lmf_leaves import lzo_decoder


class ReaderTests(unittest.TestCase):
    def test_wsx_directory(self):
        key = wsx_name_hash("test.txt")
        self.assertEqual(key, wsx_name_hash("TEST.TXT"))
        archive = struct.pack("<HIIII", 1, 3, key, 0, 3) + b"abc"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.wsx"
            path.write_bytes(archive)
            row, = parse_wsx(path)["entries"]
            self.assertEqual((row["hash"], row["offset"], row["blob"]), (key, 18, b"abc"))
            path.write_bytes(archive[:-1])
            with self.assertRaises(ValueError):
                parse_wsx(path)

    def test_lzo_chunk_framing(self):
        # A three-byte literal run, then the LZO1X end marker.
        packed = b"\x14abc\x11\0\0"
        source = struct.pack("<II", 3, len(packed)) + packed + struct.pack("<I", 0)
        self.assertEqual(list(chunks(source)), [(packed, 3)])
        with self.assertRaises(ValueError):
            list(chunks(source[:-1]))
        if find_library("lzo2"):
            self.assertEqual(lzo_decoder()(packed, 3), b"abc")

    def test_script_index_must_match_command_boundaries(self):
        payload = bytearray(0x260)
        stream = bytes((0xF0, 0, 0, 0, 1, 0, 0x16, 0, 0, 0, 7, 0))
        start, index = 0x244, 0x244 + len(stream)
        for field, value in ((0x44, start), (0x8C, len(stream)), (0x4C, index), (0x98, 8)):
            struct.pack_into("<I", payload, field, value)
        payload[start:index] = stream
        struct.pack_into("<2I", payload, index, 0, 6)
        self.assertEqual(frame(payload, {0xF0: 6, 0x16: 6})[:3], (len(stream), 2, 2))
        struct.pack_into("<I", payload, index + 4, 7)
        with self.assertRaises(ValueError):
            frame(payload, {0xF0: 6, 0x16: 6})

    def test_save_directory(self):
        header = bytearray(HEADER_SIZE)
        end = HEADER_SIZE + 12
        struct.pack_into("<3I", header, 0x2C, end, 38, 310)
        struct.pack_into("<3I", header, 0x39C, 8, 4, HEADER_SIZE)
        struct.pack_into("<61I", header, 0x4B8, HEADER_SIZE + 3, *([HEADER_SIZE + 8] * 60))
        struct.pack_into("<18I", header, 0x5B0, HEADER_SIZE + 8, *([end] * 17))
        struct.pack_into("<I", header, 0x600, 4)
        parsed = parse_header(header, end)
        self.assertEqual(parsed["preview"], (HEADER_SIZE, 3))
        self.assertEqual(parsed["levels"][0], (HEADER_SIZE + 8, 4))
        struct.pack_into("<I", header, 0x600, 9)
        with self.assertRaises(ValueError):
            parse_header(header, end)

    def test_texture_bake_to_png(self):
        source = struct.pack("<256H", 0, 0x7C00, *([0] * 254))
        palette = rgba_palette(source, transparent_zero=True)
        payload = struct.pack("<HH", 0x4001, 2) + bytes((1, 0))
        record = struct.pack("<IHHI", 0x028E, 3, 1, len(payload)) + payload
        width, height, rgba = decode_texture(record, palette)
        expected = b"\0\0\0\0\xf8\0\0\xff\0\0\0\0"
        self.assertEqual((width, height, rgba), (3, 1, expected))
        png = png_bytes(width, height, rgba)
        length, tag = struct.unpack_from(">I4s", png, 33)
        self.assertEqual(tag, b"IDAT")
        self.assertEqual(zlib.decompress(png[41:41 + length]), b"\0" + expected)
