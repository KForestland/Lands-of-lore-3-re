# DLOW1 script summary

**CONFIRMED.** Record counts in `DLOW1.WSX` come from the two native streams and their event pools. See the [reader](../../lol3-script-events.md).

| Stream | First file offset | Bytes | Records | Group headers | Direct event rows |
|---|---:|---:|---:|---:|---:|
| object | `0x153CC0D` | 37,393 | 4,867 | 1,244 | 1,648 |
| region | `0x1560732` | 2,176 | 355 | 121 | 221 |

The predicate count at MAP +0xB8 is 255.

| Event pool | Kind | Count | Native matcher |
|---|---:|---:|---|
| object | 0 | 778 | structural row |
| object | 1 | 234 | structural row |
| object | 2 | 25 | `0x4F1AD0` |
| object | 3 | 185 | `0x4A8240` |
| object | 4 | 116 | `0x4A84FB` |
| object | 5 | 29 | `0x4A82DE` |
| object | 6 | 611 | `0x4A8A48` |
| object | 7 | 3 | `0x4A8B09` |
| object | 9 | 350 | `0x4A8C4E` |
| object | 19 | 173 | structural row |
| object | 21 | 37 | `0x4A9088` |
| object | 22 | 292 | `0x4A8DDE` |
| region | 0 | 118 | structural row |
| region | 12 | 221 | `0x4AC252` |
| region | 19 | 1 | structural row |
