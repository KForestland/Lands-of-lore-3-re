# Native dialogue and message tables

Addresses refer to the [English retail image](lol3-lmf-reader.md).

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

**UNCONFIRMED.** The exact binding from an object interaction or
dialogue script command to a dialogue record ID remains open.
The initializer passes the dialogue table's count to its runtime
object at `0x433D8E–0x433D99`. Trace the calls that obtain a row
ID from that object, then match the ID to the corresponding original
`devent` and `dtext` entries. The table layout was checked without
printing the text.
