# Native dialogue and message tables

Addresses refer to the [image from the English GOG release (1.07a)](lol3-lmf-reader.md).

**CONFIRMED.** At `0x433CD3–0x433D1B` the journal-related
initializer probes then loads `qevent.trr` through `0x4092A0`.
Its neighbours at `0x433D49` and `0x433D72` load
`qtext.trr` and `devent.trr`. The strings are at
`LOL3.DAT+0x147054`, +0x147048 and +0x14703C.
A separate caller at `0x454E10` opens `dtext.trr`
(string at +0x1485A0).

**CONFIRMED.** The eager loader reads u32 count, count u32 IDs, then
count+1 u32 stored boundaries (`0x4092D5–0x40935B`). It adjusts
each boundary by subtracting `8*count+4` at
`0x40936A–0x40937B`. The actual file payload follows the final
directory word at `8*count+8`. Thus each stored boundary measures
four fewer bytes than its corresponding file position in these entries. The payload read is `0x4093C3` and
its in-memory transform is `0x4093D0`. The lookup at
`0x409440–0x40947C` linearly matches an ID and returns a pointer
to the associated payload. The alternate reader `0x409490`
retains the file name and initializes an 0x800-byte buffer
(`0x40958B–0x4095C4`).

| Original entry in DAT/locallng.wsx | File offset | Count | Bytes |
|---|---:|---:|---:|
| qevent.trr | `0x5987786` | 67 | 879 |
| qtext.trr | `0x5987AF5` | 67 | 6,314 |
| devent.trr | `0x58E4F95` | 5,763 | 74,927 |
| dtext.trr | `0x58F7444` | 5,763 | 440,376 |

## Script identifiers and row lookup

**CONFIRMED.** The object runner's opcode 0x16 takes an
identifier starting at command +4. On the admitted branch
`0x448237–0x448287`, it sends that identifier to the sound
request and then calls `0x4344B0` and `0x4340D0` with it.
Both readers copy bytes 4–7 from the supplied identifier and
NUL-terminate the four-character search key
(`0x4340E3–0x4340F7`, `0x4344C6–0x4344D9`).
Thus the tag is command bytes +8–+0x0B.

**CONFIRMED.** `0x4340D0` binary-searches the `devent.trr` tags
(stored in case-insensitive order, IDs 0 to count−1; rows probed
by ID through `0x409440`; `0x434110–0x434146`), using the
case-insensitive comparator at `0x51A160–0x51A1AE`. On a
match it submits the row ID as event type 10 through
`0x434180` and sends the same ID to `0x455250`
(`0x434148–0x43416E`). The journal-related sibling
`0x4344B0` scans `qevent.trr` and looks up the corresponding
`qtext.trr` row on a match (`0x4344DE–0x434516`).
The relevant pointers were installed at `0x433D24`,
`0x433D52` and `0x433D7B`.

**CONFIRMED.** Both `devent.trr` and `qevent.trr` consist of
five-byte entries with four tag bytes and a trailing zero in the
listed original archive spans. IDs are unique in each table.
The dialogue tag table has 5,761 distinct case-folded tags
for 5,763 IDs. All 5,763 IDs appear in `dtext.trr`. All
67 `qevent.trr` IDs appear in `qtext.trr`. A case-insensitive
comparison of command bytes +8–+0x0B against the dialogue
tag table matches 2,641 of the 2,642 stored opcode-0x16
records from MAP +0x44/+0x8C. For example,
`CKEEP.WSX+0xD039F0` joins to dialogue ID 2711.
The one unmatched record is `HWHIT.WSX+0x111423D`.
**CONFIRMED.** Its identifier is seven characters, `dh09eh2`, so the
tag is `eh2` plus a NUL. Its group (index 2860, `HWHIT.WSX+0x1114219`)
is run by the kind-6 event at `HWHIT.WSX+0x111BE27`. Under the prefix that matches the other names,
`HWHITs.wsx` has no `LEVELS\HWHIT\dh09eh2.aud` entry, while `dh09eh26.aud` exists and
no opcode-0x16 record names it. Files `dh09eh20`, `21` and `23`–`26` exist; records
name `20`, `21`, `23`–`25` and `dh09eh2`; neither uses `22`. Whether a last digit was
lost, and which, is **UNCONFIRMED** (`26` is the only file without a record). Triggering the kind-6 event at `HWHIT.WSX+0x111BE27` in a running game and logging the name the sound request on `0x448237–0x448287` opens settles it. The region stream holds one more opcode-0x16
record, `PWOD3.WSX+0x1BC8883`, whose four-character tag `hwl2` also
matches no dialogue tag. Archive names
are case-insensitive; the files are stored in lower case.

