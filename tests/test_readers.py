import struct
import sys
import tempfile
import unittest
import zlib
from ctypes.util import find_library
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from extract_wsx_entries import parse_wsx, wsx_name_hash
from lol3_cache_seed import FILL_MARKER, HEADER, body_covers
from lol3_pht import cycle_covers, pht_covers
from lol3_save_header import HEADER_SIZE, parse_header
from lol3_script_framing import frame
from lol3_texture_archive import chunks
from lol3_level_schematic import map_geometry, schematic_svg
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

    def test_pht_cycle_rejects_a_corrupt_later_byte(self):
        period = 16
        block = bytes(range(0x30, 0x30 + period))
        stream = block * 3 + block[:7]
        pin = sha256(block).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Small.PHT"
            path.write_bytes(stream)
            self.assertTrue(cycle_covers(path, period, pin))
            self.assertTrue(pht_covers(path, {"small.pht": len(stream)}, period, pin))
            self.assertFalse(pht_covers(path, {"small.pht": len(stream) + 1}, period, pin))
            self.assertFalse(cycle_covers(path, period, "0" * 64))
            for at in (period + 3, len(stream) - 1):
                corrupt = bytearray(stream)
                corrupt[at] ^= 1
                path.write_bytes(corrupt)
                self.assertFalse(cycle_covers(path, period))
            path.write_bytes(block)
            self.assertFalse(cycle_covers(path, period))

    def test_cache_body_rejects_a_changed_header(self):
        size, copies = 8, 3
        header = bytes(range(HEADER))
        block = FILL_MARKER.to_bytes(4, "little") + b"\x01\x02\x03\x04"
        data = header + block * copies
        pins = dict(header_sha=sha256(header).hexdigest(), block_sha=sha256(block).hexdigest(),
                    block_size=size, copies=copies)
        self.assertTrue(body_covers(data, **pins))
        changed = bytearray(data)
        changed[5] ^= 1
        self.assertFalse(body_covers(bytes(changed), **pins))
        changed = bytearray(data)
        changed[HEADER + 2 * size + 6] ^= 1
        self.assertFalse(body_covers(bytes(changed), **pins))
        self.assertFalse(body_covers(data, **dict(pins, block_sha="0" * 64)))

    def test_schematic_marks_need_no_game_files(self):
        header = bytearray(0x244)
        struct.pack_into("<I", header, 0, 38)
        vertex_start = 0x244
        point_start = vertex_start + 8 * 4
        path_start = point_start + 34
        field1 = path_start + 35
        surface = field1
        surface_end = surface + 56
        tables = surface_end
        strides = (0x25, 0x21, 0x38, 0x25)
        offsets = []
        for stride in strides:
            offsets.append(tables)
            tables += stride
        struct.pack_into("<6I", header, 4, vertex_start, field1, surface, 0, 0, 0)
        struct.pack_into("<I", header, 4 + 16 * 4, surface_end)
        struct.pack_into("<3I", header, 4 + 19 * 4, 4, 0, 1)
        struct.pack_into("<II", header, 0xC4, 1, point_start)
        struct.pack_into("<II", header, 0xD8, 1, path_start)
        for at, offset, count_at in zip((0x14, 0x18, 0x1C, 0x20), offsets, (0x60, 0x64, 0x68, 0x6C)):
            struct.pack_into("<I", header, at, offset)
            struct.pack_into("<I", header, count_at, 1)
        body = bytearray(tables)
        body[:0x244] = header
        scale = 10 << 16
        for index, (x, z) in enumerate(((0, 0), (scale, 0), (scale, scale), (0, scale))):
            struct.pack_into("<ii", body, vertex_start + 8 * index, x, z)
        struct.pack_into("<hhHH", body, point_start, 5, 5, 0, 0)
        struct.pack_into("<HBB", body, path_start, 0, 1, 0)
        struct.pack_into("<4H", body, surface + 0x10, 0, 1, 2, 3)
        struct.pack_into("<H", body, surface + 0x1E, 0xFFFF)
        for offset, (x, z) in zip(offsets, ((2, 3), (4, 6), (7, 1), (8, 8))):
            struct.pack_into("<hh", body, offset, x, z)
        vertices, surfaces, waypoints, routes, placed = map_geometry(bytes(body))
        self.assertEqual(len(vertices), 4)
        self.assertEqual(waypoints, [(5 << 16, 5 << 16)])
        self.assertEqual(routes, [[(5 << 16, 5 << 16)]])
        self.assertEqual([item[:2] for item in placed],
                         [("type 3", 1), ("type 16", 1), ("creature", 1), ("item", 1)])
        drawing = schematic_svg("SYN", vertices, surfaces, waypoints, routes, placed)
        self.assertIn("waypoint (1)", drawing)
        self.assertIn("path (1)", drawing)
        self.assertIn('stroke-dasharray="5 3"', drawing)
        self.assertIn("<title>SYN MAP schematic</title>", drawing)
        self.assertIn(">1</text>", drawing)
        self.assertIn("numbered", drawing)
