"""File reader commands report bad inputs without Python tracebacks."""
import json
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

    def test_missing_optional_texture_cache(self):
        # The shipped seed must not be picked up as a game-written cache.
        (self.data / "cdcache.wsx").write_bytes(b"shipped seed")
        for name in ("texture_spans", "texture_palettes", "texture_png"):
            tool = f"lol3_{name}.py"
            with self.subTest(tool=tool):
                run = subprocess.run(
                    [sys.executable, str(TOOLS / tool), "--data", str(self.data), "--check"],
                    cwd=self.root, env=self.env, capture_output=True, text=True, timeout=10,
                )
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertEqual(run.stderr, "")
                self.assertEqual(len(run.stdout.splitlines()), 1)
                self.assertTrue(run.stdout.startswith(f"CHECK {name}: SKIP: no game-written cdcache.wsx"))
                self.assert_bad(tool, "--data", self.data, "--check", "--cache", self.root / "wrong.wsx")

    def test_save(self):
        self.bad_files("SAVE.000", b"short", "lol3_save_header.py", "--data", self.data, self.data / "SAVE.000")


class OutputGuard(unittest.TestCase):
    """No tool writes into the game data (the --data folder, a folder holding a WSX archive or
    LOL3.DAT, or anything below one); the entry extractor also refuses the repository."""

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.game = self.root / "GAME"
        self.data = self.game / "DAT"
        self.data.mkdir(parents=True)
        (self.game / "LOL3.DAT").write_bytes(b"MZ")
        (self.data / "TEST.WSX").write_bytes(struct.pack("<HI3I", 1, 4, 0x1234, 0, 4) + b"abcd")
        self.loose = self.root / "LOOSE"
        (self.loose / "SUB").mkdir(parents=True)
        (self.loose / "fake.wsx").write_bytes(b"")
        self.repo = TOOLS.parent
        self.env = {key: value for key, value in os.environ.items()
                    if key not in ("LOL1_DATA", "LOL2_DAT", "LOL3_DAT")}

    def run_tool(self, tool, *args):
        return subprocess.run([sys.executable, str(TOOLS / tool), *map(str, args)], cwd=self.root,
                              env=self.env, capture_output=True, text=True, timeout=20)

    def assert_refused(self, targets, tool, *args):
        for target in targets:
            with self.subTest(tool=tool, target=target):
                run = self.run_tool(tool, *[target if a is None else a for a in args])
                self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
                self.assertIn("give an output path outside", run.stderr)
                self.assertNotIn("Traceback", run.stderr)
                self.assertFalse(target.exists())

    def game_targets(self, name):
        return (self.loose / name, self.loose / "SUB" / name, self.data / name,
                self.game / name, self.game / "SAVEGAME" / name)

    def test_output_refusal(self):
        sys.path.insert(0, str(TOOLS))
        try:
            from cli_errors import output_refusal
        finally:
            sys.path.remove(str(TOOLS))
        outside = self.root / "out" / "x.png"
        for target in self.game_targets("x.png"):
            with self.subTest(target=target):
                self.assertIsNotNone(output_refusal(target, self.data))
        self.assertIsNotNone(output_refusal(self.root / "elsewhere", [None, self.root / "elsewhere"]))
        self.assertIsNone(output_refusal(outside, self.data))
        self.assertIsNone(output_refusal(self.repo / "docs" / "x.md", self.data))
        self.assertIsNotNone(output_refusal(self.repo / "docs" / "x.md", self.data, repository=True))
        self.assertIsNone(output_refusal(outside, self.data, repository=True))

    def test_shared_parser_refuses_game_folders(self):
        self.assert_refused(self.game_targets("sheets"), "lol3_level_report.py", "--data", self.data, "--out", None)
        lmf = self.root / "A.LMF"
        lmf.write_bytes(b"")
        self.assert_refused(self.game_targets("lmf.json"), "walk_lmf_leaves.py", lmf, "-o", None)
        self.assert_refused(self.game_targets("manifest.json"), "extract_wsx_entries.py", "--data", self.data,
                            "--out", self.root / "entries", "--manifest", None)
        self.assertFalse((self.root / "entries").exists())

    def test_extracted_entries_refuse_game_and_repository(self):
        targets = (*self.game_targets("entries"), self.repo / "no-such-folder")
        self.assert_refused(targets, "extract_wsx_entries.py", "--data", self.data, "--stems", "TEST", "--out", None)
        fine = self.root / "entries"
        manifest = self.root / "manifest.json"
        run = self.run_tool("extract_wsx_entries.py", "--data", self.data, "--stems", "TEST",
                            "--out", fine, "--manifest", manifest)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual([path.read_bytes() for path in (fine / "TEST").iterdir()], [b"abcd"])
        self.assertEqual(json.loads(manifest.read_text())[0]["stem"], "TEST")
