#!/usr/bin/env python3
"""Write one Markdown sheet per LoL3 level from the original WSX archives.

For each level stem (an archive in DAT/ that holds a LEVELS\\<STEM>\\<STEM>.LMF entry)
the sheet lists, all read from the files:
  - the level archive's entries, each named by the native name hash
    (LEVELS\\<STEM>\\<STEM>.LMF, .MAP, .ODF, .TE_; docs/lol3-wsx-reader.md);
  - the light map: stored LZO1X groups and light-map members (directory only);
  - the MAP and ODF header fields measured on all levels (docs/formats/map-odf.md);
  - the sound sidecar <STEM>S.WSX: number of RIFF WAVE files and their formats.
  - object and region script record counts, the movie stems named by opcode 0x15,
    and whether a music stem or another level name occurs in those commands.
File roles, ids and counts only; no game text, pictures or sound.

  lol3_level_report.py --data DAT --out DIR      # all levels + README.md
  lol3_level_report.py --check --data DAT        # one line
"""
import os
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lol3_cli  # noqa: E402
from extract_wsx_entries import parse_wsx, wsx_name_hash  # noqa: E402
from lol3_script_framing import native_sizes  # noqa: E402
from lol3_script_notes import STREAMS, walk  # noqa: E402
from walk_lmf_leaves import lmf_groups  # noqa: E402

ROLES = (".LMF", ".MAP", ".ODF", ".TE_")
DATA_BIAS = 0x401800


def c_strings(image, offset, count):
    out = []
    for pointer in struct.unpack_from("<%dI" % count, image, offset):
        at = pointer - DATA_BIAS
        if pointer == 0 or not (0 <= at < len(image)):
            raise ValueError("name pointer at file %#x" % offset)
        end = image.find(b"\x00", at)
        text = image[at:end]
        if not text or any(byte < 32 or byte > 126 for byte in text):
            raise ValueError("name text at file %#x" % at)
        out.append(text.decode("ascii"))
    return out


def level_path_stems(image):
    """Stems in the executable's levels\\<stem>\\<stem> list, including aglob."""
    blob = image[0x147D6C:0x147EE8]
    names = []
    at = 0
    while at < len(blob):
        if blob[at:at + 7] == b"levels\\":
            end = blob.find(b"\x00", at)
            parts = blob[at:end].decode("ascii").split("\\")
            if len(parts) == 3 and parts[1] == parts[2]:
                names.append(parts[1])
            at = end + 1
        else:
            at += 1
    if len(names) != 19:
        raise ValueError("level path list %s" % len(names))
    return names


def load_script_context(data_dir):
    image = (Path(data_dir).resolve().parent / "LOL3.DAT").read_bytes()
    music = c_strings(image, 0x148180, 40)
    return {
        "sizes": native_sizes(image),
        "movies": c_strings(image, 0x148BD0, 19),
        "music": [name for name in music if name.isalnum() and name != "None"],
        "levels": level_path_stems(image),
    }


def script_facts(payload, sizes, stem, movies, music, level_names):
    walks = {space: walk(payload, 0, space, sizes) for space in STREAMS}
    named = Counter()
    second = Counter()
    music_hit = []
    level_hit = []
    hash_hit = []
    music_hashes = {wsx_name_hash("MUSIC\\%s.aud" % name): name for name in music}
    level_hashes = {}
    for name in level_names:
        if name.upper() == stem:
            continue
        level_hashes[wsx_name_hash("LEVELS\\%s\\%s.MAP" % (name, name))] = name
    for space, (stream, starts, _base, _counts, _events, _aliases) in walks.items():
        folded = bytes(stream).lower()
        for name in music:
            if name.lower().encode("ascii") in folded:
                music_hit.append((space, name))
        for name in level_names:
            if name.upper() == stem:
                continue
            if name.lower().encode("ascii") in folded:
                level_hit.append((space, name))
        for at in starts:
            opcode = stream[at]
            row = bytes(stream[at:at + sizes[opcode]])
            if opcode == 0x15:
                named[row[4]] += 1
                second[row[5]] += 1
            for index in range(0, len(row) - 3):
                dword = struct.unpack_from("<I", row, index)[0]
                if dword in music_hashes:
                    hash_hit.append(music_hashes[dword])
                if dword in level_hashes:
                    hash_hit.append(level_hashes[dword])
    return {
        "object": len(walks["object"][1]),
        "region": len(walks["region"][1]),
        "movies": named,
        "second": second,
        "music_hit": music_hit,
        "level_hit": level_hit,
        "hash_hit": hash_hit,
        "movie_names": movies,
    }


