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

**UNCONFIRMED.** The exact per-item effects when a player activates
a slot remain open. The input binding and definition-time switch
are now located. Follow reads of the dwords at `0x5D4D58–0x5D4D7C`
to the item-use button event. Match the selected inventory instance
to its definition and resolve the virtual method or switch invoked
there. The object-script opcode-3 vtable +0xC0 call is an additional
candidate at `0x448025`.
