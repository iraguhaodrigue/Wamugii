"""Build one branded PDF (handout + worksheet) per lesson from a course content pack.

usage: make_pdfs.py <pack_module> <out_dir>
"""
import base64, html, importlib, random, re, sys, asyncio, zlib
from pathlib import Path
import markdown

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
pack = importlib.import_module(f'app.course_content.{sys.argv[1]}')
COURSE = pack.COURSE
OUT = Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
LOGO = base64.b64encode((Path(__file__).resolve().parents[2] / 'wamugii-frontend/public/logo-emblem-128.png').read_bytes()).decode()

CSS = """
@page { size: A4; margin: 15mm 15mm 14mm 15mm; }
* { box-sizing: border-box; }
body { font-family: Georgia, 'Times New Roman', serif; color: #23262b; font-size: 10.6pt; line-height: 1.5; margin: 0; }
h1,h2,h3,.sans { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
.top { display:flex; align-items:center; gap:12px; border-bottom: 2px solid #b76e79; padding-bottom: 8px; }
.top img { width: 44px; height: 44px; border-radius: 50%; }
.brand { font-family: Helvetica, Arial, sans-serif; font-weight: 800; letter-spacing: .5px; font-size: 12.5pt; color:#1d1f24; }
.slogan { font-size: 8.5pt; color:#b76e79; font-family: Helvetica, Arial, sans-serif; }
.course { margin-left:auto; text-align:right; font-family: Helvetica, Arial, sans-serif; font-size: 8.5pt; color:#6b7280; }
.kicker { margin-top: 16px; font-family: Helvetica, Arial, sans-serif; font-size: 8.5pt; text-transform: uppercase; letter-spacing: 1.2px; color:#b76e79; font-weight: 700; }
h1 { font-size: 21pt; margin: 4px 0 6px; line-height: 1.15; color:#15171b; }
.meta { font-family: Helvetica, Arial, sans-serif; font-size: 9pt; color:#6b7280; }
.meta b { color:#23262b; }
.video { margin-top: 8px; font-family: Helvetica, Arial, sans-serif; font-size: 9pt; background:#f6eef0; border-radius: 8px; padding: 7px 10px; color:#7a3f49; }
.video a { color:#7a3f49; }
.notes h2 { font-size: 12.5pt; color:#15171b; margin: 18px 0 6px; padding-bottom: 3px; border-bottom: 1px solid #ecdde0; page-break-after: avoid; }
.notes p { margin: 6px 0; }
.notes ul, .notes ol { margin: 6px 0 6px 0; padding-left: 20px; }
.notes li { margin: 3px 0; }
.notes table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 9.2pt; page-break-inside: avoid; }
.notes th { background:#b76e79; color:white; text-align:left; padding: 5px 7px; font-family: Helvetica, Arial, sans-serif; font-weight: 600; }
.notes td { border-bottom: 1px solid #ead9dc; padding: 5px 7px; vertical-align: top; }
.notes blockquote { margin: 8px 0; padding: 8px 12px; background:#faf6f7; border-left: 3px solid #b76e79; font-style: italic; }
.objective { background:#f6eef0; border-radius: 10px; padding: 9px 12px; margin-top: 12px; }
.objective b { font-family: Helvetica, Arial, sans-serif; color:#7a3f49; }
.takeaway { margin: 14px 0; padding: 10px 14px; border-radius: 10px; background: linear-gradient(90deg,#b76e79,#8c4c57); color:white; page-break-inside: avoid; }
.takeaway b { font-family: Helvetica, Arial, sans-serif; }
.page-break { page-break-before: always; }
.ws-head { display:flex; justify-content: space-between; gap: 16px; font-family: Helvetica, Arial, sans-serif; font-size: 9.5pt; margin-top: 12px; }
.ws-head span { flex:1; border-bottom: 1px solid #9ca3af; padding-bottom: 14px; }
.task { border: 1.5px solid #ead9dc; border-radius: 10px; padding: 10px 12px 6px; margin: 12px 0; page-break-inside: avoid; }
.task h3 { margin: 0 0 4px; font-size: 10.5pt; color:#7a3f49; }
.line { border-bottom: 1px solid #c9ccd1; height: 22px; }
.quiz { font-size: 9.6pt; }
.quiz ol { padding-left: 18px; }
.quiz li { margin: 8px 0; page-break-inside: avoid; }
.quiz .opts { display: grid; grid-template-columns: 1fr 1fr; gap: 2px 18px; margin-top: 3px; font-family: Helvetica, Arial, sans-serif; font-size: 9pt; color:#374151; }
.foot { margin-top: 16px; font-family: Helvetica, Arial, sans-serif; font-size: 7.8pt; color:#9ca3af; text-align:center; }
"""

