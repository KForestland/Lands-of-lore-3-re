# Patches

Small checked edits for a reader's own copy of the original game. A patch records the replacement bytes and a hash of the span it replaces. A patch must not remove or bypass a disc check, a serial check or any other copy protection, and none here does. The format and its limits are on the [patch format page](../docs/formats/patch.md). This folder has the list. It does not hold a patch file: the remaining reports are not a few proven bytes.

The format is `lol-patch-3`. Each change lists its file, entry, offset, old span length and SHA-256, and new bytes. Keep `undo.json` private. It holds original game bytes from your copy.

How to start the game on a current machine is [Running](RUNNING.md).

These pages read English retail 1.07a. The program stores `Win95/NT 1.07a` at `LOL3.DAT+0x14DEAC` and `May  7 1999` at `+0x14DE74`. It does not store a second version string, and it does not store the changelog. Official updates v1.06J (7 May 1999) and v1.07a (9 May 1999) are already in that build. The 1.07a note covers display and driver crashes, a rebuilt cache, several quests that did not start, infinite experience in the Frozen Wastes, a second shard, a Lower Gladstone room that could not be left, the sigil teleport, and a crash on the White Tower case. Those are program and data fixes already shipped by Westwood. They are not repeated here. A search of this `LOL3.DAT` for the report names (Sioned, the scarf, the Draracle, the White Tower, a grate) found none of those words. Nearby bytes that look similar are level and movie stems (`uhfrozen`, `mfrozen`) and the key name `COMMENTS_JOURNAL`, not these reports.

## Where each reported fault sits

One line per report. Script means a quest or scene order. State means a flag, a form, or where the player stands. Program means bytes in the executable or its stub. A few-byte patch is a short edit of those files. A setting and a reload are not that patch. The names below are not stored in `LOL3.DAT`. Quest rows are the language tables (`qevent.trr`, 67 rows). No row has a file offset in the program. No few-byte patch can be marked possible from these notes, so none is attempted. These places were not walked.

- Rescuing Sioned (wiki Bugs). Script: she does not return to the guild after she is freed. The page says there is no known fix. No few-byte patch.
- Orcish Retribution (wiki Bugs). Script: the quest is accepted and the reward item is not given. The page says there is no known fix. No few-byte patch.
- Perfumed Scarf (wiki Bugs). Script: the side quest does not start. The page says there is no known solution. No few-byte patch.
- Sewer grate on the left of Gladstone Keep (wiki Bugs). Script: it stays shut when lockpicking is high enough. No file offset. No few-byte patch.
- A wall in the Draracle's Lair, level 3 (Bolle, GameFAQs 2527, after the patch). State: one place pulls the player in. The note says to step backwards. No file offset. No few-byte patch.
- Rhynn's later meeting (same notes). Script: the meeting in Upper Gladstone ignores the library talk. No few-byte patch.
- Blue Deer inn room (same notes). State: the innkeeper sometimes never asks for payment, so the stored things stay locked. No few-byte patch.
- Blue gem (same notes). State: taking the other gems first, or killing every mutant chicken first, leaves the blue gem untakeable. The note says to take the blue gem first. No few-byte patch.
- A later visit to Victoria's shop (same notes). Script: items can be picked up and payment is not taken. No few-byte patch.
- Scavenger eyes will not throw (same notes). Script: the journal says to throw them and the player does not. No few-byte patch.
- The woods ask for another disc (same notes). Program: entering the woods from Gladstone can ask for another disc and then refuse the woods. The note's remedy is to load a save that is already in the woods. A change that skips a disc check is out of scope. No other few-byte patch is isolated.
- Volcano elevator urn (same notes). Script: taking the statue out sends the platform up and leaves the player below. The notes say to reload from another area, or to leave the quest. No few-byte patch.
- Solved quests stay in the journal (same notes). State. The 1.07a note already claims a fix for quests that are not crossed out, and this report says they still stay. No further byte is isolated.
- No new quest after the five herbs (same notes). Script. No few-byte patch.
- Rix's staff leaves the pack when it is not worn (same notes). State. No few-byte patch.

### Retail script checks

These anchors are for English 1.07a. Quest and dialogue IDs come from the
original TRR directory and the [native lookup](../docs/lol3-dialogue-dispatch.md).
The settling steps distinguish a failure to select an event from a failure
after the event runs.

