"""Make an offline guide from a player's copy of Lands of Lore III."""
from collections import defaultdict
from struct import iter_unpack, unpack_from

from edition import identify, WITNESSES
from game_names import creature_journal, creature_tags, level_names
from level_edit_data import item_catalogue
from level_html import find_data
from lol3_level_schematic import PLACEMENTS, map_geometry, schematic_svg
from lol3_script_framing import level_maps, map_range
from my_game_faults import FAULT_NAMES, saved_report
from my_game_ui import MyGame, catalogue, edition_label, report


TITLE = "Lands of Lore III · My Game"
ITEM_PLACEMENTS = next(row for row in PLACEMENTS if row[0] == "item")


def item_records(raw):
    _, start_field, count_field, width, _ = ITEM_PLACEMENTS
    start, = unpack_from("<I", raw, start_field)
    count, = unpack_from("<I", raw, count_field)
    for row in range(count):
        identity, = unpack_from("<I", raw, start + width * row + 0x20)
        yield identity, f"Placed item {row + 1}"

    stream = map_range(raw, 0x44, 0x8C)
    index = map_range(raw, 0x4C, 0x98)
    starts = sorted({at for at, in iter_unpack("<I", index)})
    if bool(stream) != bool(starts) or (starts and (starts[0] != 0 or starts[-1] >= len(stream))):
        raise ValueError("invalid script command index")
    recipients = {1: "Grant to the player", 2: "Grant to a creature", 192: "Possible grant to the current object"}
    for row, (start, end) in enumerate(zip(starts, starts[1:] + [len(stream)]), 1):
        if end - start != 16 or stream[start] != 3:
            continue
        recipient = recipients.get(stream[start + 1])
        if recipient:
            identity, = unpack_from("<I", stream, start + 4)
            yield identity, f"{recipient}, script record {row}"


def game_page(folder):
    data = find_data(folder, "DAT", "QWOD0.WSX")
    names = level_names(data)
    items, spells = {}, {}
    for identity, _, name, flags in item_catalogue(data):
        if name:
            (spells if flags & 2 else items)[identity] = name
    if not names or not items or not spells:
        raise ValueError("missing game name tables")
    edition = edition_label(data, identify, WITNESSES, "Windows layout (exact version unverified)")

    maps, locations = [], defaultdict(list)
    for stem, raw in level_maps(data):
        name = f"{names[stem]} ({stem})" if stem in names else stem
        image = schematic_svg(name, *map_geometry(raw)).encode("utf-8")
        maps.append((stem, name, image, "svg+xml"))
        for identity, label in item_records(raw):
            locations[identity].append((name, label))
    if not maps:
        raise ValueError("missing level maps")

    creatures = sorted({name for _, name in creature_journal(data)}, key=str.casefold)
    creature_source = "Names from the game's creature journal."
    if not creatures:
        creatures = sorted({tag for stem, *_ in maps for tag in creature_tags(data, stem).values()}, key=str.casefold)
        creature_source = "Names from the stored creature definitions."

    def names_table(key, title, values, description=""):
        return key, title, catalogue(key, title, ("Name",), ((name,) for name in values), description)

    tables = (
        names_table("items", "Items", sorted(items.values(), key=str.casefold)),
        names_table("spells", "Spells", sorted(spells.values(), key=str.casefold)),
        names_table("creatures", "Creatures", creatures, creature_source),
    )
    heading = "Where is it?"
    rows = ((name, area, record) for key, name in sorted(items.items(), key=lambda row: row[1].casefold())
            for area, record in (locations[key] or [("—", "No placement or grant recorded in these levels.")]))
    found = catalogue("where", heading, ("Item", "Area", "Record"), rows,
                      "This table and the plans count placed items from 1. The research notes count them "
                      "from 0, so placed item 4 here is item 3 in the notes. "
                      "Script grants can depend on what you do in the game.")
    return report(TITLE, edition, maps, tables, extras=(("where", heading, found),))


app = MyGame("LoL3 My Game", TITLE, "Lands of Lore III", "DAT", game_page,
             read_saved=saved_report, faults=FAULT_NAMES)


if __name__ == "__main__":
    raise SystemExit(app.main())
