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
spell are still open. The next check is to resolve +0x9C/+0x98
for a creature of known current and maximum health and confirm
a single difference update through the cited caller.
