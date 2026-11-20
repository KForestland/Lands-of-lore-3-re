#!/usr/bin/env python3
"""Read LOL3.DAT and list every save selector's live bytes, length, flags and adjuster.

  lol3_save_selectors.py --data DAT
  lol3_save_selectors.py --data DAT --check

The global loader (0x436D43) and the global writer (0x43789D) call 0x438140.
The level reader (0x43745B) and the level writer (0x437F3A) call 0x438940.
--check reads the two selector counts from the bound compare at the head of each
descriptor, requires the call sites, jump tables, padding and adjuster bounds
above, counts the 0x43C410 calls in each adjuster arm, and requires the selector
table on the save page to match those arms. It also reads the 90 table slots
of level selector 38 (86 distinct arm addresses; slot 89 is the shared tail)
and requires that table to match. Without Capstone, --check verifies the
dispatch addresses in the page and the original code and table bounds.
"""
from cli_errors import run_cli
from hashlib import sha256
from pathlib import Path

import lol3_cli
from lol3_script_framing import CODE_BIAS, RETAIL_PE

try:
    from capstone import Cs, CS_ARCH_X86, CS_MODE_32
    from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_OP_REG
except ModuleNotFoundError as error:
    if error.name != "capstone":
        raise
    Cs = None

PAGE = Path(__file__).resolve().parents[1] / "docs" / "lol3-native-saves.md"
BEGIN = "<!-- selectors:begin -->"
END = "<!-- selectors:end -->"
NESTED_BEGIN = "<!-- nested-arms:begin -->"
NESTED_END = "<!-- nested-arms:end -->"
# Level selector 38 calls 0x43A4E0. Byte +0x64 is compared with 0x94 (ja),
# so indexes 0 through 0x94 are accepted. The byte at 0x43AFD8 translates
# the index into one of 90 slots, and the dword table at 0x43AE70 holds their
# arm addresses (86 distinct; slot 89 is the shared tail 0x43AE12).
NESTED_CMP = 0x43A52D
NESTED_MAP = 0x43AFD8
NESTED_TABLE = 0x43AE70
NESTED_TAIL = 0x43AE12
NESTED_JOIN = 0x43AE08
NESTED_BACK = 0x43A528
NESTED_INDEXES = 0x95
NESTED_SLOTS = 90
SHARED_OFFSETS = (0x10, 0x14, 0x34, 0x48, 0x4C)
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
    0x43A12B: "calls 0x43A4E0, which accepts indexes 0 through 0x94 in byte +0x64 and selects one of 90 table slots through the map at 0x43AFD8 and the table at 0x43AE70; the slots are listed after this table",
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


def dispatch_rows(image):
    for kind, descriptor, table_at, count, adjuster, arms, index_map, limit in (
        ("Global", GLOBAL_DESCRIPTOR, GLOBAL_TABLE, GLOBAL_COUNT, GLOBAL_ADJUSTER,
         GLOBAL_ARMS, GLOBAL_MAP, GLOBAL_ADJUST_MAX),
        ("Level", LEVEL_DESCRIPTOR, LEVEL_TABLE, LEVEL_COUNT, LEVEL_ADJUSTER,
         LEVEL_ARMS, LEVEL_MAP, LEVEL_ADJUST_MAX),
    ):
        if u32(image, table_at + 4 * count) != 0x90909090:
            raise ValueError(f"{kind} descriptor padding differs")
        for index in range(count):
            entry = u32(image, table_at + 4 * index)
            if not descriptor < entry < table_at:
                raise ValueError(f"{kind} selector {index} outside descriptor arms")
            arm = None
            if index <= limit:
                slot = image[index_map - CODE_BIAS + index]
                if arms + 4 * slot >= index_map:
                    raise ValueError(f"{kind} selector {index} outside adjuster table")
                arm = u32(image, arms + 4 * slot)
                if not adjuster <= arm < arms:
                    raise ValueError(f"{kind} selector {index} outside adjuster arms")
            yield kind, index, entry, arm


