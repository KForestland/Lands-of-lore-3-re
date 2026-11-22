"""Read the documented save fields requested by the LoL3 fault page."""
from dataclasses import dataclass
from hashlib import sha256
from struct import iter_unpack, unpack_from

from cli_errors import game_path
from extract_wsx_entries import wsx_name_hash
from game_names import level_stems
from level_edit_data import entry
from level_html import find_data
from lol3_save_header import parse_header
from lol3_save_selectors import selector_flags
from lol3_save_writer import GLOBAL_SECTIONS, Packed, read_level, read_packed
from lol3_script_framing import RETAIL_PE, map_range
from my_game_ui import DATA_ERRORS
from walk_lmf_leaves import lzo_decoder


@dataclass(frozen=True)
class Fault:
    title: str
    shared: tuple[int, ...] = ()
    local: tuple[tuple[str, int], ...] = ()
    quests: tuple[int, ...] = ()
    position: bool = False
    omitted: str = ""


FAULTS = (
    Fault("Rescuing Sioned", shared=(8,), quests=(36,), omitted="The rescue and Dawn events are not decoded from the save."),
    Fault("Perfumed Scarf", shared=(17,), local=(("DLOW1", 6),)),
    Fault("Left sewer grate", position=True, omitted="The failed lock request is not decoded from the save."),
    Fault("Draracle wall", position=True, omitted="The first unintended movement is not recorded in these saved values."),
    Fault("Blue Deer inn room", local=(("DLOW1", 4),), quests=(12,),
          omitted="The controller and dialogue steps are not decoded from the save."),
    Fault("Blue Gem", omitted="The socket and creature event state is not decoded from the save."),
    Fault("Victoria's shop", omitted="The shop and payment state is not decoded from the save."),
    Fault("Volcano elevator", shared=(25,), position=True, omitted="The platform's movement is not recorded in these saved values."),
    Fault("Solved quests in the journal", quests=(12, 35, 36, 37), omitted="The report omits how the journal draws the entries."),
    Fault("Five herbs", shared=(6,), local=(("BUPP1", 22),), quests=(35,),
          omitted="Boris's state is not decoded from the save."),
    Fault("Rix's Plasma Staff", omitted="The first pack change and item count are not decoded from the save."),
)
FAULT_NAMES = tuple(fault.title for fault in FAULTS)


def decompressor():
    try:
        from lzokay import LzokayError, decompress
    except ImportError:
        return lzo_decoder()

    def decode(packet, size):
        try:
            expanded = decompress(packet, size)
        except LzokayError as error:
            raise ValueError("invalid compressed save data") from error
        if len(expanded) != size:
            raise ValueError("save chunk expanded to the wrong size")
        return expanded

    return decode


def expand(part, decode):
    return b"".join(decode(packet, size) for size, packet in part.chunks)


def global_section(blob, header, index, decode):
    start, length = header["sections"][index]
    return expand(read_packed(blob[start:start + length]), decode)


def restore_bytes(delta, baseline):
    if len(delta) != len(baseline):
        raise ValueError("the save and installed reference values have different lengths")
    return bytes(value ^ original for value, original in zip(delta, baseline))


def journal_entries(blob, header, decode):
    # Save selectors for the IDs and states of categories 5 and 12.
    # Native journal initialization fills the IDs with -1 and the states with 0.
    for category, ids_selector, states_selector in ((5, 23, 36), (12, 29, 42)):
        ids = global_section(blob, header, ids_selector, decode)
        states = global_section(blob, header, states_selector, decode)
        if len(ids) != len(states):
            raise ValueError("mismatched saved journal tables")
        for (identity,), (state,) in zip(iter_unpack("<i", ids), iter_unpack("<I", states)):
            if identity:
                yield category, ~identity, state


def local_bytes(blob, header, data, image, stem, decode):
    level = next((number for number, code in level_stems(data).items() if code == stem), None)
    if level is None:
        return b""
    start, length = header["levels"][level - 2]
    if not length:
        return b""
    flags = selector_flags(image)[GLOBAL_SECTIONS:]
    block = read_level(blob[start:start + length], flags, None)
    part = block.sections[24]
    if not isinstance(part, Packed) or not part.chunks:
        return b""
    raw = entry(data, f"{stem}.WSX", key=wsx_name_hash(f"LEVELS\\{stem}\\{stem}.MAP"))
    if raw is None:
        return b""
    return restore_bytes(expand(part, decode), map_range(raw, 0xB4, 0xB0))


def saved_report(source, folder, selection):
    fault = FAULTS[selection]
    try:
        blob = source.read_bytes()
        header = parse_header(blob, len(blob))
        level, x, y, heading, region = unpack_from("<IiiIH", blob, 0x498)
        if not 2 <= level <= 19:
            raise ValueError("level outside original save range")
    except DATA_ERRORS as error:
        raise ValueError("Choose an original Lands of Lore III saved game.") from error

    try:
        data = find_data(folder, "DAT", "QWOD0.WSX")
        image = game_path(data.parent, "LOL3.DAT").read_bytes()
        if sha256(image).hexdigest() != RETAIL_PE:
            raise ValueError("unknown executable layout")
    except DATA_ERRORS as error:
        raise ValueError("Choose the game folder for the documented Lands of Lore III English 1.07a edition.") from error

    lines = [f"Lands of Lore III fault report — {fault.title}", f"Saved level: {level}"]
    if fault.position:
        lines.extend((f"X: {x / 65536}", f"Y: {y / 65536}", f"Facing (game units): {heading & 0xFFFF}"))
        if region != 0xFFFF:
            lines.append(f"Region: {region}")
    omissions = [fault.omitted] if fault.omitted else []

    try:
        if fault.shared or fault.local or fault.quests:
            decode = decompressor()
        if fault.shared:
            odf = entry(data, "GLOBAL.WSX", key=wsx_name_hash("GLOBAL\\GLOBAL.ODF"))
            if odf is None:
                raise ValueError("missing global reference values")
            shared = restore_bytes(global_section(blob, header, 1, decode), map_range(odf, 0x64, 0x60))
            lines.extend(f"Shared byte {index}: {shared[index]}" for index in fault.shared)
        for stem, index in fault.local:
            values = local_bytes(blob, header, data, image, stem, decode)
            if index < len(values):
                lines.append(f"{stem} level byte {index}: {values[index]}")
            else:
                omissions.append(f"This save has no stored {stem} level byte {index}.")
        if fault.quests:
            rows = list(journal_entries(blob, header, decode))
            for quest in fault.quests:
                states = [(category, state) for category, identity, state in rows if identity == quest]
                if states:
                    lines.extend(f"Quest {quest}, journal category {category}: {state}" for category, state in states)
                else:
                    omissions.append(f"The save has no journal entry for quest {quest}.")
    except DATA_ERRORS as error:
        raise ValueError("This saved game and game folder could not provide the required report values.") from error

    return "\n".join(lines) + "\n", "\n".join(omissions)
