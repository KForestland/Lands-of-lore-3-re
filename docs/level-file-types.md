# LoL3 level companion types (from LOL3.DAT strings)

Per-level assets referenced by the engine:

| Ext | Role (working hypothesis) | CKEEP candidate |
|-----|---------------------------|-----------------|
| `.map` | Level map / sector layout | WSX entry1 (~504KB table38) |
| `.odf` | Object/descriptor catalog | WSX entry2 (~48KB table38 names+placements) |
| `.lmf` | Nested geometry index + pool | `CKEEP.LMF` |
| `.tex` | Level texture package | WSX entry3 art blob (~12.7MB, `palette.pcx`, `*.pcx` names) |

Also: `global\\global.tex`, `global\\spell.tex`, `global\\*.odf`.

Renderer hooks in `LOL3.DAT`:
- `_Uncompress_Texture_Column`
- `_Get_Texture`
- `_Draw_Floor_Primitive` / `_Draw_Wall_Primitive` / `_Draw_Slant_Primitive` / `_Draw_Sprite_Primitive`

Implies column-oriented texture compression for software/Glide path.
