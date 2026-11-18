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

### Mode transitions and target inputs

**CONFIRMED.** The constructor copies the initial behavior and
action to both pairs of bytes, accepting behavior 0–16 and action
0–17. Out-of-range values become 6 and 0 respectively
(`0x4B4633–0x4B4691`). The behavior runner starts at
`0x4B4B90`. With actor +0x40 set it forces current mode 10,
selects the player as +0x6C and sets +0xF0 bits 0–2 before
the switch (`0x4B4B9B–0x4B4BD6`). A switch-local transition
changes stack +0x10 and redispatches in the same update. A
requested transition writes +0xFD and is applied by `0x4B4A70`.

| Current behavior | Confirmed continuation and transition inputs |
|---:|---|
| 0 | Point index +0xD4 reads the 8-byte [waypoint](GLOSSARY.md) table `[0x5701A4]`. Waypoint word +4 selects a [surface](GLOSSARY.md). An out-of-range surface index redispatches locally as 6. A valid waypoint enters the waypoint-movement path, with arrival tested in `0x4BCAC0` (`0x4B4D7E–0x4B4EA6`). |
| 1 | Direct return without a mode or target write (`0x4B5C19`). |
| 2 | With shared `[0x7D75E4]` set, +0x118 bit 0x200 or no +0x68 calls target refresh and copies +0x6C to +0x68. Either target reaches `0x4B5527/2D`. If both are null, redispatches locally as 6 (`0x4B4DFC–0x4B4E44`). |
| 3 | +0x110 bit 0x800 or an absent +0x68 takes the point path. A type-1 target temporarily executes mode 4 and restores the old +0xFC. Type 4 supplies a position. Inside the actor's +0x14 virtual range it calls `0x49ED50`, clears destination bit 3 and requests sequence 0x17. Otherwise it moves toward the target. Other target types are cleared (`0x4B4BF7–0x4B4D78`). |
| 4 | Refreshes null +0x6C, then uses +0xF2 & 7 and the +0x118 path bits. It can copy a target point and choose between movement or animation based on distance and the five-way result of `0x4BF730` (`0x4B57C6–0x4B5A96`). |
| 5 | Unless combat flag +0x114 bit 0x80 is set, assigns the player and copies +0xF0 into +0xF2. Falls into mode 4 (`0x4B57AA–0x4B57C6`). |
| 6 | Calls `0x4BC8C0(actor, 0, 3)` and returns. This uses the shared destination and movement helper, with no direct hit call (`0x4B5AA3–0x4B5AB4`, `0x4BC9BC–0x4BCA67`). |
| 7 | +0xF8 = 0xFF redispatches locally as 6. Otherwise +0xF8 selects a four-byte path record and abs(signed +0xF9) selects the waypoint. On arrival the signed index advances, loops to zero or reverses by assigning `2-count`, according to path byte +3 bit 0. It also clears +0x118 mask 0x30 so the next waypoint is loaded (`0x4B4E49–0x4B4E62`, `0x4B5AB5–0x4B5BF4`). |
| 8 | Refreshes null +0x6C. Tests observation byte +0xF2 and +0x118 bit 0x100. It can copy a target point, request a point from `0x4FD6C0`, or retain the selected destination until the distance test succeeds. Arrival clears destination flags (`0x4B50FC–0x4B52F6`). |
| 9 | Refreshes null +0x6C. +0x118 bit 0 together with +0xF2 & 5 and +0x110 bit 0x10 changes the path flags. +0xF2 & 7 can reach the mode-13 continuation. Otherwise it checks arrival, then calls `0x4FD6C0` and `0x4FD760` before selecting or retaining the destination (`0x4B5303–0x4B545E`). |
| 10 | Refreshes null +0x6C. With +0xF2 & 7, copies target XYZ and enters the mode-4 distance continuation. Without those bits, takes the fallback at `0x4B5A41` (`0x4B546B–0x4B54B9`). |
| 11 | Same direct return as 1 (`0x4B5C19`). |
| 12 | Same waypoint path and local mode-6 fallback as 0 (`0x4B4D7E–0x4B4EA6`). |
| 13 | Refreshes null +0x6C. +0xF2 & 7 copies target XYZ and calls movement with type 1. Otherwise requests sequence 0 through the common return (`0x4B54BE–0x4B5522`, `0x4B5C11`). |
| 14 | Clears +0x118 mask 0x30, requests sequence 0 and returns (`0x4B5C02–0x4B5C20`). |
| 15 | The zero-health and hit receiver paths distinguish this mode. Secondary action 15 clears +0x6C, writes 15 to current and requested behavior and clears +0xF2. It can then select action 16 (`0x4BA6F4–0x4BA706`, `0x4B9236–0x4B925E`, `0x4B6BA2–0x4B6C52`). Outside the 0–14 behavior switch at `0x4B4BE7`; the runner returns through `0x4B5C19`. |
| 16 | Frame update bypasses ordinary action dispatch and enters the special sequence branch at `0x4B69E9–0x4B6A14`. It is outside the same 0–14 switch at `0x4B4BE7`. |

