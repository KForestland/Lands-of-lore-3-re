#!/usr/bin/env python3
"""Describe original LoL3 script records and their event references.

  lol3_script_notes.py --data DAT --out DIR    # full local notes outside the checkout
  lol3_script_notes.py --data DAT --summary DIR # reproduce the small summaries
  lol3_script_notes.py --data DAT --check     # verify the checked-in summaries
  lol3_script_notes.py --data DAT --timers QWOD0
"""
from collections import Counter, defaultdict
from pathlib import Path
from struct import error as struct_error, iter_unpack, unpack_from

import lol3_cli
from lol3_script_framing import GROUP_HEADER, level_map_entries, map_range, native_sizes, u32

STREAMS = {
    "object": (0x44, 0x8C, 0x40, 0x88),
    "region": (0x3C, 0x84, 0x38, 0x80),
}
MATCHERS = {
    2: (0x4F1AD0, "timer expires"),
    3: (0x4A8240, "object event"),
    4: (0x4A84FB, "object request"),
    5: (0x4A82DE, "object event and value"),
    6: (0x4A8A48, "object value"),
    7: (0x4A8B09, "threshold test"),
    8: (0x4A8D25, "object word"),
    9: (0x4A8C4E, "hit filter"),
    10: (0x4A8EB2, "object selector and event"),
    11: (0x4AC4F2, "region event"),
    12: (0x4AC252, "conditional region event"),
    15: (0x4AC650, "region comparison"),
    21: (0x4A9088, "object event"),
    22: (0x4A8DDE, "identifier match"),
}
TARGETS = {1: "player", 2: "creature", 3: "object pool 3", 4: "object pool 4",
           0x10: "object pool 0x10", 0x20: "object pool 0x20",
           0x90: "region", 0xC0: "bound object"}
EFFECTS = {
    0x01: ("pass the command to virtual slot +0xC0", 0x447F31),
    0x02: ("submit a player action", 0x447FB0),
    0x03: ("pass an item grant to virtual slot +0xC0", 0x448020),
    0x05: ("submit two operands to virtual slot +0xC8", 0x447E3E),
    0x06: ("select an object action", 0x446290),
    0x07: ("submit two operands to virtual slot +0xCC", 0x447E66),
    0x09: ("set an object property through its subcommand", 0x447680),
    0x0D: ("pass the command to virtual slot +0xC0", 0x447F31),
    0x0E: ("apply a timer action", 0x446760),
    0x0F: ("build two positions and apply an object action", 0x4484B7),
    0x10: ("set object state byte", 0x447F49),
    0x11: ("add a signed value to object state (clamp to 0–255)", 0x447F8F),
    0x12: ("submit a sequence update", 0x447E9B),
    0x13: ("submit a scripted hit", 0x4E7290),
    0x14: ("submit an audio resource ID", 0x422C40),
    0x15: ("submit an indexed request", 0x46FA60),
    0x16: ("request dialogue audio and look up its four-character tag", 0x448271),
    0x17: ("store the shifted RNG result in object state", 0x447F6C),
    0x18: ("submit the alternate audio request", 0x422FA0),
    0x19: ("look up a quest row by ID", 0x434560),
    0x1A: ("resolve a target and submit an object setup request", 0x4482F8),
    0x1B: ("process queued commands or resume a group", 0x449912),
    0x1C: ("allocate and configure an effect object", 0x44838C),
    0xC4: ("select a region geometry update", 0x4E5EC0),
    0xC5: ("select a region flag update", 0x4E5D30),
    0xC6: ("set a level byte", 0x4E5BD0),
    0xC7: ("set a shared byte", 0x4E5C30),
    0xCC: ("update a region or auxiliary row", 0x4E63C0),
    0xCE: ("add a signed value to a shared byte (clamp to 0–255)", 0x4E5C50),
    0xCF: ("add a signed value to a level byte (clamp to 0–255)", 0x4E5BF0),
    0xD0: ("run a duration or region operation", 0x4E66D0),
    0xD2: ("select a settings operation", 0x4E6A80),
}
ARRAY_TARGETS = {0xC6: "level", 0xC7: "shared", 0xCE: "shared", 0xCF: "level"}
OBJECT_OPS = {1, 3, 5, 6, 7, 9, 13, 14, 15, 16, 17, 19, 20, 23, 24}
EXCERPT_LEVEL = "CKEEP"
EXCERPT_SIZE = 18

def word(data, at):
    return unpack_from("<H", data, at)[0]


