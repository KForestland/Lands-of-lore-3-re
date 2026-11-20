# Patches

Small checked edits for a reader's own copy of the original game. A patch file holds the changed bytes and the expected old bytes, not a game file. A patch must not remove or bypass a disc check, a serial check or any other copy protection, and none here does. The format and its limits are on the [patch format page](../docs/formats/patch.md). This folder has the list. It does not hold a patch file: the remaining reports are not a few proven bytes.

The file format, when a patch is added, is `lol-patch-2`. `kind` is `data` or `program`. Each change has `file`, `entry`, `offset`, `old` and `new`.

These pages read English retail 1.07a. Official updates v1.06J (7 May 1999) and v1.07a (9 May 1999) are already in that build. The 1.07a note covers display and driver crashes, a rebuilt cache, several quests that did not start, infinite experience in the Frozen Wastes, a second shard, a Lower Gladstone room that could not be left, the sigil teleport, and a crash on the White Tower case. Those are program and data fixes already shipped by Westwood. They are not repeated here.

## Reports still named after 1.07a

No few-byte correction for these is on our pages, and the published notes say several have no known fix.

- Guild quests. The Lands of Lore wiki Bugs page says Rescuing Sioned cannot be finished because she does not return to the guild, and Orcish Retribution is accepted but the item is not given.
- The same page says a sewer grate on the left of Gladstone Keep stays shut. The Perfumed Scarf side quest is also reported as never starting.
- Scene faults named after the patch, in the GameFAQs 1.07a notes: a wall in the Draracle's Lair that pulls the player in, a blue gem that cannot be taken, a later shop visit that will not take payment, an elevator urn that leaves the player below, and solved quests that stay in the journal. Each one is a script or state fault. None has a published byte edit.
