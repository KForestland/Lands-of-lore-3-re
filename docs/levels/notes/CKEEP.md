# CKEEP script summary

**CONFIRMED.** Record counts in `CKEEP.WSX` come from the two native streams and their event pools. See the [reader](../../lol3-script-events.md).

| Stream | First file offset | Bytes | Records | Group headers | Direct event rows |
|---|---:|---:|---:|---:|---:|
| object | `0xD036F4` | 15,228 | 1,746 | 445 | 481 |
| region | `0xD0E7B7` | 210 | 35 | 10 | 19 |

The predicate count at MAP +0xB8 is 255.

| Event pool | Kind | Count | Native matcher |
|---|---:|---:|---|
| object | 0 | 136 | structural row |
| object | 1 | 62 | structural row |
| object | 2 | 15 | `0x4F1AD0` |
| object | 3 | 6 | `0x4A8240` |
| object | 4 | 45 | `0x4A84FB` |
| object | 5 | 10 | `0x4A82DE` |
| object | 6 | 172 | `0x4A8A48` |
| object | 9 | 2 | `0x4A8C4E` |
| object | 19 | 99 | structural row |
| object | 21 | 25 | `0x4A9088` |
| object | 22 | 206 | `0x4A8DDE` |
| region | 0 | 11 | structural row |
| region | 12 | 19 | `0x4AC252` |
| region | 19 | 5 | structural row |
