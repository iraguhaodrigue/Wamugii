"""Build a course's Student Handbook PDF and one chapter PDF per lesson.

The handbook is written so a student can learn the whole course by reading
alone: every lesson becomes a full chapter with worked examples, diagrams,
common mistakes, a self-check quiz and model answers.

Chapter text lives in  app/course_content/handbooks/<slug>/NN.md
(plus intro.md for the "How to use this handbook" page). The multiple-choice
self-check comes from the lesson quiz in the course pack, in the same option
order as the online quiz, so the handbook and the website always agree.

usage (run from wamugii-backend/):
    python scripts/course_make_handbook.py ai_foundations          # book + lesson PDFs
    python scripts/course_make_handbook.py ai_foundations --book   # book only
    python scripts/course_make_handbook.py ai_foundations --lessons

Output:
    app/course_content/pdfs/<slug>/NN.pdf            one chapter per lesson
    app/course_content/handbooks/<slug>/handbook.pdf the complete handbook
    app/course_content/handbooks/<slug>/handbook.json pages and words, for the course page
Needs: playwright (with Chromium), markdown, pypdf; fonts Inter and Lora.
"""
from __future__ import annotations

import asyncio
import base64
import html
import importlib
import io
import json
import random
import re
import sys
import zlib
from datetime import date
from pathlib import Path

import markdown
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from handbook_figures import FIGURES  # noqa: E402

LOGO = base64.b64encode((ROOT.parent / "wamugii-frontend/public/logo-emblem-128.png").read_bytes()).decode()
SITE = "wamugii.kento.rw"
SPECIAL = ("Summary", "Key terms", "Think deeper", "Practice")
BOX_LABELS = {"key": "Key idea", "example": "Worked example", "mistake": "Common mistake",
              "rwanda": "In Rwanda", "think": "Think about it", "tip": "Tip", "note": "Note"}