def level_stems(data_dir):
    """(stem, main archive, sidecar) for every archive holding its own LEVELS\\<STEM>\\<STEM>.LMF key."""
    files = {f.stem.upper(): f for f in lol3_cli.wsx_files(data_dir)}
    out = []
    for stem, f in sorted(files.items()):
        try:
            p = parse_wsx(f)
        except ValueError:
            continue
        if wsx_name_hash(f"LEVELS\\{stem}\\{stem}.LMF") in {e["hash"] for e in p["entries"]}:
            out.append((stem, f, files.get(stem + "S")))
    return out


def geometry_check(data, fields):
    """Validate the table joins read by LOL3.DAT at 0x43EAB2–0x43EC92."""
    vertex_count, attached_count, surface_count = fields[19:22]
    start = fields[2]
    end = start + 56 * surface_count
    point_count, point_start = struct.unpack_from("<II", data, 0xC4)
    path_count, path_start = struct.unpack_from("<II", data, 0xD8)
    if not (end <= fields[16] <= len(data)
            and point_start == fields[0] + 8 * vertex_count
            and path_start == point_start + 34 * point_count
            and fields[1] == path_start + 35 * path_count):
        return False
    for offset in range(start, end, 56):
        neighbors = struct.unpack_from("<4H", data, offset + 8)
        vertices = struct.unpack_from("<4H", data, offset + 0x10)
        attached, = struct.unpack_from("<H", data, offset + 0x1E)
        count = data[offset + 0x32]
        if (any(index != 0xFFFF and index >= surface_count for index in neighbors)
                or any(index >= vertex_count for index in vertices)
                or (count and attached + count > attached_count)
                or (not count and attached != 0xFFFF)):
            return False
    for _, _, surface, _ in struct.iter_unpack("<hhHH", data[point_start:point_start + 8 * point_count]):
        if surface != 0xFFFF and surface >= surface_count:
            return False
    return all(first + count <= point_count
               for first, count, _ in struct.iter_unpack("<HBB", data[path_start:path_start + 4 * path_count]))


def read_level(stem, main, side, ctx):
    p = parse_wsx(main)
    names = {wsx_name_hash(f"LEVELS\\{stem}\\{stem}{r}"): r for r in ROLES}
    rows = []
    blobs = {}
    for e in sorted(p["entries"], key=lambda e: e["index"]):
        role = names.get(e["hash"])
        rows.append((e["index"], e["hash"], e["offset"], e["size"], role))
        if role:
            blobs[role] = e["blob"]
    groups = list(lmf_groups(blobs[".LMF"])) if ".LMF" in blobs else []
    lm = dict(groups=len(groups), members=sum(len(g["lengths"]) for g in groups))
    hdr = {}
    geometry_ok = False
    for role in (".MAP", ".ODF"):
        b = blobs.get(role)
        if b and len(b) >= 156 and struct.unpack_from("<I", b, 0)[0] == 38:
            f = struct.unpack_from("<38I", b, 4)
            hdr[role] = dict(size=len(b), f0=f[0], f1=f[1], f2=f[2], f20=f[20])
            if role == ".MAP" and len(b) >= 0xDC:
                geometry_ok = geometry_check(b, f)
                hdr[role]["surfaces"] = f[21]
    sounds = Counter()
    side_count = 0
    if side is not None:
        sp = parse_wsx(side)
        side_count = len(sp["entries"])
        for e in sp["entries"]:
            b = e["blob"]
            if b[:4] == b"RIFF" and b[8:12] == b"WAVE" and b.find(b"fmt ") > 0:
                i = b.find(b"fmt ")
                tag, ch, rate = struct.unpack_from("<HHI", b, i + 8)
                bits = struct.unpack_from("<H", b, i + 22)[0]
                sounds[(tag, ch, rate, bits)] += 1
            else:
                sounds["other"] += 1
    script = script_facts(blobs[".MAP"], ctx["sizes"], stem, ctx["movies"], ctx["music"], ctx["levels"])
    return dict(stem=stem, main=main.name, size=main.stat().st_size, rows=rows, roles=sorted(blobs),
                lm=lm, hdr=hdr, geometry_ok=geometry_ok, side=side.name if side else None,
                side_count=side_count, sounds=sounds, script=script)


