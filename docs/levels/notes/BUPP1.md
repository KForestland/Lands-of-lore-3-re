# BUPP1 script summary

**CONFIRMED.** Record counts in `BUPP1.WSX` come from the two native streams and their event pools. See the [reader](../../lol3-script-events.md).

| Stream | First file offset | Bytes | Records | Group headers | Direct event rows |
|---|---:|---:|---:|---:|---:|
| object | `0x18C7E39` | 73,555 | 8,795 | 2,106 | 2,693 |
| region | `0x18FE0B0` | 4,702 | 759 | 211 | 326 |

The predicate count at MAP +0xB8 is 255.

| Event pool | Kind | Count | Native matcher |
|---|---:|---:|---|
| object | 0 | 718 | structural row |
| object | 1 | 197 | structural row |
| object | 2 | 49 | `0x4F1AD0` |
| object | 3 | 186 | `0x4A8240` |
| object | 4 | 179 | `0x4A84FB` |
| object | 5 | 49 | `0x4A82DE` |
| object | 6 | 911 | `0x4A8A48` |
| object | 9 | 401 | `0x4A8C4E` |
| object | 10 | 2 | `0x4A8EB2` |
| object | 19 | 521 | structural row |
| object | 21 | 123 | `0x4A9088` |
| object | 22 | 793 | `0x4A8DDE` |
| region | 0 | 96 | structural row |
| region | 11 | 7 | `0x4AC4F2` |
| region | 12 | 319 | `0x4AC252` |
| region | 19 | 71 | structural row |
