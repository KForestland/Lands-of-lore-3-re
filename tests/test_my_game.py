"""Use invented names and records to exercise the LoL3 guide."""
from base64 import b64decode
from dataclasses import replace
from gzip import decompress
from hashlib import sha256
from pathlib import Path
import re
import struct
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from tests.kit_fixture import geometry, make_fixture
from extract_wsx_entries import wsx_name_hash
from lol3_text_writer import write_trr
from lol3_save_writer import Packed, synthetic_slot, write_slot
from lol3_wsx_writer import write_wsx
from my_game import app
from my_game_ui import GameFolderError


def archive(path, entries):
    rows, cursor = [], 0
    for name, blob in entries:
        key = wsx_name_hash(name) if isinstance(name, str) else name
        rows.append((key, cursor, blob))
        cursor += len(blob)
    path.write_bytes(write_wsx(rows))


def make_my_game_fixture(game):
    make_fixture(game)
    data = game / "DAT"
    definitions = bytearray(0x204 + 2 * 139)
    struct.pack_into("<I", definitions, 4, 0x204)
    struct.pack_into("<I", definitions, 0x34, 2)
    for number, at in enumerate((0x204, 0x204 + 139), 1):
        struct.pack_into("<I", definitions, at + 0x18, 100 + number)
        struct.pack_into("<I", definitions, at + 0x73, number)
    definitions[0x204 + 139 + 0x3F] = 2
    archive(data / "GLOBAL.WSX", [("GLOBAL\\GLOBAL.ODF", definitions)])
    archive(data / "locallng.wsx", [
        ("f_automp.trr", write_trr([(10002, b"Test Cavern")])),
        ("itemjt.trr", write_trr([(1, b"ABCDTest Compass"), (2, b"ABCDTest Flash")])),
        ("monster.trr", write_trr([(3, b"\x020\x031Test Drake\r")])),
    ])

    image = bytearray(0x147138 + 27 * 20 + 40)
    image[:2] = b"MZ"
    position = len(image) - 40
    struct.pack_into("<I", image, 0x147138 + 27 * 2, position - 0x143800 + 0x545000)
    name = b"levels\\qwod0\\qwod0\0"
    image[position:position + len(name)] = name
    (game / "LOL3.DAT").write_bytes(image)

    level = bytearray(geometry())
    start, = struct.unpack_from("<I", level, 0x20)
    struct.pack_into("<I", level, start + 0x20, 101)
    struct.pack_into("<I", level, 0x44, len(level))
    struct.pack_into("<I", level, 0x8C, 32)
    level.extend(struct.pack("<BBBBI8x", 3, 1, 0, 0, 101))
    level.extend(struct.pack("<BBBBI8x", 3, 16, 0, 0, 101))
    struct.pack_into("<I", level, 0x4C, len(level))
    struct.pack_into("<I", level, 0x98, 8)
    level.extend(struct.pack("<II", 0, 16))
    archive(data / "QWOD0.WSX", [("LEVELS\\QWOD0\\QWOD0.MAP", level), (1, b"x"), (2, b"y"), (3, b"z")])


def check_page(page):
    plans = re.findall(r'data-svg-gzip="([^"]+)"', page)
    assert len(plans) == 1
    svg = decompress(b64decode(plans[0])).decode("utf-8")
    assert "<svg" in svg and "Test Cavern (QWOD0)" in svg
    for label in ("<h3>Test Cavern (QWOD0)</h3>", "Test Compass", "Test Flash", "Test Drake", "Placed item 1",
                  "count placed items from 1",
                  "Grant to the player, script record 1"):
        assert label in page, label
    assert "script record 2" not in page


class MyGame(unittest.TestCase):
    def test_fault_report_includes_only_requested_save_values(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            game = root / "fixture"
            make_my_game_fixture(game)
            slot = synthetic_slot()
            sections = list(slot.sections)
            sections[23] = Packed(((8, struct.pack("<ii", ~35, ~1)),))
            sections[36] = Packed(((8, struct.pack("<II", 5, 2)),))
            source = root / "Do not include this filename.000"
            raw = write_slot(replace(slot, sections=tuple(sections)))
            source.write_bytes(raw)
            index = app.faults.index("Solved quests in the journal")
            digest = sha256((game / "LOL3.DAT").read_bytes()).hexdigest()
            with patch("my_game_faults.RETAIL_PE", digest), patch("my_game_faults.decompressor", return_value=lambda packet, size: packet):
                text, omitted = app.read_saved(source, game, index)
            self.assertIn("Saved level: 2", text)
            self.assertIn("Quest 35, journal category 5: 5", text)
            self.assertIn("The save has no journal entry for quest 12.", omitted)
            self.assertNotIn("Quest 1,", text)
            self.assertNotIn("Fixture", text)
            self.assertNotIn(source.name, text)
            self.assertEqual(source.read_bytes(), raw)

    def test_page_shows_placements_and_eligible_grants(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            game = root / "fixture"
            make_my_game_fixture(game)
            original = {path: path.read_bytes() for path in game.rglob("*") if path.is_file()}
            out = app.write_page(game / "DAT", root / "page.html", open_page=False)
            check_page(out.read_text(encoding="utf-8"))
            with self.assertRaisesRegex(ValueError, "outside the game folder"):
                app.write_page(game, game / "page.html", open_page=False)
            self.assertEqual({path: path.read_bytes() for path in game.rglob("*") if path.is_file()}, original)

    def test_empty_folder_is_refused(self):
        with TemporaryDirectory() as temp:
            with self.assertRaisesRegex(GameFolderError, app.wrong_folder):
                app.write_page(Path(temp), open_page=False)