def sheet(L):
    s = L["stem"]
    lines = [f"# {s}", "",
             f"Made by `tools/lol3_level_report.py` from `DAT/{L['main']}`"
             + (f" and `DAT/{L['side']}`" if L["side"] else "") + ". Formats: [WSX](../formats/wsx.md), "
             "[LMF light maps](../formats/lmf.md), [MAP and ODF](../formats/map-odf.md), [textures](../formats/textures.md).", "",
             "## Level archive", "",
             f"`{L['main']}` is {L['size']:,} bytes with {len(L['rows'])} entries. Each entry is named by the native "
             f"name hash of `LEVELS\\{s}\\{s}.<ext>` ([WSX reader](../lol3-wsx-reader.md#resource-name-key)).", "",
             "| Entry | Key | File offset | Size | Name |", "|---:|---|---:|---:|---|"]
    for idx, key, off, size, role in L["rows"]:
        lines.append(f"| {idx} | 0x{key:08X} | {off:,} | {size:,} | "
                     + (f"`LEVELS\\{s}\\{s}{role}`" if role else "not named by the four level names") + " |")
    lines += ["", "## Light map", "",
              f"{L['lm']['groups']:,} stored LZO1X groups holding {L['lm']['members']:,} light-map members "
              "(directory read; `walk_lmf_leaves.py --decode` checks every member).", "",
              "## MAP and ODF headers", "", "| Entry | Size | Field 0 | Field 1 | Field 2 | Field 20 |",
              "|---|---:|---:|---:|---:|---:|"]
    for role in (".MAP", ".ODF"):
        h = L["hdr"].get(role)
        if h:
            lines.append(f"| `{role[1:]}` | {h['size']:,} | {h['f0']:,} | {h['f1']:,} | {h['f2']:,} | {h['f20']:,} |")
    lines += ["", "For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes)."]
    if L["geometry_ok"]:
        lines.append(f"Field 21 counts {L['hdr']['.MAP']['surfaces']:,} surface rows in section 2 "
                     "([native readers](../lol3-map-odf-readers.md#map-sections-1-and-2)).")
    lines += ["", "## Sounds", ""]
    if L["side"]:
        fmt = ", ".join(
            (f"{n} × format {k[0]} ({'IMA ADPCM, ' if k[0] == 17 else ''}{'mono' if k[1] == 1 else 'stereo' if k[1] == 2 else str(k[1]) + ' ch'}, "
             f"{k[2]:,} Hz, {k[3]}-bit)") if k != "other" else f"{n} other"
            for k, n in sorted(L["sounds"].items(), key=lambda kv: -kv[1]))
        lines.append(f"`{L['side']}` holds {L['side_count']} entries: {fmt}.")
    else:
        lines.append("No sidecar archive.")
    facts = L["script"]
    lines += ["", "## Scripts", "",
              f"The object stream has {facts['object']:,} records and the region stream has {facts['region']:,} records. "
              "Both counts are a walk of the MAP command bytes with the opcode sizes from the executable. "
              "The [script summary](notes/{s}.md) gives the same record counts with the event pools.".format(s=s),
              ""]
    if facts["movies"]:
        parts = [f"`{facts['movie_names'][index]}` (index {index}, {count} command{'s' if count != 1 else ''})"
                 for index, count in sorted(facts["movies"].items())]
        lines.append("Opcode 0x15 byte +4 names " + "; ".join(parts) + ". "
                     "Byte +5 is 0 on each of these commands. "
                     "VA `0x447F97` passes byte +4 to VA `0x46FA60`, and VA `0x46FCF2` reads "
                     "`[index*4 + 0x54A3D0]`, the 19 stems at file `0x148BD0`.")
    else:
        lines.append("Opcode 0x15 does not occur, so these streams name no movie stem.")
    if facts["music_hit"] or any(name for name in facts["hash_hit"]):
        lines.append("A framed command contains a music stem or its aud-name hash. That hit is listed by the check.")
    else:
        lines.append("No framed command contains a music stem from the pointer table at file `0x148180`, "
                     "or the hash of `MUSIC\\<stem>.aud`.")
    if facts["level_hit"]:
        lines.append("A framed command contains another level stem.")
    else:
        lines.append("No framed command contains another level stem, in either case, or the hash of that level's MAP name. "
                     "So no exit in these two streams names its target level by stem or MAP hash; an exit by numeric index or another path is not ruled out.")
    lines += ["", "## Related notes", "",
              f"- [Script summary](notes/{s}.md) gives trigger and effect counts from the original MAP.",
              "- [MAP and ODF readers](../lol3-map-odf-readers.md) describe the remaining open fields.",
              "- [Light maps](../formats/lmf.md) describes the stored data and remaining renderer questions.", ""]
    return "\n".join(lines)