def split_sections(md):
    """Pull objective, takeaway and the 'Try it yourself' section out of the notes."""
    objective = re.search(r"\*\*Learning objective:\*\*\s*(.+)", md)
    takeaway = re.search(r"\*\*Takeaway:\*\*\s*(.+)", md)
    body = md
    if objective: body = body.replace(objective.group(0), "")
    if takeaway: body = body.replace(takeaway.group(0), "")
    m = re.search(r"^## Try it yourself\s*\n(.*)$", body, re.S | re.M)
    tasks = m.group(1).strip() if m else ""
    if m: body = body[:m.start()]
    return (objective.group(1).strip() if objective else ""), (takeaway.group(1).strip() if takeaway else ""), body.strip(), tasks

def md(text):
    return markdown.markdown(text, extensions=["tables", "sane_lists"])

def task_items(tasks):
    items = re.findall(r"^\s*\d+\.\s+(.+)$", tasks, re.M)
    if not items and tasks:
        items = [tasks]
    return items

def build(lesson, number, module_title, total):
    objective, takeaway, body, tasks = split_sections(lesson["content"])
    week = module_title.split("·")[0].strip()
    video = lesson.get("video")
    video_html = (f'<div class="video">▶ <b>Watch:</b> <a href="{video}">{video}</a> — open the lesson online to watch inside the course.</div>' if video else "")
    task_html = ""
    for i, t in enumerate(task_items(tasks), 1):
        lines = "".join('<div class="line"></div>' for _ in range(5))
        task_html += f'<div class="task"><h3>Task {i}</h3><div>{md(t)}</div>{lines}</div>'
    quiz_html = ""
    if lesson.get("quiz"):
        qs = ""
        for q, opts, correct, _ in lesson["quiz"]:
            # Same seeded order as the online quiz (app/seed_course_content.py).
            order = list(range(len(opts)))
            random.Random(zlib.crc32(q.encode("utf-8"))).shuffle(order)
            opts = [opts[i] for i in order]
            o = "".join(f"<div>{chr(65+j)}. {html.escape(x)}</div>" for j, x in enumerate(opts))
            qs += f"<li>{html.escape(q)}<div class='opts'>{o}</div></li>"
        quiz_html = f'<h2 class="sans" style="font-size:12.5pt;margin-top:18px">Self-check</h2><p class="meta">Think about your answers here, then take the quiz online — it is marked instantly and explains every answer.</p><div class="quiz"><ol>{qs}</ol></div>'
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="top"><img src="data:image/png;base64,{LOGO}"><div><div class="brand">WAMUGII TECH SOLUTIONS</div><div class="slogan">We Build. We Innovate. We Empower.</div></div>
<div class="course">{html.escape(COURSE['title'])}<br>{html.escape(module_title)}</div></div>
<div class="kicker">{html.escape(week)} · Lesson {number} of {total} · Handout</div>
<h1>{html.escape(lesson['title'])}</h1>
<div class="meta">Study time: <b>about {lesson['minutes']} minutes</b> (reading, video and activity)</div>
{video_html}
{f'<div class="objective"><b>Your goal in this lesson:</b> {md(objective)[3:-4]}</div>' if objective else ''}
<div class="notes">{md(body)}</div>
{f'<div class="takeaway"><b>Remember this:</b> {md(takeaway)[3:-4]}</div>' if takeaway else ''}
<div class="page-break"></div>
<div class="top"><img src="data:image/png;base64,{LOGO}"><div><div class="brand">WAMUGII TECH SOLUTIONS</div><div class="slogan">Student Worksheet</div></div>
<div class="course">{html.escape(COURSE['title'])}<br>Lesson {number}: {html.escape(lesson['title'])}</div></div>
<div class="ws-head"><span>Name:</span><span>Date:</span></div>
<h2 class="sans" style="font-size:12.5pt;margin-top:16px">Activity</h2>
{task_html or '<p>Complete the activity described in the lesson.</p>'}
{quiz_html}
<div class="foot">© WAMUGII TECH SOLUTIONS · wamugii.kento.rw · Original course material — for enrolled students.</div>
</body></html>"""

async def main():
    from playwright.async_api import async_playwright
    lessons = [(l, m["title"]) for m in COURSE["modules"] for l in m["lessons"]]
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        for n, (lesson, mt) in enumerate(lessons, 1):
            await page.set_content(build(lesson, n, mt, len(lessons)), wait_until="load")
            await page.pdf(path=str(OUT / f"{n:02d}.pdf"), format="A4", print_background=True,
                           display_header_footer=True, header_template="<span></span>",
                           footer_template='<div style="font-size:7px;color:#9ca3af;width:100%;text-align:center;font-family:Helvetica">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>',
                           margin={"top": "15mm", "bottom": "16mm", "left": "15mm", "right": "15mm"})
            print("pdf", n, lesson["title"])
        await browser.close()

asyncio.run(main())
