# Native item definitions and use entry points

Addresses refer to the [English retail image](lol3-lmf-reader.md).

**CONFIRMED.** In the input-name table at `LOL3.DAT+0x14EA08`,
indexes 32–41 name the two bindings for each of five item slots.
The reader at `0x4F338B–0x4F33CE` looks up those names in the user
settings and resolves the configured keys. The store at `0x4F34A5`
writes the key per index into dwords at VA `0x5D4CD8`.

**CONFIRMED.** The definition initializer at `0x4ACD17` reads
139-byte rows. It tests definition flag 2 in the byte at row +0x3F (`0x4ACD4A`, `0x4ACDD5–0x4ACDE4`)
and invokes `0x4AD250` from `0x4ACDE4` when set. That function
dispatches on definition dword +0x73 minus 0x50 with upper bound
0x10A using byte table `0x4AE328` and jump slots `0x4AE20C`.
The arm at `0x4AD275–0x4AD2A6` copies row +0x5B/+0x43 to words
`0x545548/0x54554A` and sets bits depending on row +0x47.
These operations occur during definition loading.

**CONFIRMED.** The name consumer at `0x4AD110` opens
`itemjt.trr` (string at `LOL3.DAT+0x148558`). It queries a numeric
definition ID through `0x409440` at `0x4AD169`. On a hit, it copies
from the returned pointer +4 until the byte-2 delimiter, then stores
the resulting string pointer at `[0x662A9C][id]`
(`0x4AD172–0x4AD1B4`). The archive witness is the 343-entry
`DAT/locallng.wsx+0x5968140`.

**CONFIRMED.** The input builder at `0x466B60` makes six-byte
selector/key rows. The indexed loop at `0x467373–0x46739B` reads
the configured keys and registers them through `0x41DB00`.
The registration reads flag/pointer pairs from `0x545E20`
(`0x41DB53–0x41DB97`). The input event has a release bit 0x800
(`0x41D8A0–0x41D92B`), and a registered handler is called at
`0x41DA2F`.

| Configured indexes | Selectors and callbacks | Native action |
|---|---|---|
| 32–41 | 0x12–0x16, `0x41E560/570/580/590/5A0` | Slots 0–4, on release. `0x41E4B0` checks modifier cells `0x5D5800/04` for alternate routes `0x4305A0` and `0x432E50`. The default uses the HUD slot and calls `0x426D30`, which reaches item use at `0x426F7B`. |
| 46–55 | 0x19–0x1D, `0x41E340/370/3A0/3D0/400` | Slots 5–9, on press. The callbacks directly call `0x4282E0` with ECX `0x583151`. |

## Definition directory

**CONFIRMED.** The `GLOBAL\GLOBAL.ODF` entry at
`GLOBAL.WSX+0x3866` has item table offset u32 +4 = 0x1F0
and count +0x34 = 343. The loader seeks and passes the count
at `0x44057A–0x44059F` to `0x4ACC40`, and the definition
reader consumes count × 139 bytes at `0x4ACCCE–0x4ACD17`.
The table starts at `GLOBAL.WSX+0x3A56`. All 343 keys in
each of the following lookup columns are distinct in that table.

| Row field | Native interpretation and source |
|---|---|
| +0x18 u32 | Identity used by `0x440930–0x440955`. The grant command uses this identity. |
| +0x73 u32 | Numeric lookup key used by `0x440960–0x440985`. Also selects the definition-load cases and item name. |
| +0x14 dword | Overwritten with a runtime resource pointer, advanced by 16 × row u8 +0x2E (`0x4ACE0E–0x4ACE19`). |
| +0x3F dword | Bit 1 invokes the definition-load switch at `0x4ACDE4`. A specific row +0x73 value 7 also sets bits 2 and 3 (`0x4ACD62–0x4ACD8B`) and definition +0x4F bit 0x10 (`0x4ACD89`), the bit the use-effect path tests at `0x4D7C9C`; value 0x3F sets +0x4F bit 0x20 (`0x4ACD94`). Only definition 5 has +0x73 = 7. |
| +0x4F dword | Includes the state sense used by `0x4AD050–0x4AD08D`. Bit 1 of the separate byte-array row `[0x662A90][index]` is interpreted relative to definition bit 1. The two update paths invert the operations for the two senses (`0x4AD090–0x4AD106`). |
| +0x7D u16 | Nonzero disk value `v` becomes `max(1, floor(256/v))` at `0x4ACE1B–0x4ACE3E`. The consumer meaning is **UNCONFIRMED**. |

