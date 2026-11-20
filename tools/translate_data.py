"""LoL3 TRR tables in the original installation."""
from filecmp import cmp
from struct import iter_unpack

import modkit
from modkit_core import game_folder
from lol3_text_writer import read_trr, trr_sources, write_trr
from extract_wsx_entries import wsx_name_hash

# Directory keys from DAT/LOCALLNG.WSX. The keys stay fixed when text moves.
TEXT_NAMES = {0xE363A4C3: "dtext.trr", 0xE370A4C3: "qtext.trr",
              0xE3E4F49B: "devent.trr", 0xE3E5289B: "qevent.trr",
              0x5FB4088C: "itemjt.trr"}


CHARSET = "the mapped game font encoding"


def warning_fonts(file, label):
    if label.lower() == "dtext.trr":
        return lambda name: name.upper().endswith("/STD8P.FNT")
    return None


def preserve_controls(original, text):
    """Carry leading formatting codes into a normal full-cell replacement."""
    if text and ord(text[0]) < 32:
        return text
    at = 0
    while at < len(original) and 0 < ord(original[at]) < 32:
        code = original[at]
        at += 1
        if code in ("\x02", "\x03") and at < len(original) and "0" <= original[at] <= "9":
            at += 1
    return original[:at] + text


def mirror_files(base, name):
    path = base / name
    if path.parent == base or path.name.upper() != "LOCALLNG.WSX" or path.parent.name.upper() != "DAT":
        return ()
    return tuple(p.name for p in base.iterdir() if p.is_file() and
                 p.name.upper() == "LOCALLNG.WSX" and cmp(path, p, shallow=False))


def font_sources(base):
    names = {wsx_name_hash(name): name for name in ("STD6P.FNT", "STD8P.FNT", "OPTION_L.FNT", "OPTION_H.FNT", "FONT_NED.FNT")}
    archives = {"LOCAL.WSX"}
    folders = [base, *(p for p in base.iterdir() if p.is_dir() and p.name.upper() == "DAT")]
    for folder in folders:
        for path in sorted(folder.iterdir()):
            if path.name.upper() not in archives or not path.is_file():
                continue
            archives.remove(path.name.upper())
            yield from fonts_in_archive(path, names)


def fonts_in_archive(path, names):
    with path.open("rb") as source:
        count = int.from_bytes(source.read(2), "little")
        source.read(4)
        rows = tuple(iter_unpack("<III", source.read(count * 12)))
        for key, at, size in rows:
            if not 20 <= size <= 65535:
                continue
            source.seek(at + 6 + count * 12)
            header = source.read(20)
            if (int.from_bytes(header[:2], "little") != size or header[2:4] != b"\x00\x05"
                    or header[4:8] != b"\x0e\x00\x14\x00"):
                continue
            yield f"{path.name}/{names.get(key, f'{key:08X}')}", header + source.read(size - 20)


def decode(raw):
    # The 0x80–0xAF glyph runs display CP437 accents and punctuation.
    # Outside the mapped range preserve the stored byte as an explicit escape.
    return "".join(bytes((i,)).decode("cp437") if i < 0xB0 else chr(0xDC00 + i) for i in raw)


def encode(text):
    out = bytearray()
    for index, char in enumerate(text):
        if 0xDC80 <= ord(char) <= 0xDCFF:
            out.append(ord(char) - 0xDC00)
            continue
        raw = char.encode("cp437")
        if raw[0] >= 0xB0:
            raise UnicodeEncodeError("game font", text, index, index + 1, "unmapped glyph value")
        out.extend(raw)
    return bytes(out)


def root(path):
    return game_folder(modkit, path)


def sources(base):
    dat = next((p for p in base.iterdir() if p.is_dir() and p.name.upper() == "DAT"), None)
    if dat is None:
        raise ValueError(f"Give --data {modkit.FOLDER}.")
    archives = (path for path in dat.iterdir() if path.name.upper() == "LOCALLNG.WSX")
    duplicates = {base / name for path in archives for name in mirror_files(base, path.relative_to(base))}
    for path, index, key, at, blob in trr_sources(dat, indexed=True):
        if path in duplicates:
            continue
        label = path.name if key is None else TEXT_NAMES.get(key, f"{key:08X}.trr")
        yield path.relative_to(base).as_posix(), index, label, at, blob


def read(label, blob):
    limit = "locked" if label.lower() in ("qevent.trr", "devent.trr") else "no limit"
    return [(f"{key:08X}", decode(value), limit) for key, value in read_trr(blob)]


def write(label, blob, changes):
    if changes and label.lower() in ("qevent.trr", "devent.trr"):
        raise ValueError("Event tags join by their stored text. Keep them unchanged.")
    rows = read_trr(blob)
    for i, text in changes.items():
        try:
            value = encode(text)
        except UnicodeError:
            raise ValueError(f"CSV row {i + 2} has a character outside the mapped glyphs. Choose a character listed by translate fonts.") from None
        rows[i] = rows[i][0], value
    if sum(len(value) + 1 for _, value in rows) + 8 * len(rows) + 4 > 0xFFFFFFFF:
        raise ValueError("This TRR exceeds the 32-bit offset range. Shorten the new text.")
    return write_trr(rows)
