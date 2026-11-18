# QWOD0 script summary

**CONFIRMED.** Record counts in `QWOD0.WSX` come from the two native streams and their event pools. See the [reader](../../lol3-script-events.md).

| Stream | First file offset | Bytes | Records | Group headers | Direct event rows |
|---|---:|---:|---:|---:|---:|
| object | `0x74BD89` | 1,192 | 164 | 44 | 60 |
| region | `0x751929` | 252 | 42 | 5 | 33 |

The predicate count at MAP +0xB8 is 255.

| Event pool | Kind | Count | Native matcher |
|---|---:|---:|---|
| object | 0 | 84 | structural row |
| object | 1 | 47 | structural row |
| object | 2 | 2 | `0x4F1AD0` |
| object | 3 | 5 | `0x4A8240` |
| object | 4 | 18 | `0x4A84FB` |
| object | 5 | 1 | `0x4A82DE` |
| object | 6 | 25 | `0x4A8A48` |
| object | 9 | 8 | `0x4A8C4E` |
| object | 19 | 4 | structural row |
| object | 22 | 1 | `0x4A8DDE` |
| region | 0 | 10 | structural row |
| region | 12 | 33 | `0x4AC252` |
