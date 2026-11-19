# Native item definitions and use entry points

Addresses refer to the [English retail image](lol3-lmf-reader.md).

**CONFIRMED.** In the input-name table at `LOL3.DAT+0x14EA08`,
indexes 32–41 name the two bindings for each of five item slots.
The reader at `0x4F338B–0x4F33CE` looks up those names in the user
settings and resolves the configured keys. The store at `0x4F34A5`
writes the key per index into dwords at VA `0x5D4CD8`.

**CONFIRMED.** The definition initializer at `0x4ACD17` reads
139-byte rows. It tests definition flag 2 in the byte at row +0x3F (`0x4ACD4A`, `0x4ACDD5–0x4ACDE4`)
and invokes `0x4AD250` from `0x4ACDE4` when set. That function
dispatches on definition dword +0x73 minus 0x50 with upper bound
0x10A using byte table `0x4AE328` and jump slots `0x4AE20C`.
The arm at `0x4AD275–0x4AD2A6` copies row +0x5B/+0x43 to words
`0x545548/0x54554A` and sets bits depending on row +0x47.
These operations occur during definition loading.

**CONFIRMED.** The name consumer at `0x4AD110` opens
`itemjt.trr` (string at `LOL3.DAT+0x148558`). It queries a numeric
definition ID through `0x409440` at `0x4AD169`. On a hit, it copies
from the returned pointer +4 until the byte-2 delimiter, then stores
the resulting string pointer at `[0x662A9C][id]`
(`0x4AD172–0x4AD1B4`). The archive witness is the 343-entry
`DAT/locallng.wsx+0x5968140`.

**CONFIRMED.** The input builder at `0x466B60` makes six-byte
selector/key rows. The indexed loop at `0x467373–0x46739B` reads
the configured keys and registers them through `0x41DB00`.
The registration reads flag/pointer pairs from `0x545E20`
(`0x41DB53–0x41DB97`). The input event has a release bit 0x800
(`0x41D8A0–0x41D92B`), and a registered handler is called at
`0x41DA2F`.

| Configured indexes | Selectors and callbacks | Native action |
|---|---|---|
| 32–41 | 0x12–0x16, `0x41E560/570/580/590/5A0` | Slots 0–4, on release. `0x41E4B0` checks modifier cells `0x5D5800/04` for alternate routes `0x4305A0` and `0x432E50`. The default uses the HUD slot and calls `0x426D30`, which reaches item use at `0x426F7B`. |
| 46–55 | 0x19–0x1D, `0x41E340/370/3A0/3D0/400` | Slots 5–9, on press. The callbacks directly call `0x4282E0` with ECX `0x583151`. |

## Definition directory

**CONFIRMED.** The `GLOBAL\GLOBAL.ODF` entry at
`GLOBAL.WSX+0x3866` has item table offset u32 +4 = 0x1F0
and count +0x34 = 343. The loader seeks and passes the count
at `0x44057A–0x44059F` to `0x4ACC40`, and the definition
reader consumes count × 139 bytes at `0x4ACCCE–0x4ACD17`.
The table starts at `GLOBAL.WSX+0x3A56`. All 343 keys in
each of the following lookup columns are distinct in that table.

| Row field | Native interpretation and source |
|---|---|
| +0x18 u32 | Identity used by `0x440930–0x440955`. The grant command uses this identity. |
| +0x73 u32 | Numeric lookup key used by `0x440960–0x440985`. Also selects the definition-load cases and item name. |
| +0x14 dword | Overwritten with a runtime resource pointer, advanced by 16 × row u8 +0x2E (`0x4ACE0E–0x4ACE19`). |
| +0x3F dword | Bit 1 invokes the definition-load switch at `0x4ACDE4`. A specific row +0x73 value 7 also sets bits 2 and 3 (`0x4ACD62–0x4ACD8B`) and definition +0x4F bit 0x10 (`0x4ACD89`), the bit the use-effect path tests at `0x4D7C9C`; value 0x3F sets +0x4F bit 0x20 (`0x4ACD94`). Only definition 5 has +0x73 = 7. |
| +0x4F dword | Includes the state sense used by `0x4AD050–0x4AD08D`. Bit 1 of the separate byte-array row `[0x662A90][index]` is interpreted relative to definition bit 1. The two update paths invert the operations for the two senses (`0x4AD090–0x4AD106`). |
| +0x7D u16 | Nonzero disk value `v` becomes `max(1, floor(256/v))` at `0x4ACE1B–0x4ACE3E` (ESI there is row +0x4F). **CONFIRMED** reader: `0x492319` in `0x4922B0`, when its second argument is nonzero. It finds the definition's index ((definition − `[0x57017C]`) / 139) and subtracts the value from byte +0x10+index of one 366-byte record at `0x5838B8`. A value above the byte sets it to 0 (`0x49230F–0x49234E`). The one caller passing 1 is `0x491C20` (`0x491C58`), reached from `0x446D98`. The meaning of those 19 records is **UNCONFIRMED**. Break at `0x492319` and note the player action. |

## Script grants

**CONFIRMED.** Player construction installs the vtable at
`0x538388` (`0x408D80`, `0x40A504`). Table +0xC0
at `LOL3.DAT+0x136C48` resolves to `0x410AA0`. Selector
1 returns the player through `0x41EDE0 → 0x41EE00`.
The opcode-3 dispatch at `0x448025` reaches the player arm.
At `0x410B19–0x410B4B` it checks a game guard and passes
u32 command +4, u8 +0xC and mode 1 or 3 to `0x49EF70`.