CSS = """
@page { size: A4; margin: 17mm 17mm 18mm 17mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: Lora, Georgia, serif; color: #1e293b; font-size: 10.6pt; line-height: 1.6; margin: 0; }
h1, h2, h3, h4, .sans, table, figcaption, .box-label, .kicker, .toc, .opts { font-family: Inter, Helvetica, Arial, sans-serif; }
p { margin: 0 0 8px; orphans: 3; widows: 3; }
a { color: #0e7490; text-decoration: none; }
strong { color: #0f172a; }
h2 { font-size: 14.5pt; color: #0f172a; margin: 22px 0 8px; padding-bottom: 4px; border-bottom: 2px solid #e2e8f0; page-break-after: avoid; break-after: avoid; }
h2 .num { color: #0e7490; margin-right: 8px; }
h3 { font-size: 11.6pt; color: #0e7490; margin: 16px 0 6px; page-break-after: avoid; break-after: avoid; }
ul, ol { margin: 4px 0 10px; padding-left: 22px; }
li { margin: 3px 0; }
blockquote { margin: 12px 0; padding: 10px 16px; background: #f0fdfa; border-left: 4px solid #0e7490; border-radius: 0 10px 10px 0; font-size: 11pt; }
blockquote p { margin: 0; }
table { border-collapse: collapse; width: 100%; margin: 10px 0 14px; font-size: 9pt; line-height: 1.4; page-break-inside: avoid; break-inside: avoid; }
th { background: #0e7490; color: white; text-align: left; padding: 6px 8px; font-weight: 600; }
td { border-bottom: 1px solid #e2e8f0; padding: 6px 8px; vertical-align: top; }
tr:nth-child(even) td { background: #f8fafc; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 0.86em; background: #f1f5f9; padding: 1px 4px; border-radius: 4px; }
figure { margin: 14px 0 16px; text-align: center; page-break-inside: avoid; break-inside: avoid; }
figcaption { font-size: 8.8pt; color: #64748b; margin-top: 6px; }
figcaption b { color: #0e7490; }
.box { border-radius: 12px; padding: 11px 15px 5px; margin: 14px 0; page-break-inside: avoid; break-inside: avoid; border: 1.4px solid; }
.box-label { break-after: avoid; page-break-after: avoid; font-size: 8.6pt; font-weight: 800; letter-spacing: .9px; text-transform: uppercase; margin-bottom: 5px; }
.box.key { background: #ecfeff; border-color: #67e8f9; } .box.key .box-label { color: #0e7490; }
.box.example { background: #f5f3ff; border-color: #c4b5fd; } .box.example .box-label { color: #6d28d9; }
.box.mistake { background: #fff7ed; border-color: #fdba74; } .box.mistake .box-label { color: #c2410c; }
.box.rwanda { background: #f0fdf4; border-color: #86efac; } .box.rwanda .box-label { color: #15803d; }
.box.think, .box.tip, .box.note { background: #f8fafc; border-color: #cbd5e1; } .box.think .box-label, .box.tip .box-label, .box.note .box-label { color: #334155; }
.box.example { page-break-inside: auto; break-inside: auto; }

.opener { background: linear-gradient(135deg, #0b1120 0%, #0e3a4a 55%, #3b1d7a 100%); color: white; border-radius: 16px; padding: 22px 24px 20px; margin-bottom: 16px; }
.opener .kicker { font-size: 8.6pt; font-weight: 700; letter-spacing: 1.4px; text-transform: uppercase; color: #67e8f9; }
.opener h1 { font-size: 22pt; line-height: 1.15; margin: 6px 0 8px; color: white; }
.opener .chapno { font-family: Inter, sans-serif; font-size: 10pt; color: #c4b5fd; font-weight: 700; }
.opener .meta { font-family: Inter, sans-serif; font-size: 8.8pt; color: #cbd5e1; }
.learn { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 12px 16px 6px; margin: 0 0 16px; }
.learn .box-label { color: #0e7490; }
.learn ul { margin-top: 2px; }
.learn li::marker { color: #0e7490; }
.section-end h2 { border-bottom-color: #c4b5fd; }
.summary-box { background: linear-gradient(135deg, #ecfeff, #f5f3ff); border-radius: 12px; padding: 10px 16px 4px; }
.terms li { margin: 4px 0; }
.mcq { font-size: 10pt; }
.mcq > li { margin: 10px 0; page-break-inside: avoid; break-inside: avoid; }
.opts { display: grid; grid-template-columns: 1fr 1fr; gap: 3px 20px; margin-top: 4px; font-size: 9pt; color: #334155; }
.think-q li { margin: 8px 0; }
.chapter { page-break-before: always; break-before: page; }
.first { page-break-before: avoid; break-before: avoid; }

.answers h3 { margin-top: 18px; }
.answers .ans { font-size: 9.6pt; margin: 3px 0 6px; }
.answers .model { font-size: 9.6pt; background: #f8fafc; border-left: 3px solid #6d28d9; padding: 6px 10px; margin: 4px 0 10px; border-radius: 0 8px 8px 0; }
.answers .model p { margin: 0 0 4px; }
.key-letter { font-family: Inter, sans-serif; font-weight: 800; color: #0e7490; }

.front h1, .back h1 { font-size: 20pt; color: #0f172a; margin: 0 0 12px; }
.toc { font-size: 10pt; }
.toc .week { font-weight: 800; color: #6d28d9; font-size: 9pt; letter-spacing: 1px; text-transform: uppercase; margin: 14px 0 4px; }
.toc .row { display: flex; align-items: baseline; gap: 8px; margin: 3px 0; }
.toc .row .n { width: 22px; color: #0e7490; font-weight: 700; }
.toc .row .dots { flex: 1; border-bottom: 1px dotted #94a3b8; transform: translateY(-3px); }
.toc .row .p { width: 26px; text-align: right; font-weight: 600; }
.divider { page-break-before: always; break-before: page; min-height: 240mm; display: flex; flex-direction: column; justify-content: center; }
.divider .kicker { font-family: Inter, sans-serif; color: #6d28d9; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; font-size: 10pt; }
.divider h1 { font-size: 30pt; color: #0f172a; margin: 8px 0 14px; line-height: 1.1; }
.divider .bar { width: 80px; height: 6px; border-radius: 3px; background: linear-gradient(90deg, #0e7490, #6d28d9); margin-bottom: 18px; }
.divider ol { font-family: Inter, sans-serif; font-size: 11pt; color: #334155; }
.gloss dt { font-family: Inter, sans-serif; font-weight: 700; color: #0f172a; margin-top: 7px; font-size: 10pt; }
.gloss dd { margin: 1px 0 0 0; font-size: 9.8pt; }
.gloss dd .ch { color: #94a3b8; font-family: Inter, sans-serif; font-size: 8pt; }
.gloss .letter { font-family: Inter, sans-serif; font-size: 15pt; font-weight: 800; color: #0e7490; margin: 14px 0 2px; border-bottom: 1px solid #e2e8f0; }
.gloss { column-count: 2; column-gap: 26px; }
.gloss dt { break-after: avoid; }
.gloss dd { break-inside: avoid; }
.lesson-top { display: flex; align-items: center; gap: 10px; font-family: Inter, sans-serif; font-size: 8.5pt; color: #64748b; margin-bottom: 10px; }
.lesson-top img { width: 26px; height: 26px; border-radius: 50%; }
.lesson-top b { color: #0f172a; }
"""