**CONFIRMED.** Opcode 0x19, with dword +0xC equal to 5,
sends u32 +4 as the quest row ID and +8 as the associated
argument to `0x434560` (`0x4482AC–0x4482C6`).
The latter queries both quest tables at `0x43457B` and
`0x434592`. At `BUPP1.WSX+0x18C8D4F` the ID is 61
and the argument is 5. All 53 object-stream occurrences
and one region-stream occurrence have +0xC = 5 and valid
quest IDs in the original `qevent.trr` ID array.

## Text read and transform

**CONFIRMED.** The dialogue display opens `dtext.trr` through
the streaming reader at `0x454E10` and stores its handle
at object +0xCD8. It supplies the dialog ID from the parallel
list to `0x409650` at `0x4547FC–0x45480B`. The renderer
also calls that reader with the selected ID at
`0x458777–0x45878C`. The reader scans IDs, reads the
selected payload and applies the same byte transform as the
eager reader (`0x409698–0x409712`).

**CONFIRMED.** The transform replaces a matching byte from
the NUL-terminated table `LOL3.DAT+0x1521B0` with the
corresponding byte from +0x1521C0. Other bytes pass unchanged
(`0x5086C2–0x508701`). The total buffer length is passed
by the caller. No lines are reproduced here.

**CONFIRMED.** The duplicate tags are `mr24` (IDs 3572, 3573) and
`ya85` (5196, 5197). Replaying the search `0x434102–0x434146` on the
original table returns 3572 and 5196. The search never probes the last
ID, 5762 (`ZK49`). No stored opcode-0x16 record and no string in
`LOL3.DAT` uses these three tags. The same search finds the
other 2,641 stored object-stream tags. **UNCONFIRMED:** what the game does with the HWHIT query
above, the keys built at run time by `0x48A6F3–0x48A709`, and the
meaning of every display format marker. Settle the first two in a
running game: break at `0x4340D0` and `0x422FA0` when the HWHIT
kind-6 event fires, and record the key, the path and whether
`0x434180` is reached. Settle the markers by listing every byte the
renderer branches on after `0x45878C`.

## Writing the stored tables

**CONFIRMED.** `tools/lol3_text_writer.py --check --data /path/to/DAT`
rebuilds the counts, ordered IDs, relative boundaries and NUL-terminated
stored payloads before the transform at `0x5086C2`. It reads 53 TRR
tables and each rebuilds byte for byte. The 53 are 26 TRR members of
`DAT/locallng.wsx`, the same 26 members in the byte-identical
`locallng.wsx` beside `DAT`, and the loose `PROMPT.TRR` at file +0. That
is 26 distinct tables: the loose prompt table equals the member at
`locallng.wsx+0x5986BB5` (key `0x623224A4`, file name at
`LOL3.DAT+0x143B8C`). Counting every copy they hold 26,170 text or tag
records; one archive's 26 members hold 13,065. The four quest and
dialogue tables are identified by the offsets above, and their counts
(67, 67, 5,763, 5,763) match `lol3_media_check.py --trr`. `--list` prints
the file, source offset, key, byte length and row count for every
matching entry, never the text.
