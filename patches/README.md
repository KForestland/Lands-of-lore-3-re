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