COVER_CSS = """
@page { size: A4; margin: 0; }
html, body { margin: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.cover { width: 210mm; height: 297mm; position: relative; overflow: hidden; color: white; font-family: Inter, sans-serif;
  background: radial-gradient(circle at 85% 12%, rgba(103,232,249,.35), transparent 38%), radial-gradient(circle at 10% 90%, rgba(139,92,246,.45), transparent 45%), linear-gradient(160deg, #0b1120 0%, #0c2a36 50%, #2a1660 100%); }
.grid { position: absolute; inset: 0; background-image: linear-gradient(rgba(255,255,255,.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.05) 1px, transparent 1px); background-size: 12mm 12mm; }
.inner { position: absolute; inset: 22mm 20mm; display: flex; flex-direction: column; }
.brand { display: flex; align-items: center; gap: 12px; font-weight: 800; letter-spacing: .6px; font-size: 12pt; }
.brand img { width: 46px; height: 46px; border-radius: 50%; }
.brand small { display: block; font-weight: 500; color: #67e8f9; font-size: 8.5pt; letter-spacing: .4px; }
.kick { margin-top: 70mm; color: #67e8f9; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; font-size: 11pt; }
h1 { font-size: 46pt; line-height: 1.02; margin: 10px 0 14px; letter-spacing: -1px; }
.sub { font-size: 14pt; color: #cbd5e1; max-width: 140mm; line-height: 1.45; font-family: Lora, serif; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 22px; }
.chip { border: 1px solid rgba(255,255,255,.28); border-radius: 999px; padding: 6px 14px; font-size: 9.5pt; background: rgba(255,255,255,.06); }
.foot { margin-top: auto; display: flex; justify-content: space-between; align-items: flex-end; font-size: 9pt; color: #94a3b8; }
.foot b { color: white; }
.bar { width: 90px; height: 7px; border-radius: 4px; background: linear-gradient(90deg, #22d3ee, #8b5cf6); }
"""

FOOTER = ('<div style="font-family:Inter,Helvetica,sans-serif;font-size:7.5px;color:#94a3b8;width:100%;'
          'padding:0 17mm;display:flex;justify-content:space-between">'
          '<span>{left}</span><span>Page <span class="pageNumber"></span></span></div>')


def md(text: str) -> str:
    return markdown.markdown(text, extensions=["tables", "sane_lists", "md_in_html", "fenced_code"])


def inline(text: str) -> str:
    out = md(text).strip()
    return out[3:-4] if out.startswith("<p>") and out.endswith("</p>") else out


def shuffled(question: str, options: list[str], correct: int) -> tuple[list[str], int]:
    """Same seeded option order as the online quiz (app/seed_course_content.py)."""
    order = list(range(len(options)))
    random.Random(zlib.crc32(question.encode("utf-8"))).shuffle(order)
    return [options[i] for i in order], order.index(correct)


