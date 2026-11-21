"""Build assets/banner-2.svg: the hero banner.

- Name types itself out (typewriter) with a blinking cursor, holds, erases, loops
- "currently building" status pill with words that slide in and out
- floating isometric cubes, orbiting rings, scan sweep

Run:  python scripts/banner.py && python scripts/compose.py
Uses SMIL <animate> for the typewriter (works inside GitHub's <img> sandbox) and CSS for the rest.
"""
import os
from xml.sax.saxutils import escape as e

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONO = "ui-monospace,SFMono-Regular,Consolas,Menlo,monospace"
SANS = "-apple-system,Segoe UI,Helvetica,Arial,sans-serif"
K = 0.866
H = 340
NAME = "Collins Maina"
NAME_W = 440  # fixed text width so the per-letter reveal lines up
NX = 56


def cube(cx, cy, s, top, left, right, cls, delay):
    t = f"{cx},{cy-s} {cx+K*s:.1f},{cy-s/2} {cx},{cy} {cx-K*s:.1f},{cy-s/2}"
    l = f"{cx-K*s:.1f},{cy-s/2} {cx},{cy} {cx},{cy+s} {cx-K*s:.1f},{cy+s/2}"
    r = f"{cx},{cy} {cx+K*s:.1f},{cy-s/2} {cx+K*s:.1f},{cy+s/2} {cx},{cy+s}"
    return (f'<g class="{cls}" style="animation-delay:{delay}s"><polygon points="{l}" fill="{left}"/>'
            f'<polygon points="{r}" fill="{right}"/><polygon points="{t}" fill="{top}"/>'
            f'<polyline points="{t}" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="1"/>'
            f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy+s}" stroke="#fff" stroke-opacity=".18"/></g>')


# ---- typewriter timeline (fractions of one 11s loop) ----
n = len(NAME)
steps = [(NAME_W * i / n) for i in range(n + 1)]
times, widths = [0.0], [0.0]
t0, t1 = 0.05, 0.27           # typing
for i in range(1, n + 1):
    times.append(t0 + (t1 - t0) * i / n)
    widths.append(steps[i])
e0, e1 = 0.86, 0.95           # erasing
for j in range(1, n + 1):
    times.append(e0 + (e1 - e0) * j / n)
    widths.append(steps[n - j])
kt = ";".join(f"{x:.4f}" for x in times)
clip_w = ";".join(f"{w + 8:.1f}" for w in widths)
cur_x = ";".join(f"{NX + w + 4:.1f}" for w in widths)

roles = ["web apps", "automation", "APIs", "agents"]
role_txt = "".join(
    f'<text class="role" style="animation-delay:{i*2}s" x="276" y="249" font-family="{MONO}" font-size="16" font-weight="700" fill="#7ff0dc">{e(r)}<tspan fill="#00C9A7" class="cur">_</tspan></text>'
    for i, r in enumerate(roles))
