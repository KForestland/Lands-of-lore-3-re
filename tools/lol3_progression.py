#!/usr/bin/env python3
"""Read LoL3 MAP scripts to tabulate each portal and its guard.

Opcode 2 with byte +4 equal to 27 or 76 is the player arm at 0x410F98.
Byte +5 stores a level-table index in the low 5 bits and a second argument
in the high 3 bits. The guard is the kind-19 predicate on the one event
that names that command or its group header; earlier rows the walker tries
first are listed and combined into the condition that takes the row. A
level-to-level section and the steps from QWOD0 follow the table.

  lol3_progression.py --data DAT              # print the page
  lol3_progression.py --data DAT --out FILE   # write the page
  lol3_progression.py --check --data DAT      # docs/PROGRESSION.md equals the page
"""
from cli_errors import run_cli
import os
import re
from collections import Counter, defaultdict, deque, namedtuple
from pathlib import Path
from struct import error as struct_error, iter_unpack, unpack_from

import lol3_cli
from lol3_level_report import DATA_BIAS, level_path_stems
from lol3_script_framing import GROUP_HEADER, level_map_entries, map_range, native_sizes, u32
from lol3_script_notes import MATCHERS, STREAMS, walk, word

PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "PROGRESSION.md")
TABLE_FILE = 0x147138
RECORD = 27
PORTAL_SUBS = (27, 0x4C)
OPS = ("==", "!=", "<=", ">=", ">", "<", "and", "or")


def level_names(image):
    """Stem by row of the 27-byte table at file 0x147138 (VA 0x548938)."""
    names = {}
    for index in range(21):
        rec = image[TABLE_FILE + index * RECORD:TABLE_FILE + (index + 1) * RECORD]
        if len(rec) != RECORD:
            raise ValueError("level table is short")
        pointer = u32(rec, 0)
        at = pointer - DATA_BIAS
        if pointer == 0 or not 0 <= at < len(image):
            names[index] = None
            continue
        end = image.find(b"\x00", at)
        text = image[at:end]
        prefix = b"levels\\"
        if not text.startswith(prefix) or not text.endswith(text[len(prefix):].split(b"\\")[-1]):
            raise ValueError(f"level name {index} is not levels\\stem\\stem")
        parts = text.decode("ascii").split("\\")
        if len(parts) != 3 or parts[1] != parts[2]:
            raise ValueError(f"level name {index} is not levels\\stem\\stem")
        names[index] = parts[1]
    if names[0] is not None or names[20] is not None:
        raise ValueError("level table rows 0 and 20 are not empty")
    if u32(image, TABLE_FILE) == 0 or u32(image, TABLE_FILE + 20 * RECORD) != 0:
        raise ValueError("level table row 0 is a null pointer or row 20 is not")
    stems = [names[index] for index in range(1, 20)]
    if len(stems) != 19 or len(set(stems)) != 19 or set(stems) != set(level_path_stems(image)):
        raise ValueError("level table differs from the path list")
    return names


def decode(predicates, index, seen):
    if index in seen:
        return f"predicate {index} again"
    if index >= len(predicates):
        raise ValueError(f"predicate {index} is outside the table")
    row = predicates[index]
    if len(row) != 5 or row[0] > 7:
        raise ValueError(f"predicate {index} is not a 5-byte operator 0-7")

    def operand(side, kind, arg):
        if kind == 0:
            return str(arg)
        if kind == 2 and side == "L" and arg == 0:
            return "object+0x1C bit 0x80000"
        if kind == 2:
            return f"shared {arg}"
        if kind == 3:
            return f"level {arg}"
        if kind == 4:
            return decode(predicates, arg, seen | {index})
        if kind == 5:
            return "object+0x31"
        raise ValueError(f"predicate {index} operand type {kind}")

    return f"({operand('L', row[1], row[2])} {OPS[row[0]]} {operand('R', row[3], row[4])})"

def operand_key(kind, arg, side):
    if kind == 0:
        return None
    if kind == 2 and side == "L" and arg == 0:
        return "object+0x1C bit 0x80000"
    if kind == 2:
        return f"shared {arg}"
    if kind == 3:
        return f"level {arg}"
    if kind == 5:
        return "object+0x31"
    return None


