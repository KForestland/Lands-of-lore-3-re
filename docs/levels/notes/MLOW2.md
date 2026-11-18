# MLOW2 script summary

**CONFIRMED.** Record counts in `MLOW2.WSX` come from the two native streams and their event pools. See the [reader](../../lol3-script-events.md).

| Stream | First file offset | Bytes | Records | Group headers | Direct event rows |
|---|---:|---:|---:|---:|---:|
| object | `0x14CDB6F` | 25,528 | 3,298 | 798 | 1,224 |
| region | `0x14ED156` | 1,214 | 202 | 7 | 192 |

The predicate count at MAP +0xB8 is 255.

| Event pool | Kind | Count | Native matcher |
|---|---:|---:|---|
| object | 0 | 592 | structural row |
| object | 1 | 230 | structural row |
| object | 2 | 37 | `0x4F1AD0` |
| object | 3 | 169 | `0x4A8240` |
| object | 4 | 101 | `0x4A84FB` |
| object | 5 | 42 | `0x4A82DE` |
| object | 6 | 445 | `0x4A8A48` |
| object | 9 | 185 | `0x4A8C4E` |
| object | 19 | 170 | structural row |
| object | 21 | 51 | `0x4A9088` |
| object | 22 | 194 | `0x4A8DDE` |
| region | 0 | 116 | structural row |
| region | 12 | 192 | `0x4AC252` |
| region | 19 | 2 | structural row |
