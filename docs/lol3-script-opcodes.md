# LoL3 MAP script opcodes and framing

Addresses use the [English retail PE convention](lol3-lmf-reader.md).
The [object and script reader](lol3-object-dispatch.md) gives the MAP
header offsets, predicate reader and route from an object event to
a script command.

**CONFIRMED.** The length function at `0x4E56A0` subtracts one from
u8 command +0, bounds the result to 0xEF, reads an index byte at
`0x4E5790 + opcode - 1`, and jumps through
`0x4E56F0 + 4 * index`. An arm either returns a constant or uses
the zero return at `0x4E56EF`. The table below lists the 39
positive sizes (40 jump slots; slot 39 is the zero return). The low destinations are the 28 object slots at
`0x449A1C`, indexed by opcode minus one. The map destination uses
the index byte at `0x4E5AB4 + opcode - 0x15` and jump slots at
`0x4E5A7C` (`0x4E59A3–0x4E59BE`). The group runner handles an
initial 0xF0 itself (`0x4E58A2–0x4E58B6`).

The effects below are **CONFIRMED** to the address or operation
stated. An **UNCONFIRMED** marker qualifies the continuation.
Each observed opcode has one original WSX offset. The six absent
opcodes have an original executable witness. Those operands are
not observed in the 18 MAP ranges.

In the witness column, "size selector" means the opcode's index byte in the length table at `0x4E5790` (the opcode never occurs in a MAP, so the program itself is the witness). Archive names are case-insensitive; some files are stored in lower case.