def decode_events(data, starts, offsets, pool_base):
    events, by_index = Counter(), defaultdict(list)
    at = 0
    while at < len(data):
        size, kind = data[at:at + 2]
        if size < 2 or at + size > len(data):
            raise ValueError(f"invalid event length at {pool_base + at:#x}")
        events[kind] += 1
        if kind in MATCHERS:
            operand = word(data, at + 2)
            if offsets is not None and operand >= len(offsets):
                raise ValueError(f"event index out of range at {pool_base + at:#x}")
            source = offsets[operand] if offsets is not None else operand
            if source not in starts:
                raise ValueError(f"event at {pool_base + at:#x} references a non-command")
            guard = None
            if at + size + 4 <= len(data) and data[at + size + 1] == 19:
                guard = word(data, at + size + 2)
            row = data[at:at + size]
            if kind in (11, 12):
                match = f"region {word(row, 4)} receives event {row[6]}"
            elif kind == 15:
                match = f"region {word(row, 4)} passes comparison mode {row[6]}"
            elif kind == 2:
                match = "timer expires"
            elif kind in (3, 5, 6, 21):
                match = f"{MATCHERS[kind][1]} {row[4]}"
            else:
                match = MATCHERS[kind][1]
            if guard is not None:
                match += f" and guard {guard} passes"
            by_index[source].append(f"{match} at 0x{pool_base + at:X}")
        at += size
    return events, by_index


def command(row):
    opcode = row[0]
    if opcode == GROUP_HEADER:
        return "embedded group header reaches the high range exit", "none"
    effect, va = EFFECTS[opcode]
    target = "runtime context"
    if opcode in ARRAY_TARGETS:
        target = f"{ARRAY_TARGETS[opcode]} byte {row[4]}"
        value = row[5]
        if opcode in (0xCE, 0xCF) and value >= 128:
            value -= 256
        effect += f" ({value})"
    elif opcode in OBJECT_OPS:
        target = TARGETS.get(row[1], f"selector 0x{row[1]:X}")
        if row[1] not in (1, 0xC0):
            target += f" {word(row, 2)}"
        if opcode in (9, 14, 16, 17):
            effect += f" (operand {row[4]})"
    elif opcode in (0xC4, 0xC5):
        target = f"region {word(row, 2)}"
    elif opcode == 0x19 and u32(row, 12) == 5:
        target = f"quest row {u32(row, 4)}"
    return f"{effect} (code 0x{va:X})", target


def walk(payload, map_base, space, native_lengths):
    loc, size, event_loc, event_size = STREAMS[space]
    stream = map_range(payload, loc, size)
    starts = []
    at = 0
    while at < len(stream):
        length = native_lengths.get(stream[at])
        if length is None or at + length > len(stream):
            raise ValueError(f"invalid {space} command at stream offset {at:#x}")
        starts.append(at)
        at += length
    boundaries = set(starts)
    offsets = ([row[0] for row in iter_unpack("<I", map_range(payload, 0x4C, 0x98))]
               if space == "object" else None)
    if offsets is not None and set(offsets) != boundaries:
        raise ValueError("object index differs from framed boundaries")
    pool = map_range(payload, event_loc, event_size)
    counts, events = decode_events(pool, boundaries, offsets, map_base + u32(payload, event_loc))
    aliases = defaultdict(list)
    for index, position in enumerate(offsets or ()):
        aliases[position].append(index)
    base = map_base + u32(payload, loc)
    return stream, starts, base, counts, events, aliases


def lines(walked):
    stream, starts, base, _, events, aliases = walked
    for index, start in enumerate(starts):
        length = 1
        if stream[start] == GROUP_HEADER:
            length = stream[start + 4]
            if index + length >= len(starts):
                raise ValueError(f"group at {base + start:#x} ends outside its stream")
            first = index + 1
        else:
            first = index
        actions, targets = [], []
        for position in starts[first:first + length]:
            effect, target = command(stream[position:])
            actions.append(effect)
            targets.append(target)
        when = " or ".join(events.get(start, ())) or "UNCONFIRMED producer"
        does = " → ".join(actions) or "empty group"
        touches = ", ".join(dict.fromkeys(targets)) or "no explicit target"
        ids = ", ".join(str(i) for i in aliases.get(start, ()))
        label = f"index {ids}, " if ids else ""
        yield start, f"- {label}`0x{base + start:X}` — *When* {when}. *Does* {does}. *Touches* {touches}.\n"


def summarize(stem, walks, predicates):
    lines = [f"# {stem} script summary", "",
             f"**CONFIRMED.** Record counts in `{stem}.WSX` come from the two native "
             "streams and their event pools. See the [reader](../../lol3-script-events.md).", "",
             "| Stream | First file offset | Bytes | Records | Group headers | Direct event rows |",
             "|---|---:|---:|---:|---:|---:|"]
    for space, (stream, starts, base, counts, events, _) in walks.items():
        headers = sum(stream[at] == GROUP_HEADER for at in starts)
        refs = sum(len(x) for x in events.values())
        lines.append(f"| {space} | `0x{base:X}` | {len(stream):,} | {len(starts):,} | {headers:,} | {refs:,} |")
    lines.extend(("", f"The predicate count at MAP +0xB8 is {predicates}.", "",
                  "| Event pool | Kind | Count | Native matcher |",
                  "|---|---:|---:|---|"))
    for space, (_, _, _, counts, _, _) in walks.items():
        for kind, count in sorted(counts.items()):
            evidence = f"`0x{MATCHERS[kind][0]:X}`" if kind in MATCHERS else "structural row"
            lines.append(f"| {space} | {kind} | {count:,} | {evidence} |")
    return "\n".join(lines) + "\n"