def variables(predicates, index, seen=frozenset()):
    """Names of the stored bytes a predicate reads, following type-4 operands."""
    if index in seen or index >= len(predicates):
        raise ValueError(f"predicate {index} loops or is outside the table")
    row = predicates[index]
    found = set()
    for side, kind, arg in (("L", row[1], row[2]), ("R", row[3], row[4])):
        if kind == 4:
            found |= variables(predicates, arg, seen | {index})
        elif kind not in (0, 2, 3, 5):
            raise ValueError(f"predicate {index} operand type {kind}")
        else:
            key = operand_key(kind, arg, side)
            if key:
                found.add(key)
    return found


def evaluate(predicates, index, env):
    """The kind-19 evaluator 0x4F02B0 for one assignment of the stored bytes (env)."""
    row = predicates[index]

    def value(side, kind, arg):
        if kind == 0:
            return arg
        if kind == 4:
            return evaluate(predicates, arg, env)
        return env[operand_key(kind, arg, side)]

    left, right = value("L", row[1], row[2]), value("R", row[3], row[4])
    op = row[0]
    return int((left == right, left != right, left <= right, left >= right, left > right, left < right,
                bool(left) and bool(right), bool(left) or bool(right))[op])


def ranges(name, values):
    """'shared 9 ≤ 1 or ≥ 6' from a set of byte values."""
    if not values:
        return "never"
    if len(values) == 256:
        return "always"
    runs, start = [], None
    for v in range(257):
        if v in values and start is None:
            start = v
        if v not in values and start is not None:
            runs.append((start, v - 1))
            start = None
    parts = []
    for low, high in runs:
        if low == high:
            parts.append(f"= {low}")
        elif low == 0:
            parts.append(f"≤ {high}")
        elif high == 255:
            parts.append(f"≥ {low}")
        else:
            parts.append(f"{low}–{high}")
    return f"{name} " + " or ".join(parts)


def event_text(kind, row):
    """Every byte the matcher compares, by kind."""
    if kind == 11:
        return f"region {word(row, 4)} kind 11 event {row[6]}"
    if kind == 12:
        return f"region {word(row, 4)} kind 12 event {row[6]} cond {row[7]}"
    if kind == 15:
        return f"region {word(row, 4)} kind 15 mode {row[6]} source {row[7]} value {word(row, 8)}"
    if kind == 2:
        return "kind 2 timer"
    if kind == 4:
        return f"kind 4 mode {row[4]} invert {row[5]} value 0x{unpack_from('<I', row, 6)[0]:08X}"
    if kind in (5, 6):
        return f"kind {kind} event {row[4]} value {row[5]}"
    if kind in (3, 21):
        return f"kind {kind} event {row[4]}"
    if kind == 22:
        return "kind 22 name " + bytes(row[4:]).split(b"\x00")[0].decode("ascii")
    raise ValueError(f"event kind {kind} has no matcher description")


def competes(space, earlier, later):
    """True when the walker for later's kind can take earlier first for an input later accepts."""
    kind = later.kind
    if earlier.kind != kind:
        return False
    a, b = earlier.row, later.row
    if space == "region":
        if kind == 12 and b[6] == 2 and a[6] == 6:
            return True  # 0x4AC2FB: event byte 6 matches input 2 for any region
        return word(a, 4) == word(b, 4) and a[6] == b[6]
    if kind == 5:  # 0x4A82DE-0x4A82FD: value 0xFF on either side matches any nonzero value
        return a[4] == b[4] and (a[5] == b[5] or 0xFF in (a[5], b[5]))
    if kind == 6 and b[4] == 20:  # 0x4A888F-0x4A88A6: value 0 on either side matches any value
        return a[4] == 20 and (a[5] == b[5] or 0 in (a[5], b[5]))
    if kind == 6:  # generic walker 0x4A87B5-0x4A87C0 compares event byte +4 only
        return a[4] == b[4]
    if kind == 22:
        return bytes(a[4:]).split(b"\x00")[0] == bytes(b[4:]).split(b"\x00")[0]
    if kind == 4:
        if bytes(a[4:]) == bytes(b[4:]):
            raise ValueError("a kind-4 portal event has an identical earlier row; kind-4 order is not traced")
        return False
    raise ValueError(f"no first-match rule for kind {kind}")


Event = namedtuple("Event", "kind row guard list at")