def rows(image):
    md = decoder()
    return [(kind, index, entry, describe(md, image, entry), arm)
            for kind, index, entry, arm in dispatch_rows(image)]


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


def _reg(ins, op):
    if op.type != X86_OP_REG:
        return None
    return ins.reg_name(op.reg)


def _mem(ins, op):
    if op.type != X86_OP_MEM or op.mem.index:
        return None
    return ins.reg_name(op.mem.base), op.mem.disp


def nested_map(image):
    raw = image[NESTED_MAP - CODE_BIAS:NESTED_MAP - CODE_BIAS + NESTED_INDEXES]
    if len(raw) != NESTED_INDEXES or any(slot >= NESTED_SLOTS for slot in raw):
        raise ValueError("selector 38 map is not 149 slots in 0..89")
    return list(raw)


def shared_tail(md, image):
    """The five dwords every arm relocates, then the link back to the switch."""
    offs = []
    va = NESTED_TAIL
    for _ in range(5):
        lea, mov, push_a, push_b, push_c, call = (
            ins_at(md, image, va + delta) for delta in (0, 3, 5, 6, 7, 8)
        )
        base, disp = _mem(lea, lea.operands[1])
        if not (lea.mnemonic == "lea" and _reg(lea, lea.operands[0]) == "eax"
                and base == "esi" and mov.mnemonic == "mov" and mov.op_str == "ecx, edi"
                and [item.op_str for item in (push_a, push_b, push_c)] == ["eax", "eax", "ebp"]
                and call.mnemonic == "call" and call.operands[0].imm & 0xFFFFFFFF == POINTER_HELPER):
            raise ValueError(f"shared tail at {va:#x} is not a pointer-helper call")
        offs.append(disp)
        va = call.address + call.size
    link = ins_at(md, image, va)
    base, disp = _mem(link, link.operands[1])
    add = ins_at(md, image, 0x43AE5A)
    back = ins_at(md, image, 0x43AE5F)
    ret = ins_at(md, image, 0x43AE6A)
    if not (link.mnemonic == "mov" and _reg(link, link.operands[0]) == "esi" and base == "esi" and disp == -0x14
            and add.mnemonic == "add" and add.op_str == "esi, 0x14"
            and back.mnemonic == "jne" and back.operands[0].imm & 0xFFFFFFFF == NESTED_BACK
            and ret.mnemonic == "ret" and ret.op_str == "0xc"):
        raise ValueError("shared tail does not walk [esi-0x14] back to the switch")
    if tuple(offs) != SHARED_OFFSETS:
        raise ValueError(f"shared tail offsets {offs} are not {SHARED_OFFSETS}")
    return offs


def _helper_lea(md, image, ins):
    """A lea of [esi+disp] that 0x43C410 receives, either here or at the join.

    The result is ((displacement, count, stride), next address, joined). A stride
    of 0 is one dword. Slot 7's second lea is 0x14 dwords from +0x7C, step 4.
    """
    if ins.mnemonic != "lea":
        return None
    base, disp = _mem(ins, ins.operands[1])
    dest = _reg(ins, ins.operands[0])
    if base != "esi" or dest == "ecx":
        return None
    nxt = ins_at(md, image, ins.address + ins.size)
    if dest == "eax" and nxt.mnemonic == "jmp" and nxt.operands[0].type == X86_OP_IMM and nxt.operands[0].imm & 0xFFFFFFFF == NESTED_JOIN:
        return (disp, 1, 0), nxt.address + nxt.size, True
    va = ins.address + ins.size
    item = nxt
    count = 1
    if dest == "edi" and item.mnemonic == "mov" and _reg(item, item.operands[0]) == "ebx" and item.operands[1].type == X86_OP_IMM:
        count = item.operands[1].imm
        va = item.address + item.size
        item = ins_at(md, image, va)
        if item.mnemonic != "mov":
            raise ValueError(f"counted lea at {ins.address:#x} does not reload ecx")
        va = item.address + item.size
        item = ins_at(md, image, va)
    seq = []
    for _ in range(5):
        seq.append(item)
        va = item.address + item.size
        item = ins_at(md, image, va)
    call = next((entry for entry in seq if entry.mnemonic == "call"), None)
    pushes = [entry.op_str for entry in seq if entry.mnemonic == "push"]
    if not (call is not None and call.operands[0].imm & 0xFFFFFFFF == POINTER_HELPER and pushes[:3] == [dest, dest, "ebp"]):
        raise ValueError(f"lea at {ins.address:#x} is not passed to the pointer helper")
    va = call.address + call.size
    if count == 1:
        return (disp, 1, 0), va, False
    add = ins_at(md, image, va)
    dec = ins_at(md, image, add.address + add.size)
    branch = ins_at(md, image, dec.address + dec.size)
    if not (add.mnemonic == "add" and add.op_str == f"{dest}, 4" and dec.mnemonic == "dec"
            and branch.mnemonic == "jne"):
        raise ValueError(f"counted lea at {ins.address:#x} is not a step-4 loop")
    return (disp, count, 4), branch.address + branch.size, False


