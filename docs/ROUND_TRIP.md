# Round-trip proof for LoL3

Five writers read the original files, build a replacement in memory and compare it with the original. Nothing is written to disk. "Byte-identical" means the rebuilt file equals the original file. "Decode-identical" means the rebuilt compressed data reads back to the same bytes as the original, while the compressed bytes themselves differ.

| Writer | What is rebuilt | Comparison | Counts (GOG copy that has run, with saves) |
|---|---|---|---|
| `lol3_wsx_writer.py` | WSX archives from their parsed rows | Byte-identical | 51 DAT archives and the loose `LOCAL.WSX` and `locallng.wsx`, 7,614 rows; `cdcache.wsx` left out |
| `lol3_lzo_writer.py` | LMF light maps and `.TE_` texture banks, re-compressed with liblzo2 | Decode-identical; all 18 rebuilt light maps differ from the files | 424,288 LMF members in 5,256 groups; 465 texture blocks in 18 banks |
| `lol3_lzo_writer.py` | Packed SMD frames in `SLICECD1`–`4.WSX`, re-compressed with liblzo2 | Decoded bytes only; the frames are not written back into an archive | 15,990 distinct frames from 33,068 packed references in the 18 level banks and the two shared banks |
| `lol3_save_writer.py` | Game-written save slots from their fields | Byte-identical; the stored LZO packets are copied, so no compressor is tested | 47 slots, 416 level blocks, 59,654 packets (your saves give other counts) |
| `lol3_map_writer.py` | The 18 level MAPs from their command, waypoint, path and placement fields and the native-read fields of the header, geometry, region, predicate and event tables | Byte-identical; 15,822,119 of 21,232,680 bytes come from fields with a native read and the other 5,410,561 are copied as stored, listed by range with `--coverage` | 54,940 object and 4,040 region commands, 2,384 waypoints, 36 paths, 23,850 placements |
| `lol3_text_writer.py` | TRR text and tag tables from their parsed IDs and fields | Byte-identical; count, IDs, boundary table and NUL terminators are regenerated, field bytes come from the parsed rows | 53 tables: 26 members in each of the two identical `locallng.wsx` and the loose `PROMPT.TRR` (26 distinct); 26,170 rows counting every copy |

## WSX archives

**CONFIRMED.** The writer emits the u16 entry count at +0, the u32 data size at +2, the 12-byte rows from +6 in their stored order (key, offset from the start of the data, size), then the entries in offset order. Every archive comes out byte for byte equal to the file. A member changed in memory moves the later offsets and reads back with the change. `cdcache.wsx` is written by the game and has its own layout, so it is left out. [WSX layout and writing](formats/wsx.md#writing)

## Light maps and texture banks

**CONFIRMED.** For an LMF, the writer expands each stored group, compresses it again with liblzo2's `lzo1x_1_compress`, and writes the new group lengths (the low 18 bits at the group's first row), the member offsets and the pool size at +0x14. The header up to +0x100 and the directory size at +0x10 are kept, so the pool starts at the same offset. Each group must read back to the same members at the same boundaries. For a `.TE_` bank, the writer keeps the expanded total at +0, writes each new block length before its block and ends with a zero length, the stream the reader at `0x4E47E9–0x4E4839` walks. This proves that the format can be written, not that the game's own compressor is reproduced: the new packed bytes differ from the original in every group. [LMF writing](formats/lmf.md#writing) · [LMF group reader](lol3-lmf-reader.md#file-and-group-reader) · [Texture wrapper](formats/textures.md#compressed-level-wrapper)

## Packed SMD frames

