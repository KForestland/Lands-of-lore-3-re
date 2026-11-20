# Patches

Small checked edits for a reader's own copy of the original game. A patch records the replacement bytes and a hash of the span it replaces. A patch must not remove or bypass a disc check, a serial check or any other copy protection, and none here does. The format and its limits are on the [patch format page](../docs/formats/patch.md). This folder has the list. It does not hold a patch file: the remaining reports are not a few proven bytes.

The format is `lol-patch-3`. Each change lists its file, entry, offset, old span length and SHA-256, and new bytes. Keep `undo.json` private. It holds original game bytes from your copy.

How to start the game on a current machine is [Running](RUNNING.md).

These pages read English retail 1.07a. The program stores `Win95/NT 1.07a` at `LOL3.DAT+0x14DEAC` and `May  7 1999` at `+0x14DE74`. It does not store a second version string, and it does not store the changelog. Official updates v1.06J (7 May 1999) and v1.07a (9 May 1999) are already in that build. The 1.07a note covers display and driver crashes, a rebuilt cache, several quests that did not start, infinite experience in the Frozen Wastes, a second shard, a Lower Gladstone room that could not be left, the sigil teleport, and a crash on the White Tower case. Those are program and data fixes already shipped by Westwood. They are not repeated here. A search of this `LOL3.DAT` for the report names (Sioned, the scarf, the Draracle, the White Tower, a grate) found none of those words. Nearby bytes that look similar are level and movie stems (`uhfrozen`, `mfrozen`) and the key name `COMMENTS_JOURNAL`, not these reports.

## Reports still named after 1.07a

No few-byte correction for these is on our pages, and the published notes say several have no known fix.

- Guild quests. The Lands of Lore wiki Bugs page says Rescuing Sioned cannot be finished because she does not return to the guild, and Orcish Retribution is accepted but the item is not given.
- The same page says a sewer grate on the left of Gladstone Keep stays shut. The Perfumed Scarf side quest is also reported as never starting.
- Scene faults named after the patch, in the GameFAQs 1.07a notes: a wall in the Draracle's Lair that pulls the player in, a blue gem that cannot be taken, a later shop visit that will not take payment, an elevator urn that leaves the player below, and solved quests that stay in the journal. Each one is a script or state fault. None has a published byte edit.

No row above has a file offset in this program. A small patch is not written for any of them. To see a report, follow the place named in that row. This pass did not launch the game.
