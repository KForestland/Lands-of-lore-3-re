#!/usr/bin/env python3
"""Read LOL3.DAT and list every save selector's live bytes, length, flags and adjuster.

  lol3_save_selectors.py --data DAT
  lol3_save_selectors.py --data DAT --check

The global loader (0x436D43) and the global writer (0x43789D) call 0x438140.
The level reader (0x43745B) and the level writer (0x437F3A) call 0x438940.
--check reads the two selector counts from the bound compare at the head of each
descriptor, requires the call sites, jump tables, padding and adjuster bounds
above, counts the 0x43C410 calls in each adjuster arm, and requires the selector
table on the save page to match those arms.
"""
from cli_errors import run_cli
from hashlib import sha256
from pathlib import Path

import lol3_cli
from lol3_script_framing import CODE_BIAS, RETAIL_PE

from capstone import Cs, CS_ARCH_X86, CS_MODE_32
from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_OP_REG

PAGE = Path(__file__).resolve().parents[1] / "docs" / "lol3-native-saves.md"
BEGIN = "<!-- selectors:begin -->"
END = "<!-- selectors:end -->"
GLOBAL_DESCRIPTOR, GLOBAL_TABLE, GLOBAL_COUNT = 0x438140, 0x438848, 61
LEVEL_DESCRIPTOR, LEVEL_TABLE, LEVEL_COUNT = 0x438940, 0x439460, 75
GLOBAL_ADJUSTER, GLOBAL_MAP, GLOBAL_ARMS = 0x439590, 0x439AEC, 0x439AC4
LEVEL_ADJUSTER, LEVEL_MAP, LEVEL_ARMS = 0x439B30, 0x43A488, 0x43A410
GLOBAL_ADJUST_MAX, LEVEL_ADJUST_MAX = 0x3C, 0x48
POINTER_HELPER = 0x43C410
# (call site, callee): the loader, reader and writers that copy the sections.
CALL_SITES = (
    (0x436D43, GLOBAL_DESCRIPTOR), (0x43789D, GLOBAL_DESCRIPTOR),
    (0x43745B, LEVEL_DESCRIPTOR), (0x437F3A, LEVEL_DESCRIPTOR),
    (0x436E14, GLOBAL_ADJUSTER), (0x436E83, GLOBAL_ADJUSTER), (0x437928, GLOBAL_ADJUSTER),
    (0x437513, LEVEL_ADJUSTER), (0x43757A, LEVEL_ADJUSTER), (0x437FDC, LEVEL_ADJUSTER),
    (0x436F2E, 0x437340),
)

