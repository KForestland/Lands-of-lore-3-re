# HWHIT script summary

**CONFIRMED.** Record counts in `HWHIT.WSX` come from the two native streams and their event pools. See the [reader](../../lol3-script-events.md).

| Stream | First file offset | Bytes | Records | Group headers | Direct event rows |
|---|---:|---:|---:|---:|---:|
| object | `0x110EB73` | 28,326 | 3,549 | 764 | 959 |
| region | `0x1127A52` | 1,126 | 146 | 26 | 67 |

The predicate count at MAP +0xB8 is 255.

| Event pool | Kind | Count | Native matcher |
|---|---:|---:|---|
| object | 0 | 564 | structural row |
| object | 1 | 240 | structural row |
| object | 2 | 45 | `0x4F1AD0` |
| object | 3 | 92 | `0x4A8240` |
| object | 4 | 171 | `0x4A84FB` |
| object | 5 | 64 | `0x4A82DE` |
| object | 6 | 345 | `0x4A8A48` |
| object | 9 | 77 | `0x4A8C4E` |
| object | 10 | 8 | `0x4A8EB2` |
| object | 19 | 244 | structural row |
| object | 22 | 157 | `0x4A8DDE` |
| region | 0 | 25 | structural row |
| region | 11 | 6 | `0x4AC4F2` |
| region | 12 | 59 | `0x4AC252` |
| region | 15 | 2 | `0x4AC650` |
| region | 19 | 1 | structural row |
