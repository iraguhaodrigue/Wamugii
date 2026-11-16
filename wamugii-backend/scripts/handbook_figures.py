"""Diagrams for the course handbooks, drawn as plain SVG.

Each function returns an SVG string. Chapters ask for a figure with
``[[fig:name|caption]]``; the handbook builder looks the name up in FIGURES.
All numbers shown in the diagrams match the worked examples in the chapters.
"""
from html import escape

TEAL = "#0e7490"
CYAN = "#06b6d4"
VIOLET = "#6d28d9"
INK = "#1e293b"
MUTED = "#64748b"
LINE = "#cbd5e1"
SOFT_T = "#ecfeff"
SOFT_V = "#f5f3ff"
GREEN = "#047857"
RED = "#b91c1c"
AMBER = "#b45309"

FONT = "font-family:Inter,Helvetica,Arial,sans-serif"


def _svg(w, h, body):
    return (f'<svg viewBox="0 0 {w} {h}" width="100%" style="max-width:{w}px;{FONT}" '
            f'xmlns="http://www.w3.org/2000/svg" role="img">{body}</svg>')


def _t(x, y, s, size=13, fill=INK, weight=400, anchor="middle"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="{anchor}">{escape(s)}</text>')


def _box(x, y, w, h, fill=SOFT_T, stroke=TEAL, r=10):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>'


def _arrow(x1, y1, x2, y2, color=MUTED, width=1.8):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" '
            f'marker-end="url(#ah)"/>')


