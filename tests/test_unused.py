"""Compare the unused-opcode summary with the measured opcode table."""
from pathlib import Path
import re
import unittest

DOCS = Path(__file__).resolve().parents[1] / "docs"


class UnusedClaims(unittest.TestCase):
    def test_opcode_summary(self):
        reference = (DOCS / "lol3-script-opcodes.md").read_text(encoding="utf-8")
        table = reference.split("## Per-class effects")[0]
        rows = re.findall(r"^\| 0x([0-9A-F]+) \| \d+ \| [^|]+\| ([\d,]+) \|", table, re.M)
        absent = {int(code, 16) for code, count in rows if count == "0"}
        page = (DOCS / "UNUSED.md").read_text(encoding="utf-8")
        summary = page.split("## Opcodes absent")[1].split("## Development options")[0]
        documented = {int(code, 16) for code in re.findall(r"^\| `0x([0-9A-F]+)` \|", summary, re.M)}
        used, total = map(int, re.search(r"use (\d+) of the (\d+) values", summary).groups())
        self.assertEqual(total, len(rows))
        self.assertEqual(used, total - len(absent))
        self.assertEqual(documented, absent)
