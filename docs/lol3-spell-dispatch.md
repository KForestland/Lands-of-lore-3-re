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

### Producers of the alternate counters

**CONFIRMED.** Both selector values are the counters themselves.
The two debit callers pass ECX `0x570900`. `0x4329C8–0x4329D8`
adds its argument to `ECX+0x1B9` (`0x570AB9`), and
`0x432AD8–0x432AE8` adds to `ECX+0x11121` (`0x581A21`).
Both then refresh HUD groups 3–7 via `0x432CC0–0x432CD5`.

| Selector and debit | Original item that supplies a charge | Producer |
|---|---|---|
| `0x570AB9`, `0x4A5A20` | Ancient's Stone (ID `0x36`, `GLOBAL.WSX+0x5692`, name at `locallng.wsx+0x596B2C8`) and Force Pod (ID `0xE7`, `GLOBAL.WSX+0xB597`, name at `+0x5977225`) | Both use regular index 6 (`0x54B930 → 0x49FB10`). Operation 1 adds one at `0x49FB23`. |
| `0x581A21`, `0x4A5A3A` | Mana Cluster (ID `0x110`, `GLOBAL.WSX+0xCB4F`, name at `locallng.wsx+0x597A8A0`) | Regular index 112 (`0x54BAD8 → 0x4A6120`). Operation 1 adds one at `0x4A6133`. |

The item numeric key is at definition +0x73. The original name reader
uses that key at `0x4AD169–0x4AD1B4`. For a positive second-counter
addition, `0x432AF1–0x432B06` also gets the player's mana ceiling
via `0x40FF00` (player vtable +0xB0 at `0x538438`) and passes it
as an increase to `0x40FFE0`. A negative
argument skips that refill (`0x432AE8–0x432AEF`).

**CONFIRMED.** The `0x54` and `0x59` admission arm requires a
nonzero first counter. Zero queues message `0x5B` and goes to the
failure return (`0x4A5BB0–0x4A5BCE`, `0x4A470A–0x4A4727`).
When the same successful cast has that charge selected, the first
debit takes priority at `0x4A5A0D–0x4A5A25`. The ordinary path
can check the second counter at `0x4A46DE–0x4A46F3` and spend
one charge at `0x4A5A27–0x4A5A3F`.

**UNCONFIRMED.** A live cast after either consumable and the final
cost-discount selector names. On an ordinary successful cast, log
the two `0x433C80` results and the corresponding level byte at
`0x4A59A1` or `0x4A59EF`.

## Live cast setup

**CONFIRMED.** Loading the level-5 autosave (SHA-256 prefix
`df50eda48c27`) on the original English executable with the Wine
audio drivers disabled produced `[0x5D5098] = 20` and zero at
`0x570AB9` and `0x581A21`. The five slots used by the key casts
were empty. The pointer at `0x583151+0x80` was `0x5469B8`,
and the slot pointers at +0x50, +0x60, +0x70, +0x80 and +0x90
were zero, matching the use-slot reader at `0x4282FA–0x42830C`.
The game displayed the level during load. The loader waited in
`0x46F68F–0x46F69B` with `[0x65BD64] = 1`. The audio service was
disabled (`[0x7F4DF8] = 0` at the check in `0x506F70`). The progress
path installs its completion callback `0x46F8A0` at `0x46F573` and
waits for it to clear that cell.

**UNCONFIRMED.** Runtime cast selection or payment. Pressing the
five configured cast keys during the blocked load did not reach
`0x4A46C1`. No negative debit was seen at `0x410014` or at either
alternate function. (The load waits on a flag the progress sound's completion callback clears: `0x46F55B` sets `[0x65BD64]` to 1 whatever the sound result, so without audio the loader hangs. With the debugger attached, set `[0x65BD64]` to 0, or force the `0x46F512` skip, and label the run as patched in memory.) A load that completes the progress sound and
a slot with an equipped spell provide the ordinary control. Log a
cast of 0x54 or 0x59 with a nonzero selector and read the debit
arguments to witness alternate payment.
