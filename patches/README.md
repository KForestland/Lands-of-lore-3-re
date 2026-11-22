# Patches

Small checked edits for a reader's own copy of the original game. A patch records the replacement bytes and a hash of the span it replaces. A patch must not remove or bypass a disc check, a serial check or any other copy protection, and none here does. The format and its limits are on the [patch format page](../docs/formats/patch.md). This folder has the list. It does not hold a patch file: the remaining reports are not a few proven bytes.

The format is `lol-patch-3`. Each change lists its file, entry, offset, old span length and SHA-256, and new bytes. Keep `undo.json` private. It holds original game bytes from your copy.

How to start the game on a current machine is [Running](RUNNING.md).

The English GOG release checked here stores `Win95/NT 1.07a` at `LOL3.DAT+0x14DEAC` and `May  7 1999` at `+0x14DE74`. The version string matches Westwood's 1.07a update notes. Those notes cover display and driver crashes, cache rebuilding and several quest fixes. The version string alone does not verify each fix.

## Where each reported fault sits

**A — no record found that would restore a path.**

**B — failing state still needed.** The check found related code or data. A few-byte patch has not been located yet. A save at the failure, with the action that leads to it, would let us check which step goes wrong.

- **B.** Rescuing Sioned. She fails to return to the guild after Copper frees her.
- **A.** Orcish Retribution. Acknowledgement and reward are separate. Leina's reward path requires the King's Pardon.
- **B.** Perfumed Scarf. Copper cannot start the scarf exchange with Solan.
- **B.** Left sewer grate. The grate stays closed with sufficient lockpicking reported.
- **B.** Draracle wall. Near the wall Copper is pulled in. Bolle reports backing away in steps.
- **A.** Rhynn. His later greeting does not check whether Copper met him at the library.
- **B.** Blue Deer inn room. The rent request never comes and the room stays locked.
- **B.** Blue Gem. The gem becomes unavailable after other gems are taken or the mutant chickens are killed.
- **B.** Victoria's shop. Copper can pick up goods on a later visit but cannot complete the purchase.
- **A.** Scavenger eyes. The shipped item handler performs no throw despite the journal instructions.
- **B.** Volcano elevator. After removing the statue, Copper is left below when the platform rises.
- **B.** Solved quests in the journal. Some entries remain visible after completion.
- **B.** Five herbs. The herb quest is crossed out and the next quest fails to arrive.
- **B.** Rix's Plasma Staff. The unequipped staff disappears from the pack.

Bolle also reports that entering the woods can ask for another disc. His workaround is to return to a save already in the woods. That report concerns the program's disc check and is outside the script and data checks below.

### Retail script and data checks

