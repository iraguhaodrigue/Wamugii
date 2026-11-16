"""Turn every coding lesson into a Jupyter notebook that opens in Google Colab.

One notebook per lesson that has Python code: the lesson text becomes text
cells and every Python example becomes a code cell, in the same order, so
"Runtime > Run all" runs the whole lesson. The notebooks go into the public
repository github.com/wamugii/notebooks, and each lesson on the
website gets an "Open in Google Colab" button pointing at its notebook:

    https://colab.research.google.com/github/wamugii/notebooks/blob/main/<course-slug>/lesson-NN.ipynb

Only lesson content goes into the notebooks -- never site code, keys or data.

usage (run from wamugii-backend/):
    python scripts/course_make_notebooks.py /path/to/wamugii-notebooks
"""
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

REPO = "wamugii/notebooks"
BRANCH = "main"
SITE = "https://wamugii.kento.rw"
LOGO = f"{SITE}/logo-emblem-128.png"

# Course packs with Python lessons, in programme order.
PACKS = [
    "math_python_for_ai",
    "machine_learning_fundamentals",
    "deep_learning_neural_networks",
    "modern_ai_llms_generative",
    "responsible_ai_deployment",
]

# Libraries Colab does not always have. Installing one that is already there
# is quick and harmless.
PIP = {
    "anthropic": "anthropic",
    "openai": "openai",
    "fastapi": "fastapi httpx",
    "uvicorn": "uvicorn",
}
GPU_IMPORTS = {"torch", "torchvision", "transformers"}

# Projects where the student writes the first part themselves: an empty cell,
# with instructions, right after the section that asks for it.
STUDENT_CELLS = {
    ("math-python-for-ai", 24): (
        "## Part 1",
        "# Part 1 is your work: paste the data cell from the Week 2 project (Lesson 12)\n"
        "# and your cleaning code here, so that a cleaned DataFrame called `clean` exists.\n"
        "# Then run the cells below.\n",
    ),
}
FENCE = re.compile(r"```python[ \t]*\n(.*?)```", re.S)


def colab_url(slug: str, number: int) -> str:
    return f"https://colab.research.google.com/github/{REPO}/blob/{BRANCH}/{slug}/lesson-{number:02d}.ipynb"


def imports(code: str) -> set[str]:
    found = set()
    for m in re.finditer(r"^\s*import\s+([^\n#]+)", code, re.M):
        for part in m.group(1).split(","):
            found.add(part.strip().split()[0].split(".")[0])
    for m in re.finditer(r"^\s*from\s+([A-Za-z_]\w*)", code, re.M):
        found.add(m.group(1))
    return found


def _lines(text: str) -> list[str]:
    """Notebook JSON stores cell text as a list of lines that keep their newline."""
    parts = text.splitlines(keepends=True)
    if parts and parts[-1].endswith("\n"):
        parts[-1] = parts[-1][:-1]
    return parts