def structured_events(payload, space, starts):
    """Matcher rows keyed by the command offset they name, plus every row of the pool in order."""
    _loc, _size, event_loc, event_size = STREAMS[space]
    pool = map_range(payload, event_loc, event_size)
    offsets = ([item[0] for item in iter_unpack("<I", map_range(payload, 0x4C, 0x98))]
               if space == "object" else None)
    boundaries = set(starts)
    found = defaultdict(list)
    ordered = []
    at = 0
    number = 0
    while at < len(pool):
        size, kind = pool[at:at + 2]
        if size < 2 or at + size > len(pool):
            raise ValueError(f"invalid event length at stream {space} offset {at:#x}")
        if kind == 0:
            number += 1
        if kind in MATCHERS:
            operand = word(pool, at + 2)
            if offsets is not None and operand >= len(offsets):
                raise ValueError(f"event index out of range at stream {space} offset {at:#x}")
            source = offsets[operand] if offsets is not None else operand
            if source not in boundaries:
                raise ValueError(f"event at stream {space} offset {at:#x} references a non-command")
            guard = None
            if at + size + 4 <= len(pool) and pool[at + size + 1] == 19:
                guard = word(pool, at + size + 2)
            event = Event(kind, bytes(pool[at:at + size]), guard, number, at)
            found[source].append(event)
            ordered.append((source, event))
        at += size
    return found, ordered


def taken_when(predicates, own, earlier):
    """Own guard and the guards of rows the walker tries first, as one condition."""
    guards = [own] + [guard for _, guard in earlier]
    if any(guard is None for _, guard in earlier):
        return "never (an earlier row with no guard matches first)"
    if not earlier:
        if own is None:
            return "upstream: no guard here"
        names = variables(predicates, own)
        if len(names) == 1:
            name = next(iter(names))
            return ranges(name, {v for v in range(256) if evaluate(predicates, own, {name: v})})
        return decode(predicates, own, set())
    names = set()
    for guard in guards:
        if guard is not None:
            names |= variables(predicates, guard)
    if len(names) == 1:
        name = next(iter(names))
        values = {v for v in range(256)
                  if (own is None or evaluate(predicates, own, {name: v}))
                  and not any(evaluate(predicates, guard, {name: v}) for _, guard in earlier)}
        return ranges(name, values)
    text = "none" if own is None else decode(predicates, own, set())
    return text + " and not " + " and not ".join(decode(predicates, guard, set()) for _, guard in earlier)


def collect(data_dir):
    image = (Path(data_dir).resolve().parent / "LOL3.DAT").read_bytes()
    names = level_names(image)
    sizes = native_sizes(image)
    by_stem = {stem: index for index, stem in names.items() if stem}
    rows = []
    archives = []
    for stem, _map_base, payload in level_map_entries(data_dir):
        archives.append(stem)
        count, start = u32(payload, 0xB8), u32(payload, 0xBC)
        end = start + count * 5
        if start < 0x244 or end > len(payload):
            raise ValueError(f"{stem} predicate table runs outside the MAP")
        predicates = [payload[start + index * 5:start + index * 5 + 5] for index in range(count)]
        for space in STREAMS:
            stream, starts, _base, _counts, walked, _aliases = walk(payload, 0, space, sizes)
            events, ordered = structured_events(payload, space, starts)
            if {key: len(value) for key, value in events.items()} != {key: len(value) for key, value in walked.items()}:
                raise ValueError(f"{stem} {space} event join differs from the script notes")
            index_of = {at: index for index, at in enumerate(starts)}
            group_of = {}
            for at in starts:
                if stream[at] != GROUP_HEADER:
                    continue
                length = stream[at + 4]
                index = index_of[at]
                members = starts[index + 1:index + 1 + length]
                if len(members) != length:
                    raise ValueError(f"{stem} {space} group at {at} ends outside its stream")
                for member in members:
                    # A later header is the inner group. The event names that header.
                    group_of[member] = at
            for at in starts:
                if stream[at] != 2 or stream[at + 4] not in PORTAL_SUBS:
                    continue
                if sizes[2] != 6:
                    raise ValueError("opcode 2 is not 6 bytes")
                sub = stream[at + 4]
                packed = stream[at + 5]
                level = (packed & 31) + 2
                arg2 = (packed >> 5) + (8 if sub == 0x4C else 0)
                if names.get(level) is None:
                    raise ValueError(f"{stem} portal at {at} selects empty level row {level}")
                if stream[at + 1] != 1 or word(stream, at + 2) != 0:
                    raise ValueError(f"{stem} portal at {at} is not selector 1 index 0")
                key = group_of.get(at, at)
                linked = events.get(key, [])
                if len(linked) != 1 or (key != at and events.get(at)):
                    raise ValueError(f"{stem} {space} portal at {at} is linked to {len(linked)} events")
                event = linked[0]
                guard = event.guard
                if guard is not None and guard >= 5000:
                    raise ValueError(f"{stem} portal at {at} has guard {guard} of 5000 or more")
                earlier = [(source, other.guard) for source, other in ordered
                           if other.list == event.list and other.at < event.at and competes(space, other, event)]
                rows.append((
                    by_stem[stem.lower()],
                    stem,
                    names[level].upper(),
                    sub,
                    arg2,
                    space,
                    key,
                    at,
                    event_text(event.kind, event.row),
                    "none" if guard is None else decode(predicates, guard, set()),
                    ", ".join(f"{source} " + ("none" if g is None else decode(predicates, g, set()))
                              for source, g in earlier) or "—",
                    taken_when(predicates, guard, earlier),
                ))
    if len(archives) != 18:
        raise ValueError(f"expected 18 MAP archives, found {len(archives)}")
    rows.sort(key=lambda row: (row[0], by_stem[row[2].lower()], row[3], row[4], row[5], row[6], row[7]))
    return [row[1:] for row in rows], archives, names


