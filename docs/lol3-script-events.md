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
The terminator and render rows have separate uses.

| Pool | Kind | Bytes | Rows | Matcher or observed consumer |
|---|---:|---:|---:|---|
| Region | 0 | 2 | 905 | List terminator, e.g. `CKEEP.WSX+0xD0E889` |
| Region | 11 | 8 | 49 | Region u16 +4 and event u8 +6, `0x4AC4F2–0x4AC50B` |
| Region | 12 | 8 | 2,080 | Region u16 +4, event u8 +6 and conditional +7, `0x4AC252–0x4AC2E9` |
| Region | 15 | 10 | 72 | Region comparison path, `0x4AC650–0x4AC766`. Individual comparison modes are **UNCONFIRMED** here. |
| Region | 19 | 4 | 145 | Guard trailer, `0x4F0611–0x4F0639` |
| Object | 0 | 2 | 9,699 | List terminator, e.g. `CKEEP.WSX+0xD08DB8` |
| Object | 1 | 16 | 4,516 | `CKEEP.WSX+0xD0962C`. Full render consumer **UNCONFIRMED**. |
| Object | 2 | 10 | 768 | Periodic timer, `0x4F1AD0–0x4F1B84` |
| Object | 3 | 6 | 1,010 | Compare event u8 +4, `0x4A8255–0x4A8290` |
| Object | 4 | 10 | 1,999 | Request mode at +4 through 11 slots, `0x4A84FB–0x4A8516` |
| Object | 5 | 6 | 605 | Compare event u8 +4 and value u8 +5. Value 0xFF gives a wildcard on either side, `0x4A82DE–0x4A8300`. |
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
need signed input at least four times u8 +7. Event 8 compares
input directly against u8 +7. Events 2 and 3 give true on input
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

| Type | Left +2 | Right +4 |
|---:|---|---|
| 0 | Literal unsigned byte, `0x4F02DD` | Literal unsigned byte, `0x4F0387` |
| 1 | Level array `[0x5D54BC]` indexed by operand, `0x4F02EA` | Same array, `0x4F039F` |
| 2 | Bound object's +0x1C bit 0x80000 for operand zero. Otherwise shared array `[0x5D54C0]`, `0x4F02FF–0x4F0336`. | Shared array for every operand, `0x4F03C1–0x4F03CE` |
| 3 | Bound object's u8 +0x31, `0x4F033A` | Same byte, `0x4F03E3` |
| 4 | Evaluate predicate indexed by operand, `0x4F0349–0x4F0350` | Evaluate predicate indexed by operand, `0x4F0400–0x4F0407` |
| 5 and above | Defaults and special input test at `0x4F0361–0x4F036D` | Type 5 and above reaches the initialized zero operand, `0x4F0377–0x4F0414` |

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

**UNCONFIRMED.** Which host clock updates the two live elapsed
cells is open. Their exact consumers and scale constant above
are identified. A bounded check of absolute write operands
overlapping `0x58CBA5–0x58CBAA` found no direct store. To settle
the conversion, observe the first write before `0x4F1AD0`
and compare the raw inputs in an ordinary and a long frame.