## Script grants

**CONFIRMED.** Player construction installs the vtable at
`0x538388` (`0x408D80`, `0x40A504`). Table +0xC0
at `LOL3.DAT+0x136C48` resolves to `0x410AA0`. Selector
1 returns the player through `0x41EDE0 → 0x41EE00`.
The opcode-3 dispatch at `0x448025` reaches the player arm.
At `0x410B19–0x410B4B` it checks a game guard and passes
u32 command +4, u8 +0xC and mode 1 or 3 to `0x49EF70`.

**CONFIRMED.** `0x49EF7D` looks up the identity at definition
+0x18 and `0x49EF92` initializes a temporary instance. The
initializer stores the definition pointer at +0, zero at +4,
the supplied byte at +8 and zero at +9 (`0x49E940–0x49E95B`).
The pool routine at `0x49EE80` requests a 16-byte slot,
copies those fields and clears +0xC
(`0x49EED3–0x49EEE6`, `0x49E910–0x49E92D`,
`0x49E560–0x49E577`). When the request mode differs from
2, the routine also calls recipient vtable +0x78 with the
allocated pointer and grant mode (`0x49EEF0–0x49EF0E`).
The byte +8 can be set at grant time. Its purpose for all item
classes remains **UNCONFIRMED**.

**CONFIRMED.** `BUPP1.WSX+0x18CA79F` contains a 16-byte
opcode-3 grant with selector 1 and byte +0xC equal to 4.
Its identity `0xF50F9FCB` matches definition 53 at
`GLOBAL.WSX+0x571D`. Of 1,021 stored selector-1 opcode-3
records across the 18 indexed command streams, 1,010 match
the native +0x18 identity column. The eleven other operands
remain **UNCONFIRMED** as exceptional command contexts.

## Use effects

**CONFIRMED.** Common use `0x4282E0` reads the pointer in
inventory row `[ECX+0x80] + 16*slot`, or the cursor pointer at
`[0x585488]` for cursor use. A null instance or a nonzero
`0x49F170` check returns before dispatch. Definition flag
`+0x3F & 0x0C` goes through `0x433B70` into the
`0x429520` action path. The other branch builds use operation 1
and calls `0x49E960` at `0x4283AF`
(`0x4282E0–0x4283AF`). In the action path, eligible instance
bytes +8 between 101 and 109 are decremented, and that path
chooses operation 13 or 6 (`0x429C18–0x429C9A`).

**CONFIRMED.** `0x49E960` reads the definition dword +0x4B
and, if the request has no recipient, supplies the player
(`0x49E969–0x49E97C`). When definition byte +0x3F bit 1 is
set, it calls table slot 108 at `0x54BAC8`, which points to
`0x4A4520` (`0x49E97C–0x49E992`). Otherwise, after the
operation-specific guards it calls `[0x54B918 + 4*index]`
(`0x49E995–0x49EA0F`). There are 124 consecutive code pointers
in the table. The 258 regular original definitions use 114
distinct indexes. The other 85 definitions all store zero at
+0x4B and take the special arm. This census reads 343 rows at
`GLOBAL.WSX+0x3A56`. For example, definition 53 at +0x571D uses
regular index 2, destination `0x49F6D0`. Definition 77 at +0x6425
uses the [special cast arm](lol3-spell-dispatch.md#player-cast-and-cost).

**CONFIRMED.** A separate effect route at `0x4D7C6E–0x4D7CA0`
reads live object +0x34 as a definition pointer and tests
definition +0x43, instance +0x2A and definition +0x4F bit 0x10.
On the admitted path it fills a 72-byte hit request with mask
0x100, flags 4, kind 5 and subtype 0xFF
(`0x4D7CA2–0x4D7CE7`). It selects the recipient from
`[0x600764]` or `[0x600768]`.

**UNCONFIRMED.** Most regular destination effects remain open.
The input and dispatch paths now identify the exact handler.
For each regular index, use one +0x4B witness from the original
definition table and follow that destination's first state write
or effect request for operation 1. The hit route at `0x4D7C6E`
still needs an original action that reaches it.
