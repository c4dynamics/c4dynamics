-- Converts a raw HTML <br> (used in the notebook source for table-cell line
-- breaks, so GitHub/Jupyter/nbsphinx render it correctly) into a real line
-- break for the typst/PDF render, which otherwise drops raw HTML entirely.
function RawInline(el)
  if el.format == "html" and el.text:match("^<br%s*/?>$") then
    return pandoc.LineBreak()
  end
end
