"""Pull the real GitHub contribution calendar plus profile stats into assets/stats.json.

Uses only public endpoints. The calendar comes from github.com/users/<user>/contributions
(the same data as your profile graph, including PRs, issues and reviews).
Run before graphs.py:  python scripts/profile_stats.py && python scripts/graphs.py
"""
import os, re, json, html, urllib.request

U = "coll-ins"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "assets", "stats.json")
H = {"User-Agent": "profile-stats", "Accept": "application/vnd.github+json"}


def fetch(url, headers=H):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def api(url, default=None):
    try:
        return json.loads(fetch(url))
    except Exception as ex:
        print("api failed:", url.split("?")[0][-40:], ex)
        return default


stats = json.load(open(PATH, encoding="utf-8")) if os.path.exists(PATH) else {}

# ---- real contribution calendar ----
page = fetch(f"https://github.com/users/{U}/contributions", {"User-Agent": "profile-stats"})
cells = re.findall(r'data-date="(\d{4}-\d\d-\d\d)" id="(contribution-day-component-\d+-\d+)" data-level="(\d)"', page)
tips = dict(re.findall(r'for="(contribution-day-component-\d+-\d+)"[^>]*>([^<]*)<', page))
cal = {}
for d, cid, lvl in cells:
    m = re.match(r"(\d+) contribution", html.unescape(tips.get(cid, "")))
    cal[d] = int(m.group(1)) if m else 0
stats["calendar"] = dict(sorted(cal.items()))

# ---- profile numbers (search API has its own quota) ----
q = lambda s: (api(f"https://api.github.com/search/{s}", {}) or {}).get("total_count", 0)
user = api(f"https://api.github.com/users/{U}", {}) or {}
repos = api(f"https://api.github.com/users/{U}/repos?per_page=100", []) or []
prof = {
    "followers": user.get("followers", stats.get("profile", {}).get("followers", 0)),
    "stars": sum(r.get("stargazers_count", 0) for r in repos) if repos else stats.get("profile", {}).get("stars", 0),
    "prs": q(f"issues?q=author:{U}+type:pr"),
    "issues": q(f"issues?q=author:{U}+type:issue"),
    "reviews": q(f"issues?q=reviewed-by:{U}+type:pr"),
    "commits": q(f"commits?q=author:{U}"),
}
stats["profile"] = prof
json.dump(stats, open(PATH, "w", encoding="utf-8"), indent=1)
print("calendar days:", len(cal), "total:", sum(cal.values()), prof)
