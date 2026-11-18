# OLOW3 script summary

**CONFIRMED.** Record counts in `OLOW3.WSX` come from the two native streams and their event pools. See the [reader](../../lol3-script-events.md).

| Stream | First file offset | Bytes | Records | Group headers | Direct event rows |
|---|---:|---:|---:|---:|---:|
| object | `0x16C4DD5` | 19,454 | 2,494 | 538 | 1,016 |
| region | `0x16DFBD1` | 1,220 | 203 | 2 | 196 |

The predicate count at MAP +0xB8 is 255.

| Event pool | Kind | Count | Native matcher |
|---|---:|---:|---|
| object | 0 | 551 | structural row |
| object | 1 | 236 | structural row |
| object | 2 | 32 | `0x4F1AD0` |
| object | 3 | 137 | `0x4A8240` |
| object | 4 | 82 | `0x4A84FB` |
| object | 5 | 49 | `0x4A82DE` |
| object | 6 | 379 | `0x4A8A48` |
| object | 9 | 169 | `0x4A8C4E` |
| object | 19 | 124 | structural row |
| object | 21 | 32 | `0x4A9088` |
| object | 22 | 136 | `0x4A8DDE` |
| region | 0 | 111 | structural row |
| region | 12 | 196 | `0x4AC252` |