def arm_facts(md, image, start):
    """Setup call, the vtable left at +0, the vtable the setup call sees, and extra dwords."""
    if start == NESTED_TAIL:
        return None, None, (None, None), ()
    va = start
    seen = set()
    setup = None
    setup_at = None
    stores = []
    extra = []
    while va not in seen and len(seen) < 40:
        if va >= NESTED_TAIL:
            break
        seen.add(va)
        ins = ins_at(md, image, va)
        if ins is None:
            raise ValueError(f"no instruction at {va:#x}")
        found = _helper_lea(md, image, ins)
        if found is not None:
            item, va, joined = found
            extra.append(item)
            if joined:
                break
            continue
        if ins.mnemonic == "lea":
            base, disp = _mem(ins, ins.operands[1])
            if _reg(ins, ins.operands[0]) == "ecx" and base == "esi":
                setup_at = disp
        if ins.mnemonic == "mov" and len(ins.operands) == 2:
            base, disp = _mem(ins, ins.operands[0]) or (None, None)
            if base == "esi" and disp == 0 and ins.operands[1].type == X86_OP_IMM:
                stores.append(ins.operands[1].imm & 0xFFFFFFFF)
        if ins.mnemonic == "call" and ins.operands[0].type == X86_OP_IMM:
            target = ins.operands[0].imm & 0xFFFFFFFF
            if target != POINTER_HELPER:
                if setup is not None:
                    raise ValueError(f"arm {start:#x} has two setup calls")
                setup = target
        if ins.mnemonic == "jmp" and ins.operands[0].type == X86_OP_IMM:
            dest = ins.operands[0].imm & 0xFFFFFFFF
            if dest in (NESTED_JOIN, NESTED_TAIL) or dest >= NESTED_TAIL:
                break
            va = dest
            continue
        if ins.mnemonic.startswith("ret"):
            raise ValueError(f"arm {start:#x} returned before the shared tail")
        va += ins.size
    else:
        raise ValueError(f"arm {start:#x} did not reach the shared tail")
    during = stores[0] if len(stores) > 1 else None
    vtable = stores[-1] if stores else None
    if len(stores) > 2:
        raise ValueError(f"arm {start:#x} stores {len(stores)} vtables")
    return setup, setup_at if during is not None else None, (during, vtable), tuple(extra)