class Chapter:
    def __init__(self, number: int, lesson: dict, week_title: str, text: str):
        self.n = number
        self.lesson = lesson
        self.title = lesson["title"]
        self.week = week_title
        self.fig_count = 0
        self.learn: list[str] = []
        self.think: list[tuple[str, str]] = []
        self.terms: list[tuple[str, str]] = []
        self.body_html = self._render(text)

    # -- parsing ---------------------------------------------------------------
    def _render(self, text: str) -> str:
        text = text.replace("\r\n", "\n")
        m = re.search(r"^:::learn\n(.*?)\n:::\s*$", text, re.S | re.M)
        if m:
            self.learn = [re.sub(r"^\s*-\s+", "", x).strip() for x in m.group(1).splitlines() if x.strip()]
            text = text[:m.start()] + text[m.end():]

        sections = re.split(r"^## ", text, flags=re.M)
        intro, rest = sections[0], sections[1:]
        out = [self._blocks(intro)]
        k = 0
        for sec in rest:
            title, _, body = sec.partition("\n")
            title = title.strip()
            if title == "Think deeper":
                self._parse_think(body)
                continue
            if title == "Key terms":
                self.terms = [(t.strip(), d.strip()) for t, d in re.findall(r"^\s*-\s+\*\*(.+?)\*\*\s+[—-]+\s+(.+)$", body, re.M)]
            if title in SPECIAL:
                cls = {"Summary": "summary", "Key terms": "terms", "Practice": "practice"}[title]
                inner = self._blocks(body)
                if title == "Summary":
                    inner = f'<div class="summary-box">{inner}</div>'
                out.append(f'<div class="section-end {cls}"><h2>{html.escape(title)}</h2>{inner}</div>')
            else:
                k += 1
                out.append(f'<h2><span class="num">{self.n}.{k}</span>{html.escape(title)}</h2>{self._blocks(body)}')
        return "\n".join(out)

    def _parse_think(self, body: str) -> None:
        parts = re.split(r"^\s*\d+\.\s+", body, flags=re.M)
        for part in parts[1:]:
            m = re.search(r"^:::answer\n(.*?)\n:::\s*$", part, re.S | re.M)
            q = part[:m.start()].strip() if m else part.strip()
            a = m.group(1).strip() if m else ""
            self.think.append((q, a))

    def _blocks(self, text: str) -> str:
        def box(m: re.Match) -> str:
            kind, title, body = m.group(1), (m.group(2) or "").strip(), m.group(3)
            label = title or BOX_LABELS.get(kind, kind.title())
            return (f'<div class="box {kind}" markdown="1">\n<div class="box-label">{html.escape(label)}</div>\n\n'
                    f"{body.strip()}\n\n</div>")

        text = re.sub(r"^:::(\w+)[ \t]*([^\n]*)\n(.*?)\n:::[ \t]*$", box, text, flags=re.S | re.M)

        def fig(m: re.Match) -> str:
            name, cap = m.group(1), m.group(2)
            self.fig_count += 1
            svg = FIGURES[name]()
            return (f'<figure>{svg}<figcaption><b>Figure {self.n}.{self.fig_count}</b> — '
                    f"{html.escape(cap)}</figcaption></figure>")

        text = re.sub(r"^\[\[fig:(\w+)\|(.+?)\]\]\s*$", fig, text, flags=re.M)
        return md(text)

    # -- output ------------------------------------------------------------------
    def quiz(self) -> list[tuple[str, list[str], int, str]]:
        out = []
        for q, opts, correct, why in self.lesson.get("quiz", []):
            o, c = shuffled(q, opts, correct)
            out.append((q, o, c, why))
        return out

    def html(self, total: int, course_title: str, standalone: bool, first: bool) -> str:
        learn = "".join(f"<li>{inline(x)}</li>" for x in self.learn)
        learn_html = (f'<div class="learn"><div class="box-label">In this chapter you will learn to</div><ul>{learn}</ul></div>'
                      if learn else "")
        mcq = ""
        for q, opts, _c, _w in self.quiz():
            o = "".join(f"<div><b>{chr(65 + j)}.</b> {html.escape(x)}</div>" for j, x in enumerate(opts))
            mcq += f'<li>{html.escape(q)}<div class="opts">{o}</div></li>'
        think = "".join(f"<li>{inline(q)}</li>" for q, _a in self.think)
        where = "at the end of this chapter" if standalone else "in the Answer key at the back of this handbook"
        check = ""
        if mcq:
            check += (f'<div class="section-end"><h2>Self-check</h2><p class="sans" style="font-size:9pt;color:#64748b">'
                      f"Choose one answer for each question. Answers with explanations are {where}. "
                      f"The same questions are in the online lesson quiz.</p><ol class=\"mcq\">{mcq}</ol></div>")
        if think:
            check += (f'<div class="section-end"><h2>Think deeper</h2><p class="sans" style="font-size:9pt;color:#64748b">'
                      f"Answer in your own words first, then compare with the model answers {where}.</p>"
                      f'<ol class="think-q">{think}</ol></div>')
        top = ""
        if standalone:
            top = (f'<div class="lesson-top"><img src="data:image/png;base64,{LOGO}"><div><b>WAMUGII TECH SOLUTIONS</b> · '
                   f"{html.escape(course_title)} · Student Handbook</div></div>")
        body = self.body_html
        # Practice goes after the self-check, so the chapter ends with something to do.
        practice = ""
        pm = re.search(r'<div class="section-end practice">.*?</div>\s*$', body, re.S)
        if pm:
            practice, body = pm.group(0), body[:pm.start()]
        cls = "chapter first" if first else "chapter"
        return (f'<section class="{cls}" id="ch{self.n}">{top}<div class="opener"><div class="kicker">{html.escape(self.week)}</div>'
                f'<div class="chapno">Chapter {self.n} of {total}</div><h1>{html.escape(self.title)}</h1>'
                f'<div class="meta">Reading and practice time: about {self.minutes()} minutes</div></div>'
                f"{learn_html}{body}{check}{practice}</section>")

    def minutes(self) -> int:
        words = len(re.findall(r"\w+", re.sub(r"<[^>]+>", " ", self.body_html)))
        return max(self.lesson.get("minutes", 30), int(round(words / 130 / 5.0) * 5) + 15)

    def answers_html(self, heading_level: str = "h3") -> str:
        rows = ""
        for i, (q, opts, c, why) in enumerate(self.quiz(), 1):
            rows += (f'<div class="ans"><span class="key-letter">{i}. {chr(65 + c)}</span> — {html.escape(opts[c])}. '
                     f'<span style="color:#475569">{html.escape(why)}</span></div>')
        model = ""
        for i, (q, a) in enumerate(self.think, 1):
            model += f'<div class="ans"><b>Think deeper {i}.</b> {inline(q)}</div><div class="model">{md(a)}</div>'
        return (f'<{heading_level}>Chapter {self.n}: {html.escape(self.title)}</{heading_level}>'
                f'<div class="ans" style="font-weight:600;color:#0f172a">Self-check</div>{rows}{model}')


