# -*- coding: utf-8 -*-
"""Emit game_data.json for the Industry Hegemon game.

Parses each published report's HTML (the structured KSF + market-share data that
gen.py rendered) and distills it into the fields the game needs:
  - ksf_weights: the 6 industry KSFs classified into the game's 4 capability axes
    (tech / brand / scale / global), normalized to sum 1
  - competitors: real company names (global leader + challenger from the global
    pie, Korean champion from reports.json)
Deduped by GICS (latest report date wins), mirroring reports.json.

Run: python3 build/game_data.py   →   writes game_data.json at repo root.
"""
import json, os, re
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# KSF phrase -> capability axis, by keyword. First axis with the most hits wins.
KEYWORDS = {
    "tech":  ["technolog", "r&d", "research", "engineer", "design", "innovat", "digital",
              "software", " ai", "data", "patent", " ip", "decarbon", "automation",
              "quality", "performance", "feed", "epc", "product develop", "platform", "ecosystem", "yield", "fab"],
    "brand": ["brand", "premium", "marketing", "customer", "loyalt", "experience",
              "reputation", "trust", "high-spec", "mix", "pricing", "content", "membership"],
    "scale": ["scale", "low-cost", "cost", "manufactur", "efficien", "capacity", "volume",
              "supply chain", "procure", "logistic", "operation", "execution", "capex", "throughput", "utiliz"],
    "global":["global", "international", "distribut", "network", "geograph", " access",
              "regulat", "complian", "localiz", "footprint", "export", "channel", "market access"],
}
CAPS = ["tech", "brand", "scale", "global"]


def classify(phrase_en):
    t = phrase_en.lower()
    best, bestn = None, 0
    for cap in CAPS:
        n = sum(t.count(k) for k in KEYWORDS[cap])
        if n > bestn:
            bestn, best = n, cap
    return best  # may be None if no keyword matched


def ksf_weights(ksf_phrases):
    w = {c: 0.0 for c in CAPS}
    for en in ksf_phrases:
        c = classify(en)
        if c:
            w[c] += 1.0
    # floor each axis so no capability is irrelevant, then normalize to 1
    for c in CAPS:
        w[c] += 0.5
    tot = sum(w.values())
    return {c: round(w[c] / tot, 3) for c in CAPS}


def parse_report(path):
    soup = BeautifulSoup(open(path, encoding="utf-8").read(), "html.parser")
    # KSF: section#ksf -> .kc -> b -> span.en
    ksf = []
    sec = soup.find("section", id="ksf")
    if sec:
        for kc in sec.select(".kc"):
            en = kc.select_one("b .en")
            if en:
                ksf.append(en.get_text(strip=True))
    # Global pie: first legend in the share section; named entries excluding "Others"
    global_firms = []
    share = soup.find("section", id="share")
    if share:
        legends = share.select(".legend, .lg")
        items = legends[0].select(".lg-item") if legends else share.select(".lg-item")
        for it in items:
            name = re.sub(r"~?[\d.]+%?$", "", it.get_text(strip=True)).strip()
            b = it.find("b")
            pct = float(re.sub(r"[^\d.]", "", b.get_text())) if b else 0.0
            if name.lower() != "others" and name:
                global_firms.append({"name": name, "share": pct})
    return ksf, global_firms


def main():
    reports = json.load(open(os.path.join(ROOT, "reports.json"), encoding="utf-8"))
    by_gics = {}
    for e in reports:  # latest date wins
        if e["gics"] not in by_gics or e["date"] > by_gics[e["gics"]]["date"]:
            by_gics[e["gics"]] = e

    out = []
    for gics, e in by_gics.items():
        path = os.path.join(ROOT, e["file"])
        if not os.path.exists(path):
            continue
        ksf, global_firms = parse_report(path)
        if len(ksf) < 3:
            continue  # too little to be useful
        out.append({
            "gics": gics,
            "industry_en": e["industry_en"], "industry_ko": e["industry_ko"],
            "sector": e["sector"],
            "ksf_weights": ksf_weights(ksf),
            "ksf_en": ksf,
            "global_company": e["global_company"], "korea_company": e["korea_company"],
            "global_firms": global_firms[:3],
        })
    out.sort(key=lambda x: (x["sector"], x["industry_en"]))
    json.dump(out, open(os.path.join(ROOT, "game_data.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("wrote game_data.json:", len(out), "industries")


if __name__ == "__main__":
    main()