# One line per adjuster arm: which dwords 0x43C410 receives. A loop line is
# only as much as one pass shows plus the stride the arm adds.
ARM_EFFECT = {
    0x4395CB: "dwords at +0x104, +0x10C, +0x110, +0x190, +0x118, +0x11C, +0x114, +0x144, +0x148, +0x279, +0x27D, +0x12E, +0x132, +0x242 and +0x309; ten dwords from +0x335 step 4; then +0x10 and +0x14",
    0x43978B: "each record's dwords at +0 and +0xC, stride = the unit, while the record start is below the byte count",
    0x4397F9: "dwords at +0x205, +0x1115 and +0x12F89",
    0x43984B: "dwords at +0x44 and +0x4C",
    0x43987B: "the dword at +0 of each record, stride = the unit, while the record start is below the byte count",
    0x4398BA: "dwords at +0x10, +0x14, +0x34, +0x48, +0x4C, +0x3498 and +0x3610; then 0x23 groups of five records, record stride 0x48 and group stride 0x178, from +0xA0, dwords at +0 and +4",
    0x4399D9: "the dword at +0x1B2A; then 0x13 steps of 0x16E from +0, and each step also passes address 0x660F48 on both sides",
    0x439A3E: "each record's dwords at +0 and +0xC, stride = the unit, while the record start is below the byte count",
    0x439AA9: "the dword at +0",
    0x439ABB: "returns without calling the pointer helper",
    0x439BD7: "dwords at +0 and +4",
    0x439B6C: "each record's dwords at +0 and +4, stride = the unit, while the record start is below the byte count",
    0x439C00: "each record's dwords at +0 and +4, stride = the unit, while the record start is below the byte count",
    0x439C6D: "the dword at +0 of each record, stride = the unit, while the record start is below the byte count",
    0x439CA8: "each record's dwords at +0, +4, +8 and +0xC, stride = the unit, while the record start is below the byte count",
    0x439D35: "each record's dwords at +0x34, +0x10 and +0x14, stride = the unit, while the record start is below the byte count",
    0x439DB1: "each record's dwords at +0x34, +0x38, +0x10 and +0x14, stride = the unit, while the record start is below the byte count",
    0x439E42: "each record's dwords at +0x44, +0x68, +0x6C, +0x90, +0xCC, +0x34, +0x10 and +0x14, stride = the unit, while the record start is below the byte count",
    0x439F27: "each record's dwords at +0x34, +0x38, +0x10 and +0x14, stride = the unit, while the record start is below the byte count",
    0x439FB8: "each record's dwords at +0x34, +0x10 and +0x14, stride = the unit, while the record start is below the byte count",
    0x43A15D: "the dword at +0",
    0x43A035: "the dword at +0",
    0x43A04E: "each record's dwords at +0xC and +0, stride = the unit, while the record start is below the byte count",
    0x43A144: "the dword at +0",
    0x43A0B5: "the dword at +0 of each record, stride = the unit, while the record start is below the byte count",
    0x43A0F0: "the dword at +0 of each record, stride = the unit, while the record start is below the byte count",
    0x43A12B: "calls 0x43A4E0, which switches on byte +0x64 through the table at 0x43AE70 (bound 0x94). Those arms are not read here",
    0x43A366: "the dword at +0 of each record, stride = the unit, while the record start is below the byte count",
    0x43A3A1: "the dword at +0 of each record, stride = the unit, while the record start is below the byte count",
    0x43A3D8: "the dword at +0 of each record, stride = the unit, while the record start is below the byte count",
    0x43A176: "0x13 dwords from +0x34 step 0x28; 0x100 dwords from +0x32C step 0x28; 0x13 dwords from +0x2B2C step 4; 8 dwords from +0x2B78 step 4; 3 dwords from +0x2B98 step 4; then the dwords at +0x2CDC and +0x2BA4",
    0x43A2D1: "the dword at +0 of each record, stride = the unit, while the record start is below the byte count",
    0x43A30C: "the dword at +0 of each record, stride = the unit, while the record start is below the byte count",
    0x43A347: "the dword at +0x18",
    0x43A408: "returns without calling the pointer helper",
}

# Calls to 0x43C410 written in each arm, read up to the arm's ret. A loop body
# counts once. --check requires these counts, so the text above cannot name
# more or fewer call sites than the arm has.
ARM_CALLS = {
    0x4395CB: 18, 0x43978B: 2, 0x4397F9: 3, 0x43984B: 2, 0x43987B: 1, 0x4398BA: 9,
    0x4399D9: 3, 0x439A3E: 2, 0x439AA9: 1, 0x439ABB: 0, 0x439B6C: 2, 0x439BD7: 2,
    0x439C00: 2, 0x439C6D: 1, 0x439CA8: 4, 0x439D35: 3, 0x439DB1: 4, 0x439E42: 8,
    0x439F27: 4, 0x439FB8: 3, 0x43A035: 1, 0x43A04E: 2, 0x43A0B5: 1, 0x43A0F0: 1,
    0x43A12B: 0, 0x43A144: 1, 0x43A15D: 1, 0x43A176: 7, 0x43A2D1: 1, 0x43A30C: 1,
    0x43A347: 1, 0x43A366: 1, 0x43A3A1: 1, 0x43A3D8: 1, 0x43A408: 0,
}


