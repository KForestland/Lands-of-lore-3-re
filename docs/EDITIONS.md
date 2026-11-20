# Identify your edition

Run this from the downloaded tools folder. Replace the example with the path to your own installation or its data folder. The command reads names, sizes and checksums and reports whether they match a measured copy. Each file is marked `matches`, `differs` or `missing`.

```sh
python3 tools/edition.py --data "/path/to/your/LoL3"
```

In Windows PowerShell, use `py -3` in place of `python3`, for example `py -3 tools/edition.py --data "C:\Games\LoL3"`. Requires Python 3.10 or later and the standard library.

Set `$LOL3_DAT` to the same folder to omit `--data`. Add `--check` to verify the complete fingerprint in one line.

## Measured files

**CONFIRMED.** Byte counts and SHA-256 cover every byte from file offset `+0x00` to EOF. File names start in the installation folder. `DAT/` marks files inside that subfolder.

### English GOG release, 1.07a

| File | Bytes | SHA-256 |
|---|---:|---|
| `LOL3.DAT` | 1,643,520 | `9a9eb04c8f404ebf68f439df4ec7dc6ad5cc230235d0f853059f636ff720ccea` |
| `LOL3.EXE` | 77,824 | `47653b3971fd623cde6c15bc29ec063d3b3ce26d500887f1c6c60abedcc81bc6` |
| `LOCAL.WSX` | 39,557,829 | `ee7d077af31aad4e3180562ae1be73a6b1c7d18be7ffc67556b24399ddfcca8c` |
| `DAT/LOCAL.WSX` | 39,557,829 | `ee7d077af31aad4e3180562ae1be73a6b1c7d18be7ffc67556b24399ddfcca8c` |
| `DAT/GLOBAL.WSX` | 8,521,360 | `8dee4f4fdbc30b018958259c4a026f490044d01567f7cb6d73552545b4c517a9` |
| `DAT/QWOD0.WSX` | 7,832,695 | `23bd769621be5e0de334c63cc01bc1eb56c4027fdcb590ef3d1635ce014c64c2` |

## Build strings and comparison

- **CONFIRMED.** `LOL3.DAT+0x14DEAC` holds `Win95/NT 1.07a`. `+0x14DE74` holds `May  7 1999` and `+0x14DE68` holds `11:09:31`. Its PE COFF timestamp at `+0xD0` is `0x37332C6E`, or 1999-05-07 18:09:50 UTC. The string gives no time zone. [Program layout](lol3-lmf-reader.md)
- **CONFIRMED.** The separate launcher `LOL3.EXE` has COFF timestamp `0x36DAF75F` at `+0xE8`, or 1999-03-01 20:23:59 UTC. The separate video component string in `LOL3.DAT+0x154F28` identifies VQA 5.0 and includes `Apr 29 1999 10:27:10`.
- Other releases have **not been measured here**. The loose `LOCAL.WSX` and `DAT/LOCAL.WSX` have the same size and full SHA-256. The fingerprint excludes the shipped seed `DAT/cdcache.wsx`, the game-written cache beside `DAT` and saved games. [WSX archives](formats/wsx.md)
