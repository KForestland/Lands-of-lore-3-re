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

The effects below are **CONFIRMED** to the address or operation
stated. An **UNCONFIRMED** marker qualifies the continuation.
Each observed opcode has one original WSX offset. The six absent
opcodes have an original executable witness. Those operands are
not observed in the 18 MAP ranges.

| Opcode | Bytes | Native case VA | Stored records in 18 MAPs | File witness | Native effect |
|---|---:|---|---:|---|---|
| 0x01 | 6 | `0x447F31` | 1,175 | `BUPP1.WSX+0x18C8633` | Calls target vtable +0xC0 with the command and retains the return (0x447F31–0x447F3C). The class-specific result is **UNCONFIRMED**. |
| 0x02 | 6 | `0x447FB0` | 1,941 | `BUPP1.WSX+0x18C800C`, +4=32 | For +4 = 2 or 3, resolves the object from +1/u16 +2 and calls player helper 0x415540 or 0x415620. Other values route to player command 0x410AA0 (0x447FB0–0x448016). |
| 0x03 | 16 | `0x448020` | 1,799 | `BUPP1.WSX+0x18CA79F` | Calls target vtable +0xC0 and keeps its result (0x448020–0x44802B). Class-specific item effects are **UNCONFIRMED** here. |
| 0x05 | 6 | `0x447E3E` | 4,496 | `BUPP1.WSX+0x18C83C9` | Calls target virtual +0xC8 with u8 +4 and +5 (0x447E3E–0x447E4E). |
| 0x06 | 6 | `0x447E59` | 1,204 | `BUPP1.WSX+0x18C9F4B`, +4=1 | Runs the object action switch on +4 through 0x446290, table 0x446438 (0x447E59–0x447E5C). |
| 0x07 | 6 | `0x447E66` | 1,494 | `BUPP1.WSX+0x18CF98D` | Calls target virtual +0xCC with u8 +4/+5 (0x447E66–0x447E76). |
| 0x08 | 8 | no case (`0x4499EB` is the object switch's default exit, the `ja` target at `0x447E31`) | 0 | `LOL3.DAT+0xE4B97`, size selector | The object table slot reaches the common exit without a command body (0x4499EB). |
| 0x09 | 6 | `0x447E81` | 10,110 | `BUPP1.WSX+0x18C7EB1`, +4=21 | Dispatches object property u8 +4 through 0x447680 and table 0x447AE0. For instance selector 1 sets object +0x18 bit 0x4000 (0x4476B3–0x4476B9). |
| 0x0B | 8 | `0x448298` | 0 | `LOL3.DAT+0xE4B9A`, size selector | Passes u16 +4 to 0x4EED60 at 0x44829F. Effects beyond the call are **UNCONFIRMED**. |
| 0x0D | 8 | `0x447F31` | 5,269 | `BUPP1.WSX+0x18C8A95` | Calls target virtual +0xC0 with the complete command (0x447F31–0x447F3C). |
| 0x0E | 8 | `0x447E8E` | 1,588 | `BUPP1.WSX+0x18C85F3`, +4=4 | Selects kind-2 timer by u8 +6, then uses u8 +4 as the operation 0–6 and +5 as its argument (0x44676C–0x4467CD). |
| 0x0F | 8 | `0x4484B7` | 219 | `BUPP1.WSX+0x18C8CBD` | Builds a point 10 fixed-point world units ahead of the target and a second point from selector +5/u16 +6, then reads action +4 (0x4484DA–0x4485C5). Action-specific effects are **UNCONFIRMED**. |
| 0x10 | 6 | `0x447F44` | 3,047 | `BUPP1.WSX+0x18C7FCD`, +4=1 | Writes command u8 +4 to object state +0x31 (0x447F44–0x447F49). |
| 0x11 | 6 | `0x447F74` | 351 | `BUPP1.WSX+0x18CA4F3`, +4=1 | Adds command s8 +4 to unsigned object state +0x31 and clamps to 0–255 (0x447F74–0x447F8F). |
| 0x12 | 18 | `0x447E9B` | 288 | `BUPP1.WSX+0x18C8A71` | Uses a sequence slot at 0x600828. With flag +0xA bit 0x20, resets progress, clears the slot and sends value 6 to the object matcher (0x447EA1–0x447ED8). |
| 0x13 | 10 | `0x449905` | 15 | `EWOD1.WSX+0x1894F72` | Fills and submits a hit request using two mask words, magnitude u8 +8 and mode +9 (0x449908 → 0x4E7290). |
| 0x14 | 10 | `0x448055` | 2,773 | `BUPP1.WSX+0x18C7EF9` | Passes u16 resource ID +4, current object and a pointer to +6 to 0x422C40 (0x44806A–0x44807D). |
| 0x15 | 6 | `0x447F97` | 25 | `CKEEP.WSX+0xD0546C` | Passes unsigned bytes +4 and +5 to the same indexed function 0x46FA60 called by the map-side arm (0x447F97–0x447FA3). Its full resource effect is **UNCONFIRMED** here. |
| 0x16 | 18 | `0x4480A4` | 2,642 | `BUPP1.WSX+0x18CA0FD` | Compares the identifier at +4 against active object/queue identifiers in branch-specific paths (0x4480C5–0x448110, 0x44819D–0x448212). The admitted branch uses command +8–+0x0B as a dialogue tag (0x448237–0x448287). See the [native dialogue lookup](lol3-dialogue-dispatch.md). |
| 0x17 | 6 | `0x447F51` | 80 | `BUPP1.WSX+0x18C7EED` | Writes the low byte of 0x44AA40(0, (u8(+4) << 5) + 31) shifted right five to object +0x31 (0x447F51–0x447F6C). |
| 0x18 | 10 | `0x448033` | 2 | `BUPP1.WSX+0x18D148A` | Checks flag 4 in byte 0x58C562 and current object 0x5896F4, then normally calls 0x422FA0 with +4/+6. The flag branch enters the continuation of 0x1C (0x448033–0x44809A). |
| 0x19 | 16 | `0x4482AC` | 53 | `BUPP1.WSX+0x18C8D4F` | Reads three dwords at +4/+8/+0xC. Value 5 at +0xC selects 0x434560, otherwise calls 0x434180 (0x4482AC–0x4482D1). |
| 0x1A | 45 | `0x4482DB` | 151 | `BUPP1.WSX+0x18C7FD3` | When 0x600854 is zero, resolves the pair +8/+0xC and calls 0x48EBE0 with the object, +4/+0x10 and pointers +0x14/+0x1D (0x4482DB–0x448316). |
| 0x1B | 10 | `0x449912` | 1,654 | `BUPP1.WSX+0x18CB66B` | Queue marker or continuation. Subcommand +8 takes the four-arm switch at 0x449C84, which can clear object +0x1C bit 0x80000 or process matching queued commands (0x44991C–0x4499E1). |
| 0x1C | 38 | `0x448320` | 217 | `BUPP1.WSX+0x18C9F51` | Gates on 0x600854, derives a position and builds an object through 0x4B1BA0 plus field-setting methods. For example +0xC/+0xE/+0x10 feed 0x4B2DE0 (0x448320–0x44840F). Its game-facing role is **UNCONFIRMED** here. |
| 0xC4 | 12 | `0x4E59D3` | 453 | `BUPP1.WSX+0x18C87E3` | Selects a 56-byte map region by u16 +2 (0x4E5EC0–0x4E5EE2). The per-flag geometry effects remain **UNCONFIRMED**. |
| 0xC5 | 6 | `0x4E59E1` | 584 | `BUPP1.WSX+0x18C83AB`, +4=10 | Selects a map region with u16 +2 and switches on +4 to edit region flags or an associated table row (0x4E5D30–0x4E5E34). |
| 0xC6 | 6 | `0x4E59FD` | 217 | `BUPP1.WSX+0x18C8231`, +4=31 | Stores byte +5 to the level array at index +4 (0x4E5BD0). |
| 0xC7 | 6 | `0x4E5A27` | 159 | `BUPP1.WSX+0x18CAA91`, +4=21 | Stores byte +5 to the shared array at index +4 (0x4E5C30). |
| 0xC8 | 6 | `0x4E5A43` | 0 | `LOL3.DAT+0xE4C57`, size selector | Writes a bounded RNG result to shared-array index +4 (0x4E5C90–0x4E5CBF). |
| 0xC9 | 6 | `0x4E5A35` | 0 | `LOL3.DAT+0xE4C58`, size selector | Writes a bounded RNG result to level-array index +4 (0x4E5CD0–0x4E5CFA). |
| 0xCC | 8 | `0x4E59C5` | 237 | `BUPP1.WSX+0x18CF361` | Uses s16 +4 to select a region update (−1 or −2) or an 8-byte auxiliary row store (0x4E63C0–0x4E643F). |
| 0xCD | 8 | no case (`0x4E5A77` is the high switch's range return, `pop esi; ret 4`) | 0 | `LOL3.DAT+0xE4C5C`, size selector | The map-side table reaches the common return, with no body (0x4E5A77). |
| 0xCE | 6 | `0x4E5A0B` | 4 | `GRULO.WSX+0xCC3986`, +4=9 | Adds s8 +5 at shared-array index +4 and clamps to 0–255 (0x4E5C50–0x4E5C77). |
| 0xCF | 6 | `0x4E5A19` | 149 | `BUPP1.WSX+0x18CFAB5`, +4=29 | Adds s8 +5 at level-array index +4 and clamps to 0–255 (0x4E5BF0–0x4E5C17). |
| 0xD0 | 8 | `0x4E5A51` | 111 | `BUPP1.WSX+0x18C7F4F`, +4=3 | Selects one of five branches by +4. Arm 0 extends a duration to at least u8(+6) × 60 × 65536 and raises byte 0x55D3A6 to at least +5, or clears both when +5 is zero (0x4E66D0–0x4E6758). |
| 0xD1 | 10 | `0x4E5A5F` | 0 | `LOL3.DAT+0xE4C60`, size selector | Uses u16 +2 to find a 44-byte region-group row, directly or via selector 0x90 and the 56-byte region table (0x4E69BD–0x4E6A08). |
| 0xD2 | 6 | `0x4E5A6D` | 127 | `BUPP1.WSX+0x18C7E3F`, +4=0 | Uses +4 to dispatch through the settings table 0x4E6CD8, reading u8 +5 in the admitted arms (0x4E6A80–0x4E6BDE). |
| 0xF0 | 6 | `0x4E5880` | 12,306 | `BUPP1.WSX+0x18C7E39`, +4=3 | At group entry, byte +4 counts following records for the native size walker (0x4E58A2–0x4E58B6). |

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
