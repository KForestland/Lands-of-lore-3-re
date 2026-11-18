# GRULO script summary

**CONFIRMED.** Record counts in `GRULO.WSX` come from the two native streams and their event pools. See the [reader](../../lol3-script-events.md).

| Stream | First file offset | Bytes | Records | Group headers | Direct event rows |
|---|---:|---:|---:|---:|---:|
| object | `0xCBFB6E` | 19,922 | 2,845 | 534 | 854 |
| region | `0xCD74AB` | 1,080 | 172 | 16 | 145 |

The predicate count at MAP +0xB8 is 255.

| Event pool | Kind | Count | Native matcher |
|---|---:|---:|---|
| object | 0 | 696 | structural row |
| object | 1 | 309 | structural row |
| object | 2 | 40 | `0x4F1AD0` |
| object | 3 | 16 | `0x4A8240` |
| object | 4 | 100 | `0x4A84FB` |
| object | 5 | 8 | `0x4A82DE` |
| object | 6 | 525 | `0x4A8A48` |
| object | 9 | 140 | `0x4A8C4E` |
| object | 19 | 335 | structural row |
| object | 22 | 25 | `0x4A8DDE` |
| region | 0 | 30 | structural row |
| region | 12 | 145 | `0x4AC252` |