cubes = (cube(690, 180, 70, "#5eead4", "#0e7f73", "#0a5a66", "fl a", 0)
         + cube(790, 130, 44, "#7ff0dc", "#139488", "#0d6f7a", "fl b", .8)
         + cube(610, 110, 34, "#a7f3e6", "#1aa99b", "#128a92", "fl c", 1.6)
         + cube(800, 225, 28, "#5eead4", "#0e7f73", "#0a5a66", "fl b", 2.2))

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{H}" viewBox="0 0 900 {H}">
<defs>
<radialGradient id="g1" cx="78%" cy="45%" r="55%"><stop offset="0" stop-color="#00C9A7" stop-opacity=".30"/><stop offset="1" stop-color="#00C9A7" stop-opacity="0"/></radialGradient>
<radialGradient id="g2" cx="0%" cy="100%" r="60%"><stop offset="0" stop-color="#2C5364" stop-opacity=".6"/><stop offset="1" stop-color="#2C5364" stop-opacity="0"/></radialGradient>
<pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M30 0H0V30" fill="none" stroke="#fff" stroke-opacity=".045"/></pattern>
<linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="#00C9A7"/><stop offset="1" stop-color="#2C5364"/></linearGradient>
<linearGradient id="name" x1="0" x2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#9ff5e6"/></linearGradient>
<linearGradient id="pillg" x1="0" x2="1"><stop offset="0" stop-color="#00C9A7" stop-opacity=".16"/><stop offset="1" stop-color="#00C9A7" stop-opacity=".04"/></linearGradient>
<filter id="blur"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="rc"><rect width="900" height="{H}" rx="18"/></clipPath>
<clipPath id="tc"><rect x="{NX-6}" y="84" width="0" height="92"><animate attributeName="width" dur="11s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt}" values="{clip_w}"/></rect></clipPath>
</defs>
<style>
.fl{{animation:float 5s ease-in-out infinite}}.fl.b{{animation-duration:6.5s}}.fl.c{{animation-duration:4.2s}}
@keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-12px)}}}}
.sh{{animation:shadow 5s ease-in-out infinite;transform-origin:700px 280px}}
@keyframes shadow{{0%,100%{{transform:scale(1);opacity:.6}}50%{{transform:scale(.85);opacity:.35}}}}
.role{{opacity:0;animation:cyc 8s infinite}}
@keyframes cyc{{0%{{opacity:0;transform:translateY(10px)}}4%,21%{{opacity:1;transform:translateY(0)}}25%,100%{{opacity:0;transform:translateY(-10px)}}}}
.cur{{animation:blink 1s steps(1) infinite}}@keyframes blink{{50%{{opacity:0}}}}
.ring{{stroke-dasharray:6 10;animation:spin 24s linear infinite;transform-origin:700px 180px}}.ring.rev{{animation-direction:reverse}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.pulse{{animation:pulse 3s ease-in-out infinite}}@keyframes pulse{{0%,100%{{opacity:.7}}50%{{opacity:1}}}}
.scan{{animation:scan 6s linear infinite}}@keyframes scan{{from{{transform:translateX(-160px) skewX(-18deg)}}to{{transform:translateX(1060px) skewX(-18deg)}}}}
.live{{animation:live 1.8s ease-in-out infinite}}@keyframes live{{50%{{opacity:.35}}}}
.bar{{animation:barin 11s ease-out infinite;transform-origin:58px 0}}
@keyframes barin{{0%,4%{{transform:scaleX(0)}}30%,86%{{transform:scaleX(1)}}96%,100%{{transform:scaleX(0)}}}}
</style>
<rect width="900" height="{H}" rx="18" fill="#080d12"/>
<rect width="900" height="{H}" rx="18" fill="url(#grid)"/>
<rect width="900" height="{H}" rx="18" fill="url(#g1)" class="pulse"/>
<rect width="900" height="{H}" rx="18" fill="url(#g2)"/>
<g clip-path="url(#rc)"><rect class="scan" y="0" width="90" height="{H}" fill="#00C9A7" opacity=".07"/></g>
<ellipse class="ring" cx="700" cy="180" rx="190" ry="82" fill="none" stroke="#00C9A7" stroke-opacity=".35"/>
<ellipse class="ring rev" cx="700" cy="180" rx="130" ry="56" fill="none" stroke="#5eead4" stroke-opacity=".25"/>
<circle r="5" fill="#00C9A7"><animateMotion dur="9s" repeatCount="indefinite" path="M510,180 a190,82 0 1,1 380,0 a190,82 0 1,1 -380,0"/></circle>
<circle r="3.5" fill="#fff"><animateMotion dur="6s" repeatCount="indefinite" path="M570,180 a130,56 0 1,0 260,0 a130,56 0 1,0 -260,0"/></circle>
<ellipse class="sh" cx="700" cy="280" rx="95" ry="16" fill="#000" filter="url(#blur)"/>
{cubes}
<text x="56" y="68" font-family="{MONO}" font-size="14" fill="#00C9A7">~/coll-ins <tspan fill="#5b6b76">on</tspan> main <tspan fill="#28c840">&#9679;</tspan></text>
<text x="{NX}" y="150" font-family="{SANS}" font-size="64" font-weight="800" fill="url(#name)" letter-spacing="-1.5" textLength="{NAME_W}" lengthAdjust="spacingAndGlyphs" clip-path="url(#tc)">{NAME}</text>
<rect x="{NX}" y="98" width="4" height="62" rx="2" fill="#00C9A7" filter="url(#glow)"><animate attributeName="x" dur="11s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt}" values="{cur_x}"/><animate attributeName="opacity" dur="0.9s" repeatCount="indefinite" calcMode="discrete" values="1;0" keyTimes="0;0.5"/></rect>
<rect class="bar" x="58" y="172" width="70" height="4" rx="2" fill="url(#bar)"/>
<text x="56" y="208" font-family="{SANS}" font-size="20" fill="#9fb0ba">Software engineer &#183; Nairobi, Kenya</text>
<rect x="56" y="226" width="376" height="38" rx="19" fill="url(#pillg)" stroke="#00C9A7" stroke-opacity=".4"/>
<circle class="live" cx="78" cy="245" r="4.5" fill="#28c840" filter="url(#glow)"/>
<text x="94" y="250" font-family="{MONO}" font-size="14" fill="#8fa1ac">currently building</text>
<text x="252" y="250" font-family="{MONO}" font-size="16" fill="#00C9A7">&#8250;</text>
{role_txt}
</svg>'''
open(os.path.join(ROOT, "assets", "banner-2.svg"), "w", encoding="utf-8").write(svg)
print("banner-2.svg", round(len(svg) / 1024, 1), "KB")
