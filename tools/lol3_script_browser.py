#!/usr/bin/env python3
"""Read a LoL3 MAP's script commands and the native-effect page.

  lol3_script_browser.py --data DAT QWOD0
  lol3_script_browser.py --data DAT --check

A summary: one line per opcode that occurs in that level's object stream and
one line per opcode in its region stream. It does not list each command, and
it does not print dialogue tags or other operand text. Subcommand tables
(class, creature, effect, region flags) stay on the opcode page. Nothing is
written unless --out is given, and that path must be outside the game tree
and this repository.

Meanings are the native-effect sentences on the opcode page, one line each.
"""
from cli_errors import run_cli
from collections import Counter
from pathlib import Path

import lol3_cli
from lol3_script_framing import level_map_entries, map_range, native_sizes

# Shortened meanings (leading sentences, nothing added) from the opcode page's native-effect column.
MEANINGS = {
    0x01: "Calls target vtable +0xC0 with the command.",
    0x02: "For +4 = 2 or 3, resolves the object from +1/u16 +2 and calls player helper 0x415540 or 0x415620. Other values route to player command 0x410AA0.",
    0x03: "Calls target vtable +0xC0 and keeps its result.",
    0x05: "Calls target virtual +0xC8 with u8 +4 and +5.",
    0x06: "Runs the object action switch on +4 through 0x446290, table 0x446438.",
    0x07: "Calls target virtual +0xCC with u8 +4/+5.",
    0x08: "The object table slot reaches the common exit without a command body.",
    0x09: "Dispatches object property u8 +4 through 0x447680 and table 0x447AE0.",
    0x0B: "Passes u16 +4 to 0x4EED60. That helper is a bare return in this executable.",
    0x0D: "Calls target virtual +0xC0 with the complete command.",
    0x0E: "Selects kind-2 timer by u8 +6, then uses u8 +4 as the operation 0-6 and +5 as its argument.",
    0x0F: "Builds a point 10 fixed-point world units ahead of the target and a second point from selector +5/u16 +6, then reads action +4.",
    0x10: "Writes command u8 +4 to object state +0x31.",
    0x11: "Adds command s8 +4 to unsigned object state +0x31 and clamps to 0-255.",
    0x12: "Uses a sequence slot at 0x600828. With flag +0xA bit 0x20, resets progress, clears the slot and sends value 6 to the object matcher.",
    0x13: "Fills and submits a hit request using two mask words, magnitude u8 +8 and mode +9.",
    0x14: "Passes u16 resource ID +4, current object and a pointer to +6 to 0x422C40.",
    0x15: "Passes unsigned bytes +4 and +5 to the indexed function 0x46FA60. The first argument indexes the movie-stem table at 0x46FCF2.",
    0x16: "Compares the identifier at +4 against active object/queue identifiers. The admitted branch uses command +8 to +0x0B as a dialogue tag.",
    0x17: "Writes the low byte of 0x44AA40(0, (u8(+4) << 5) + 31) shifted right five to object +0x31.",
    0x18: "Checks flag 4 in byte 0x58C562 and current object 0x5896F4, then normally calls 0x422FA0 with +4/+6.",
    0x19: "Reads three dwords at +4/+8/+0xC. Value 5 at +0xC selects 0x434560, otherwise calls 0x434180.",
    0x1A: "When 0x600854 is zero, resolves the pair +8/+0xC and calls 0x48EBE0 with the object, +4/+0x10 and pointers +0x14/+0x1D.",
    0x1B: "Queue marker or continuation. Subcommand +8 takes the four-arm switch at 0x449C84.",
    0x1C: "Gates on 0x600854. It allocates 0x146 bytes from heap 0x660CA4, builds a type-5 object of vtable 0x5392C8 (0x4B1BA0) at the target's position, then sets its fields from the command. Its visible role is UNCONFIRMED.",
    0xC4: "Animates the floor or ceiling height of the 56-byte map region selected by u16 +2.",
    0xC5: "Selects a map region with u16 +2 and switches on +4 to edit region flags or an associated table row.",
    0xC6: "Stores byte +5 to the level array at index +4.",
    0xC7: "Stores byte +5 to the shared array at index +4.",
    0xC8: "Writes a bounded RNG result to shared-array index +4.",
    0xC9: "Writes a bounded RNG result to level-array index +4.",
    0xCC: "Uses s16 +4 to select a region update (-1 or -2) or an 8-byte auxiliary row store.",
    0xCD: "The map-side table reaches the common return, with no body.",
    0xCE: "Adds s8 +5 at shared-array index +4 and clamps to 0-255.",
    0xCF: "Adds s8 +5 at level-array index +4 and clamps to 0-255.",
    0xD0: "Selects one of five branches by +4.",
    0xD1: "Uses u16 +2 to find a 44-byte region-group row, directly or via selector 0x90 and the 56-byte region table.",
    0xD2: "Uses +4 to dispatch through the settings table 0x4E6CD8, reading u8 +5 in the arms that +4 selects.",
    0xF0: "At group entry, byte +4 counts following records for the native size walker.",
}
# QWOD0 histograms from the retail object and region streams.
QWOD0_OBJECT = {
    0x02: 11, 0x03: 6, 0x05: 24, 0x07: 2, 0x09: 33, 0x0E: 4, 0x10: 4,
    0x14: 20, 0x15: 2, 0x16: 5, 0xC5: 6, 0xC7: 1, 0xD2: 2, 0xF0: 44,
}
QWOD0_REGION = {0x09: 37, 0xF0: 5}


