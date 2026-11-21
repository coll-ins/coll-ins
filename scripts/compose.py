"""Compose every piece in assets/ into one seamless dark image: assets/profile.svg

Run after graphs.py:  python scripts/graphs.py && python scripts/compose.py
One opaque dark canvas means the README looks the same in GitHub light and dark mode,
with no white gaps between blocks.
"""
import os, re
from xml.sax.saxutils import escape as e

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "assets")
MONO = "ui-monospace,SFMono-Regular,Consolas,Menlo,monospace"
SANS = "-apple-system,Segoe UI,Helvetica,Arial,sans-serif"
W = 900
M = 20  # side margin
BG = "#0b1015"


def read(name):
    return open(os.path.join(A, name), encoding="utf-8").read()


def place(svg, x, y, w, h=None):
    """Embed a standalone svg as a nested svg at x,y scaled to width w."""
    m = re.match(r'\s*<svg[^>]*?width="([\d.]+)" height="([\d.]+)" viewBox="([^"]+)"[^>]*>', svg)
    ow, oh, vb = float(m.group(1)), float(m.group(2)), m.group(3)
    h = h or oh * w / ow
    inner = svg[m.end():].rsplit("</svg>", 1)[0]
    return f'<svg x="{x}" y="{y}" width="{w}" height="{h:.1f}" viewBox="{vb}">{inner}</svg>', h


def header(y, label):
    return (f'<text x="{M+8}" y="{y}" font-family="{MONO}" font-size="13" letter-spacing="2" fill="#00C9A7">{e(label.upper())}</text>'
            f'<line x1="{M+8+len(label)*10+16}" y1="{y-4}" x2="{W-M-8}" y2="{y-4}" stroke="#fff" stroke-opacity=".08"/>')


def cardfix(svg, i):
    # keep each card's animation private so nothing collides inside one document
    svg = svg.replace('class="fl"', 'class="cfl"').replace(".fl{", ".cfl{").replace("float", "cfloat")
    svg = svg.replace('class="sw"', f'class="sw{i}"').replace(".sw{", f".sw{i}{{")
    svg = svg.replace("@keyframes sw{", f"@keyframes sw{i}{{").replace("animation:sw ", f"animation:sw{i} ")
    return svg


parts, y = [], 0
body = ""

# 1. banner
s, h = place(read("banner-2.svg"), 0, 0, W)
body += s
y = h + 36

# 2. selected work
body += header(y, "Selected work")
y += 22
cw = (W - 2 * M - 12) / 2
cards = ["card-connect.svg", "card-esicom.svg", "card-nexus.svg", "card-inventory.svg"]
for i, c in enumerate(cards):
    row = i // 2
    s, h = place(cardfix(read(c), i), M + (i % 2) * (cw + 12), y + row * (cw * 200 / 428 + 10), cw)
    body += s
y += 2 * (cw * 200 / 428 + 10) + 26

# 3. activity
body += header(y, "Activity")
y += 22
half = (W - 2 * M - 12) / 2
for j, f in enumerate(["graph-stats.svg", "graph-languages.svg"]):
    s, h = place(read(f), M + j * (half + 12), y, half)
    body += s
y += h + 12
for f in ["graph-streak.svg", "graph-activity.svg", "graph-heatmap.svg"]:
    s, h = place(read(f), M, y, W - 2 * M)
    body += s
    y += h + 12
y += 24

# 4. stack + now
body += header(y, "Stack")
y += 24
x = M + 8
for t in ["Python", "Django", "Flask", "JavaScript", "React", "Tailwind", "Git", "Vercel"]:
    w = len(t) * 8.4 + 30
    body += (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="32" rx="16" fill="#00C9A7" fill-opacity=".1" stroke="#00C9A7" stroke-opacity=".4"/>'
             f'<text x="{x+w/2:.0f}" y="{y+21}" text-anchor="middle" font-family="{MONO}" font-size="13" fill="#5eead4">{e(t)}</text>')
    x += w + 10
y += 32 + 40
body += header(y, "Now")
y += 28
for line in ["Studying software engineering at Moringa School and shipping client and personal projects.",
             "Most interested in automation, web apps, and fixing everyday problems with code."]:
    body += f'<text x="{M+8}" y="{y}" font-family="{SANS}" font-size="16" fill="#aebcc5">{e(line)}</text>'
    y += 26
H = y + 28

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}">'
       f'<rect width="{W}" height="{H:.0f}" fill="{BG}"/>{body}</svg>')
open(os.path.join(A, "profile.svg"), "w", encoding="utf-8").write(svg)
print("profile.svg", W, round(H), round(len(svg) / 1024), "KB")
