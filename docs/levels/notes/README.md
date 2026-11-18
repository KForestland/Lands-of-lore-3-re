# Level script notes

These 18 summaries measure the object and region streams and their
event pools in the original retail archives. The single
[CKEEP excerpt](CKEEP.excerpt.md) illustrates the output format.
The [native event reader](../../lol3-script-events.md) gives
the stream offsets and matcher evidence, and the
[opcode reference](../../lol3-script-opcodes.md) gives the size
decoder and native switch destinations.

Full listings are generated from a local game installation. A separate
file is written for each level and stream to a directory outside the
checkout and the game.

```text
python3 tools/lol3_script_notes.py --data DAT --out DIR    # a folder outside the repository
python3 tools/lol3_script_notes.py --data DAT --check
```

The listing has one line per physical script record. The *When*
clause includes each direct event row and a following predicate
guard where present. The *Does* clause describes the native actions
in stream order, including the commands counted by an initial
0xF0 header. The *Touches* clause shows directly decoded targets.
Positions are absolute offsets in the original WSX. Repeated object
index entries are shown as aliases on the same line. A line with
**UNCONFIRMED** producer has no direct reference from either event
pool for that stream. An identifier tag or a text payload is never
printed.

**CONFIRMED.** The object runner gets its position from the
MAP +0x4C u32 offset index at `0x4A8290–0x4A82A6`. The
region walker passes a byte offset into its command stream at
`0x4AC450–0x4AC45D`. In all 18 archives, 16,876 object
references and 2,201 region references resolve to a framed
boundary. The opcode switch at `0x41EDF9` supplies the selector
roles. The region arms that use u16 +2 for the region lookup are
at `0x4E5D30` and `0x4E5EC0`. A class's virtual dispatch
can add effects that are **UNCONFIRMED** in the listing.

## Summaries

- [BUPP1](BUPP1.md)
- [CKEEP](CKEEP.md)
- [DLOW1](DLOW1.md)
- [EWOD1](EWOD1.md)
- [FLAIR](FLAIR.md)
- [GRULO](GRULO.md)
- [HWHIT](HWHIT.md)
- [ISHAT](ISHAT.md)
- [JUNDR](JUNDR.md)
- [KVOLC](KVOLC.md)
- [LUPP2](LUPP2.md)
- [MLOW2](MLOW2.md)
- [NWOD2](NWOD2.md)
- [OLOW3](OLOW3.md)
- [PWOD3](PWOD3.md)
- [QWOD0](QWOD0.md)
- [RVOL0](RVOL0.md)
- [SWOD4](SWOD4.md)
