#!/usr/bin/env python3
"""
Dominion Health Check
=====================

Audits every Dominion property for the specific ways things have actually
broken — not hypothetical problems, the real ones:

  * pages that build but contain no HTML (the 430-byte stub bug)
  * a sitemap with no <loc> tags, or one that shrank
  * placeholder 555 phone numbers going live
  * images hotlinked from domains we do not control
  * dead href="#" buttons on a pricing page
  * fabricated star ratings and review counts
  * a missing homepage
  * standing rules: John 3:16, capped hero

Every repo is public, so this needs no credentials to read them.
Set RESEND_API_KEY and ALERT_EMAIL to get a note when something is wrong.

Run:  python health_check.py
Exit: 0 = clean, 1 = problems found
"""

import os, re, sys, glob, json, shutil, tempfile, subprocess
from datetime import datetime

OWNER = "dominionsoundmusic-create"

REPOS = [
    "dominionwebdesignpro-site",
    "aivoiceagentpros-site",
    "dominionreviewpro-site",
    "dominionaiagency-site",
    "dominionsolarpro-site",
    "dominion-hard-money",
    "dominionlocalbusinessdirectory-site",
    "kidstorybooks-site",
    "houston-powerwashing-pro",
    "houston-hvac-pro",
    "houston-roofing-pro",
    "dallas-powerwashing-pro",
    "dallas-hvac-pro",
    "dallas-roofing-pro",
    "phoenix-pool-cleaning-pro",
    "tucson-pool-cleaning-pro",
    "arizona-pool-cleaning-pro",
]

# Image hosts we do not control. If a page pulls from one of these, the page
# breaks the day that host changes or rate-limits us.
FOREIGN_IMAGE_HOSTS = [
    "images.unsplash.com", "source.unsplash.com",
    "static.wixstatic.com", "images.squarespace-cdn.com",
    "cdn.pixabay.com", "images.pexels.com",
]

MIN_PAGE_BYTES = 1200        # anything smaller is a stub, not a page
SITEMAP_SHRINK_ALERT = 0.5   # sitemap holding under half the pages on disk

RESERVED_PHONE = re.compile(r"\b\d{3}-555-01\d\d\b")
FAKE_RATING = re.compile(r"★{3,}[^<]{0,40}\(\s*\d+\s+reviews?\s*\)", re.I)


class Report:
    def __init__(self):
        self.problems = []   # (severity, repo, message)

    def fail(self, repo, msg):  self.problems.append(("FAIL", repo, msg))
    def warn(self, repo, msg):  self.problems.append(("WARN", repo, msg))

    @property
    def fails(self):
        return [p for p in self.problems if p[0] == "FAIL"]

    @property
    def warns(self):
        return [p for p in self.problems if p[0] == "WARN"]


def clone(repo, into):
    url = f"https://github.com/{OWNER}/{repo}.git"
    r = subprocess.run(["git", "clone", "--depth", "1", "-q", url, into],
                       capture_output=True, text=True)
    return r.returncode == 0


def read(path, limit=None):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read() if limit is None else f.read(limit)
    except Exception:
        return ""


