"""Independent raw readers for the LoL3 retail page-facts registry."""
from functools import lru_cache
from hashlib import sha256
from struct import iter_unpack, unpack_from

from cli_errors import game_path
from page_facts_auto import x86_operand

DATA_ENV = "LOL3_DAT"
IMAGE_HASH = "9a9eb04c8f404ebf68f439df4ec7dc6ad5cc230235d0f853059f636ff720ccea"


def game_file(data, name):
    data = data.resolve()
    if name.upper().startswith("DAT/"):
        return game_path(data, name[4:])
    beside = game_path(data.parent, name)
    return beside if beside.is_file() else game_path(data, name)


@lru_cache(maxsize=4)
def read_file(path):
    return path.read_bytes()


def edition_status(data):
    path = game_file(data, "LOL3.DAT")
    if not path.is_file():
        return "original LOL3.DAT unavailable"
    if sha256(read_file(path)).hexdigest() != IMAGE_HASH:
        return "LOL3.DAT does not match the measured retail 1.07a build"
    return None


def wsx_directory(path):
    with path.open("rb") as stream:
        count, size = unpack_from("<HI", stream.read(6))
        rows = list(iter_unpack("<III", stream.read(12 * count)))
    base = 6 + 12 * count
    if len(rows) != count or base + size != path.stat().st_size:
        raise ValueError(f"{path.name}: WSX index and payload do not reach EOF")
    if any(relative + extent > size for _, relative, extent in rows):
        raise ValueError(f"{path.name}: WSX entry exceeds payload")
    return [(base + relative, extent) for _, relative, extent in rows]


def read_at(path, offset, size):
    with path.open("rb") as stream:
        stream.seek(offset)
        return stream.read(size)


def lmf_first_row(path):
    candidates = []
    for offset, size in wsx_directory(path):
        fields = unpack_from("<7I", read_at(path, offset, 28))
        if fields[:3] != (0, 38, 0x100):
            continue
        _, _, start, pool, directory, _, rows = fields
        if directory == 16 * rows and start + directory == pool <= size:
            candidates.append(offset + start)
    if len(candidates) != 1:
        raise ValueError(f"{path.name}: expected one complete LMF directory")
    return candidates[0]


def pe_rows(image):
    header, = unpack_from("<I", image, 0x3C)
    if image[:2] != b"MZ" or image[header:header + 4] != b"PE\0\0":
        raise ValueError("missing PE image header")
    count, = unpack_from("<H", image, header + 6)
    size, = unpack_from("<H", image, header + 20)
    base, = unpack_from("<I", image, header + 52)
    table = header + 24 + size
    rows = {}
    for i in range(count):
        at = table + 40 * i
        name, virtual, rva, stored, offset = unpack_from("<8s4I", image, at)
        if offset + stored > len(image):
            raise ValueError("PE section leaves the original")
        rows[name.rstrip(b"\0").decode("ascii")] = (at, virtual, base + rva, stored, offset)
    return rows


def va_bytes(image, rows, address, size):
    for _, _, start, stored, offset in rows.values():
        if start <= address and address + size <= start + stored:
            at = offset + address - start
            return image[at:at + size]
    raise ValueError(f"VA {address:#x} is outside file-backed sections")


def cache_extension(image):
    rows = pe_rows(image)
    push = va_bytes(image, rows, 0x4E45D1, 5)
    load = va_bytes(image, rows, 0x4E460A, 2)
    if push[0] != 0x68 or load[0] != 0xB2:
        raise ValueError("texture extension comparison and replacement moved")
    literal = va_bytes(image, rows, unpack_from("<I", push, 1)[0], 5)
    if literal[:1] != b"." or literal[-1:] != b"\0":
        raise ValueError("invalid native texture suffix")
    stores = ((0x4E462C, b"\x88\x54\x0C\x33"), (0x4E463A, b"\x88\x54\x29\xFF"))
    if any(va_bytes(image, rows, address, 4) != opcode for address, opcode in stores):
        raise ValueError("native texture suffix stores moved")
    return (literal[:3] + load[1:]).decode("ascii").upper()


