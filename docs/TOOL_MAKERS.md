# Next steps for tool makers

## Map viewer

`tools/extract_wsx_entries.py` finds archive members by key.
`tools/lol3_level_schematic.py` already joins the MAP vertex, surface,
waypoint, path and placement rows into an overhead drawing. To add
shading and materials, follow the LMF light-map group and texture
references through the documented readers. Treat the flagged texture
paths whose colour is still open as such in a preview.
[MAP header and record offsets](formats/map-odf.md) · [LMF](formats/lmf.md) ·
[Texture flags and colour](formats/textures.md)

## Map editor

`tools/lol3_wsx_writer.py` writes WSX directories and payloads.
`tools/lol3_map_writer.py` writes the typed MAP fields, including
framed script commands and the geometry fields behind the schematic.
It carries the other bytes as stored. Start with changes that keep table
sizes fixed. Adding or deleting rows needs a relocation pass for both
script streams, surfaces, regions, waypoints, placement indices and
the file's byte offsets. The LMF writer can re-encode groups. Editing
light maps or textures in place still needs a mapping from the changed
geometry to the associated resources and their indices. The mod kit
currently exposes ODF numbers and TRR fields.
[MAP fields and retained ranges](lol3-map-odf-readers.md#writing-the-stored-fields) ·
[LMF writer](formats/lmf.md#writing) · [Writer checks](ROUND_TRIP.md)
