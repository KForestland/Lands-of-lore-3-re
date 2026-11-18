# PWOD3 script summary

**CONFIRMED.** Record counts in `PWOD3.WSX` come from the two native streams and their event pools. See the [reader](../../lol3-script-events.md).

| Stream | First file offset | Bytes | Records | Group headers | Direct event rows |
|---|---:|---:|---:|---:|---:|
| object | `0x1BB1DD4` | 14,290 | 1,788 | 404 | 674 |
| region | `0x1BC8849` | 366 | 55 | 8 | 35 |

The predicate count at MAP +0xB8 is 255.

| Event pool | Kind | Count | Native matcher |
|---|---:|---:|---|
| object | 0 | 556 | structural row |
| object | 1 | 238 | structural row |
| object | 2 | 44 | `0x4F1AD0` |
| object | 3 | 30 | `0x4A8240` |
| object | 4 | 145 | `0x4A84FB` |
| object | 5 | 27 | `0x4A82DE` |
| object | 6 | 397 | `0x4A8A48` |
| object | 8 | 1 | `0x4A8D25` |
| object | 9 | 30 | `0x4A8C4E` |
| object | 19 | 212 | structural row |
| region | 0 | 27 | structural row |
| region | 12 | 35 | `0x4AC252` |
| region | 19 | 7 | structural row |