def slot_counts(rows):
    shared = Counter()
    obj = 0
    for row in rows:
        for number in re.findall(r"\bshared (\d+)", row[8]):
            shared[int(number)] += 1
        obj += len(re.findall(r"object\+0x31", row[8]))
    return shared, obj


def brief(counter):
    if not counter:
        return "none"
    return ", ".join(f"{slot} ({count})" for slot, count in sorted(counter.items()))


def first_visit_pairs(rows):
    """Pairs of rows from one level to one destination that test one byte with == 0 and == 1."""
    tests = defaultdict(set)
    for row in rows:
        for name, literal in re.findall(r"\(((?:shared \d+|level \d+|object\+0x31)) == ([01])\)", row[8]):
            tests[(row[0], row[1], name)].add(literal)
    return sum(values == {"0", "1"} for values in tests.values())


def upstream(row):
    return row[10].startswith("upstream")


def graph(rows, archives, names):
    edges = defaultdict(list)
    for row in rows:
        edges[(row[0], row[1])].append(row)
    out = defaultdict(set)
    for source, target in edges:
        out[source].add(target)
    start = names[0x11].upper()

    def steps(usable):
        depth = {start: 0}
        queue = deque([start])
        while queue:
            here = queue.popleft()
            for there in sorted(out[here]):
                if there not in depth and usable(edges[(here, there)]):
                    depth[there] = depth[here] + 1
                    queue.append(there)
        return depth

    every = steps(lambda group: True)
    guarded = steps(lambda group: any(not upstream(row) for row in group))
    lines = [
        "## Level to level",
        "",
        f"One row per pair of levels joined by at least one portal command. Gate lists the distinct Taken when "
        f"values of those rows. An edge with a row whose gate is upstream says so; that part of its gate is UNCONFIRMED, as above.",
        "",
        "| From | To | Rows | Gate |",
        "|---|---|---:|---|",
    ]
    for source, target in sorted(edges, key=lambda pair: (archives.index(pair[0]), archives.index(pair[1]))):
        group = edges[(source, target)]
        gates = sorted({row[10] for row in group if not upstream(row)})
        mark = "upstream on " + str(sum(upstream(row) for row in group)) + " of the rows" \
            if any(upstream(row) for row in group) else ""
        lines.append(f"| {source} | {target} | {len(group)} | " + "; ".join(gates + ([mark] if mark else [])) + " |")
    lines += [
        "",
        f"Steps from {start}, the level a startup with no saved index loads, along portal commands. "
        "All edges: every portal edge, whatever its gate. Guarded edges only: edges with at least one row whose gate is read here, not upstream. "
        "A step count says only that a chain of portal commands exists; whether their gates can all pass in one game "
        "is UNCONFIRMED (settle it by following the shared bytes the gates read through the commands that write them, "
        "opcodes 0xC7 and 0xCE).",
        "",
        "| Level | Exits to | Entered from | Steps (all edges) | Steps (guarded edges only) |",
        "|---|---|---|---:|---:|",
    ]
    incoming = defaultdict(set)
    for source, target in edges:
        incoming[target].add(source)
    for stem in archives:
        lines.append(f"| {stem} | {', '.join(sorted(out[stem])) or 'none'} | {', '.join(sorted(incoming[stem])) or 'none'} "
                     f"| {every.get(stem, '—')} | {guarded.get(stem, '—')} |")
    reached = sum(stem in every for stem in archives)
    lines += ["", f"{reached} of {len(archives)} levels are reached from {start} along all edges, "
                  f"{sum(stem in guarded for stem in archives)} along guarded edges only.", ""]
    return lines