def load(pack_name: str):
    pack = importlib.import_module(f"app.course_content.{pack_name}")
    course = pack.COURSE
    folder = ROOT / "app/course_content/handbooks" / course["slug"]
    chapters: list[Chapter] = []
    n = 0
    for module in course["modules"]:
        for lesson in module["lessons"]:
            n += 1
            path = folder / f"{n:02d}.md"
            if not path.exists():
                raise SystemExit(f"missing chapter file: {path}")
            chapters.append(Chapter(n, lesson, module["title"], path.read_text("utf-8")))
    intro = (folder / "intro.md").read_text("utf-8") if (folder / "intro.md").exists() else ""
    return course, folder, chapters, intro


def page(body: str) -> str:
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>'


def cover_html(course: dict, chapters: list[Chapter]) -> str:
    weeks = len({c.week for c in chapters})
    edition = date.today().strftime("%B %Y")
    title = html.escape(course["title"])
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{COVER_CSS}</style></head><body><div class="cover">'
            f'<div class="grid"></div><div class="inner"><div class="brand"><img src="data:image/png;base64,{LOGO}">'
            f'<div>WAMUGII TECH SOLUTIONS<small>We Build. We Innovate. We Empower.</small></div></div>'
            f'<div class="kick">Student Handbook</div><h1>{title}</h1><div class="bar"></div>'
            f'<p class="sub">The complete course in one book. Every lesson explained step by step, '
            f"in simple English, so you can learn by reading alone.</p>"
            f'<div class="chips"><span class="chip">{len(chapters)} chapters</span><span class="chip">{weeks} weeks</span>'
            f'<span class="chip">Worked examples &amp; diagrams</span><span class="chip">Self-checks with answers</span>'
            f'<span class="chip">Glossary</span></div>'
            f'<div class="foot"><div><b>WAMUGII AI Program</b><br>{SITE}</div><div style="text-align:right">'
            f"Edition 1 · {edition}<br>For enrolled students</div></div></div></div></body></html>")


