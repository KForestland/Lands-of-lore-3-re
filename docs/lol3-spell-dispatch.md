# Native spell inputs and resource selection

Addresses refer to the [English retail image](lol3-lmf-reader.md).

**CONFIRMED.** The input-name table starts at
`LOL3.DAT+0x14EA08` (VA `0x550208`). Indexes 46–55 are
`CAST_SPELL_0_1` through `CAST_SPELL_4_2`, ordered as two bindings
per spell slot. The first and last strings are at file offsets
0x14F120 and 0x14F090. The input initialization loop at
`0x4F338B–0x4F34B4` reads the names and sets their configured keys
at `0x5D4CD8+4*index`. The default settings writer uses the same
names at `0x4F3CFA–0x4F3D19`.

**CONFIRMED.** The resource setup at `0x44001F–0x44002E` selects
`global\spell.odf` and `global\spell.tex`. The keys resolve to
`DAT/GLOBAL.WSX+0x16BE53` and `DAT/LOCAL.WSX+0x4F5E16` respectively.
The global texture loader registers a separate group of 512-byte
resources from the spell bank through `0x4403E0–0x440408`. At
`0x44B714–0x44B72C`, descriptor arm 2 reads the first key from
world +0xD8 and adds descriptor u16 +2 before calling the texture
object. Those palette resources are separate from field decisions
during a cast.

## Definition tables

**CONFIRMED.** The original spell ODF entry at
`GLOBAL.WSX+0x16BE53` gives a table offset u32 +4 = 412
and count +8 = 28. The loader seeks to +4 at `0x440667`,
passes +8 at `0x440676–0x440685` and stores the returned
pointer at world +0x14 (VA `0x570184`). `0x4B42FD–0x4B4348`
reads 28 rows of 87 bytes, beginning at `GLOBAL.WSX+0x16BFEF`.
An independent offset pair holds one 8-byte auxiliary row at
+0x43EC, file `GLOBAL.WSX+0x17023F`, read through
`0x440611–0x440648`. That row's gameplay role is
**UNCONFIRMED**.

**CONFIRMED.** Definition +0x18 is the identity compared by
`0x440990–0x4409B4` in the 87-byte table. The resource
rebinder at `0x4B4390–0x4B43B4` replaces row +0x14 with a
pointer and advances that pointer by 16 × row u8 +0x2E.
The first row's +0x18 is 0x375133EE and its +0x2E is 8
(`GLOBAL.WSX+0x16C007` and +0x16C01D).

## Effect object and first hit

**CONFIRMED.** Constructor `0x4C4320` installs vtable
`0x539E20` at `0x4C4341`. Effect variant dispatch uses
eight slots at `0x4C44FC` (`0x4C4365–0x4C436E`).

| Variant | Index source in `[[0x7D755C]+4]` | Native arm |
|---:|---:|---|
| 0 | +0xA4 | `0x4C4375` |
| 1 | +0xAC | `0x4C4389` |
| 2 | +0xB4 | `0x4C439A` |
| 3 | +0xBC | `0x4C43AB` |
| 4 | +0xD4 | `0x4C43CD` |
| 5 | Retain the base constructor's definition pointer | `0x4C4424` |
| 6 | +0xCC | `0x4C43FA` |
| 7 | +0xC4 | `0x4C43BC` |

Each replacement indexes the 87-byte ODF table and writes effect
+0x34 (`0x4C43D6–0x4C4421`). The constructor copies XYZ from
the supplied point and sets +0x63 bit 1 if initial placement
fails at `0x4C4487` or `0x4C44DC`. At `0x44891F`, inside
the object command switch (which opcode reaches it is
**UNCONFIRMED**), a call passes variant 2 and effect ID
0x62. Adjacent calls at `0x448952` and `0x448985` supply
variants 0 and 1 with IDs 0x63 and 0x64. These calls confirm
effect creation through a script path.

