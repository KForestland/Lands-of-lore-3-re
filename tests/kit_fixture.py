"""Make a tiny synthetic WSX installation with editable LoL3 records."""
from io import BytesIO
import struct
import wave

from tests.test_modkit import make_game
from tests.test_save_edit import GROUP, source_slot
from extract_wsx_entries import wsx_name_hash
from lol3_text_writer import write_trr
from lol3_wsx_writer import write_wsx

DATA = "DAT"
LEVEL = "QWOD0"
ARCHIVE = "DAT/locallng.wsx"
JOBS = ("level", "text", "translate", "music", "model", "movie", "sound", "save", "patch", "mod")
TRANSLATE_FROM = "Insert the disc"
SAVE_FIELD = "heading"
SAVE_AT = GROUP + 8


def geometry():
    vertex, surface = 0x244, 0x264
    prop, control, item = surface + 56, surface + 93, surface + 126
    raw = bytearray(item + 37)
    fields = {0: 38, 4: vertex, 0x50: 4, 8: surface, 0x0C: surface, 0x58: 1,
              0x44: len(raw), 0xBC: len(raw), 0xC8: surface, 0xDC: surface,
              0x14: prop, 0x60: 1, 0x18: control, 0x64: 1, 0x20: item, 0x6C: 1}
    for offset, value in fields.items():
        struct.pack_into("<I", raw, offset, value)
    for index, (x, z) in enumerate(((0, 0), (10, 0), (10, 10), (0, 10))):
        struct.pack_into("<ii", raw, vertex + 8 * index, x << 16, z << 16)
    struct.pack_into("<8H", raw, surface + 8, *([0xFFFF] * 4), 0, 1, 2, 3)
    struct.pack_into("<H", raw, surface + 0x1E, 0xFFFF)
    raw[surface + 0x22] = 0xFF
    struct.pack_into("<H", raw, surface + 0x2A, 12)
    for index, at in enumerate((prop, control, item), 2):
        struct.pack_into("<hh", raw, at, index, index + 1)
    return bytes(raw)


def make_fixture(game):
    game.mkdir()
    make_game(game)
    payload = geometry()
    material_start = 0x98
    odf = bytearray(material_start + 24)
    struct.pack_into("<II", odf, 0, 38, material_start)
    struct.pack_into("<I", odf, 0x3C, 1)
    struct.pack_into("<h", odf, material_start + 4, 7)
    map_key = wsx_name_hash("LEVELS\\QWOD0\\QWOD0.MAP")
    odf_key = wsx_name_hash("LEVELS\\QWOD0\\QWOD0.ODF")
    end = len(payload) + len(odf)
    rows = [(map_key, 0, payload), (odf_key, len(payload), odf),
            (2, end, b"x"), (3, end + 1, b"y")]
    (game / DATA / "QWOD0.WSX").write_bytes(write_wsx(rows))
    archive = game / DATA / "locallng.wsx"
    text = write_trr([(42, b"A made-up forest")])
    from extract_wsx_entries import parse_wsx_bytes
    original = parse_wsx_bytes(archive.read_bytes())["entries"]
    rows = [(row["hash"], row["offset"] - 6 - 12 * len(original), row["blob"]) for row in original]
    rows.append((wsx_name_hash("qtext.trr"), sum(len(row[2]) for row in rows), text))
    archive.write_bytes(write_wsx(rows))
    return source_slot()


def foreign_level_edit():
    from level_edit import document

    return document(LEVEL, b"a different map", [])


def inspect_jobs(test):
    out = test.root / "obj"
    test.assertIn("1 face", test.job("model", "--data", test.data, "--level", LEVEL, "--out", out))
    model = (out / "QWOD0.obj").read_text(encoding="ascii")
    test.assertIn("# texture-ref 0:7 none 12", model)
    test.assertIn("f 1/1 4/2 3/3 2/4", model)
    test.assertIn("A made-up forest", test.job("text", "--data", test.game, "qtext.trr", "--id", "42"))

    game = test.root / "Media fixture"
    data = game / DATA
    data.mkdir(parents=True)
    with BytesIO() as buffer:
        with wave.open(buffer, "wb") as audio:
            audio.setparams((1, 1, 8000, 2, "NONE", "not compressed"))
            audio.writeframes(b"xy")
        wav = buffer.getvalue()
    key = wsx_name_hash("MUSIC\\TEST.aud")
    (data / "MUSIC1.WSX").write_bytes(write_wsx([(key, 0, wav)]))
    offset = 0x148180
    image = bytearray(offset + 4 * 40)
    struct.pack_into("<40I", image, offset, *([0x401800 + len(image)] * 40))
    (game / "LOL3.DAT").write_bytes(image + b"TEST\0")
    if test.lowercase:
        lowercase(game)
    test.assertIn("channels 1 rate 8000 align 1 bits 8 stem TEST", test.job("music", "--data", data))
    test.assertIn("Entry    0", test.job("sound", "--data", data, "--list", "--file", "MUSIC1.WSX"))


def lowercase(root):
    """Rename a generated installation as a lower-case filesystem copy."""
    for path in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        lower = path.with_name(path.name.lower())
        if lower.name != path.name:
            # The intermediate name also makes a case-only rename portable.
            temporary = path.with_name(path.name + ".renaming")
            path.rename(temporary)
            temporary.rename(lower)
