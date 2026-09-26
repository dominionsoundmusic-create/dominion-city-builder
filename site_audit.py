#!/usr/bin/env python3
"""Daily page-level audit of every Dominion site repo (Sep 25 2026).

health_check.py / healthcheck.py check that each site is up. This goes deeper
and reads every page in every repo for the problems found by hand on Sep 25:
broken internal links, missing image files, pages nothing links to, sitemap
drift, leftover code or placeholder text, canonicals on the wrong domain,
British spellings, the Espanol button, and - on the lead sites only - any
wording that makes a phone line sound like a contractor.

Repos are public, so it needs no credentials. Writes healthcheck/site_audit.json
and prints one summary line per site. Exit 1 if any FAIL-level problem exists.
Run locally: python site_audit.py [path-to-folder-of-cloned-repos]
"""
import os, re, sys, glob, json, html, shutil, tempfile, subprocess, collections

OWNER = "dominionsoundmusic-create"
# repo -> kind. lead = referral phone-line sites; dominion = own brands; client = real business
SITES = {
    "houston-roofing-pro": "lead", "houston-hvac-pro": "lead", "houston-powerwashing-pro": "lead",
    "dallas-roofing-pro": "lead", "dallas-hvac-pro": "lead", "dallas-powerwashing-pro": "lead",
    "phoenix-pool-cleaning-pro": "lead", "tucson-pool-cleaning-pro": "lead", "arizona-pool-cleaning-pro": "lead",
    "dominionwebdesignpro-site": "dominion", "aivoiceagentpros-site": "dominion", "dominionreviewpro-site": "dominion",
    "dominionaiagency-site": "dominion", "dominion-hard-money": "dominion",
    "dominionlocalbusinessdirectory-site": "dominion", "kidstorybooks-site": "dominion",
    "grace-woodwork-site": "client",
}
FAIL = {"broken internal link", "missing image file", "placeholder or code text", "canonical on wrong domain",
        "sitemap URL with no page", "company claim on a lead site", "contractor voice on a lead site"}
BRIT = ["colour", "mould", "programme", "centre", "apologise", "neighbour", "realise", "recognised", "tyre",
        "favour", "behaviour", "organise", "catalogue"]
PLACEHOLDERS = ["```", "lorem ipsum", "todo:", "fixme", "{{", "[city]", "[brand]", "555-01"]
CONTRACTOR = re.compile(r"\b(call us first|we already know|our (?:team|technicians?|crews?|techs?|roofers?|cleaners?|trucks?)|"
                        r"we (?:clean|service|repair|fix|install|send|arrive|guarantee|replace|inspect|wash))\b", re.I)

