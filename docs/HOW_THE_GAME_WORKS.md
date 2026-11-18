# How Lands of Lore III works

This guide follows the original Windows game from opening its archives to saving your progress. The steps below describe confirmed behavior. The linked pages give examples and the original file offsets or program addresses.

## Starting up and finding files

Shared resources live in `GLOBAL.WSX`. A WSX archive has a directory that describes where each file starts and how long it is. The directory uses a numeric key made from the file's name. To find a resource, the engine calculates that key and searches the sorted directory.

The game uses the same kind of directory in the level archives. For example, the path for the CKEEP light map produces a key that matches the directory entry in `CKEEP.WSX`.

Details and evidence. [Archive reader](lol3-wsx-reader.md#wsx-directory) · [How names become keys](lol3-wsx-reader.md#resource-name-key)

## Loading a level

The level's MAP file supplies points, surfaces and links between surfaces. It also gives the engine waypoints, positions that creatures can step through on a path. The ODF file supplies definitions, including records that the creature constructor uses.

The level also has compressed texture and light-map data. The engine expands the texture bank in blocks and uses palettes to turn indexed texture pixels into colours. The light maps have their own directory and are unpacked in groups.

Details and evidence. [MAP and ODF readers](lol3-map-odf-readers.md) · [Texture banks](formats/textures.md#compressed-level-wrapper) · [Colours](lol3-texture-bake.md) · [Light maps](lol3-lmf-reader.md)

## Running scripts

A level has separate lists of region and object events. Each entry describes the kind of event and helps the engine find its command group. A following predicate can make the group conditional. For example, a predicate can check a value shared by scripts.

An object can also have a timer that counts down as the frame clock advances. When a command group runs, the first byte of each command tells the engine what operation to perform and how long the command is. For example, an object command can grant an item. The original command lengths account for the script streams in all 18 levels.

Details and evidence. [Event lists, shared state and frame clock](lol3-script-events.md) · [Opcode table](lol3-script-opcodes.md) · [Follow one event](tutorial-one-event.md)

## Picking up and using items

The shared item table describes the different kinds of items. The game looks up an item definition by its ID when a script grants an item. The inventory holds live items, each of which refers back to a definition.

The use routine can take an item from an inventory slot or from the cursor. The item's definition determines which routine receives the request. Most items go to the handler their definition names; spells and some special items all go to one shared handler.

Details and evidence. [Definitions and script grants](lol3-item-dispatch.md#definition-directory) · [Inventory and use](lol3-item-dispatch.md#use-effects)

## Casting spells

Each of the five spell slots (two key bindings each) sends a request through the item-use routine, and spell definitions reach its special handler. The definition supplies the initial mana cost. Some equipped items can reduce that cost for certain spells.

The normal cast path checks the adjusted cost against the player's mana. After a successful effect, the game subtracts the debit and updates the display. The effect itself can create an object that applies a hit, which then enters the combat routines.

Details and evidence. [Casting and cost](lol3-spell-dispatch.md#player-cast-and-cost) · [Effects and hits](lol3-spell-dispatch.md#effect-object-and-first-hit)

## Creature decisions and combat

A creature's current behavior selects the routine to run during its update. That routine can use its target or a waypoint and change its behavior and animation. Besides its behavior, a creature has a second "action" value with its own routines.

Some attacks send their hit request when the animation reaches a particular frame. The hit resolver works from the request's amount and flags, applies relevant modifiers and passes the result to the target's health update.

Details and evidence. [Creature modes and animation attacks](lol3-combat-dispatch.md#behavior-and-action-modes) · [Hit requests and health](lol3-combat-dispatch.md#creature-definitions-and-target-quantity) · [Animation hits](lol3-combat-dispatch.md#creature-animation-hits-and-resolver-multipliers)

## Playing movies and sound

The game can turn a movie number into an `outtakes` name and look it up in its archives. The VQA reader follows an index to each frame. A frame uses small blocks of picture data from a codebook. The movie format also stores sound chunks for the movie's own audio decoder.

Level sound effects and music are separate audio files. The music path hands a stream to the Miles sound library. The level sample path hands the library a loaded sound buffer and can set volume, pan and looping.

Details and evidence. [Movie lookup, frames and audio](formats/vqa.md) · [Music and level sound](formats/audio.md)

## Saving and loading

The game writes a slot name and version stamps at the start of a save. The header gives the preview's size and location, the current level, and positions for the game-wide sections and separate level blocks. The reader checks version stamps before loading the saved sections.

Some sections are compressed in small chunks. For some game-wide sections, the writer also compares the current bytes with a base image and stores the difference using XOR. A level block has its own directory, so the loader can find its individual saved sections.

Details and evidence. [Slot header and game-wide sections](lol3-native-saves.md#slot-header-and-stream) · [Level blocks and compression](lol3-native-saves.md#level-blocks-and-chunking)