The checks below use English GOG release (1.07a). Quest and dialogue IDs come from the original TRR directory. Placement event lists and their guards are traced through the native matcher. The stuck states are from the reports. The original maps establish the gates and actions listed here. [Dialogue lookup](../docs/lol3-dialogue-dispatch.md) · [Event matcher](../docs/lol3-script-events.md) · [Community reports](https://lands-of-lore.fandom.com/wiki/Bugs) · [Bolle's reports, section XI](https://gamefaqs.gamespot.com/pc/197755-lands-of-lore-iii/faqs/2527)

#### Rescuing Sioned

[You can help: open your save in the program and send us the report](https://github.com/KForestland/Lands-of-lore-3-re/issues/new?template=bug_report.md).

Copper frees Sioned in Ruloi World and returns to the guild without getting the return scene. In `GRULO.WSX`, object 239's value-20 event at `+0xCC8C36` checks off quest 36 and starts a sequence on creature 75. At the guild, `BUPP1.WSX+0x18E764E` requires shared byte 8 equal to 6 to set up Dawn, creature 26. Her event at `+0x18E7730` starts the report-back exchange, and its last group writes shared byte 8 to 7 at `+0x18D3184`. The journal write in GRULO and the Dawn scene are separate steps. **Patch not located yet.** The reported state has no event or save trace identifying which step failed. Check the rescue sequence, shared byte 8 and Dawn's event on the first return.

#### Orcish Retribution

Copper can hear Leina acknowledge the defeated orcs and still leave without Backbiter. The acknowledgement at `MLOW2.WSX+0x14DA083` requires creature 87's state to be 8 and leads to dialogue 3612. That exchange stops. Leina has a separate mode-3 request at `+0x14DA0AB` that requires the King's Pardon (identity `0x5ABDFC25`). NWOD2 has a placement bearing that identity. Giving her the item starts dialogue 3613. The completion of the last Pardon line at `+0x14DA0D1` runs the shipped Backbiter grant at `+0x14D26F1`. **No few-byte patch found in these records.** The acknowledgement alone does not enter the grant branch. The report does not show the Pardon was offered or that its grant failed afterward. Removing the item requirement would change the quest.

#### Perfumed Scarf

[You can help: open your save in the program and send us the report](https://github.com/KForestland/Lands-of-lore-3-re/issues/new?template=bug_report.md).

The reported failure is reaching the Solan and Mauri sequence without being able to start the scarf exchange. DLOW1 creature 100 has two mode-9 requests with operand 27. Starting from stored level byte 6 equal to 0, the request at `+0x154EB06` writes 1. The earlier guarded request at `+0x154EAF8` writes 2 when the byte is 1. The native matcher keeps the first admitted mode-9/10 row, with mode 1 taking priority if it matches. A separate request at `+0x154EB8C` needs byte 6 equal to 2 to play dialogue 2475. Offering the scarf itself uses mode 3, compares identity `0x87EFED07` at `+0x154EB6C` and sets shared byte 17 to 1 at `+0x1544880`. The item definition is present. Its identity appears once in the 18 MAPs, in this request. **Patch not located yet.** A first acquisition path is still missing from the trace. Changing the request would invent an exchange before the player acquires the scarf.

#### Left sewer grate

[You can help: open your save in the program and send us the report](https://github.com/KForestland/Lands-of-lore-3-re/issues/new?template=bug_report.md).

Copper clicks the grate left of Gladstone Keep with sufficient lockpicking reported and it stays shut. Native guards in the range 7000–7399 test a skill flag and whether the corresponding level exceeds the encoded threshold at `0x4F0540–0x4F05CE`. A placement needs an event and guard tied to this particular click before those checks can explain the fault. The CKEEP and adjacent city MAP event lists and editor notes give no unique left-grate match from the report. **Patch not located yet.** A position, facing and failed request would identify whether the gate has a script threshold or uses the native lock path.

#### Draracle wall

[You can help: open your save in the program and send us the report](https://github.com/KForestland/Lands-of-lore-3-re/issues/new?template=bug_report.md).

Copper moves near a wall in the lower lair and is drawn into it. Bolle reports backing away in steps as a way out. FLAIR has stored surface neighbors, heights and region runs read through `0x4A663C` and `0x4E7934`. There is no square or heading in the report to join to those rows. **Patch not located yet.** A saved position at the wall and the first unintended move would distinguish a surface-neighbor fault from a movement calculation.

#### Rhynn

Copper meets Rhynn by the Talamari library, then meets him in Upper Gladstone and gets the unfamiliar greeting. BUPP1 creature 40's library exchange includes dialogue 674 at `+0x18D5568`. In LUPP2, creature 39's mode-9 request at `+0x1444A47` tests its local state and request operand 5 or 6. The matching group plays dialogue 4240. The request has no kind-19 guard, and the group has no cross-level meeting check. **No few-byte patch found in these records.** A byte edit would need a demonstrated recognition branch for the later encounter. The local request and the library exchange do not point to one.

#### Blue Deer inn room

[You can help: open your save in the program and send us the report](https://github.com/KForestland/Lands-of-lore-3-re/issues/new?template=bug_report.md).

Copper reaches the room with belongings inside, yet the innkeeper makes no rent request and the room stays locked. In DLOW1, controller 285's event at `+0x154BDAA` requires state zero and starts the room conversation. Hearing the rent line continue to its final cue at `+0x154BDFA` sets object 284's state to 1 and sets property 40 on innkeeper 105 with argument 27. The separate confirmation at `+0x154EE7C` uses mode 9 with operand 27 and requires the innkeeper's state to be zero. It checks off quest 12 and sends property 21, argument 2, to controller 286. The paid line in the controller's separate branch sets level byte 4 to 1 at `+0x153F28D`. **Patch not located yet.** The first missing action could be the start of the dialogue or the transition to payment. Compare controller 285, the final cue and the live request on the locked visit.

#### Blue Gem

[You can help: open your save in the program and send us the report](https://github.com/KForestland/Lands-of-lore-3-re/issues/new?template=bug_report.md).

The report describes taking other gems or killing the mutant chickens before claiming the Blue Gem. The placed item 3 at `HWHIT.WSX+0x1125724` has identity `0x38501FA4`. Three opcode-3 records also grant that identity to the player:

| Grant in HWHIT.WSX | Event and conditions |
|---|---|
| `+0x1110007` | Type-3 object 540's mode-9 request at `+0x111A64D` expects state 0, subkind 8 and operand 5 or 6. The grant group then sets property 40 on object 540 at `+0x1110017`. |
| `+0x111059F` | Type-3 object 565 receives kind-5 event 19 at `+0x111A899`. There is no predicate trailer. The group grants a set of items that includes this gem. The sender of event 19 is open. |
| `+0x1110B15` | Type-16 socket 2 has the empty-hand request at `+0x111AB15` with predicate 207 (state 1). At `+0x1110B0F` the group resets the socket to state 0 before returning the gem. Its separate held-item event at `+0x111AB07` matches this identity and tests state 0. |

**Patch not located yet.** The socket can return a gem already inserted, and the multi-item grant needs a different event from the stand-alone grant. The records do not identify which route the report attempted or a write that disables it. Compare the placed item's presence, object 540's state and the socket state before and after the reported sequence.

#### Victoria's shop

[You can help: open your save in the program and send us the report](https://github.com/KForestland/Lands-of-lore-3-re/issues/new?template=bug_report.md).

Copper returns after the second portal and the audience, picks up goods and cannot pay for or leave with them. CKEEP object 24's value-20 event at `+0xD0913C` leads to Victoria's shop-opening dialogue 3328. The transaction conversation on creature 14 has a kind-21 event 5 at `+0xD0A4AC`, followed by the sale line at `+0xD0720A` through a named audio completion. Dialogue 5303 in BUPP1 belongs to the Mage Librarian. **Patch not located yet.** The second visit's shop and currency state at the producer of the CKEEP event is still missing. A dialogue change would leave that admission path alone.

#### Scavenger eyes

Copper has scavenger eyes in the pack and a right-click produces no throw. The shipped definition at `GLOBAL.WSX+0xDB99` has numeric key `0x12E`, identity `0x3B338875`, regular flags `0x40` and handler index 0. The regular dispatcher at `0x49EA08` calls slot zero through the table at `0x54B918`. Its body at `0x49EA40` returns zero and performs no action. The awards at `GRULO.WSX+0xCC475C`, `+0xCC4778` and `+0xCC4794` use this identity. **No few-byte patch.** No shipped throw handler is tied to this definition. Assigning another item's handler would create a use without evidence that it was this item's existing path.

#### Volcano elevator

[You can help: open your save in the program and send us the report](https://github.com/KForestland/Lands-of-lore-3-re/issues/new?template=bug_report.md).

Copper has taken the Heart of Sunrise and removes the statue while below. The platform rises without Copper. `KVOLC.WSX+0x15D137B` requires shared byte 25 equal to 1, sets object 474's state and starts a timer. The writer of that byte at `+0x15CA6CB` is on the Draracle's Sigil request, so this raising annotation alone does not identify the urn. Object 382's two timer expirations at `+0x15D0C2B` and `+0x15D0C3B` drive opposite height changes on region 5858. The mover 27 event at `+0x15D4F19` issues eleven region flag changes. **Patch not located yet.** The urn-removal request and a failed carry test on the rider are still missing. Track the player surface and the platform's moving region together from the instant of removal.

#### Solved quests in the journal

[You can help: open your save in the program and send us the report](https://github.com/KForestland/Lands-of-lore-3-re/issues/new?template=bug_report.md).

The report describes completion with an entry still visible, without identifying which entry or whether it remains active or is crossed out. The retail completion commands for rows 12, 35, 36 and 37 all send argument 5 through `0x434560`. After the quest lookups, `0x4345A9` selects journal category 12 for marker `0x32` and category 5 otherwise. The state setter at `0x434180` admits a nonzero update only when it exceeds the stored state, then calls `0x45AC30` to store it. **Patch not located yet.** Capture one affected row's category, state and rendering after its actual completion event. Removing a row or changing the common setter would also affect completed entries that the journal records correctly.

#### Five herbs

[You can help: open your save in the program and send us the report](https://github.com/KForestland/Lands-of-lore-3-re/issues/new?template=bug_report.md).

Copper's five-herb quest is crossed out, yet the next Cleric quest does not arrive. BUPP1 object 260's event at `+0x18E3EDA` needs its state to be at least 5 and writes quest 35 state 5 and level byte 22 to 1. Boris's separate event at `+0x18E9CA0` tests level byte 22 equal to 1, then sets it to 2, sets Boris's state to 11 and starts the hand-in conversation. The final cue from that conversation reaches `+0x18E9D88` and writes shared byte 6 to 5 at `+0x18D9D2C`. **Patch not located yet.** The crossed-out row alone says nothing about the second chain. Compare level byte 22, Boris's state and shared byte 6 at the failed visit to locate the stall.

#### Rix's Plasma Staff

[You can help: open your save in the program and send us the report](https://github.com/KForestland/Lands-of-lore-3-re/issues/new?template=bug_report.md).

The report describes losing an unequipped staff after taking it from Rix. In the Woods, object 968's value-30 event at `EWOD1.WSX+0x189BDE0` grants staff identity `0xDA2CD58E` to creature 76 at `+0x1894E4E`. The post-Rix familiar event on object 140 at `+0x189A40A` needs state 0 and queues a sequence without a pack operation.

The White Tower has a second grant of the same identity at `HWHIT.WSX+0x11134B1`. Kind-6 value 11 at `+0x111B9CD` belongs to creature 64. Its group also grants that creature three items of identity `0xCE4B4DE6`. This is a grant to a creature in a separate level, with no command in that group to change Copper's pack. Regular handler 36 has the distance and effect allocation path for operations 5 and 6 at `0x4A0F60`. **Patch not located yet.** Neither grant identifies a disappearance from Copper's inventory. Capture the first inventory change after obtaining the staff, including its definition key and instance count.