| Opcode | Bytes | Native case VA | Stored records in 18 MAPs | File witness | Native effect |
|---|---:|---|---:|---|---|
| 0x01 | 6 | `0x447F31` | 1,175 | `BUPP1.WSX+0x18C8633` | Calls target vtable +0xC0 with the command (0x447F31–0x447F3C). All 1,175 stored records use selector 32, so they reach the type-0x20 mover arm `0x4D662B`: the target position becomes u8(+4) percent of the mover's travel. See [per-class effects](#per-class-effects-of-the-indirect-commands). |
| 0x02 | 6 | `0x447FB0` | 1,941 | `BUPP1.WSX+0x18C800C`, +4=32 | For +4 = 2 or 3, resolves the object from +1/u16 +2 and calls player helper 0x415540 or 0x415620. Other values route to player command 0x410AA0 (0x447FB0–0x448016). |
| 0x03 | 16 | `0x448020` | 1,799 | `BUPP1.WSX+0x18CA79F` | Calls target vtable +0xC0 and keeps its result (0x448020–0x44802B). The player and creature arms grant item definition u32 +4 with byte +0xC through `0x49EF70` (`0x410B19–0x410B4B`, `0x4B8D59–0x4B8D64`). Type 16 returns 1 with no effect. Selector 192 resolves at run time. See [per-class effects](#per-class-effects-of-the-indirect-commands). |
| 0x05 | 6 | `0x447E3E` | 4,496 | `BUPP1.WSX+0x18C83C9` | Calls target virtual +0xC8 with u8 +4 and +5 (0x447E3E–0x447E4E). |
| 0x06 | 6 | `0x447E59` | 1,204 | `BUPP1.WSX+0x18C9F4B`, +4=1 | Runs the object action switch on +4 through 0x446290, table 0x446438 (0x447E59–0x447E5C). |
| 0x07 | 6 | `0x447E66` | 1,494 | `BUPP1.WSX+0x18CF98D` | Calls target virtual +0xCC with u8 +4/+5 (0x447E66–0x447E76). |
| 0x08 | 8 | no case (`0x4499EB` is the object switch's default exit, the `ja` target at `0x447E31`) | 0 | `LOL3.DAT+0xE4B97`, size selector | The object table slot reaches the common exit without a command body (0x4499EB). |
| 0x09 | 6 | `0x447E81` | 10,110 | `BUPP1.WSX+0x18C7EB1`, +4=21 | Dispatches object property u8 +4 through 0x447680 and table 0x447AE0. The selector byte indexes the table directly: selector 17 (0x11) sets object +0x18 bit 0x4000 (0x4476B3–0x4476B9); selectors 0 and 1 return 0 (0x4477BB). |
| 0x0B | 8 | `0x448298` | 0 | `LOL3.DAT+0xE4B9A`, size selector | Passes u16 +4 to 0x4EED60 at 0x44829F. That helper is a bare return in this executable (file +0xEE160). |
| 0x0D | 8 | `0x447F31` | 5,269 | `BUPP1.WSX+0x18C8A95` | Calls target virtual +0xC0 with the complete command (0x447F31–0x447F3C). 5,213 records target creatures, which switch on subcommand u8 +4 (33 arms at `0x4B8D78`). The 56 type-3 records reach `0x44FE60`, which returns 1 with no effect. See [creature subcommands](#creature-subcommands-of-opcode-0x0d). |
| 0x0E | 8 | `0x447E8E` | 1,588 | `BUPP1.WSX+0x18C85F3`, +4=4 | Selects kind-2 timer by u8 +6, then uses u8 +4 as the operation 0–6 and +5 as its argument (0x44676C–0x4467CD). |
| 0x0F | 8 | `0x4484B7` | 219 | `BUPP1.WSX+0x18C8CBD` | Builds a point 10 fixed-point world units ahead of the target and a second point from selector +5/u16 +6, then reads action +4 (0x4484DA–0x4485C5). Action +4 (0–0x94) selects an arm through index bytes `0x449BEC` and slots `0x449A8C`. Each of the 16 stored actions allocates a type-5 effect object from heap `0x660CA4` and passes the target, the second object and the point. See [effect actions](#effect-actions-of-opcode-0x0f). |
| 0x10 | 6 | `0x447F44` | 3,047 | `BUPP1.WSX+0x18C7FCD`, +4=1 | Writes command u8 +4 to object state +0x31 (0x447F44–0x447F49). |
| 0x11 | 6 | `0x447F74` | 351 | `BUPP1.WSX+0x18CA4F3`, +4=1 | Adds command s8 +4 to unsigned object state +0x31 and clamps to 0–255 (0x447F74–0x447F8F). |
| 0x12 | 18 | `0x447E9B` | 288 | `BUPP1.WSX+0x18C8A71` | Uses a sequence slot at 0x600828. With flag +0xA bit 0x20, resets progress, clears the slot and sends value 6 to the object matcher (0x447EA1–0x447ED8). |
| 0x13 | 10 | `0x449905` | 15 | `EWOD1.WSX+0x1894F72` | Fills and submits a hit request using two mask words, magnitude u8 +8 and mode +9 (0x449908 → 0x4E7290). |
| 0x14 | 10 | `0x448055` | 2,773 | `BUPP1.WSX+0x18C7EF9` | Passes u16 resource ID +4, current object and a pointer to +6 to 0x422C40 (0x44806A–0x44807D). |
| 0x15 | 6 | `0x447F97` | 25 | `CKEEP.WSX+0xD0546C` | Passes unsigned bytes +4 and +5 to the same indexed function 0x46FA60 (0x447F97–0x447FA3). The high table also has a 0x15 slot (0x4E59EF → 0x4E5D10 → 0x46FA60), but the group runner sends every command below 0xC3 to the object queue (0x4E58F4–0x4E58F6), so that slot is not reached for 0x15. The first argument indexes the movie-stem table at 0x46FCF2. See [movie lookup](formats/vqa.md) for the resulting resource path. |
| 0x16 | 18 | `0x4480A4` | 2,642 | `BUPP1.WSX+0x18CA0FD` | Compares the identifier at +4 against active object/queue identifiers in branch-specific paths (0x4480C5–0x448110, 0x44819D–0x448212). The admitted branch uses command +8–+0x0B as a dialogue tag (0x448237–0x448287). See the [native dialogue lookup](lol3-dialogue-dispatch.md). |
| 0x17 | 6 | `0x447F51` | 80 | `BUPP1.WSX+0x18C7EED` | Writes the low byte of 0x44AA40(0, (u8(+4) << 5) + 31) shifted right five to object +0x31 (0x447F51–0x447F6C). |
| 0x18 | 10 | `0x448033` | 2 | `BUPP1.WSX+0x18D148A` | Checks flag 4 in byte 0x58C562 and current object 0x5896F4, then normally calls 0x422FA0 with +4/+6. The flag branch enters the continuation of 0x1C (0x448033–0x44809A). |
| 0x19 | 16 | `0x4482AC` | 53 | `BUPP1.WSX+0x18C8D4F` | Reads three dwords at +4/+8/+0xC. Value 5 at +0xC selects 0x434560, otherwise calls 0x434180 (0x4482AC–0x4482D1). |
| 0x1A | 45 | `0x4482DB` | 151 | `BUPP1.WSX+0x18C7FD3` | When 0x600854 is zero, resolves the pair +8/+0xC and calls 0x48EBE0 with the object, +4/+0x10 and pointers +0x14/+0x1D (0x4482DB–0x448316). |
| 0x1B | 10 | `0x449912` | 1,654 | `BUPP1.WSX+0x18CB66B` | Queue marker or continuation. Subcommand +8 takes the four-arm switch at 0x449C84, which can clear object +0x1C bit 0x80000 or process matching queued commands (0x44991C–0x4499E1). |
| 0x1C | 38 | `0x448320` | 217 | `BUPP1.WSX+0x18C9F51` | Gates on 0x600854. It allocates 0x146 bytes from heap `0x660CA4`, builds a type-5 object of vtable `0x5392C8` (`0x4B1BA0`) at the target's position, then sets its fields from the command (0x448320–0x4484B2). See [opcode 0x1C fields](#opcode-0x1c-fields). The visible role of that class is **UNCONFIRMED**. Settle it in a running game: break after `0x4484AD` while a stored record such as `BUPP1.WSX+0x18C9F51` runs and capture the frame. |
| 0xC4 | 12 | `0x4E59D3` | 453 | `BUPP1.WSX+0x18C87E3` | Animates the floor or ceiling height of the 56-byte map region selected by u16 +2 (0x4E5EC0–0x4E63B0). It stays in the map queue and steps once per frame. See [opcode 0xC4 flags](#opcode-0xc4-flags). |
| 0xC5 | 6 | `0x4E59E1` | 584 | `BUPP1.WSX+0x18C83AB`, +4=10 | Selects a map region with u16 +2 and switches on +4 to edit region flags or an associated table row (0x4E5D30–0x4E5E34). |
| 0xC6 | 6 | `0x4E59FD` | 217 | `BUPP1.WSX+0x18C8231`, +4=31 | Stores byte +5 to the level array at index +4 (0x4E5BD0). |
| 0xC7 | 6 | `0x4E5A27` | 159 | `BUPP1.WSX+0x18CAA91`, +4=21 | Stores byte +5 to the shared array at index +4 (0x4E5C30). |
| 0xC8 | 6 | `0x4E5A43` | 0 | `LOL3.DAT+0xE4C57`, size selector | Writes a bounded RNG result to shared-array index +4 (0x4E5C90–0x4E5CBF). |
| 0xC9 | 6 | `0x4E5A35` | 0 | `LOL3.DAT+0xE4C58`, size selector | Writes a bounded RNG result to level-array index +4 (0x4E5CD0–0x4E5CFA). |
| 0xCC | 8 | `0x4E59C5` | 237 | `BUPP1.WSX+0x18CF361` | Uses s16 +4 to select a region update (−1 or −2) or an 8-byte auxiliary row store (0x4E63C0–0x4E643F). |
| 0xCD | 8 | no case (`0x4E5A77` is the high switch's range return, `pop esi; ret 4`) | 0 | `LOL3.DAT+0xE4C5C`, size selector | The map-side table reaches the common return, with no body (0x4E5A77). |
| 0xCE | 6 | `0x4E5A0B` | 4 | `GRULO.WSX+0xCC3986`, +4=9 | Adds s8 +5 at shared-array index +4 and clamps to 0–255 (0x4E5C50–0x4E5C77). |
| 0xCF | 6 | `0x4E5A19` | 149 | `BUPP1.WSX+0x18CFAB5`, +4=29 | Adds s8 +5 at level-array index +4 and clamps to 0–255 (0x4E5BF0–0x4E5C17). |
| 0xD0 | 8 | `0x4E5A51` | 111 | `BUPP1.WSX+0x18C7F4F`, +4=3 | Selects one of five branches by +4. Arm 0 extends a duration to at least u8(+6) × 60 × 65536 and raises byte 0x55D3A6 to at least +5, or clears both when +5 is zero (0x4E66D0–0x4E6758). |
| 0xD1 | 10 | `0x4E5A5F` | 0 | `LOL3.DAT+0xE4C60`, size selector | Uses u16 +2 to find a 44-byte region-group row, directly or via selector 0x90 and the 56-byte region table (0x4E69BD–0x4E6A08). |
| 0xD2 | 6 | `0x4E5A6D` | 127 | `BUPP1.WSX+0x18C7E3F`, +4=0 | Uses +4 to dispatch through the settings table 0x4E6CD8, reading u8 +5 in the arms that +4 selects (0x4E6A80–0x4E6BDE). |
| 0xF0 | 6 | `0x4E5880` | 12,306 | `BUPP1.WSX+0x18C7E39`, +4=3 | At group entry, byte +4 counts following records for the native size walker (0x4E58A2–0x4E58B6). |

## Per-class effects of the indirect commands

**CONFIRMED.** Command byte +1 is a selector and u16 +2 an index.
`0x41EDE0` maps the selector through the index bytes at `0x41EF54`
and the slots at `0x41EF20` (`0x41EDE5–0x41EDF9`). The six object
selectors equal the number that slot 0 of the resolved object's
vtable returns, which is the object type:

| Selector = type | Resolver arm and pool | Loader (MAP header seek / count field) | Vtable, slot 0 | +0xC0 handler |
|---:|---|---|---|---|
| 1, player | `0x41EE00` returns `0x5D4EE0` | — | `0x538388`, `0x4100A0` | `0x410AA0` |
| 2, creature | `0x41EE08`, pool `[0x7D7718]` | `0x4B44F0` (+0x1C / +0x68) | `0x53FE28`, `0x4B9170` | `0x4B86D0` |
| 3 | `0x41EE2F`, pool `[0x659EF4]` | `0x44FCD0` (+0x14 / +0x60) | `0x53F2C0`, `0x4502B0` | `0x44FE60` |
| 4, item | `0x41EE56`, pool `[0x7D7824]` | `0x4D7480` (+0x20 / +0x6C) | `0x540580`, `0x4D82A0` | `0x4D84D0` |
| 16 | `0x41EE7D`, pool `[0x65B794]` | `0x469980` (+0x18 / +0x64), 33-byte rows | `0x53F6E8`, `0x46AF60` | `0x46B710` |
| 32, mover | `0x41EEA4`, pool `[0x7D77F0]` | `0x4D59F0` (+0x24 / +0x70), 41-byte rows | `0x540458`, `0x4D5B10` | `0x4D65B0` |

The MAP loader calls the five loaders in the order of the table's rows 3, 16, 2, 32, 4 after seeking to the header field shown (`0x43EEB6–0x43EF6F`). Selectors 128, 144, 160 and 176 return rows of the map tables at `[0x570190]`, `[0x570194]`, `[0x570198]` and `[0x57018C]`; selector 192 returns the object in `[0x600850]` (`0x41EEC7–0x41EF19`). Type-4 objects are also built by the item pool (`0x4D7020` called from `0x49EAB8`). Type-32 objects are built on top of the type-16 constructor (`0x4D58FB → 0x4698D0`), and their +0xC0 handler passes every command except opcodes 1 and 9 to the type-16 handler (`0x4D65C3–0x4D65C6`).

**CONFIRMED.** Type 5 is the transient effect family. Of the 97 vtables installed by a constructor store whose +0xC0 slot is `0x43B100` (`xor eax, eax; ret 4`), 96 return 5 from slot 0 and one (`0x53FAE0`) returns 6, so a command sent to one of them does nothing. No selector reaches type 5 (index byte 12 at `0x41EF54` takes the null return `0x41EF1A`). Two base vtables (`0x539AC0`, `0x53F3E0`) have the pure-call stub `0x519F30` (`push 0x19; call 0x519250`) at +0xC0.

| Handler | Opcodes acted on | Effect |
|---|---|---|
| `0x410AA0` player | 2 (subcommand table `0x4117D4`), 3 | Opcode 3: unless byte `[0x5D5378]` is set, grants item definition u32 +4 with byte +0xC and mode 1, or mode 3 when `[0x545540]` is set, through `0x49EF70`; returns whether the grant succeeded (`0x410B19–0x410B60`). Opcodes 1 and 0x0D return 0 (`0x410B04–0x410B16`). |
| `0x4B86D0` creature | 3, 9, 0x0D | Returns 0 at once when +0x110 bit 31 is set (`0x4B86D5–0x4B86EA`). Opcode 3 grants u32 +4 with byte +0xC, mode 1, to the creature through `0x49EF70` (`0x4B8D59–0x4B8D64`). Opcode 0x0D is ignored in behaviour 15 (`0x4B8710–0x4B8719`) and otherwise switches on +4 (below). Opcode 9 switches on +4 − 0x25 (`0x4B8CB9–0x4B8CD2`), for example adding to word +0x106. Opcode 1 returns 1 with no effect. |
| `0x44FE60` type 3 | none | Returns 1. |
| `0x4D84D0` item | 9 | Opcode 9 subcommands 0x1A–0x1D (slots `0x4D8574`): 0x1A and 0x1B call the definition state helpers `0x4AD090` / `0x4AD0D0`; 0x1C looks up definition +0x73 through `0x433050` on `0x570900` and passes the result with the player `0x5D4EE0` to `0x49F010` (`0x4D8518–0x4D853B`); 0x1D starts at `0x4D8544` from the same definition field. Other opcodes return 0. |
| `0x46B710` type 16 | none | Returns 1. |
| `0x4D65B0` mover | 1, 9 | Opcode 1 below. Opcode 9 subcommands 0x23–0x2B (`0x4D65CF–0x4D65E0`), e.g. 0x23 sets +0x5C bit 0x10. |

Opcode 9 reaches +0xC0 for the selectors its own switch does not take (`0x447AD0`).

**CONFIRMED.** Stored records over the 18 MAP ranges, by selector:

| Opcode | Selector 1 | 2 | 3 | 16 | 32 | 192 |
|---|---:|---:|---:|---:|---:|---:|
| 0x01 | 0 | 0 | 0 | 0 | 1,175 | 0 |
| 0x03 | 1,021 | 346 | 0 | 16 | 0 | 416 |
| 0x0D | 0 | 5,213 | 56 | 0 | 0 | 0 |

So every stored 0x0D on type 3 and every 0x03 on type 16 is a no-op in the retail program, and a 0x03 with selector 192 grants an item only when the current object is the player or a creature.

### Opcode 0x01 on a mover

**CONFIRMED.** The 41-byte mover row supplies flags +0x21 → +0x5A,
kind +0x22 → +0x5B, flags +0x23 → +0x5C, travel +0x24, speed
+0x25 → +0x5E, start +0x26 → position +0x50 (`<< 16`), state
+0x27 → +0x5D and target +0x28 → +0x58 (`0x4D591B–0x4D5994`). For
kind 6 the travel is `0x41F680(2 × row +0x24)` and the base height
is the object's +0x26 (`0x4D5963–0x4D597B`).

The opcode-1 arm sets target +0x58 to `u8(+4) × travel / 100`
(multiply by `0x51EB851F`, shift 5). Kind 6 compares it with the
unsigned position; other kinds compare `target << 16` with the
signed 16.16 position (`0x4D662B–0x4D6781`). Equal leaves the
mover idle (+0x5D = 1 if the position is nonzero, else 0). A
larger target sets state 2 and starts the definition's sound at
+0x26 with volume +0x2C; a smaller one sets state 3 with sound
+0x2A and volume +0x37; zero travel sets state 4 (`0x4D667D–0x4D6820`,
sound call `0x422C40`). The arm then sets +0x1C bit 0 and links the
object into the update lists `0x600840` / `0x60083C`
(`0x4D6825–0x4D684A`).

The update `0x4D5B80` (vtable slot +0x3C) moves the position toward
the target at a rate from +0x5E and the frame time `[0x58CBA1]`
(`0x4D5E8C–0x4D5F45`). On arrival it sets state 1 and raises object
event 0xF at the full travel or 0x11 otherwise, through slot +0xD0
and `0x4A87A0` (`0x4D5F0E–0x4D5F37`). The position is applied by
kind:

| Kind +0x5B | Placements | Opcode-1 targets | Applied as (`0x4D5F64–0x4D61C7`) |
|---:|---:|---:|---|
| 0 | 160 | 310 | Vertical: `(base +0x54 << 16) − object +0xC + position` into `[0x600728]` |
| 1 | 77 | 112 | Vertical, the same with `− position` |
| 2 / 3 | 16 / 16 | 23 / 3 | Horizontal second coordinate `+position` / `−position` |
| 4 / 5 | 61 / 70 | 132 / 135 | Horizontal first coordinate `−position` / `+position` |
| 6 | 378 | 460 | Height field +0x26 = base +0x54 ± position (sign from +0x5A bit 0) |
| 9 | 58 | 0 | Not targeted by opcode 1 |

For kinds 2–5 the move goes through `0x469550` / `0x469400` and
the step is published in `0x600720`–`0x600728`. Every stored
opcode-1 index is below its level's mover count.

### Creature subcommands of opcode 0x0D

**CONFIRMED.** Subcommand u8 +4 indexes 33 slots at `0x4B8D78`
(`0x4B871F–0x4B872D`); values above 0x20 and most arms finish at
`0x4B8CA5`, which clears word +0xD0 and returns 1. Field names
follow the [combat page](lol3-combat-dispatch.md): +0xFC/+0xFD
current and requested behaviour, +0xFE/+0xFF current and requested
action, +0x68 and +0x6C targets, +0xF8/+0xF9 path and waypoint.

| +4 | Records | Arm | Effect |
|---:|---:|---|---|
| 0 | 335 | `0x4B8734` | Behaviour +0xFC and +0xFD = u8 +5; sets +0x118 bit 0. Behaviour 0x10 clears +0x110 bits 0x600 and +0x118 bits 0x30; others call slot +0x10C. |
| 1 | 48 | `0x4B87A3` | Action +0xFE and +0xFF = u8 +5. |
| 2 | 3,145 | `0x4B87C6` | Only in behaviour 0x10: `0x4BAAF0(u8 +5, 1, −1)`. |
| 3 | 0 | `0x4B87F4` | `0x4F28F0(u8 +5)`. |
| 4 | 50 | `0x4B8815` | Slot +0xC8 with (u8 +5, 0), the slot opcode 5 uses. |
| 5 | 0 | `0x4B883B` | u8 +5 nonzero clears +0x110 bit 0x100; zero sets it. |
| 6 | 4 | `0x4B887C` | Sets +0x110 bit 0x80. |
| 7 | 269 | `0x4B8898` | Clears +0x110 bit 0x80, +0x68 and +0xF1, applies the requested behaviour (`0x4B4A70`), +0x118 = 1. |
| 8 / 9 / 10 | 15 / 8 / 19 | `0x4B88D3` / `0x4B88F0` / `0x4B890D` | Clear +0x110 bit 0x200 / 0x400 / both. |
| 11 / 12 / 13 | 1 / 15 / 284 | `0x4B892A` / `0x4B8956` / `0x4B8982` | Set +0x110 bit 0x200 / 0x400 / both, and +0x114 bit 0x100. |
| 14 | 0 | `0x4B89AE` | +0x6C = object (selector u8 +5, index u16 +6); clears +0xF2. |
| 15 | 0 | `0x4B89E1` | +0x68 = object (u8 +5, u16 +6). |
| 16 | 0 | `0x4B8A0D` | Global `[0x7D772C]` = row u16 +6 of the 8-byte table `[0x5701A4]`, or 0 for 0xFFFF. |
| 17 / 18 | 553 / 0 | `0x4B8A9F` / `0x4B8ABC` | `0x4BA360(0)` / `0x4BA360(2)`. |
| 19 | 0 | `0x4B8AD9` | Path +0xF8 = u8 +5, waypoint +0xF9 = byte +6; clears +0x118 bits 0x30. |
| 20 | 389 | `0x4B8B35` | `0x4B8E30()`. |
| 21 | 0 | `0x4B8B0D` | Clears +0x110 bits 0x600, sets bit 0x80, `0x4BA9A0(0)`. |
| 22 | 2 | `0x4B8A5B` | Waypoint-table index +0xD4 = u16 +6 unless 0xFFFF; in behaviour 3 or 12 also +0x118 = 1. |
| 23 | 0 | `0x4B8B50` | Unlinks every carried item from list +0xCC (`0x49E870`) and passes it to `0x49F010` with the creature. |
| 24 | 0 | `0x4B8B92` | Definition (+0x34) byte +0x3D = u8 +5. |
| 25 / 26 | 0 / 0 | `0x4B8BAF` / `0x4B8BD2` | Set / clear +0xC4 bit 0x100. |
| 27 / 28 | 53 / 2 | `0x4B8BF5` / `0x4B8C12` | 27: +0xB2 = u8 +5. 28: sets +0xC4 bit 0x400. |
| 29 | 0 | `0x4B8C35` | Clears +0xC4 bit 0x400. |
| 30 | 19 | `0x4B8C58` | `0x4B8F90()`. |
| 31 / 32 | 0 / 2 | `0x4B8C96` / `0x4B8C73` | Clear / set +0x114 bit 0x200. |

The 56 type-3 records (+4 values 0, 1, 2, 20) do nothing.

### Effect actions of opcode 0x0F

**CONFIRMED.** Each stored action allocates from heap `0x660CA4`
through `0x4B3040` and constructs a type-5 object with the target
object, the second object and the point (+0x1C local):

| +4 | Records | Arm | Size | Constructor → vtable |
|---:|---:|---|---:|---|
| 6 | 4 | `0x4486BB` | 0x68 | `0x4C1C70` → `0x53E238` |
| 15 | 8 | `0x448776` | 0x68 | `0x4C35E0` → `0x53DDB8` |
| 32, 33, 119 | 3, 2, 32 | `0x44862D`, `0x448658`, `0x44903D` | 0x78 | `0x4D0A70` → `0x53D250` (32 passes mode 1, 33 mode 2) |
| 59 | 60 | `0x448B67` | 0x70 | `0x4D2630` → `0x53BA60` |
| 60 | 7 | `0x448B3E` | 0x78 | `0x4C4E00` → `0x53B940` |
| 62 | 3 | `0x448B8B` | 0x78 | `0x4C6A10`: gated on `[0x58C6E8]` bit 0, starts a sound, then `0x4C6520` |
| 81 | 9 | `0x448D81` | 0x78 | `0x4D14B0` → `0x53A980` |
| 91, 92 | 22, 2 | `0x4489F5`, `0x448A5D` | 0x7C | `0x4E96A0` → `0x539F40` (`0x449002` / `0x44902C` tails) |
| 101, 102 | 8, 29 | `0x44898F`, `0x4489C2` | 0x6C | Spell effect `0x4C4320` → `0x539E20` with spell 0x65 / 0x66 ([spell effect](lol3-spell-dispatch.md#effect-object-and-first-hit)) |
| 125 | 3 | `0x44910C` | 0x68 | `0x4EB990` → `0x538D28` with 0xB |
| 128 | 19 | `0x449130` | 0x74 | `0x4CE8C0` → `0x538E48` with 0xC000, 0x22 and an RNG draw |
| 139 | 8 | `0x44947E` | 0x78 | `0x4CFE60` → `0x5388A8` with 0x25, 0x32, 0x120 (`0x4498C3` tail) |

Records by selector: creature 71, type 3 57, type 16 77, mover 13,
selector 192 one. The on-screen look of each effect class is
**UNCONFIRMED**. Settle it in a running game: trigger the event that
runs a stored action (for action 59, `GRULO.WSX+0xCC4330`), break
after the constructor in its arm and capture the frame.

### Opcode 0x1C fields

**CONFIRMED.** After building the object at the target position
(height raised by the target's slot +0x100 value << 16), the arm
calls these setters on it (`0x4483B3–0x4484AD`):

| Command bytes | Setter | Object fields |
|---|---|---|
| +0x18, +0x19, +0x1A, +0x1B, each `<< 8` through `0x41F6C0` | `0x4B2C10` | Floats at +0x80 onward, scaled by `[0x53FE10]` |
| u16 +0xC, +0xE, +0x10 | `0x4B2DE0` | Cumulative phase times +0xC8–+0xE4 |
| +0x1C, +0x1D | `0x4B2D80` | +0x88, +0x8C |
| s8 +0x1E, +0x1F, +0x20 | `0x4B2BB0` | +0x90 onward |
| u16 +4 bits 0 and 1 | `0x4B2D10` | +0x6C, +0x70 |
| u16 +8 | `0x4B2D60` | +0xAC |
| u16 +6 | `0x4B2E60` | +0x62, and the 16-byte entry of the definition's resource table (definition +0x14, count +0x2E) |
| u16 +0xA | `0x4B2D70` | +0xB0 |
| u16 +0x12 | `0x4B2B60` | +0xEC |
| +0x14, +0x15, +0x16 | `0x4B2DB0` | +0xC4, +0xD0, +0xDC |
| +0x17 | `0x4B2D30` | +0x74 |

A nonzero u16 +0xA skips the readiness test `0x445E80`
(`0x448335–0x448345`). Opcode 0x0F action 139's neighbouring arm
builds the same class (`0x4494A9–0x4494C2`).

### Opcode 0xC4 flags

**CONFIRMED.** The command stays in map queue `0x589760` and is
called again each frame with the first-call flag clear. Byte +6:

| Bit | Records with it set | Meaning (`0x4E5F2B–0x4E6313`) |
|---|---:|---|
| 0 | 46 | Ceiling height +0x1A and busy bit 0x80 in region +0x24; clear selects floor +0x18 and busy bit 0x40. A first call on a busy half is treated as a later frame. |
| 3 | 88 | u16 +4 is the change; clear makes +4 an absolute height and stores the difference in +0xA. |
| 2 | 13 | With bit 3, a finished move reverses: +4 is negated and +0xA reloaded (ping-pong, `0x4E5F6F–0x4E5F9F`). Without bit 3 it has no effect here. |
| 5, 6 | 8, 73 | Also move further rows linked through region bytes +0x34–+0x37 (`0x4E6207–0x4E6308`). |

Remaining distance lives in +0xA and the 8.8 step accumulator in
+8. A nonzero speed byte +7 gives a step of +7 × 10 / 4 × frame
time / 60 (`0x4E610B–0x4E6152`); zero (2 records) moves the whole
distance at once. `0x4E5600` can refuse a step. Each step calls
`0x4A6750` on the row before adding to the height. Starting a move
sets the busy bit and sends region events (`0x4AC4A0`: 2 or 3 and
then 0xD for a ceiling, 0 or 1 and then 0xC for a floor, by
direction); finishing clears it, sends 0x11 (ceiling) or 0x10
(floor) and removes the queued command (`0x4E5FB6–0x4E604B`).
Observed flag values: 0 (258), 1 (29), 4 (5), 8 (71), 9 (9),
0x21 (8), 0x40 (65), 0x4C (8). In game state 6, region 0x1D20 and
the `-PATCH_TEST` option print a developer diagnostic instead
(`0x4E5ED9–0x4E5F28`).

## Array commands

**CONFIRMED.** The level array pointer at `0x5D54BC` is
initialized and read at `0x440A20–0x440A63`, and released
at `0x43F4D6–0x43F4ED`. The shared array at `0x5D54C0`
is read at `0x440A70–0x440AB6` and saved by global
selector 1 (`0x43817D–0x4381A3`). Each arm uses u8
command +4 as the index.

| Opcode | Array | Operation and native evidence |
|---|---|---|
| 0xC6 | Level | Store u8 +5 at `0x4E5BD8–0x4E5BDE`. |
| 0xC7 | Shared | Store u8 +5 at `0x4E5C38–0x4E5C3E`. |
| 0xC8 / 0xC9 | Shared / level | Store the low byte of `0x44AA40(0, (u8(+5) << 5) + 31) >> 5` (a thiscall with ecx = `0x55D3D0`, `0x4E5C95` / `0x4E5CD5`) at `0x4E5C9A–0x4E5CBF` / `0x4E5CDA–0x4E5CFA`. |
| 0xCE | Shared | Add s8 +5 and clamp to 0–255 at `0x4E5C58–0x4E5C77`. |
| 0xCF | Level | Add s8 +5 and clamp to 0–255 at `0x4E5BF8–0x4E5C17`. |

**CONFIRMED.** Opcode 0xCC with s16 +4 = −1 addresses the
56-byte region row selected by u16 +2 and calls `0x4A75F0` with
u16 +6 (`0x4E63C0–0x4E63E9`). Value −2 in the same operand
writes the low byte of +6 to region byte +0x22
(`0x4E63F6–0x4E641D`). Other values write u16 +6 to
the selected 8-byte auxiliary row and set its +5 bit 0x40
(`0x4E6423–0x4E643F`).

## What the group index addresses

**CONFIRMED.** A flat walk consumes all 431,495 bytes at the
MAP +0x44/+0x8C ranges. The sets of record starts exactly equal
the sets of u32 offsets at MAP +0x4C/+0x98 in all 18 files.
The 54,966 index entries address 54,940 starts. HWHIT has 15
repeated offsets and MLOW2 has 11. The other 16 have one index
entry per framed record. There are 12,306 0xF0 group headers
and 33 observed opcodes including that header. This describes
the archive bytes. Which entry starts an execution depends on
the event caller at `0x4A8290–0x4A82A6`.

**CONFIRMED.** At entry to `0x4E5880`, 0xF0 takes byte +4 as
the number of following size-decoded records. An initial 0x1B
takes byte +9 as the remaining count. When reached during a
group, 0x1B receives the current count and a runtime dword
before dispatch (`0x4E58B8–0x4E58C3`,
`0x4E58DB–0x4E58EE`). All 1,654 stored 0x1B records have
+9 zero across the 18 MAP ranges. The object arm can resume
a queued 0x1B with a call back to the group runner at `0x4499E1`.

**CONFIRMED.** Fourteen MLOW2 headers have another 0xF0 within
the range described by their command count. For instance
`MLOW2.WSX+0x14D0E89` has count 3 and the third record at
+0x14D0E9B is another header of count 3. As an inner record,
0xF0 is routed to the high queue and its ordinary high switch
takes the range return (`0x4E58F4–0x4E592F`,
`0x4E59A7–0x4E59B0`). A parser can preserve the raw
boundaries. **CONFIRMED.** They are not a recursive tree. The 14
headers form seven chains A → B → C, where B is A's last counted
record and C is B's first record. In the example chain (MLOW2
indices 1766, 1769, 1770) the object-event pool references A and C
once each and B never. The other six chains differ: only B is
referenced in 1883/1887/1888, 1905/1909/1910 and 1934/1938/1939;
B and C in 1956/1959/1960 and 1976/1979/1980; only A in
2153/2157/2158. A run of A sends B to queue `0x589760`. The high
switch returns 0 for 0xF0 (`0x4E59A7–0x4E59B0`, `0x4E5A77`), so B's
records do not run as part of A, and the entry is not passed to
`0x4F0860`, which receives completed entries (`0x4E5934–0x4E593E`).
A B that has its own event runs as an ordinary group, and its first
record C is then skipped the same way. A C runs only from its own
event; the C of 1883, 1905, 1934 and 2153 has none.

Run `python3 tools/lol3_script_framing.py --data DAT --check` on
the English retail files. The tool reads the size table directly
from the supplied executable and reports aggregate counts.

**CONFIRMED.** The indirect object commands are resolved per class
in [per-class effects](#per-class-effects-of-the-indirect-commands).
Opcode 0x1A checks `[0x600854]` at `0x4482DB`, resolves the pair
+8/+0xC through `0x41EDE0` (`0x4482F0–0x4482F8`) and calls
`0x48EBE0` on the global object `0x5860F0` (the second saved
position group of the [save page](lol3-native-saves.md)) with +4,
+0x10, the resolved object and pointers +0x14/+0x1D
(`0x448300–0x448316`). There +4 (0–0x11) selects an arm through
`0x48F0D4`; the common tail passes mode +0x7C to `0x48F720` and
stores the last argument at +0x4C (`0x48EC08–0x48EC48`).
**CONFIRMED.** The object at `0x5860F0` is a second player-side
actor. The hit resolver treats it like the player on both sides: on
difficulty `[0x5D57BC]` 0 a hit on the player or on it is divided by 3,
a hit by the player or by it is doubled, and a hit by it is doubled
again when `0x48FE40` on it returns nonzero (`0x4E23D8–0x4E245C`). A hit
on the player by another actor is reported to it through `0x489700`
(`0x4E228C–0x4E22AE`), and saves keep its position next to the
player's (`0x43766F–0x43776D`).
**UNCONFIRMED.** Who this actor is on screen (a companion is the
likely reading), and the visible look of the type-5 effect classes
built by opcodes 0x0F and 0x1C. Settle the actor in a running game:
break at `0x48EBE0` when an opcode-0x1A record such as
`BUPP1.WSX+0x18C7FD3` runs, and watch which character performs
action +4.
