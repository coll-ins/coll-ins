"""Build the hero banner (assets/banner-2.svg) and the footer wave (assets/s/f-wave.svg).

Centered layout like the original profile:
- animated gradient waves across the top, name typed out with a cursor
- bold statements that type themselves out one after another
- "currently building" status pill, floating cubes at the sides
SMIL <animate> drives the typing (works inside GitHub's <img> sandbox); CSS drives the rest.

Run:  python scripts/banner.py && python scripts/compose.py
"""
import math, os
from xml.sax.saxutils import escape as e

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONO = "ui-monospace,SFMono-Regular,Consolas,Menlo,monospace"
SANS = "-apple-system,Segoe UI,Helvetica,Arial,sans-serif"
K = 0.866
W, H = 900, 360
CX = W / 2
NAME = "Collins Maina"
NAME_W = 440
STATEMENTS = ["Hi there, I'm Collins", "Software Engineer | Builder",
              "I turn ideas into working products", "Always shipping something new"]
CHAR_W = 12.4  # px per character for the statements (fixed via textLength)


def cube(cx, cy, s, top, left, right, cls, delay):
    t = f"{cx},{cy-s} {cx+K*s:.1f},{cy-s/2} {cx},{cy} {cx-K*s:.1f},{cy-s/2}"
    l = f"{cx-K*s:.1f},{cy-s/2} {cx},{cy} {cx},{cy+s} {cx-K*s:.1f},{cy+s/2}"
    r = f"{cx},{cy} {cx+K*s:.1f},{cy-s/2} {cx+K*s:.1f},{cy+s/2} {cx},{cy+s}"
    return (f'<g class="{cls}" style="animation-delay:{delay}s"><polygon points="{l}" fill="{left}"/>'
            f'<polygon points="{r}" fill="{right}"/><polygon points="{t}" fill="{top}"/>'
            f'<polyline points="{t}" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="1"/>'
            f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy+s}" stroke="#fff" stroke-opacity=".18"/></g>')


def wave_path(base, amp, period, width=1800, phase=0.0, step=15):
    """Closed shape from the top edge down to a sine wave line."""
    pts = []
    x = 0
    while x <= width:
        pts.append((x, base + amp * math.sin(2 * math.pi * (x / period) + phase)))
        x += step
    d = f"M0,0 L" + " L".join(f"{x},{y:.1f}" for x, y in pts) + f" L{width},0 Z"
    return d


def wave_path_bottom(base, amp, period, bottom, width=1800, phase=0.0, step=15):
    """Closed shape from a sine wave line down to the bottom edge."""
    pts = []
    x = 0
    while x <= width:
        pts.append((x, base + amp * math.sin(2 * math.pi * (x / period) + phase)))
        x += step
    return f"M0,{bottom} L" + " L".join(f"{x},{y:.1f}" for x, y in pts) + f" L{width},{bottom} Z"


def typed(times, widths):
    return ";".join(f"{t:.4f}" for t in times), widths


# ---------------- name typewriter (11s loop) ----------------
n = len(NAME)
steps = [NAME_W * i / n for i in range(n + 1)]
times, widths = [0.0], [0.0]
for i in range(1, n + 1):
    times.append(0.05 + 0.22 * i / n)
    widths.append(steps[i])
for j in range(1, n + 1):
    times.append(0.86 + 0.09 * j / n)
    widths.append(steps[n - j])
kt = ";".join(f"{x:.4f}" for x in times)
name_x0 = CX - NAME_W / 2
clip_w = ";".join(f"{(w + 8) if w else 0:.1f}" for w in widths)
cur_x = ";".join(f"{name_x0 + w + 3:.1f}" for w in widths)

# ---------------- statements typewriter (20s loop, 5s each) ----------------
LOOP = 20.0
SLOT = 0.25
st_defs, st_text, st_cur = "", "", ""
SY = 262  # baseline of statements
for k, text in enumerate(STATEMENTS):
    L = len(text) * CHAR_W
    x0 = CX - L / 2
    s = k * SLOT
    ts, ws, cs = [0.0], [0.0], [-100.0]
    nn = len(text)
    for i in range(1, nn + 1):
        ts.append(s + 0.02 + 0.07 * i / nn)
        ws.append(L * i / nn)
        cs.append(x0 + L * i / nn + 3)
    ts.append(s + 0.235)
    ws.append(0.0)
    cs.append(-100.0)
    ktk = ";".join(f"{t:.4f}" for t in ts)
    st_defs += (f'<clipPath id="sc{k}"><rect x="{x0-4:.1f}" y="{SY-30}" width="0" height="42">'
                f'<animate attributeName="width" dur="{LOOP}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{ktk}" values="{";".join(f"{(w+8) if w else 0:.1f}" for w in ws)}"/></rect></clipPath>')
    st_text += (f'<text x="{x0:.1f}" y="{SY}" font-family="{SANS}" font-size="25" font-weight="800" fill="#eafcf8" '
                f'textLength="{L:.1f}" lengthAdjust="spacingAndGlyphs" clip-path="url(#sc{k})" class="tw">{e(text)}</text>')
    st_cur += (f'<rect class="blink tw" x="-100" y="{SY-24}" width="3" height="30" rx="1.5" fill="#00C9A7" filter="url(#glow)">'
               f'<animate attributeName="x" dur="{LOOP}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{ktk}" values="{";".join(f"{c:.1f}" for c in cs)}"/></rect>')

