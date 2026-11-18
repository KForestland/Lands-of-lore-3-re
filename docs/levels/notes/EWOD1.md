# EWOD1 script summary

**CONFIRMED.** Record counts in `EWOD1.WSX` come from the two native streams and their event pools. See the [reader](../../lol3-script-events.md).

| Stream | First file offset | Bytes | Records | Group headers | Direct event rows |
|---|---:|---:|---:|---:|---:|
| object | `0x1891EA6` | 21,666 | 2,629 | 623 | 1,068 |
| region | `0x18ABEED` | 532 | 82 | 16 | 53 |

The predicate count at MAP +0xB8 is 255.

| Event pool | Kind | Count | Native matcher |
|---|---:|---:|---|
| object | 0 | 648 | structural row |
| object | 1 | 211 | structural row |
| object | 2 | 30 | `0x4F1AD0` |
| object | 3 | 91 | `0x4A8240` |
| object | 4 | 297 | `0x4A84FB` |
| object | 5 | 33 | `0x4A82DE` |
| object | 6 | 452 | `0x4A8A48` |
| object | 9 | 136 | `0x4A8C4E` |
| object | 19 | 223 | structural row |
| object | 22 | 29 | `0x4A8DDE` |
| region | 0 | 35 | structural row |
| region | 12 | 53 | `0x4AC252` |
| region | 19 | 7 | structural row |
