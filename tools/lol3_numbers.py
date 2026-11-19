#!/usr/bin/env python3
"""Generate the LoL3 numeric reference from the original program and WSX files."""
from hashlib import sha256
from pathlib import Path
from struct import unpack_from

from cli_errors import run_cli
from extract_wsx_entries import wsx_name_hash
import lol3_cli
from lol3_combat_census import ITEM_ROWS, ITEM_STRIDE, ITEM_TABLE, global_wsx
from lol3_media_check import read_at, wsx_rows
from lol3_script_framing import RETAIL_PE

PAGE = Path(__file__).resolve().parents[1] / "docs" / "NUMBERS.md"


def table(columns, rows):
    return "\n".join(["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
                     + ["| " + " | ".join(map(str, row)) + " |" for row in rows])


def item_rows(archive):
    relative = unpack_from("<I", archive, 0x3866 + 4)[0]
    count = unpack_from("<I", archive, 0x3866 + 0x34)[0]
    if (0x3866 + relative, count) != (ITEM_TABLE, ITEM_ROWS):
        raise ValueError("unexpected GLOBAL.ODF item table")
    for i in range(count):
        at = ITEM_TABLE + ITEM_STRIDE * i
        row = archive[at:at + ITEM_STRIDE]
        key = unpack_from("<I", row, 0x73)[0]
        flags = unpack_from("<I", row, 0x3F)[0]
        identity = unpack_from("<I", row, 0x18)[0]
        handler = "—" if flags & 2 else unpack_from("<I", row, 0x4B)[0]
        cost = unpack_from("<I", row, 0x5B)[0] if flags & 2 else "—"
        step = unpack_from("<H", row, 0x7D)[0]
        yield (i, f"`+0x{at:X}`", f"`{key:#x}`", f"`{identity:#010x}`", f"`{flags:#x}`", handler, cost, step)


def spell_rows(archive):
    relative, count = unpack_from("<II", archive, 0x16BE53 + 4)
    if (relative, count) != (412, 28):
        raise ValueError("unexpected SPELL.ODF table")
    base = 0x16BE53 + relative
    for i in range(count):
        at = base + 87 * i
        identity = unpack_from("<I", archive, at + 0x18)[0]
        yield (i + 1, f"`+0x{at:X}`", f"`{identity:#010x}`", archive[at + 0x2E])


def creature_rows(data):
    for path in lol3_cli.wsx_files(data):
        with path.open("rb") as file:
            if file.read(2) != b"\x04\0":
                continue
            file.seek(0)
            stem = path.stem.upper()
            key = wsx_name_hash(f"LEVELS\\{stem}\\{stem}.ODF")
            directory = wsx_rows(file)
            for stored, offset, length in directory:
                if stored != key:
                    continue
                odf = read_at(file, offset, length)
                start = unpack_from("<I", odf, 0x10)[0]
                count = unpack_from("<I", odf, 0x48)[0]
                if start + 147 * count > len(odf):
                    raise ValueError(f"{stem} creature table outside ODF")
                for slot in range(count):
                    at = start + 147 * slot
                    hp = unpack_from("<H", odf, at + 0x63)[0]
                    strength = odf[at + 0x81]
                    selectors = " ".join(f"{byte:02X}" for byte in odf[at:at + 4])
                    pairs = unpack_from("<8H", odf, at + 4)
                    masks = " ".join(f"{a:04X}/{b:04X}" for a, b in zip(pairs[::2], pairs[1::2]))
                    yield (stem, slot, f"`+0x{offset+at:X}`", hp, strength, max(1, strength // 10),
                           strength // 2, selectors, masks)


def render(data):
    program = (data.parent / "LOL3.DAT").read_bytes()
    if sha256(program).hexdigest() != RETAIL_PE:
        raise ValueError("the report requires the documented English retail LOL3.DAT")
    archive = global_wsx(data)
    items = list(item_rows(archive))
    spells = list(spell_rows(archive))
    creatures = list(creature_rows(data))
    if len(creatures) != 334:
        raise ValueError("expected 334 creature definitions")
    effect = 0x14A760
    magnitude = [(i, value, f"`+0x{effect+i:X}`")
                 for i, value in enumerate(unpack_from("<9b", program, effect))]
    return "\n\n".join([
        "# LoL3 numbers at a glance",
        "Generated from the English retail program and archives by `tools/lol3_numbers.py`. Numeric identifiers and byte offsets identify each record.",
        "## Item definitions",
        "The loader reads the 343 item rows of 139 bytes through `0x44057A–0x44059F` and `0x4ACCCE–0x4ACD17`. Fields +0x73 and +0x18 are distinct lookup columns ([definition fields](lol3-item-dispatch.md#definition-directory)). Bit 1 of +0x3F sends a definition to the special cast arm instead of the regular handler index at +0x4B ([use effects](lol3-item-dispatch.md#use-effects)). On the special cast path, `0x4A4547–0x4A4564` reads +0x5B as the base cost, before cast gates and discounts ([cast cost](lol3-spell-dispatch.md#player-cast-and-cost)). The last column is the disk u16 at +0x7D; for a nonzero value v the loader stores max(1, floor(256/v)) (`0x4ACE1B–0x4ACE3E`, [definition fields](lol3-item-dispatch.md#definition-directory)). **UNCONFIRMED.** What the +0x7D value counts in play. Test: break at `0x492319` and note the player action. **UNCONFIRMED.** No per-item scalar damage or armour is proven for the full table. Test: follow the regular handler and the equipment cases into a resolved hit packet before assigning those values.",
        table(("Row", "GLOBAL.WSX", "Key +73", "Identity +18", "Flags +3F", "Regular handler", "Special +5B", "Disk +7D"), items),
        "## Spell effects",
        "The 28 records of 87 bytes follow the spell ODF header; the loader at `0x440667–0x440685` takes their offset and count from it. Definition lookup compares +0x18 at `0x440990–0x4409B4`, and the frame rebinder reads the frame count at +0x2E at `0x4B4390–0x4B43B4` ([spell effect table](lol3-spell-dispatch.md#definition-tables)). The special-definition cost inputs are in the item table above.",
        table(("Row (1-based)", "GLOBAL.WSX", "Identity", "Frame count"), spells),
        "The first-hit path at `0x4C462E–0x4C463D` reads one signed magnitude per variant from this table; the resolver can change the eventual loss ([first hit](lol3-spell-dispatch.md#effect-object-and-first-hit)).",
        table(("Variant", "Magnitude", "LOL3.DAT"), magnitude),
        "## Creature definitions by level (field-3 type rows, not placements; a few tags are objects)",
        "Header words +0x10 and +0x48 of each level ODF locate these 147-byte rows ([creature records](lol3-map-odf-readers.md#creature-definitions-in-field-3)). The first 20 bytes hold the selectors and hexadecimal mask pairs of the mitigation records ([mitigation records](lol3-combat-dispatch.md#where-the-mitigation-records-come-from)). **CONFIRMED.** The constructor copies definition +0x63 to the health ceiling +0x108 (`0x4B479E–0x4B47A2`); the setter clamps health to it ([creature definitions](lol3-combat-dispatch.md#creature-definitions-and-target-quantity)). **CONFIRMED.** On the setup path `0x4B48D6–0x4B48F4`, helper `0x4F1220–0x4F122A` returns half of byte +0x81, rounded down, for actor +0xFA. Actor +0xF7 can reduce this result by its integer quarter (`0x4B48FA–0x4B4903`). A kind-1 animation hit multiplies +0xFA by the frame percentage (`0x4B6F6A–0x4B7044`, only with actor +0x110 bit 0x800000 and byte `0x7D75F2` nonzero; [animation hits](lol3-combat-dispatch.md#creature-animation-hits-and-resolver-multipliers)). The reader derives byte +0x82 = max(1, floor(+0x81/10)) (`0x4F0E60–0x4F0E7B`). **UNCONFIRMED.** What byte +0x82 is used for. Test: in a running level, set a read watchpoint on +0x82 of one creature's 139-byte runtime definition row and note the reading address.",
        table(("Level", "ODF slot", "WSX offset", "HP cap", "Base +81", "Derived +82", "Base +FA", "Selectors", "Mask pairs"), creatures),
    ]) + "\n"


def main():
    parser = lol3_cli.tool_args(__doc__, out_help="write the generated Markdown page")
    args = parser.parse_args()
    if args.check and args.out:
        parser.error("--check reads only")
    page = render(Path(args.data).resolve())
    if args.check:
        if PAGE.read_text(encoding="utf-8") != page:
            raise ValueError("docs/NUMBERS.md differs from the original tables")
        print("CHECK lol3_numbers: LoL3 tables match docs/NUMBERS.md")
    elif args.out:
        Path(args.out).write_text(page, encoding="utf-8")
    else:
        print(page, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