static = f'<text class="st" x="{CX}" y="132" text-anchor="middle" font-family="{SANS}" font-size="62" font-weight="800" fill="url(#name)" letter-spacing="-1.5">{NAME}</text>'
for k, text in enumerate(STATEMENTS):
    static += (f'<text class="st sf" style="animation-delay:{k*5}s" x="{CX}" y="{SY}" text-anchor="middle" font-family="{SANS}" '
               f'font-size="25" font-weight="800" fill="#eafcf8">{e(text)}</text>')

roles = ["web apps", "automation", "APIs", "agents"]
PILL_X = CX - 188
role_txt = "".join(
    f'<text class="role" style="animation-delay:{i*2}s" x="{PILL_X+220}" y="{H-27}" font-family="{MONO}" font-size="16" font-weight="700" fill="#7ff0dc">{e(r)}<tspan fill="#00C9A7" class="cur">_</tspan></text>'
    for i, r in enumerate(roles))

cubes = (cube(110, 118, 40, "#5eead4", "#0e7f73", "#0a5a66", "fl a", 0)
         + cube(60, 190, 22, "#a7f3e6", "#1aa99b", "#128a92", "fl c", 1.2)
         + cube(790, 105, 48, "#7ff0dc", "#139488", "#0d6f7a", "fl b", .8)
         + cube(842, 185, 24, "#5eead4", "#0e7f73", "#0a5a66", "fl c", 2.0))

