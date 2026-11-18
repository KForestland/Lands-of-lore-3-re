# Native hit requests and resolution

Addresses refer to the [English retail image](lol3-lmf-reader.md).

**CONFIRMED.** Script opcode 19 jumps through the object dispatcher
to `0x449905`, which calls `0x4E7290`. That helper clears a
72-byte request, copies the two words at command +4/+6, and places
the object and computed magnitude in the request. Mode byte +9
selects the magnitude.

| Mode | Magnitude and site |
|---|---|
| 1 | command u8 +8 times target vtable +0xA0 return, divided by 100 (`0x4E72DF–0x4E72FA`) |
| 2 | same formula using target vtable +0x9C (`0x4E72D3–0x4E72FA`) |
| Other | literal u8 +8 (`0x4E72AF–0x4E72CD`, `0x4E72FD`) |

The complete request is sent to target vtable +0x8C at
`0x4E731C`.

**CONFIRMED.** The resolver at `0x4E2270` checks live fields
of both participants. Its packet dword +0x14 selects a six-slot
switch at `0x4E246B`, using table `0x4E2984`. Slots 0, 1,
3, 4 and 5 share an arm. Slot 2 scales the request using the
two participants' vtable +0xFC returns (`0x4E24D6–0x4E250C`).
At `0x4E2948–0x4E2952` a non-null target receives the completed
packet through vtable +0x80. The object path at `0x446584–0x4465B7`
passes the old quantity from +0x9C, invokes the resolver and applies
new minus old through vtable +0x98.

**UNCONFIRMED.** Concrete virtual-slot meanings by class, all
mitigation masks, and the initial hit request for each weapon and
spell are still open. For the creature class, +0x98/+0x9C are
resolved below; other classes remain open.

## Creature definitions and target quantity

**CONFIRMED.** In all 18 level ODFs, u32 +0x10 and count
+0x48 locate 334 type-tagged field-3 definitions of 147 bytes,
which the creature setup consumes (a few tags are object ids, Q5).
CKEEP's eight rows begin at `CKEEP.WSX+0xD40705`.
The [definition reader](lol3-map-odf-readers.md) maps the
135-byte body and 12-byte type tag. The creature setup at
`0x4B4589–0x4B45A2` uses a 139-byte stride for its definition
argument. `0x4B4882` stores that pointer at object +0x34.
It installs vtable `0x53FE28` at `0x4B45AA` and copies
32 bytes from its definition's resolved type block +8 to
object +0xA0 (`0x4B45C1–0x4B45D7`).

**CONFIRMED.** Creature vtable `LOL3.DAT+0x13E628` has
the following interpreted slots. Slot 0 returns type 2
(`0x4B9170`).

| Slot | Destination | Native effect |
|---|---|---|
| +0x3C | `0x4B63B0` | Frame update and behavior/animation processing |
| +0x8C | `0x4B9190` | Hit receiver |
| +0x98 | `0x4BA870` | Adds signed argument to current u16 +0xDC and calls setter `0x4BA6F0` |
| +0x9C | `0x4BA8A0` | Reads current u16 +0xDC |
| +0xA0 | `0x4BA800` | Reads upper quantity u16 +0x108 |

The setter clamps to +0x108 at `0x4BA742–0x4BA765`.
Zero with object +0x114 bit 0x200 set can enter
`0x4BA360`, subject to +0x110 bit 0x80. The other
zero branch uses 1 (`0x4BA710–0x4BA742`). Behavior
0x0F takes a separate path that sets +0xDC to zero
(`0x4BA6F4–0x4BA706`). The current quantity and zero
path confirm +0xDC's health role.

**CONFIRMED.** The creature hit receiver clears +0x114
bit 0x20 and rejects a hit from itself
(`0x4B9190–0x4B91BE`). At `0x4B98D0` it calls the shared
resolver `0x4E2270`. If resolved loss +0x24 is nonzero it passes
result +0x2C to the setter and loss +0x24 to `0x4B8530`
(`0x4B98DD–0x4B9907`). The resolver rounds its accumulated
fixed-point loss as `(value + 65535) >> 16`, clamps loss
to starting health +0x28, and writes
`max(0, starting health − loss)` at +0x2C
(`0x4E28AD–0x4E2945`). In the middle of that path, a
kind-1 hit by the player adds 10 if the test for ID 0x13A
succeeds. Zero computed loss with a non-null attacker
becomes 1 before the health clamp
(`0x4E28BC–0x4E2902`). Full mitigation masks remain
**UNCONFIRMED**.

## Behavior and action modes

**CONFIRMED.** The frame route calls `0x4B4A70` to copy
requested behavior +0xFD to current +0xFC and requested
action +0xFF to current +0xFE. A changed behavior resets
dword +0x118 to 1 (`0x4B4A70–0x4B4AA6`).
The behavior table is at `0x4B5C44` and has 15 slots
(`0x4B4BD6–0x4B4BF0`). The following are dispatch effects
visible before further class-specific branches.

| Mode | Mode entry | First operation |
|---:|---|---|
| 0, 12 | `0x4B4D7E` | Indexes the 8-byte waypoint table `[0x5701A4]` with actor u16 +0xD4. |
| 1, 11 | `0x4B5C19` | Common return. |
| 2 | `0x4B4DFC` | Tests shared byte `[0x7D75E4]`, object +0x118 bit 0x200 and target +0x68. |
| 3 | `0x4B4BF7` | Takes the point path when +0x110 bit 0x800 is set or +0x68 is null. |
| 4 | `0x4B57C6` | If +0x6C is null, calls `0x4BF340(actor, 1, 0)`, then tests +0xF2. |
| 5 | `0x4B57AA` | With +0x114 bit 0x80 clear, selects player as +0x6C and copies byte +0xF0 to +0xF2. |
| 6 | `0x4B5AA3` | Calls `0x4BC8C0(actor, 0, 3)`. |
| 7 | `0x4B4E49` | If +0xF8 is 0xFF, jumps into mode 6. Otherwise follows the path at `0x4B5AB5`. |
| 8 | `0x4B50FC` | Supplies a null-target fallback through `0x4BF340`, then tests +0xF2 and +0x118 bit 0x100. |
| 9 | `0x4B5303` | Same null-target fallback. Its flag-set branch tests +0xF2 bits 0 and 2. |
| 10 | `0x4B546B` | With +0xF2 & 7, copies coordinates from target +0x6C to actor +0x94 and following fields. |
| 13 | `0x4B54BE` | Similar target and observation gate, with a separate continuation. |
| 14 | `0x4B5C02` | Clears actor +0x118 bits 4–5 and calls `0x4BA9A0(actor, 0)`. |

**CONFIRMED.** The secondary action byte +0xFE has an
18-slot table at `0x4B757C` (`0x4B6A19–0x4B6A2A`).
Current behavior 0x10 has a separate path
(`0x4B69E9–0x4B6A14`). Behavior 0x0F suppresses ordinary
hit processing in `0x4B9236–0x4B925E`.
The animation names and all secondary actions remain
**UNCONFIRMED**. Match a requested-action producer to
the slot's effect and a subsequent animation sequence before
assigning a gameplay name.
