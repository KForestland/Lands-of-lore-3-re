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
`0x440611–0x440648`. **CONFIRMED.** The loader stores that
row's pointer at world +0x78 (`0x440642`, VA `0x5701E8`). The
only absolute reader is `0x4909D5` in `0x4909A0`, which has 48
direct callers, among them the spell effect update at `0x4C4725`.
It picks the row by frame word +8, skips 8-byte entries until byte
+1 equals object byte +0x60 (`0x490A11–0x490A2F`), then handles the
matching entries. Kind byte 0 ends the list and returns the total so
far. Kind 1 adds byte +2 to the total. Kind 2
plays sound u16 +2 through `0x422C40` (`0x4909D5–0x490A6F`).
The one original row is eight zero bytes, so it asks for nothing.
**CONFIRMED.** No original spell frame has a nonzero word +8.
The 28 rows are followed in the same resource by a count of 447,
which equals the sum of the 28 frame counts at row +0x2E, then
a count of 447 at `GLOBAL.WSX+0x16C973`, then 447 frames of 16 bytes at `+0x16C977`. Every frame's
u16 at +8 is 0. `0x4FD560` reads that count, copies `count × 16`
bytes (`shl ecx, 4` at `0x4FD57C`) and overwrites only dword +0
of each frame. The rebinder below slices that array by row +0x2E.
`0x490A03` (`mov cx, word ptr [eax+8]`) therefore loads 0 from
every shipped frame and reads the single auxiliary row.
`lol3_native_checks.py --check` recounts the 447 words, the
following pool count 545 (the sum of frame byte +0xD) and those
instruction bytes.

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
script opcode 0x0F, a call passes variant 2 and effect ID
0x62. **CONFIRMED.** Opcode 0x0F reads action byte +4 at
`0x4485BD`. Action 0x62 has index byte 54 at `0x449BEC+0x62`,
and slot `0x449A8C+4×54` (`0x449B64`) holds `0x4488F6`, the arm
that makes this call. Actions 0x63 and 0x64 take slots 55 and 56.
The [opcode 0x0F action table](lol3-script-opcodes.md#effect-actions-of-opcode-0x0f)
lists no stored record for actions 0x62–0x64. Adjacent calls at `0x448952` and `0x448985` supply
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

**CONFIRMED.** The cast can pay from one of two counters.
Entry `0x4A4520` clears both payment locals at stack +0x30
and +0x34 (`0x4A4533–0x4A453F`). The first-counter route
requires nonzero `[0x570AB9]`, sets +0x30 and skips the
second-counter test. The other route tests the dword at
`[0x581A21]`: a nonzero value sets +0x34 and skips the
mana affordability comparison (`0x4A46C1–0x4A46FF`,
`0x4A5B93–0x4A5BCE`).

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

**CONFIRMED.** The item numeric key is at definition +0x73.
The original name reader uses that key at `0x4AD169–0x4AD1B4`.
Scanning all 343 original rows from `GLOBAL.WSX+0x3A56`
finds one regular definition whose +0x4B is 112, Mana Cluster
at +0xCB4F. Its +0x3F is 0x40. The native dispatcher
reads both fields at `0x49E969–0x49E992` before the regular
table lookup at `0x49EA08`. The complete `.text` virtual range
(`LOL3.DAT+0x400..+0x1366E4`, VA `0x401000..0x5372E4`)
contains two `E8 rel32` encodings targeting `0x432AD0` (and no
`E9` or conditional-jump targets):
`0x4A6133` passes +1 after regular handler 112 accepts
operation 1, and `0x4A5A3A` passes −1. A whole-file search
finds no literal dword pointer to the writer. These checks
cover encoded direct calls, literal pointers and the original
item table.

**UNCONFIRMED.** Indirect or computed targets of the writer.
These cannot be ruled out statically. In a debugged session,
break at `0x432AD0` and log each return address. Any return
other than `0x4A5A3F` and `0x4A6138` is an indirect caller.

#### Second-counter debit

**CONFIRMED.** The first-counter admissions are IDs 0x54 and
0x59 by direct comparisons, and 0x5E, 0x63, 0x68, 0x6D,
0x72, 0x77, 0x7C, 0x81, 0x86, 0x8B, 0x9C–0x9F and
0x15A by the byte index at `0x4A5E20` and jump slots at
`0x4A5DEC`. All 17 are special definitions in the original
item table at `GLOBAL.WSX+0x3A56`. They go to the
dedicated admission `0x4A5BB0`; zero queues message 0x5B
through `0x4A5BC7–0x4A5BCE`. The preflight called by
`0x421D35` and `0x425B95` uses the same IDs
(`0x4346F0–0x434759`, tables `0x434790` and `0x43475C`).
Other IDs can use the second counter. ID 0x57 at
`GLOBAL.WSX+0x67F2` is one such original spell.

**CONFIRMED.** After the spell effect, `0x4A5A0D–0x4A5A25`
pays the first counter when selected and the effect succeeded.
The second branch at `0x4A5A27–0x4A5A3F` requires stack
+0x34 set and the effect result in EBX nonzero. It pushes
−1 and ECX `0x570900`; `0x432AD8–0x432AE0` reads,
adds and stores the counter modulo 2³² at
`0x570900+0x11121 = 0x581A21`. The helper calls the
refresh loop for groups 3–7 (`0x432AE8 → 0x432CC0`)
and skips the positive-only refill. When the resulting
counter is zero it writes 0x1F at `[ESI+0x28]+0x358`
(`0x432B52–0x432B66`). The debit then rejoins at
`0x4A5A7D`, past the ordinary mana debit at `0x4A5A4D`.
A failed effect takes `0x4A5A31 → 0x4A5A54` and
skips the counter store.

**CONFIRMED.** A positive argument refills mana by passing
the ceiling from player vtable +0xB0 (`0x538438 → 0x40FF00`)
as an increase to `0x40FFE0`. It also sets state +0x12F8D
to 1 and may emit feedback via `0x422C40`
(`0x432AF1–0x432B4D`). The zeroing paths use EDI = 0
at `0x42E613 → 0x42E759` and `0x4325AC → 0x4326B7`.
The display path reads the same relative offset at
`0x430C7D` and formats a positive count in decimal
at `0x430C87–0x430C8F`.

Run `tools/lol3_native_checks.py --data DAT --check` to
recheck the direct calls, counter store and guards, both
admission tables, and the 343 definition rows.

**UNCONFIRMED, live witness.** The earlier attempt at the
DLOW1 placement left the cursor and counter at zero. For a
successful second-counter trial start with Mana Cluster in
inventory, use it and check `0x4A6133` for +1. Then cast
ID 0x57 against a valid target. At `0x4A5A3A` record
counter and mana, check the new counter at `0x432AE0` and
check the zero-state store at `0x432B5F` when starting
from one charge. Observe the display after both calls.

### The two cost discounts

**CONFIRMED.** `0x433C80(list, key)` rejects lists above 12, then
calls `0x45AB20` on the 24-byte record at `ECX + 24 × list + 4`
(`0x433C84–0x433C9B`). That record holds a count at +0, a key array
pointer at +4 and a value array pointer at +0xC; the helper returns
the value paired with the key, or 0 when the key is absent
(`0x45AB20–0x45AB4C`). With ECX `0x57095C`, list 0 holds spell IDs
(the callers at `0x418C0F–0x418FD0` test 0x55–0x59 and 0x82–0x86),
list 7 keys 0–3 and list 8 keys 4–0x15 (69 direct callers in all).
The two discounts test list 8 keys 10 and 13.

**CONFIRMED.** The level bytes belong to four parallel slots: a
joined flag at `0x5D50C8 + k`, a level at `0x5D50BC + k` and a dword
at `0x5D50AC + 4k`. The guard predicates `0x4F0540`, `0x4F0570`,
`0x4F0590` and `0x4F05B0` return 0 unless slot k's flag is set and
otherwise compare its level with their argument
(`0x4F0540–0x4F05C3`); `0x458247–0x45824D` reads both by slot.
`0x5D50BD` and `0x5D50BE` are the levels of slots 1 and 2.

**CONFIRMED.** The selector at stack +0x18 starts at 1
(`0x4A4571`). The effect switch on definition +0x73 − 0x50
(index bytes `0x4A5CE0`, slots `0x4A5BD4`, `0x4A478D–0x4A47A4`)
writes 0 to it only in the arms for IDs 0x5E (`0x4A4B94`),
0x60 (`0x4A4C0B`), 0x7D–0x81 (`0x4A5479`), and on some paths
of 0x98–0x9B (`0x4A583A`) and 0x9C–0x9F (`0x4A5877`). So every
other spell ID takes the list-8 key 10 discount scaled by slot-1
level, and those IDs take the key 13 discount scaled by slot-2
level.

**CONFIRMED.** The four slots are the Fighter, Wizard, Cleric and
Thief classes on screen. The display at `0x458241–0x4582B5` reads
slot k's level and dword, then asks text key 0x2723 + k through
`0x428890` with ECX `0x570900`. That function looks the key up in
the table at `[ECX+0x58]`, which `0x431600–0x431613` fills from
`tooltip.trr` (string at `LOL3.DAT+0x146F18`). In the original
`DAT/locallng.wsx` entry at +0x598AD7C, keys 0x2723–0x2726 are
"Fighter", "Wizard", "Cleric" and "Thief". So the two discounts scale
with the Wizard level (slot 1) and the Cleric level (slot 2).

**UNCONFIRMED.** What list-8 keys 10 and 13 are called on screen,
and a live cast after either consumable. On an ordinary successful
cast, log the two `0x433C80` results and the corresponding level
byte at `0x4A59A1` or `0x4A59EF`.

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

**Superseded.** This blocked load did not settle runtime cast
selection or payment. The null-sink run below witnessed the
ordinary debit and the first-counter debit. Only the second-counter
debit stays open (end of page). Pressing the
five configured cast keys during the blocked load did not reach
`0x4A46C1`. No negative debit was seen at `0x410014` or at either
alternate function. (The load waits on a flag the progress sound's completion callback clears: `0x46F55B` sets `[0x65BD64]` to 1 whatever the sound result, so without audio the loader hangs. With the debugger attached, set `[0x65BD64]` to 0, or force the `0x46F512` skip, and label the run as patched in memory.) A load that completes the progress sound and
a slot with an equipped spell provide the ordinary control. Log a
cast of 0x54 or 0x59 with a nonzero selector and read the debit
arguments to witness alternate payment.


### Casts with a null sink

**CONFIRMED.** The private software-only PulseAudio sink let the
original loader finish. With the level-2 player slot (a save written by the game, not shipped)
whose SHA-256 prefix is `5ae559b2cabe`, the save restore at `0x43703E` had
437 mana and alternate counters 35 and 0. The journal's spell
storage contains IDs `0x59` and `0x54` at rows 11 and 12 of
`0x548568`. The native save reader's selector 14 covers that
25-row table (`0x438341–0x438369`). The original journal moved
`0x59` into the first quick spell slot.

| Cast through `0x4A46C1` | Live debit |
|---|---|
| `0x57` ordinary control | `0x410014` changed mana 437 → 415 (−22), returning to `0x4A5A52`. |
| `0x59` with first counter 35 | Call `0x4A5A20` reached the store at `0x4329D0` with −1. Counter 35 → 34, and mana was 437 both before and after. |

**CONFIRMED, second-counter setup.** The original placement
reader reads 37 bytes at `0x4D74B0` and passes the row to
`0x4D7380` at `0x4D74D0`. The constructor takes its item
identity at `+0x20` via `0x4D7390–0x4D73AA`. The original
Mana Cluster (`0x110`, key `0xE2F77FE7`) occurs at
`DLOW1.WSX+0x155A349` and `FLAIR.WSX+0x15CB594`. The native
level descriptors for DLOW1 and FLAIR are at `LOL3.DAT+0x1471A4`
and `+0x1471DA` (level IDs 4 and 6).

The copied level-4 player slot (game-written, `df378d294f42`) loaded the DLOW1
item at X −635, Z 4913, height 110, surface 1287. The positions
are converted by `0x4411FB–0x441215`. The loaded player started
on surface 5106, at floor height 10 (`DLOW1.WSX+0x15385BD`).
After turning, advancing to the counter and clicking, the cursor
cell `0x585488` and counter `0x581A21` stayed zero. No tested
player slot held the item in save sections 10–14. The section-2
player item pool (`0x4381AA → 0x438773`) and old pointers at
save `+0x3B4` (definitions) and `+0x3C8` (pool) gave the lookup
for the 47 available player slots (written by the game, not shipped).

### DLOW1 approach with the native placement live

**CONFIRMED, reachability trial.** The closest available level-4
source (`df378d294f42`, slot +0x49C/+0x4A0) restored with
79 mana and counters 3 and 0 at `0x43703E`. The constructor
`0x4D7380` instantiated the `0xE2F77FE7` item from
`DLOW1.WSX+0x155A349`, whose coordinates are
(−635, 4913, 110) and whose surface is 1287. Tile 1287 starts at
`DLOW1.WSX+0x1504255` and has floor height 110 at +0x18.

Walking around the counter, jumping toward it and clicking from
two angles left the cursor and second counter zero. The closest
logged jump pose at `0x43766F` was (−637, 4895, 52) with
heading `0x041F`. After crossing the horizontal target from the
lower floor, the next save (`f88f201e77d4`) read approximately
(−638, 4927, 10), on surface 1255 (slot +0x4A8).
The watched cluster-use call `0x4A6133` and second-counter
store `0x432AE0` did not execute in this trial. The runner reached
the item's horizontal neighbourhood but could not take the
placement at its height.

**UNCONFIRMED.** The live second-counter debit. Reach the DLOW1
item from surface 1287 or the FLAIR placement on surface 3243
(`FLAIR.WSX+0x15CB594`, X −12204, Z 8308, height 300). With the
cursor empty, capture pickup of definition `0xE2F77FE7` at
`0x4D83A0 → 0x49EDA0`. Use the item to reach `0x4A6133`
and verify the count at `0x432AE0`. Cast spell 0x57 against
a valid target and record its −1 debit and mana balance at
`0x4A5A3A`. Follow the count in the HUD at `0x430C7D`.

### Casts with edited quick slots

**CONFIRMED, edited-save run.** The BUPP1 source slot
`5ae559b2cabe` was copied and loaded by the English retail
original under Wine with a private software renderer and
null sink. The copied slot (`90099b161497`) kept both counters
as written by the game. The recipe changes the following
bytes. Offsets in each row are relative to that selector's
expanded payload and the source slot start is in parentheses.

| Selector | Offset and old → new |
|---|---|
| G2 (`0x1A441`) | `+0x270: 00 00 00 00→5C 3C E5 21`, `+0x280: 00 00 00 00→19 B1 E5 21` |
| G3 (`0x1A805`) | `+0x04: 7F→FF`, `+0x05: 06→07` |
| G10 (`0x1AD22`) | `+0x50: 80 4A→10 4B`, `+0x70: B0 4B→80 4F` |
| G11 (`0x1ADC2`) | `+0x00: 80→C0`, `+0x04: 03→01`, `+0x10: 90→D0` |
| G13 (`0x1AE92`) | `+0xC0: 00 00 00 00 00→80 4C 71 02 03`, `+0xE0: 00 00 00 00 00→90 4C 71 02 01` |

At G2, new rows 39 and 40 reference original definition
indices 52 (Ancient's Stone, `0x36`) and 267 (Mana Cluster,
`0x110`). The corresponding original definition offsets
are `GLOBAL.WSX+0x5692/+0xCB4F`. G3 marks both rows occupied.
G10's first and third cast keys take the pool references
that G14 rows 11/12 already held for spells `0x59/0x54`
(decimal 89/84). The middle quick slot keeps `0x57`.
G11 points the first two pockets at the new rows. The old
pocket pointers and counts move to G13 rows 12 and 14.
G2 and G3 are stored as LZO chunks (dword expanded length,
dword packed length, LZO1X data). Only the chunk holding the
edited bytes was re-encoded, with liblzo2 `lzo1x_1_compress`;
the other chunks were copied unchanged. G10, G11 and G13 are
stored unpacked and were edited in place. The two repacked
sections grew from 964/48 to 986/63 bytes, with expanded sizes
unchanged. Update their packed-length words, add the running
22/37-byte shifts to following global starts at slot `+0x4B8`, add 37 to each level start at
`+0x5B0`, and add 37 to the total length at `+0x2C`.
[Pointer and directory requirements](lol3-native-saves.md#editing-a-copy-of-an-original-slot)

At `0x43703E` the live cast-key IDs were `59/57/54`, pocket
IDs `36/110`, mana 437 and counters 35/0. A left click on
each pocket transferred its item to the cursor. Right click
in the viewport used it through the original handler.

| Original action | Native observation |
|---|---|
| Key 2, spell `0x57` with no second charge | The ordinary writer `0x410014` stored 415, −22 from mana 437, returning to `0x4A5A52`. |
| Use Ancient's Stone | `0x49FB23` led to `0x4329D0`, first counter 35 → 36, return `0x49FB28`. |
| Key 1, spell `0x59` | `0x4A5A20` led to `0x4329D0`, first counter 36 → 35 with mana 437 at cast admission. |
| Key 3, spell `0x54` | The cast reached `0x4A46C1` with first counter 35. The view reported no enemy to attack and neither debit writer fired. |
| Use Mana Cluster | `0x4A6133` led to `0x432AE0`, second counter 0 → 1, return `0x4A6138`. |
| Key 2, spell `0x57` after Mana Cluster | `0x4A5A3A` passed −1 to the second writer, which changed 1 → 0 and returned to `0x4A5A3F`. The negative ordinary-mana watch had no hit for this cast. |

Mana here is `[0x5D5098]`, the player +0x1B8 cell that the
ordinary writer stores (ECX `0x5D4EE0`). It read 437 again at
the next cast after the 415 store. The writer watch logged only
negative arguments, so the recovery between those casts was not
traced.

The viewport showed the spell effect during the charged cast.
At the subsequent save entry `0x43766F`, mana was 437, the
first and second counters were 35 and 0, and the cursor was
empty. The exact charged HUD indicator remains **UNCONFIRMED**.
The edited-save trial establishes both original item writers
and the alternate debit once the item is available. A native
save with an acquired Mana Cluster would reproduce the
path without the inventory setup.

The autosave the game wrote at `0x43766F` (`6bf815a1e022`)
has new definition and pool bases and keeps the edits that
were not consumed. Pool rows 39 and 40 are zero again and the
G3 bytes +0x04/+0x05 are back to `7F 06`. Both G11 pockets
have a zero pointer and count. G10's three cast keys and G13
rows 12 and 14 hold the same pool rows as the edited copy
(rows 12, 18 and 83; rows 35 and 36). So the game cleared both
used items and translated the remaining pointers to its new
bases when it saved.

## Close-out

### Q12

**What was measured.** The seventeen bytes at `LOL3.DAT` file +0x30094 are `B9 20 00 00 00 33 C0 BF 58 A5 5F 00 83 C4 0C F3 AB`. They zero 32 dwords, 128 bytes, at `0x5FA558` after the decimal format call at `0x430C8F`.

**What was tried.** This slice follows the display read at `0x430C7D`. The page already records the second-counter debit, the edited-save observation, and the list-8 discounts on keys 10 and 13.

**What would settle it.** The running-game test is not yet run ([test Q12](NEEDS_A_RUNNING_GAME.md#q12-which-live-cast-consumes-an-alternate-resource), [probes not yet run](NEEDS_A_RUNNING_GAME.md#probes-not-yet-run)). Still open are native acquisition, the exact HUD feedback, individual handler effects beyond indexes 0–36, 39–70, 72–87, 89–93, 95–97, 99 and 112 (37, 38, 55, 71, 88, 94 and 98 have no regular definition), and the on-screen names of slots, keys and mask bits.
