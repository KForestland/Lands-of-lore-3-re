"""Read LoL3's automap titles, item and spell names, and creature labels."""
from functools import lru_cache
from pathlib import Path
from struct import unpack_from

from cli_errors import ReaderArgumentParser, game_path, run_cli
from extract_wsx_entries import wsx_name_hash
from level_edit_data import entry, item_catalogue
from level_html import find_data
from lol3_cli import DEFAULT_DATA
from lol3_text_writer import read_trr


def localized_names(data, name):
    blob = entry(data, "LOCALLNG.WSX", key=wsx_name_hash(name))
    return dict(read_trr(blob, name)) if blob is not None else {}


@lru_cache(maxsize=1)
def level_names(data):
    path = game_path(data.parent, "LOL3.DAT")
    if not path.is_file():
        return {}
    image = path.read_bytes()
    start = 0x147138
    if len(image) < start + 27 * 20 or image[:2] != b"MZ":
        return {}
    titles = localized_names(data, "f_automp.trr")
    names = {}
    for index in range(2, 20):
        pointer, = unpack_from("<I", image, start + 27 * index)
        at = pointer - 0x545000 + 0x143800
        if not 0 <= at < len(image):
            continue
        parts = image[at:at + 27].partition(b"\0")[0].split(b"\\")
        if len(parts) != 3 or parts[0] != b"levels" or parts[1] != parts[2] or not parts[1].isalnum():
            continue
        # The automap uses the names of the corresponding earlier areas
        # for the two final rows (0x40571B–0x40573B).
        title = titles.get(10000 + {18: 11, 19: 5}.get(index, index))
        if title:
            names[parts[1].decode("ascii").upper()] = title.decode("cp437")
    return names


def creature_tags(data, stem):
    key = wsx_name_hash(f"LEVELS\\{stem}\\{stem}.ODF")
    odf = entry(data, f"{stem}.WSX", key=key)
    if not odf or len(odf) < 0x204:
        return {}
    start, = unpack_from("<I", odf, 0x10)
    count, = unpack_from("<I", odf, 0x48)
    if start < 0x204 or start + 147 * count > len(odf):
        return {}
    tags = {}
    for slot in range(count):
        at = start + 147 * slot + 135
        tag = odf[at:at + 12].partition(b"\0")[0].decode("ascii", "replace")
        if tag and tag.isprintable():
            tags[slot] = tag
    return tags


def creature_journal(data):
    for key, field in localized_names(data, "monster.trr").items():
        if field.startswith(b"\x020\x031"):
            title = field[4:].partition(b"\r")[0].decode("cp437").strip()
            if title and title.isprintable():
                yield key, title


def main():
    parser = ReaderArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, required=DEFAULT_DATA is None,
                        help="your game folder or its DAT folder")
    args = parser.parse_args()
    data = find_data(args.data, "DAT", "QWOD0.WSX")
    titles = level_names(data)
    items = list(item_catalogue(data))
    groups = (
        ("Levels", titles.items()),
        ("Items", ((f"{key:#x}", title) for _, key, title, flags in items if title and not flags & 2)),
        ("Spells", ((f"{key:#x}", title) for _, key, title, flags in items if title and flags & 2)),
        ("Creature journal", creature_journal(data)),
    )
    for heading, rows in groups:
        print(f"\n{heading}")
        for key, label in rows:
            print(f"{label} ({key})")
    print("\nCreature definition tags")
    for path in sorted(data.glob("*"), key=lambda value: value.name.casefold()):
        if path.suffix.upper() != ".WSX" or not path.is_file():
            continue
        stem = path.stem.upper()
        for slot, label in creature_tags(data, stem).items():
            print(f"{label} ({stem}, definition {slot})")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
