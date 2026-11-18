# LoL3 MAP script opcodes and framing

Addresses use the [English retail PE convention](lol3-lmf-reader.md).
The [object and script reader](lol3-object-dispatch.md) gives the MAP
header offsets, predicate reader and route from an object event to
a script command.

**CONFIRMED.** The length function at `0x4E56A0` subtracts one from
u8 command +0, bounds the result to 0xEF, reads an index byte at
`0x4E5790 + opcode - 1`, and jumps through
`0x4E56F0 + 4 * index`. An arm either returns a constant or uses
the zero return at `0x4E56EF`. The table below lists the 39
positive sizes (40 jump slots; slot 39 is the zero return). The low destinations are the 28 object slots at
`0x449A1C`, indexed by opcode minus one. The map destination uses
the index byte at `0x4E5AB4 + opcode - 0x15` and jump slots at
`0x4E5A7C` (`0x4E59A3–0x4E59BE`). The group runner handles an
initial 0xF0 itself (`0x4E58A2–0x4E58B6`).

| Opcode | Bytes | Native case VA | Stored records in 18 MAPs |
|---|---:|---|---:|
| 0x01 | 6 | `0x447F31` | 1,175 |
| 0x02 | 6 | `0x447FB0` | 1,941 |
| 0x03 | 16 | `0x448020` | 1,799 |
| 0x05 | 6 | `0x447E3E` | 4,496 |
| 0x06 | 6 | `0x447E59` | 1,204 |
| 0x07 | 6 | `0x447E66` | 1,494 |
| 0x08 | 8 | no case (`0x4499EB` is the object switch's default exit, the `ja` target at `0x447E31`) | 0 |
| 0x09 | 6 | `0x447E81` | 10,110 |
| 0x0B | 8 | `0x448298` | 0 |
| 0x0D | 8 | `0x447F31` | 5,269 |
| 0x0E | 8 | `0x447E8E` | 1,588 |
| 0x0F | 8 | `0x4484B7` | 219 |
| 0x10 | 6 | `0x447F44` | 3,047 |
| 0x11 | 6 | `0x447F74` | 351 |
| 0x12 | 18 | `0x447E9B` | 288 |
| 0x13 | 10 | `0x449905` | 15 |
| 0x14 | 10 | `0x448055` | 2,773 |
| 0x15 | 6 | `0x447F97` | 25 |
| 0x16 | 18 | `0x4480A4` | 2,642 |
| 0x17 | 6 | `0x447F51` | 80 |
| 0x18 | 10 | `0x448033` | 2 |
| 0x19 | 16 | `0x4482AC` | 53 |
| 0x1A | 45 | `0x4482DB` | 151 |
| 0x1B | 10 | `0x449912` | 1,654 |
| 0x1C | 38 | `0x448320` | 217 |
| 0xC4 | 12 | `0x4E59D3` | 453 |
| 0xC5 | 6 | `0x4E59E1` | 584 |
| 0xC6 | 6 | `0x4E59FD` | 217 |
| 0xC7 | 6 | `0x4E5A27` | 159 |
| 0xC8 | 6 | `0x4E5A43` | 0 |
| 0xC9 | 6 | `0x4E5A35` | 0 |
| 0xCC | 8 | `0x4E59C5` | 237 |
| 0xCD | 8 | no case (`0x4E5A77` is the high switch's range return, `pop esi; ret 4`) | 0 |
| 0xCE | 6 | `0x4E5A0B` | 4 |
| 0xCF | 6 | `0x4E5A19` | 149 |
| 0xD0 | 8 | `0x4E5A51` | 111 |
| 0xD1 | 10 | `0x4E5A5F` | 0 |
| 0xD2 | 6 | `0x4E5A6D` | 127 |
| 0xF0 | 6 | `0x4E5880` | 12,306 |

## Array commands

**CONFIRMED.** The level array pointer at `0x5D54BC` is
initialized and read at `0x440A20–0x440A63`, and released
at `0x43F4D6–0x43F4ED`. The shared array at `0x5D54C0`
is read at `0x440A70–0x440AB6` and saved by global
selector 1 (`0x43817D–0x4381A3`). Each arm uses u8
command +4 as the index.

| Opcode | Array | Operation and native evidence |
|---|---|---|
| 0xC6 | Level | Store u8 +5 at `0x4E5BD8–0x4E5BDE`. |
| 0xC7 | Shared | Store u8 +5 at `0x4E5C38–0x4E5C3E`. |
| 0xC8 / 0xC9 | Shared / level | Store the low byte of `0x44AA40(0, (u8(+5) << 5) + 31) >> 5` (a thiscall with ecx = `0x55D3D0`, `0x4E5C95` / `0x4E5CD5`) at `0x4E5C9A–0x4E5CBF` / `0x4E5CDA–0x4E5CFA`. |
| 0xCE | Shared | Add s8 +5 and clamp to 0–255 at `0x4E5C58–0x4E5C77`. |
| 0xCF | Level | Add s8 +5 and clamp to 0–255 at `0x4E5BF8–0x4E5C17`. |

**CONFIRMED.** Opcode 0xCC with s16 +4 = −1 addresses the
56-byte region row selected by u16 +2 and calls `0x4A75F0` with
u16 +6 (`0x4E63C0–0x4E63E9`). Value −2 in the same operand
writes the low byte of +6 to region byte +0x22
(`0x4E63F6–0x4E641D`). Other values write u16 +6 to
the selected 8-byte auxiliary row and set its +5 bit 0x40
(`0x4E6423–0x4E643F`).

## What the group index addresses

**CONFIRMED.** A flat walk consumes all 431,495 bytes at the
MAP +0x44/+0x8C ranges. The sets of record starts exactly equal
the sets of u32 offsets at MAP +0x4C/+0x98 in all 18 files.
The 54,966 index entries address 54,940 starts. HWHIT has 15
repeated offsets and MLOW2 has 11. The other 16 have one index
entry per framed record. There are 12,306 0xF0 group headers
and 33 observed opcodes including that header. This describes
the archive bytes. Which entry starts an execution depends on
the event caller at `0x4A8290–0x4A82A6`.

**CONFIRMED.** At entry to `0x4E5880`, 0xF0 takes byte +4 as
the number of following size-decoded records. An initial 0x1B
takes byte +9 as the remaining count. When reached during a
group, 0x1B receives the current count and a runtime dword
before dispatch (`0x4E58B8–0x4E58C3`,
`0x4E58DB–0x4E58EE`). All 1,654 stored 0x1B records have
+9 zero across the 18 MAP ranges. The object arm can resume
a queued 0x1B with a call back to the group runner at `0x4499E1`.

**CONFIRMED.** Fourteen MLOW2 headers have another 0xF0 within
the range described by their command count. For instance
`MLOW2.WSX+0x14D0E89` has count 3 and the third record at
+0x14D0E9B is another header of count 3. As an inner record,
0xF0 is routed to the high queue and its ordinary high switch
takes the range return (`0x4E58F4–0x4E592F`,
`0x4E59A7–0x4E59B0`). A parser can preserve the raw
boundaries. Treating these records as a recursively executed
tree assigns a behavior that is **UNCONFIRMED**. To settle
whether this exact archive pair is executed in context, follow
both index references to their event callers and record which
entry is passed to `0x4E5880`.

Run `python3 tools/lol3_script_framing.py --data DAT --check` on
the English retail files. The tool reads the size table directly
from the supplied executable and reports aggregate counts.

**UNCONFIRMED.** The native switch cases identify entry sites
for individual effects. To settle the indirect object commands,
resolve the placement's vtable before following the slot called
by the case. For one size-specific example, opcode 0x1A checks
`[0x600854]` at `0x4482DB`, then passes operands +4, +0x10
and pointers +0x14/+0x1D, plus the result of `0x41EDE0(+8, +0xC)` (`0x4482F0–0x4482F8`), at `0x448300–0x448316`.
Trace `0x48EBE0` from that call before naming the effect.
