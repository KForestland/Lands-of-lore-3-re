# Follow one region event in Lands of Lore III

This example follows a change to the floor when the player enters
surface 2833 in KVOLC with the entry condition described below. The
A surface is a row of the [MAP surface table](lol3-map-odf-readers.md#map-sections-1-and-2);
its event records and commands sit in separate [MAP ranges](lol3-script-events.md#two-event-pools). The steps use the
original `KVOLC.WSX` and the [English retail PE](lol3-lmf-reader.md).

## Entering the surface

1. **CONFIRMED.** The movement code compares the previous surface
   at player +0x104 with the newly selected surface
   (`0x40CBD6–0x40CBE4`). On a transition it installs the new surface
   at `0x40CE1F` and sends event 2 at `0x40CEA4–0x40CEBC`.
   The third argument is 0 or 2 on this ordinary entry path.
2. **CONFIRMED.** At `KVOLC.WSX+0x15E7517` the eight-byte
   record has kind 12, command offset `0x0832`, surface 2833,
   event 2 and condition byte 1. The matcher calculates the
   surface index and checks both the index and event
   (`0x4AC205–0x4AC275`). With condition 1 and incoming
   argument 2, the event-2 arm passes at `0x4AC2BB–0x4AC2E4`.
   With argument 0 it fails there. The next record at
   `+0x15E751F` is kind 12. With no kind-19 predicate trailer,
   the guard returns true (`0x4AC2E9`, `0x4F0611–0x4F0615`,
   `0x4F077E`).
3. **CONFIRMED.** The runner adds `0x0832` to the region
   command stream at `KVOLC.WSX+0x15E5716`
   (`0x4AC450–0x4AC45D`). The header at `+0x15E5F48`
   has byte +4 equal to 1, so it runs one command
   (`0x4E58A2–0x4E58B4`).

## The command changes the floor

**CONFIRMED.** At `KVOLC.WSX+0x15E5F4E`, opcode `0xC4`
targets surface 2833 with the signed word −597 at +4, flags
0 at +6 and speed byte 12 at +7. The handler checks flags
bit 0 for the surface height word to change. Zero selects
surface +0x18. It checks bit 3 for the target mode. Zero
makes −597 an absolute target (`0x4E605F–0x4E6088`).
The original signed height at `KVOLC.WSX+0x15755A8` is −592.
From that state the handler writes −5 into its remaining
distance at command +0xA and marks the surface as moving by
setting +0x24 bit 0x40 (`0x4E608C–0x4E60EB`). It also sends two events
to the surface (`0x4E60E6`, `0x4E60F5`); they are not followed here.

**CONFIRMED.** The region update queue calls the same handler
with its update argument zero; it removes the entry when the
handler reports completion (`0x4F08DD–0x4F08F1`). The update
uses speed 12 and the frame elapsed value at `0x58CBA1`, clamps
the final step to what remains, and updates surface +0x18
(`0x4E6102–0x4E61D2`, `0x4E6277–0x4E627F`). Surface corners
use that signed height shifted left by 16
(`0x4A76DE–0x4A76F5`), so the expected visible result is the floor
of surface 2833 moving from −592 to −597 when the qualifying
entry runs and the movement checks allow completion. The
[opcode table](lol3-script-opcodes.md) identifies the geometry handler.

See the [KVOLC script summary](levels/notes/KVOLC.md), or run the
[script listing tool](lol3-script-opcodes.md)
on your own files. The offsets above identify the record and group.

```sh
python3 tools/lol3_script_notes.py --data "$LOL3_DAT" --out ../lol3-notes
grep -iE '15e7517|15e5f48' ../lol3-notes/KVOLC.region.script-list.md
```
