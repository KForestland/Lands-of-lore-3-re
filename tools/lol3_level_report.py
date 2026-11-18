#!/usr/bin/env python3
"""Write one Markdown sheet per LoL3 level from the original WSX archives.

For each level stem (an archive in DAT/ that holds a LEVELS\\<STEM>\\<STEM>.LMF entry)
the sheet lists, all read from the files:
  - the level archive's entries, each named by the native name hash
    (LEVELS\\<STEM>\\<STEM>.LMF, .MAP, .ODF, .TE_; docs/lol3-wsx-reader.md);
  - the light map: stored LZO1X groups and light-map members (directory only);
  - the MAP and ODF header fields measured on all levels (docs/formats/map-odf.md);
  - the sound sidecar <STEM>S.WSX: number of RIFF WAVE files and their formats.
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
from walk_lmf_leaves import lmf_groups  # noqa: E402

ROLES = (".LMF", ".MAP", ".ODF", ".TE_")


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


def read_level(stem, main, side):
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
    for role in (".MAP", ".ODF"):
        b = blobs.get(role)
        if b and len(b) >= 156 and struct.unpack_from("<I", b, 0)[0] == 38:
            f = struct.unpack_from("<38I", b, 4)
            hdr[role] = dict(size=len(b), f0=f[0], f1=f[1], f2=f[2], f20=f[20])
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
    return dict(stem=stem, main=main.name, size=main.stat().st_size, rows=rows, roles=sorted(blobs),
                lm=lm, hdr=hdr, side=side.name if side else None, side_count=side_count, sounds=sounds)


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
    lines += ["", "For the MAP entry, field 2 − field 1 = 8 × field 20 (section 1 holds field 20 records of 8 bytes).", "",
              "## Sounds", ""]
    if L["side"]:
        fmt = ", ".join(
            (f"{n} × format {k[0]} ({'IMA ADPCM, ' if k[0] == 17 else ''}{'mono' if k[1] == 1 else 'stereo' if k[1] == 2 else str(k[1]) + ' ch'}, "
             f"{k[2]:,} Hz, {k[3]}-bit)") if k != "other" else f"{n} other"
            for k, n in sorted(L["sounds"].items(), key=lambda kv: -kv[1]))
        lines.append(f"`{L['side']}` holds {L['side_count']} entries: {fmt}.")
    else:
        lines.append("No sidecar archive.")
    lines += ["", "## Open", "",
              "- What each script group does: the streams frame with the native size table "
              "([script opcodes](../lol3-script-opcodes.md)), many command effects are open (Q11).",
              "- MAP sections 0 and 2 and the ODF layout (Q4, Q5); what the renderer does with the light map (Q3).", ""]
    return "\n".join(lines)


def readme(levels):
    lines = ["# Level sheets", "",
             "One sheet per level, written by `tools/lol3_level_report.py --data DAT --out docs/levels` from the original "
             "archives: named entries, light-map groups, MAP/ODF headers and the sound sidecar. File roles and counts only.", "",
             "| Level | Archive | Entries | Light-map members | MAP size | ODF size | Sounds |", "|---|---|---:|---:|---:|---:|---:|"]
    for L in levels:
        lines.append(f"| [{L['stem']}]({L['stem']}.md) | `{L['main']}` | {len(L['rows'])} | {L['lm']['members']:,} | "
                     f"{L['hdr'].get('.MAP', {}).get('size', 0):,} | {L['hdr'].get('.ODF', {}).get('size', 0):,} | {L['side_count']} |")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = lol3_cli.tool_args(__doc__ or "")
    a = ap.parse_args()
    stems = level_stems(a.data)
    levels = [read_level(*s) for s in stems]
    if a.check:
        named = sum(1 for L in levels if L["roles"] == sorted(ROLES))
        snd = Counter()
        for L in levels:
            snd.update(L["sounds"])
        map_ok = sum(1 for L in levels if ".MAP" in L["hdr"] and L["hdr"][".MAP"]["f2"] - L["hdr"][".MAP"]["f1"] == 8 * L["hdr"][".MAP"]["f20"])
        print(f"CHECK level_report: {len(levels)} level archives; all four level names (.LMF .MAP .ODF .TE_) found by hash in "
              f"{named}; MAP section-1 rule holds in {map_ok}; {sum(L['lm']['members'] for L in levels):,} light-map members; "
              f"{sum(snd.values()):,} sidecar sounds, non-WAVE: {snd.get('other', 0)}")
        return 0 if levels and named == len(levels) and map_ok == len(levels) and not snd.get("other") else 1
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
