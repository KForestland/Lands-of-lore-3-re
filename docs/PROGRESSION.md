# Progression

Made by `tools/lol3_progression.py` from the portal commands in the 18 MAP scripts ([level sheets](levels/README.md)). One row is one opcode-2 command whose byte +4 is 27 or 76. **CONFIRMED.** The player handler `0x410AA0` jumps through the table at `0x4117D4` by byte +4 (`0x410B63–0x410B7D`, bound 0x51); entries 27 and 76, and no others, are `0x410F98` ([opcode 0x02](lol3-script-opcodes.md#portal-subcommands-of-opcode-0x02)). That arm stores `(byte +5 & 31) + 2` at `[0x5D5370]` and `(byte +5 >> 5)`, plus 8 when the subcommand is 76, at `[0x5D5374]` (`0x410F98–0x410FC3`). When byte `[0x5D5380]` is nonzero it stores nothing and returns (`0x410FB0–0x410FB8`). After the command group, `0x4E596A–0x4E598A` copies those dwords to `[0x5D5368]` and `[0x5D536C]` and clears them; the object queue has a second copy of the same code at `0x447C86–0x447CA8`. `0x46CC2B` passes them to `0x46CCB0`, which passes them to `0x436890`. The first is the level index: `0x43D7B0` stores it at context +0x76B and reads the name from the 27-byte record at `0x548938`. The second is forwarded to `0x43D7B0`, and that function does not read it. Row 0's pointer is not a string in the program, and row 20 is zeros. Row 1 is `aglob`. Rows 2–19 are the 18 level stems in table order, the same names as the path list. A startup with no saved index stores the immediate `0x11` (row 17, `qwod0`). No portal command selects row 1 or row 17. Every portal command has selector 1 and index 0.

The Event column is the one object or region record that names the command, or the group header that contains it, with every byte its matcher compares. Group is that record's command offset; Command is the portal opcode's own offset. Guard is the record's kind-19 predicate, a 5-byte row at MAP +0xBC ([predicates](lol3-script-events.md#predicates-and-global-bytes)); `none` means no predicate trailer. `shared N` is byte N of `[0x5D54C0]`. A type-4 operand is another row of the same table. `object+0x31` is the byte at `[0x600850]+0x31`. Each of these guards is a row below 5000, so none is an item or equipment test. Slot numbers are table indexes, not names.

**CONFIRMED.** A walker runs only the first row of its list that matches and whose guard passes, then returns: region kind 12 `0x4AC2F3` → `0x4AC450–0x4AC46E`, object kind 5 `0x4A830A` → `0x4A832E–0x4A8351`. The kind 11, kind 6 and kind 22 walkers end the same way (`0x4AC515`, `0x4A87CD`, `0x4A88B3`, `0x4A8E25`). Earlier lists the rows before this one in the same list that the walker can take first for an input this row accepts: the same region and event byte (or a kind-12 row with event 6, which matches input 2 for any region, `0x4AC2FB`), the same kind-5 event byte with an equal value or 0xFF on either side, the same kind-6 event byte (for event 20, an equal value or 0 on either side, `0x4A888F–0x4A88A6`), or the same kind-22 name. Each is shown as its group offset and guard. Taken when combines this row's guard with NOT each earlier guard; when they read one byte it is written as the values of that byte that take this row.

**UNCONFIRMED.** A row with no guard and no earlier row (Taken when `upstream`) runs whenever its event arrives, so its gate is whatever sends that event (another script command or the program), which is not traced here. Settle it in a running game with a write breakpoint on `0x410FC3` (the store to `[0x5D5370]`) and the caller chain at the hit, and statically by finding the callers of the walker for that kind with that event byte.

Locked doors are not covered by this page: a door inside a level is object state and its own records, not a portal command, and no portal guard here tests an item key (5000+n) or an equipped item (6000+n). First-visit selectors: 0 pairs of rows from one level to the same destination test one byte with == 0 and == 1.

131 portal commands, 82 with a predicate. 49 rows have an earlier row the walker tries first; 46 rows have no guard and no earlier row (gate upstream). Subcommand 27 on 125, subcommand 76 on 6. Shared slots named in the guards: 9 (81), 10 (2), 14 (2). object+0x31 named in the guards: 7. Levels with no portal command: SWOD4.

| From | To | Sub | Arg2 | Stream | Group | Command | Event | Guard | Earlier | Taken when |
|---|---|---:|---:|---|---:|---:|---|---|---|---|
| <a name="level-bupp1"></a>[BUPP1](levels/BUPP1.md) | CKEEP | 27 | 1 | object | 518 | 530 | kind 6 event 25 value 0 | none | — | upstream: no guard here |
| BUPP1 | CKEEP | 27 | 1 | object | 536 | 542 | kind 6 event 20 value 0 | (object+0x31 == 1) | 455 (object+0x31 == 0) | object+0x31 = 1 |
| BUPP1 | DLOW1 | 27 | 1 | object | 1930 | 1936 | kind 6 event 20 value 1 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| BUPP1 | DLOW1 | 27 | 1 | region | 3338 | 3350 | region 7505 kind 12 event 2 cond 0 | (shared 14 > 0) | — | shared 14 ≥ 1 |
| BUPP1 | DLOW1 | 27 | 1 | region | 3356 | 3374 | region 7505 kind 12 event 2 cond 0 | none | 3338 (shared 14 > 0) | shared 14 = 0 |
| BUPP1 | DLOW1 | 27 | 1 | region | 3380 | 3392 | region 7506 kind 12 event 2 cond 0 | (shared 14 > 0) | — | shared 14 ≥ 1 |
| BUPP1 | DLOW1 | 27 | 1 | region | 3398 | 3416 | region 7506 kind 12 event 2 cond 0 | none | 3380 (shared 14 > 0) | shared 14 = 0 |
| BUPP1 | DLOW1 | 27 | 1 | region | 4582 | 4582 | region 10437 kind 11 event 0 | none | — | upstream: no guard here |
| BUPP1 | DLOW1 | 27 | 1 | region | 4588 | 4588 | region 10438 kind 11 event 0 | none | — | upstream: no guard here |
| BUPP1 | DLOW1 | 27 | 1 | region | 4594 | 4594 | region 10439 kind 11 event 0 | none | — | upstream: no guard here |
| BUPP1 | DLOW1 | 27 | 2 | region | 2092 | 2098 | region 5328 kind 12 event 2 cond 0 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| BUPP1 | DLOW1 | 27 | 2 | region | 2116 | 2122 | region 5329 kind 12 event 2 cond 0 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| BUPP1 | DLOW1 | 27 | 2 | region | 2140 | 2146 | region 5330 kind 12 event 2 cond 0 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| BUPP1 | DLOW1 | 27 | 2 | region | 2164 | 2170 | region 5331 kind 12 event 2 cond 0 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| BUPP1 | DLOW1 | 27 | 2 | region | 2188 | 2194 | region 5332 kind 12 event 2 cond 0 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| BUPP1 | DLOW1 | 27 | 2 | region | 4374 | 4380 | region 10133 kind 12 event 2 cond 0 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| BUPP1 | DLOW1 | 27 | 2 | region | 4398 | 4404 | region 10134 kind 12 event 2 cond 0 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| BUPP1 | EWOD1 | 27 | 5 | object | 8128 | 8134 | kind 6 event 20 value 1 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| BUPP1 | MLOW2 | 27 | 1 | object | 1942 | 1948 | kind 6 event 20 value 1 | (shared 9 > 1) | 1930 (shared 9 < 2) | shared 9 ≥ 2 |
| BUPP1 | MLOW2 | 27 | 2 | region | 2104 | 2110 | region 5328 kind 12 event 2 cond 0 | (shared 9 > 1) | 2092 (shared 9 < 2) | shared 9 ≥ 2 |
| BUPP1 | MLOW2 | 27 | 2 | region | 2128 | 2134 | region 5329 kind 12 event 2 cond 0 | (shared 9 > 1) | 2116 (shared 9 < 2) | shared 9 ≥ 2 |
| BUPP1 | MLOW2 | 27 | 2 | region | 2152 | 2158 | region 5330 kind 12 event 2 cond 0 | (shared 9 > 1) | 2140 (shared 9 < 2) | shared 9 ≥ 2 |
| BUPP1 | MLOW2 | 27 | 2 | region | 2176 | 2182 | region 5331 kind 12 event 2 cond 0 | (shared 9 > 1) | 2164 (shared 9 < 2) | shared 9 ≥ 2 |
| BUPP1 | MLOW2 | 27 | 2 | region | 2200 | 2206 | region 5332 kind 12 event 2 cond 0 | (shared 9 > 1) | 2188 (shared 9 < 2) | shared 9 ≥ 2 |
| BUPP1 | MLOW2 | 27 | 2 | region | 4386 | 4392 | region 10133 kind 12 event 2 cond 0 | (shared 9 > 1) | 4374 (shared 9 < 2) | shared 9 ≥ 2 |
| BUPP1 | MLOW2 | 27 | 2 | region | 4410 | 4416 | region 10134 kind 12 event 2 cond 0 | (shared 9 > 1) | 4398 (shared 9 < 2) | shared 9 ≥ 2 |
| BUPP1 | NWOD2 | 27 | 5 | object | 8140 | 8146 | kind 6 event 20 value 1 | (shared 9 > 1) | 8128 (shared 9 < 2) | shared 9 ≥ 2 |
| <a name="level-ckeep"></a>[CKEEP](levels/CKEEP.md) | BUPP1 | 27 | 1 | object | 6976 | 6994 | kind 6 event 15 value 0 | none | — | upstream: no guard here |
| <a name="level-dlow1"></a>[DLOW1](levels/DLOW1.md) | BUPP1 | 27 | 3 | region | 1810 | 1816 | region 5134 kind 12 event 2 cond 0 | none | — | upstream: no guard here |
| DLOW1 | BUPP1 | 27 | 3 | region | 1822 | 1828 | region 5135 kind 12 event 2 cond 0 | none | — | upstream: no guard here |
| DLOW1 | BUPP1 | 27 | 4 | object | 24180 | 24186 | kind 5 event 1 value 0 | (object+0x31 == 1) | — | object+0x31 = 1 |
| DLOW1 | EWOD1 | 27 | 4 | object | 5097 | 5103 | kind 6 event 20 value 2 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| DLOW1 | NWOD2 | 27 | 4 | object | 5109 | 5115 | kind 6 event 20 value 2 | (shared 9 > 1) | 5097 (shared 9 < 2) | shared 9 ≥ 2 |
| <a name="level-ewod1"></a>[EWOD1](levels/EWOD1.md) | BUPP1 | 27 | 2 | object | 16172 | 16172 | kind 6 event 15 value 0 | (shared 9 < 4) | — | shared 9 ≤ 3 |
| EWOD1 | DLOW1 | 27 | 3 | object | 16190 | 16190 | kind 6 event 15 value 0 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| EWOD1 | DLOW1 | 27 | 3 | region | 298 | 298 | region 6342 kind 12 event 2 cond 0 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| EWOD1 | FLAIR | 27 | 1 | object | 5173 | 5179 | kind 6 event 20 value 0 | (object+0x31 == 1) | 5104 (object+0x31 == 0) | object+0x31 = 1 |
| EWOD1 | HWHIT | 27 | 1 | object | 6576 | 6594 | kind 5 event 1 value 0 | (object+0x31 == 0) | — | object+0x31 = 0 |
| EWOD1 | KVOLC | 27 | 1 | object | 10540 | 10552 | kind 5 event 1 value 0 | (shared 10 != 0) | 10522 (shared 10 == 0) | shared 10 ≥ 1 |
| EWOD1 | LUPP2 | 27 | 2 | object | 16178 | 16178 | kind 6 event 15 value 0 | (shared 9 > 3) | 16172 (shared 9 < 4) | shared 9 ≥ 4 |
| EWOD1 | MLOW2 | 27 | 3 | object | 16196 | 16196 | kind 6 event 15 value 0 | ((shared 9 > 1) and (shared 9 < 4)) | 16190 (shared 9 < 2) | shared 9 2–3 |
| EWOD1 | MLOW2 | 27 | 3 | region | 304 | 304 | region 6342 kind 12 event 2 cond 0 | ((shared 9 > 1) and (shared 9 < 4)) | 298 (shared 9 < 2) | shared 9 2–3 |
| EWOD1 | OLOW3 | 27 | 3 | object | 16202 | 16202 | kind 6 event 15 value 0 | (shared 9 > 3) | 16190 (shared 9 < 2), 16196 ((shared 9 > 1) and (shared 9 < 4)) | shared 9 ≥ 4 |
| EWOD1 | OLOW3 | 27 | 3 | region | 310 | 310 | region 6342 kind 12 event 2 cond 0 | (shared 9 > 3) | 298 (shared 9 < 2), 304 ((shared 9 > 1) and (shared 9 < 4)) | shared 9 ≥ 4 |
| EWOD1 | RVOL0 | 27 | 1 | object | 10522 | 10534 | kind 5 event 1 value 0 | (shared 10 == 0) | — | shared 10 = 0 |
| <a name="level-flair"></a>[FLAIR](levels/FLAIR.md) | EWOD1 | 27 | 2 | object | 17420 | 17426 | kind 6 event 20 value 1 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| FLAIR | EWOD1 | 27 | 2 | object | 31780 | 31806 | kind 4 mode 0 invert 0 value 0x00000000 | none | — | upstream: no guard here |
| FLAIR | EWOD1 | 27 | 2 | object | 31812 | 31838 | kind 5 event 1 value 0 | none | — | upstream: no guard here |
| FLAIR | EWOD1 | 27 | 3 | region | 3496 | 3502 | region 6701 kind 12 event 2 cond 0 | none | 3448 (shared 9 == 2), 3460 (shared 9 == 3), 3472 (shared 9 == 4), 3484 (shared 9 == 5) | shared 9 ≤ 1 or ≥ 6 |
| FLAIR | NWOD2 | 27 | 2 | object | 17432 | 17438 | kind 6 event 20 value 1 | ((shared 9 > 1) and (shared 9 < 4)) | 17420 (shared 9 < 2) | shared 9 2–3 |
| FLAIR | NWOD2 | 27 | 3 | region | 3448 | 3454 | region 6701 kind 12 event 2 cond 0 | (shared 9 == 2) | — | shared 9 = 2 |
| FLAIR | NWOD2 | 27 | 3 | region | 3460 | 3466 | region 6701 kind 12 event 2 cond 0 | (shared 9 == 3) | 3448 (shared 9 == 2) | shared 9 = 3 |
| FLAIR | PWOD3 | 27 | 2 | object | 17444 | 17450 | kind 6 event 20 value 1 | (shared 9 > 3) | 17420 (shared 9 < 2), 17432 ((shared 9 > 1) and (shared 9 < 4)) | shared 9 ≥ 4 |
| FLAIR | PWOD3 | 27 | 3 | region | 3472 | 3478 | region 6701 kind 12 event 2 cond 0 | (shared 9 == 4) | 3448 (shared 9 == 2), 3460 (shared 9 == 3) | shared 9 = 4 |
| FLAIR | PWOD3 | 27 | 3 | region | 3484 | 3490 | region 6701 kind 12 event 2 cond 0 | (shared 9 == 5) | 3448 (shared 9 == 2), 3460 (shared 9 == 3), 3472 (shared 9 == 4) | shared 9 = 5 |
| FLAIR | <a name="level-swod4"></a>[SWOD4](levels/SWOD4.md) | 27 | 2 | object | 31926 | 31966 | kind 4 mode 3 invert 0 value 0xAD2C35FB | none | — | upstream: no guard here |
| <a name="level-grulo"></a>[GRULO](levels/GRULO.md) | EWOD1 | 27 | 6 | object | 6810 | 6810 | kind 5 event 1 value 0 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| GRULO | FLAIR | 27 | 4 | object | 15856 | 15902 | kind 4 mode 3 invert 0 value 0x3B676D5C | none | — | upstream: no guard here |
| GRULO | NWOD2 | 27 | 6 | object | 6816 | 6816 | kind 5 event 1 value 0 | (shared 9 < 4) | 6810 (shared 9 < 2) | shared 9 2–3 |
| GRULO | PWOD3 | 27 | 6 | object | 6822 | 6822 | kind 5 event 1 value 0 | (shared 9 >= 4) | 6810 (shared 9 < 2), 6816 (shared 9 < 4) | shared 9 ≥ 4 |
| <a name="level-hwhit"></a>[HWHIT](levels/HWHIT.md) | EWOD1 | 76 | 8 | object | 3887 | 3893 | kind 5 event 1 value 0 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| HWHIT | FLAIR | 27 | 4 | object | 8986 | 9032 | kind 4 mode 3 invert 0 value 0x3B676D5C | none | — | upstream: no guard here |
| HWHIT | NWOD2 | 76 | 8 | object | 3899 | 3905 | kind 5 event 1 value 0 | ((shared 9 > 1) and (shared 9 < 4)) | 3887 (shared 9 < 2) | shared 9 2–3 |
| HWHIT | PWOD3 | 76 | 8 | object | 3911 | 3917 | kind 5 event 1 value 0 | (shared 9 > 3) | 3887 (shared 9 < 2), 3899 ((shared 9 > 1) and (shared 9 < 4)) | shared 9 ≥ 4 |
| <a name="level-ishat"></a>[ISHAT](levels/ISHAT.md) | PWOD3 | 76 | 10 | object | 7275 | 7275 | kind 5 event 1 value 0 | none | — | upstream: no guard here |
| <a name="level-jundr"></a>[JUNDR](levels/JUNDR.md) | FLAIR | 27 | 4 | object | 44119 | 44165 | kind 4 mode 3 invert 0 value 0x3B676D5C | none | — | upstream: no guard here |
| JUNDR | NWOD2 | 76 | 9 | object | 14827 | 14827 | kind 6 event 20 value 0 | (shared 9 < 4) | — | shared 9 ≤ 3 |
| JUNDR | PWOD3 | 76 | 9 | object | 14833 | 14833 | kind 6 event 20 value 0 | (shared 9 >= 4) | 14827 (shared 9 < 4) | shared 9 ≥ 4 |
| <a name="level-kvolc"></a>[KVOLC](levels/KVOLC.md) | EWOD1 | 27 | 7 | object | 12153 | 12165 | kind 5 event 1 value 0 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| KVOLC | FLAIR | 27 | 4 | object | 18331 | 18343 | kind 4 mode 3 invert 0 value 0x3B676D5C | none | — | upstream: no guard here |
| KVOLC | NWOD2 | 27 | 7 | object | 12171 | 12183 | kind 5 event 1 value 0 | (shared 9 < 4) | 12153 (shared 9 < 2) | shared 9 2–3 |
| KVOLC | PWOD3 | 27 | 7 | object | 12189 | 12201 | kind 5 event 1 value 0 | (shared 9 >= 4) | 12153 (shared 9 < 2), 12171 (shared 9 < 4) | shared 9 ≥ 4 |
| <a name="level-lupp2"></a>[LUPP2](levels/LUPP2.md) | DLOW1 | 27 | 1 | region | 24 | 24 | region 5228 kind 11 event 0 | none | — | upstream: no guard here |
| LUPP2 | OLOW3 | 27 | 1 | region | 48 | 60 | region 5692 kind 12 event 2 cond 0 | none | — | upstream: no guard here |
| LUPP2 | OLOW3 | 27 | 1 | region | 66 | 78 | region 5701 kind 12 event 2 cond 0 | none | — | upstream: no guard here |
| LUPP2 | OLOW3 | 27 | 1 | region | 84 | 96 | region 5702 kind 12 event 2 cond 0 | none | — | upstream: no guard here |
| LUPP2 | OLOW3 | 27 | 2 | region | 18 | 18 | region 3853 kind 12 event 2 cond 0 | none | — | upstream: no guard here |
| LUPP2 | PWOD3 | 27 | 5 | region | 30 | 42 | region 5687 kind 12 event 2 cond 0 | none | — | upstream: no guard here |
| <a name="level-mlow2"></a>[MLOW2](levels/MLOW2.md) | BUPP1 | 27 | 3 | region | 1172 | 1172 | region 5457 kind 12 event 2 cond 0 | none | — | upstream: no guard here |
| MLOW2 | BUPP1 | 27 | 4 | object | 13208 | 13214 | kind 5 event 1 value 0 | (object+0x31 == 1) | — | object+0x31 = 1 |
| MLOW2 | NWOD2 | 27 | 4 | object | 2762 | 2768 | kind 6 event 20 value 2 | none | — | upstream: no guard here |
| <a name="level-nwod2"></a>[NWOD2](levels/NWOD2.md) | BUPP1 | 27 | 2 | object | 10493 | 10493 | kind 6 event 15 value 0 | (shared 9 < 4) | — | shared 9 ≤ 3 |
| NWOD2 | DLOW1 | 27 | 3 | object | 10511 | 10511 | kind 6 event 15 value 0 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| NWOD2 | DLOW1 | 27 | 3 | region | 256 | 256 | region 6360 kind 12 event 2 cond 0 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| NWOD2 | DLOW1 | 27 | 3 | region | 274 | 274 | region 6361 kind 12 event 2 cond 0 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| NWOD2 | FLAIR | 27 | 1 | region | 368 | 368 | region 9778 kind 12 event 2 cond 0 | none | — | upstream: no guard here |
| NWOD2 | FLAIR | 27 | 1 | region | 374 | 374 | region 9779 kind 12 event 2 cond 0 | none | — | upstream: no guard here |
| NWOD2 | FLAIR | 27 | 1 | region | 380 | 380 | region 9780 kind 12 event 2 cond 0 | none | — | upstream: no guard here |
| NWOD2 | FLAIR | 27 | 1 | region | 386 | 386 | region 9781 kind 12 event 2 cond 0 | none | — | upstream: no guard here |
| NWOD2 | GRULO | 27 | 1 | object | 5073 | 5085 | kind 5 event 1 value 0 | none | — | upstream: no guard here |
| NWOD2 | HWHIT | 27 | 1 | object | 4989 | 5001 | kind 5 event 1 value 0 | none | — | upstream: no guard here |
| NWOD2 | JUNDR | 27 | 1 | object | 5037 | 5049 | kind 5 event 1 value 0 | none | — | upstream: no guard here |
| NWOD2 | KVOLC | 27 | 1 | object | 5013 | 5025 | kind 5 event 1 value 0 | none | — | upstream: no guard here |
| NWOD2 | LUPP2 | 27 | 2 | object | 10499 | 10499 | kind 6 event 15 value 0 | (shared 9 > 3) | 10493 (shared 9 < 4) | shared 9 ≥ 4 |
| NWOD2 | MLOW2 | 27 | 3 | object | 10517 | 10517 | kind 6 event 15 value 0 | ((shared 9 > 1) and (shared 9 < 4)) | 10511 (shared 9 < 2) | shared 9 2–3 |
| NWOD2 | MLOW2 | 27 | 3 | region | 262 | 262 | region 6360 kind 12 event 2 cond 0 | ((shared 9 > 1) and (shared 9 < 4)) | 256 (shared 9 < 2) | shared 9 2–3 |
| NWOD2 | MLOW2 | 27 | 3 | region | 280 | 280 | region 6361 kind 12 event 2 cond 0 | ((shared 9 > 1) and (shared 9 < 4)) | 274 (shared 9 < 2) | shared 9 2–3 |
| NWOD2 | OLOW3 | 27 | 3 | object | 10523 | 10523 | kind 6 event 15 value 0 | (shared 9 > 3) | 10511 (shared 9 < 2), 10517 ((shared 9 > 1) and (shared 9 < 4)) | shared 9 ≥ 4 |
| NWOD2 | OLOW3 | 27 | 3 | region | 268 | 268 | region 6360 kind 12 event 2 cond 0 | (shared 9 > 3) | 256 (shared 9 < 2), 262 ((shared 9 > 1) and (shared 9 < 4)) | shared 9 ≥ 4 |
| NWOD2 | OLOW3 | 27 | 3 | region | 286 | 286 | region 6361 kind 12 event 2 cond 0 | (shared 9 > 3) | 274 (shared 9 < 2), 280 ((shared 9 > 1) and (shared 9 < 4)) | shared 9 ≥ 4 |
| <a name="level-olow3"></a>[OLOW3](levels/OLOW3.md) | LUPP2 | 27 | 3 | region | 1202 | 1202 | region 5435 kind 12 event 2 cond 0 | none | — | upstream: no guard here |
| OLOW3 | LUPP2 | 27 | 3 | region | 1208 | 1208 | region 5436 kind 12 event 2 cond 0 | none | — | upstream: no guard here |
| OLOW3 | LUPP2 | 27 | 4 | object | 11250 | 11256 | kind 5 event 1 value 0 | (object+0x31 == 1) | — | object+0x31 = 1 |
| OLOW3 | PWOD3 | 27 | 4 | object | 2192 | 2198 | kind 6 event 20 value 2 | none | — | upstream: no guard here |
| <a name="level-pwod3"></a>[PWOD3](levels/PWOD3.md) | BUPP1 | 27 | 2 | object | 11602 | 11602 | kind 6 event 15 value 0 | (shared 9 < 4) | — | shared 9 ≤ 3 |
| PWOD3 | DLOW1 | 27 | 3 | object | 11620 | 11620 | kind 6 event 15 value 0 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| PWOD3 | DLOW1 | 27 | 3 | region | 196 | 196 | region 6357 kind 12 event 2 cond 0 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| PWOD3 | DLOW1 | 27 | 3 | region | 214 | 214 | region 6358 kind 12 event 2 cond 0 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| PWOD3 | FLAIR | 27 | 1 | region | 306 | 306 | region 9767 kind 12 event 2 cond 0 | none | — | upstream: no guard here |
| PWOD3 | FLAIR | 27 | 1 | region | 312 | 312 | region 9768 kind 12 event 2 cond 0 | none | — | upstream: no guard here |
| PWOD3 | FLAIR | 27 | 1 | region | 318 | 318 | region 9769 kind 12 event 2 cond 0 | none | — | upstream: no guard here |
| PWOD3 | FLAIR | 27 | 1 | region | 324 | 324 | region 9770 kind 12 event 2 cond 0 | none | — | upstream: no guard here |
| PWOD3 | GRULO | 27 | 1 | object | 4892 | 4904 | kind 5 event 1 value 0 | none | — | upstream: no guard here |
| PWOD3 | HWHIT | 27 | 1 | object | 4838 | 4850 | kind 5 event 1 value 0 | none | — | upstream: no guard here |
| PWOD3 | ISHAT | 27 | 1 | object | 4910 | 4922 | kind 5 event 1 value 0 | none | — | upstream: no guard here |
| PWOD3 | JUNDR | 27 | 1 | object | 4874 | 4886 | kind 5 event 1 value 0 | none | — | upstream: no guard here |
| PWOD3 | KVOLC | 27 | 1 | object | 4856 | 4868 | kind 5 event 1 value 0 | none | — | upstream: no guard here |
| PWOD3 | LUPP2 | 27 | 2 | object | 11608 | 11608 | kind 6 event 15 value 0 | (shared 9 > 3) | 11602 (shared 9 < 4) | shared 9 ≥ 4 |
| PWOD3 | MLOW2 | 27 | 3 | object | 11626 | 11626 | kind 6 event 15 value 0 | ((shared 9 > 1) and (shared 9 < 4)) | 11620 (shared 9 < 2) | shared 9 2–3 |
| PWOD3 | MLOW2 | 27 | 3 | region | 202 | 202 | region 6357 kind 12 event 2 cond 0 | ((shared 9 > 1) and (shared 9 < 4)) | 196 (shared 9 < 2) | shared 9 2–3 |
| PWOD3 | MLOW2 | 27 | 3 | region | 220 | 220 | region 6358 kind 12 event 2 cond 0 | ((shared 9 > 1) and (shared 9 < 4)) | 214 (shared 9 < 2) | shared 9 2–3 |
| PWOD3 | OLOW3 | 27 | 3 | object | 11632 | 11632 | kind 6 event 15 value 0 | (shared 9 > 3) | 11620 (shared 9 < 2), 11626 ((shared 9 > 1) and (shared 9 < 4)) | shared 9 ≥ 4 |
| PWOD3 | OLOW3 | 27 | 3 | region | 208 | 208 | region 6357 kind 12 event 2 cond 0 | (shared 9 > 3) | 196 (shared 9 < 2), 202 ((shared 9 > 1) and (shared 9 < 4)) | shared 9 ≥ 4 |
| PWOD3 | OLOW3 | 27 | 3 | region | 226 | 226 | region 6358 kind 12 event 2 cond 0 | (shared 9 > 3) | 214 (shared 9 < 2), 220 ((shared 9 > 1) and (shared 9 < 4)) | shared 9 ≥ 4 |
| <a name="level-qwod0"></a>[QWOD0](levels/QWOD0.md) | BUPP1 | 27 | 1 | object | 176 | 194 | kind 6 event 20 value 0 | (object+0x31 == 0) | — | object+0x31 = 0 |
| QWOD0 | BUPP1 | 27 | 1 | object | 230 | 242 | kind 22 name de15a215 | none | — | upstream: no guard here |
| <a name="level-rvol0"></a>[RVOL0](levels/RVOL0.md) | EWOD1 | 27 | 7 | object | 279 | 291 | kind 5 event 1 value 0 | (shared 9 < 2) | — | shared 9 ≤ 1 |
| RVOL0 | FLAIR | 27 | 2 | object | 1475 | 1481 | kind 5 event 1 value 0 | none | — | upstream: no guard here |
| RVOL0 | FLAIR | 27 | 2 | object | 1493 | 1499 | kind 4 mode 9 invert 0 value 0x00000005 | none | — | upstream: no guard here |
| RVOL0 | NWOD2 | 27 | 7 | object | 297 | 309 | kind 5 event 1 value 0 | (shared 9 < 4) | 279 (shared 9 < 2) | shared 9 2–3 |
| RVOL0 | PWOD3 | 27 | 7 | object | 315 | 327 | kind 5 event 1 value 0 | (shared 9 >= 4) | 279 (shared 9 < 2), 297 (shared 9 < 4) | shared 9 ≥ 4 |

## Level to level

One row per pair of levels joined by at least one portal command. Gate lists the distinct Taken when values of those rows. An edge with a row whose gate is upstream says so; that part of its gate is UNCONFIRMED, as above.

| From | To | Rows | Gate |
|---|---|---:|---|
| BUPP1 | CKEEP | 2 | object+0x31 = 1; upstream on 1 of the rows |
| BUPP1 | DLOW1 | 15 | shared 14 = 0; shared 14 ≥ 1; shared 9 ≤ 1; upstream on 3 of the rows |
| BUPP1 | EWOD1 | 1 | shared 9 ≤ 1 |
| BUPP1 | MLOW2 | 8 | shared 9 ≥ 2 |
| BUPP1 | NWOD2 | 1 | shared 9 ≥ 2 |
| CKEEP | BUPP1 | 1 | upstream on 1 of the rows |
| DLOW1 | BUPP1 | 3 | object+0x31 = 1; upstream on 2 of the rows |
| DLOW1 | EWOD1 | 1 | shared 9 ≤ 1 |
| DLOW1 | NWOD2 | 1 | shared 9 ≥ 2 |
| EWOD1 | BUPP1 | 1 | shared 9 ≤ 3 |
| EWOD1 | DLOW1 | 2 | shared 9 ≤ 1 |
| EWOD1 | FLAIR | 1 | object+0x31 = 1 |
| EWOD1 | HWHIT | 1 | object+0x31 = 0 |
| EWOD1 | KVOLC | 1 | shared 10 ≥ 1 |
| EWOD1 | LUPP2 | 1 | shared 9 ≥ 4 |
| EWOD1 | MLOW2 | 2 | shared 9 2–3 |
| EWOD1 | OLOW3 | 2 | shared 9 ≥ 4 |
| EWOD1 | RVOL0 | 1 | shared 10 = 0 |
| FLAIR | EWOD1 | 4 | shared 9 ≤ 1; shared 9 ≤ 1 or ≥ 6; upstream on 2 of the rows |
| FLAIR | NWOD2 | 3 | shared 9 2–3; shared 9 = 2; shared 9 = 3 |
| FLAIR | PWOD3 | 3 | shared 9 = 4; shared 9 = 5; shared 9 ≥ 4 |
| FLAIR | SWOD4 | 1 | upstream on 1 of the rows |
| GRULO | EWOD1 | 1 | shared 9 ≤ 1 |
| GRULO | FLAIR | 1 | upstream on 1 of the rows |
| GRULO | NWOD2 | 1 | shared 9 2–3 |
| GRULO | PWOD3 | 1 | shared 9 ≥ 4 |
| HWHIT | EWOD1 | 1 | shared 9 ≤ 1 |
| HWHIT | FLAIR | 1 | upstream on 1 of the rows |
| HWHIT | NWOD2 | 1 | shared 9 2–3 |
| HWHIT | PWOD3 | 1 | shared 9 ≥ 4 |
| ISHAT | PWOD3 | 1 | upstream on 1 of the rows |
| JUNDR | FLAIR | 1 | upstream on 1 of the rows |
| JUNDR | NWOD2 | 1 | shared 9 ≤ 3 |
| JUNDR | PWOD3 | 1 | shared 9 ≥ 4 |
| KVOLC | EWOD1 | 1 | shared 9 ≤ 1 |
| KVOLC | FLAIR | 1 | upstream on 1 of the rows |
| KVOLC | NWOD2 | 1 | shared 9 2–3 |
| KVOLC | PWOD3 | 1 | shared 9 ≥ 4 |
| LUPP2 | DLOW1 | 1 | upstream on 1 of the rows |
| LUPP2 | OLOW3 | 4 | upstream on 4 of the rows |
| LUPP2 | PWOD3 | 1 | upstream on 1 of the rows |
| MLOW2 | BUPP1 | 2 | object+0x31 = 1; upstream on 1 of the rows |
| MLOW2 | NWOD2 | 1 | upstream on 1 of the rows |
| NWOD2 | BUPP1 | 1 | shared 9 ≤ 3 |
| NWOD2 | DLOW1 | 3 | shared 9 ≤ 1 |
| NWOD2 | FLAIR | 4 | upstream on 4 of the rows |
| NWOD2 | GRULO | 1 | upstream on 1 of the rows |
| NWOD2 | HWHIT | 1 | upstream on 1 of the rows |
| NWOD2 | JUNDR | 1 | upstream on 1 of the rows |
| NWOD2 | KVOLC | 1 | upstream on 1 of the rows |
| NWOD2 | LUPP2 | 1 | shared 9 ≥ 4 |
| NWOD2 | MLOW2 | 3 | shared 9 2–3 |
| NWOD2 | OLOW3 | 3 | shared 9 ≥ 4 |
| OLOW3 | LUPP2 | 3 | object+0x31 = 1; upstream on 2 of the rows |
| OLOW3 | PWOD3 | 1 | upstream on 1 of the rows |
| PWOD3 | BUPP1 | 1 | shared 9 ≤ 3 |
| PWOD3 | DLOW1 | 3 | shared 9 ≤ 1 |
| PWOD3 | FLAIR | 4 | upstream on 4 of the rows |
| PWOD3 | GRULO | 1 | upstream on 1 of the rows |
| PWOD3 | HWHIT | 1 | upstream on 1 of the rows |
| PWOD3 | ISHAT | 1 | upstream on 1 of the rows |
| PWOD3 | JUNDR | 1 | upstream on 1 of the rows |
| PWOD3 | KVOLC | 1 | upstream on 1 of the rows |
| PWOD3 | LUPP2 | 1 | shared 9 ≥ 4 |
| PWOD3 | MLOW2 | 3 | shared 9 2–3 |
| PWOD3 | OLOW3 | 3 | shared 9 ≥ 4 |
| QWOD0 | BUPP1 | 2 | object+0x31 = 0; upstream on 1 of the rows |
| RVOL0 | EWOD1 | 1 | shared 9 ≤ 1 |
| RVOL0 | FLAIR | 2 | upstream on 2 of the rows |
| RVOL0 | NWOD2 | 1 | shared 9 2–3 |
| RVOL0 | PWOD3 | 1 | shared 9 ≥ 4 |

Steps from QWOD0, the level a startup with no saved index loads, along portal commands. All edges: every portal edge, whatever its gate. Guarded edges only: edges with at least one row whose gate is read here, not upstream. A step count says only that a chain of portal commands exists; whether their gates can all pass in one game is UNCONFIRMED (settle it by following the shared bytes the gates read through the commands that write them, opcodes 0xC7 and 0xCE).

| Level | Exits to | Entered from | Steps (all edges) | Steps (guarded edges only) |
|---|---|---|---:|---:|
| BUPP1 | CKEEP, DLOW1, EWOD1, MLOW2, NWOD2 | CKEEP, DLOW1, EWOD1, MLOW2, NWOD2, PWOD3, QWOD0 | 1 | 1 |
| CKEEP | BUPP1 | BUPP1 | 2 | 2 |
| DLOW1 | BUPP1, EWOD1, NWOD2 | BUPP1, EWOD1, LUPP2, NWOD2, PWOD3 | 2 | 2 |
| EWOD1 | BUPP1, DLOW1, FLAIR, HWHIT, KVOLC, LUPP2, MLOW2, OLOW3, RVOL0 | BUPP1, DLOW1, FLAIR, GRULO, HWHIT, KVOLC, RVOL0 | 2 | 2 |
| FLAIR | EWOD1, NWOD2, PWOD3, SWOD4 | EWOD1, GRULO, HWHIT, JUNDR, KVOLC, NWOD2, PWOD3, RVOL0 | 3 | 3 |
| GRULO | EWOD1, FLAIR, NWOD2, PWOD3 | NWOD2, PWOD3 | 3 | — |
| HWHIT | EWOD1, FLAIR, NWOD2, PWOD3 | EWOD1, NWOD2, PWOD3 | 3 | 3 |
| ISHAT | PWOD3 | PWOD3 | 5 | — |
| JUNDR | FLAIR, NWOD2, PWOD3 | NWOD2, PWOD3 | 3 | — |
| KVOLC | EWOD1, FLAIR, NWOD2, PWOD3 | EWOD1, NWOD2, PWOD3 | 3 | 3 |
| LUPP2 | DLOW1, OLOW3, PWOD3 | EWOD1, NWOD2, OLOW3, PWOD3 | 3 | 3 |
| MLOW2 | BUPP1, NWOD2 | BUPP1, EWOD1, NWOD2, PWOD3 | 2 | 2 |
| NWOD2 | BUPP1, DLOW1, FLAIR, GRULO, HWHIT, JUNDR, KVOLC, LUPP2, MLOW2, OLOW3 | BUPP1, DLOW1, FLAIR, GRULO, HWHIT, JUNDR, KVOLC, MLOW2, RVOL0 | 2 | 2 |
| OLOW3 | LUPP2, PWOD3 | EWOD1, LUPP2, NWOD2, PWOD3 | 3 | 3 |
| PWOD3 | BUPP1, DLOW1, FLAIR, GRULO, HWHIT, ISHAT, JUNDR, KVOLC, LUPP2, MLOW2, OLOW3 | FLAIR, GRULO, HWHIT, ISHAT, JUNDR, KVOLC, LUPP2, OLOW3, RVOL0 | 4 | 4 |
| QWOD0 | BUPP1 | none | 0 | 0 |
| RVOL0 | EWOD1, FLAIR, NWOD2, PWOD3 | EWOD1 | 3 | 3 |
| SWOD4 | none | FLAIR | 4 | — |

18 of 18 levels are reached from QWOD0 along all edges, 14 along guarded edges only.