class Lin:
    """coeff * each named factor, plus a constant. None means not linear."""

    def __init__(self, terms, const=0):
        merged = {}
        for name, coeff in terms:
            merged[name] = merged.get(name, 0) + coeff
        self.terms = tuple(sorted((name, coeff) for name, coeff in merged.items() if coeff))
        self.const = const

    def __mul__(self, other):
        if isinstance(other, int):
            return Lin([(name, coeff * other) for name, coeff in self.terms], self.const * other)
        if self.const == 0 and other.const == 0 and len(self.terms) == 1 and len(other.terms) == 1:
            a, b = self.terms[0], other.terms[0]
            if a[1] == 1 and b[1] == 1:
                return Lin([((a[0], b[0]), 1)])
        return None

    def __add__(self, other):
        if isinstance(other, int):
            return Lin(self.terms, self.const + other)
        if not isinstance(other, Lin):
            return None
        return Lin((*self.terms, *other.terms), self.const + other.const)

    def __sub__(self, other):
        if isinstance(other, int):
            return self + (-other)
        if not isinstance(other, Lin):
            return None
        return self + Lin([(name, -coeff) for name, coeff in other.terms], -other.const)

    def text(self):
        parts = []
        for name, coeff in self.terms:
            shown = name if isinstance(name, str) else f"({name[0]}*{name[1]})"
            if coeff == 1:
                parts.append(shown)
            elif coeff == -1:
                parts.append(f"-{shown}")
            else:
                parts.append(f"({shown}*{coeff:#x})" if coeff > 0 else f"({shown}*{coeff:#x})")
        if self.const or not parts:
            parts.append(f"{self.const:#x}")
        if len(parts) == 1:
            return parts[0]
        return "(" + "+".join(parts) + ")"


def image_of(data_dir):
    image = (Path(data_dir).resolve().parent / "LOL3.DAT").read_bytes()
    if sha256(image).hexdigest() != RETAIL_PE:
        raise ValueError("LOL3.DAT does not match the documented English retail executable")
    return image


def u32(image, va):
    off = va - CODE_BIAS
    return int.from_bytes(image[off:off + 4], "little")


def decoder():
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = True
    return md


def ins_at(md, image, va):
    got = list(md.disasm(image[va - CODE_BIAS:va - CODE_BIAS + 16], va))
    return got[0] if got else None


def walk(md, image, start):
    va = start
    seen = set()
    while va not in seen and len(seen) < 40:
        seen.add(va)
        ins = ins_at(md, image, va)
        if ins is None:
            raise ValueError(f"no instruction at {va:#x}")
        yield ins
        if ins.mnemonic.startswith("ret"):
            return
        if ins.mnemonic == "jmp" and ins.operands[0].type == X86_OP_IMM:
            va = ins.operands[0].imm & 0xFFFFFFFF
            continue
        va += ins.size
    raise ValueError(f"descriptor {start:#x} did not return")


def mem_name(ins, op):
    if op.mem.index or op.mem.base:
        return None
    return f"[{op.mem.disp & 0xFFFFFFFF:#x}]"


