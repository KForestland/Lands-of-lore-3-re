# How a LoL3 level is put together

A level uses a main archive for its map, object definitions, textures and light map. A second archive supplies level sound samples. The QWOD0 offsets below identify the actual inputs to the readers. [QWOD0 sheet](levels/QWOD0.md)

## Pieces

| Piece | QWOD0 witness | What the program uses |
|---|---|---|
| Geometry | MAP at `QWOD0.WSX+0x72E28B` | The MAP reader takes a 0x244-byte header at `0x43E7E7`. Header +4 points to vertices, +0x0C points to surfaces and +0xC8 points to waypoints. The reads include `0x43EAB2–0x43EB04` and `0x43EBD9–0x43EBF4`. [MAP sections](lol3-map-odf-readers.md) |
| Textures | TE_ at `QWOD0.WSX+0x36` | The packed texture bank has LZO1X chunks. The loader changes .tex to .te_ at `0x4E462C–0x4E463A`; its compressed reader calls the decoder from `0x4E47E9–0x4E4839`. [Texture wrappers](formats/textures.md) |
| Lighting | LMF at `QWOD0.WSX+0x68D913` | The LMF reader groups and expands the light-map members. The level loader calls it at `0x43E1BD`, and the directory read starts at `0x440B40`. [Light-map reader](lol3-lmf-reader.md#file-and-group-reader) |
| Definitions and placements | ODF at `QWOD0.WSX+0x774CF4`; five placement tables in the MAP | The ODF header is read at `0x43FC8D` and its field-3 reader takes 147-byte creature definitions at `0x4F0D7C–0x4F0DB0`. The MAP reader installs the placement rows separately. [MAP and ODF](formats/map-odf.md) · [Definition readers](lol3-map-odf-readers.md#creature-definitions-in-field-3) |
| Scripts | MAP event pools, group offsets, predicates and command streams | `0x43EA72–0x43EA9A` installs the object stream from header +0x44, and `0x43EA36–0x43EA60` reads its group offsets. The object matcher picks a command pointer through those offsets. [Script dispatch](lol3-object-dispatch.md) |
| Text | `DAT/locallng.wsx`, for example qevent.trr at `+0x5987786` | The journal initializer calls the shared ID-and-boundary reader at `0x433CD3–0x433D1B`. The dialogue display has a separate input at `0x454E10`. [Dialogue tables](lol3-dialogue-dispatch.md) |
| Sound | Level archive `QWOD0S.WSX`, sample at `+0x64886` | The level sample entries are RIFF WAVE. The sound path sends a resident sample buffer to the Miles import at `0x50763B`. [Level samples](formats/audio.md#level-sample-data) |

## Load order

1. **CONFIRMED.** The level loader appends the literal `S.wsx` from `LOL3.DAT+0x147F2C` at `0x43DAF3`. It probes the resulting name at `0x43DB23`. If found and allocation succeeds, the archive setup call at `0x43DB48` installs the returned pointer into the level context at `0x43DB51`. The same routine (`0x43D7B0`) then calls the resource routine `0x43DCF0` at `0x43DCB6`, so the sound archive is prepared before the main resource readers. [WSX lookup](lol3-wsx-reader.md)
2. **CONFIRMED.** On the path that reaches the retail resource readers successfully, texture preparation at `0x43E047` precedes the LMF call at `0x43E1BD`, the ODF call at `0x43E246` and the MAP call at `0x43E304`. The suffixes at `LOL3.DAT+0x147F7C`, `+0x147F74` and `+0x147F6C` name the LMF, ODF and MAP. The directory's record order is different from this call order. [Texture route](formats/textures.md#compressed-level-wrapper) · [Name-key witnesses](lol3-wsx-reader.md#resource-name-key)
3. Within ODF, the loader seeks to field 0, optionally reads field 20 and continues with fields 1, 2, 4 and 3 at `0x43FCD6`, `0x43FD09`, `0x43FD45`, `0x43FD76`, `0x43FDA7` and `0x43FDE2`. The MAP reader then installs geometry, events, script buffers and placements through its own seeks. For example the group-offset copy at `0x43EA36–0x43EA60` precedes the command copy at `0x43EA72–0x43EA9A`. [ODF and MAP seek order](lol3-map-odf-readers.md)
4. The shared TRR readers have their own entry points. An object opcode-0x16 command passes a tag to the sound and dialogue paths at `0x448237–0x448287`. Dialogue lookup reads the tag and then returns an ID-linked payload from the corresponding shared table. [Dialogue and script identifiers](lol3-dialogue-dispatch.md#script-identifiers-and-row-lookup)

**UNCONFIRMED.** The first sample payload needed on each successful level entry is still open. Follow the archive pointer stored at `0x43DB51` to the first named sample lookup that passes a buffer to `0x50763B`. That distinguishes preparing a sound archive from reading or playing a particular sample. When the shared TRR tables load relative to the level loader is also open: follow the callers of the journal initializer that reaches `0x433CD3` and compare them with `0x43D7B0`.
