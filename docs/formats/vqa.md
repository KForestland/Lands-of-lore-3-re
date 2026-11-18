# VQA movies

**CONFIRMED.** The original executable indexes the 19 stem pointers at
`LOL3.DAT+0x148BD0` (VA `0x54A3D0`). The caller formats `%s.vqa`
at `0x46FCF2–0x46FD1F`, then formats `outtakes\%s` and checks the
resource at `0x46FFA5–0x46FFC8`. Native hash lookup matches every
`MOVIES1–4` key. The opener at `0x470043` passes the constructed
name to the VQA reader at `0x50DF70`.

| Archive and file offset | Key | Stem in `outtakes` | Frames |
|---|---:|---|---:|
| `MOVIES1.WSX+0xB5EA3BE` | `0xE6B697C3` | `msizzle.vqa` | 630 |
| `MOVIES1.WSX+0x6A72B60` | `0xF49392E5` | `mking.vqa` | 3,271 |
| `MOVIES1.WSX+0x9B10DD8` | `0x1A5BC1AC` | `mcredit2.vqa` | 3,922 |
| `MOVIES1.WSX+0x42` | `0x7DEAB07C` | `mintro01.vqa` | 2,024 |
| `MOVIES1.WSX+0x366BDC4` | `0x7DEAB17C` | `mintro02.vqa` | 2,222 |
| `MOVIES2.WSX+0x1E` | `0xB6D39FE5` | `mtent.vqa` | 2,515 |
| `MOVIES2.WSX+0x3C47C74` | `0x57537BDE` | `mvol0.vqa` | 166 |
| `movies3.wsx+0x35ABB6` | `0x39723254` | `munder.vqa` | 887 |
| `movies3.wsx+0x2A` | `0x57538EDE` | `mvolc.vqa` | 166 |
| `movies3.wsx+0x1340B5E` | `0x607583A3` | `mshard1.vqa` | 236 |
| `movies4.wsx+0x92B3850` | `0xBB2F297C` | `mruloi.vqa` | 1,136 |
| `movies4.wsx+0x841696A` | `0xCE57BA70` | `mshatter.vqa` | 691 |
| `movies4.wsx+0x6763F54` | `0xE3FF6CA7` | `mfrozen.vqa` | 535 |
| `movies4.wsx+0x1F849D4` | `0x027D61CF` | `mepilog.vqa` | 361 |
| `movies4.wsx+0x4AB3EE` | `0x1A5BE2AC` | `mcredits.vqa` | 3,922 |
| `movies4.wsx+0x72` | `0x1AE6C0A4` | `mcmpfire.vqa` | 367 |
| `movies4.wsx+0x29378EE` | `0x53B663C2` | `mfinale.vqa` | 2,824 |
| `movies4.wsx+0x75736CE` | `0x607584A3` | `mshard2.vqa` | 236 |
| `movies4.wsx+0x7C4BBBA` | `0x607585A3` | `mshard3.vqa` | 246 |

## Frame and audio chunks

**CONFIRMED.** The native reader checks `FORM` and `WVQA` at
`0x50E0E6–0x50E131`, swaps the chunk length to host order and
rounds the skip to an even byte (`0x50E149–0x50E191`,
`0x50E30A–0x50E313`). VQHD must be 42 bytes
(`0x50E1A9–0x50E1D0`). Its u16 +4 is the frame count, u16
+6/+8 are width/height, and +0x0C defaults the frame rate
(`0x50E1D6–0x50E22B`). The checked header fields on all 19
are version 3, flags `0x1D`, 640 × 480, 4 × 4 block dimensions
and 15 frames per second. Block size is used as the divisor for
the displayed dimensions at `0x5126F9–0x512721`.

**CONFIRMED.** Every FINF payload contains four bytes per frame.
In all 26,357 stored entries, multiplying the u32 by two gives
a byte offset from FORM start. 26,106 point to an SN2J chunk,
and 251 to VQFL. The executable dispatches FINF at
`0x50E26F–0x50E297`. For example, in
`MOVIES1.WSX+0x42`, the first FINF word at file `+0x1CA`
is `0x1094`, pointing to SN2J at file `+0x216A`.

**CONFIRMED.** VQHD +0x18/+0x1A/+0x1B hold
22,050 Hz, two channels and 16 output bits in the 19 files.
SND2 is a differential 4-bit stream with a persistent state per
channel. Dispatch enters `0x5124C0` from `0x50FC02`;
`0x5124EE–0x512501` computes decoded bytes as
`compressed bytes × (output bits >> 2)`. The decoder
selects the 16-bit stereo arm at `0x517304 → 0x5176D8`.
It updates running samples from lookup tables and clamps to signed
16-bit range (`0x517740–0x51776A`). A 1,470-byte SND2 therefore
gives 5,880 bytes or 1,470 stereo sample frames at the observed
settings. 26,356 chunks have 1,470 bytes. The last odd-sized
chunk family has one 1,469-byte example in the msizzle entry.

**CONFIRMED.** SN2J restores two six-byte decoder state records.
Per channel the first u16 is the step state and the following
signed dword is the sample accumulator. The native handler copies
the fields into the state at `0x512684–0x5126AF`; the decoder
loads that state at `0x5176DA–0x5176DE`. The second SN2J in
`MOVIES1.WSX+0x42` starts at file `+0x1795E`; its
body bytes `40 05 04 F8 FF FF C0 05 1B F6 FF FF` give
running samples −2,044 and −2,533.

**UNCONFIRMED.** The full `LINF` and `CINF` layouts and
the frame pixel decode are open. The first mintro01 VQFR at
`MOVIES1.WSX+0x2744` holds a CBFZ chunk. A trace from
the native VQFR/VQFL tags to the inner CBFZ/VPTR branches
would bind the video encoding.