**CONFIRMED.** Vtable +0x3C at executable file +0x13865C
selects `0x4C4530`. The first update searches within
`min(150, 6 × (5 + animation byte +0x0E))` 16.16 units
(`0x4C4562–0x4C45B1`). It filters candidates by flags,
type and exact distance (`0x4C45C2–0x4C4628`).
Magnitude comes from the signed-byte table at `0x54BF60`
at the index from effect +0x69. Its entries 0–8 are
10, 20, 40, 80, 10, 0, 10, 10 and 60
(`LOL3.DAT+0x14A760`, `0x4C462E–0x4C463D`).
Zero skips the hit. Variant 4 submits mask 0x20 and flags
1. Other admitted variants here use mask 0x10 and flags 5
(`0x4C467C–0x4C46B3`). The target receiver makes the final
health change. See the [native combat path](lol3-combat-dispatch.md).

## Player cast and cost

**CONFIRMED.** The ten direct key-cell references
`0x4AA5F6–0x4AA663` pick configured bindings for display.
Their later path calls a key-name function and TRR lookup
(`0x4AA667–0x4AA689`). A player update calls the effect
constructor with variant 8 at `0x41503F` (variant 8 is above 7, so `0x4C4365` sends it to the default arm, like variant 5, and its magnitude entry is 60), then releases an
item object (`0x415044–0x415053`). Those paths have separate
inputs in the original code.

**CONFIRMED.** The five cast callbacks feed slots 5–9 to
`0x4282E0`. The [item use dispatcher](lol3-item-dispatch.md#use-effects)
sends special definitions to `0x4A4520`. The handler requires
request operation 1 and starts with the definition dword +0x5B
as mana cost (`0x4A4547–0x4A4564`, `0x4A45C4–0x4A45D4`).
For example, the original row at `GLOBAL.WSX+0x6425` holds
ID 0x50 and cost 50. The row at +0x7F4B holds ID 0x82 and cost 5.

**CONFIRMED.** `0x42B850` scans eight equipped rows at
`0x546EF8–0x546F68` for a definition's numeric ID. With IDs
0x128, 0xD8, 0xDC and 0xDB all present, spell IDs 0x82–0x86
halve cost with integer truncation (`0x4A4620–0x4A4688`).
With ID 0xE9 equipped, spell IDs 0x50–0x54 subtract
`trunc(cost/4)` (`0x4A468C–0x4A46BD`). The ordinary
resource test compares that adjusted cost with player dword
+0x1B8, read by `0x40FEF0`. An unsigned cost above the
current value queues message ID 0x59 and returns 4 before
the effect switch (`0x4A46F5–0x4A4727`).

**CONFIRMED.** After the effect branch, two conditional
discounts check `0x433C80(8, 10)` and `0x433C80(8, 13)`
with ECX `0x57095C`. They apply to opposite values of
the local cast flag at stack +0x18. They use bytes
`0x5D50BD` and `0x5D50BE`, respectively. Let that byte
be `n` and let `c` be the cost after the equipment adjustment.
The discount computes `d = trunc(c*(25+2*(n-1))/100)`,
uses 1 if `d` is zero, and uses `max(1, c-d)` as the
debit (`0x4A596F–0x4A5A0D`). On the ordinary success
path, `0x4A5A45–0x4A5A4D` passes the negative debit
to `0x40FFE0`. That function clamps the updated +0x1B8
between zero and the vtable +0xB0 return, then refreshes
the HUD (`0x40FFE0–0x410052`). The failed-effect branch
at `0x4A5A41–0x4A5A54` skips this debit.

**CONFIRMED.** For IDs 0x54 and 0x59, a nonzero
`[0x570AB9]` can select a different payment route, which
calls `0x4329C0(-1)` on success. The other bypass tests
`[0x581A21]` and can call `0x432AD0(-1)` instead
(`0x4A46C1–0x4A46F3`, `0x4A5BB0–0x4A5BCE`,
`0x4A5A0D–0x4A5A54`).

**UNCONFIRMED.** The gameplay names of those two alternate
resources and the final cost-discount selectors are open.
To distinguish the resources, take the 0x54 or 0x59 row
through `0x4A5BB0`, then identify the initializer and HUD
consumer of the counter that `0x4329C0` changes. On an
ordinary successful cast, log the two `0x433C80` results
and the corresponding level byte before `0x4A59A1` or
`0x4A59EF` to name the discount conditions.
