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

**UNCONFIRMED.** Spell targeting, cost, duration, and final effect
dispatch are still unbound. The named binding slots delimit the
input search. Follow consumers of the ten key dwords beginning
at VA `0x5D4D90`, then compare a fixed spell slot's selection to
the `spell.odf` descriptor and active object class. A switch or
virtual call reached from that consumer would settle the cast path.