def describe(md, image, start):
    """Return pointer, byte count, unit and flags text for one descriptor arm."""
    regs = {}
    outs = {}
    slots = {8: "ptr", 0xC: "size", 0x10: "unit", 0x14: "flags"}
    for ins in walk(md, image, start):
        if ins.mnemonic in ("jmp", "ret"):
            continue
        if ins.mnemonic == "mov" and len(ins.operands) == 2:
            dst, src = ins.operands
            if dst.type == X86_OP_REG:
                rn = ins.reg_name(dst.reg)
                if src.type == X86_OP_IMM:
                    regs[rn] = Lin((), src.imm & 0xFFFFFFFF)
                elif src.type == X86_OP_REG:
                    regs[rn] = regs.get(ins.reg_name(src.reg))
                elif src.type == X86_OP_MEM and src.mem.index == 0 and ins.reg_name(src.mem.base) == "esp" and src.mem.disp in slots:
                    regs[rn] = Lin((), src.mem.disp)
                elif src.type == X86_OP_MEM and src.mem.index == 0 and src.mem.base == 0:
                    regs[rn] = Lin([(mem_name(ins, src), 1)])
                elif src.type == X86_OP_MEM and src.mem.index == 0:
                    base = regs.get(ins.reg_name(src.mem.base))
                    if isinstance(base, Lin) and len(base.terms) == 1 and base.terms[0][1] == 1 and base.const == 0:
                        symbol = base.terms[0][0]
                        if isinstance(symbol, str) and symbol.startswith("["):
                            regs[rn] = Lin([(f"dword({symbol}+{src.mem.disp:#x})", 1)])
                        else:
                            regs[rn] = None
                    else:
                        regs[rn] = None
                else:
                    regs[rn] = None
            elif dst.type == X86_OP_MEM and dst.mem.index == 0 and dst.mem.base:
                base = regs.get(ins.reg_name(dst.mem.base))
                val = Lin((), src.imm & 0xFFFFFFFF) if src.type == X86_OP_IMM else regs.get(ins.reg_name(src.reg)) if src.type == X86_OP_REG else None
                if isinstance(base, Lin) and base.const in slots and not base.terms and dst.mem.disp == 0 and isinstance(val, Lin):
                    outs[slots[base.const]] = val.text()
        elif ins.mnemonic == "lea" and ins.operands[0].type == X86_OP_REG:
            rn = ins.reg_name(ins.operands[0].reg)
            src = ins.operands[1]
            if src.type != X86_OP_MEM:
                regs[rn] = None
                continue
            disp = src.mem.disp
            base = regs.get(ins.reg_name(src.mem.base)) if src.mem.base else Lin((), 0)
            index = regs.get(ins.reg_name(src.mem.index)) if src.mem.index else Lin((), 0)
            scale = src.mem.scale or 1
            if isinstance(base, Lin) and isinstance(index, Lin):
                scaled = index * scale
                regs[rn] = None if scaled is None else base + scaled + disp
            else:
                regs[rn] = None
        elif ins.mnemonic in ("shl", "shr") and ins.operands[0].type == X86_OP_REG and ins.operands[1].type == X86_OP_IMM:
            rn = ins.reg_name(ins.operands[0].reg)
            cur = regs.get(rn)
            shift = ins.operands[1].imm
            if isinstance(cur, Lin) and ins.mnemonic == "shl":
                regs[rn] = cur * (1 << shift)
            elif isinstance(cur, Lin) and ins.mnemonic == "shr" and all(coeff % (1 << shift) == 0 for _, coeff in cur.terms) and cur.const % (1 << shift) == 0:
                regs[rn] = Lin([(name, coeff >> shift) for name, coeff in cur.terms], cur.const >> shift)
            elif isinstance(cur, Lin) and ins.mnemonic == "shr":
                regs[rn] = Lin([(f"({cur.text()}>>{shift})", 1)])
            else:
                regs[rn] = None
        elif ins.mnemonic == "imul" and ins.operands[0].type == X86_OP_REG:
            rn = ins.reg_name(ins.operands[0].reg)
            src = ins.operands[1]
            other = None
            if src.type == X86_OP_REG:
                other = regs.get(ins.reg_name(src.reg))
            elif src.type == X86_OP_MEM and src.mem.base and src.mem.index == 0:
                base = regs.get(ins.reg_name(src.mem.base))
                if isinstance(base, Lin) and len(base.terms) == 1 and base.terms[0][1] == 1 and base.const == 0 and isinstance(base.terms[0][0], str):
                    other = Lin([(f"dword({base.terms[0][0]}+{src.mem.disp:#x})", 1)])
            cur = regs.get(rn)
            regs[rn] = cur * other if isinstance(cur, Lin) and isinstance(other, Lin) else None
        elif ins.mnemonic == "sub" and len(ins.operands) == 2 and ins.operands[0].type == X86_OP_REG and ins.operands[1].type == X86_OP_REG:
            rn = ins.reg_name(ins.operands[0].reg)
            cur = regs.get(rn)
            other = regs.get(ins.reg_name(ins.operands[1].reg))
            regs[rn] = cur - other if isinstance(cur, Lin) and isinstance(other, Lin) else None
        elif ins.mnemonic == "add" and len(ins.operands) == 2 and ins.operands[0].type == X86_OP_REG and ins.operands[1].type == X86_OP_REG:
            rn = ins.reg_name(ins.operands[0].reg)
            cur = regs.get(rn)
            other = regs.get(ins.reg_name(ins.operands[1].reg))
            regs[rn] = cur + other if isinstance(cur, Lin) and isinstance(other, Lin) else None
        else:
            if ins.mnemonic == "mov":
                continue
            # An unhandled arithmetic instruction clears the destination.
            if ins.operands and ins.operands[0].type == X86_OP_REG:
                regs[ins.reg_name(ins.operands[0].reg)] = None
    missing = [name for name in slots.values() if name not in outs]
    if missing:
        raise ValueError(f"descriptor {start:#x} left {', '.join(missing)} unset")
    return outs


