# Script and event dispatch in the native image

The addresses in this page refer to the English retail `LOL3.DAT`
PE32. Subtract `0x400C00` for an instruction's file offset. The
[PE identification](lol3-lmf-reader.md) gives the executable hash.

## Measured candidates

- **CONFIRMED.** The level-load call at `0x43E304` passes the name
  formed with the `.map` string (file `0x147F6C`, VA `0x43E293`).
  The callee reads a 0x244-byte header and checks dword 38 on the
  ordinary path (`0x43E7E7–0x43E80B`). It seeks to a header-provided
  offset and reads the next 0x218-byte block at `0x43E884–0x43E89A`.
  The corresponding ODF loader at `0x43FC40` opens the name produced
  from file string `.odf` (`0x147F74`, call at `0x43E246`).
  ODF reader `0x4F0CE0` consumes 135-byte bodies with 12-byte type tags
  and resolves the tags at `0x4F0D86–0x4F0DA9`.
- **CONFIRMED.** The filename check at `0x519B11` tests `.cmd` next to
  `.exe`, `.bat` and `.com` (strings at file `0x1400E4–0x1400FC`).
  It returns a mode bit at `0x519B47` and does not consume file contents.
  This rules out that particular `.cmd` reference as a bytecode reader.
- **CONFIRMED.** At `0x4FD963–0x4FDA0E`, the initializer builds a
  `global\ai\%s` path and passes `stat.csv`, `goals.csv`,
  `actions.csv` and `effector.csv` to `0x4FD780`. Their strings start
  at file `0x1503BC`. The callee opens the files, walks CR/LF rows and
  commas, calls a decimal conversion, and stores cells as bytes
  (`0x4FD7E3–0x4FD8C8`). The four uppercase native path hashes have no
  directory match in the original `DAT/GLOBAL.WSX` or either
  `LOCAL.WSX`. The table's file origin and runtime selection remain open.
- **CONFIRMED.** The six-entry jump table at VA `0x4E2984` (file
  `0xE1D84`) is reached by a bounded dword at caller-owned +0x14
  (`0x4E245F–0x4E246B`). Five slots land at `0x4E2472` and slot 2
  at `0x4E24D6`. Both use fields of the same live packet.
  In particular, the latter combines packet +0x1C with the +0xFC
  virtual returns of the two object pointers (`0x4E24D6–0x4E250C`).
  Call site `0x4465A8` gives the live packet and immediately applies
  the difference of +0x2C from the old amount through an object method.
  This switch establishes a live-object calculation. Its input has no
  demonstrated link to an archive script record.

## What would settle script dispatch

**UNCONFIRMED.** A program counter, a script record frame and a table
whose selector comes from the original level stream remain unbound.
The checks above followed the obvious file-extension lead, bounded
one native indexed dispatch and found the CSV reader. The level map
loader is the best next input source. Use a known CKEEP object/action
pair, follow its load through the section directory at
`0x43E884–0x43E89A`, then match an archive byte offset to the native
load of a selector and to a handler or a virtual event method.