def opcode_counts(stream, sizes):
    """Count commands in one stream. Operand bytes are not returned."""
    counts = Counter()
    at = 0
    view = memoryview(stream)
    while at < len(view):
        opcode = view[at]
        length = sizes.get(opcode)
        if length is None or at + length > len(view):
            raise ValueError(f"invalid command at stream offset {at:#x}")
        if opcode not in MEANINGS:
            raise ValueError(f"opcode {opcode:#x} has no page meaning")
        counts[opcode] += 1
        at += length
    return counts


def summary_text(stem, object_stream, region_stream, sizes):
    """One heading and one line per opcode that occurs, for each stream."""
    lines = []
    for space, stream in (("object", object_stream), ("region", region_stream)):
        counts = opcode_counts(stream, sizes)
        lines.append(f"{stem} {space} commands: {sum(counts.values()):,}")
        for opcode in sorted(counts):
            lines.append(f"0x{opcode:02X} {counts[opcode]:,}: {MEANINGS[opcode]}")
    return "\n".join(lines) + "\n"


def level_summary(stem, payload, sizes):
    return summary_text(stem, map_range(payload, 0x44, 0x8C), map_range(payload, 0x3C, 0x84), sizes)


def _payload(data_dir, stem):
    found = [item for item in level_map_entries(data_dir) if item[0] == stem]
    if len(found) != 1:
        raise ValueError(f"expected one MAP for {stem}")
    return found[0][2]


def check_line(data_dir):
    sizes = native_sizes((Path(data_dir).resolve().parent / "LOL3.DAT").read_bytes())
    if set(sizes) != set(MEANINGS):
        missing = sorted(set(sizes) - set(MEANINGS))
        extra = sorted(set(MEANINGS) - set(sizes))
        raise ValueError(f"page meanings and the size table differ: missing {missing}, extra {extra}")
    payload = _payload(data_dir, "QWOD0")
    object_counts = opcode_counts(map_range(payload, 0x44, 0x8C), sizes)
    region_counts = opcode_counts(map_range(payload, 0x3C, 0x84), sizes)
    text = level_summary("QWOD0", payload, sizes)
    if dict(object_counts) != QWOD0_OBJECT or dict(region_counts) != QWOD0_REGION:
        raise ValueError(f"QWOD0 histograms differ: object {dict(object_counts)} region {dict(region_counts)}")
    for counts in (object_counts, region_counts):
        for opcode, count in counts.items():
            if f"0x{opcode:02X} {count:,}: {MEANINGS[opcode]}" not in text:
                raise ValueError(f"QWOD0 summary dropped opcode {opcode:#x}")
    return (f"CHECK script_browser: QWOD0 object {sum(object_counts.values()):,} commands "
            f"in {len(object_counts)} opcodes, region {sum(region_counts.values()):,} commands "
            f"in {len(region_counts)} opcodes; each line is that opcode's page meaning")


def main():
    parser = lol3_cli.tool_args(
        __doc__, out_help="write the summary to this file, outside the game tree and this repository")
    parser.add_argument("level", nargs="?", help="level archive stem, for example QWOD0")
    args = parser.parse_args()
    if args.check and args.out:
        parser.error("--check writes nothing")
    if args.check:
        try:
            print(check_line(args.data))
        except (OSError, ValueError) as error:
            parser.exit(1, f"CHECK script_browser FAILED: {error}\n")
        return 0
    if not args.level:
        parser.error("give a level stem, or --check")
    try:
        data_dir = Path(args.data).resolve()
        sizes = native_sizes((data_dir.parent / "LOL3.DAT").read_bytes())
        text = level_summary(args.level.upper(), _payload(data_dir, args.level.upper()), sizes)
    except (OSError, ValueError) as error:
        parser.exit(1, f"script browser: {error}\n")
    if args.out:
        output = Path(args.out).resolve()
        game = data_dir.parent
        repo = Path(__file__).resolve().parents[1]
        if output == game or game in output.parents:
            parser.error("--out must be outside the game tree")
        if output == repo or repo in output.parents:
            parser.error("--out must be outside the repository")
        output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
