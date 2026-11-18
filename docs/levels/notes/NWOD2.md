# NWOD2 script summary

**CONFIRMED.** Record counts in `NWOD2.WSX` come from the two native streams and their event pools. See the [reader](../../lol3-script-events.md).

| Stream | First file offset | Bytes | Records | Group headers | Direct event rows |
|---|---:|---:|---:|---:|---:|
| object | `0x1BFA14D` | 15,799 | 1,891 | 414 | 704 |
| region | `0x1C11231` | 428 | 66 | 12 | 37 |

The predicate count at MAP +0xB8 is 255.

| Event pool | Kind | Count | Native matcher |
|---|---:|---:|---|
| object | 0 | 532 | structural row |
| object | 1 | 229 | structural row |
| object | 2 | 40 | `0x4F1AD0` |
| object | 3 | 21 | `0x4A8240` |
| object | 4 | 113 | `0x4A84FB` |
| object | 5 | 25 | `0x4A82DE` |
| object | 6 | 427 | `0x4A8A48` |
| object | 9 | 42 | `0x4A8C4E` |
| object | 19 | 222 | structural row |
| object | 22 | 36 | `0x4A8DDE` |
| region | 0 | 29 | structural row |
| region | 12 | 37 | `0x4AC252` |
| region | 19 | 8 | structural row |