def readme(levels):
    lines = ["# Level sheets", "",
             "One sheet per level, written by `tools/lol3_level_report.py --data DAT --out docs/levels` from the original "
             "archives: named entries, light-map groups, MAP/ODF headers, the sound sidecar, and the script record counts. "
             "Each sheet lists the movie stems named by opcode 0x15. The framed commands do not contain a music stem or another level name.", "",
             "The [script summaries](notes/README.md) cover triggers and script groups for each level.", "",
             "| Level | Archive | Entries | Light-map members | MAP size | ODF size | Sounds |", "|---|---|---:|---:|---:|---:|---:|"]
    for L in levels:
        lines.append(f"| [{L['stem']}]({L['stem']}.md) | `{L['main']}` | {len(L['rows'])} | {L['lm']['members']:,} | "
                     f"{L['hdr'].get('.MAP', {}).get('size', 0):,} | {L['hdr'].get('.ODF', {}).get('size', 0):,} | {L['side_count']} |")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = lol3_cli.tool_args(__doc__ or "")
    a = ap.parse_args()
    ctx = load_script_context(a.data)
    stems = level_stems(a.data)
    levels = [read_level(*s, ctx) for s in stems]
    if a.check:
        named = sum(1 for L in levels if L["roles"] == sorted(ROLES))
        snd = Counter()
        for L in levels:
            snd.update(L["sounds"])
        map_ok = sum(1 for L in levels if ".MAP" in L["hdr"] and L["hdr"][".MAP"]["f2"] - L["hdr"][".MAP"]["f1"] == 8 * L["hdr"][".MAP"]["f20"])
        geometry_ok = sum(L["geometry_ok"] for L in levels)
        objects = sum(L["script"]["object"] for L in levels)
        regions = sum(L["script"]["region"] for L in levels)
        movie_commands = sum(sum(L["script"]["movies"].values()) for L in levels)
        stray = sum(len(L["script"]["music_hit"]) + len(L["script"]["level_hit"]) + len(L["script"]["hash_hit"])
                    for L in levels)
        bad_index = any(index >= len(L["script"]["movie_names"]) for L in levels for index in L["script"]["movies"])
        bad_second = any(value != 0 for L in levels for value in L["script"]["second"])
        print(f"CHECK level_report: {len(levels)} level archives; all four level names (.LMF .MAP .ODF .TE_) found by hash in "
              f"{named}; MAP section-1 rule holds in {map_ok}, surface and waypoint joins in {geometry_ok}; "
              f"{sum(L['lm']['members'] for L in levels):,} light-map members; "
              f"{sum(snd.values()):,} sidecar sounds, non-WAVE: {snd.get('other', 0)}; "
              f"scripts {objects} object / {regions} region; opcode 0x15 names {movie_commands} movies; "
              f"music and other-level names in scripts: {stray}")
        ok = (len(levels) and named == map_ok == geometry_ok == len(levels) and not snd.get("other")
              and objects == 54940 and regions == 4040 and movie_commands == 25
              and stray == 0 and not bad_index and not bad_second)
        return 0 if ok else 1
    if not a.out:
        ap.print_help(); return 2
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for L in levels:
        (out / f"{L['stem']}.md").write_text(sheet(L), encoding="utf-8")
    (out / "README.md").write_text(readme(levels), encoding="utf-8")
    print(f"wrote {len(levels)} sheets to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