def _inside(path, folder):
    """True when path lies inside folder (Path.is_relative_to needs Python 3.9)."""
    try:
        path.relative_to(folder)
        return True
    except ValueError:
        return False


def timer_lines(stem, walks):
    """Kind 2 is the timer matcher. Other kinds stay in the written summary."""
    lines = [f"{stem} timers"]
    for space, walked in walks.items():
        lines.append(f"{space} kind 2 timer expires: {walked[3][2]}")
    return "\n".join(lines) + "\n"


def main():
    parser = lol3_cli.tool_args(__doc__, out_help="external directory for full listings")
    parser.add_argument("--summary", type=Path, help="write the small checked-in notes")
    parser.add_argument("--timers", help="print one level's kind-2 timer counts")
    args = parser.parse_args()
    if args.timers:
        if args.check or args.out or args.summary:
            parser.error("--timers only prints")
        try:
            data_dir = Path(args.data).resolve()
            sizes = native_sizes((data_dir.parent / "LOL3.DAT").read_bytes())
            stem = args.timers.upper()
            found = [item for item in level_map_entries(data_dir) if item[0] == stem]
            if len(found) != 1:
                raise ValueError(f"expected one MAP for {stem}")
            _name, map_base, payload = found[0]
            walks = {space: walk(payload, map_base, space, sizes) for space in STREAMS}
            print(timer_lines(stem, walks), end="")
        except (OSError, ValueError, KeyError, struct_error) as error:
            parser.exit(1, f"script notes: {error}\n")
        return 0
    if sum(bool(x) for x in (args.check, args.out, args.summary)) != 1:
        parser.error("choose --check, --out DIR or --summary DIR")
    try:
        data_dir = Path(args.data).resolve()
        root = Path(__file__).resolve().parents[1]
        output = Path(args.out).resolve() if args.out else args.summary
        if args.out and (_inside(output, root) or _inside(output, data_dir.parent)):
            raise ValueError("full listings require a directory outside this checkout and the game folder")
        if output:
            output.mkdir(parents=True, exist_ok=True)
        sizes = native_sizes((data_dir.parent / "LOL3.DAT").read_bytes())
        totals = Counter()
        for stem, map_base, payload in level_map_entries(data_dir):
            walks = {space: walk(payload, map_base, space, sizes) for space in STREAMS}
            summary = summarize(stem, walks, u32(payload, 0xB8))
            small = {f"{stem}.md": summary}
            for space, data in walks.items():
                totals[space] += len(data[1])
                totals[space + " events"] += sum(len(rows) for rows in data[4].values())
                if args.check:
                    if sum(1 for _ in lines(data)) != len(data[1]):
                        raise ValueError(f"{stem} {space} script listing count differs")
                if args.out:
                    with (output / f"{stem}.{space}.script-list.md").open("w", encoding="utf-8") as file:
                        file.write(f"# {stem} {space} script records\n\n")
                        for _, line in lines(data):
                            file.write(line)
            if stem == EXCERPT_LEVEL:
                walked = walks["object"]
                sample = [line for at, line in lines(walked) if at in walked[4]][:EXCERPT_SIZE]
                small[f"{stem}.excerpt.md"] = (
                    f"# {stem} script excerpt\n\nThe first {len(sample)} directly referenced object "
                    "script entries. Offsets are absolute in the original WSX. "
                    "[Summary](CKEEP.md), [schema](README.md).\n\n" + "".join(sample))
            for filename, body in small.items():
                if args.check and (root / "docs/levels/notes" / filename).read_text() != body:
                    raise ValueError(f"stale summary or excerpt: {filename}")
                if args.summary:
                    (output / filename).write_text(body, encoding="utf-8")
            totals["levels"] += 1
        if totals["levels"] != 18 or totals["object"] != 54_940 or totals["region"] != 4_040:
            raise ValueError("retail script counts differ")
        if (totals["object events"], totals["region events"]) != (16_876, 2_201):
            raise ValueError("retail event counts differ")
        print(f"CHECK script_notes: {totals['levels']} level summaries, "
              f"{totals['object']:,} object and {totals['region']:,} region records, "
              f"{totals['object events']:,}/{totals['region events']:,} direct object/region references")
        return 0
    except (OSError, ValueError, KeyError, struct_error) as error:
        parser.exit(1, f"script notes: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