| Report | Static witness | Settling step |
|---|---|---|
| Sioned | `GRULO.WSX+0xCC1086` submits quest row 36, then starts the sequence at `+0xCC1096`. `BUPP1.WSX+0x1B45DAC` has a rescue annotation for creature 26 in its editor tail. | Compare the rescue sequence and creature 26 on the first return to the guild. |
| Orcish Retribution | `MLOW2.WSX+0x14D2563` uses the dialogue tag for quest 42. `NWOD2.WSX+0x1CD5847` has the editor annotation for the defeated orcs. | Record the final encounter, then the return and item grant with the same inventory room in a working and failing save. |
| Perfumed Scarf | `DLOW1.WSX+0x154EB06` takes request mode 9 with operand 27 and writes level byte 6 to 1. The corresponding event at `+0x154EAF8` takes the same request when the byte is 1 and sets it to 2. The request at `+0x154EB8C` then requires value 2 for dialogue 2475. The stored initial byte is 0 at `+0x159416C`. | Record the two mode-9 dispatches and the following dialogue request from a save at byte 6 equal to 0. |
| Sewer grate | Object request modes and threshold guard families are decoded. Several sewer MAPs have doors and gates. The report gives no event ID or reproducible square that selects one. | Give the area, grate position, thief guild status and skill and the request on the failed click. |
| Draracle wall | `FLAIR` surface and region descriptors give the stored geometry and surface adjacency. The report describes a location without coordinates. | Mark the square, heading and direction of the unintended move on the level plan. |
| Rhynn | `BUPP1.WSX+0x18D5568` resolves Rhynn dialogue ID 674. `LUPP2.WSX+0x1442B07` resolves dialogue ID 4240 from a separate request. | Compare the later request and the recorded library meeting state in two otherwise matched slots. |
| Blue Deer | `DLOW1.WSX+0x153F2FD` resolves the rent quest row 12. The paid line at `+0x153F2B1` resolves quest row 51. The separate payment confirmation at `+0x154513C` submits row 12 with argument 5 and then sets property 21 on object 286. | Record the room request, whether the rent quest was already present, the cursor item and the payment or refusal event. |
| Blue gem | Four HWHIT kind-4 events at `+0x111AACB`, `+0x111AAE9`, `+0x111AB07` and `+0x111AB25` have distinct mode-3 identities and all use guard 206. The White Tower chicken dialogue has its own event at `+0x111B73F`. | Identify the blue socket and compare its request, guard result and bound object state before and after the other gems or the last chicken. |
| Victoria | CKEEP contains the Victoria room labels. The two commands at `BUPP1.WSX+0x18D1EBE` and `+0x18D1EFA` map to payment dialogue 5303. The first has an object-state guard. That line alone cannot identify a shop transaction. | Record the actual pickup/payment request in Victoria's shop, the visit number and the currency balance. |
| Scavenger eyes | The native item dispatch has separate paths for selecting an item in the pack and submitting a throw request. The report does not identify the inventory instance or the target. | Record the definition key and request kind for the attempted throw and a working throw from the same slot. |
| Volcano elevator | `KVOLC.WSX+0x15D137B` sends its guarded raising event to script index 1012. The lowering event is `+0x15D0C25`. A separate mover event at `+0x15D4F19` links to the annotated delay. | Take out the statue with the player below and record which raising event dispatched and what event brings the platform back. |
| Journal entries | Retail quests such as 12, 35, 36 and 37 have opcode `0x19` commands with argument 5. The 1.07a notes describe a fix. | Identify an exact quest row, capture its completion event and inspect the journal state afterward. |
| Five herbs | `BUPP1.WSX+0x18E3EDA` tests the bound object state against 5 with ≥ at `+0x1B321DB`. Its group submits quest 35 with argument 5 and sets level byte 22 to 1. | Verify all five distinct herb keys, the bound counter and the next guild dialogue after that group. |
| Rix's staff | `EWOD1.WSX+0x1978777` names the post-Rix familiar event in the editor tail. It does not establish an inventory removal. | Save before the staff disappears and record its definition key, equipped state and the first change to the pack or cursor. |
