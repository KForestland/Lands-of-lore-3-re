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

**UNCONFIRMED.** The button-to-cast mapping and exact mana debit
remain open. The direct key-cell references resolve to the label
path above. The ODF table and its effect constructor resolve
effect setup and hit magnitude. To settle costs, follow the player
cast request before effect allocation and record the selected
slot, selected definition, resource comparison and debit together.
The effect hit magnitude table by itself does not specify a cost.