def check_repo(repo, path, rep):
    pages = [p for p in glob.glob(path + "/**/*.html", recursive=True)]
    city_pages = [p for p in pages if os.path.basename(p) != "index.html"]

    # ---- homepage -------------------------------------------------------
    home = os.path.join(path, "index.html")
    if not os.path.exists(home):
        rep.fail(repo, "no index.html — the site has no homepage")
        home_src = ""
    else:
        home_src = read(home)   # full file: markers can sit past any truncation point
        if len(home_src) < 2000:
            rep.fail(repo, f"homepage is only {len(home_src)} bytes")

    # ---- pages that are not really pages --------------------------------
    if city_pages:
        stubs = [p for p in city_pages if os.path.getsize(p) < MIN_PAGE_BYTES]
        if stubs:
            rep.fail(repo, f"{len(stubs)} of {len(city_pages)} pages are under "
                           f"{MIN_PAGE_BYTES} bytes (e.g. {os.path.relpath(stubs[0], path)})")

        sample = read(city_pages[0])
        if "<title>" not in sample:
            rep.fail(repo, "generated pages have no <title> tag")
        if "<html" not in sample.lower() and "<!doctype" not in sample.lower():
            rep.fail(repo, "generated pages contain no HTML structure")

    # ---- sitemap --------------------------------------------------------
    sm_path = os.path.join(path, "sitemap.xml")
    if not os.path.exists(sm_path):
        rep.warn(repo, "no sitemap.xml")
    else:
        sm = read(sm_path)
        locs = len(re.findall(r"<loc>", sm))
        if locs == 0:
            rep.fail(repo, "sitemap.xml has no <loc> entries — Google cannot read it")
        elif city_pages and locs < len(pages) * SITEMAP_SHRINK_ALERT:
            rep.warn(repo, f"sitemap lists {locs} URLs but the repo has {len(pages)} pages")

    # ---- placeholder phone numbers --------------------------------------
    hits = 0
    for p in ([home] + city_pages[:40]):
        if os.path.exists(p) and RESERVED_PHONE.search(read(p)):
            hits += 1
    if hits:
        rep.fail(repo, f"reserved 555-01XX placeholder phone number on {hits} sampled page(s)")

    # ---- hotlinked images -----------------------------------------------
    for hostname in FOREIGN_IMAGE_HOSTS:
        n = home_src.count(hostname)
        if n:
            rep.warn(repo, f"{n} image(s) hotlinked from {hostname}")

    # ---- dead buttons ---------------------------------------------------
    dead = len(re.findall(r'href="#"', home_src))
    if dead:
        rep.fail(repo, f"{dead} link(s) on the homepage point to href=\"#\" and do nothing")

    # ---- invented reviews -----------------------------------------------
    if FAKE_RATING.search(home_src):
        rep.fail(repo, "homepage shows a star rating with a review count — verify it is real")
    if city_pages:
        s = read(city_pages[0])
        if FAKE_RATING.search(s):
            rep.fail(repo, "generated pages show star ratings with review counts")

    # ---- standing rules -------------------------------------------------
    if home_src and "John 3:16" not in home_src:
        rep.warn(repo, "homepage is missing the John 3:16 reference")
    if home_src and "max-height:700px" not in home_src.replace(" ", ""):
        rep.warn(repo, "homepage hero may not be capped at 700px")

    return len(pages)


def send_email(subject, body):
    key = os.environ.get("RESEND_API_KEY")
    to = os.environ.get("ALERT_EMAIL")
    if not key or not to:
        return
    try:
        import requests
        requests.post("https://api.resend.com/emails",
                      headers={"Authorization": "Bearer " + key,
                               "Content-Type": "application/json"},
                      json={"from": "Dominion Health <alerts@dominionaiagency.com>",
                            "to": [to], "subject": subject,
                            "text": body}, timeout=20)
        print("\nAlert email sent to", to)
    except Exception as e:
        print("\nCould not send alert email:", e)


def main():
    rep = Report()
    tmp = tempfile.mkdtemp(prefix="dominion-health-")
    total_pages = 0
    checked = 0

    print("=" * 68)
    print("DOMINION HEALTH CHECK —", datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("=" * 68)

    try:
        for repo in REPOS:
            dest = os.path.join(tmp, repo)
            if not clone(repo, dest):
                rep.fail(repo, "could not clone — repo missing or renamed?")
                print(f"  {repo:<38} CLONE FAILED")
                continue
            n = check_repo(repo, dest, rep)
            total_pages += n
            checked += 1
            issues = [p for p in rep.problems if p[1] == repo]
            mark = "ok" if not issues else f"{len(issues)} issue(s)"
            print(f"  {repo:<38} {n:>6} pages   {mark}")
            shutil.rmtree(dest, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("-" * 68)
    print(f"  {checked} properties, {total_pages:,} pages")
    print()

    if rep.fails:
        print("PROBLEMS THAT NEED FIXING")
        for _, repo, msg in rep.fails:
            print(f"  [{repo}] {msg}")
        print()

    if rep.warns:
        print("WORTH A LOOK")
        for _, repo, msg in rep.warns:
            print(f"  [{repo}] {msg}")
        print()

    if not rep.problems:
        print("Everything clean.")
        return 0

    lines = ["Dominion health check — " + datetime.now().strftime("%Y-%m-%d %H:%M"), ""]
    if rep.fails:
        lines += ["NEEDS FIXING:"] + [f"  [{r}] {m}" for _, r, m in rep.fails] + [""]
    if rep.warns:
        lines += ["WORTH A LOOK:"] + [f"  [{r}] {m}" for _, r, m in rep.warns]
    send_email(f"Dominion health: {len(rep.fails)} problems, {len(rep.warns)} warnings",
               "\n".join(lines))

    return 1 if rep.fails else 0


if __name__ == "__main__":
    sys.exit(main())