def rows(image):
    md = decoder()
    global_entries = [u32(image, GLOBAL_TABLE + 4 * i) for i in range(GLOBAL_COUNT)]
    level_entries = [u32(image, LEVEL_TABLE + 4 * i) for i in range(LEVEL_COUNT)]
    global_map = list(image[GLOBAL_MAP - CODE_BIAS:GLOBAL_MAP - CODE_BIAS + GLOBAL_COUNT])
    level_map = list(image[LEVEL_MAP - CODE_BIAS:LEVEL_MAP - CODE_BIAS + LEVEL_ADJUST_MAX + 1])
    out = []
    for index, entry in enumerate(global_entries):
        fields = describe(md, image, entry)
        arm = u32(image, GLOBAL_ARMS + 4 * global_map[index])
        out.append(("Global", index, entry, fields, arm))
    for index, entry in enumerate(level_entries):
        fields = describe(md, image, entry)
        if index > LEVEL_ADJUST_MAX:
            arm = None
        else:
            arm = u32(image, LEVEL_ARMS + 4 * level_map[index])
        out.append(("Level", index, entry, fields, arm))
    return out


def effect(arm):
    if arm is None:
        return "index above 0x48, so the adjuster returns before its jump table"
    return ARM_EFFECT[arm]


def table(image):
    lines = [
        "| Selector | Descriptor | Live bytes | Byte count | Unit | Flags | Adjuster | Dwords passed to the pointer helper |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for kind, index, entry, fields, arm in rows(image):
        arm_text = "none" if arm is None else f"`{arm:#x}`"
        lines.append(
            f"| {kind} {index} | `{entry:#x}` | `{fields['ptr']}` | `{fields['size']}` | "
            f"`{fields['unit']}` | `{fields['flags']}` | {arm_text} | {effect(arm)} |"
        )
    return "\n".join(lines)


def pins(image):
    found = {(kind, index): fields for kind, index, _entry, fields, _arm in rows(image)}
    expect = {
        ("Global", 0): ("0x5d4ee0", "0x464", "0x464", "0x7"),
        ("Global", 5): ("0x0", "0x0", "0x0", "0x1"),
        ("Global", 7): ("0x585444", "0x68", "0x68", "0x1"),
        ("Global", 11): ("0x546a58", "0x50", "0x10", "0x1"),
        ("Level", 12): ("[0x570194]", "([0x5701b4]*0x38)", "0x38", "0x7"),
        ("Level", 25): ("dword([0x7d7824]+0x0)", "(dword([0x7d7824]+0x8)*dword([0x7d7824]+0xc))", "dword([0x7d7824]+0xc)", "0x7"),
    }
    for key, want in expect.items():
        got = found[key]
        have = (got["ptr"], got["size"], got["unit"], got["flags"])
        if have != want:
            raise ValueError(f"{key[0]} {key[1]} decoded {have}, expected {want}")
    md = decoder()
    for head, table_va, count in ((GLOBAL_DESCRIPTOR, GLOBAL_TABLE, GLOBAL_COUNT), (LEVEL_DESCRIPTOR, LEVEL_TABLE, LEVEL_COUNT)):
        heads = list(md.disasm(image[head - CODE_BIAS:head - CODE_BIAS + 20], head))
        bound, jump = heads[1], heads[3]
        if bound.mnemonic != "cmp" or bound.operands[1].imm + 1 != count:
            raise ValueError(f"descriptor {head:#x} bound is not {count - 1:#x}")
        if jump.mnemonic != "jmp" or jump.operands[0].mem.disp & 0xFFFFFFFF != table_va or jump.operands[0].mem.scale != 4:
            raise ValueError(f"descriptor {head:#x} does not jump through {table_va:#x} with 4-byte entries")
        if u32(image, table_va + 4 * count) != 0x90909090:
            raise ValueError(f"descriptor table {table_va:#x} entry {count} is not the nop padding")
        if not all(head < u32(image, table_va + 4 * i) < table_va for i in range(count)):
            raise ValueError(f"descriptor table {table_va:#x} has an arm outside {head:#x}")
    for head, bound_va, bound, map_va, arms_va in ((GLOBAL_ADJUSTER, 0x4395B3, GLOBAL_ADJUST_MAX, GLOBAL_MAP, GLOBAL_ARMS),
                                                  (LEVEL_ADJUSTER, 0x439B54, LEVEL_ADJUST_MAX, LEVEL_MAP, LEVEL_ARMS)):
        cmp, _ja, _xor, mov, jmp = list(md.disasm(image[bound_va - CODE_BIAS:bound_va - CODE_BIAS + 24], bound_va))[:5]
        if cmp.mnemonic != "cmp" or cmp.operands[1].imm != bound:
            raise ValueError(f"adjuster {head:#x} bound is not {bound:#x}")
        if mov.operands[1].mem.disp & 0xFFFFFFFF != map_va or jmp.operands[0].mem.disp & 0xFFFFFFFF != arms_va:
            raise ValueError(f"adjuster {head:#x} does not use map {map_va:#x} and arms {arms_va:#x}")
    for site, callee in CALL_SITES:
        ins = ins_at(md, image, site)
        if ins is None or ins.mnemonic != "call" or ins.operands[0].imm & 0xFFFFFFFF != callee:
            raise ValueError(f"{site:#x} is not a call to {callee:#x}")
    for arm, want in ARM_CALLS.items():
        calls = 0
        for ins in md.disasm(image[arm - CODE_BIAS:arm - CODE_BIAS + 0x400], arm):
            if ins.mnemonic == "call" and ins.operands[0].imm & 0xFFFFFFFF == POINTER_HELPER:
                calls += 1
            if ins.mnemonic.startswith("ret"):
                break
        if calls != want:
            raise ValueError(f"adjuster arm {arm:#x} has {calls} pointer-helper calls, expected {want}")
    used = {arm for kind, _index, _entry, _fields, arm in rows(image) if arm is not None}
    if used - set(ARM_CALLS) or used - set(ARM_EFFECT):
        raise ValueError("an adjuster arm has no effect line or call count")


def marked(text):
    try:
        start = text.index(BEGIN) + len(BEGIN)
        end = text.index(END, start)
    except ValueError as error:
        raise ValueError("save page is missing the selector markers") from error
    body = text[start:end]
    if body.startswith("\n"):
        body = body[1:]
    if body.endswith("\n"):
        body = body[:-1]
    return body


def main():
    parser = lol3_cli.tool_args(__doc__, writes=False)
    args = parser.parse_args()
    try:
        image = image_of(args.data)
        pins(image)
        rendered = table(image)
        if args.check:
            page = marked(PAGE.read_text(encoding="utf-8"))
            if page != rendered:
                raise ValueError("docs/lol3-native-saves.md selector table differs from LOL3.DAT")
            print("CHECK save_selectors: 61 global and 75 level selectors match docs/lol3-native-saves.md")
            return 0
        print(rendered, end="")
    except (OSError, ValueError) as error:
        parser.exit(1, f"save selectors: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