**CONFIRMED.** `0x49EF7D` looks up the identity at definition
+0x18 and `0x49EF92` initializes a temporary instance. The
initializer stores the definition pointer at +0, zero at +4,
the supplied byte at +8 and zero at +9 (`0x49E940–0x49E95B`).
The pool routine at `0x49EE80` requests a 16-byte slot,
copies those fields and clears +0xC
(`0x49EED3–0x49EEE6`, `0x49E910–0x49E92D`,
`0x49E560–0x49E577`). When the request mode differs from
2, the routine also calls recipient vtable +0x78 with the
allocated pointer and grant mode (`0x49EEF0–0x49EF0E`).
The byte +8 can be set at grant time. Its purpose for all item
classes remains **UNCONFIRMED**. Readers seen so far are the
charge paths at `0x429C18–0x429C9A`, `0x49F76B–0x49F7AA` and
`0x49FC40–0x49FD10`. To settle another class, grant it with a
known +0xC and put a read watchpoint on instance +8.

**CONFIRMED.** `BUPP1.WSX+0x18CA79F` contains a 16-byte
opcode-3 grant with selector 1 and byte +0xC equal to 4.
Its identity `0xF50F9FCB` matches definition 53 at
`GLOBAL.WSX+0x571D`. Of 1,021 stored selector-1 opcode-3
records across the 18 indexed command streams, 1,010 match
the native +0x18 identity column. **CONFIRMED.** The eleven others
are ten in `BUPP1.WSX` (`+0x18CFF33` to `+0x18CFFA3` in steps of
16, `+0x18D0123`, `+0x18D0143`) and one at `HWHIT.WSX+0x1110029`.
Their identities occur in no structured data in DAT or LOL3.DAT
(three appear once each only as chance byte matches inside compressed
media), and in
neither definition key column. For such an identity `0x440930`
returns 0 (`0x440953`). `0x49EE8D` then reads definition +0x73
through that null pointer. With guard `[0x5D5378]` clear
(`0x410B19`), executing one would fault.
**UNCONFIRMED.** Whether the game ever runs them. Break at
`0x49EF82` with EAX = 0.

## Use effects

**CONFIRMED.** Common use `0x4282E0` reads the pointer in
inventory row `[ECX+0x80] + 16*slot`, or the cursor pointer at
`[0x585488]` for cursor use. A null instance or a nonzero
`0x49F170` check returns before dispatch. Definition flag
`+0x3F & 0x0C` goes through `0x433B70` into the
`0x429520` action path. The other branch builds use operation 1
and calls `0x49E960` at `0x4283AF`
(`0x4282E0–0x4283AF`). In the action path, eligible instance
bytes +8 between 101 and 109 are decremented, and that path
chooses operation 13 or 6 (`0x429C18–0x429C9A`).

