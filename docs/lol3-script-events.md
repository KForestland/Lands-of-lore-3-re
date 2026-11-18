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
The terminator rows and the kind-1 rows (consumer UNCONFIRMED) have separate uses.

| Pool | Kind | Bytes | Rows | Matcher or observed consumer |
|---|---:|---:|---:|---|
| Region | 0 | 2 | 905 | List terminator, e.g. `CKEEP.WSX+0xD0E889` |
| Region | 11 | 8 | 49 | Region u16 +4 and event u8 +6, `0x4AC4F2–0x4AC50B` |
| Region | 12 | 8 | 2,080 | Region u16 +4, event u8 +6 and conditional +7, `0x4AC252–0x4AC2E9` |
| Region | 15 | 10 | 72 | Region comparison path, `0x4AC650–0x4AC766`. Individual comparison modes are **UNCONFIRMED** here. |
| Region | 19 | 4 | 145 | Guard trailer, `0x4F0611–0x4F0639` |
| Object | 0 | 2 | 9,699 | List terminator, e.g. `CKEEP.WSX+0xD08DB8` |
| Object | 1 | 16 | 4,516 | `CKEEP.WSX+0xD0962C`. Consumer **UNCONFIRMED**. |
| Object | 2 | 10 | 768 | Periodic timer, `0x4F1AD0–0x4F1B84` |
| Object | 3 | 6 | 1,010 | Compare event u8 +4, `0x4A8255–0x4A8290` |
| Object | 4 | 10 | 1,999 | Request mode at +4 through 11 slots, `0x4A84FB–0x4A8516` |
| Object | 5 | 6 | 605 | Compare event u8 +4 and value u8 +5. Input 0xFF matches any value; record value 0xFF matches any nonzero input (`0x4A82DE–0x4A8300`, `0x4A82F0–0x4A82FB`). |
| Object | 6 | 6 | 7,917 | Compare u8 +4, with specific variants that also test +5, e.g. `0x4A8900–0x4A8925`. |
| Object | 7 | 6 | 3 | Threshold branch, `0x4A8B09–0x4A8B64`. Full comparison modes **UNCONFIRMED**. |
| Object | 8 | 6 | 16 | Compare u16 +4, with 0xFFFF wildcard, `0x4A8D25–0x4A8D40`. |
| Object | 9 | 10 | 1,904 | Hit filter path, `0x4A8C4E–0x4A8C7B`. Full bit meanings **UNCONFIRMED**. |
| Object | 10 | 8 | 17 | Selector/event alternatives, `0x4A8EB2–0x4A8F00`, `0x4A8F8D–0x4A8FFF` |
| Object | 19 | 4 | 3,994 | Guard trailer, `0x4F0611–0x4F0639` |
| Object | 21 | 8 | 269 | Compare event byte, `0x4A9088–0x4A9096` |
| Object | 22 | 14 | 2,368 | Identifier comparison, `0x4A8DBC–0x4A8E1B`. Full identifier protocol **UNCONFIRMED**. |

**CONFIRMED.** Region kind 12 has a ten-slot event table at
`0x4AC470`. Events 0, 4 and 7 use the true arm. Events 1 and 9
need signed input at least four times u8 +7. Event 8 tests signed
input ≥ u8 +7 (`0x4AC287–0x4AC290`). Events 2 and 3 give true on input
2, truth of +7 on input 1, and +7 equal to zero on input 0.
Other inputs retain the caller flag. Events 5 and 6 use that
flag directly (`0x4AC27B–0x4AC2E4`). The following predicate
can still reject the event (`0x4AC2E9`).

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
The meanings of those families and named individual global
indices remain **UNCONFIRMED**. Follow a concrete guard value
to its helper and join the index to its native initializer.

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
