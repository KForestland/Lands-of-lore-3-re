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

**CONFIRMED.** Initializer `0x44A290–0x44A454` copies 40
stem pointers from `0x549980` to `0x629070`. The source occupies
`LOL3.DAT+0x148180–0x14821F`. The builder bypasses index 0 at
`0x44A763–0x44A767`. Hashing the template `MUSIC\%s.aud` (`0x549BC4`, case-normalized) from slots
1–39 joins 37 of the 38 directory entries across `MUSIC1–4`,
using 31 distinct keys. Several discs carry the same key. For
example, index 14 resolves to `uewoods0` and key `0xBD4CB6E0`,
at `MUSIC1.WSX+0x36`.

**CONFIRMED** (what is stored). **UNCONFIRMED** (a name for the
remaining key). Slot 9 is `uhfrozen` at `LOL3.DAT+0x148348`
(key `0x1D4F90DA`). Slot 11 is `uhfroze2` at `LOL3.DAT+0x148330`
(key `0x1D4F74DA`). Those are the only two `uhfroze` spellings in
`LOL3.DAT`. `LOL3.EXE` has none. The same ASCII bytes, the
upper-case bytes `UHFROZE` followed by `1`, and the UTF-16LE spelling `uhfroze1` are absent
from the 51 size-checked archives and from the shipped
`cdcache.wsx`. The four music archives hold 38 entries and 32
distinct keys. Thirty-one of those keys are `MUSIC\%s.aud` for
the alphanumeric stems other than `None` and `uhfroze2`, and
they cover 37 entries. The remaining key is `0x1D4F73DA`, the
directory dword at `music4.wsx+0x8A`. Its payload is
`music4.wsx+0x11FD49A`, 6,530,290 bytes. That key equals the hash
of the computed candidate `MUSIC\uhfroze1.aud`, and that spelling
is not stored.

Hashing every NUL-terminated printable ASCII string of 4–180
characters (a longer run is hashed as its last 180; 2,374 in
`LOL3.DAT`, 222 in `LOL3.EXE`, 3,701,411 in the 51 archives)
joins 53 path-like names to directory keys. Fifty-two of the
names are stored in `LOL3.DAT`. `LOL3.EXE` adds none. The other
name, `missing.aud`, is stored at `locallng.wsx+0x58C6636` and
`+0x58C6646`. Its key `0x2E02FD5E` is the 1,160-byte WAVE at
`LOCAL.WSX+0x240FF66` (directory row `+0x11A`). One further
printable run, at `LOCAL.WSX+0x147CF1F`, collides with a
directory key and has no separator and no extension, so it is
not a name. No stored string hashes to `0x1D4F73DA`. This search
hashes whole stored strings and the one computed name above; it
does not join other prefixes or suffixes and does not read UTF-16
strings. The hash upper-cases its input, so case does not matter.
A wider review search (runs of 3 or more characters, UTF-16LE runs,
path components, and twelve folder prefixes with seven extensions)
also found no name for the key.

`lol3_name_hash.py --check` re-counts the stems, the music join
and the stored-string hits. The stem table at `0x629070` is written
only by the initializer (`0x44A2A1–0x44A450`) and read only at
`0x44A775` and `0x44A7DD`. So slots 0–39 never build this key.
A stored spelling, for example in another release, is the settling
test. A run that stops at `0x44A7F5` with this key would also settle it. The 76
constructed level and global names stay with the WSX check.

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
