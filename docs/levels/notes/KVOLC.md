# KVOLC script summary

**CONFIRMED.** Record counts in `KVOLC.WSX` come from the two native streams and their event pools. See the [reader](../../lol3-script-events.md).

| Stream | First file offset | Bytes | Records | Group headers | Direct event rows |
|---|---:|---:|---:|---:|---:|
| object | `0x15C5F18` | 25,213 | 3,183 | 708 | 804 |
| region | `0x15E5716` | 6,623 | 834 | 244 | 312 |

The predicate count at MAP +0xB8 is 255.

| Event pool | Kind | Count | Native matcher |
|---|---:|---:|---|
| object | 0 | 1,146 | structural row |
| object | 1 | 883 | structural row |
| object | 2 | 64 | `0x4F1AD0` |
| object | 3 | 22 | `0x4A8240` |
| object | 4 | 115 | `0x4A84FB` |
| object | 5 | 25 | `0x4A82DE` |
| object | 6 | 472 | `0x4A8A48` |
| object | 9 | 53 | `0x4A8C4E` |
| object | 19 | 255 | structural row |
| object | 22 | 53 | `0x4A8DDE` |
| region | 0 | 105 | structural row |
| region | 11 | 28 | `0x4AC4F2` |
| region | 12 | 268 | `0x4AC252` |
| region | 15 | 16 | `0x4AC650` |
| region | 19 | 9 | structural row |