**CONFIRMED.** `0x49E960` reads the definition dword +0x4B
and, if the request has no recipient, supplies the player
(`0x49E969–0x49E97C`). When definition byte +0x3F bit 1 is
set, it calls table slot 108 at `0x54BAC8`, which points to
`0x4A4520` (`0x49E97C–0x49E992`). Otherwise, after the
operation-specific guards it calls `[0x54B918 + 4*index]`
(`0x49E995–0x49EA0F`). There are 124 consecutive code pointers
in the table. The 258 regular original definitions use 114
distinct indexes. The other 85 definitions all store zero at
+0x4B and take the special arm. This census reads 343 rows at
`GLOBAL.WSX+0x3A56`. For example, definition 53 at +0x571D uses
regular index 2, destination `0x49F6D0`. Definition 77 at +0x6425
uses the [special cast arm](lol3-spell-dispatch.md#player-cast-and-cost).

**CONFIRMED.** A separate effect route at `0x4D7C6E–0x4D7CA0`
reads live object +0x34 as a definition pointer and tests
definition +0x43, instance +0x2A and definition +0x4F bit 0x10.
On the admitted path it fills a 72-byte hit request with mask
0x100, flags 4, kind 5 and subtype 0xFF
(`0x4D7CA2–0x4D7CE7`). It selects the recipient from
`[0x600764]` or `[0x600768]`.

**UNCONFIRMED.** Most regular destination effects remain open.
The input and dispatch paths now identify the exact handler.
For each regular index, use one +0x4B witness from the original
definition table and follow that destination's first state write
or effect request for operation 1. The hit route at `0x4D7C6E`
still needs an original action that reaches it.

### Regular handler examples

**CONFIRMED.** The following fourteen indexes cover 148 of the 258 regular
definitions in the original table at `GLOBAL.WSX+0x3A56`. The counts
come from definition +0x4B on rows with +0x3F bit 1 clear. An index
here identifies a destination after the common dispatch gates.

| Index and original witness | Definitions | Native behavior |
|---|---:|---|
| 0, `GLOBAL.WSX+0x3A56` | 117 | `0x49EA40–0x49EA42` returns 0 without changing state. The common guard at `0x49E9AC–0x49EA01` runs before this handler, so the stub result alone describes only the handler. |
| 1, `GLOBAL.WSX+0x40DA` | 1 | Operation 5 plays the sound named by definition u16 +0x37 (`0x422C40` at `0x49F683`). If the 0–1 draw is nonzero and request +8 is nonnull, it allocates template 0x78 and calls `0x4EAC90` with the player, target +0x5C, the address of target +0x4C and variant 1. Returns 0 (`0x49F660–0x49F6CF`). |
| 2, `GLOBAL.WSX+0x571D` | 1 | Operation 1 checks the target and can request an effect through template 0x78 (`0x49F6D0–0x49F766`). An admitted instance +8 above 3 becomes 2. Otherwise a positive value decrements by one, and zero stays zero. A resulting zero selects definition lookup key 0x38, calls `0x432A90` and returns 3. A positive result returns 4 (`0x49F76B–0x49F7AA`). |
| 3, `GLOBAL.WSX+0xA5D8` | 1 | Operation 6 projects five coordinate units from request +8's position using the angle derived at `0x4A2900` and the fixed-point trig at `0x4A2922–0x4A2994`. It allocates template 0x146 at `0x4A29A1`. The object path checks a list from `0x444800` and sends a hit through target vtable +0x8C if within 64 units of the effect. Fields are mask 0x100, flags 4, kind 5, subtype 0x51 and magnitude 50 (`0x4A2AFC–0x4A2B93`, distance `0x44AAB0–0x44AADF`). Operation 6 returns 4. Other operations return 0 (`0x4A28DC–0x4A28E9`, `0x4A2B95–0x4A2BD5`). |
| 4, `GLOBAL.WSX+0x9A71` | 1 | Operation 1 may play the sound at `[0x58C6F4]+0xD6` (`0x49F82D–0x49F851`), runs the player +0x32D update `0x418AE0` (`0x49F85B`), sets the request +0x1C instance's +4 to 60 and searches the active list by definition +0x73. A match adds 60 to the existing row and returns 2. Otherwise it adds 20 to player dword +0x1C4, calls `0x41CCA0(0x252, 1)`, refreshes groups 1, 4, 3 and 2 and returns 5 (`0x49F856–0x49F8B4`, `0x431740–0x431794`, `0x42BB50–0x42BB76`). Operation 8 decrements instance +4 if `[0x58CC10]` is nonzero. At zero it removes the 20-point modifier and returns 2. If player +0x218 still has bit 3 set and bit 26 clear, it also calls `0x430540(0x127)` and clears bit 3 (`0x49F7B5–0x49F828`). |
| 5, `GLOBAL.WSX+0x924C` and `+0x9EC9` | 2 | Operation 7 can allocate template 0x74 with variant 0 and return 2. With `[0x5853E6]` set it stores player +0x1EF (`0x5D50CF`) = 0x6E and +0x1EE = 1 and returns 4 instead (`0x49F8E3–0x49F97E`). Operations 6, 13 and 14 take the other arm of the table at `0x49FAEC–0x49FB04`. With that guard set they do the same two stores and return 0; a distance of 128 units or less also returns 0. With the guard clear and distance above 128 units, it uses numeric key 0xA5 to find the instance, can rewrite the operation from its +8 and releases it. The resulting operation sends variant 0x40 (13), 0x20 (14) or 0 (6) through `0x4EC800` and returns 4, including allocation failure (`0x49F97F–0x49FAEA`). |
| 6, `GLOBAL.WSX+0x5692` and `+0xB597` | 2 | Operation 1 adds one alternate spell charge at `0x49FB23 → 0x4329C0` and returns 2 at `0x49FB51`. |
| 7, `GLOBAL.WSX+0xC80D` | 1 | Operation 5 draws an integer from 1 through 1,000. If bit 9 of the resolved region +4 is set, the draw must exceed 749. Otherwise it must exceed 249. Success can allocate template 0x68 and call `0x4C35E0` with variant 3. A failed draw can request the u16 from `[0x58C6F4]+0xDC`. Returns 0 (`0x49FB60–0x49FC3C`, draw `0x44AA40–0x44AAA5`). |
| 8, `GLOBAL.WSX+0x5833` | 1 | Operation 1 with `[0x58323D] = 0xFF` can play a cue and returns 0. Otherwise it resolves a target using `0x46DDC0`, can create template 0x6C through `0x4C1DF0` and sets player +0x21C bit 0. With a nonzero target +0x5C, instance +8 becomes 2 if above 3 or decrements if positive. At zero the definition becomes key 0x3A and the handler calls `0x432A90` and returns 3. Other paths return 0 (`0x49FC40–0x49FD10`, definition store `0x49EA70–0x49EA85`). |
| 9, `GLOBAL.WSX+0x8F95` | 3 | Operation 1 can submit the u16 resource ID from `[0x58C6F4]+0xD6`, applies the player +0x32D update and adds 10 to player dword +0x224. Returns 2 (`0x49FD20–0x49FD71`). |
| 10, `GLOBAL.WSX+0x9FDF` | 2 | Operation 1 can submit the same resource ID. It sends a self-sourced player hit with mask 0x80, flags 0x20, kind 2, subtype 0x44 and dword +0x1C = 1 (`0x49FDBC–0x49FE05`) to `0x40AED0`, then returns 2 (`0x49FD80–0x49FE13`). |
| 54, `GLOBAL.WSX+0x5E2C` | 4 | Operations 6, 13 and 14 enter separate branches. After the `0x44AAB0` distance calculation, each requires a result above 0x800000. An available template 0x7C is passed to `0x4E96A0` along with the source and target position. The variant depends on operation and definition +0x73. These branches return 4 even when the lookup returns null (`0x4A1A30–0x4A1C6D`). |
| 87, `GLOBAL.WSX+0x9362` | 11 | Operation 1 applies the player +0x32D update, can submit the same resource ID (`0x4A38E5–0x4A3909`), and returns 2. Definition +0x73 = 0xA7 also sends the same hit as index 10 when the random result from the inclusive range 0–95 is below 32 (`0x4A3872–0x4A3921`, helper `0x44AA40`). |
| 112, `GLOBAL.WSX+0xCB4F` | 1 | Operation 1 adds one second-counter charge at `0x4A6133 → 0x432AD0` and returns 2 at `0x4A6161`. [Alternate charge and mana effects](lol3-spell-dispatch.md#producers-of-the-alternate-counters) |

**CONFIRMED.** The shared update at `0x418AE0–0x418B15`
maps the previous unsigned player +0x32D value to 0 below 900,
450 from 900 through 8,999, and 900 from 9,000 upwards. The
ordinary inventory/cursor caller handles result 2 by retrieving
the item and calling `0x49F010`, which releases the instance
(`0x4283B4–0x4283F5`, `0x49F02D–0x49F041`). Result 3 has
a separate stack-count test and callback
(`0x42846B–0x4284C0`).

**CONFIRMED.** Index 4's +0x1C4 modifier is the starting
value at `0x42A978`. The calculation zeroes it on player
+0x218 mask 0x80000. For unsigned player +0x32D above 900,
it subtracts `floor((value - 900)/10)` from the modifier,
with a minimum of `trunc(modifier*4/5)` up to 9,000
and `trunc(modifier/2)` above 9,000
(`0x42A97F–0x42A9DD`). Later steps apply more adjustments
and include equipment contributions (`0x42A9DD–0x42AA9B`).
The result feeds hit-packet magnitude at `0x4A050F–0x4A0538`
and event comparisons at `0x4BDCFE–0x4BDD58`.

**CONFIRMED.** Player +0x32D (`0x5D520D`) is the hunger value.
The tooltip at `0x42B107–0x42B12F` picks text key 0x274F below
900, 0x2750 below 9,000 and 0x2751 otherwise. In the `tooltip.trr`
entry at `locallng.wsx+0x598AD7C` these are "Not hungry", "Hungry"
and "Starving". Above 9,000 the mana ceiling `0x40FF00` (player
vtable +0xB0) drops by (value − 9,000)/30, to at least 1. Player
+0x224 (`0x5D5104`) is consumed at `0x40D668–0x40D715`. While
+0x1C0 and +0x224 are nonzero and +0x208 is zero, each pass adds a
time-scaled step of 30 × the value (`0x46E6E0`) to +0x1C0, capped by
vtable +0xA0. +0x224 is cleared, and byte +0x1EC raised by it, only
once +0x1C0 passes byte +0x1EC + value or reaches the cap
(`0x40D6D1–0x40D70F`); otherwise it stays for the next pass. +0x1C0 is the
quantity the player's hit slots +0x98/+0x9C change and read
(`0x40FF80`, `0x40FEA0`).

**UNCONFIRMED.** The visual effect from template 0x78, the on-screen
name of player +0x1C0, and the class-specific effect
of the template 0x7C variants remain open. Follow the update slot
on the object generated at `0x49F766` or `0x4A1C5E`. Trace the
readers of +0x1C0 to its first display (the readers of `0x5D520D` and
`0x5D5104` are traced above; for indexes 1, 3, 5, 7 and 8 the admission, arguments
and immediate writes are mapped in the table above).
Template-specific effects and presentation still need the
first update of the objects constructed at `0x49F6C6`,
`0x4A29B9`, `0x49F972`/`0x49FAB0`/`0x49FAD9`,
`0x49FC08` and `0x49FCBC`. Of the 100 indexes listed in the
grouping below, 36 are read in the handler tables (12–17, 19–32,
35, 36 and 39–52) 13 more (1–10, 54, 87, 112) are in the examples table above, and 51 remain only grouped. Indexes 18, 33 and
34 have a regular definition and are not in that grouping; they are
read in those tables. Index 11 has no regular definition and is
read there too.

`tools/lol3_native_checks.py --data DAT --check` rechecks the
seven new definition witnesses, native dispatch addresses and
selected calls and stores for indexes 1, 3, 4, 5, 7 and 8.

**CONFIRMED.** Direct calls in the 113 nonzero regular handlers
(using destinations from `[0x54B918 + 4 × index]` in address
order for range bounds), with indexes:

| Direct call | Handlers | Indexes |
|---|---:|---|
| Effect heap `0x4B3040` (builds a type-5 object) | 33 | 1, 2, 3, 5, 7, 8, 15, 16, 26, 27, 30, 35, 36, 50, 54, 56, 57, 58, 60, 62, 63, 68, 70, 75, 83, 84, 85, 100, 106, 109, 111, 113, 114 |
| Sound `0x422C40` | 66 | 1–10, 16, 20–22, 27–32, 39, 41–43, 45, 46, 50, 56, 62–64, 67–70, 72, 73, 75–87, 89, 90, 92, 93, 95, 96, 100, 102, 105, 106, 109–114 |
| Player +0x32D update `0x418AE0` | 22 | 4, 9, 20, 31, 39, 41, 43, 46, 67, 69, 74, 76, 79, 80, 82, 86, 87, 89, 92, 93, 95, 113 |
| Mana change `0x40FFE0` | 6 | 32, 39, 43, 90, 92, 95 |
| Player hit `0x40AED0` | 5 | 10, 42, 48, 77, 87 |
| No direct call (inline state only) | 24 | 12, 13, 14, 17, 19, 23, 24, 25, 40, 44, 47, 49, 51, 52, 53, 61, 65, 97, 101, 103, 107, 118, 119, 122 |

### Indexes 11 through 30

**CONFIRMED.** Each row is that handler's own tests, stores, calls and
returns. The operation is the dword at request +0. Other operations
return 0 unless the row says otherwise. Player +0x218 is `0x5D50F8`.
A called function is named and not followed. Index 11 is absent from
the grouping table; its body calls sound `0x422C40` and the player hit
`0x40AED0`. Index 18 is also absent from that table.

| Index | Address | Definitions | Effect | Reading |
|---|---|---:|---|---|
| 11 | `0x49FE20` | 0 | Operation 1 only. When `[0x58C6E8]` bit 0 is clear, plays the u16 at `[0x58C6F4]+0xD6` through `0x422C40`. Sends a self-sourced player hit with mask 0x80, flags 0x40, kind 2, subtype 0x45 and dword +0x1C = 1 (`0x49FE69–0x49FEA5`) to `0x40AED0`, and returns 2. No regular definition selects this index. | CONFIRMED |
| 12 | `0x4A0040` | 1 | Operation 5 only. Requires request +8 and that object's +0x5C. The player heading word at +0x26 (`0x5D4F06`) must fall in the unsigned window from the target's heading minus 0x2000 through heading plus 0x2000. That path fills a 0x48-byte record with the target at +4, the player at +8, kind 1, subtype 0xFF, mask and flags from definition words +0x3B and +0x3D, and magnitude 0x19, calls the target vtable +0x8C, then vtable +0xA4 with 0x19. Every path, including that one, returns 0 (`0x4A00F1`). | CONFIRMED |
| 13 | `0x4A0100` | 1 | Operation 11 reads player +0x218. If bit 0 is set it clears bit 0; otherwise it clears bit 27. It writes the dword back. If bit 0 is still set, or bit 27 is set, or player +0x1FC (`0x5D50DC`) is nonzero, it returns 0. Otherwise it clears bit 15 of player +0x3C0 (`0x5D52A0`) and returns 0. Operation 10 sets bit 15 of +0x3C0, then sets bit 27 of +0x218 if bit 0 is set and bit 0 otherwise. It returns 0. | CONFIRMED |
| 14 | `0x4A0180` | 1 | Operation 11 clears bit 1 of player +0x218 and returns 0. Operation 10 sets bit 1 of +0x218 and bit 2 of player +0x21C (`0x5D50FC`) and returns 0. | CONFIRMED |
| 15 | `0x4A01C0` | 1 | Operation 1 only. Calls `0x46DDC0` (`ecx = 0x58C6F8`, arguments 0x1000000 and 0). A null result returns 0. It keeps the result's +0x5C only when that object's vtable +0 returns 2 and definition byte +0x76 bit 3 is clear (`0x4A01F1–0x4A0209`). When `[0x54BF70]` is zero it drops that object. When the dword is nonzero it allocates template 0x6C through `0x4B3040` and, if that returns nonzero, calls `0x4D14E0` with the search result, the kept object and the player. A null kept object stores player +0x1EF (`0x5D50CF`) = 0x6A and +0x1EE (`0x5D50CE`) = 1 and returns 0. A kept object returns 2. | CONFIRMED |
| 16 | `0x4A0260` | 2 | Operations 5 and 6. Pushes request +8's +0x50 and +0x4C and request +4's +8 and +4 to `0x44AAB0`. A result of 0x800000 or less returns 0. Otherwise, when `[0x58C6E8]` bit 0 is clear, it plays the u16 at `[0x58C6F4]+0xF4`. It allocates template 0x78 through `0x4B3040` and, if that is nonzero, calls `0x4D14B0` with 1, the address of request +8's +0x4C, request +8's +0x5C and the player. Returns 4 even when the allocation is null. | CONFIRMED |
| 17 | `0x4A0300` | 1 | Operation 11 clears bit 2 of player +0x218 and returns 1. Operation 10 sets bit 2 and returns 1. | CONFIRMED |
| 18 | `0x4A0340` | 1 | Operation 11 clears bit 3 of player +0x218 and returns 1. Operation 10 sets bit 3 and returns 1. Operation 5 calls `0x431760` (`ecx = 0x570900`, arguments 0xB4 and 0). If that is nonzero, or bit 26 of +0x218 is set, it returns 0. Otherwise it calls `0x430540` (`ecx = 0x570900`, argument 0x127), clears bit 3 and returns 4. | CONFIRMED |
| 19 | `0x4A03C0` | 1 | Operation 17 returns 2 and writes nothing. Operation 11 clears bit 5 of player +0x218 and returns 1. Operation 10 sets bit 5 and returns 1. | CONFIRMED |
| 20 | `0x4A0400` | 1 | Operation 1 only. When `[0x58C6E8]` bit 0 is clear, plays the u16 at `[0x58C6F4]+0xD6`. Calls the player +0x32D update `0x418AE0` and then `0x41AC40`, both with `ecx = 0x5D4EE0`. Returns 2. | CONFIRMED |
| 21 | `0x4A0450` | 1 | Operation 11 clears bit 6 of player +0x218 and returns 1. Operation 10 sets bit 6 and returns 1. Operation 5 draws through `0x44AA40` (`ecx = 0x55D3D0`, arguments 0 and 4), adds 0x6F, and when `[0x58C6E8]` bit 0 is clear plays the u16 at `[0x58C6F4]` plus twice that sum. It reads request +8 and that object's +0x5C with no null test. The hit record holds the target at +4, the player at +8, kind 1, subtype 0xFF, mask 2, flags 4, and magnitude from `0x42A970` (`ecx = 0x5831E1`, arguments 1, 0 and 0), doubled when `0x433C80` (`ecx = 0x57095C`, arguments 8 and 7) is nonzero. It calls the target vtable +0x8C and returns 3. | CONFIRMED |
| 22 | `0x4A0560` | 1 | Operations 1 and 7 share `0x4A063D`. If `[0x58323D]` is 0xFF, it plays the u16 at `[0x58C6F4]+0` when `[0x58C6E8]` bit 0 is clear and returns 4. If `[0x5853E6]` is nonzero, it stores player +0x1EF = 0x6E and +0x1EE = 1, plays or skips that word, and returns 4. Otherwise a mismatch of `[0x585488]` with request +0x1C calls `0x4D8CB0` with the player and 0 and returns 2. A match with a null request +8 calls `0x46DDC0` (`ecx = 0x58C6F8`, arguments 0x7FFF0000 and 1); a null result takes that same return. When object +0x34 equals 2 and `0x44AAB0` on object +4, object +0, request +4's +8 and request +4's +4 is at most 0x1000000, it saves player +4, +8 and +0xC, copies the object's +0, +4 and +8 there, adds a `0x600870` heading step (player heading +0x26 plus 0x8000, and that sum plus 0x4000, each masked to 16 bits, indexed after a shift of 2, negated on the upper half, scaled by 40) to the copied +4 and +8, calls `0x4D8CB0` with the player and 1, restores the three dwords and returns 2. The remaining arm reads object +0x1C. A nonzero value calls `0x486930` and then, when that returns nonzero, `0x4A7480` with 0, that pointer, its word +0x18 shifted left 16, and the object's +4 and +0; a zero return from `0x486930` calls `0x4A7040` with -1, 0 and those two object dwords. A zero +0x1C takes `[0x6007A4]` when `[0x600854]` is nonzero and `[0x600768]` is the player; otherwise it takes player +0x110 (`0x5D4EF0`), or that pointer's +4 when bit 12 of player +0x118 (`0x5D4EF8`) is clear and the pointer is nonzero, and calls `0x4A7480` or, if the pointer is null, `0x4A7040` as above. Either arm then calls `0x422650` (`ecx = 0x5853F8`) and `0x49EA90` with the `0x4A7480`/`0x4A7040` result, object +0x4B AND 2, the object, the player and the `0x422650` result (push order). A zero from `0x49EA90` calls `0x422480` with the `0x422650` result. A nonzero `0x49EA90` with a nonzero `0x422650` result passes that result to `0x49E580` and `0x49E590`. This arm returns 1. Operation 18 requires request +0x18. If `[0x5853E6]` is nonzero it returns 0. The object's vtable +0 must return 2, and definition byte +0x76 bit 3 must be clear. If `[0x58323D]` is 0xFF it plays or skips the word at `[0x58C6F4]+0` and returns 4, without the +0x1EF stores. Otherwise `[0x5853E6]` is tested again (already zero here): the nonzero arm stores +0x1EF = 0x6E and +0x1EE = 1, plays or skips that word and returns 4; the zero arm calls `0x4BEBB0` with 0x12C and returns 2. | CONFIRMED |
| 23 | `0x4A0910` | 1 | Operation 17 returns 2 and writes nothing. Operation 11 clears bit 7 of player +0x218 and returns 1. Operation 10 sets bit 7 and returns 1. | CONFIRMED |
| 24 | `0x4A0950` | 1 | Operation 11 clears bit 8 of player +0x218 and returns 0. Operation 10 sets bit 8 and returns 0. | CONFIRMED |
| 25 | `0x4A0980` | 1 | Operation 11 clears bit 9 of player +0x218 and returns 1. Operation 10 sets bit 9 and returns 1. | CONFIRMED |
| 26 | `0x4A09C0` | 1 | Operation 6 only. Pushes the same four dwords as index 16 to `0x44AAB0`. A result below 0x800000 returns 0. Otherwise it allocates template 0x78 and, if that is nonzero, calls `0x4D0A70` with 0, the address of request +8's +0x4C, 6, 0 and the player. Returns 4 even when the allocation is null. | CONFIRMED |
| 27 | `0x4A0A30` | 1 | Operation 5 only; every path returns 0. Plays definition u16 +0x37 through `0x422C40` with no `[0x58C6E8]` test. The draw `0x44AA40` (`ecx = 0x55D3D0`, arguments 0 and 1) must be nonzero. It loads request +8's +0x5C before the null branch and returns 0 when either pointer is null. It copies the object's +4, +8 and +0xC, calls vtable +0x100, and adds that result's low byte, shifted left 16, to the copied +0xC. `0x44AC06` receives the player's +8 and +4 and the object's +8 and +4. The result, shifted left 8, indexes `0x600870` with the same upper-half negation as index 22; that dword times 0x80000, then shifted right 16, is added to the copied +4, and `0x405610` of the shifted angle plus 0x4000 is scaled the same way and added to the copied +8. It allocates template 0x146 through `0x4B3040`. A nonzero object is passed to `0x4B1BA0` with the local position and the target. When that returns nonzero the handler calls `0x41F6C0` with the shifted angle, 0x1E, 0 and 0x2D (one further 0 is discarded) and then `0x4B2C10` with that return, `0x4B2D80` with 0x18 and 0xC, `0x4B2BB0` with 0, 0 and 0, `0x4B2D10` with 1 and 1, `0x4B2D60` with 0x28, `0x4B2E60` with 0xF, `0x4B2D70` with 0 and `0x4B2DE0` with 0x32, 0 and 0. It then fills a hit record with the target, the player, kind 1, subtype 0xFF, mask and flags from definition words +0x3B and +0x3D, and magnitude from `0x42A970`, and calls the target vtable +0x8C. | CONFIRMED |
| 28 | `0x4A0C50` | 1 | Operation 5 only; every path returns 0. Plays definition u16 +0x37 with no sound gate. `0x44AA40` (`ecx = 0x55D3D0`, arguments 1 and 4) must return exactly 1. It loads request +8's +0x5C before the null branch and returns 0 when either pointer is null. The hit record holds the target at +4, the player at +8, kind 1, subtype 0xFF, magnitude from `0x42A970` (`ecx = 0x5831E1`, arguments 1, 0 and 0), mask 0x80 and flags 0x40. It calls the target vtable +0x8C. | CONFIRMED |
| 29 | `0x4A0D00` | 1 | Same control as index 28, except the draw must be greater than 2 and the flags word is 0x20. Returns 0. | CONFIRMED |
| 30 | `0x4A0DB0` | 1 | Operation 5 only; every path returns 0. Plays definition u16 +0x37 with no sound gate. Requires request +8 and its +0x5C, tested before use. That object's vtable +0 must return 2, and definition byte +0x76 bit 3 must be clear. It calls vtable +0xA0, loads that dword as an integer and multiplies it by the double 0.05 at `0x53FDA8`, and passes the product through `0x518450`. It then calls vtable +0x9C, vtable +0xA0 again, vtable +0xB8 with the negated scaled value, subtracts both from the +0x9C result, and calls vtable +0x98 with the difference. When `[0x58C6E8]` bit 0 is clear it plays the u16 at `[0x58C6F4]+0x3F2`, pushing 1, 0, the object and the id. It allocates template 0x6C and, if nonzero, calls `0x4D3310` with the object (request +8's +0x5C), 0x14, 0x64, 0x780000, 0x681A and 0x300. | CONFIRMED |

### Indexes 31 through 52

**CONFIRMED.** Same rules as the table above. Indexes 37 and 38 have
no regular definition, and no definition of either kind uses them.
Their slots return 1 (`0x4A0FD0` for operations 10 and 11,
`0x4A0FF0` for operation 1) and write nothing. Indexes 33 and 34 are
not in the grouping table.

| Index | Address | Definitions | Effect | Reading |
|---|---|---:|---|---|
| 31 | `0x49FEC0` | 1 | Operation 1 only. Calls the player +0x32D update `0x418AE0`, adds 0x32 to player +0x224 (`0x5D5104`) and sets bit 9 of player +0x21C (`0x5D50FC`). When `[0x58C6E8]` bit 0 is clear, plays the u16 at `[0x58C6F4]+0x1A`. Returns 2. | CONFIRMED |
| 32 | `0x49FF20` | 1 | Operation 17 returns 2 and writes nothing. Operation 11 plays the u16 at `[0x58C6F4]+0x404` when the sound gate is clear, then calls `0x4134B0` and `0x40FF80` with the dword at player +0x311 (`0x5D51F1`) and calls `0x4134F0` and the mana change `0x40FFE0` with the negation of player +0x30D (`0x5D51ED`). Returns 0. Operation 10 calls `0x40FEB0`, keeps a quarter of that result, and passes its negation to `0x4134B0` and `0x40FF80`. It calls `0x40FF00`, keeps a quarter of that result, and passes it to `0x4134F0` and `0x40FFE0`. It then plays the u16 at `[0x58C6F4]+0x3EE` when the sound gate is clear, stores the mana-ceiling quarter at +0x30D and the `0x40FEB0` quarter at +0x311, and returns 0. | CONFIRMED |
| 33 | `0x4A4470` | 2 | Returns 0 at once when `[0x58323D]` is 0xFF. Operation 19 calls `0x4193F0` with request +0x18 and returns 0. Operation 1 calls `0x49ECF0` with request +0x1C, request +4, the address of request +8's +0x4C and 1, then `0x419460` with the player and that result, then `0x432150` (`ecx = 0x570900`, argument 0x146). A nonzero result returns 2. A zero result calls `0x49EA70` with request +0x1C and 0x146, stores 1 at that object's byte +8, and returns 3. | CONFIRMED |
| 34 | `0x4A4500` | 1 | Operation 1 calls `0x4193B0` with the player and returns 2. | CONFIRMED |
| 35 | `0x4A0EF0` | 1 | Operation 6 only. The same four-dword `0x44AAB0` test as index 16 must be at least 0x800000. Allocates template 0x78 and, if nonzero, calls `0x4D13D0` with the player, 0, 6, 0xF0000, 3 and the address of request +8's +0x4C. Returns 4 even when the allocation is null. | CONFIRMED |
| 36 | `0x4A0F60` | 2 | Operations 5 and 6. The same distance test must be at least 0x800000. Allocates template 0x74 and, if nonzero, calls `0x4C4D20` with the player, 0, the address of request +8's +0x4C, 0x140000 and 3. Returns 4 even when the allocation is null. | CONFIRMED |
| 39 | `0x4A1010` | 1 | Operation 1. Plays the u16 at `[0x58C6F4]+0xD6` when the sound gate is clear, calls `0x418AE0`, passes 5 to `0x40FFE0`, plays the u16 at `[0x58C6F4]+0x3EE` when the gate is clear, and returns 2. | CONFIRMED |
| 40 | `0x4A1090` | 1 | Operation 1 returns 1 and writes nothing. | CONFIRMED |
| 41 | `0x4A10B0` | 1 | Operation 1. Plays the u16 at `[0x58C6F4]+0xD6` when the sound gate is clear, calls `0x418AE0`, adds 0x14 to player +0x224 and returns 2. | CONFIRMED |
| 42 | `0x4A1110` | 1 | Operation 1. Plays the u16 at `[0x58C6F4]+0xD6` when the sound gate is clear, then draws through `0x44AA40` (`ecx = 0x55D3D0`, arguments 1 and 0x3E8). A result above 0x3B5 sends a self-sourced player hit with mask 0x80, flags 0x40, kind 2, subtype 0x45 and dword +0x1C = 0. A result above 0x31F and at most 0x3B5 sends one with mask 0x80, flags 0x20, kind 2, subtype 0x44 and dword +0x1C = 0. Both go to `0x40AED0`. A lower result sends no hit. Returns 2. | CONFIRMED |
| 43 | `0x4A1210` | 1 | Operation 1. Same calls as index 39, except `0x40FFE0` receives 0x32. Returns 2. | CONFIRMED |
| 44 | `0x4A1290` | 1 | Operation 11 clears bit 10 of player +0x218 and returns 1. Operation 10 sets bit 10 and returns 1. | CONFIRMED |
| 45 | `0x4A12D0` | 1 | Operations 1 and 7. If `[0x58323D]` is 0xFF, plays or skips the u16 at `[0x58C6F4]+0` and returns 4. If `[0x5853E6]` is nonzero, stores player +0x1EF = 0x6E and +0x1EE = 1, plays or skips that word, and returns 4. The in-range arm (object +0x34 equals 2 and `0x44AAB0` on object +4, object +0, request +4's +8 and request +4's +4 is at most 0x1000000) saves and restores player +4, +8 and +0xC around the same `0x600870` heading step as index 22, calls `0x4D8EC0` with the player and 1, and returns 2. A mismatch of `[0x585488]` with request +0x1C calls `0x4D8EC0` with the player and 1 and returns 2. A null result from `0x46DDC0` (`ecx = 0x58C6F8`, arguments 0x7FFF0000 and 1) calls `0x4D8EC0` with the player and 0 and returns 2. The far arm is the same `0x486930`, `0x4A7480`, `0x4A7040`, `0x422650`, `0x49EA90`, `0x422480`, `0x49E580` and `0x49E590` sequence as index 22 and returns 1. | CONFIRMED |
| 46 | `0x4A15C0` | 1 | Operation 1. Plays the u16 at `[0x58C6F4]+0xD6` when the sound gate is clear, calls `0x418AE0`, calls `0x413520` with the player, and returns 2. | CONFIRMED |
| 47 | `0x4A1610` | 1 | Operation 17 returns 2 and writes nothing. Operation 11 clears bit 11 of player +0x218 and returns 0. Operation 10 sets bit 11 and returns 0. | CONFIRMED |
| 48 | `0x4A1650` | 1 | Operation 5 only; every path returns 0. If bit 11 of player +0x218 is set, it returns 0. Otherwise it sends a self-sourced player hit through `0x40AED0` with mask and flags from definition words +0x3B and +0x3D, kind 1, subtype 0xFF and magnitude from `0x42A970` (`ecx = 0x5831E1`, arguments 1, 0 and 0). | CONFIRMED |
| 49 | `0x4A16E0` | 1 | Operation 11 clears bit 12 of player +0x218 and returns 1. Operation 10 sets bit 12 and returns 1. | CONFIRMED |
| 50 | `0x4A1720` | 1 | Operation 6 only. The same distance test must be at least 0x800000, or it returns 0. If request +8's +0x5C is null, or that object's vtable +0 does not return 2, it allocates template 0x7C and, when that is nonzero, calls `0x4E96A0` with request +4, the address of request +8's +0x4C, 2 and 0, then returns 4. When the vtable returns 2, it copies the object's +4 and +8, stores object +0xC plus vtable +0x100's low byte shifted left 16 as the third local coordinate (the object is not written), and scans the target's definition (object +0x34) bytes 0 through 3 for the values 4, then 3, then 2. A matching byte reads the word at that definition +4 plus 4 times that index; object byte +0xE5 selects the exemptions below. Word bit 4, unless that byte is 0x2A, 0x2B or 0x2C, allocates template 0x78 and, if nonzero, calls `0x4D0A70` with request +4, the object, 6, the adjusted position and 1. Word bit 0, with the same three exemptions, allocates template 0x74, calls `0x4C3110` with the player, the object and 1 when the allocation is nonzero, and sets bit 7 of player +0x21C. Word bit 5, unless the byte is 0x2C or 0x29, plays the u16 at `[0x58C6F4]+0xF4` when the sound gate is clear, allocates template 0x78 and, if nonzero, calls `0x4D14B0` with the player, the object, the adjusted position and 1. If no word matches, it allocates template 0x7C and, if nonzero, calls `0x4E96A0` with request +4, the adjusted position, 2 and the object. Each of these arms returns 4 even when the allocation is null. | CONFIRMED |
| 51 | `0x4A1960` | 1 | Operation 11 clears bit 13 of player +0x218 and returns 1. Operation 10 sets bit 13 and returns 1. | CONFIRMED |
| 52 | `0x4A19A0` | 1 | Operation 17 returns 1 and writes nothing. Operation 11 clears bit 14 of player +0x218 and returns 1. Operation 10 sets bit 14 and returns 1. | CONFIRMED |

`lol3_combat_census.py --check` recounts the definitions per index.
Index 115 calls `0x48EBE0` on the object at `0x5860F0` (the
[opcode 0x1A](lol3-script-opcodes.md#per-class-effects-of-the-indirect-commands)
receiver), and index 123 reads a file through `0x4357A0`.
