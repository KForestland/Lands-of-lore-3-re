"""Synthetic witnesses for the format writers."""
from ctypes.util import find_library
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from extract_wsx_entries import parse_wsx, parse_wsx_bytes
from lol3_lzo_writer import lzo_encoder, mutation_check as lzo_mutation_check, write_light_map, write_texture
from lol3_wsx_writer import mutation_check, relayout, write_wsx
from walk_lmf_leaves import lzo_decoder


class WsxRoundTrip(unittest.TestCase):
    def test_preserves_directory_order(self):
        rows = [(0xFFFFFFFF, 2, b"xyz"), (2, 0, b"AB")]
        expected = struct.pack("<H7I", 2, 5, 0xFFFFFFFF, 2, 3, 2, 0, 2) + b"ABxyz"
        self.assertEqual(write_wsx(rows), expected)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.wsx"
            path.write_bytes(expected)
            entries = sorted(parse_wsx(path)["entries"], key=lambda row: row["index"])
            self.assertEqual([(row["hash"], row["unk"], row["blob"]) for row in entries], rows)

    def test_changed_member_is_written(self):
        rows = [(0xFFFFFFFF, 2, b"xyz"), (2, 0, b"AB")]
        changed = relayout([(0xFFFFFFFF, 2, b"xyz"), (2, 0, b"ABC")])
        self.assertEqual(changed, [(0xFFFFFFFF, 3, b"xyz"), (2, 0, b"ABC")])
        rebuilt = write_wsx(changed)
        self.assertNotEqual(rebuilt, write_wsx(rows))
        reread = sorted(parse_wsx_bytes(rebuilt)["entries"], key=lambda row: row["index"])
        self.assertEqual([row["blob"] for row in reread], [b"xyz", b"ABC"])
        mutation_check(rows)

    def test_rejects_a_gap(self):
        with self.assertRaises(ValueError):
            write_wsx([(1, 1, b"missing byte first")])


@unittest.skipUnless(find_library("lzo2"), "requires liblzo2")
class LzoRoundTrip(unittest.TestCase):
    def test_group_continuation_and_texture_container(self):
        encode, decode = lzo_encoder(), lzo_decoder()
        # Two synthetic member spans occupy one stored LZO group.
        decoded = b"ABCD" + b"efghi"
        packed = encode(decoded)
        header = struct.pack("<7I", 0, 38, 0x100, 0x120, 32, len(packed), 2).ljust(0x100, b"\0")
        lm = header + struct.pack("<8I", 0, 4, 0, len(packed), 4, 5, 1, 0) + packed
        rebuilt, groups, members = write_light_map(lm, encode, decode)
        self.assertEqual((groups, members), (1, 2))
        self.assertEqual(struct.unpack_from("<I", rebuilt, 0x110)[0], 4)
        texture = struct.pack("<2I", len(decoded), len(packed)) + packed + b"\0" * 4
        rebuilt, blocks = write_texture(texture, encode, decode)
        self.assertEqual(blocks, [decoded])
        self.assertEqual(decode(rebuilt[8:-4], len(decoded)), decoded)
        lzo_mutation_check(lm, encode, decode)


class SaveRoundTrip(unittest.TestCase):
    def test_untouched_packets_and_recomputed_level_directory(self):
        from dataclasses import replace
        from lol3_save_header import parse_header
        from lol3_save_writer import SYNTHETIC_FLAGS as flags, read_slot, synthetic_slot, write_slot
        slot = synthetic_slot()
        origin = write_slot(slot)
        self.assertEqual(read_slot(origin, *flags), slot)
        level = replace(slot.levels[0], sections=(b"more raw bytes",) + slot.levels[0].sections[1:])
        changed = replace(slot, levels=(level,) + slot.levels[1:])
        rewritten = write_slot(changed)
        self.assertEqual(read_slot(rewritten, *flags), changed)
        old_directory = parse_header(origin, len(origin))
        directory = parse_header(rewritten, len(rewritten))
        self.assertEqual(directory["levels"][0][1] - old_directory["levels"][0][1], len(b"more raw bytes") - 3)
        a, n = directory["preview"]
        self.assertEqual(rewritten[a:a + n], origin[a:a + n])

    def test_reject_truncated_packed_chunk(self):
        from lol3_save_writer import read_packed
        with self.assertRaises(ValueError):
            read_packed(struct.pack("<2I", 1, 4) + b"!")

    def test_header_edit_reads_back_through_the_save_header_reader(self):
        from dataclasses import replace
        from lol3_save_header import report
        from lol3_save_writer import SYNTHETIC_FLAGS, read_slot, synthetic_slot, write_slot
        slot = synthetic_slot()
        origin = write_slot(slot)
        positions = (slot.positions[0], slot.positions[1] + 0x10000) + slot.positions[2:]
        edited = write_slot(replace(slot, positions=positions))
        self.assertEqual(len(edited), len(origin))
        self.assertEqual([at for at in range(len(origin)) if origin[at] != edited[at]], [0x49E])
        self.assertIn(f"player +0x49c: x {positions[1]} ", report(edited))
        self.assertEqual(read_slot(edited, *SYNTHETIC_FLAGS).positions, positions)