def front_html(course: dict, chapters: list[Chapter], intro: str, pages: dict[str, int]) -> str:
    rows = ""
    week = None
    for c in chapters:
        if c.week != week:
            week = c.week
            rows += f'<div class="week">{html.escape(week)}</div>'
        p = pages.get(f"ch{c.n}", "")
        rows += (f'<div class="row"><span class="n">{c.n}</span><span>{html.escape(c.title)}</span>'
                 f'<span class="dots"></span><span class="p">{p}</span></div>')
    rows += '<div class="week">Reference</div>'
    for key, label in (("glossary", "Glossary"), ("answers", "Answer key")):
        rows += (f'<div class="row"><span class="n"></span><span>{label}</span><span class="dots"></span>'
                 f'<span class="p">{pages.get(key, "")}</span></div>')
    how = f'<div class="front"><h1>How to use this handbook</h1>{md(intro)}</div>' if intro else ""
    return f'{how}<div class="front chapter"><h1>Contents</h1><div class="toc">{rows}</div></div>'


def glossary_html(chapters: list[Chapter]) -> str:
    terms: dict[str, tuple[str, int]] = {}
    for c in chapters:
        for t, d in c.terms:
            key = t.lower()
            if key not in terms:
                terms[key] = (f"<dt>{html.escape(t)}</dt><dd>{inline(d)} <span class=\"ch\">· Ch. {c.n}</span></dd>", c.n)
    body, letter = "", ""
    for key in sorted(terms, key=lambda s: re.sub(r"[^a-z0-9]", "", s)):
        first = re.sub(r"[^a-z]", "", key)[:1].upper() or "#"
        if first != letter:
            letter = first
            body += f'<div class="letter">{letter}</div>'
        body += terms[key][0]
    return (f'<section class="chapter back" id="glossary"><h1>Glossary</h1><p class="sans" style="font-size:9pt;color:#64748b">'
            f"Every key term in the handbook, A to Z, with the chapter where it is explained.</p><dl class=\"gloss\">{body}</dl></section>")


def answers_html(chapters: list[Chapter]) -> str:
    inner = "".join(c.answers_html() for c in chapters)
    return (f'<section class="chapter back answers" id="answers"><h1>Answer key</h1><p class="sans" style="font-size:9pt;color:#64748b">'
            f"Self-check answers with the reason, and model answers for every Think deeper question. A model answer shows one "
            f"good answer; yours can use different words or examples and still be right.</p>{inner}</section>")


def divider_html(week: str, chapters: list[Chapter]) -> str:
    label, _, title = week.partition("·")
    items = "".join(f"<li>{html.escape(c.title)}</li>" for c in chapters if c.week == week)
    first = next(c.n for c in chapters if c.week == week)
    return (f'<section class="divider"><div class="kicker">{html.escape(label.strip())}</div><h1>{html.escape(title.strip() or week)}</h1>'
            f'<div class="bar"></div><ol start="{first}">{items}</ol></section>')


def book_body(course, chapters, intro, pages) -> str:
    parts = [front_html(course, chapters, intro, pages)]
    week = None
    for c in chapters:
        if c.week != week:
            week = c.week
            parts.append(divider_html(week, chapters))
        parts.append(c.html(len(chapters), course["title"], standalone=False, first=False))
    parts.append(glossary_html(chapters))
    parts.append(answers_html(chapters))
    return page("".join(parts))