def nested_rows(image):
    md = decoder()
    slots = nested_map(image)
    shared_tail(md, image)
    raw = image[NESTED_CMP - CODE_BIAS:NESTED_CMP - CODE_BIAS + 26]
    if raw != bytes.fromhex("3d940000000f87da08000033c98a88d8af4300ff248d70ae4300"):
        raise ValueError("selector 38 switch is not cmp 0x94, the map, and the 90-arm table")
    if NESTED_MAP != NESTED_TABLE + NESTED_SLOTS * 4:
        raise ValueError("the byte map does not start immediately after the arm table")
    targets = [u32(image, NESTED_TABLE + 4 * slot) for slot in range(NESTED_SLOTS)]
    rows = []
    for slot, target in enumerate(targets):
        if not NESTED_CMP < target <= NESTED_TAIL:
            raise ValueError(f"slot {slot} target {target:#x} is outside the switch")
        setup, passed, pair, extra = arm_facts(md, image, target)
        during, vtable = pair
        rows.append((slot, target, setup, passed, during, vtable, extra))
    expect = {
        0: (0x43A547, 0x43C250, None, None, 0x53E908, ((0x68, 1, 0), (0x80, 1, 0))),
        7: (0x43A5F7, 0x43B0F0, None, None, 0x53E118, ((0x78, 1, 0), (0x7C, 0x14, 4))),
        8: (0x43A63A, 0x43B0F0, None, None, 0x53DFF8, ((0x68, 1, 0),)),
        18: (0x43AC90, 0x43B090, 0x38, 0x539AC0, 0x539880, ((0x80, 1, 0),)),
        81: (0x43ADAA, 0x43B090, 0x38, 0x539AC0, 0x538E48, ((0x70, 1, 0),)),
        89: (NESTED_TAIL, None, None, None, None, ()),
    }
    for slot, want in expect.items():
        if rows[slot][1:] != want:
            raise ValueError(f"slot {slot} decoded {rows[slot][1:]}, expected {want}")
    return slots, rows


def nested_table(image):
    slots, rows = nested_rows(image)
    counts = {}
    for slot in slots:
        counts[slot] = counts.get(slot, 0) + 1
    if [counts[slot] for slot in (89, 88, 75, 87, 54)] != [48, 6, 5, 3, 2]:
        raise ValueError("selector 38 slot counts changed")
    if sum(1 for count in counts.values() if count == 1) != 85 or len(counts) != 90:
        raise ValueError("selector 38 does not use all 90 arms")
    distinct = len({target for _slot, target, *_rest in rows})
    if distinct != 86:
        raise ValueError(f"selector 38 has {distinct} distinct arm addresses, not 86")
    if [row[0] for row in rows if row[5] is None] != [89]:
        raise ValueError("a slot other than 89 stores no vtable")
    lines = [
        "Indexes 0 through 0x94 (149 values) select these 90 table slots. Slot 89 is selected by 48 indexes, slot 88 by 6, slot 75 by 5, slot 87 by 3, slot 54 by 2, and every other slot by one index.",
        "",
        f"The 90 slots hold {distinct} distinct arm addresses: slots 18 and 20, 43 and 45, 46 and 48, and 87 and 88 share one. Slot 89 is the shared tail `0x43AE12` itself, the same target the `ja` at `0x43A532` takes for an index above 0x94; it stores no vtable. The other 89 slots each store a vtable at +0 before they reach the tail.",
        "",
        "Every slot, and an index above 0x94, then relocates the dwords at +0x10, +0x14, +0x34, +0x48 and +0x4c through `0x43C410`. The tail then loads the dword at `[esi-0x14]`. It returns when that dword is zero; otherwise it adds `0x14` and jumps back to the switch at `0x43A528`.",
        "",
        "| Slot | Arm | Setup call | Vtable left at +0 | Further dwords relocated |",
        "|---:|---|---|---|---|",
    ]
    for slot, target, setup, passed, during, vtable, extra in rows:
        if setup is None:
            setup_text = "none"
        elif during is None:
            setup_text = f"`{setup:#x}`"
        else:
            setup_text = f"`{setup:#x}` passing +{passed:#x} while +0 is `{during:#x}`"
        vtable_text = "none" if vtable is None else f"`{vtable:#x}`"
        parts = []
        for disp, count, stride in extra:
            if count == 1:
                parts.append(f"+{disp:#x}")
            else:
                parts.append(f"{count:#x} dwords from +{disp:#x} step {stride}")
        extra_text = "none" if not parts else ", ".join(parts)
        lines.append(f"| {slot} | `{target:#x}` | {setup_text} | {vtable_text} | {extra_text} |")
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
    nested_rows(image)


