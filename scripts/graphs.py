import json, os, math, datetime
from xml.sax.saxutils import escape as e
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = json.load(open("assets/stats.json"))
MONO = "ui-monospace,SFMono-Regular,Consolas,Menlo,monospace"
SANS = "-apple-system,Segoe UI,Helvetica,Arial,sans-serif"
today = datetime.date.fromisoformat(D["generated"])
days = {datetime.date.fromisoformat(k): v for k, v in D["calendar"].items()}
total = sum(days.values())

# grid start: the Sunday 52 weeks before this week's Sunday
this_sun = today - datetime.timedelta(days=(today.weekday() + 1) % 7)
start = this_sun - datetime.timedelta(weeks=52)
weeks = []
d = start
while d <= today:
    weeks.append([d + datetime.timedelta(days=i) for i in range(7)])
    d += datetime.timedelta(weeks=1)
wk_counts = [sum(days.get(x, 0) for x in w if x <= today) for w in weeks]
active_days = sum(1 for x, v in days.items() if x >= start)
best_week = max(wk_counts)
# streak
cur = best = run = 0
dd = start
while dd <= today:
    if days.get(dd, 0):
        run += 1
        best = max(best, run)
    else:
        run = 0
    dd += datetime.timedelta(days=1)

# common head
def head(w, h, extra_defs=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
<linearGradient id="fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#14202a"/><stop offset="1" stop-color="#0a1016"/></linearGradient>
<linearGradient id="bd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#00C9A7" stop-opacity=".7"/><stop offset=".5" stop-color="#2C5364" stop-opacity=".45"/><stop offset="1" stop-color="#00C9A7" stop-opacity=".12"/></linearGradient>
{extra_defs}</defs>
<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="16" fill="url(#fill)" stroke="url(#bd)" stroke-width="1.5"/>
'''

def title(t, sub=""):
    s = f'<text x="28" y="38" font-family="{MONO}" font-size="12" letter-spacing="1.6" fill="#00C9A7">{e(t.upper())}</text>'
    if sub:
        s += f'<text x="28" y="58" font-family="{SANS}" font-size="13" fill="#7d8f9a">{e(sub)}</text>'
    return s

# ---------- 1. stats card (rank) + streak card ----------
P = D.get("profile", {})
# streaks from the real calendar
cal_days = sorted(d for d in days if d <= today)
active_days = sum(1 for d in cal_days if days[d] > 0)
total = sum(days[d] for d in cal_days)
longest = (0, None, None)
run, run_start = 0, None
for d in cal_days:
    if days[d] > 0:
        if run == 0:
            run_start = d
        run += 1
        if run > longest[0]:
            longest = (run, run_start, d)
    else:
        run = 0
cur_end = today if days.get(today, 0) > 0 else today - datetime.timedelta(days=1)
cur, d = 0, cur_end
while days.get(d, 0) > 0:
    cur += 1
    d -= datetime.timedelta(days=1)
cur_start = cur_end - datetime.timedelta(days=cur - 1) if cur else None
best = longest[0]

# rank, same formula and weights as github-readme-stats
def exp_cdf(x): return 1 - 2 ** (-x)
def log_cdf(x): return x / (1 + x)
score = (2 * exp_cdf(P.get("commits", 0) / 250) + 3 * exp_cdf(P.get("prs", 0) / 50) + 1 * exp_cdf(P.get("issues", 0) / 25)
         + 1 * exp_cdf(P.get("reviews", 0) / 2) + 4 * log_cdf(P.get("stars", 0) / 50) + 1 * log_cdf(P.get("followers", 0) / 10)) / 12
pct = (1 - score) * 100
grade = "C"
for lim, g in ((1, "S"), (12.5, "A+"), (25, "A"), (37.5, "A-"), (50, "B+"), (62.5, "B"), (75, "B-"), (87.5, "C+"), (100, "C")):
    if pct <= lim:
        grade = g
        break

def fmt(d): return d.strftime("%b %d, %Y") if d else ""

w, h = 420, 230
s = head(w, h, '<style>.rg{stroke-dasharray:0 400;animation:rg 1.6s ease-out .2s forwards}@keyframes rg{to{stroke-dasharray:var(--l) 400}}.n{animation:up .9s ease-out both}@keyframes up{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}</style>') + title("Stats", f"@{D['user']} on GitHub")
rx, ry, rr = 92, 138, 46
RC = 2 * math.pi * rr
fill_len = RC * max(min(score * 1.0, 1), 0.04)
s += (f'<circle cx="{rx}" cy="{ry}" r="{rr}" fill="none" stroke="#1f2f3a" stroke-width="9"/>'
      f'<circle class="rg" style="--l:{fill_len:.1f}px" cx="{rx}" cy="{ry}" r="{rr}" fill="none" stroke="#00C9A7" stroke-width="9" stroke-linecap="round" transform="rotate(-90 {rx} {ry})"/>'
      f'<text x="{rx}" y="{ry+10}" text-anchor="middle" font-family="{SANS}" font-size="30" font-weight="800" fill="#f2f6f8">{grade}</text>')
rows = [("Commits", P.get("commits", 0)), ("Pull requests", P.get("prs", 0)), ("Issues", P.get("issues", 0)), ("Stars earned", P.get("stars", 0)), ("Followers", P.get("followers", 0))]
for i, (k, v) in enumerate(rows):
    y = 92 + i * 26
    s += (f'<g class="n" style="animation-delay:{i*.1}s"><circle cx="190" cy="{y-4}" r="3" fill="#00C9A7"/>'
          f'<text x="202" y="{y}" font-family="{SANS}" font-size="14" fill="#9fb0ba">{k}</text>'
          f'<text x="392" y="{y}" text-anchor="end" font-family="{MONO}" font-size="15" font-weight="700" fill="#f2f6f8">{v}</text></g>')
s += '</svg>'
open("assets/graph-stats.svg", "w", encoding="utf-8").write(s)

# streak card (full width)
w, h = 860, 170
s = head(w, h, f'<style>.fr{{stroke-dasharray:0 400;animation:fr 1.4s ease-out .3s forwards}}@keyframes fr{{to{{stroke-dasharray:{2*math.pi*40*min(cur/max(best,1),1):.1f} 400}}}}.n{{animation:up .9s ease-out both}}@keyframes up{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}</style>')
cols3 = [(143, str(total), "Total contributions", f"{fmt(cal_days[0])} - {fmt(cal_days[-1])}"),
         (430, str(cur), "Current streak", f"{fmt(cur_start)} - {fmt(cur_end)}" if cur else "no active streak today"),
         (717, str(best), "Longest streak", f"{fmt(longest[1])} - {fmt(longest[2])}")]
for i, (x, big, lab, sub) in enumerate(cols3):
    if i == 1:
        s += (f'<circle cx="{x}" cy="78" r="40" fill="none" stroke="#1f2f3a" stroke-width="7"/>'
              f'<circle class="fr" cx="{x}" cy="78" r="40" fill="none" stroke="#00C9A7" stroke-width="7" stroke-linecap="round" transform="rotate(-90 {x} 78)"/>'
              f'<text x="{x}" y="90" text-anchor="middle" font-family="{SANS}" font-size="36" font-weight="800" fill="#f2f6f8">{big}</text>')
        s += f'<text x="{x}" y="146" text-anchor="middle" font-family="{SANS}" font-size="14" font-weight="600" fill="#00C9A7">{lab}</text><text x="{x}" y="164" text-anchor="middle" font-family="{MONO}" font-size="11" fill="#7d8f9a">{e(sub)}</text>'
    else:
        s += (f'<g class="n" style="animation-delay:{i*.15}s"><text x="{x}" y="90" text-anchor="middle" font-family="{SANS}" font-size="44" font-weight="800" fill="#f2f6f8">{big}</text>'
              f'<text x="{x}" y="124" text-anchor="middle" font-family="{SANS}" font-size="14" font-weight="600" fill="#00C9A7">{lab}</text>'
              f'<text x="{x}" y="144" text-anchor="middle" font-family="{MONO}" font-size="11" fill="#7d8f9a">{e(sub)}</text></g>')
for x in (286, 573):
    s += f'<line x1="{x}" y1="38" x2="{x}" y2="140" stroke="#fff" stroke-opacity=".08"/>'
s += '</svg>'
open("assets/graph-streak.svg", "w", encoding="utf-8").write(s)

# ---------- 2. languages donut ----------
raw = D["languages"]
keep = {"Python", "JavaScript", "CSS", "HTML", "Shell"}
lang = [(n, b) for n, b in raw if n in keep]
other = sum(b for n, b in raw if n not in keep)
if other:
    lang.append(("Other", other))
tb = sum(b for _, b in lang)
cols = ["#00C9A7", "#5eead4", "#2C8FA6", "#1b6b7d", "#a7f3e6", "#3d5560"]
w, h = 420, 220
cx, cy, r = 110, 130, 56
C = 2 * math.pi * r
s = head(w, h, '<style>.seg{animation:draw 1.4s ease-out both}@keyframes draw{from{stroke-dasharray:0 1000}}</style>') + title("Languages", "By code written, original repos")
s += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#16222b" stroke-width="22"/>'
off = 0
for i, (n, b) in enumerate(lang):
    frac = b / tb
    ln = max(frac * C - 2, 0.5)
    s += f'<circle class="seg" style="animation-delay:{i*.15}s" cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{cols[i%len(cols)]}" stroke-width="22" stroke-dasharray="{ln:.2f} {C-ln:.2f}" stroke-dashoffset="{-off:.2f}" transform="rotate(-90 {cx} {cy})"/>'
    off += frac * C
s += f'<text x="{cx}" y="{cy+6}" text-anchor="middle" font-family="{SANS}" font-size="20" font-weight="800" fill="#f2f6f8">{lang[0][0]}</text>'
for i, (n, b) in enumerate(lang):
    y = 84 + i * 20
    s += f'<rect x="212" y="{y-9}" width="10" height="10" rx="3" fill="{cols[i%len(cols)]}"/><text x="230" y="{y}" font-family="{SANS}" font-size="13" fill="#c3d1d8">{e(n)}</text><text x="392" y="{y}" text-anchor="end" font-family="{MONO}" font-size="12" fill="#7d8f9a">{b/tb*100:.1f}%</text>'
s += '</svg>'
open("assets/graph-languages.svg", "w", encoding="utf-8").write(s)

# ---------- 3. daily activity (fat bars, last 60 days) ----------
NDAYS = 60
recent = [(x, days.get(x, 0)) for x in (today - datetime.timedelta(days=i) for i in range(NDAYS - 1, -1, -1))]
w, h = 860, 250
px0, px1, py0, py1 = 56, 836, 88, 198
mx = max(c for _, c in recent) or 1
top = math.ceil(mx / 10) * 10 if mx > 10 else mx
slot = (px1 - px0) / NDAYS
bw = slot * 0.7
defs = '''<linearGradient id="bar" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#00C9A7" stop-opacity=".35"/><stop offset="1" stop-color="#5eead4"/></linearGradient>
<style>.b{transform-box:fill-box;transform-origin:50% 100%;animation:gr .9s cubic-bezier(.2,.8,.2,1) both}@keyframes gr{from{transform:scaleY(0)}}</style>'''
s = head(w, h, defs) + title("Contribution activity", f"Contributions per day, last {NDAYS} days · {sum(c for _, c in recent)} contributions")
for g in range(0, 4):
    y = py1 - g * (py1 - py0) / 3
    s += (f'<line x1="{px0}" y1="{y:.1f}" x2="{px1}" y2="{y:.1f}" stroke="#fff" stroke-opacity=".07"/>'
          f'<text x="{px0-10}" y="{y+4:.1f}" text-anchor="end" font-family="{MONO}" font-size="11" fill="#6b7d88">{round(top*g/3)}</text>')
for i, (dday, c) in enumerate(recent):
    x = px0 + i * slot + (slot - bw) / 2
    hh = max(c / top * (py1 - py0), 3)
    fill = "url(#bar)" if c else "#1f2f3a"
    s += (f'<rect class="b" style="animation-delay:{i*0.015:.2f}s" x="{x:.1f}" y="{py1-hh:.1f}" width="{bw:.1f}" height="{hh:.1f}" rx="{min(bw/2,4):.1f}" fill="{fill}">'
          f'<title>{c} contribution{"s" if c != 1 else ""} on {dday.isoformat()}</title></rect>')
    if i % 10 == 0:
        s += f'<text x="{x+bw/2:.1f}" y="{py1+22}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="#6b7d88">{dday.strftime("%b %d")}</text>'
bi = max(range(NDAYS), key=lambda k: recent[k][1])
bx = px0 + bi * slot + slot / 2
by = py1 - recent[bi][1] / top * (py1 - py0)
s += f'<text x="{min(bx, px1-70):.1f}" y="{max(by-10,78):.1f}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="#5eead4">{recent[bi][1]} contributions</text>'
s += '</svg>'
open("assets/graph-activity.svg", "w", encoding="utf-8").write(s)

# ---------- 4. heatmap ----------
cell, gap = 16, 3
w = 56 + len(weeks) * (cell + gap) + 16
h = 268
levels = ["#22333f", "#0f6b5f", "#13a48e", "#1fd9b8", "#aefbee"]
def lvl(c):
    if c == 0: return 0
    if c == 1: return 1
    if c <= 4: return 2
    if c <= 9: return 3
    return 4
defs = '<style>.c{animation:pop .5s ease-out both}@keyframes pop{from{opacity:0;transform:scale(.4)}}.c{transform-box:fill-box;transform-origin:center}</style>'
s = head(w, h, defs) + title("Contribution map", f"{total} contributions across {active_days} active days")
gx, gy = 56, 86
seen = None
for i, wk in enumerate(weeks):
    m = wk[0].strftime("%b")
    if m != seen and wk[0].day <= 7:
        seen = m
        s += f'<text x="{gx + i*(cell+gap)}" y="{gy-8}" font-family="{MONO}" font-size="11" fill="#8ea0ab">{m}</text>'
    for j, dday in enumerate(wk):
        if dday > today: continue
        c = days.get(dday, 0)
        delay = (i * 0.012) + j * 0.01
        s += f'<rect class="c" style="animation-delay:{delay:.2f}s" x="{gx + i*(cell+gap)}" y="{gy + j*(cell+gap)}" width="{cell}" height="{cell}" rx="4" fill="{levels[lvl(c)]}" stroke="#fff" stroke-opacity=".05"><title>{c} contribution{"s" if c!=1 else ""} on {dday.isoformat()}</title></rect>'
for j, nm in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
    s += f'<text x="{gx-10}" y="{gy + j*(cell+gap) + 12}" text-anchor="end" font-family="{MONO}" font-size="10" fill="#8ea0ab">{nm}</text>'
lg = w - 28 - 5 * 16 - 60
s += f'<text x="{lg-34}" y="{h-18}" font-family="{MONO}" font-size="11" fill="#8ea0ab">less</text>'
for k, col in enumerate(levels):
    s += f'<rect x="{lg+k*16}" y="{h-28}" width="12" height="12" rx="3" fill="{col}"/>'
s += f'<text x="{lg+5*16+4}" y="{h-18}" font-family="{MONO}" font-size="11" fill="#8ea0ab">more</text></svg>'
open("assets/graph-heatmap.svg", "w", encoding="utf-8").write(s)
print("ok", w, total, active_days, best, best_week)

# inject the data into the site so it works offline and on Pages
import re
p = "site/index.html"
h = open(p, encoding="utf-8").read()
blob = "/*DATA*/" + json.dumps(D, separators=(",", ":")) + "/*END*/"
h = re.sub(r"/\*DATA\*/.*?/\*END\*/", lambda m: blob, h, flags=re.S)
open(p, "w", encoding="utf-8").write(h)
