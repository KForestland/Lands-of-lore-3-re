# SWOD4 script summary

**CONFIRMED.** Record counts in `SWOD4.WSX` come from the two native streams and their event pools. See the [reader](../../lol3-script-events.md).

| Stream | First file offset | Bytes | Records | Group headers | Direct event rows |
|---|---:|---:|---:|---:|---:|
| object | `0x5DEAA4` | 956 | 115 | 31 | 53 |
| region | `0x5E3538` | 34 | 5 | 1 | 2 |

The predicate count at MAP +0xB8 is 255.

| Event pool | Kind | Count | Native matcher |
|---|---:|---:|---|
| object | 0 | 58 | structural row |
| object | 1 | 38 | structural row |
| object | 2 | 1 | `0x4F1AD0` |
| object | 3 | 12 | `0x4A8240` |
| object | 4 | 14 | `0x4A84FB` |
| object | 5 | 3 | `0x4A82DE` |
| object | 6 | 17 | `0x4A8A48` |
| object | 9 | 1 | `0x4A8C4E` |
| object | 19 | 3 | structural row |
| object | 22 | 5 | `0x4A8DDE` |
| region | 0 | 4 | structural row |
| region | 12 | 2 | `0x4AC252` |
