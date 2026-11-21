"""Build the README slices in assets/s/ from the pieces in assets/.

Every slice is an opaque dark image, so the README reads as one seamless block in GitHub
light and dark mode, while each slice can still carry its own link (cards -> repos,
footer pills -> LinkedIn / GitHub / 3D site).

Run after graphs.py:  python scripts/graphs.py && python scripts/compose.py
"""
import os, re
from xml.sax.saxutils import escape as e

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "assets")
OUT = os.path.join(A, "s")
os.makedirs(OUT, exist_ok=True)
MONO = "ui-monospace,SFMono-Regular,Consolas,Menlo,monospace"
SANS = "-apple-system,Segoe UI,Helvetica,Arial,sans-serif"
BG = "#0d1117"


def read(name):
    return open(os.path.join(A, name), encoding="utf-8").read()


def place(svg, x, y, w):
    m = re.match(r'\s*<svg[^>]*?width="([\d.]+)" height="([\d.]+)" viewBox="([^"]+)"[^>]*>', svg)
    ow, oh, vb = float(m.group(1)), float(m.group(2)), m.group(3)
    h = oh * w / ow
    inner = svg[m.end():].rsplit("</svg>", 1)[0]
    return f'<svg x="{x}" y="{y}" width="{w}" height="{h:.1f}" viewBox="{vb}">{inner}</svg>', h


def save(name, w, h, body):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h:.0f}" viewBox="0 0 {w} {h:.0f}">'
           f'<rect width="{w}" height="{h:.0f}" fill="{BG}"/>{body}</svg>')
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(svg)


def heading(label, sub=""):
    b = (f'<text x="28" y="56" font-family="{MONO}" font-size="14" letter-spacing="2.4" fill="#00C9A7">{e(label.upper())}</text>'
         f'<line x1="{28+len(label)*11+22}" y1="52" x2="872" y2="52" stroke="#fff" stroke-opacity=".09"/>')
    if sub:
        b += f'<text x="28" y="82" font-family="{SANS}" font-size="14" fill="#7d8f9a">{e(sub)}</text>'
    save_h = 110 if sub else 90
    return b, save_h


def pill(w, h, x, y, text, fill, stroke, color):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
            f'<text x="{x+w/2}" y="{y+h/2+5}" text-anchor="middle" font-family="{SANS}" font-size="15" font-weight="700" fill="{color}">{e(text)}</text>')


# ---------- hero: just the banner (clicking it opens the 3D site) ----------
b, h = place(read("banner-2.svg"), 0, 0, 900)
save("hero-3.svg", 900, h, b)

# ---------- find-me row right under the banner (3 x 33.3%, each its own link) ----------
for name, text, fill, stroke, color in [("t-linkedin", "LinkedIn  ↗", "#0A66C2", "#3b8ae6", "#ffffff"),
                                        ("t-github", "GitHub  ↗", "#161b22", "#2C5364", "#e6edf3"),
                                        ("t-site", "3D Portfolio  ↗", "#00C9A7", "#5eead4", "#04110f")]:
    save(name + ".svg", 300, 96, pill(236, 48, 32, 14, text, fill, stroke, color))

# ---------- "Selected work" heading ----------
hb, hh = heading("Selected work", "Tap a project to open its repo")
save("h-work.svg", 900, hh, hb)

# ---------- project cards (50% wide each) ----------
cards = [("card-connect.svg", "Open Connect"), ("card-esicom.svg", "Open Esicom Suppliers"),
         ("card-nexus.svg", "Open Nexus"), ("card-inventory.svg", "Open Inventory Management")]
for i, (f, label) in enumerate(cards):
    s, ch = place(read(f), 20, 16, 410)
    arrow = f'<text x="430" y="{16+ch+34}" text-anchor="end" font-family="{MONO}" font-size="13" fill="#00C9A7">{e(label)} ↗</text>'
    save(f"card-{i}.svg", 450, 16 + ch + 56, s + arrow)

# ---------- everything without its own link: one tall image (no seams) ----------
body, y = "", 0
hb, hh = heading("Activity", "Real contribution data from GitHub")
body += hb
y += hh
for j, f in enumerate(["graph-stats.svg", "graph-languages.svg"]):
    s, ch = place(read(f), 20 + j * 440, y, 420)
    body += s
y += ch + 16
for f in ["graph-streak.svg", "graph-activity.svg", "graph-heatmap.svg"]:
    s, ch = place(read(f), 20, y, 860)
    body += s
    y += ch + 16
y += 20
hb, hh = heading("About")
body += f'<g transform="translate(0,{y})">{hb}</g>'
y += hh + 6
x = 28
for t in ["Python", "Django", "Flask", "JavaScript", "React", "Tailwind", "Git", "Vercel"]:
    w = len(t) * 8.4 + 32
    body += (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="34" rx="17" fill="#00C9A7" fill-opacity=".1" stroke="#00C9A7" stroke-opacity=".4"/>'
             f'<text x="{x+w/2:.0f}" y="{y+22}" text-anchor="middle" font-family="{MONO}" font-size="13" fill="#5eead4">{e(t)}</text>')
    x += w + 12
y += 34 + 40
for i, line in enumerate(["Studying software engineering at Moringa School and shipping client and personal projects.",
                          "Most interested in automation, web apps, and fixing everyday problems with code."]):
    body += f'<text x="28" y="{y+i*28}" font-family="{SANS}" font-size="16" fill="#aebcc5">{e(line)}</text>'
y += 28 + 36
hb, hh = heading("Find me")
body += f'<g transform="translate(0,{y})">{hb}</g>'
y += hh - 10
save("rest.svg", 900, y, body)

# ---------- footer pills (3 x 33.3%) ----------
for name, text, fill, stroke, color in [("f-linkedin", "LinkedIn  ↗", "#0A66C2", "#3b8ae6", "#ffffff"),
                                        ("f-github", "GitHub  ↗", "#161b22", "#2C5364", "#e6edf3"),
                                        ("f-site", "3D Portfolio  ↗", "#00C9A7", "#5eead4", "#04110f")]:
    save(name + ".svg", 300, 140, pill(236, 48, 32, 28, text, fill, stroke, color))
print("slices:", len(os.listdir(OUT)))
