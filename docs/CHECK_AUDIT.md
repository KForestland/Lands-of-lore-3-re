# Check audit

The 19 November 2026 audit used reviewed commit `2d8cd64` and the English retail originals with the existing cache and saves.
An untouched local clone passed the corpus checks and unit tests. In scratch clones
each case changed one value or deleted one file, ran the full `check_all.py`
and `python3 -m unittest`, then restored the file. The source installations
were read-only for the audit. The deliberate changes were never committed.

**Baseline result.** 11 of 20 changes failed at least one suite.
9 escaped both suites. Rows below describe the deliberate scratch errors.

| Case | Kind | File and deliberate change | Full corpus check that failed | Unit tests |
|---:|---|---|---|---|
| 01 | Generated page | `docs/NUMBERS.md`: first item disk +0x7D value from 3 to 4 | `lol3_numbers` | Passed |
| 02 | Generated page | `docs/NUMBERS.md`: first item record from +0x3A56 to +0x3A57 | `lol3_numbers` | Passed |
| 03 | Generated page | `docs/NUMBERS.md`: describe all offsets as decimal | `lol3_numbers` | Passed |
| 04 | Reader | `tools/lol3_map_spans.py`: expected waypoint byte +7 count from 2,067 to 2,066 | `lol3_map_spans` | Passed |
| 05 | Reader | `tools/lol3_wsx_writer.py`: expected loose WSX count from 2 to 3 | `lol3_wsx_writer` | Passed |
| 06 | Reader | `tools/lol3_script_framing.py`: native code bias from 0x400C00 to 0x400C01 | `lol3_script_framing`, `lol3_script_notes`, `lol3_level_report`, `lol3_progression`, `lol3_map_writer`, `lol3_combat_census`, `lol3_claimed_edges`, `lol3_name_hash`, `lol3_odf_companions`, `lol3_native_checks`, `lol3_save_writer`, `lol3_save_selectors`, `lol3_script_browser` | Passed |
| 07 | Reader | `tools/lol3_map_writer.py`: signed waypoint coordinates to unsigned | Passed | Failed |
| 08 | Reader | `tools/lol3_map_writer.py`: unsigned path bytes to signed | Passed | Passed |
| 09 | Reader | `tools/lol3_native_checks.py`: expected first texture copy mismatch count from 500 to 501 | Passed | Passed |
| 10 | Reader | `tools/lol3_save_writer.py`: global save sections from 61 to 60 | `lol3_save_writer` | Failed |
| 11 | Reader | `tools/lol3_cache_seed.py`: shipped seed header from 114 to 115 | `rating`, `lol3_cache_seed` | Failed |
| 12 | Format documentation | `docs/formats/wsx.md`: WSX directory start from +6 to +7 | Passed | Passed |
| 13 | Format documentation | `docs/formats/lmf.md`: LMF directory-offset field from +0x08 to +0x09 | Passed | Passed |
| 14 | Format documentation | `docs/formats/lmf.md`: LMF pool extent from +0x14 to +0x15 | Passed | Passed |
| 15 | Format documentation | `docs/formats/map-odf.md`: waypoint pointer from MAP +0xC8 to +0xC9 | Passed | Passed |
| 16 | Format documentation | `docs/formats/map-odf.md`: MAP section-1 field index from 1 to 3 | Passed | Passed |
| 17 | Format documentation | `docs/lol3-native-saves.md`: global save directory start from +0x4B8 to +0x4B9 | Passed | Passed |
| 18 | Deleted target | `docs/formats/wsx.md`: remove the WSX format page | `rating`, `doc_index`, `doc_links` | Passed |
| 19 | Deleted target | `docs/levels/README.md`: remove the level sheet index | `lol3_level_report`, `rating`, `doc_index`, `doc_links` | Passed |
| 20 | Narrative | `docs/HOW_THE_GAME_WORKS.md`: describe mana debit as a credit | Passed | Passed |

Escaped cases: 08, 09, 12, 13, 14, 15, 16, 17, 20.

## Checks added after the audit

- `doc_format_offsets.py --check` reads six sampled offsets from the format
  pages. For each one it builds a small synthetic file with a marker at the
  documented offset and asks the reader that decodes the field (the WSX
  directory parser, the LMF group walker, the section-1 listing, the MAP
  waypoint and path row readers and the slot header reader). A wrong page
  offset, or a reader that moved the field, fails. The check reports the
  affected page and field and is part of `check_all.py`.
- A synthetic path row keeps unsigned count and flag bytes above 127. The full
  suite now passes `--decode-copy` to the native check when liblzo2 is installed.
  That comparison reads the five flagged copy mips of each of the 18 shipped
  banks (90 mips).

The focused checks rejected all 8 automatable escapes in a second
scratch pass (cases 08, 09, 12, 13, 14, 15, 16, 17).
Case 20 remains outside automated coverage. The sentence changes the meaning
of a description while leaving the bytes, generated tables and links valid.
A reviewer can compare that sentence with the evidence it cites. The offset
check covers the named rows only.
