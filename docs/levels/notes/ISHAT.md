# ISHAT script summary

**CONFIRMED.** Record counts in `ISHAT.WSX` come from the two native streams and their event pools. See the [reader](../../lol3-script-events.md).

| Stream | First file offset | Bytes | Records | Group headers | Direct event rows |
|---|---:|---:|---:|---:|---:|
| object | `0xECBDB2` | 25,236 | 3,061 | 531 | 743 |
| region | `0xEE3CFE` | 1,012 | 162 | 10 | 137 |

The predicate count at MAP +0xB8 is 255.

| Event pool | Kind | Count | Native matcher |
|---|---:|---:|---|
| object | 0 | 475 | structural row |
| object | 1 | 275 | structural row |
| object | 2 | 100 | `0x4F1AD0` |
| object | 3 | 12 | `0x4A8240` |
| object | 4 | 104 | `0x4A84FB` |
| object | 5 | 10 | `0x4A82DE` |
| object | 6 | 405 | `0x4A8A48` |
| object | 8 | 5 | `0x4A8D25` |
| object | 9 | 55 | `0x4A8C4E` |
| object | 19 | 209 | structural row |
| object | 22 | 52 | `0x4A8DDE` |
| region | 0 | 29 | structural row |
| region | 11 | 6 | `0x4AC4F2` |
| region | 12 | 131 | `0x4AC252` |
| region | 19 | 1 | structural row |
