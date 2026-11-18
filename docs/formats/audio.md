# Music and level sound

## Music streams

**CONFIRMED.** The four MUSIC archives hold 38 RIFF WAVE entries
with format `0x55`. Their `fmt ` chunks describe two channels,
44,100 Hz, 16,000 bytes per second, alignment 1 and a
12-byte format extension. In every entry the first two `data`
frames carry an MPEG-1 Layer III header with 128 kb/s and 44,100 Hz.
The distance from the first header to the second is 417 bytes
plus the padding bit. In `MUSIC1.WSX+0x36`, the format tag
at `+0x4A` is `55 00`. The first frame begins `FF FB 90 44`.

**CONFIRMED.** The native music caller selects a stem from
`0x629070` and formats `MUSIC\%s.aud`
(`LOL3.DAT` VA `0x44A763–0x44A783`, string at file
`+0x1483C4`). A score-directory override formats
`%s\\%s.wav` at `0x44A7CA–0x44A7EC`. After resolving the
resource, `0x44A8E8 → 0x4715A0 → 0x50B080` reaches the
imported Miles `AIL_open_stream` at `0x50B142`
(IAT `0x5382E4`, import name at `LOL3.DAT+0x14364C`).
The caller passes a filename and configures the playback volume
and pan before starting the stream (`0x50B135–0x50B1FA`).

**UNCONFIRMED.** The native path templates above do not identify
all of the MUSIC archive keys. The stem pointer array at
`0x629070` has no on-disk image. A trace of its initializer or
a resolved score-resource name at `0x44A7F5` would settle that join.

## Level sample data

**CONFIRMED.** The 18 level sound archives hold 6,696
RIFF WAVE entries. All use IMA ADPCM tag `0x11`, 4 bits per
sample and 22,050 Hz. Mono has 512-byte blocks and rate
11,100 bytes/s (6,596 entries), stereo 1,024-byte blocks
and rate 22,201 bytes/s (100 entries). Both give 1,017
sample frames per block by
`1 + 2 × (block bytes − 4 × channels) / channels`.
For example, `QWOD0S.WSX+0x64886` holds a mono sample
whose format extension ends in `02 00 F9 03` (extension
size 2 and sample-frame count 1,017). The native sample path
passes the resident file buffer to the Miles
`AIL_set_sample_file` import at `0x50763B`
(IAT `0x5382D8`, `LOL3.DAT+0x143602`), then sets
pan, volume and looping at `0x5076BC–0x5076E2`.
Movie audio has a separate native decoder, described in [VQA movies](vqa.md).

Run `python3 tools/lol3_media_check.py --data DAT --check`
to check movie identity, frame indexes and both audio corpora in place.