def map_section(data, width):
    outcomes, maps = {0, 1, 2}, 0
    for path in sorted(data.iterdir()):
        if path.suffix.upper() != ".WSX":
            continue
        count, = unpack_from("<H", read_at(path, 0, 2))
        if count != 4:
            continue
        for offset, size in wsx_directory(path):
            if size < 0x58:
                continue
            header = read_at(path, offset, 0x58)
            if unpack_from("<II", header) != (38, 12076):
                continue
            starts = unpack_from("<4I", header, 4)
            rows, = unpack_from("<I", header, 0x54)
            outcomes &= {i for i in range(3) if starts[i + 1] - starts[i] == width * rows}
            maps += 1
    if len(outcomes) != 1 or maps != 18:
        raise ValueError(f"{maps} MAP headers do not establish a unique section: {outcomes}")
    return outcomes.pop()


def wsx_count(data):
    paths = sorted(path for path in data.iterdir()
                   if path.suffix.upper() == ".WSX" and path.stem.upper() != "CDCACHE")
    paths += [game_file(data, name) for name in ("LOCAL.WSX", "LOCALLNG.WSX")]
    if len(paths) != 53:
        raise ValueError(f"expected 53 original WSX archives, found {len(paths)}")
    return sum(len(wsx_directory(path)) for path in paths)


def music_wave_headers(data):
    for disc in range(1, 5):
        path = game_file(data, f"DAT/MUSIC{disc}.WSX")
        for offset, size in wsx_directory(path):
            header = read_at(path, offset, min(size, 128))
            if header[:4] != b"RIFF" or header[8:12] != b"WAVE":
                continue
            at = 12
            while at + 8 <= len(header):
                length, = unpack_from("<I", header, at + 4)
                if header[at:at + 4] == b"fmt " and length >= 16 and at + 12 <= len(header):
                    yield unpack_from("<H", header, at + 10)[0]
                    break
                at += 8 + length + (length & 1)
            else:
                raise ValueError(f"{path.name}+{offset:#x}: WAVE format header unavailable")


def read_witness(data, spec):
    kind, *args = spec
    if kind == "wsx_count":
        return wsx_count(data), "WSX directory headers in DAT and the two loose originals"
    if kind == "map_section":
        return map_section(data, args[0]), "18 raw MAP headers, section starts and field 20"
    if kind in {"wave_count", "wave_channels"}:
        channels = list(music_wave_headers(data))
        source = "MUSIC1–4.WSX directory members and RIFF WAVE format headers"
        if kind == "wave_count":
            return len(channels), source
        if not channels or len(set(channels)) != 1:
            raise ValueError("music WAVE format headers do not agree on channel count")
        return {1: "one channel", 2: "two channels"}.get(channels[0], f"{channels[0]} channels"), source
    path = game_file(data, args[0])
    if kind == "archive_size":
        entry = args[1]
        offset, size = wsx_directory(path)[entry]
        return size, f"{path.name} entry {entry} at +{offset:#x}"
    if kind == "lmf_first_row":
        return lmf_first_row(path), f"{path.name}, LMF member offset plus stored directory offset"
    image = read_file(path)
    if kind == "absolute_operand":
        va = args[1]
        code = va_bytes(image, pe_rows(image), va, 8)
        return x86_operand(code, 4), f"{path.name} instruction at VA {va:#x}"
    if kind == "pe_virtual_size":
        at, virtual, _, _, _ = pe_rows(image)[args[1]]
        return virtual, f"{path.name}+{at + 8:#x}, RemapTab virtual size"
    if kind == "pe_section":
        _, section, field = args
        rows = pe_rows(image)
        if section not in rows:
            raise ValueError(f"{path.name} has no PE section {section!r}")
        at = rows[section][0]
        member = {"rva": 12, "virtual": 8, "stored": 16, "offset": 20}[field]
        return unpack_from("<I", image, at + member)[0], f"{path.name}+{at + member:#x}, {section} {field}"
    if kind == "cache_extension":
        return cache_extension(image), f"{path.name} VA 0x4E45D1, 0x4E460A, 0x4E462C and 0x4E463A"
    raise ValueError(f"unknown byte witness {kind!r}")
