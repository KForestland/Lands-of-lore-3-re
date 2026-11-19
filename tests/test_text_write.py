import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from lol3_text_writer import read_trr, write_trr


class TextWriteTests(unittest.TestCase):
    def test_id_order_and_boundary_after_variable_length_edit(self):
        rows = [(32, b"AbCd"), (10, b""), (32, b"first\x07second")]
        self.assertEqual(read_trr(write_trr(rows)), rows)
        changed = rows[:2] + [(32, b"ab")]
        result = write_trr(changed)
        self.assertEqual(read_trr(result), changed)
        self.assertEqual(struct.unpack_from("<4I", result, 16), (28, 33, 34, 37))
        self.assertEqual(len(result), 41)

    def test_embedded_nul(self):
        with self.assertRaisesRegex(ValueError, "NUL"):
            write_trr([(1, b"two\0fields")])
        with self.assertRaisesRegex(ValueError, "invalid text"):
            read_trr(write_trr([(1, b"abcd")])[:-1] + b"x")
