# LoL3 event lists, predicates and timers

Addresses use the [retail PE convention](lol3-lmf-reader.md).
The [opcode reference](lol3-script-opcodes.md) describes the command
streams. All section offsets below are relative to the MAP entry.

## Two event pools

**CONFIRMED.** MAP +0x38/+0x80 holds the region-event pool.
`0x43E976–0x43E99E` loads its bytes to `[0x7DEA68]`.
A region descriptor is 44 bytes and supplies a list offset at
its u16 +0x0E (`0x4AC203–0x4AC229`). A matched event u16 +2
gives a byte offset into the separate stream loaded from MAP
+0x3C/+0x84 to `[0x7DE740]` (`0x43E9B6–0x43E9DE`,
`0x4AC450–0x4AC45D`).

**CONFIRMED.** MAP +0x40/+0x88 holds the object-event pool.
`0x43E9F6–0x43EA1E` loads it to `[0x600844]`.
The accessor at `0x44A060–0x44A081` adds object u16 +0x24
unless object +0x18 bit 0x1000 is set. It also establishes the
bound object at `[0x600850]`. A matched event u16 +2 instead
indexes the u32 command offsets from MAP +0x4C
(`0x4A8290–0x4A82A6`).

**CONFIRMED.** Each row begins with u8 length and u8 kind. The
walk advances by length and stops at kind zero or length zero
(`0x4A8255–0x4A8288`). The following counts are physical records
from a flat length walk over the two MAP ranges in all 18 levels.
Every row fits its range. For kinds with a group reference, the
u16 +2 values are within the matching stream or index bounds.
The terminator rows and the kind-1 rows have separate uses. **CONFIRMED.** Every kind-1 row directly follows a terminator row. `0x4F21B0` walks a list while the kind is below its argument and returns the row only on an exact kind match. `0x445F80` calls it with kind 1 when object +0x18 bit 0x200 is set; it is vtable slot +0xE4 (next to `0x44A060` at +0xD0) in seven vtables (bases `0x539AC0`, `0x53F2C0`, `0x53F3E0`, `0x53F6E8`, `0x53FE28`, `0x540458`, `0x540580`). `0x4466B0` (called at `0x492EB7` and `0x492FBC`) also fetches it, updates it through `0x49E180` (which rewrites row +2 and +0xF) and copies row +2, +6, +8, +0xA and +0xE (`0x4466B0–0x446745`). The game meaning of these fields is open.

