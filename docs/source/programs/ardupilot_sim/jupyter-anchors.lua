-- Turn headings written in HTML (<h1 ...> ... </h1>) into real headings.
-- Pandoc keeps the tags as raw HTML, which the Typst/PDF render drops, so the
-- title would come out as a plain paragraph. Two forms are handled:
--   * tags on their own lines: RawBlock "<h1 ...>", content blocks, RawBlock "</h1>"
--     (the closing level is not checked, so a stray </h2> still closes an <h1>)
--   * the whole heading in one raw block: re-read as HTML
-- Inline styling inside (e.g. <span style="color: ...">) is kept.
local function html_headings(blocks)
  local out, i = {}, 1
  while i <= #blocks do
    local b = blocks[i]
    local level = b.t == 'RawBlock' and b.format == 'html' and b.text:match('^%s*<[hH]([1-6])[%s>]')
    if not level then
      table.insert(out, b)
      i = i + 1
    elseif b.text:match('</[hH][1-6]>%s*$') then
      -- the whole heading in one raw block
      for _, nb in ipairs(pandoc.read(b.text, 'html').blocks) do
        table.insert(out, nb)
      end
      i = i + 1
    else
      -- collect the content up to the closing tag
      local inlines, j = pandoc.Inlines{}, i + 1
      while j <= #blocks and not (blocks[j].t == 'RawBlock' and blocks[j].text:match('^%s*</[hH][1-6]>')) do
        if blocks[j].t == 'Plain' or blocks[j].t == 'Para' then
          if #inlines > 0 then inlines:insert(pandoc.Space()) end
          inlines:extend(blocks[j].content)
        end
        j = j + 1
      end
      if j > #blocks then             -- no closing tag: leave the blocks as they are
        table.insert(out, b)
        i = i + 1
      else
        inlines = inlines:walk{SoftBreak = function() return pandoc.Space() end}
        table.insert(out, pandoc.Header(tonumber(level), inlines))
        i = j + 1
      end
    end
  end
  return out
end

-- Give each heading the anchor Jupyter generates ("## 1. Introduction" ->
-- "1.-Introduction"), so in-notebook links like [x](#1.-Introduction) resolve
-- in the Typst/PDF render too, without changing the notebook source.
local function anchor(h)
  h.identifier = pandoc.utils.stringify(h.content):gsub(' ', '-')
  return h
end

-- two passes, in order, so the headings built from HTML get anchors too
return {
  {Blocks = html_headings},
  {Header = anchor},
}
