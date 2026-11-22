"""Use invented names and records to exercise the LoL3 guide."""
from pathlib import Path
import struct
from tempfile import TemporaryDirectory
import unittest

from tests.kit_fixture import geometry, make_fixture
from extract_wsx_entries import wsx_name_hash
from lol3_text_writer import write_trr
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
    assert page.count("data:image/svg+xml;base64,") == 1
    for label in ("Test Cavern", "Test Compass", "Test Flash", "Test Drake", "Placed item 1",
                  "Grant to the player, script record 1"):
        assert label in page, label
    assert "script record 2" not in page


class MyGame(unittest.TestCase):
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
