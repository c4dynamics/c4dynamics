-- Centers standalone images in the typst/PDF render.
--
-- Matplotlib/Jupyter cell outputs land in the pandoc AST as a paragraph
-- containing a single bare Image (no caption), which quarto's typst writer
-- renders left-aligned as `#box(image(...))`. Markdown images with alt text
-- already become captioned Figure blocks via pandoc's implicit-figures
-- extension and are centered by typst's `#figure` by default, so this only
-- needs to handle the uncaptioned case.
function Para(el)
  if #el.content == 1 and el.content[1].t == "Image" then
    return pandoc.Para({
      pandoc.RawInline("typst", "#align(center)["),
      el.content[1],
      pandoc.RawInline("typst", "]"),
    })
  end
end
