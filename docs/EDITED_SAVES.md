# Runs on edited saves

Some probes on [NEEDS_A_RUNNING_GAME](NEEDS_A_RUNNING_GAME.md) need an
item that no game-written save had in reach. For those, a copy of a save
the game wrote was changed by hand and loaded in the original English
retail 1.07a game.

An edited save shows what the original program does with that state. It
does not show that ordinary play reaches the same state. A native save
(one the game wrote during normal play) is still needed for that. The
rules an edit must keep (saved pointer ranges, re-encoded chunk lengths,
directory starts, version stamps, no separate checksum) are in
[editing a copy of an original slot](lol3-native-saves.md#editing-a-copy-of-an-original-slot).

The one run below belongs to a probe that is still open. It does not
answer the probe on its own; the [rating](../README.md#rating) counts how
many answered probes rest on edited saves only.

## Q12. The second spell counter

- **Question:** which live cast consumes an alternate resource?
  ([probe](NEEDS_A_RUNNING_GAME.md#q12-which-live-cast-consumes-an-alternate-resource))
- **Edited:** two new item rows (Ancient's Stone and Mana Cluster) put
  in the first two pockets, and two cast keys pointed at spells `0x59`
  and `0x54`
  ([byte table](lol3-spell-dispatch.md#casts-with-edited-quick-slots)).
- **Showed:** Ancient's Stone added a first-counter charge and spell
  `0x59` spent one. Mana Cluster added a second-counter charge at
  `0x4A6133`. Spell `0x57` then took the second counter from 1 to 0 at
  `0x432AE0`. The watch on ordinary mana spending had no hit for that
  cast. The game later wrote its own
  autosave from that state.
- **Loaded again (2026-11-20):** the same edited copy
  (`90099b161497`, no further bytes changed), with two live edits in
  the cache initializer. The three casts gave the same results; the
  items were not used
  ([record](NEEDS_A_RUNNING_GAME.md#probes-not-yet-run), under
  "Remaining native casts").
- **A native save would add:** the item taken in ordinary play (the
  [DLOW1 try](lol3-spell-dispatch.md#dlow1-approach-with-the-native-placement-live)
  could not reach it), and the exact counter shown on the HUD.

## See the fields in an offline page

Run from the tools repository with Python 3.10 or newer. Use a fresh HTML
file outside the game and save folders.

```sh
python3 tools/lol.py save page '/path/to/your/original save' --out "../my save fields.html"
```

Open the page in your browser. It displays the current values and the evidence
status for each editable field. Choose your terminal and a new save path outside the repository and save folder.
Enter a different value in the field and copy the command that appears.
Headings are shown in hex. You can enter hex or decimal. Run the
command from the tools repository. It writes one edited copy. For a second edit
to the same save, generate a page from the first copy and choose another output
filename. Keep the page private because it contains your save name and path.

**CONFIRMED.** The page reads the slot name from `+0x00`, level ID at
`+0x498` and player group at `+0x49C`. See
[the documented save layout](lol3-native-saves.md).
