import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from lol3_map_writer import emit, field_bytes, read_command, read_fields, rebuild, retained_spans, waypoints, write_command


def synthetic_map():
    raw = bytearray(0x2CF)
    for at, value in {4: 0x248, 8: 0x295, 0x0C: 0x2A0, 0x14: 0x2AA,
                      0x44: 0x2A0, 0x4C: 0x2A6, 0x60: 1, 0x8C: 6,
                      0x98: 4, 0xC4: 1, 0xC8: 0x250, 0xCC: 0x244,
                      0xD8: 1, 0xDC: 0x272}.items():
        struct.pack_into("<I", raw, at, value)
    raw[0x244:0x248] = b"test"
    struct.pack_into("<hhHBB", raw, 0x250, -8, 6, 0xFFFF, 2, 5)
    raw[0x258:0x272] = b"x" * 26
    struct.pack_into("<HBB", raw, 0x272, 0, 1, 1)
    raw[0x276:0x295] = b"y" * 31
    raw[0x2A0:0x2A6] = b"\x10\x02\x00\x00\x2a\x35"
    struct.pack_into("<hh", raw, 0x2AA, -9, 20)
    return raw


class MapWriteTests(unittest.TestCase):
    def test_signed_operand_and_stored_tail(self):
        raw = b"\xcf\xa0\x20\x01\x03\xff"
        row = read_command(raw)
        self.assertEqual(row["operands"], (3, -1))
        row["operands"] = (4, -2)
        self.assertEqual(write_command(row, {0xCF: 6}), raw[:4] + b"\x04\xfe")

    def test_field_bytes_leave_out_stored_bytes(self):
        self.assertEqual(field_bytes("6sH"), 2)
        self.assertEqual(field_bytes("I4s"), 4)
        self.assertEqual(field_bytes(""), 0)

    def test_round_trip_with_labels_paths_and_placement(self):
        raw = synthetic_map()
        self.assertEqual(waypoints(raw)[1], [(-8, 6, 0xFFFF, 2, 5)])
        self.assertEqual([len(body) for _, _, body in retained_spans(raw)], [4, 26, 31, 0])
        result, counts, seen = rebuild(raw, {0x10: 6})
        self.assertEqual(result, raw)
        self.assertEqual(counts["placements"], 1)
        self.assertEqual(seen, {0x10})
        # command 4 + 1 operand byte, waypoint row 8, path row 4, placement X/Z 4
        self.assertEqual(counts["field bytes"], 21)

    def test_edited_fields_change_only_their_bytes(self):
        raw = synthetic_map()
        fields = read_fields(raw, {0x10: 6})
        fields["commands"]["object"][1][0]["operands"] = (3,)
        fields["waypoints"][1][0] = (-7, 6, 0xFFFF, 2, 5)
        rows = fields["placements"]["type 3"][1]
        rows[0] = (-9, 21, rows[0][2])
        changed = emit(raw, fields, {0x10: 6})
        self.assertEqual([at for at in range(len(raw)) if raw[at] != changed[at]], [0x250, 0x2A4, 0x2AC])
        self.assertEqual(waypoints(changed)[1], [(-7, 6, 0xFFFF, 2, 5)])
