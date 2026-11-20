# Unused content and development leftovers

The scope is the [English Windows 1.07a release](EDITIONS.md). The record counts describe the stored MAPs. The executable measurements describe the installed retail program.

## Bytes the level loader skips

**CONFIRMED.** Each of the 18 MAPs has a tail beginning at its header's `+0xC0` offset. The tails total 606,420 bytes. The largest begins at `JUNDR.WSX+0xF90748` and holds 104,044 bytes. The retail loader's 22 direct seeks and nested seek at `0x4EFE96` never select that offset. Every typed range ends at or before the tail. **UNCONFIRMED.** The record grammar in these tails and the original tool that consumed them. [MAP tail evidence](lol3-map-odf-readers.md)

## Opcodes absent from both shipped streams

**CONFIRMED.** The 18 MAPs hold 54,940 object commands and 4,040 region commands. Both streams together use 33 of the 39 values with a positive length in the program. Re-reading the length-table selector at `0x4E5790 + opcode − 1` and framing both streams finds no instance of the six values below. [Native opcode table](lol3-script-opcodes.md) · [Script notes and event reader](lol3-script-events.md)

| Absent command | Executable file offset of size selector | Native destination |
|---|---|---|
| `0x08` | `LOL3.DAT+0xE4B97` | Common object exit `0x4499EB`. |
| `0x0B` | `+0xE4B9A` | `0x448298` calls the return-only helper `0x4EED60`. |
| `0xC8` | `+0xE4C57` | `0x4E5A43` routes to the shared-array random-value store. |
| `0xC9` | `+0xE4C58` | `0x4E5A35` routes to the level-array random-value store. |
| `0xCD` | `+0xE4C5C` | Common map return `0x4E5A77`. |
| `0xD1` | `+0xE4C60` | `0x4E5A5F` routes to the region-group resolver. |

## Development options and files

- **CONFIRMED.** `-CONVERT_TEST` is stored at `LOL3.DAT+0x147FAC`. The MAP loader tests it at `0x43E7F4` and can accept a header that fails the usual leading-word and surface-count tests. Five other operands refer to the same switch, at `0x43F742, 0x43FC96, 0x44051B, 0x440608, 0x440BCE`. The texture and definition readers still impose their following bounds checks. [MAP and ODF startup](lol3-map-odf-readers.md) · [Shared and editor texture paths](lol3-texture-palette-sources.md#shared-retail-banks-and-the-editor-path)
- **CONFIRMED.** Four graphics options can set the flag that skips an RGB555 candidate at `0x495072`. The strings are `-D3DUSEARGB4444`, `-D3DPERMEDIA2`, `-D3DNOVERTEXCOLOR` and `-D3DMONOLIGHTMAPS`, respectively at file `+0x149360, +0x149380, +0x1493B0, +0x1493C4`. The immediate and indirect setters are at `0x472AC1–0x472AD8` and `0x472A6A–0x472A79`. [Texture selection](lol3-texture-bake.md)
- **CONFIRMED.** The literal `-NO_ASSERTS` occurs at file `+0x1520FC`. Its operand at `0x5077AF` reaches the argument lookup at `0x434890`. A match jumps from `0x5077BE` to the return at `0x507860`, skipping the report and termination path at `0x5077CD–0x50785D`.
- **CONFIRMED.** The PE debug directory at file `+0x170` locates three debug payloads beyond the final file-backed program section. They begin at `+0x17F400, +0x17F510, +0x1911E0`. The last carries an NB10 marker and a PDB filename at `+0x1911F0`. [PE extents](formats/executable.md)
- **CONFIRMED.** Four loose PHT files are byte-for-byte prefixes of a repeated stream. The generator is identified at `LOL3.DAT` VA `0x51B655`. **UNCONFIRMED.** Which program wrote these files and whether the retail game ever opens them. [PHT evidence](formats/pht.md)