**CONFIRMED.** The target refresh helper `0x4BF340` uses
definition byte +0x7A and actor +0x114 bit 0x80. That flag
requests behavior 4 and sets +0xF2 bits 0–2
(`0x4BF34F–0x4BF3BA`). The common movement helper reads
target +0x6C and observation +0xF2 for argument 1, and
target +0x68 and observation +0xF1 for argument 2. It
compares the chosen type with +0x118 bits 4–5 and uses
the destination at +0x94/+0x98 when those bits are set
(`0x4BC8F4–0x4BCA67`).

| Action | Native entry | Confirmed first effect |
|---:|---|---|
| 0 | `0x4B6A31` | Clears selected +0x114 bits and runs the behavior table when +0x110 permits. |
| 1 | `0x4B6A57` | Same gate, with helper `0x4B5CA0`. |
| 2 | `0x4B6A7D` | Calls `0x4B5CC0`. |
| 3 | `0x4B6A98` | Calls `0x4B5F90`. |
| 4, 6 | `0x4B6ACE` | +0x40 chooses `0x4B5CA0` or `0x4B60C0`. |
| 5 | `0x4B6AB3` | Calls `0x4B5FA0`. |
| 7 | `0x4B6AFA` | Sets +0x110 bit 1 and calls `0x4B5CA0` when permitted. |
| 8 | `0x4B6B2B` | Writes 1 to +0x8C, sets +0x118 bit 0x1000 and calls `0x4B5DC0(0x11)`. |
| 9 | `0x4B6B5E` | Calls `0x4B6230` and sets the selected +0x118 flag. |
| 10–12 | `0x4B6B70` | With the shared enable byte set, calls `0x4BAAF0(0, 0, -1)`. |
| 13 | `0x4B6DF3` | Shared continuation. |
| 14 | `0x4B6B81` | Same gate as 10–12, with first argument 0x0B. |
| 15 | `0x4B6BA2` | Enters behavior 15, with possible action-16 transition above. |
| 16 | `0x4B6C7C` | Continuation of the behavior-15 path through `0x4B6CE6` and its sequence checks. |
| 17 | `0x4B6DB3` | Conditionally selects sequence 0x14, falls back to sequence 0 on failure and can reset current action. |

**UNCONFIRMED.** The remaining movement flag names, script
and hit producers for every requested mode, and the animation
names are open. To settle a particular shipped behavior, log
writes to +0xFD and +0xFF and the switch-local stack mode,
and capture +0x68/+0x6C, +0xF1/+0xF2 and +0x118 on that
update. The separate write sites above distinguish initial
mode, requested transitions and switch-local fallbacks.

### Creature animation hits and resolver multipliers

**CONFIRMED.** The frame-advance path selects the forward or
reverse animation frame through `0x4F28F0`
(`0x4B6EB4–0x4B6F1A`). Its payload pointer is at +4 of
the return value. With actor +0x110 bit 0x800000 and shared
byte `0x7D75F2` nonzero, it computes
`floor(frame.u8[2] * actor.u8[0xFA] / 100)`.
A nonzero result becomes request dword +0x1C. The routine
fills the request's words +0/+2 from animation payload
+4/+6, uses actor +0x6C as recipient, actor itself as
attacker, and stores kind 1 and subtype 0xFF. It dispatches
through the recipient's vtable +0x8C at `0x4B7044`
(`0x4B6F6A–0x4B7044`). The source is the selected
animation frame even when the behavior runner has also
issued a movement request in that update.

**CONFIRMED.** The resolver scans packed four-byte
mask pairs and associated one-byte effect selectors. A
nonzero request word +0 or +2 requires an intersection
with its respective mask. Selectors 0 and 1 leave the
current contribution alone. For the remaining selectors
it dispatches through `0x4E299C`
(`0x4E26CF–0x4E2731`).

| Selector | Result on the 16.16 contribution `v` |
|---:|---|
| 2 | `2*v` at `0x4E2738` |
| 3 | `3*v` at `0x4E273F` |
| 4 | `4*v` at `0x4E2747` |
| 5 | `trunc(v/2)` at `0x4E276E` |
| 6 | `trunc(3*v/4)` at `0x4E2785` |
| 7 | Removes this contribution from the normal hit calculation, via `0x4E27A1` and `0x4E281F`. |
| 8 | Gives recipient +0x98 the value ceil(trunc(v/2) / 65536), and zeroes the contribution (`0x4E27AF–0x4E27E9`). |
| 9 | Gives the same slot ceil(v / 65536) and zeroes the contribution (`0x4E27D0–0x4E27E9`). |
| 10 | `trunc(v/4)` at `0x4E274F` |

Arms 5, 6, 7 and 10 also check the resolver's local +0x18
condition and request second-word bit 0x10. With the local
condition set and that bit clear, they keep `v` unchanged.
The game-facing names of the mask families are
**UNCONFIRMED**. Match both mask words from an original
animation payload to the tested mask pair, then compare
the contribution at its table arm before assigning the
element or defense name.