ARROW_DEF = (f'<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
             f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/></marker></defs>')


def circles():
    b = f'<ellipse cx="300" cy="150" rx="285" ry="140" fill="{SOFT_T}" stroke="{TEAL}" stroke-width="2"/>'
    b += f'<ellipse cx="340" cy="170" rx="200" ry="100" fill="#cffafe" stroke="{CYAN}" stroke-width="2"/>'
    b += f'<ellipse cx="380" cy="190" rx="110" ry="58" fill="{SOFT_V}" stroke="{VIOLET}" stroke-width="2"/>'
    b += _t(300, 36, "Artificial intelligence", 15, TEAL, 700)
    b += _t(300, 54, "rules, search, planning, learning", 11, MUTED)
    b += _t(320, 96, "Machine learning", 14, "#0e7490", 700)
    b += _t(320, 113, "learns patterns from data", 11, MUTED)
    b += _t(380, 186, "Deep learning", 14, VIOLET, 700)
    b += _t(380, 204, "many-layered neural networks", 10.5, MUTED)
    return _svg(600, 300, b)


def waves():
    pts = [(40, 210), (90, 150), (140, 110), (190, 190), (240, 220), (290, 140), (330, 120),
           (370, 200), (420, 215), (470, 160), (520, 120), (560, 70), (600, 40)]
    path = "M" + " L".join(f"{x},{y}" for x, y in pts)
    b = ARROW_DEF + f'<line x1="30" y1="240" x2="620" y2="240" stroke="{LINE}" stroke-width="1.5"/>'
    b += f'<path d="{path}" fill="none" stroke="{TEAL}" stroke-width="3" stroke-linejoin="round"/>'
    for x, lab in [(40, "1950s"), (140, "1960s"), (215, "1970s"), (330, "1980s"), (395, "1990s"), (500, "2012"), (600, "2020s")]:
        b += _t(x, 258, lab, 11, MUTED)
    b += f'<rect x="170" y="40" width="90" height="200" fill="#e0f2fe" opacity="0.6"/>'
    b += f'<rect x="355" y="40" width="80" height="200" fill="#e0f2fe" opacity="0.6"/>'
    b += _t(215, 60, "1st AI winter", 11, "#0369a1", 600)
    b += _t(395, 60, "2nd AI winter", 11, "#0369a1", 600)
    b += _t(110, 95, "early optimism", 11, INK, 600)
    b += _t(300, 105, "expert systems", 11, INK, 600)
    b += _t(540, 178, "deep learning", 11, VIOLET, 700)
    b += _t(568, 30, "LLMs", 11, VIOLET, 700)
    b += _t(20, 140, "interest", 11, MUTED, anchor="start").replace("<text", '<text transform="rotate(-90 20 140)"')
    return _svg(640, 270, b)


def agent():
    b = ARROW_DEF
    b += _box(30, 60, 170, 120, "#f8fafc", LINE)
    b += _t(115, 50, "ENVIRONMENT", 12, MUTED, 700)
    b += _t(115, 110, "the world:", 12, MUTED)
    b += _t(115, 128, "roads, weather,", 12, MUTED)
    b += _t(115, 146, "people, data", 12, MUTED)
    b += _box(380, 60, 190, 120)
    b += _t(475, 50, "AGENT", 12, TEAL, 700)
    b += _t(475, 112, "decides what to do", 13, INK, 600)
    b += _t(475, 132, "(agent function)", 11, MUTED)
    b += f'<path d="M200,85 C270,40 310,40 378,85" fill="none" stroke="{TEAL}" stroke-width="2" marker-end="url(#ah)"/>'
    b += _t(290, 38, "percepts, via SENSORS", 12, TEAL, 600)
    b += f'<path d="M378,155 C310,200 270,200 202,155" fill="none" stroke="{VIOLET}" stroke-width="2" marker-end="url(#ah)"/>'
    b += _t(290, 212, "actions, via ACTUATORS", 12, VIOLET, 600)
    return _svg(600, 225, b)


def searchmap():
    nodes = {"Kigali": (70, 150), "Muhanga": (230, 230), "Musanze": (250, 60), "Ngororero": (400, 200), "Rubavu": (530, 90)}
    h = {"Kigali": 120, "Muhanga": 100, "Musanze": 55, "Ngororero": 60, "Rubavu": 0}
    edges = [("Kigali", "Muhanga", 50), ("Kigali", "Musanze", 90), ("Muhanga", "Ngororero", 45),
             ("Ngororero", "Rubavu", 85), ("Musanze", "Rubavu", 65)]
    b = ""
    for a, c, d in edges:
        (x1, y1), (x2, y2) = nodes[a], nodes[c]
        b += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{LINE}" stroke-width="3"/>'
        b += f'<rect x="{(x1+x2)/2-20}" y="{(y1+y2)/2-11}" width="40" height="20" rx="6" fill="white" stroke="{LINE}"/>'
        b += _t((x1 + x2) / 2, (y1 + y2) / 2 + 4, f"{d} km", 10.5, INK, 600)
    for n, (x, y) in nodes.items():
        goal = n == "Rubavu"
        start = n == "Kigali"
        b += f'<circle cx="{x}" cy="{y}" r="30" fill="{SOFT_V if goal else SOFT_T}" stroke="{VIOLET if goal else TEAL}" stroke-width="2"/>'
        b += _t(x, y + 4, n, 10 if len(n) > 7 else 11, INK, 700)
        b += _t(x, y + 46, f"h = {h[n]}", 10.5, VIOLET if goal else MUTED, 600)
        if start:
            b += _t(x, y - 38, "START", 10, TEAL, 700)
        if goal:
            b += _t(x, y - 38, "GOAL", 10, VIOLET, 700)
    return _svg(600, 290, b)


def workflow():
    stages = ["Define the problem", "Collect data", "Prepare data", "Train a model", "Evaluate", "Deploy", "Monitor & improve"]
    import math
    b = ARROW_DEF
    cx, cy, r = 300, 165, 120
    pos = []
    for i, s in enumerate(stages):
        a = -math.pi / 2 + i * 2 * math.pi / len(stages)
        pos.append((cx + r * 1.55 * math.cos(a), cy + r * math.sin(a)))
    for i in range(len(stages)):
        (x1, y1), (x2, y2) = pos[i], pos[(i + 1) % len(stages)]
        dx, dy = x2 - x1, y2 - y1
        L = (dx * dx + dy * dy) ** 0.5
        b += _arrow(x1 + dx / L * 62, y1 + dy / L * 26, x2 - dx / L * 66, y2 - dy / L * 28, TEAL if i < 6 else VIOLET, 2)
    for i, ((x, y), s) in enumerate(zip(pos, stages)):
        b += _box(x - 75, y - 20, 150, 40, SOFT_V if i == 6 else SOFT_T, VIOLET if i == 6 else TEAL, 18)
        b += _t(x, y + 4, f"{i+1}. {s}", 11.5, INK, 600)
    b += _t(cx, cy - 4, "a LOOP,", 13, VIOLET, 700)
    b += _t(cx, cy + 14, "not a straight line", 11.5, MUTED)
    return _svg(600, 330, b)


def kmeans():
    import random
    rnd = random.Random(4)
    groups = [((120, 90), TEAL, "students: heavy data"), ((330, 200), VIOLET, "traders: many calls"), ((470, 80), AMBER, "shop owners: high MoMo")]
    b = f'<line x1="40" y1="260" x2="580" y2="260" stroke="{LINE}"/><line x1="40" y1="20" x2="40" y2="260" stroke="{LINE}"/>'
    for (gx, gy), col, lab in groups:
        for _ in range(14):
            x, y = gx + rnd.gauss(0, 32), gy + rnd.gauss(0, 24)
            b += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="5" fill="{col}" opacity="0.75"/>'
        b += f'<path d="M{gx-9},{gy-9} L{gx+9},{gy+9} M{gx+9},{gy-9} L{gx-9},{gy+9}" stroke="{INK}" stroke-width="3.5"/>'
        b += _t(gx, gy + 80 if gy < 150 else gy - 58, lab, 11.5, col, 700)
    b += _t(310, 282, "data use per month →", 11, MUTED)
    b += _t(24, 140, "calls per month →", 11, MUTED).replace("<text", '<text transform="rotate(-90 24 140)"')
    return _svg(600, 290, b)


def rlloop():
    b = ARROW_DEF
    b += _box(60, 70, 160, 90)
    b += _t(140, 110, "AGENT", 14, TEAL, 700)
    b += _t(140, 130, "policy: state → action", 10.5, MUTED)
    b += _box(380, 70, 170, 90, "#f8fafc", LINE)
    b += _t(465, 110, "ENVIRONMENT", 14, MUTED, 700)
    b += _t(465, 130, "the world reacts", 10.5, MUTED)
    b += f'<path d="M220,90 L378,90" stroke="{VIOLET}" stroke-width="2.2" marker-end="url(#ah)"/>'
    b += _t(300, 80, "action", 12, VIOLET, 700)
    b += f'<path d="M380,130 L222,130" stroke="{TEAL}" stroke-width="2.2" marker-end="url(#ah)"/>'
    b += _t(300, 150, "new state", 12, TEAL, 700)
    b += f'<path d="M465,160 C465,225 140,225 140,162" fill="none" stroke="{GREEN}" stroke-width="2.2" marker-end="url(#ah)"/>'
    b += _t(300, 222, "reward  (+ good, − bad)", 12, GREEN, 700)
    return _svg(610, 240, b)


def splits():
    b = ""
    parts = [(0, 70, TEAL, "Training 70%", "the model learns here"), (70, 15, CYAN, "Validation 15%", "compare and tune"),
             (85, 15, VIOLET, "Test 15%", "open once, at the end")]
    for start, w, col, lab, sub in parts:
        x = 20 + start * 5.6
        b += f'<rect x="{x}" y="40" width="{w*5.6}" height="56" fill="{col}" rx="4"/>'
        b += _t(x + w * 2.8, 74, lab, 12.5, "white", 700)
        # Validation and test captions sit on different lines so they never overlap.
        b += _t(x + w * 2.8, 122 if start < 85 else 142, sub, 11, col, 600)
    b += _t(300, 26, "One dataset, three separate jobs", 12, MUTED, 600)
    return _svg(600, 155, b)


def fitcurves():
    import math
    xs = [0.5, 1.2, 1.9, 2.6, 3.3, 4.0, 4.7, 5.4]
    ys = [1.2, 2.6, 2.4, 3.9, 3.5, 4.4, 4.0, 4.9]
    panels = [("Underfitting", "too simple", "line"), ("Good fit", "captures the trend", "curve"), ("Overfitting", "memorises the noise", "wiggle")]
    b = ""
    for i, (title, sub, kind) in enumerate(panels):
        ox = 15 + i * 200
        sx = lambda x: ox + 15 + x * 30
        sy = lambda y: 175 - y * 28
        b += f'<rect x="{ox}" y="20" width="185" height="190" rx="10" fill="#f8fafc" stroke="{LINE}"/>'
        for x, y in zip(xs, ys):
            b += f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="4.5" fill="{TEAL}"/>'
        if kind == "line":
            d = f"M{sx(0.3):.1f},{sy(3.4):.1f} L{sx(5.6):.1f},{sy(3.4):.1f}"
            col = AMBER
        elif kind == "curve":
            d = "M" + " L".join(f"{sx(x):.1f},{sy(1.4 + 3.3 * math.log(1 + x) / math.log(6.6)):.1f}" for x in [0.3 + k * 0.1 for k in range(54)])
            col = GREEN
        else:
            pts = sorted(zip(xs, ys))
            d = f"M{sx(pts[0][0]):.1f},{sy(pts[0][1]):.1f}"
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                mx = (x1 + x2) / 2
                d += f" Q{sx(mx):.1f},{sy((y1 + y2) / 2 + (1.1 if y2 < y1 else -1.1)):.1f} {sx(x2):.1f},{sy(y2):.1f}"
            col = RED
        b += f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2.6"/>'
        b += _t(ox + 92, 192, title, 13, col, 700)
        b += _t(ox + 92, 206, sub, 10.5, MUTED)
    return _svg(615, 220, b)


def confusion(tp=40, fp=20, fn=10, tn=930, pos="fraud", neg="normal"):
    b = ""
    b += _t(330, 22, f"What really happened", 12, MUTED, 700)
    b += _t(250, 46, f"Really {pos}", 12, INK, 700)
    b += _t(420, 46, f"Really {neg}", 12, INK, 700)
    b += _t(95, 110, f"Predicted {pos}", 12, INK, 700, "middle")
    b += _t(95, 200, f"Predicted {neg}", 12, INK, 700, "middle")
    cells = [(170, 60, "#d1fae5", GREEN, f"TP = {tp}", "caught"), (340, 60, "#fee2e2", RED, f"FP = {fp}", "false alarm"),
             (170, 150, "#fee2e2", RED, f"FN = {fn}", "missed"), (340, 150, "#d1fae5", GREEN, f"TN = {tn}", "correctly left alone")]
    for x, y, fill, col, a, sub in cells:
        b += f'<rect x="{x}" y="{y}" width="160" height="80" rx="8" fill="{fill}" stroke="{col}" stroke-width="1.5"/>'
        b += _t(x + 80, y + 38, a, 16, col, 800)
        b += _t(x + 80, y + 58, sub, 11, col)
    return _svg(520, 240, b)


def neuron():
    b = ARROW_DEF
    ins = [("cloudiness 0.9", "w = 0.5"), ("rain forecast 0.8", "w = 0.8"), ("already raining 0", "w = 1.0")]
    for i, (lab, w) in enumerate(ins):
        y = 50 + i * 70
        b += _box(10, y - 18, 150, 36, "#f8fafc", LINE, 18)
        b += _t(85, y + 4, lab, 11.5, INK, 600)
        b += _arrow(160, y, 290, 140, TEAL, 1.8)
        b += _t(225, y + (8 if i == 0 else 18 if i == 1 else -4) + (0 if i != 1 else -14), w, 11, VIOLET, 700)
    b += f'<circle cx="335" cy="140" r="44" fill="{SOFT_T}" stroke="{TEAL}" stroke-width="2"/>'
    b += _t(335, 136, "Σ + bias", 13, INK, 700)
    b += _t(335, 154, "bias = −0.6", 10.5, MUTED)
    b += _arrow(379, 140, 450, 140, TEAL, 2)
    b += _box(452, 116, 70, 48, SOFT_V, VIOLET)
    b += _t(487, 136, "activ-", 11, VIOLET, 700)
    b += _t(487, 151, "ation", 11, VIOLET, 700)
    b += _arrow(522, 140, 560, 140, TEAL, 2)
    b += _t(335, 225, "0.9×0.5 + 0.8×0.8 + 0×1.0 − 0.6 = 0.49 → fires: take the umbrella", 11.5, INK, 600)
    return _svg(600, 240, b)


def network():
    layers = [4, 6, 6, 3]
    names = ["input layer", "hidden layer 1", "hidden layer 2", "output layer"]
    xs = [70, 230, 390, 540]
    b = ""
    coords = []
    for n, x in zip(layers, xs):
        top = 140 - (n - 1) * 20
        coords.append([(x, top + j * 40) for j in range(n)])
    for a, c in zip(coords, coords[1:]):
        for (x1, y1) in a:
            for (x2, y2) in c:
                b += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{LINE}" stroke-width="1"/>'
    for i, layer in enumerate(coords):
        col = TEAL if i == 0 else VIOLET if i == 3 else CYAN
        for (x, y) in layer:
            b += f'<circle cx="{x}" cy="{y}" r="13" fill="white" stroke="{col}" stroke-width="2.4"/>'
        b += _t(xs[i], 270, names[i], 11.5, col, 700)
    b += _t(150, 25, "edges", 11, MUTED, 600) + _t(310, 25, "shapes", 11, MUTED, 600) + _t(465, 25, "objects", 11, MUTED, 600)
    return _svg(610, 285, b)


def descent():
    import math
    sx = lambda w: 40 + w * 80
    sy = lambda L: 240 - L * 18
    d = "M" + " L".join(f"{sx(w):.1f},{sy((w-3)**2):.1f}" for w in [k * 0.05 for k in range(0, 121)] if (w - 3) ** 2 <= 11.5)
    b = ARROW_DEF + f'<path d="{d}" fill="none" stroke="{TEAL}" stroke-width="2.6"/>'
    w = 0.0
    pts = []
    for _ in range(6):
        pts.append(w)
        w = w - 0.1 * 2 * (w - 3)
    for a, c in zip(pts, pts[1:]):
        b += f'<line x1="{sx(a):.1f}" y1="{sy((a-3)**2):.1f}" x2="{sx(c):.1f}" y2="{sy((c-3)**2):.1f}" stroke="{VIOLET}" stroke-width="2" marker-end="url(#ah)"/>'
    for i, a in enumerate(pts):
        b += f'<circle cx="{sx(a):.1f}" cy="{sy((a-3)**2):.1f}" r="5" fill="{VIOLET}"/>'
    b += f'<circle cx="{sx(3)}" cy="{sy(0)}" r="6" fill="{GREEN}"/>'
    b += _t(sx(3) + 70, sy(0) - 8, "lowest loss (w = 3)", 11.5, GREEN, 700)
    b += _t(sx(0) + 6, sy(9) - 10, "start: w = 0, loss = 9", 11.5, VIOLET, 700, "start")
    b += _t(300, 268, "weight w →", 11, MUTED)
    b += _t(20, 140, "loss →", 11, MUTED).replace("<text", '<text transform="rotate(-90 20 140)"')
    return _svg(560, 280, b)


def attention():
    words = ["The", "farmer", "sold", "the", "cow", "because", "it", "was", "old"]
    weights = {"farmer": 0.21, "cow": 0.62, "sold": 0.07, "old": 0.06}
    xs = [40 + i * 66 for i in range(len(words))]
    b = ""
    itx = xs[6]
    for w, x in zip(words, xs):
        if w in weights and w != "it":
            k = weights[w]
            b += f'<path d="M{itx},120 Q{(itx+x)/2},{120-160*k-30} {x},120" fill="none" stroke="{VIOLET}" stroke-width="{1+14*k:.1f}" opacity="{0.35+0.6*k:.2f}"/>'
            b += _t((itx + x) / 2, 120 - 80 * k - 20, f"{k:.2f}", 11, VIOLET, 700)
    for i, (w, x) in enumerate(zip(words, xs)):
        hl = w == "it"
        b += f'<rect x="{x-30}" y="120" width="60" height="32" rx="8" fill="{SOFT_V if hl else SOFT_T}" stroke="{VIOLET if hl else TEAL}" stroke-width="{2.4 if hl else 1.4}"/>'
        b += _t(x, 141, w, 12.5, INK, 700 if hl or w == "cow" else 500)
    b += _t(300, 185, "How much 'it' attends to each word (illustrative numbers)", 11, MUTED)
    return _svg(610, 195, b)


def llmstages():
    b = ARROW_DEF
    stages = [("1. Pre-training", "predict the next token", "on huge amounts of text"), ("2. Fine-tuning", "learn from examples of", "good instructions & answers"),
              ("3. Preference tuning", "people rank answers;", "model moves toward the best")]
    for i, (a, s1, s2) in enumerate(stages):
        x = 15 + i * 200
        b += _box(x, 30, 175, 100, SOFT_V if i == 2 else SOFT_T, VIOLET if i == 2 else TEAL)
        b += _t(x + 87, 62, a, 13, VIOLET if i == 2 else TEAL, 700)
        b += _t(x + 87, 86, s1, 11, INK)
        b += _t(x + 87, 103, s2, 11, INK)
        if i < 2:
            b += _arrow(x + 177, 80, x + 213, 80, MUTED, 2)
    b += _t(102, 150, "knows language, not yet helpful", 10.5, MUTED)
    b += _t(302, 150, "follows instructions", 10.5, MUTED)
    b += _t(502, 150, "more helpful and safer", 10.5, MUTED)
    return _svg(610, 160, b)


def riskpyramid():
    levels = [("Unacceptable — banned", "#fecaca", RED, "social scoring, manipulation"), ("High risk — strict duties", "#fed7aa", AMBER, "hiring, credit, education, medical"),
              ("Limited risk — be transparent", "#fef3c7", "#a16207", "chatbots, deepfakes must be labelled"), ("Minimal risk — no special duties", "#d1fae5", GREEN, "spam filters, video games")]
    b = ""
    for i, (lab, fill, col, ex) in enumerate(levels):
        y = 20 + i * 60
        half_top = 85 + i * 68
        half_bot = 85 + (i + 1) * 68
        cx = 300
        b += f'<path d="M{cx-half_top},{y} L{cx+half_top},{y} L{cx+half_bot},{y+56} L{cx-half_bot},{y+56} z" fill="{fill}" stroke="{col}" stroke-width="1.4"/>'
        b += _t(cx, y + 25, lab, 12.5, col, 800)
        b += _t(cx, y + 43, ex, 10.5, INK)
    return _svg(600, 270, b)


def tradeoff():
    # threshold, fraud caught (of 50), precision %, recall %  (flagged: 32, 60, 100, 200)
    rows = [(0.9, 30, 94, 60), (0.7, 40, 67, 80), (0.5, 46, 46, 92), (0.3, 49, 25, 98)]
    b = f'<line x1="60" y1="210" x2="560" y2="210" stroke="{LINE}"/><line x1="60" y1="20" x2="60" y2="210" stroke="{LINE}"/>'
    for i, (thr, _tp, prec, rec) in enumerate(rows):
        x = 120 + i * 125
        b += f'<rect x="{x-38}" y="{210-prec*1.8}" width="34" height="{prec*1.8}" fill="{TEAL}" rx="3"/>'
        b += f'<rect x="{x+4}" y="{210-rec*1.8}" width="34" height="{rec*1.8}" fill="{VIOLET}" rx="3"/>'
        b += _t(x - 21, 205 - prec * 1.8, f"{prec}%", 10.5, TEAL, 700)
        b += _t(x + 21, 205 - rec * 1.8, f"{rec}%", 10.5, VIOLET, 700)
        b += _t(x, 228, f"flag if > {thr}", 11, INK, 600)
    b += f'<rect x="215" y="262" width="12" height="12" fill="{TEAL}"/>' + _t(233, 273, "precision", 11, TEAL, 700, "start")
    b += f'<rect x="315" y="262" width="12" height="12" fill="{VIOLET}"/>' + _t(333, 273, "recall", 11, VIOLET, 700, "start")
    b += _t(310, 250, "Lower threshold → more flags → recall up, precision down", 11, MUTED)
    return _svg(600, 285, b)


FIGURES = {
    "circles": circles, "waves": waves, "agent": agent, "searchmap": searchmap, "workflow": workflow,
    "kmeans": kmeans, "rlloop": rlloop, "splits": splits, "fitcurves": fitcurves, "confusion": confusion,
    "neuron": neuron, "network": network, "descent": descent, "attention": attention, "llmstages": llmstages,
    "riskpyramid": riskpyramid, "tradeoff": tradeoff,
}