WAVE_BASE = 214
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
<linearGradient id="wg" x1="0" x2="1"><stop offset="0" stop-color="#0F2027"/><stop offset=".5" stop-color="#2C5364"/><stop offset="1" stop-color="#00C9A7"/></linearGradient>
<linearGradient id="wg2" x1="0" x2="1"><stop offset="0" stop-color="#2C5364"/><stop offset="1" stop-color="#00C9A7"/></linearGradient>
<radialGradient id="g1" cx="50%" cy="30%" r="60%"><stop offset="0" stop-color="#00C9A7" stop-opacity=".22"/><stop offset="1" stop-color="#00C9A7" stop-opacity="0"/></radialGradient>
<pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M30 0H0V30" fill="none" stroke="#fff" stroke-opacity=".045"/></pattern>
<linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="#00C9A7"/><stop offset="1" stop-color="#2C5364"/></linearGradient>
<linearGradient id="name" x1="0" x2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#b8fff2"/></linearGradient>
<linearGradient id="pillg" x1="0" x2="1"><stop offset="0" stop-color="#00C9A7" stop-opacity=".16"/><stop offset="1" stop-color="#00C9A7" stop-opacity=".04"/></linearGradient>
<filter id="blur"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="rc"><rect width="{W}" height="{H}" rx="18"/></clipPath>
<clipPath id="tc"><rect x="{name_x0-6:.1f}" y="70" width="0" height="92"><animate attributeName="width" dur="11s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt}" values="{clip_w}"/></rect></clipPath>
{st_defs}
</defs>
<style>
.fl{{animation:float 5s ease-in-out infinite}}.fl.b{{animation-duration:6.5s}}.fl.c{{animation-duration:4.2s}}
@keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-12px)}}}}
.w1{{animation:wv 11s linear infinite}}.w2{{animation:wv 17s linear infinite reverse}}.w3{{animation:wv 7s linear infinite}}
@keyframes wv{{from{{transform:translateX(0)}}to{{transform:translateX(-450px)}}}}
.role{{opacity:0;animation:cyc 8s infinite}}
@keyframes cyc{{0%{{opacity:0;transform:translateY(10px)}}4%,21%{{opacity:1;transform:translateY(0)}}25%,100%{{opacity:0;transform:translateY(-10px)}}}}
.cur,.blink{{animation:blink 1s steps(1) infinite}}@keyframes blink{{50%{{opacity:0}}}}
.pulse{{animation:pulse 3s ease-in-out infinite}}@keyframes pulse{{0%,100%{{opacity:.7}}50%{{opacity:1}}}}
.scan{{animation:scan 7s linear infinite}}@keyframes scan{{from{{transform:translateX(-160px) skewX(-18deg)}}to{{transform:translateX(1060px) skewX(-18deg)}}}}
.st{{display:none}}.sf{{opacity:0;animation:sfade 20s infinite}}
@keyframes sfade{{0%{{opacity:0}}2%,22%{{opacity:1}}25%,100%{{opacity:0}}}}
@media (max-width:640px){{.tw{{display:none}}.st{{display:inline}}}}
.live{{animation:live 1.8s ease-in-out infinite}}@keyframes live{{50%{{opacity:.35}}}}
.bar{{animation:barin 11s ease-out infinite;transform-origin:{CX}px 0}}
@keyframes barin{{0%,4%{{transform:scaleX(0)}}30%,86%{{transform:scaleX(1)}}96%,100%{{transform:scaleX(0)}}}}
</style>
<rect width="{W}" height="{H}" rx="18" fill="#080d12"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#grid)"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#g1)" class="pulse"/>
<g clip-path="url(#rc)">
<g class="w2" opacity=".45"><path d="{wave_path(WAVE_BASE+14, 14, 450, phase=1.6)}" fill="url(#wg2)"/></g>
<g class="w3" opacity=".7"><path d="{wave_path(WAVE_BASE+4, 11, 450, phase=3.1)}" fill="url(#wg)"/></g>
<g class="w1"><path d="{wave_path(WAVE_BASE-6, 12, 450)}" fill="url(#wg)"/></g>
<rect class="scan" y="0" width="90" height="{H}" fill="#00C9A7" opacity=".06"/>
</g>
{cubes}
<text x="{CX}" y="48" text-anchor="middle" font-family="{MONO}" font-size="14" fill="#7ff0dc">~/coll-ins <tspan fill="#8fa1ac">on</tspan> main <tspan fill="#28c840">&#9679;</tspan></text>
<text x="{name_x0:.1f}" y="132" font-family="{SANS}" font-size="64" font-weight="800" fill="url(#name)" letter-spacing="-1.5" textLength="{NAME_W}" lengthAdjust="spacingAndGlyphs" clip-path="url(#tc)" class="tw">{NAME}</text>
<rect x="{name_x0:.1f}" y="84" width="4" height="62" rx="2" fill="#00C9A7" filter="url(#glow)" class="blink tw"><animate attributeName="x" dur="11s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt}" values="{cur_x}"/></rect>
<rect class="bar" x="{CX-35}" y="150" width="70" height="4" rx="2" fill="url(#bar)"/>
<text x="{CX}" y="184" text-anchor="middle" font-family="{SANS}" font-size="18" fill="#cfe3ea">Software engineer &#183; Nairobi, Kenya</text>
{st_text}{st_cur}{static}
<rect x="{PILL_X}" y="{H-50}" width="376" height="38" rx="19" fill="url(#pillg)" stroke="#00C9A7" stroke-opacity=".4"/>
<circle class="live" cx="{PILL_X+22}" cy="{H-31}" r="4.5" fill="#28c840" filter="url(#glow)"/>
<text x="{PILL_X+38}" y="{H-26}" font-family="{MONO}" font-size="14" fill="#8fa1ac">currently building</text>
<text x="{PILL_X+196}" y="{H-26}" font-family="{MONO}" font-size="16" fill="#00C9A7">&#8250;</text>
{role_txt}
</svg>'''
open(os.path.join(ROOT, "assets", "banner-2.svg"), "w", encoding="utf-8").write(svg)
print("banner-2.svg", round(len(svg) / 1024, 1), "KB")

# ---------------- footer wave ----------------
FH = 150
fw = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{FH}" viewBox="0 0 {W} {FH}">
<defs>
<linearGradient id="fg" x1="0" x2="1"><stop offset="0" stop-color="#00C9A7"/><stop offset=".5" stop-color="#2C5364"/><stop offset="1" stop-color="#0F2027"/></linearGradient>
<linearGradient id="fg2" x1="0" x2="1"><stop offset="0" stop-color="#00C9A7"/><stop offset="1" stop-color="#2C5364"/></linearGradient>
</defs>
<style>
.w1{{animation:wv 11s linear infinite}}.w2{{animation:wv 17s linear infinite reverse}}.w3{{animation:wv 7s linear infinite}}
@keyframes wv{{from{{transform:translateX(0)}}to{{transform:translateX(-450px)}}}}
</style>
<rect width="{W}" height="{FH}" fill="#0d1117"/>
<text x="{CX}" y="42" text-anchor="middle" font-family="{SANS}" font-size="16" fill="#8fa1ac">Thanks for stopping by. Explore the projects above, and say hi.</text>
<g class="w2" opacity=".45"><path d="{wave_path_bottom(FH-62, 12, 450, FH, phase=1.2)}" fill="url(#fg2)"/></g>
<g class="w3" opacity=".7"><path d="{wave_path_bottom(FH-52, 10, 450, FH, phase=2.6)}" fill="url(#fg)"/></g>
<g class="w1"><path d="{wave_path_bottom(FH-44, 11, 450, FH)}" fill="url(#fg)"/></g>
</svg>'''
os.makedirs(os.path.join(ROOT, "assets", "s"), exist_ok=True)
open(os.path.join(ROOT, "assets", "s", "f-wave.svg"), "w", encoding="utf-8").write(fw)
print("f-wave.svg")