def md_cell(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": _lines(text.strip())}


def code_cell(text: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": _lines(text.rstrip())}


def build(course: dict, lesson: dict, number: int, week: str, total: int) -> dict | None:
    content = lesson["content"]
    blocks = FENCE.findall(content)
    if not blocks:
        return None
    used = set().union(*(imports(b) for b in blocks))
    gpu = bool(used & GPU_IMPORTS)
    pip = sorted({pkg for mod, pkgs in PIP.items() if mod in used for pkg in pkgs.split()})

    head = (
        f'<img src="{LOGO}" width="56" align="right" alt="WAMUGII">\n\n'
        f"**{course['title']}** · {week} · Lesson {number} of {total}\n\n"
        f"# {lesson['title']}\n\n"
        "**How to use this notebook:** run the code cells **in order**, from top to bottom "
        "(press ▶ on each cell, or use **Runtime → Run all**). You can change any code and run it again. "
        "To keep your changes, use **File → Save a copy in Drive**."
    )
    if gpu:
        head += (
            "\n\n**This lesson uses a GPU.** Before you start: **Runtime → Change runtime type → T4 GPU → Save**. "
            "The code also runs without a GPU, only more slowly."
        )
    if used & {"anthropic", "openai", "google"}:
        head += (
            "\n\n**API key:** this lesson calls an AI model. Add your key with the **key icon (Secrets)** in the "
            "left bar, switch on **Notebook access**, and never paste a key into the code."
        )
    head += f"\n\nThe lesson, quiz and certificate are on [WAMUGII]({SITE}/courses/{course['slug']})."

    cells = [md_cell(head)]
    if pip:
        cells.append(code_cell(f"# Install the libraries this lesson needs (takes a few seconds).\n%pip install -q {' '.join(pip)}"))

    pos = 0
    for m in FENCE.finditer(content):
        text = content[pos:m.start()].strip()
        if text:
            cells.append(md_cell(text))
        cells.append(code_cell(m.group(1)))
        pos = m.end()
    rest = content[pos:].strip()
    if rest:
        cells.append(md_cell(rest))
    extra = STUDENT_CELLS.get((course["slug"], number))
    if extra:
        marker, code = extra
        at = next(i for i, c in enumerate(cells) if c["cell_type"] == "markdown" and marker in "".join(c["source"]))
        # The marker sits in a text cell that may hold several sections: split it so the
        # empty cell lands right after the section that asks for it.
        text = "".join(cells[at]["source"])
        start = text.index(marker)
        nxt = text.find("\n## ", start + len(marker))
        before, after = (text, "") if nxt < 0 else (text[:nxt], text[nxt:])
        cells[at] = md_cell(before)
        cells[at + 1:at + 1] = [code_cell(code)] + ([md_cell(after)] if after.strip() else [])
    cells.append(md_cell(
        "---\n"
        f"Finished? Go back to [{course['title']} on WAMUGII]({SITE}/courses/{course['slug']}), "
        "tick the lesson as done and take the quiz.\n\n"
        "*© WAMUGII TECH SOLUTIONS · Original course material for WAMUGII AI Program students.*"
    ))

    meta = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
        "colab": {"provenance": [], "toc_visible": True, "name": f"lesson-{number:02d}.ipynb"},
    }
    if gpu:
        meta["accelerator"] = "GPU"
        meta["colab"]["gpuType"] = "T4"
    return {"nbformat": 4, "nbformat_minor": 5, "metadata": meta, "cells": cells}


def main(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    index = []
    for pack_name in PACKS:
        course = importlib.import_module(f"app.course_content.{pack_name}").COURSE
        lessons = [(lesson, m["title"]) for m in course["modules"] for lesson in m["lessons"]]
        folder = out_dir / course["slug"]
        folder.mkdir(exist_ok=True)
        rows = []
        for number, (lesson, week) in enumerate(lessons, 1):
            nb = build(course, lesson, number, week, len(lessons))
            if nb is None:
                continue
            # Ids make the notebook valid for current Jupyter versions; stable so re-runs don't churn git.
            for i, cell in enumerate(nb["cells"]):
                cell["id"] = f"c{number:02d}-{i:03d}"
            path = folder / f"lesson-{number:02d}.ipynb"
            path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", "utf-8")
            rows.append((number, lesson["title"], week.split("·")[0].strip()))
        index.append((course, rows))
        print(f"{course['slug']}: {len(rows)} notebooks")

    badge = "https://colab.research.google.com/assets/colab-badge.svg"
    readme = [
        "# WAMUGII AI Program — lesson notebooks",
        "",
        f"Every coding lesson of the [WAMUGII AI Program]({SITE}/courses) as a notebook you can open in "
        "**Google Colab** with one click: free, nothing to install, and a free GPU for the deep-learning lessons.",
        "",
        "**How to use:** click **Open in Colab**, then run the cells from top to bottom (**Runtime → Run all**). "
        "To keep your work, choose **File → Save a copy in Drive**. Lessons that call an AI model need an API key: "
        "add it with the key icon (**Secrets**) in Colab's left bar and switch on notebook access.",
        "",
        "These notebooks are generated from the course lessons. To report a problem, use the questions box under "
        "the lesson on the website.",
        "",
    ]
    for course, rows in index:
        readme += [f"## {course['title']}", "", "| # | Lesson | Week | |", "|---|---|---|---|"]
        for number, title, week in rows:
            readme.append(f"| {number} | {title} | {week} | [![Open in Colab]({badge})]({colab_url(course['slug'], number)}) |")
        readme.append("")
    readme += ["---", "© WAMUGII TECH SOLUTIONS · Original course material. Please do not republish.", ""]
    (out_dir / "README.md").write_text("\n".join(readme), "utf-8")
    print("README.md written")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]))
