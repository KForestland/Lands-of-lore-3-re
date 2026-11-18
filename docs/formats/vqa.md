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

**UNCONFIRMED.** Display pixel-format masks and end-to-end RGB
output are open. The tile callback writes packed u16 words.
To verify displayed colour, follow the destination pointer
passed at `0x512A9F–0x512AAF` to the surface format
negotiation and compare its masks with a known nonzero
word from the first CBFZ tile. The native uses of the
trailing reserved header words also remain open.
