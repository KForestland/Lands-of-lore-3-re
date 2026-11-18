# JUNDR script summary

**CONFIRMED.** Record counts in `JUNDR.WSX` come from the two native streams and their event pools. See the [reader](../../lol3-script-events.md).

| Stream | First file offset | Bytes | Records | Group headers | Direct event rows |
|---|---:|---:|---:|---:|---:|
| object | `0xF23EB2` | 53,332 | 7,766 | 1,587 | 2,019 |
| region | `0xF4DD57` | 1,256 | 195 | 28 | 142 |

The predicate count at MAP +0xB8 is 255.

| Event pool | Kind | Count | Native matcher |
|---|---:|---:|---|
| object | 0 | 795 | structural row |
| object | 1 | 473 | structural row |
| object | 2 | 66 | `0x4F1AD0` |
| object | 3 | 12 | `0x4A8240` |
| object | 4 | 162 | `0x4A84FB` |
| object | 5 | 178 | `0x4A82DE` |
| object | 6 | 1,422 | `0x4A8A48` |
| object | 8 | 9 | `0x4A8D25` |
| object | 9 | 105 | `0x4A8C4E` |
| object | 10 | 5 | `0x4A8EB2` |
| object | 19 | 833 | structural row |
| object | 22 | 60 | `0x4A8DDE` |
| region | 0 | 44 | structural row |
| region | 12 | 142 | `0x4AC252` |
| region | 19 | 4 | structural row |
