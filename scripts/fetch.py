import os, json, urllib.request, datetime, sys, collections

U = "coll-ins"
H = {"User-Agent": "stats-gen", "Accept": "application/vnd.github+json"}


def get(url):
    req = urllib.request.Request(url, headers=H)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r), r.headers.get("X-RateLimit-Remaining")


repos = []
page = 1
while True:
    d, rem = get(f"https://api.github.com/users/{U}/repos?per_page=100&page={page}")
    repos += d
    if len(d) < 100:
        break
    page += 1
own = [r for r in repos if not r["fork"]]
print("total", len(repos), "own", len(own), "remaining", rem, file=sys.stderr)

today = datetime.date.today()
since = (today - datetime.timedelta(days=370)).isoformat() + "T00:00:00Z"
langs = collections.Counter()
days = collections.Counter()
per_repo = {}
for r in own:
    n = r["name"]
    try:
        l, rem = get(f"https://api.github.com/repos/{U}/{n}/languages")
        langs.update(l)
        total = 0
        p = 1
        while True:
            c, rem = get(f"https://api.github.com/repos/{U}/{n}/commits?author={U}&since={since}&per_page=100&page={p}")
            for x in c:
                dt = x["commit"]["author"]["date"][:10]
                days[dt] += 1
                total += 1
            if len(c) < 100:
                break
            p += 1
        per_repo[n] = total
    except Exception as ex:
        print("skip", n, ex, file=sys.stderr)
        if "403" in str(ex):
            break
print("remaining", rem, file=sys.stderr)
json.dump({"generated": today.isoformat(), "user": U, "repos_total": len(repos), "repos_own": len(own),
           "languages": langs.most_common(), "days": dict(days), "per_repo": per_repo},
          open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "stats.json"), "w"), indent=1)
print("commits", sum(days.values()), "days", len(days))