def marked(text, begin=BEGIN, end_mark=END):
    try:
        start = text.index(begin) + len(begin)
        end = text.index(end_mark, start)
    except ValueError as error:
        raise ValueError("save page is missing the selector markers") from error
    body = text[start:end]
    if body.startswith("\n"):
        body = body[1:]
    if body.endswith("\n"):
        body = body[:-1]
    return body


def check_dispatch_page(image, text):
    """Check the stored tables and their marked page rows without a disassembler."""
    for va, hex_bytes in (
        (GLOBAL_DESCRIPTOR, "8b44240483f83c0f87f8060000ff248548884300"),
        (LEVEL_DESCRIPTOR, "8b44240483f84a0f87120b0000ff248560944300"),
        (0x4395B3, "83f83c0f87ff04000033c98a88ec9a4300ff248dc49a4300"),
        (0x439B54, "83f8480f87ab08000033c98a8888a44300ff248d10a44300"),
        (NESTED_CMP, "3d940000000f87da08000033c98a88d8af4300ff248d70ae4300"),
    ):
        expected = bytes.fromhex(hex_bytes)
        at = va - CODE_BIAS
        if image[at:at + len(expected)] != expected:
            raise ValueError(f"save selector dispatch differs at {va:#x}")
    for site, callee in CALL_SITES:
        at = site - CODE_BIAS
        if (image[at] != 0xE8 or
                site + 5 + int.from_bytes(image[at + 1:at + 5], "little", signed=True) != callee):
            raise ValueError(f"{site:#x} is not a call to {callee:#x}")

    def columns(block, *indices):
        for line in block.splitlines()[2:]:
            parts = line.split("|")
            if len(parts) <= max(indices) + 1:
                raise ValueError("incomplete save selector page row")
            yield tuple(parts[i].strip() for i in indices)

    expected = [(f"{kind} {index}", f"`{entry:#x}`", f"`{arm:#x}`" if arm is not None else "none")
                for kind, index, entry, arm in dispatch_rows(image)]
    if list(columns(marked(text), 1, 2, 7)) != expected:
        raise ValueError("save page selector addresses differ from LOL3.DAT")

    slots = nested_map(image)
    targets = [u32(image, NESTED_TABLE + 4 * slot) for slot in range(NESTED_SLOTS)]
    if (len(set(slots)) != NESTED_SLOTS or len(set(targets)) != 86
            or targets[-1] != NESTED_TAIL or not all(NESTED_CMP < target <= NESTED_TAIL for target in targets)):
        raise ValueError("level selector 38 slot or arm bounds differ")
    expected = [(str(slot), f"`{target:#x}`") for slot, target in enumerate(targets)]
    _, heading, rows_text = marked(text, NESTED_BEGIN, NESTED_END).partition("| Slot |")
    if not heading or list(columns(heading + rows_text, 1, 2)) != expected:
        raise ValueError("save page nested arm addresses differ from LOL3.DAT")


def main():
    parser = lol3_cli.tool_args(__doc__, writes=False)
    args = parser.parse_args()
    try:
        image = image_of(args.data)
        if Cs is None:
            if not args.check:
                raise ValueError("install Capstone to list decoded save selector instructions")
            check_dispatch_page(image, PAGE.read_text(encoding="utf-8"))
            print("CHECK save_selectors: 61 global, 75 level and 90 nested dispatch rows match; "
                  "instruction decoding uses optional Capstone")
            return 0
        pins(image)
        rendered = table(image)
        nested = nested_table(image)
        if args.check:
            text = PAGE.read_text(encoding="utf-8")
            if marked(text) != rendered:
                raise ValueError("docs/lol3-native-saves.md selector table differs from LOL3.DAT")
            if marked(text, NESTED_BEGIN, NESTED_END) != nested:
                raise ValueError("docs/lol3-native-saves.md nested arm table differs from LOL3.DAT")
            print("CHECK save_selectors: 61 global and 75 level selectors match docs/lol3-native-saves.md")
            return 0
        print(rendered, end="")
    except (OSError, ValueError) as error:
        parser.exit(1, f"save selectors: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