**CONFIRMED.** The writer walks the descriptor and mip directories of each expanded level bank and of `GLOBAL\GLOBAL.TEX` and `GLOBAL\SPELL.TEX` in `LOCAL.WSX`. A mip whose flags mark an SMD frame reference carries, at record +0xC, the SMD name at +0x10, the offset at +0x20, the expanded length at +0x24 and the stored length at +0x28. A nonzero stored length is the compressed path at `0x4E1588–0x4E159F`. The writer follows each packed reference into its `SLICECD1`–`4.WSX` member, re-compresses the bytes after the 16-byte frame prefix and reads them back. The shipped banks hold 33,068 packed references to 15,990 distinct frames, so the proof needs no game-written cache. When the game-written `cdcache.wsx` is present, its 4,428 packed references are followed too and reach no further frame (its 4,429th SMD reference has stored length zero and is read directly). [SMD references and worked example](lol3-texture-bake.md#smd-slice-frame-references)

## Save slots

**CONFIRMED.** The writer reads each slot into fields and writes it again. It regenerates the file length at +0x2C, the 61 global section offsets at +0x4B8, and the 18 level start offsets and lengths at +0x5B0 and +0x600. Each level block gets its 0x34C-byte header with the 75 section starts at +0xF4 and expanded lengths at +0x220. A section is split into packets when its selector flag, read from the descriptor tables behind `0x438140` and `0x438940` in `LOL3.DAT`, has bit 4. Each packet gets its two u32 lengths back and keeps its stored LZO bytes. Unnamed header bytes and raw sections keep their contents. With liblzo2 each packet must also expand to its stored expanded length. A player-x change made in memory alters only its 4 bytes and reads back through `lol3_save_header.py`. [Slot header](lol3-native-saves.md#slot-header-and-stream) · [Level blocks and chunking](lol3-native-saves.md#level-blocks-and-chunking) · [Selector payloads](lol3-native-saves.md#selector-payloads)

## MAP rows and commands

**CONFIRMED.** The writer frames both command streams with the 39 opcode sizes from `LOL3.DAT` and writes back each command's opcode, selector, index and typed operands, the 8-byte waypoint rows, the 4-byte path rows, every placement's X/Z words and the mover's eight state bytes. It also writes back the header words, vertex, section-1, +0x34 and +0x30 rows, the object command index, predicates, level bytes, and the surface, region, settings, +0x2C, +0x48 and event fields whose stored value a native instruction reads. Everything else (5,410,561 bytes) is copied as stored: operand and row bytes without a known read, the other placement bytes, the 11,496-byte shared block, the waypoint and path labels, the 1,784-byte surface-to-script gap and the remaining unparsed sections. So the check proves the framing and the read widths, not the meaning of the copied bytes. A change to one command operand, one waypoint, one vertex and one placement made in memory alters only those bytes and reads back through `lol3_script_notes.py` and `lol3_level_schematic.py`. `--list STEM` gives offsets, sizes and SHA-256 of the four named copied spans and `--coverage STEM` lists every retained range by MAP and WSX offset, never their bytes. [Byte table](lol3-map-odf-readers.md#writing-the-stored-fields)

## Text tables

**CONFIRMED.** A TRR is a u32 count, the u32 IDs, then count + 1 u32 boundaries (counted from +4), then the NUL-terminated fields. The writer rebuilds the whole table from (ID, field) rows; IDs may repeat and be out of order. It finds the TRR-shaped members of both `locallng.wsx` copies and the loose `.trr` files, and stops unless there are 53 and the four quest and dialogue tables are among them. A field changed in memory changes the length and the later boundaries and reads back through the same directory reader `lol3_media_check.py` uses (synthetic test). [Writing the stored tables](lol3-dialogue-dispatch.md#writing-the-stored-tables)

## Run the checks

```bash
python3 tools/lol3_wsx_writer.py --data "$LOL3_DAT" --check
python3 tools/lol3_lzo_writer.py --data "$LOL3_DAT" --check
python3 tools/lol3_save_writer.py --data "$LOL3_DAT" --check
python3 tools/lol3_map_writer.py --data "$LOL3_DAT" --check
python3 tools/lol3_text_writer.py --data "$LOL3_DAT" --check
python3 -m unittest tests.test_round_trip tests.test_map_write tests.test_text_write
```

All five run in `tools/check_all.py`. Without liblzo2 the LZO and save writers print SKIP. Without the game-written cache the LZO check still runs in full on the shipped banks and says the cache was not followed; give `--cache PATH` for a cache stored elsewhere. Without game-written saves the save writer checks a synthetic slot and reports SKIP. The unit tests use synthetic archives, light maps, banks, slots, MAPs and TRR rows and need no game files.
