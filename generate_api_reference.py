"""Generate rich, source-accurate API reference markdown for the chatbot's RAG corpus.

Pulls documentation directly from the real docstrings in c4dynamics/**/*.py (via
Python's inspect module) instead of a hand-written summary, so the corpus
reflects the actual source -- full parameter descriptions, worked examples,
behavioral notes -- rather than a compressed paraphrase of it. Converts the
numpydoc/RST docstring formatting (.. code::, .. math::, :mod:/:class:/:func:
cross-references, "Parameters\\n----------" section headers) into clean
markdown.

One file per class/module is emitted, each self-contained with every public
method's full docstring, so a single retrieved item is both precisely titled
(matches "what does ekf.predict do" style queries) and content-rich (doesn't
need a second, better-matching chunk to actually answer the question).

Run this after any docstring changes in c4dynamics/**/*.py, then re-upload the
changed files with upload_corpus.ps1.
"""

import inspect
import re
from pathlib import Path

import c4dynamics as c4d

OUT_DIR = Path(r"C:\Users\zivme\Dropbox\c4dynamics\docs\source\tutorials\api_generated")


def rst_to_md(text: str) -> str:
    if not text:
        return ""

    # Cross-reference roles: :role:`label <target>` or :role:`target`
    def repl_role(m):
        label = (m.group(1) or "").strip()
        target = (m.group(2) or "").strip()
        return f"`{label or target}`"

    text = re.sub(
        r":(?:class|mod|func|meth|attr|data|obj):`([^<`]*?)(?:<([^>`]+)>)?`",
        repl_role,
        text,
    )

    # Inline math role: :math:`...`
    text = re.sub(r":math:`([^`]+)`", r"$\1$", text)

    # .. math:: block -> $$...$$
    def repl_math_block(m):
        body = "\n".join(line.strip() for line in m.group(1).splitlines() if line.strip())
        return f"\n$$\n{body}\n$$\n"

    # The block can contain blank lines between equations (RST allows this
    # inside a directive body) -- match runs of indented-or-blank lines, which
    # naturally stops at the first non-indented, non-blank line (i.e. the
    # real end of the block, back at base indentation).
    text = re.sub(
        r"\.\. math::\s*\n\n((?:(?:^[ \t]+.*)?\n)+)",
        repl_math_block,
        text,
        flags=re.MULTILINE,
    )

    # .. code:: block -> fenced python block (dedented, keeps >>> / ... prompts
    # and the expected output lines exactly as the doctest specifies them)
    def repl_code_block(m):
        body = m.group(1)
        lines = body.splitlines()
        indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
        indent = min(indents) if indents else 0
        dedented = "\n".join(line[indent:] if len(line) >= indent else line for line in lines)
        return f"\n```python\n{dedented.strip()}\n```\n"

    # Same blank-line tolerance as the math block above -- a doctest can have
    # blank lines between statements without that ending the directive body.
    text = re.sub(
        r"\.\. code::\s*\n\n((?:(?:^[ \t]+.*)?\n)+)",
        repl_code_block,
        text,
        flags=re.MULTILINE,
    )

    # numpydoc section headers ("Parameters\n----------") -> "### Parameters"
    text = re.sub(
        r"^([A-Z][A-Za-z ]+)\n-{3,}\s*\n",
        lambda m: f"### {m.group(1).strip()}\n",
        text,
        flags=re.MULTILINE,
    )

    # Figure directives -- an image reference is useless in a text corpus
    text = re.sub(r"\.\. figure::.*(?:\n[ \t]+.*)*", "", text)

    # Any remaining bare directive we didn't handle explicitly
    text = re.sub(r"^\.\. \w+::.*$", "", text, flags=re.MULTILINE)

    # Collapse runs of 3+ blank lines left behind by the substitutions above
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def doc_member(name: str, obj, heading_level: int = 3) -> str:
    doc = inspect.getdoc(obj)
    if not doc:
        return ""

    md = rst_to_md(doc)
    if not md:
        return ""

    hashes = "#" * heading_level

    try:
        sig = inspect.signature(obj)
        sig_line = f"```python\n{name}{sig}\n```\n\n"
    except (ValueError, TypeError):
        sig_line = ""

    return f"{hashes} `{name}`\n\n{sig_line}{md}\n\n"


def doc_class(title: str, cls) -> str:
    parts = [f"# {title}\n\n"]

    class_doc = inspect.getdoc(cls)
    if class_doc:
        md = rst_to_md(class_doc)
        if md:
            parts.append(md + "\n\n")

    for name, member in inspect.getmembers(cls):
        if name.startswith("_"):
            continue
        if inspect.isfunction(member) or inspect.ismethod(member):
            parts.append(doc_member(name, member))
        elif isinstance(member, property) and member.fget is not None:
            parts.append(doc_member(name, member.fget))

        note = EXTRA_NOTES.get((title, name))
        if note:
            parts.append(f"> **Note (verified by testing, not in the docstring above):** {note}\n\n")

    return "".join(parts)


