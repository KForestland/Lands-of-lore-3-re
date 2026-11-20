# Running the Windows 1.07a game on a current machine

Read this against your own copy. The notes below come from the programs and the setup files in one English tree, and from the strings those programs store. No game was launched for this page, so a setting is listed because a file names it, not because a play session scored it.

The program stores `Win95/NT 1.07a` at `LOL3.DAT+0x14DEAC`. The date `May  7 1999` is at `+0x14DE74`.

## Which programs are which

| File | What it is | Role |
| --- | --- | --- |
| `LOL3.EXE` | 77,824-byte MZ | The Windows launcher beside `LOL3.DAT`. The version string is not in this file. |
| `LOL3.DAT` | MZ stub, the game program | Holds `Win95/NT 1.07a`, the option names, and the driver names below. |
| `MSS32.DLL` | Miles sound library | Named from `LOL3.DAT+0x143660` as `mss32.dll`. |
| `LOLSETUP.INI` | Setup text beside the game | Processor, swap and CD rate. Not the video driver. |

## Display and the 3D driver

`options.ini` is named at `LOL3.DAT+0x14FA28`. The video keys in the program, and the value this tree's `options.ini` stores:

| Key | File offset | Value in this tree's `options.ini` |
| --- | --- | --- |
| `Video_Resolution` | `0x14F8F0` | `640x480x8` |
| `Video_3D_Driver` | `0x14F904` | `SoFtWaRe` |
| `Video_Variable_Frame_Rate` | `0x14F914` | `Yes` |
| `Video_Gamma_Correction` | `0x14F934` | `5` |
| `Video_Texture_Cache` | `0x14F954` | `Large` |
| `Video_Texture_Resolution` | `0x14F970` | `Low` |
| `Acceleration_Filtering` | `0x14F8D8` | `On` |

The resolution text is built with the format `%dx%dx%d` at `LOL3.DAT+0x144238`. One complete example stored in the program is `640x480x8` at `+0x144250`. Another file beside the game, `options_safe.ini`, stores `1024x768x32` and the driver `Glide/3Dfx: Voodoo Graphics`. That Glide sentence is in the program at `+0x149564`. The other Glide names there are `Glide/3Dfx: Banshee/Voodoo 3` (`+0x149514`), `Glide/3Dfx: Voodoo Rush` (`+0x149534`) and `Glide/3Dfx: Voodoo 2` (`+0x14954C`).

The software renderer name in the program is `SoFtWaRe` at `+0x144244`, the same spelling this tree's `options.ini` uses. Direct3D is the prefix `Direct3D: ` at `+0x149354`. The switches that follow it in the program are `-D3DUSEARGB4444`, `-D3DTBLENDADD`, `-D3DPERMEDIA2`, `-D3DNONSQUARE`, `-D3DFUZZYEDGES`, `-D3DNOVERTEXCOLOR` and `-D3DMONOLIGHTMAPS`. This page did not start the Direct3D path. The last recorded run of this copy used the software renderer, which is the `SoFtWaRe` value above.

## Sound

The audio keys are in the same options block:

| Key | File offset | Value in this tree's `options.ini` |
| --- | --- | --- |
| `Audio_Channels` | `0x14F9C8` | `16` |
| `Audio_Reverse` | `0x14F9AC` | `Off` |
| `Audio_Music_Type` | `0x14F990` | `Digital` |
| `Volume_SFX` | `0x14FA04` | `8` |
| `Volume_Music` | `0x14F9EC` | `8` |
| `Volume_Conversation` | `0x14F9D8` | `8` |

`LOLSETUP.INI` in this tree records a CD rate and a swap size. It does not name a sound card.

## Cache and the crash marker

The program names `cdcache.lst` at `+0x14DF48`, `cdcache.ls_` at `+0x14DFF0`, `cdcache.wsx` at `+0x14DFE4`, `cdcache.hdr` at `+0x14DFD8`, and `cdcache2.smf` at `+0x14DFFC`. The switch `-NOCDCACHE` is at `+0x147F88`.

In this tree `cdcache2.smf` is 9 bytes and the bytes are the text `The game `. That is the marker. This page did not reproduce the crash that leaves it, and it did not delete the file.

`LOL3.EXE` is the program to start. The video driver it will use is the `Video_3D_Driver` line in `options.ini`.
