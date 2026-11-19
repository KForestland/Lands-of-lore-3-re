"""File reader commands report bad inputs without Python tracebacks."""
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "tools"


class ReaderErrors(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.data = self.root / "data"
        self.data.mkdir()
        self.env = {key: value for key, value in os.environ.items()
                    if key not in ("LOL1_DATA", "LOL2_DAT", "LOL3_DAT")}

    def assert_bad(self, tool, *args):
        run = subprocess.run([sys.executable, str(TOOLS / tool), *map(str, args)],
                             cwd=self.root, env=self.env, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(run.returncode, 0, run.stdout)
        output = run.stderr or run.stdout
        self.assertNotIn("Traceback", run.stdout + run.stderr)
        self.assertEqual(len(output.strip().splitlines()), 1, output)

    def bad_files(self, name, short, tool, *args):
        file = self.data / name
        for kind, content in (("empty", b""), ("short", short)):
            with self.subTest(tool=tool, input=kind):
                file.write_bytes(content)
                self.assert_bad(tool, *args)

    def test_missing_data_folder(self):
        self.assert_bad("check_all.py", "--data", self.root / "missing")
        self.assert_bad("lol3_texture_spans.py", "--data", self.root / "missing", "--check")

    def test_archive(self):
        short = struct.pack("<H4I", 1, 4, 0x1234, 0, 4) + b"x"
        self.bad_files("TEST.WSX", short, "extract_wsx_entries.py",
                       "--data", self.data, "--list", "--stems", "TEST")

    def test_light_map(self):
        self.bad_files("A.LMF", b"Light Map\0", "walk_lmf_leaves.py", self.data / "A.LMF")

    def test_localized_text(self):
        self.bad_files("LOCALLNG.WSX", struct.pack("<HI", 1, 24),
                       "lol3_media_check.py", "--data", self.data, "--trr", "qevent.trr")

    def test_executable(self):
        path = self.root / "LOL3.DAT"
        for content in (b"", b"MZ\x01"):
            path.write_bytes(content)
            with self.subTest(size=len(content)):
                self.assert_bad("lol3_native_checks.py", "--data", self.data, "--list")

    def test_texture_cache(self):
        cache = self.root / "cdcache.wsx"
        record = struct.pack("<IHHIHH", 0x028E, 1, 1, 5, 0, 1)
        for content in (b"", record):
            cache.write_bytes(content)
            with self.subTest(size=len(content)):
                self.assert_bad("lol3_texture_spans.py", "--data", self.data, "--list", 1)

    def test_save(self):
        self.bad_files("SAVE.000", b"short", "lol3_save_header.py", "--data", self.data, self.data / "SAVE.000")
