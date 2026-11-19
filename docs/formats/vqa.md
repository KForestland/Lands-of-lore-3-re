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
The native seek computes `2 × (word & 0x0FFFFFFF)`
(`0x5103C7–0x5103DD`, `0x5107FA–0x510811`). The offset
is from FORM start. All 26,357 shipped words have a zero high
nibble. Of these, 26,106 point to an SN2J chunk and 251 to
VQFL. FINF dispatch at `0x50E26F–0x50E297` reads these words
into the buffer at decoder +0x762 (`0x511C50–0x511C6B`). For example, in
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
settings. 26,356 chunks have 1,470 bytes. The remaining
chunk is 1,469 bytes, in the msizzle entry.

**CONFIRMED.** SN2J restores two six-byte decoder state records.
Per channel the first u16 is the step state and the following
signed dword is the sample accumulator. The native handler copies
the fields into the state at `0x512684–0x5126AF`; the decoder
loads that state at `0x5176DA–0x5176DE`. The second SN2J in
`MOVIES1.WSX+0x42` starts at file `+0x1795E`; its
body bytes `40 05 04 F8 FF FF C0 05 1B F6 FF FF` give
running samples −2,044 and −2,533.

## Seek tables and frame payloads

**CONFIRMED.** Each `LINF` contains `LINH` and `LIND`.
Each `CINF` contains `CINH` and `CIND`. Both use
the ordinary big-endian child chunk sizes and little-endian
fields. The readers are `0x510E50–0x510FF3` and
`0x5118E0–0x511A93`.

| Chunk | Original fields and use |
|---|---|
| LINH | Six bytes. u16 +0 is row count, used to allocate four bytes per row at `0x510ECE–0x510F19`. The next word's low two bits gate the first-frame membership search at `0x510285–0x5102B4`. The 19 header values at +2/+4 are 2/0. |
| LIND | Four bytes per row, u16 first and u16 end frame. `0x5102A5–0x5102B4` compares the first frame and uses a four-byte stride. `0x50F33A–0x50F384` uses both words to estimate the indexed span. All 270 recorded end values equal VQHD frame count minus one. |
| CINH | Eight bytes. u16 +0 is row count and allocates six bytes per row at `0x51196D–0x5119B8`. Word +2 is a divisor in the codebook-buffer calculation at `0x513913–0x513952`. Both trailing words are zero in all 19 entries. |
| CIND | Six bytes per row, u16 start frame and u32 compressed codebook bytes. The scanner at `0x511E95–0x511EC7` returns the first row's length whose start frame is greater than its argument. That limit feeds codebook accumulation at `0x511DA2–0x511DB2` and `0x511F14–0x511F24`. |

For the movie starting at `MOVIES1.WSX+0x42`, the LINH body at file +0x90
and the CINH body at +0x116 both give 26 rows. Their first LIND and
CIND pairs are (0, 2023) and (0, 85810), at +0x9E and
+0x126. The first CBFZ body starts at +0x2754 and is 85,810
bytes. In all 19 movies, the LIND and CIND start frames
match one another. All 270 CIND lengths match the CBFZ
at that frame. Frame 0 uses the CBFZ inside its VQFR.
The other 251 codebooks are in VQFL, at the corresponding
FINF offset. The media tool verifies the joins in place.

**CONFIRMED.** VQFR and VQFL both pass their nested chunks
to `0x510B00` (`0x50FD41`, `0x50FD8B`).
That parser swaps each child size and advances by
`8 + round_up_even(size)` (`0x510B33–0x510B86`).
It reads CBFZ through `0x511D00`, raw VPTR through
`0x512170`, and compressed VPRZ through `0x5121B0`
(`0x510CAF`, `0x510CE6`, `0x510DAF`). Across the
corpus, 3,616 VQFRs hold VPTR and 22,741 hold VPRZ.
All 26,357 hold exactly one of those two pointer streams.

**CONFIRMED.** Both compressed payloads reach the same
LCW routine, through `0x51311D` for CBFZ and
`0x513189` for VPRZ. The decoder at `0x517F3B` selects
the relative arm and skips the first input byte when it is
zero (`0x517F4F–0x517F59`, `0x51800F–0x518019`).
Both arms use an overlapping output copy with a 12-bit
back distance for command 0x00–0x7F, literals for
0x81–0xBF, an end marker 0x80 and a u16 count plus byte
fill for 0xFE. Commands 0xC0–0xFD use length
`(command & 63) + 3`, and 0xFF takes a u16 length.
They then take a u16 source as an absolute output offset
in the ordinary arm, or as distance back from the current
output in the relative arm (`0x517F64–0x517FFE`,
`0x51801B–0x5180AF`). The caller supplies an output
limit. The native stop is the marker or this limit.