def level_cell(stem, pending):
    if stem in pending:
        pending.remove(stem)
        return f'<a name="level-{stem.lower()}"></a>[{stem}](levels/{stem}.md)'
    return stem


def check_level_sheets(rows):
    directory = Path(PAGE).parent / "levels"
    mentioned = {stem for row in rows for stem in row[:2]}
    sheets = {path.stem for path in directory.glob("*.md")} - {"README"}
    if sheets != mentioned:
        raise ValueError(f"without a sheet: {sorted(mentioned - sheets)}; "
                         f"without a progression row: {sorted(sheets - mentioned)}")
    for stem in sorted(sheets):
        text = (directory / f"{stem}.md").read_text(encoding="utf-8")
        for link in (f"](../PROGRESSION.md#level-{stem.lower()})", "](../NUMBERS.md)"):
            if link not in text:
                raise ValueError(f"missing {link[2:-1]} link in {stem}.md")
    return len(sheets)


def page(rows, archives, names):
    sources = {row[0] for row in rows}
    silent = [stem for stem in archives if stem not in sources]
    guarded = sum(row[8] != "none" for row in rows)
    after = sum(row[9] != "—" for row in rows)
    up = sum(upstream(row) for row in rows)
    subs = Counter(row[2] for row in rows)
    shared, obj = slot_counts(rows)
    lines = [
        "# Progression",
        "",
        "Made by `tools/lol3_progression.py` from the portal commands in the 18 MAP scripts "
        "([level sheets](levels/README.md)). One row is one opcode-2 command whose byte +4 is 27 or 76. "
        "**CONFIRMED.** The player handler `0x410AA0` jumps through the table at `0x4117D4` by byte +4 "
        "(`0x410B63–0x410B7D`, bound 0x51); entries 27 and 76, and no others, are `0x410F98` "
        "([opcode 0x02](lol3-script-opcodes.md#portal-subcommands-of-opcode-0x02)). "
        "That arm stores `(byte +5 & 31) + 2` at `[0x5D5370]` and `(byte +5 >> 5)`, plus 8 when the subcommand is 76, "
        "at `[0x5D5374]` (`0x410F98–0x410FC3`). When byte `[0x5D5380]` is nonzero it stores nothing and returns "
        "(`0x410FB0–0x410FB8`). After the command group, `0x4E596A–0x4E598A` copies those dwords to `[0x5D5368]` "
        "and `[0x5D536C]` and clears them; the object queue has a second copy of the same code at `0x447C86–0x447CA8`. "
        "`0x46CC2B` passes them to `0x46CCB0`, which passes them to `0x436890`. The first is the level index: "
        "`0x43D7B0` stores it at context +0x76B and reads the name from the 27-byte record at `0x548938`. "
        "The second is forwarded to `0x43D7B0`, and that function does not read it. "
        "Row 0's pointer is not a string in the program, and row 20 is zeros. Row 1 is `aglob`. "
        "Rows 2–19 are the 18 level stems in table order, the same names as the path list. "
        "A startup with no saved index stores the immediate `0x11` (row 17, `qwod0`). "
        "No portal command selects row 1 or row 17. Every portal command has selector 1 and index 0.",
        "",
        "The Event column is the one object or region record that names the command, or the group header that "
        "contains it, with every byte its matcher compares. Group is that record's command offset; Command is the "
        "portal opcode's own offset. Guard is the record's kind-19 predicate, a 5-byte row at MAP +0xBC "
        "([predicates](lol3-script-events.md#predicates-and-global-bytes)); `none` means no predicate trailer. "
        "`shared N` is byte N of `[0x5D54C0]`. A type-4 operand is another row of the same table. "
        "`object+0x31` is the byte at `[0x600850]+0x31`. Each of these guards is a row below 5000, so none is an "
        "item or equipment test. Slot numbers are table indexes, not names.",
        "",
        "**CONFIRMED.** A walker runs only the first row of its list that matches and whose guard passes, then "
        "returns: region kind 12 `0x4AC2F3` → `0x4AC450–0x4AC46E`, object kind 5 `0x4A830A` → `0x4A832E–0x4A8351`. "
        "The kind 11, kind 6 and kind 22 walkers end the same way (`0x4AC515`, `0x4A87CD`, `0x4A88B3`, `0x4A8E25`). "
        "Earlier lists the rows before this one in the same list that the walker can take first for an input this "
        "row accepts: the same region and event byte (or a kind-12 row with event 6, which matches input 2 for any "
        "region, `0x4AC2FB`), the same kind-5 event byte with an equal value or 0xFF on either side, the same kind-6 "
        "event byte (for event 20, an equal value or 0 on either side, `0x4A888F–0x4A88A6`), or the same kind-22 name. "
        "Each is shown as its group offset and guard. Taken when combines this row's guard with NOT each earlier "
        "guard; when they read one byte it is written as the values of that byte that take this row.",
        "",
        "**UNCONFIRMED.** A row with no guard and no earlier row (Taken when `upstream`) runs whenever its event arrives, so its gate is "
        "whatever sends that event (another script command or the program), which is not traced here. Settle it in a "
        "running game with a write breakpoint on `0x410FC3` (the store to `[0x5D5370]`) and the caller chain at the "
        "hit, and statically by finding the callers of the walker for that kind with that event byte.",
        "",
        "Locked doors are not covered by this page: a door inside a level is object state and its own records, not "
        "a portal command, and no portal guard here tests an item key (5000+n) or an equipped item (6000+n). "
        f"First-visit selectors: {first_visit_pairs(rows)} pairs of rows from one level to the same destination test "
        "one byte with == 0 and == 1.",
        "",
        f"{len(rows)} portal commands, {guarded} with a predicate. {after} rows have an earlier row the walker tries "
        f"first; {up} rows have no guard and no earlier row (gate upstream). "
        f"Subcommand 27 on {subs[27]}, subcommand 76 on {subs[0x4C]}. "
        f"Shared slots named in the guards: {brief(shared)}. "
        f"object+0x31 named in the guards: {obj}. "
        "Levels with no portal command: " + (", ".join(silent) if silent else "none") + ".",
        "",
        "| From | To | Sub | Arg2 | Stream | Group | Command | Event | Guard | Earlier | Taken when |",
        "|---|---|---:|---:|---|---:|---:|---|---|---|---|",
    ]
    pending = set(archives)
    for row in rows:
        cells = list(row)
        cells[0] = level_cell(cells[0], pending)
        if row[1] not in sources:
            cells[1] = level_cell(cells[1], pending)
        lines.append("| " + " | ".join(str(part) for part in cells) + " |")
    lines.append("")
    lines += graph(rows, archives, names)
    return "\n".join(lines)


def main():
    parser = lol3_cli.tool_args(__doc__, out_help="write the progression page to this file")
    args = parser.parse_args()
    try:
        rows, archives, names = collect(args.data)
        text = page(rows, archives, names)
    except (OSError, ValueError, KeyError, struct_error) as error:
        parser.exit(1, f"CHECK progression: {error}")
    guarded = sum(row[8] != "none" for row in rows)
    if args.check:
        stored = open(PAGE, encoding="utf-8").read() if os.path.isfile(PAGE) else ""
        if stored != text:
            parser.exit(1, "CHECK progression: docs/PROGRESSION.md differs from the portal table")
        try:
            covered = check_level_sheets(rows)
        except (OSError, ValueError) as error:
            parser.exit(1, f"CHECK progression: {error}")
        print(f"CHECK progression: {len(rows)} portals, {guarded} predicates; docs/PROGRESSION.md matches; {covered} linked level sheets")
        return 0
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(text)
        print(f"wrote {len(rows)} portals, {guarded} predicates to {args.out}")
        return 0
    import sys
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
