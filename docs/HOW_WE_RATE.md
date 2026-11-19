# How we rate this repository

The README and [STATUS](STATUS.md) carry four counted lines instead of a
single percentage. `python3 tools/rating.py --data <DAT>` prints them from
your copy of the game and the pages; `--check` (part of `check_all.py`)
fails when the README or STATUS lines differ from the counts.

## The four lines

**Files read.** How many files in the game's `DAT` folder a reader in this
repository accounts for to the last byte, by count and by size. For a WSX
archive that means the directory, the entry sizes and the data area add up
to the file length with no overlap (`tools/extract_wsx_entries.py`). It
does **not** mean that every entry inside is decoded or understood; the
[STATUS](STATUS.md) table says how far each format is read. Files the game
writes while it runs (the full texture cache sits in the game folder,
next to `DAT`) are not part of this count. The shipped compact
`cdcache.wsx` does not parse as an ordinary archive, and the four `.PHT`
files have no known layout. These five files are **not** counted as read.
They are listed separately as repeated blocks: `tools/lol3_cache_seed.py`
shows the pinned 114-byte header plus 51 copies of one pinned
64,000-byte block fill `cdcache.wsx`, and `tools/lol3_pht.py` shows every
byte of each `.PHT` file is the pinned shared cycle of 0x1010000 bytes.
What those bytes mean and what reads or writes them stays open (Q1 for
the cache).

**Rules traced.** How many statements on the current pages carry the
evidence label CONFIRMED (backed by a program address or a file offset
that was checked) and how many carry UNCONFIRMED (a reading, with the test
that would settle it). Pages marked as history are left out. It counts
labels, not importance: one CONFIRMED may cover a whole table and one
UNCONFIRMED a single byte. It does **not** claim that unlabelled text is
wrong or that labelled text is complete.

**Seen in the running game.** Of the probes on
[NEEDS_A_RUNNING_GAME.md](NEEDS_A_RUNNING_GAME.md) (tests that the files
and the program text cannot settle alone), how many were answered by
running the original game. It counts probe headings under "Answered
probes" and "Remaining probes", not numbered questions: a question can
have more than one probe, and a probe need not belong to a numbered
question. Each answer holds for the setup it names (one
display, one renderer, one save). Most documented facts were never
observed in a running game; they are proved from the program and the files
instead, and this line does **not** count them.

**Open questions.** The state words of the At-a-glance table in
[OPEN_QUESTIONS.md](OPEN_QUESTIONS.md): answered, mostly answered, partly
answered. A question may be answered for one setup only; the table says so.

## What the rating does not say

It is not a measure of completeness and cannot be turned into one: the
four lines count different things and none of them has a known total for
"everything the game does". Older notes in this repository that gave a
percentage are kept as history and are marked so.