### 4×4 block pointers

**CONFIRMED.** The 19 original headers use 4×4 blocks and
mode byte 4 at VQHD +0x20. The callback selector installs
`0x5168F0` and `0x516A40` for that combination
(`0x51273A–0x512745`, `0x512795–0x5127D7`).
Both VPTR and VPRZ set chunk-state bit 0x20, so the
output routine chooses the second callback, `0x516A40`
(`0x510CB4–0x510CC0`, `0x510DB4–0x510DC3`,
`0x512A91–0x512AAF`). It executes the expanded stream
over 160 × 120 tiles, from left to right then top to bottom.
Each codebook tile is 32 bytes, with four rows of four
little-endian pixel words (`0x516CCF–0x516D0B`).
A transparent copy leaves the previous pixel at source
word 0x8000 (`0x516B63–0x516B91`).

| Word high bits | Action |
|---|---|
| `0x0000` | Advance by the low byte without drawing (`0x516AB0–0x516AC0`). |
| `0x2000` | Copy the tile in the low byte `2 + 2*((word>>8)&31)` times (`0x516AC5–0x516B45`). |
| `0x4000` | Copy the tile in the low byte, then copy the next `2 + 2*((word>>8)&31)` tiles, reading one index byte per tile (`0x516BF6–0x516CC6`). |
| `0x6000` | Copy one opaque tile selected by the low 13 bits (`0x516CCB–0x516D1E`). |
| `0x8000` | Copy one tile selected by the low 13 bits, with transparency (`0x516D23–0x516D29`, `0x516B5F–0x516BA2`). |
| `0xA000` | Copy an opaque tile selected by the low 13 bits. The next byte gives the count (`0x516A9C`, `0x516AD0–0x516AF7`, `0x516D2F–0x516D35`). |
| `0xC000` | Same count and 13-bit index as 0xA000, with transparency (`0x516D3B–0x516DC9`). |
| `0xE000` | No drawing or destination advancement on this callback (`0x516D3B–0x516D41`, `0x516BA8`). |

For example, the first VPTR in the movie at
`MOVIES1.WSX+0x42` begins at file +0x1768E. Its first three
little-endian words are 0x3F00, 0x3F00 and 0x2F00,
copying tile 0 for 64, 64 and 32 blocks. Those 160 tiles
fill the first block row exactly.

**CONFIRMED.** A bounded in-memory pass expanded the
270 CBFZ and 22,741 VPRZ payloads with the two native LCW
arms. It also walked the 3,616 raw VPTR payloads. Every pointer
stream consumed exactly its bytes, filled a 160 × 120 block grid
without a command crossing a block row, and used in-range tile
indexes. The native output limit for the pointers is
`(2 × tile_count + 4) & ~3` (`0x513AD7–0x513B09`).
Among the expanded codebooks, 257 have a whole number
of 32-byte tiles, 11 have one trailing byte, and two have
two. No original pointer in those streams selects a partial tile.
The only observed pointer modes were 0x0000, 0x2000,
0x4000, 0x6000 and 0xA000. The other rows above are
confirmed in the native callback.

