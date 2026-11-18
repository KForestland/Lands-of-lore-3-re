# Native object and script dispatch

Addresses refer to the [English retail PE](lol3-lmf-reader.md).

**CONFIRMED.** The MAP loader installs the command stream from header
u32 +0x44 and byte size +0x8C at `0x43EA72–0x43EA9A`. It reads a
table of u32 group offsets from +0x4C with byte size +0x98 at
`0x43EA36–0x43EA60`. The base and table are held at `0x7DE738`
and `0x7DE748`, respectively. In 18 original level MAP entries these
fields describe 431,495 bytes of commands and 54,966 in-range offsets,
including ones into groups. CKEEP's command bytes start at
`CKEEP.WSX+0xD036F4`. Its 1,746 offsets begin at +0xD07270.

## Events and guards

**CONFIRMED.** The kind-3 walker `0x4A8240` advances by u8 +0 and
stops on zero type or length. It selects kind +1 = 3 and compares
the incoming event with byte +4. After the guard at `0x4A8263`,
it uses u16 +2 as an index into the group-offset table and calls
`0x4E5880` on the resulting command pointer (`0x4A8290–0x4A82A6`).
The caller at `0x4F2A84` fires the matcher before updating object
state byte +0x38 when flags +0x18 contain 0x0400
(`0x4F2A67–0x4F2A8F`). The kind-6 path at `0x4A8900` admits
value +4 = 0x1C and compares byte +5 with its caller's operand.

**CONFIRMED.** The guard checks for kind 0x13 immediately following
the matched record (`0x4F05D0–0x4F0635`). Values below 5000 go to
`0x4F02B0`, where 5-byte predicates come from MAP header +0xBC
and count +0xB8 (`0x43E949–0x43E964`, `0x4F0240–0x4F026C`).
Left and right operand type bytes +1/+3 select switches at
`0x4F02D6` and `0x4F0380`. Operation byte +0 selects equality,
inequality, signed <=, >=, >, <, and boolean AND/OR (IDs 0–7)
at `0x4F046D`. CKEEP's 255 predicates start at file +0xD2F277.
Guard values 5000 and above take the range dispatch
`0x4F0635–0x4F0767`. Their gameplay meanings are **UNCONFIRMED**.

## Command selection

**CONFIRMED.** `0x4E5880` reads an 0xF0 group header's command count
at byte +4 and accepts an unframed single command. It advances
with the native size decoder `0x4E56A0`. That decoder's byte index
table starts at `0x4E5790` and its jump slots at `0x4E56F0`.
An embedded 0x1B command can preserve the remaining count at +9.

| Input | Dispatch and example |
|---|---|
| Commands below 195 | `0x4E58F4–0x4E590E` selects object queue `0x5838A8`. The object helper uses its command's first byte at `0x447E29` and jumps through the 28 slots at `0x449A1C`, indexed by opcode minus one. Opcode 3 calls object vtable +0xC0 (`0x448020–0x448025`). Opcode 5 calls +0xC8 with bytes +4/+5 (`0x447E3E–0x447E4E`). Opcode 6 selects an object action subcommand through table `0x446438` (`0x446290–0x4462C7`). |
| Commands 195 and above | `0x4E591F–0x4E592F` uses queue `0x589760`. `0x4E59A0` dispatches via byte index table `0x4E5AB4` and jump slots `0x4E5A7C`. Through the byte index table, Opcode 0xC6 (198) stores byte +5 to a level-local byte array indexed by +4 (`0x4E59FD → 0x4E5BD0`). Opcode 0xCF (207) adds signed +5 to that array with saturation to 0–255 (`0x4E5A19 → 0x4E5BF0`); its 149 records carry +5 = 255 (96) or 1 (51), i.e. −1 or +1. Opcodes 0xC7 (`0x4E5A27 → 0x4E5C30`) and 0xCE (`0x4E5A0B → 0x4E5C50`) take other arms, not read here. |

**CONFIRMED.** CKEEP group index 0 reads offset zero at +0xD07270.
The group at +0xD036F4 has six-byte header 0xF0 and one child. The
child at +0xD036FA is opcode 9, byte +1 = 3, u16 +2 = 53, +4 = 21.
Its table slot calls `0x447680` at `0x447E84`.

The [opcode table and corpus check](lol3-script-opcodes.md) identify all framing lengths, object and map dispatch cases, and the array operations.

**UNCONFIRMED.** The full set of command effects, producer meanings,
and the concrete object implementations of the virtual slots still
need separate traces. Begin with the low switch above and follow each
virtual slot from the class resolved by the command's selector.
