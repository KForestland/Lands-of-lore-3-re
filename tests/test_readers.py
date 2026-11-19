import io
import struct
import sys
import tempfile
import unittest
import zlib
from collections import Counter
from ctypes.util import find_library
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from extract_wsx_entries import directory_lines, parse_wsx, wsx_name_hash
from lol3_cache_seed import shipped_listing, written_listing
from lol3_claimed_edges import MAP_HEADER, MAP_VERTICES, pattern_lines, shared_block_text
from lol3_combat_census import item_lines, mitigation_lines
from lol3_map_spans import row_listing, section1_listing
from lol3_media_check import movie_chunk_lines, trr_lines
from lol3_name_hash import stem_lines
from lol3_odf_companions import name_listing
from lol3_pht import head_line
from lol3_script_framing import object_slot_lines, subcommand_lines
from lol3_script_notes import timer_lines
from lol3_texture_archive import descriptor_lines
from lol3_texture_png import slice_directory_lines
from walk_lmf_leaves import directory_text
from lol3_cache_seed import FILL_MARKER, HEADER, body_covers
from lol3_pht import cycle_covers, pht_covers
from lol3_save_header import HEADER_SIZE, parse_header, report, synthetic_slot
from lol3_script_browser import MEANINGS, summary_text
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
        short = report(bytes(header) + bytes(12))
        self.assertIn("version +0x30/+0x34: 38 310", short)
        self.assertIn("+0x94: 00 00 00 00", short)
        self.assertIn("shorter than the 0x34c block header", short)
        self.assertNotIn("section 0:", short)
        struct.pack_into("<I", header, 0x600, 9)
        with self.assertRaises(ValueError):
            parse_header(header, end)

    def test_save_report_needs_no_game_files(self):
        blob = synthetic_slot()
        text = report(blob)
        self.assertIn("display name +0: Reader", text)
        self.assertIn(f"file length +0x2c: {len(blob)}", text)
        self.assertIn("version +0x30/+0x34: 38 310", text)
        self.assertNotIn("layout", text)
        self.assertIn("display name bytes after the NUL +0x7..+0x2c:", text)
        self.assertIn("+0x7: 52 53 00", text)
        self.assertIn("unnamed +0x5ac..+0x5b0:\n+0x5ac: 5a 5a 5a 5a", text)
        self.assertIn("unnamed +0x5f8..+0x600:\n+0x5f8: 66 77 88 99 aa bb cc dd", text)
        self.assertIn("+0x94: aa bb cc dd", text)
        self.assertIn("+0x648: 10 20 30 40", text)
        self.assertIn("player +0x49c: x 65536 (1.0000) z -131072 (-2.0000) heading 0x8000 region 0x18", text)
        self.assertIn("second object +0x4aa: x 196608 (3.0000) z 262144 (4.0000) heading 0x100 region 0xffff", text)
        self.assertIn("global 0 +0x650 length 4", text)
        self.assertEqual(sum(line.startswith("global ") and line[7].isdigit() for line in text.splitlines()), 61)
        self.assertIn("level index 0 section 0: stored +0x34c length 8, expanded 16, not expanded", text)
        self.assertEqual(sum(line.startswith("level index 0 section ") for line in text.splitlines()), 75)
        self.assertEqual(text.count(": empty"), 17)
        self.assertNotIn("PAYLOAD", text)
        self.assertNotIn("50 41 59 4c", text)
        broken = bytearray(blob)
        struct.pack_into("<I", broken, HEADER_SIZE + 8 + 0xF4 + 4, 0)
        with self.assertRaises(ValueError):
            report(bytes(broken))

    def test_directory_listings_need_no_game_files(self):
        key = wsx_name_hash("test.txt")
        archive = struct.pack("<HIIII", 1, 3, key, 0, 3) + b"abc"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.wsx"
            path.write_bytes(archive)
            listed = directory_lines(parse_wsx(path))
            head = Path(directory) / "a.pht"
            head.write_bytes(bytes(range(20)))
            self.assertEqual(head_line(head),
                             "a.pht 20 bytes +0: 00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f")
        self.assertIn(f"key {key:#010x} offset 0x12 size 3", listed)
        self.assertNotIn("abc", listed)
        table, table_size, pool_size, count = 0x100, 16, 4, 1
        pool = table + table_size
        header = struct.pack("<7I", 0, 38, table, pool, table_size, pool_size, count)
        data = header + bytes(table - len(header)) + struct.pack("<4I", 0, 4, 0, 4) + b"abcd"
        listing = directory_text(data, "SYN")
        self.assertIn("SYN: 276 bytes, directory rows 1, groups 1", listing)
        self.assertIn("group row 0 offset 0x110 packed 4 expanded 4 members 1", listing)
        self.assertNotIn("abcd", listing)
        block = bytearray(MAP_VERTICES)
        struct.pack_into("<3I", block, 0, 38, MAP_VERTICES, 0)
        struct.pack_into("<I", block, 0xCC, MAP_HEADER)
        block[MAP_HEADER:MAP_HEADER + 2] = b"\xab\xcd"
        span = shared_block_text(bytes(block))
        self.assertIn(f"span +{MAP_HEADER:#x}..+{MAP_VERTICES:#x}: {MAP_VERTICES - MAP_HEADER} bytes", span)
        self.assertIn("+0x244: ab cd", span)
        self.assertNotIn("count", span)
        self.assertNotIn("row", span)
        payload = bytearray(0x180)
        struct.pack_into("<II", payload, 0xC4, 1, 0x100)
        struct.pack_into("<hhHBB", payload, 0x100, 5, -6, 7, 2, 0)
        payload[0x108:0x122] = b"Secret\x00" + bytes(19)
        struct.pack_into("<II", payload, 0xD8, 1, 0x130)
        struct.pack_into("<HBB", payload, 0x130, 0, 1, 4)
        payload[0x134:0x153] = b"Hidden" + bytes(25)
        rows = row_listing(bytes(payload), "SYN")
        self.assertIn("waypoint 1: x 5 z -6 surface 0x7 +6 0x2 +7 0x0", rows)
        self.assertIn("53 65 63 72 65 74", rows)
        self.assertIn("path 1: first 0 count 1 flags 0x4", rows)
        self.assertNotIn("Secret", rows)
        self.assertNotIn("Hidden", rows)

    def test_script_browser_groups_opcodes_without_game_files(self):
        sizes = {0x01: 6, 0x16: 18, 0xF0: 6}
        command = bytes((0x01, 1, 0, 0, 4, 0))
        dialogue = bytes((0x16,)) + bytes(7) + b"ABCD" + bytes(6)
        self.assertEqual(len(dialogue), 18)
        text = summary_text("SYN", command + command + dialogue, bytes((0xF0, 0, 0, 0, 0, 0)), sizes)
        self.assertIn("SYN object commands: 3", text)
        self.assertIn(f"0x01 2: {MEANINGS[0x01]}", text)
        self.assertIn(f"0x16 1: {MEANINGS[0x16]}", text)
        self.assertNotIn("ABCD", text)
        self.assertIn("SYN region commands: 1", text)
        self.assertIn(f"0xF0 1: {MEANINGS[0xF0]}", text)
        with self.assertRaises(ValueError):
            summary_text("SYN", command[:-1], b"", sizes)

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
        strides = (0x25, 0x21, 0x38, 0x29, 0x25)
        offsets = []
        for stride in strides:
            offsets.append(tables)
            tables += stride
        struct.pack_into("<6I", header, 4, vertex_start, field1, surface, 0, 0, 0)
        struct.pack_into("<I", header, 4 + 16 * 4, surface_end)
        struct.pack_into("<3I", header, 4 + 19 * 4, 4, 0, 1)
        struct.pack_into("<II", header, 0xC4, 1, point_start)
        struct.pack_into("<II", header, 0xD8, 1, path_start)
        for at, offset, count_at in zip((0x14, 0x18, 0x1C, 0x24, 0x20), offsets, (0x60, 0x64, 0x68, 0x70, 0x6C)):
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
        for offset, (x, z) in zip(offsets, ((2, 3), (4, 6), (7, 1), (9, 2), (8, 8))):
            struct.pack_into("<hh", body, offset, x, z)
        vertices, surfaces, waypoints, routes, placed = map_geometry(bytes(body))
        self.assertEqual(len(vertices), 4)
        self.assertEqual(waypoints, [(5 << 16, 5 << 16)])
        self.assertEqual(routes, [[(5 << 16, 5 << 16)]])
        self.assertEqual([item[:2] for item in placed],
                         [("type 3", 1), ("type 16", 1), ("creature", 1), ("mover (type 32)", 1), ("item", 1)])
        drawing = schematic_svg("SYN", vertices, surfaces, waypoints, routes, placed)
        self.assertIn("mover (type 32) (1), numbered", drawing)
        self.assertIn('fill="none" stroke="#14343b"', drawing)
        self.assertLess(drawing.index("<circle"), drawing.index('<rect x="'))
        self.assertIn("waypoint (1)", drawing)
        self.assertIn("path (1)", drawing)
        self.assertIn('stroke-dasharray="5 3"', drawing)
        self.assertIn("<title>SYN MAP schematic</title>", drawing)
        self.assertIn(">1</text>", drawing)
        self.assertIn("numbered", drawing)
        self.assertIn("1-based", drawing)
        # A far waypoint does not widen the scale; two dots on one spot keep one number.
        notes = []
        crowded = placed + [("item", 2, 8 << 16, 8 << 16, "#c47b12")]
        wide = schematic_svg("SYN", vertices, surfaces, waypoints + [(5000 << 16, 0)], routes, crowded, notes=notes)
        self.assertIn("1 overlapping numbers left out", notes)
        self.assertIn("outside the bounding box of the surface edges, not drawn: 1 waypoints, 0 placements", notes)
        self.assertEqual(wide.count('<rect x="'), drawing.count('<rect x="'))
        bare = schematic_svg("SYN", vertices, surfaces, waypoints, routes, placed, labels=False)
        self.assertNotIn("paint-order", bare)
        self.assertNotIn("numbered", bare)

    def test_remaining_listings_need_no_game_files(self):
        header = bytearray(0x76)
        header[0:2] = b"\xab\xcd"
        struct.pack_into("<I", header, 0x72, 0xD0BCD8BE)
        shipped = shipped_listing(bytes(header))
        self.assertIn("header 114 bytes", shipped)
        self.assertIn("dword +0x72 0xd0bcd8be", shipped)
        self.assertIn("+0x0: ab cd", shipped)
        self.assertNotIn("field", shipped)
        prefix = bytearray(0x76 + 40 * 0x18)
        struct.pack_into("<I", prefix, 0x72, 0xF1E2D3C4)
        struct.pack_into("<5I", prefix, 0x76, 0x436, 4, 0xE128E112, 3, 9)
        prefix[0x76 + 0x14:0x76 + 0x18] = bytes((1, 2, 0, 0x67))
        written = written_listing(bytes(prefix))
        self.assertIn("position 0x436 span 0x4 key 0xe128e112", written)
        self.assertIn("generation index 2 pin 0 +0x17 0x67", written)
        payload = bytearray(0x60)
        struct.pack_into("<II", payload, 0x08, 0x40, 0)
        struct.pack_into("<I", payload, 0x54, 1)
        struct.pack_into("<HBBBBBB", payload, 0x40, 0xFFFF, 1, 2, 128, 0x14, 8, 0)
        rows = section1_listing(bytes(payload), "SYN")
        self.assertIn("SYN section-1 rows 1", rows)
        self.assertIn("row 1: +0 0xffff +2 0x1 +3 0x2 +4 0x80 +5 0x14 +5&0x1f 0x14 +6 0x8 +7 0x0", rows)
        odf = bytearray(0x200)
        struct.pack_into("<I", odf, 4, 0x80)
        struct.pack_into("<I", odf, 0x3C, 1)
        struct.pack_into("<I", odf, 0x10, 0xAE)
        struct.pack_into("<I", odf, 0x48, 1)
        odf[0x80 + 24:0x80 + 31] = b"Floor39"
        odf[0xAE + 0x87:0xAE + 0x8D] = b"SPIDER"
        struct.pack_into("<HH", odf, 0xAE + 0x59, 750, 500)
        listed, tags = name_listing(bytes(odf), "SYN")
        self.assertEqual(tags, ["SPIDER"])
        self.assertIn("name 1: Floor39", listed)
        self.assertIn("creature 1: tag SPIDER +0x59 750 +0x5b 500", listed)
        bank = bytearray(0x2AC + 58)
        struct.pack_into("<I", bank, 0x10, 0x2AC)
        struct.pack_into("<I", bank, 0x2A8, 1)
        struct.pack_into("<H", bank, 0x2AC + 2, 0x15)
        bank[0x2AC + 0xD] = 3
        self.assertIn("descriptor 1: +0x2ac key 0x15 arm 3", descriptor_lines(bytes(bank), "SYN"))
        frame = bytearray(24)
        struct.pack_into("<II", frame, 16, 0x130, 0x142)
        directory = slice_directory_lines(bytes(frame), 2, "a.smd")
        self.assertIn("slice 0 +0x130", directory)
        self.assertIn("slice 1 +0x142", directory)
        blob = struct.pack("<IIII", 1, 7, 0x0C, 0x12) + b"HELLO\0"
        dialogue = trr_lines(blob, "qevent.trr")
        self.assertIn("id 7 boundary 0xc", dialogue)
        self.assertNotIn("HELLO", dialogue)
        self.assertIn("key 0x%08x" % wsx_name_hash("MUSIC\\Tune.aud"), stem_lines(["Tune"]).replace("0x", "0x"))
        record = bytes((2, 0, 0, 0)) + struct.pack("<8H", 0x104, 4, 0, 0, 0, 0, 0, 0)
        self.assertIn("selectors 0x2 0x0 0x0 0x0 masks 0x104/0x4", mitigation_lines(Counter({record: 3})))
        archive = bytearray(0x3A56 + 139 * 343)
        for index in range(1, 343):
            archive[0x3A56 + 139 * index + 0x3F] = 2
        archive[0x3A56 + 0x73:0x3A56 + 0x77] = struct.pack("<I", 0x50)
        archive[0x3A56 + 0x4B:0x3A56 + 0x4F] = struct.pack("<I", 1)
        text = item_lines(bytes(archive))
        self.assertIn("definition 0: +0x73 0x50", text)
        self.assertIn("regular definitions 1", text)
        image = bytearray(0x48E1C + 28 * 4)
        struct.pack_into("<I", image, 0x48E1C, 0x447F31)
        self.assertIn("slot 1 opcode 0x01: 0x447f31", object_slot_lines(bytes(image)))
        payload = bytearray(0xC0)
        struct.pack_into("<I", payload, 0x44, 0xA0)
        struct.pack_into("<I", payload, 0x8C, 8)
        payload[0xA0:0xA8] = bytes((0x0D, 2, 0, 0, 2, 0, 0, 0))
        struct.pack_into("<I", payload, 0x3C, 0xA8)
        struct.pack_into("<I", payload, 0x84, 12)
        payload[0xA8:0xB4] = bytes((0xC4, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0))
        listed = subcommand_lines([("SYN", bytes(payload))],
                                  {0x0D: 8, 0x0F: 8, 0x1C: 38, 0xC4: 12, 0xC6: 6, 0xC7: 6, 0xCE: 6, 0xCF: 6})
        self.assertIn("subcommand 2: 1", listed)
        self.assertIn("opcode 0xC4 records 0", listed)
        timers = timer_lines("SYN", {"object": (None, None, None, Counter({2: 2}))})
        self.assertIn("object kind 2 timer expires: 2", timers)
        body = b"VQHD" + struct.pack(">I", 42) + bytes(42)
        form = b"FORM" + struct.pack(">I", 4 + len(body)) + b"WVQA" + body
        chunks = movie_chunk_lines(io.BytesIO(form), 0, len(form))
        self.assertEqual(chunks, [f"VQHD +0xc size 42"])
        counted = pattern_lines({"counts": {0xE128E119: 1, 0xD0B8E10A: 2, 0x00A8E101: 3, 0xDCD8E100: 0},
                                 "plus4": Counter({0: 4, 2: 5, 6: 6, 0x0B: 0})})
        self.assertIn("QWOD0 C5 A5: texture 1, MAP 2, light map 3, ODF 0", counted)
        self.assertIn("0xb on 0", counted)
