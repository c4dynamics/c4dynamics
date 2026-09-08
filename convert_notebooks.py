from pathlib import Path
import nbformat


SOURCE = Path(r"C:\Users\zivme\Dropbox\c4dynamics\docs\source")


def notebook_to_markdown(path: Path) -> str:
    notebook = nbformat.read(path, as_version=4)

    parts = []

    for cell in notebook.cells:
        if cell.cell_type == "markdown":
            parts.append(cell.source)

        elif cell.cell_type == "code":
            parts.append("```python\n")
            parts.append(cell.source.rstrip())
            parts.append("\n```\n")

    return "\n\n".join(parts)


for notebook in SOURCE.rglob("*.ipynb"):
    markdown = notebook_to_markdown(notebook)

    output = notebook.with_suffix(".md")
    output.write_text(markdown, encoding="utf-8")

    print(f"Created: {output}")