def vis(t):
    t = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", "", t, flags=re.S | re.I)
    return html.unescape(re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", t)))

def audit(root, kind):
    files = glob.glob(f"{root}/**/*.html", recursive=True)
    idx = open(f"{root}/index.html", errors="ignore").read() if os.path.exists(f"{root}/index.html") else ""
    m = re.search(r'rel="canonical" href="https?://(?:www\.)?([^/"]+)', idx); dom = m.group(1) if m else ""
    issues = collections.defaultdict(list); inbound = collections.Counter()
    def resolve(src, href):
        h = href.split("#")[0].split("?")[0]
        if not h or h.startswith(("tel:", "mailto:", "javascript:", "data:", "sms:")) or "'" in h or "+" in h: return True
        if h.startswith("http"):
            mm = re.match(r"https?://(?:www\.)?([^/]+)(/.*)?", h)
            if not mm or mm.group(1).lower() != dom.lower(): return True
            h = mm.group(2) or "/"
        path = root + h if h.startswith("/") else os.path.normpath(os.path.join(os.path.dirname(src), h))
        for c in (path, path.rstrip("/") + "/index.html", path + ".html", path.rstrip("/") + ".html"):
            if os.path.isfile(c): return c
        return False
    for p in files:
        rel = os.path.relpath(p, root); t = open(p, errors="ignore").read()
        if "<body" not in t.lower(): continue
        noindex = "noindex" in t[:4000].lower()
        cm = re.search(r'rel="canonical" href="([^"]+)"', t)
        if cm and dom and dom.lower() not in cm.group(1).lower(): issues["canonical on wrong domain"].append(f"{rel} -> {cm.group(1)}")
        body = t[t.lower().find("<body"):]
        for href in re.findall(r'<a\b[^>]*href="([^"]*)"', body):
            r = resolve(p, href)
            if r is False: issues["broken internal link"].append(f"{rel} -> {href}")
            elif isinstance(r, str) and os.path.abspath(r) != os.path.abspath(p): inbound[os.path.relpath(r, root)] += 1
        for src in re.findall(r'<img\b[^>]*\ssrc="([^"]+)"', t) + re.findall(r"url\('(/images/[^']+)'\)", t):
            if src.startswith(("http", "data:")) or "'" in src or "+" in src: continue
            if resolve(p, src) is False: issues["missing image file"].append(f"{rel} -> {src}")
        v = vis(t); vl = v.lower()
        for bad in PLACEHOLDERS:
            if bad in vl: issues["placeholder or code text"].append(f"{rel}: {bad}")
        for w in BRIT:
            if re.search(r"\b" + w, vl): issues["British spelling"].append(f"{rel}: {w}")
        if not noindex and 'id="gt-bar"' not in t and "google_translate_element" not in t: issues["no Espanol button"].append(rel)
        if kind == "lead" and not any(x in rel for x in ("privacy", "terms")):
            if re.search(r"licensed (and|&) insured", vl) and "?" not in v[max(0, vl.find("licensed")-80):vl.find("licensed")+60]:
                issues["company claim on a lead site"].append(rel)
            for mm in CONTRACTOR.finditer(v): issues["contractor voice on a lead site"].append(f"{rel}: {mm.group(0)}")
    for p in files:
        rel = os.path.relpath(p, root); t = open(p, errors="ignore").read()
        if rel in ("index.html", "404.html") or "noindex" in t[:4000].lower() or any(x in rel for x in ("privacy", "terms", "thanks", "shop-upload", "write.html")): continue
        if inbound[rel] == 0: issues["orphan page"].append(rel)
    sm = f"{root}/sitemap.xml"
    if os.path.exists(sm):
        for l in re.findall(r"<loc>([^<]+)</loc>", open(sm, errors="ignore").read()):
            if resolve(f"{root}/index.html", l) is False: issues["sitemap URL with no page"].append(l)
    return dom, {k: v for k, v in issues.items()}

def main():
    local = sys.argv[1] if len(sys.argv) > 1 else None
    work = local or tempfile.mkdtemp()
    out, bad = {}, 0
    for repo, kind in SITES.items():
        root = f"{work}/{repo}"
        if not local:
            subprocess.run(["git", "clone", "-q", "--depth", "1", f"https://github.com/{OWNER}/{repo}.git", root], check=False)
        if not os.path.isdir(root): out[repo] = {"error": "could not read repo"}; bad += 1; continue
        dom, iss = audit(root, kind)
        fails = sum(len(v) for k, v in iss.items() if k in FAIL); warns = sum(len(v) for k, v in iss.items() if k not in FAIL)
        bad += fails > 0
        out[repo] = {"domain": dom, "kind": kind, "fail": fails, "warn": warns, "issues": {k: v[:25] for k, v in iss.items()}}
        print(f"{'FAIL' if fails else ('WARN' if warns else 'OK  ')}  {repo:38} fail={fails} warn={warns}  " + "; ".join(f"{k}={len(v)}" for k, v in iss.items()))
    os.makedirs("healthcheck", exist_ok=True)
    json.dump(out, open("healthcheck/site_audit.json", "w"), indent=1)
    print(f"site_audit sites={len(SITES)} failing={bad}")
    if not local: shutil.rmtree(work, ignore_errors=True)
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