The tile callback writes packed u16 words. See the
[live offscreen format and test word](#live-introduction-opener).
**CORRECTED.** The trailing VQHD words are not all unused. The decoder
copies the header to decoder +0xEC (`0x50E1BE`). Dword +0x22 is a
size bound. The FINF handler `0x513870` computes
`(u16 +0x10 × block width × block height + 4) & ~3`, doubled for
mode 1 or 4 (`0x513896–0x5138CE`). A larger +0x22 fails with −3.
Zero is replaced by that bound (`0x5138D4–0x5138F5`). The value
plus 0x10, rounded down to four, goes to decoder +0x766
(`0x5139AA–0x5139BB`). All 19 headers hold a nonzero +0x22 below
the bound, for example 0x16AF0 in `MOVIES1.WSX+0x42`. Dword +0x26
is an audio byte count (`0x51069A–0x5106C6`). If it is zero and flag
bit 8 is clear, the count becomes half the audio bytes per second.
It is zero in all 19. Bytes +0x1C to +0x1F give the audio rate,
channels and bits when flag bit 0x40 is set (`0x50E3C6–0x50E3DE`).
They are zero, and flags 0x1D lack bit 0x40. Only u16 +0x0E and
byte +0x21 have no reader in the decoder code `0x50D000–0x519000`.
Both are zero in all 19.

## Live introduction opener

**CONFIRMED.** On the original English executable under Wine 9.0,
the Extras menu requested `outtakes\mintro01.vqa` at `0x50DF70`.
With Direct3D and the audio drivers disabled, the path opened
`MOVIES1.WSX` and returned a null decoder, which faulted at the
`[ECX+0x80]` read at `0x50ECA7`. A second launch supplied the exact
original `MOVIES1.WSX+0x42` entry as a loose file in the test copy
(57,064,834 bytes, SHA-256 prefix `db4ed8d3b7cf`). This exercised
file reads through VQHD, LIND, CIND and FINF. The call at `0x50E404`
returned −13 at `0x50E409`. The opener then returned −13 with the
decoder pointer still zero at `0x470048`. The [audio initialization
path](#frame-and-audio-chunks) therefore failed before the tile callback.

**CONFIRMED.** The caller requests a 640 × 480 movie object with
nominal depth 16 at `0x46FEAA–0x46FEB9`. The DirectDraw path
allocates its offscreen surface through `0x50365B` and reads back its
descriptor at `0x50377F`. The creation descriptor's flags are 7
(`0x50361D`), so it requests dimensions and caps. In this run
`GetSurfaceDesc` and the subsequent `Lock` both returned depth 16,
pitch 1,280 and masks `F800/07E0/001F` for that same offscreen surface.
The original call to `0x5046E0` at `0x470078` takes its pixel pointer,
then the decoder setup would store it at decoder +0x1AA at `0x50EE38`.
The RGB565 movie surface and the [RGB5551 texture copy](../lol3-texture-bake.md#live-direct3d-texture-format)
are separate measurements.

**CONFIRMED, original playback with a null sink.** Wine 9.0 used
a private PulseAudio 16.1 server exposing only `module-null-sink`.
The English retail executable opened the archive clip with status
−1 and a populated decoder at `0x470048`. It presented the
640 × 480 movie through Direct3D. The locked movie surface,
intermediate DirectDraw surface and primary surface all had depth 16
and masks `F800/07E0/001F`. The movie lock reported a 1,280-byte
pitch (`0x50377F`, `0x5046E0`, `0x470078`).

**CONFIRMED.** Decoder callback `0x46FDB0` reaches renderer slot
+0x8C through `0x46FDD8`. With renderer table `0x538730`, the
slot is `0x47ABE0`, which calls the format reader `0x409C70`.
It counts the contiguous bits in the reported channel masks.
For 5/6/5, `0x409D27` selects conversion mode 2, whose table
arm at `0x46F93C` uses shifts 11, 6 and 0 for the original
five-bit red, green and blue. `0x46FA48–0x46FA53` replaces
each word through that table before the tile callback. For a 15-bit
word `w`, this mode yields `((w & 0x7FE0) << 1) | (w & 0x1F)`.

**CONFIRMED, frame 16.** The frame number came from frame
node +0x1C (read by `0x513212`). The first raw VPTR word
`0x2101` (`MOVIES1.WSX+0x1E60E`) selects tile 1. The fourth
word of that tile, at expanded book +0x26 from CBFZ `+0x2754`,
is `0x0421`. The corresponding live book word at `0x512AAF`
was `0x0841`. The callback selected `0x516A40` and copied
that word at pixel (3, 0), as measured before and after the call
(`0x512AAF` and `0x512AB5`). The same word remained in the
movie surface after submission through `0x470109` and `0x47011B`.
The measured RGB565 mask triple gives channel integers `(1, 2, 1)`.

**CONFIRMED, DirectDraw submission.** The original renderer copies
the movie to its intermediate surface in tiles at `0x476275` and
submits the frame via its display callback at `0x47011B`. Wine
logged those blits and the primary-buffer update. At frame 60,
for example, the decoder word `0x4351` at (439, 97) also appeared
in the low 16 bits of the separate Xvfb window capture. The
post-submit capture matched 248,455 of 307,200 low words.
**UNCONFIRMED.** The cause of the remaining capture differences,
full-frame synchronization with the window surface and other
renderer or display formats. To settle the differences, stop at
`0x47011B` for one frame. Dump the locked movie surface and the
intermediate surface. Capture the window before the next decoder
call and compare all 307,200 words. Other formats need a display
that reports different masks to `0x409C70`.