# Facts discovered through live chatbot testing that the source docstrings
# don't state explicitly (e.g. a getter-only property doesn't say "read-only"
# in its own text -- the absence of a setter is the only signal, and that's
# too weak for retrieval to reliably act on). Keeping these INSIDE the same
# rich, well-titled file as the member they apply to, instead of in a
# separate curated file, means they compete as part of the same winning
# chunk rather than having to win retrieval on their own.
EXTRA_NOTES: dict[tuple[str, str], str] = {
    ("rigidbody", "angles"): (
        "This property is **read-only** (no setter) — `rb.angles = [...]` raises "
        "`AttributeError: can't set attribute`. To set initial or new Euler angles, "
        "either pass `phi`/`theta`/`psi` to the constructor or set those individual "
        "attributes directly (e.g. `rb.phi = 0.1`)."
    ),
    ("rigidbody", "ang_rates"): (
        "This property is **read-only** (no setter) — `rb.ang_rates = [...]` raises "
        "`AttributeError: can't set attribute`. Set `p`/`q`/`r` individually instead "
        "(via the constructor or as direct attributes), never `rb.ang_rates = [...]`."
    ),
    ("rigidbody", "BR"): (
        "This property is **read-only** (no setter) — it's computed from the current "
        "Euler angles, not something you assign directly. `rb.BR = ...` raises "
        "`AttributeError: can't set attribute`."
    ),
    ("rigidbody", "RB"): (
        "This property is **read-only** (no setter), same as `BR` — computed from the "
        "current Euler angles, not directly assignable."
    ),
    ("rigidbody", "I"): (
        "Unlike `angles`/`ang_rates`/`BR`/`RB` above, `I` genuinely IS settable as a "
        "3-element list/array: `rb.I = [Ixx, Iyy, Izz]`."
    ),
    ("ekf", "predict"): (
        "`fx` and `hx` (see `update` below) are **pre-evaluated numpy arrays**, not "
        "callables — you compute the nonlinear derivative/measurement value yourself, "
        "inside your own simulation loop, using the filter's *current* state estimate "
        "each iteration, and pass that resulting array in. Do not define `fx`/`hx` as "
        "Python functions and pass the function object itself — `predict(fx=some_function, "
        "...)` is invalid; it must be `predict(fx=some_function(ekf.X, ...), ...)`, i.e. "
        "already evaluated before the call."
    ),
    ("ekf", "update"): (
        "Same as `predict`'s `fx` note above: `hx` is a pre-evaluated array (the value "
        "of h(x) at the current state), not a callable passed in as-is."
    ),
    ("rigidbody", "inteqm"): (
        "`forces`, `moments`, and `dt` are all **required** positional arguments with no "
        "defaults — there is no no-argument or partial-argument form of this call."
    ),
}


def doc_module_functions(title: str, module, names: list[str]) -> str:
    parts = [f"# {title}\n\n"]
    for name in names:
        obj = getattr(module, name)
        parts.append(doc_member(name, obj, heading_level=2))
    return "".join(parts)


CLASS_TARGETS = [
    ("state", c4d.state),
    ("datapoint", c4d.datapoint),
    ("pixelpoint", c4d.pixelpoint),
    ("rigidbody", c4d.rigidbody),
    ("kalman", c4d.filters.kalman),
    ("ekf", c4d.filters.ekf),
    ("lowpass", c4d.filters.lowpass),
    ("seeker", c4d.sensors.seeker),
    ("radar", c4d.sensors.radar),
    ("gps", c4d.sensors.gps),
    ("imu", c4d.sensors.imu),
    ("magnetometer", c4d.sensors.magnetometer),
    ("lineofsight", c4d.sensors.lineofsight),
    ("yolov3", c4d.detectors.yolov3),
]

MODULE_FUNCTION_TARGETS = [
    ("rotmat", c4d.rotmat, ["rotx", "roty", "rotz", "dcm321", "dcm321euler"]),
    ("eqm", c4d.eqm, ["eqm3", "eqm6", "int3", "int6"]),
    ("utils", c4d, ["cprint", "tic", "toc", "plotdefaults", "gif"]),
]


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for title, obj in CLASS_TARGETS:
        content = doc_class(title, obj)
        out_path = OUT_DIR / f"{title}.md"
        out_path.write_text(content, encoding="utf-8")
        print(f"Created: {out_path} ({len(content)} chars)")

    for title, module, names in MODULE_FUNCTION_TARGETS:
        content = doc_module_functions(title, module, names)
        out_path = OUT_DIR / f"{title}.md"
        out_path.write_text(content, encoding="utf-8")
        print(f"Created: {out_path} ({len(content)} chars)")