| Pool | Kind | Bytes | Rows | Matcher or observed consumer |
|---|---:|---:|---:|---|
| Region | 0 | 2 | 905 | List terminator, e.g. `CKEEP.WSX+0xD0E889` |
| Region | 11 | 8 | 49 | Region u16 +4 and event u8 +6, `0x4AC4F2–0x4AC50B` |
| Region | 12 | 8 | 2,080 | Region u16 +4, event u8 +6 and conditional +7, `0x4AC252–0x4AC2E9` |
| Region | 15 | 10 | 72 | **CONFIRMED.** Threshold test on the objects resting on a row. Walker `0x4AC9F9–0x4ACA6C` in `0x4AC990` calls `0x4ACAB0`. u16 +4 must be the changed 56-byte row. The guard runs first (`0x4ACAE9`). `0x4A7CC0` gives the summed vtable +0xC value W and count N of objects resting on a row. The threshold T is u16 +8, or with +7 nonzero the W (modes 0–3) or N (modes 4–7) of row u16 +8. With signed change d, mode +6 is: 0 W > T ≥ W+d; 1 W < T ≤ W+d; 2 W = T ≠ W+d; 3 W ≠ T = W+d (`0x4ACB66–0x4ACBA0`, table `0x4ACC1C`). Modes 4–7 put N in place of W and T−1 (d > 0) or T+1 in place of W+d (`0x4ACBA2–0x4ACBE4`), so in those modes the second comparison is fixed (T−1 ≤ T always holds, T+1 ≤ T never does); above 7, nonzero N fires. Stored rows: 36 of mode 0 and 36 of mode 1, all with +7 = 0. The path `0x4AC650–0x4AC766` matches kind 13, which has no stored rows. |
| Region | 19 | 4 | 145 | Guard trailer, `0x4F0611–0x4F0639` |
| Object | 0 | 2 | 9,699 | List terminator, e.g. `CKEEP.WSX+0xD08DB8` |
| Object | 1 | 16 | 4,516 | `CKEEP.WSX+0xD0962C`. **CONFIRMED** consumer: the row after a terminator, fetched by `0x4F21B0` with kind 1 from `0x445F80` and `0x4466B0` (see above). Field meanings open. |
| Object | 2 | 10 | 768 | Periodic timer, `0x4F1AD0–0x4F1B84` |
| Object | 3 | 6 | 1,010 | Compare event u8 +4, `0x4A8255–0x4A8290` |
| Object | 4 | 10 | 1,999 | Request mode at +4, inversion byte at +5 and a mode-dependent u32 at +6. See [object requests](#object-requests). |
| Object | 5 | 6 | 605 | Compare event u8 +4 and value u8 +5. Input 0xFF matches any value; record value 0xFF matches any nonzero input (`0x4A82DE–0x4A8300`, `0x4A82F0–0x4A82FB`). |
| Object | 6 | 6 | 7,917 | Compare u8 +4, with specific variants that also test +5, e.g. `0x4A8900–0x4A8925`. |
| Object | 7 | 6 | 3 | **CONFIRMED.** Quantity threshold in `0x4A8AC0`, mode u8 +4 through table `0x4A8BC4`, value V = u8 +5. Inputs are hit-request +0x28 (before) and +0x2C (after) from resolver `0x4E2270`; `0x4465E0` runs it when object +0x18 bit 0x400 is set, e.g. after `0x4B98D0`. Mode 0: while +5 is nonzero, subtract before−after from +5; fire and zero +5 when the drop reaches it. Mode 1: before ≥ V > after. Mode 2: before ≤ V < after. Mode 3: after = V. Above 3 never fires (`0x4A8AFC–0x4A8B5A`). All 3 stored rows are mode 1 with V 200 or 100, e.g. `DLOW1.WSX+0x154DFA0`. |
| Object | 8 | 6 | 16 | Compare u16 +4, with 0xFFFF wildcard, `0x4A8D25–0x4A8D40`. |
| Object | 9 | 10 | 1,904 | Hit filter in `0x4A8BE0`, run by `0x4465E0` after kind 7. **CONFIRMED:** nonzero u16 +4 and +6 must each share a bit with request words +0 and +2. Mode +9 & 7 (table `0x4A8CF4`): 1 loss +0x24 ≥ u8 +8; 2 the same, then +8 becomes 0 unless bit 0x80 is set; 3 before +0x28 > +8 ≥ after +0x2C; 4 after ≤ +8; 0 and 5–7 never. A matching row fires when the guard `0x4F05D0` returns nonzero (`0x4A8C7B–0x4A8C85`). After a fire, +9 bit 0x80 clears +9 (one shot) (`0x4A8C0F–0x4A8CDE`). Stored modes: 1 (1,272), 4 (630), 2 (2). The names of the mask bits are **UNCONFIRMED**, as on the [combat page](lol3-combat-dispatch.md); settle them there from the producers of request words +0/+2. |
| Object | 10 | 8 | 17 | Selector/event alternatives, `0x4A8EB2–0x4A8F00`, `0x4A8F8D–0x4A8FFF` |
| Object | 19 | 4 | 3,994 | Guard trailer, `0x4F0611–0x4F0639` |
| Object | 21 | 8 | 269 | Compare event byte, `0x4A9088–0x4A9096` |
| Object | 22 | 14 | 2,368 | **CONFIRMED.** Finished named audio. Opcode 0x16 formats `%s\%s.aud` (`LOL3.DAT+0x14812C`) from its identifier and plays it through `0x422FA0` with ID 0xFFFE (`0x448244–0x448271`); the path is copied to object `0x589998` +0x2BCC (`0x42314E–0x423177`). When the slot loop `0x422B3A–0x422C15` retires the slot, it passes that path to `0x4A8DA0` on the owning object's list. The file-name part from `0x51AE90` is compared case-sensitively with the NUL-terminated name at +4 (`0x4A8DE9–0x4A8E13`). Otherwise the loop passes slot +4 to the kind-8 matcher `0x4A8D10` (`0x422BD0–0x422BDD`). 2,361 of the 2,368 names equal an opcode-0x16 identifier in the same level's object stream. |

**CONFIRMED.** Region kind 12 has a ten-slot event table at
`0x4AC470`. Events 0, 4 and 7 use the true arm. Events 1 and 9
need signed input at least four times u8 +7. Event 8 tests signed
input ≥ u8 +7 (`0x4AC287–0x4AC290`). Events 2 and 3 give true on input
2, truth of +7 on input 1, and +7 equal to zero on input 0.
Other inputs retain the caller flag. Events 5 and 6 use that
flag directly (`0x4AC27B–0x4AC2E4`). The following predicate
can still reject the event (`0x4AC2E9`).

### Object requests

**CONFIRMED.** The kind-4 matcher loads the dword at +6 at
`0x4A8503` and uses row +4 to select one of 11 slots at
`0x4A86E8`. Mode 3 compares the dword with the supplied item's
definition identity (`0x4A8566–0x4A857B`). Modes 4, 5 and 6 test
the dword as a mask against definition +0x3F, +0x3D and +0x4F.
Mode 7 compares it to definition +0x57 (`0x4A8580–0x4A85E0`).
Modes 9 and 10 require subkind 8 and check whether the target state
byte is zero or nonzero respectively. They accept the request
operand when it equals the row's dword or that dword plus one
(`0x4A85E2–0x4A8611`). A nonzero byte at +5 inverts the result
at `0x4A861F–0x4A862D`, before the kind-19 guard runs.

**CONFIRMED.** The 18 MAPs have 1,999 kind-4 rows. The writer
regenerates all 1,999 inversion bytes and the operand dwords in
1,613 rows. The latter are 68 mode-3 rows, one mode-6 row and
1,544 mode-9 rows. The total gain is 8,451 bytes from native reads.
In the remaining 386 rows, modes 0, 1 and 2 leave the loaded dword
unused. Their dwords stay retained.
[Retained MAP classes](lol3-map-odf-readers.md#retained-span-classes)

## Predicates and global bytes

**CONFIRMED.** A following kind-19 row applies a guard whose
u16 index is at +2 (`0x4F0611–0x4F0639`). With no such record,
the check returns 1 (`0x4F077E`). Below 5000, the index selects
a five-byte row loaded from MAP +0xBC with count +0xB8. The
row is operation, left type, left operand, right type, right operand
(`0x43E949–0x43E964`, `0x4F02B0–0x4F0414`). Operation
IDs 0–7 are equal, unequal, signed ≤, ≥, >, <, boolean AND, OR
(`0x4F046D`, table `0x4F04F8`).

| Type | Left +2 (table `0x4F0424`) | Right +4 (table `0x4F0444`) |
|---:|---|---|
| 0 | Literal unsigned byte, `0x4F02DD` | Literal unsigned byte, `0x4F0387` |
| 1 | Default input (the evaluator's second stack argument), `0x4F036D` | Zero operand, `0x4F0411` |
| 2 | Bound object's +0x1C bit 0x80000 for operand zero. Otherwise shared array `[0x5D54C0]`, `0x4F02FF–0x4F0336` | Shared array for every operand, `0x4F03C1–0x4F03CE` |
| 3 | Level array `[0x5D54BC]` indexed by operand, `0x4F02EA` | Same array, `0x4F039F` |
| 4 | Evaluate predicate indexed by operand, `0x4F0349–0x4F0350` | Evaluate predicate indexed by operand, `0x4F0400–0x4F0407` |
| 5 | Bound object's u8 +0x31 (object pointer `[0x600850]`), `0x4F033A` | Same byte, `0x4F03E3` |
| 6 | Default input, `0x4F036D` | Above 5: zero operand |
| 7 | False when the predicate index is 1 or more, otherwise default input, `0x4F0361` | Above 5: zero operand |

Left types above 7 take the default input. The kind-19 guard calls `0x4F02B0` with a single argument (`0x4F0772`), so the default input is not defined on that path. Over the 18 MAP +0xBC tables the left types used are 0 (3,066), 2 (321), 3 (232), 4 (66) and 5 (905); the right types used are 0, 3 and 4. Type 1 never occurs.

**CONFIRMED.** The level array is loaded from MAP +0xB4,
length +0xB0 (`0x43E91D–0x43E93A`, `0x440A20`).
Global save selector 1 stores the shared array and length
(`0x43817D–0x4381A3`). The higher guard indices use alternate
tests and threshold families with bases 5000, 6000, 7000, 7100,
7200 and 7300 (`0x4F0635–0x4F0767`).
**CONFIRMED.** Index n ≥ 5000 is tested as follows. 5000+n: the
cursor item `[0x585488]` or an item list or cell of `0x570900` holds item
key n (definition +0x73; `0x4F0520 → 0x432150–0x4321CF`). 6000+n: one of
the eight equipped rows holds key n (`0x4F0530 → 0x42B850`, see
the [spell page](lol3-spell-dispatch.md)). 7000/7100/7200/7300+n:
slot k = 0–3 has its flag `0x5D50C8+k` set and level
`0x5D50BC+k` above n (`0x4F0540–0x4F05CE`). The eight values
7399, 7409 … 7469 compare `[0x586158]` with 0–3; the first four
also need `[0x589544]` zero (`0x4F0647–0x4F06E2`, index bytes
`0x4F07AC`). **UNCONFIRMED:** what `[0x586158]` and `[0x589544]`
mean in play, and the game names of the shared and level array
indices. Settle the first by finding the writers of those two
dwords and a consumer that shows them to the player. Settle an
array index by listing the 0xC6/0xC7/0xCE/0xCF records that write
it and the events that run them.

## Timers and elapsed units

**CONFIRMED.** A kind-2 record has flags +4, disable bit zero
at +5, reload bytes +6/+7 and a u16 countdown at +8.
Let `a` and `b` be +6/+7. The reload selector is `a` if
flags & 0x20, otherwise the result of `0x44AA40(b, a)`
with ECX `0x55D3D0` (`0x4F1A03–0x4F1A26`).
The original code stores 60 to `[0x58CCB8]` at `0x407BAD`.

| Mode in priority order | Reload before u16 truncation | Elapsed input |
|---|---|---|
| Flags & 0x10 | selected × 60 | dword `[0x58CBA7]` |
| Flags & 0x80 | a × 60 × 60 | same dword |
| Neither | selected × 256 | sign-extended word `[0x58CBA5]` |

The three arms are at `0x4F1A26–0x4F1A58`, and the
elapsed loads are at `0x4F1B02–0x4F1B16`. With unsigned
countdown above elapsed, subtract and continue. Otherwise
reload, preserving `countdown + reload − elapsed` when
the unsigned reload alone exceeds elapsed, and write zero
otherwise. The event reaches the group runner only when
its guard passes (`0x4F1B16–0x4F1B6F`). The kind-2 row at
`CKEEP.WSX+0xD08E7E` has flags 0x20, reload byte 1 and
stored countdown 0x100, a direct fixed reload witness.

**CONFIRMED.** The writer is the frame update at `0x46D570`.
Its caller supplies ECX `0x58C6F8` (`0x46CBD4–0x46CBD9`)
and the update copies it to EBP. The elapsed values are
written indirectly at EBP +0x4AD and +0x4AF. The stopwatch at
+0x499 is initialized with rate 480 at `0x46D11F–0x46D12B`.
The Windows host computes `floor(1000/480) = 2` ms and
registers the periodic callback `0x507F40` through
`timeSetEvent` (`0x407CB1–0x407CC5`,
`0x507E20–0x507E59`). That callback increments the host
counter (`0x507F57–0x507F7B`). The rate selector uses shift
0 for 480, 1 for 240, 2 for 120 and 3 for 60
(`0x503170–0x5031CC`), and `0x5031F0–0x503218` reads
and shifts the counter. Stopwatch read
`0x503260–0x5032A8` subtracts its saved counter value.

**CONFIRMED.** The loop waits for at least 24 quanta when
`[0x545A2C] = 0x5385E0`, otherwise 16
(`0x409930–0x409943`, `0x46D84F–0x46D882`).
It inserts the elapsed sample capped at 480 into a four-sample
ring, updates its sum `S` and resets the stopwatch
(`0x46D887–0x46D8DE`). The following values use integer
arithmetic and start from zero (`0x46D229–0x46D242`).

| Store | Value | Native source |
|---|---|---|
| `0x58CBA1` dword | `D = min(0x80000, trunc((S << 16)/32))` | `0x46D8E3–0x46D902` |
| `0x58CBA5` word | `out = (D+r8) >> 8`, then `r8 = D+(r8 & 255)-(out << 8)` | `0x46D90C–0x46D934` |
| `0x58CBA7` dword | `out = (D+r16) >> 16`, then `r16 = D+(r16 & 65535)-(out << 16)` | `0x46D93A–0x46D95E` |

The second accumulator adds `D`, compares with `60 << 16`
and subtracts that threshold when reached
(`0x46D969–0x46D998`). These are the writer-side units for
the countdown inputs above.
