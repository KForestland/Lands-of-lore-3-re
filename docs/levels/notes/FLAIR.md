# FLAIR script summary

**CONFIRMED.** Record counts in `FLAIR.WSX` come from the two native streams and their event pools. See the [reader](../../lol3-script-events.md).

| Stream | First file offset | Bytes | Records | Group headers | Direct event rows |
|---|---:|---:|---:|---:|---:|
| object | `0x15A0A94` | 46,018 | 5,718 | 1,312 | 1,493 |
| region | `0x15CE163` | 5,054 | 697 | 164 | 271 |

The predicate count at MAP +0xB8 is 255.

| Event pool | Kind | Count | Native matcher |
|---|---:|---:|---|
| object | 0 | 1,106 | structural row |
| object | 1 | 500 | structural row |
| object | 2 | 162 | `0x4F1AD0` |
| object | 3 | 12 | `0x4A8240` |
| object | 4 | 204 | `0x4A84FB` |
| object | 5 | 31 | `0x4A82DE` |
| object | 6 | 741 | `0x4A8A48` |
| object | 9 | 77 | `0x4A8C4E` |
| object | 10 | 2 | `0x4A8EB2` |
| object | 19 | 310 | structural row |
| object | 22 | 264 | `0x4A8DDE` |
| region | 0 | 103 | structural row |
| region | 11 | 1 | `0x4AC4F2` |
| region | 12 | 216 | `0x4AC252` |
| region | 15 | 54 | `0x4AC650` |
| region | 19 | 29 | structural row |
