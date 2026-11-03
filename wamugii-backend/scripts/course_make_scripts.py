"""Instructor video-recording guide for lessons that have no video yet."""
import base64, html, importlib, re, sys, asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
COURSE = importlib.import_module(f'app.course_content.{sys.argv[1]}').COURSE
OUT = Path(sys.argv[2])
LOGO = base64.b64encode((Path(__file__).resolve().parents[2] / 'wamugii-frontend/public/logo-emblem-128.png').read_bytes()).decode()

def first_sentence(text):
    text = re.sub(r"[*_`>|☐]", "", text).strip()
    text = re.sub(r"^\s*(?:[-•]|\d+[.)])\s*", "", text)
    text = re.sub(r"\s+", " ", text)
    m = re.match(r"(.+?[.!?])(\s|$)", text)
    return (m.group(1) if m else text)[:220]

blocks = []
n = 0
for module in COURSE["modules"]:
    for l in module["lessons"]:
        n += 1
        if l.get("video"):
            continue
        c = l["content"]
        obj = re.search(r"\*\*Learning objective:\*\*\s*(.+)", c)
        take = re.search(r"\*\*Takeaway:\*\*\s*(.+)", c)
        parts = re.split(r"^## ", c, flags=re.M)[1:]
        points = []
        for part in parts:
            title, _, body = part.partition("\n")
            if re.match(r"try it yourself", title, re.I):
                continue
            body = " ".join(re.sub(r"^\s*(?:[-•]|\d+[.)])\s*", "", x) for x in body.splitlines() if x.strip() and not x.startswith("|") and not x.startswith("**Takeaway"))
            points.append((title.strip(), first_sentence(body) if body else ""))
        is_project = "Project" in l["title"]
        demo = ('<p><b>Demo:</b> Share your screen and walk through the project steps and the worksheet, showing one finished example.</p>'
                if is_project else
                '<p><b>Live demo (1-2 min):</b> Open an AI assistant and do the lesson&#39;s &quot;Try it yourself&quot; activity live, including checking one part of the answer.</p>')
        mins = "4–6" if is_project else "5–8"
        rows = "".join(f"<li><b>{html.escape(t)}</b> — {html.escape(s)}</li>" for t, s in points[:7])
        blocks.append(f"""
<section>
<div class="kicker">Lesson {n} · {html.escape(module['title'])}</div>
<h2>{html.escape(l['title'])}</h2>
<p class="meta">Suggested length: {mins} minutes · talking-head + screen share</p>
<div class="box"><b>Open (30 sec):</b> "Welcome back to AI Career Essentials. In this lesson you will {html.escape((obj.group(1) if obj else '').rstrip('.')[:1].lower() + (obj.group(1) if obj else '').rstrip('.')[1:])}."</div>
<p><b>Cover these points (show an example on screen for each):</b></p>
<ol>{rows}</ol>
{demo}
<div class="box"><b>Close (30 sec):</b> "{html.escape(take.group(1).strip() if take else 'That is the key idea for today.')} Now complete the activity and the quiz below this video."</div>
</section>""")

page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size: A4; margin: 15mm; }}
body {{ font-family: Helvetica, Arial, sans-serif; color:#23262b; font-size: 10pt; line-height:1.45; }}
.top {{ display:flex; align-items:center; gap:12px; border-bottom:2px solid #b76e79; padding-bottom:8px; margin-bottom: 10px; }}
.top img {{ width:44px; height:44px; border-radius:50%; }}
h1 {{ font-size: 19pt; margin: 6px 0; }}
section {{ page-break-inside: avoid; border:1.5px solid #ead9dc; border-radius:10px; padding:10px 14px; margin: 12px 0; }}
h2 {{ font-size: 13pt; margin: 2px 0 2px; }}
.kicker {{ font-size:8pt; text-transform:uppercase; letter-spacing:1px; color:#b76e79; font-weight:700; }}
.meta {{ color:#6b7280; font-size:8.5pt; margin: 0 0 6px; }}
.box {{ background:#f6eef0; border-radius:8px; padding:6px 10px; margin:6px 0; }}
ol {{ margin: 4px 0; padding-left: 18px; }} li {{ margin: 2px 0; }}
</style></head><body>
<div class="top"><img src="data:image/png;base64,{LOGO}"><div><b>WAMUGII TECH SOLUTIONS</b><br><span style="color:#b76e79;font-size:8.5pt">Instructor guide</span></div></div>
<h1>{html.escape(COURSE['title'])} — Video recording scripts</h1>
<p>These lessons do not have a matched video yet. Record a short video for each using the outline below, upload it to YouTube (Public or Unlisted), then paste the link into the lesson's <b>Video URL</b> in the admin panel (Admin → Courses → {html.escape(COURSE['title'])} → Lessons → Edit). Tips: record in a quiet room, phone horizontal at eye level, light facing you, and keep each video under 8 minutes.</p>
{''.join(blocks)}
</body></html>"""

async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        await pg.set_content(page, wait_until="load")
        await pg.pdf(path=str(OUT), format="A4", print_background=True)
        await b.close()
asyncio.run(main())
print("ok", len(blocks), "scripts")
