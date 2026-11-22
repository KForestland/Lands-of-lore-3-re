# How we rate this repository

The README and [STATUS](STATUS.md) carry five counted lines instead of a
single percentage. `python3 tools/rating.py --data <DAT>` prints them from
your copy of the game and the pages; `--check` (part of `check_all.py`)
fails when the README or STATUS lines differ from the counts.

## The five lines

**Files read.** How many files in the game's `DAT` folder a reader in this
repository accounts for to the last byte, by count and by size. For a WSX
archive that means the directory, the entry sizes and the data area add up
to the file length with no overlap (`tools/extract_wsx_entries.py`). It
does **not** mean that every entry inside is decoded or understood; the
[STATUS](STATUS.md) table says how far each format is read. The count
looks only at the files directly inside `DAT`. The files the game writes
while it runs (the full texture cache next to `DAT`, the saves in
`SAVEGAME`) are outside that folder, so playing the game does not change
the count. The shipped compact
`cdcache.wsx` does not parse as an ordinary archive, and the four `.PHT`
files have no header, directory or entries: their bytes are a generated
stream ([PHT](formats/pht.md)). These five files are **not** counted as read.
They are listed separately as repeated blocks: `tools/lol3_cache_seed.py`
shows the pinned 114-byte header plus 51 copies of one pinned
64,000-byte block fill `cdcache.wsx`, and `tools/lol3_pht.py` shows every
byte of each `.PHT` file is the pinned shared cycle of 0x1010000 bytes.
What those bytes mean and what reads or writes them stays open (Q1 for
the cache).

**Rules traced.** How many statements on the current pages carry the
evidence label CONFIRMED (backed by a program address or a file offset
that was checked) and how many carry UNCONFIRMED (a reading, with the test
that would settle it). Pages marked as history are left out. The glossary defines the label words; its labels are not counted. It counts
labels, not importance: one CONFIRMED may cover a whole table and one
UNCONFIRMED a single byte. It does **not** claim that unlabelled text is
wrong or that labelled text is complete.
Two samples of 30 CONFIRMED statements, taken by different rules, were re-derived from the bytes ([samples](CONFIRMED_SAMPLE.md)). First sample: 24 held, 6 held in part, none wrong. Second sample: 15 held, 12 held in part, 3 corrected (2 wrong, 1 overstated). Four statements first picked for both lists were replaced in the second, so 60 different statements were checked. A further sample on 21 November re-derived ten more statements. [November 21 sample](CONFIRMED_SAMPLE.md#independent-checks-on-21-november-2026)

**Seen in the running game.** Of the probes on
[NEEDS_A_RUNNING_GAME.md](NEEDS_A_RUNNING_GAME.md) (tests that the files
and the program text cannot settle alone), how many were answered by
running the original game. It counts probe headings under "Answered
probes" and "Remaining probes", not numbered questions: a question can
have more than one probe, and a probe need not belong to a numbered
question. Each answer holds for the setup it names (one
display, one renderer, one save). Most documented facts were never
observed in a running game; they are proved from the program and the files
instead, and this line does **not** count them. Probes listed under "Probes not yet run" are not counted in either number.

The same line says how many answered probes rest on edited saves only.
An edited save is a copy of a game-written save with a few bytes
changed by hand; [edited saves](EDITED_SAVES.md) lists each such run.
An answered probe counts here when its section says "edited-save run"
and none of its bold labels says "answered" without "edited-save". A
label like that marks a run on a save the game wrote itself. A probe
that is still open is not counted, even when an edited-save run added
evidence to it.

**Open questions.** The state words of the At-a-glance table in
[OPEN_QUESTIONS.md](OPEN_QUESTIONS.md): answered, mostly answered, partly
answered. *Answered*: nothing is left to settle from the files or the
program. *Mostly answered*: the main question is settled; named details
remain. *Partly answered*: part is settled; the main point is open. A row
that says 'answered for' a setup (one renderer, one device) counts as
answered for that setup only.

**Page facts.** The scanner counts offsets, names and numbers in passages
marked as proved, in measured examples, and at the registry's explicit anchors.
On 22 November 2026, the tool registered independent checks for 54 of 8,341
candidate literals (0.65%).
Registered witnesses independently read the named original files. The scanner
recognizes quoted bytes or strings at file offsets, loose-file sizes, counts
from named check commands, named literals in original files, and absolute
instruction operands. It also checks supported record-size arithmetic for
consistency. Run
`python3 tools/page_facts.py --check --data DAT` to compare those values or
`python3 tools/page_facts.py --list` to see the prose-only claims and their reason.
The prose inventory flags changes for review. Its fingerprints do not establish
what the bytes say. After verifying a documentation change, review the output
of `python3 tools/page_facts.py --inventory` before recording the revised inventory.
Handoffs list the changed proved lines, and the reviewer re-derives each one before merging.

## What the rating does not say

It is not a measure of completeness and cannot be turned into one: the
five lines count different things and none of them has a known total for
"everything the game does". Older notes in this repository that gave a
percentage are kept as history and are marked so.
