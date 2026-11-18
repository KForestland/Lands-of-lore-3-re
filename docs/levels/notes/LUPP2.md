# LUPP2 script summary

**CONFIRMED.** Record counts in `LUPP2.WSX` come from the two native streams and their event pools. See the [reader](../../lol3-script-events.md).

| Stream | First file offset | Bytes | Records | Group headers | Direct event rows |
|---|---:|---:|---:|---:|---:|
| object | `0x14412C5` | 6,514 | 837 | 178 | 337 |
| region | `0x144D5B1` | 102 | 17 | 4 | 9 |

The predicate count at MAP +0xB8 is 255.

| Event pool | Kind | Count | Native matcher |
|---|---:|---:|---|
| object | 0 | 219 | structural row |
| object | 1 | 78 | structural row |
| object | 2 | 14 | `0x4F1AD0` |
| object | 3 | 2 | `0x4A8240` |
| object | 4 | 31 | `0x4A84FB` |
| object | 5 | 16 | `0x4A82DE` |
| object | 6 | 160 | `0x4A8A48` |
| object | 8 | 1 | `0x4A8D25` |
| object | 9 | 68 | `0x4A8C4E` |
| object | 19 | 47 | structural row |
| object | 21 | 1 | `0x4A9088` |
| object | 22 | 44 | `0x4A8DDE` |
| region | 0 | 8 | structural row |
| region | 11 | 1 | `0x4AC4F2` |
| region | 12 | 8 | `0x4AC252` |