def outline_pages(pdf_bytes: bytes, chapters: list[Chapter]) -> dict[str, int]:
    """Find the page each chapter, the glossary and the answer key start on."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    found: dict[str, int] = {}
    wanted = {f"Chapter {c.n} of {len(chapters)}": f"ch{c.n}" for c in chapters}
    for i, pg in enumerate(reader.pages, 1):
        text = pg.extract_text() or ""
        for marker, key in wanted.items():
            if key not in found and marker in text:
                found[key] = i
        if "glossary" not in found and re.search(r"^Glossary\s*$", text, re.M) and "Every key term" in text:
            found["glossary"] = i
        if "answers" not in found and re.search(r"^Answer key\s*$", text, re.M) and "Self-check answers" in text:
            found["answers"] = i
    return found


def add_bookmarks(writer: PdfWriter, chapters: list[Chapter], pages: dict[str, int], has_intro: bool) -> None:
    """Clickable bookmarks for PDF readers. Body page n is PDF page n + 1 (the cover comes first)."""
    writer.add_outline_item("Cover", 0)
    if has_intro:
        writer.add_outline_item("How to use this handbook", 1)
    first_ch = pages.get("ch1")
    if first_ch:
        writer.add_outline_item("Contents", first_ch - 2 if has_intro else first_ch - 1)
    parent, week = None, None
    for c in chapters:
        p = pages.get(f"ch{c.n}")
        if not p:
            continue
        if c.week != week:
            week = c.week
            parent = writer.add_outline_item(week, p - 1)
        writer.add_outline_item(f"{c.n}. {c.title}", p, parent=parent)
    for key, label in (("glossary", "Glossary"), ("answers", "Answer key")):
        if pages.get(key):
            writer.add_outline_item(label, pages[key])


async def render(pw_page, html_doc: str, footer_left: str, outline: bool = False) -> bytes:
    await pw_page.set_content(html_doc, wait_until="load")
    await pw_page.evaluate("document.fonts.ready")
    return await pw_page.pdf(format="A4", print_background=True, display_header_footer=True, outline=outline, tagged=True,
                             header_template="<span></span>", footer_template=FOOTER.format(left=html.escape(footer_left)),
                             margin={"top": "17mm", "bottom": "18mm", "left": "17mm", "right": "17mm"})


async def main(pack_name: str, do_book: bool, do_lessons: bool) -> None:
    from playwright.async_api import async_playwright

    course, folder, chapters, intro = load(pack_name)
    out_lessons = ROOT / "app/course_content/pdfs" / course["slug"]
    out_lessons.mkdir(parents=True, exist_ok=True)
    left = f"{course['title']} · Student Handbook · WAMUGII TECH SOLUTIONS"
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        pw_page = await browser.new_page()
        if do_lessons:
            for c in chapters:
                doc = page(c.html(len(chapters), course["title"], standalone=True, first=True)
                           + f'<section class="chapter answers"><h1 style="font-size:16pt">Answers</h1>{c.answers_html()}</section>')
                pdf = await render(pw_page, doc, f"{course['title']} · Chapter {c.n} · WAMUGII TECH SOLUTIONS")
                (out_lessons / f"{c.n:02d}.pdf").write_bytes(pdf)
                print(f"chapter {c.n:02d}: {len(PdfReader(io.BytesIO(pdf)).pages)} pages  {c.title}")
        if do_book:
            body = await render(pw_page, book_body(course, chapters, intro, {}), left)
            pages = outline_pages(body, chapters)
            body = await render(pw_page, book_body(course, chapters, intro, pages), left)
            check = outline_pages(body, chapters)
            if check != pages:
                print("warning: page numbers moved between passes", {k: (pages.get(k), v) for k, v in check.items() if pages.get(k) != v})
            await pw_page.set_content(cover_html(course, chapters), wait_until="load")
            await pw_page.evaluate("document.fonts.ready")
            cover = await pw_page.pdf(format="A4", print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
            writer = PdfWriter()
            writer.append(PdfReader(io.BytesIO(cover)))
            writer.append(PdfReader(io.BytesIO(body)), import_outline=False)
            add_bookmarks(writer, chapters, check, has_intro=bool(intro))
            writer.add_metadata({"/Title": f"{course['title']} — Student Handbook", "/Author": "WAMUGII TECH SOLUTIONS",
                                 "/Subject": "WAMUGII AI Program course handbook"})
            buf = io.BytesIO()
            writer.write(buf)
            target = folder / "handbook.pdf"
            target.write_bytes(buf.getvalue())
            final = PdfReader(io.BytesIO(buf.getvalue()))
            total = len(final.pages)
            words = sum(len(re.findall(r"[A-Za-z0-9']+", pg.extract_text() or "")) for pg in final.pages)
            # Read by the course page ("Includes a 197-page Student Handbook").
            (folder / "handbook.json").write_text(json.dumps(
                {"pages": total, "words": words, "chapters": len(chapters), "edition": date.today().isoformat()},
                indent=2) + "\n", "utf-8")
            print(f"handbook: {target}  {total} pages, {words} words, {len(buf.getvalue()) // 1024} KB")
        await browser.close()


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if not args:
        raise SystemExit(__doc__)
    both = not ({"--book", "--lessons"} & flags)
    asyncio.run(main(args[0], both or "--book" in flags, both or "--lessons" in flags))
