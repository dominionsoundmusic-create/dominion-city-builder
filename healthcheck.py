#!/usr/bin/env python3
"""Daily health check for the Dominion properties.

Runs on GitHub Actions (which can reach the sites; Claude's sandbox cannot).
Writes results to healthcheck/latest.json and appends a one-line summary to
healthcheck/history.log on the `healthcheck` branch, so daily runs never touch
main and never trigger a Netlify deploy.
"""

import json, socket, ssl, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone

# domain -> a string that must appear in the page body. Empty means status-only.
SITES = {
    "dominionhardmoney.com":            "Dominion Hard Money",
    "dominionwebdesignpro.com":         "Dominion Web Design Pro",
    "dominionsolarpro.com":             "Dominion Solar Pro",
    "aivoiceagentpros.com":             "AI Voice Agent Pros",
    "dominionaiagency.com":             "Dominion AI Agency",
    "dominionreviewpro.com":            "Dominion Review Pro",
    "dominionlocalbusinessdirectory.com": "",
    "gracewoodworkkilgore.com":         "Grace Woodwork",
    "kidstorybooks.com":                "",
    "dominionsoundmusic.com":           "",
    "houstonexpertroofers.com":         "",
    "houstonpowerwashingpro.com":       "",
    "houstonairandheating.com":         "",
    "dfwexpertroofers.com":             "",
    "dallaspowerwashingpro.com":        "",
    "dallasairandheating.com":          "",
    "phoenixpoolcleaningpro.com":       "",
    "tucsonpoolcleaningpro.com":        "",
    "yumapoolcleaningpro.com":          "",
}

TIMEOUT = 20
UA = "DominionHealthCheck/1.0 (+https://dominionwebdesignpro.com)"


def ssl_days_left(host):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=TIMEOUT) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ss:
                exp = ss.getpeercert()["notAfter"]
        when = datetime.strptime(exp, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        return (when - datetime.now(timezone.utc)).days
    except Exception:
        return None


def check(domain, needle):
    url = "https://%s/" % domain
    row = {"domain": domain, "url": url}
    started = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = r.read(200000).decode("utf-8", "replace")
            row["status"] = r.status
            row["final_url"] = r.geturl()
    except urllib.error.HTTPError as e:
        row["status"] = e.code
        body = ""
    except Exception as e:
        row["status"] = None
        row["error"] = "%s: %s" % (type(e).__name__, e)
        body = ""
    row["ms"] = int((time.time() - started) * 1000)
    row["bytes"] = len(body)
    if needle:
        row["expected_text"] = needle
        row["text_found"] = needle.lower() in body.lower()
    row["ssl_days_left"] = ssl_days_left(domain)

    problems = []
    if row["status"] != 200:
        problems.append("HTTP %s" % row["status"])
    if needle and not row.get("text_found"):
        problems.append("expected text missing")
    if row["ms"] > 5000:
        problems.append("slow: %dms" % row["ms"])
    d = row["ssl_days_left"]
    if d is not None and d < 14:
        problems.append("SSL expires in %d days" % d)
    if row["status"] == 200 and row["bytes"] < 500:
        problems.append("body only %d bytes" % row["bytes"])

    row["verdict"] = "FAIL" if (row["status"] != 200 or (needle and not row.get("text_found"))) \
        else ("WARN" if problems else "OK")
    row["problems"] = problems
    return row


def main():
    results = [check(d, n) for d, n in SITES.items()]
    fails = [r for r in results if r["verdict"] == "FAIL"]
    warns = [r for r in results if r["verdict"] == "WARN"]
    out = {
        "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "checked": len(results),
        "fail": len(fails),
        "warn": len(warns),
        "ok": len(results) - len(fails) - len(warns),
        "results": sorted(results, key=lambda r: (r["verdict"] != "FAIL", r["verdict"] != "WARN", r["domain"])),
    }
    import os
    os.makedirs("healthcheck", exist_ok=True)
    with open("healthcheck/latest.json", "w") as f:
        json.dump(out, f, indent=2)
    line = "%s  checked=%d ok=%d warn=%d fail=%d%s\n" % (
        out["run_at"], out["checked"], out["ok"], out["warn"], out["fail"],
        ("  FAIL: " + ", ".join(r["domain"] for r in fails)) if fails else "")
    with open("healthcheck/history.log", "a") as f:
        f.write(line)
    print(line.strip())
    for r in results:
        if r["problems"]:
            print("  %-6s %-36s %s" % (r["verdict"], r["domain"], "; ".join(r["problems"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
