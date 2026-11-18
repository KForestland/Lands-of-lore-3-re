# RVOL0 script summary

**CONFIRMED.** Record counts in `RVOL0.WSX` come from the two native streams and their event pools. See the [reader](../../lol3-script-events.md).

| Stream | First file offset | Bytes | Records | Group headers | Direct event rows |
|---|---:|---:|---:|---:|---:|
| object | `0x233F6A` | 1,873 | 194 | 45 | 46 |
| region | `0x235ABD` | 100 | 13 | 4 | 4 |

The predicate count at MAP +0xB8 is 255.

| Event pool | Kind | Count | Native matcher |
|---|---:|---:|---|
| object | 0 | 45 | structural row |
| object | 1 | 36 | structural row |
| object | 2 | 2 | `0x4F1AD0` |
| object | 4 | 2 | `0x4A84FB` |
| object | 5 | 5 | `0x4A82DE` |
| object | 6 | 11 | `0x4A8A48` |
| object | 9 | 5 | `0x4A8C4E` |
| object | 19 | 10 | structural row |
| object | 22 | 21 | `0x4A8DDE` |
| region | 0 | 4 | structural row |
| region | 12 | 4 | `0x4AC252` |
