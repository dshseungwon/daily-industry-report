# -*- coding: utf-8 -*-
"""
game_data.py — 발행된 리포트 HTML → 게임(산업 패권)용 game_data.json.

매일 GitHub Action이 reports/<date>/*.html 를 발행한다. 이 스크립트는 reports.json(전체
이력 메타)에서 gics별 최신 리포트를 골라 그 HTML에서 게임이 쓰는 실데이터를 뽑는다:
  - ksf_weights : KSF 6요인을 게임 4역량(tech/brand/scale/global)으로 분류·정규화
  - global_firms: 글로벌 점유율 파이(legend)에서 회사·% (Others 제외, 'English한글' 정제, 국가 제외)
  - korea_firms : 한국 점유율 파이에서 동일 처리
  - cagr        : 있으면 성장률 라벨
stdlib만 사용(정규식). 외부 의존성 없음 → CI에서 그대로 동작.

연동: 일일 워크플로의 'Generate' 단계 뒤(‘Commit & push’ 전)에 `python3 build/game_data.py`를
호출하면 game_data.json이 갱신되고, git add -A 가 함께 커밋·게시한다(GitHub Pages).
게임 레포는 이 game_data.json(레포 루트 = Pages 루트)을 가져다 쓴다.

실행: python3 build/game_data.py   →   레포 루트 game_data.json (dict[gics])
"""
import json, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPS = ["tech", "brand", "scale", "global"]

# KSF 영문 요인명 → 4역량. CHECK_ORDER 순으로 첫 매칭(brand/scale/global을 tech보다 먼저).
CHECK_ORDER = ["brand", "scale", "global", "tech"]
KEYWORDS = {
    "brand":  ["brand", "premium", "high-spec", "marketing", "design", "loyalty", "trust", "reputation",
               "customer experience", "content", "franchise", "membership", "luxury"],
    "scale":  ["scale", "low-cost", "low cost", "cost", "manufactur", "capacity", "volume",
               "production", "pricing", "throughput", "yield", "operational", "utiliz", "fleet", "density",
               "efficiency", "efficient", "vertical integ"],
    "global": ["global", "international", "distribution", "network", "geograph", "export",
               "supply chain", "supply-chain", "footprint", "reach", "regulat", "compliance",
               "diversif", "logistic", "channel", "access", "infra", "proximity"],
    "tech":   ["r&d", "rnd", "research", "technolog", "innovat", "ai", "chip", "semiconductor",
               "software", "patent", "decarbon", "sustainab", "digital", "data", "automation",
               "engineering", "clinical", " ip", "spec", "performance", "advanced", "quality", "fuel"],
}

COUNTRY_EN = {"united states", "china", "russia", "saudi arabia", "india", "iran", "iraq", "canada",
              "brazil", "japan", "germany", "united arab emirates", "kuwait", "norway", "mexico",
              "qatar", "nigeria", "australia", "south korea", "united kingdom", "france", "indonesia"}
COUNTRY_KO = {"미국", "중국", "러시아", "사우디아라비아", "사우디", "인도", "이란", "이라크", "캐나다",
              "브라질", "일본", "독일", "아랍에미리트", "쿠웨이트", "노르웨이", "멕시코", "카타르",
              "나이지리아", "호주", "한국", "영국", "프랑스", "인도네시아"}


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def classify(factor_en):
    s = factor_en.lower()
    for cap in CHECK_ORDER:
        for kw in KEYWORDS[cap]:
            if kw in s:
                return cap
    return ""


def ksf_weights(titles):
    raw = {c: 0.0 for c in CAPS}
    n = len(titles) or 1
    for i, t in enumerate(titles):
        cap = classify(t)
        if cap:
            raw[cap] += (n - i)        # 순위 가중(앞일수록 중요)
    total = sum(raw.values())
    if total <= 0:
        return {c: 0.25 for c in CAPS}
    return {c: round(raw[c] / total, 4) for c in CAPS}


def clean_name(raw):
    s = html.unescape((raw or "").strip())
    m = re.match(r"^([^가-힣]+?)\s*([가-힣].*)$", s)
    en, ko = (m.group(1).strip(), m.group(2).strip()) if m else (s, None)
    country = None
    cm = re.search(r"\(([^)]+)\)\s*$", en)          # 영문명 끝의 (HQ 국가) 추출 → 게임 본국 배정용
    if cm:
        country = cm.group(1).strip()
        en = en[:cm.start()].strip()
    is_country = en.lower() in COUNTRY_EN or (ko in COUNTRY_KO) or (not en and (ko in COUNTRY_KO))
    return en, ko, is_country, country


def firms(pairs):
    out = []
    for name, share in pairs:
        en, ko, is_country, country = clean_name(name)
        low = en.lower()
        if (not en or is_country or low in ("others", "other", "etc", "n/a")
                or low.startswith("rest of") or low.startswith("other ") or "remaining" in low):
            continue
        rec = {"name": en, "share": share}
        if ko:
            rec["ko"] = ko
        if country:
            rec["country"] = country
        out.append(rec)
    return out[:5]


def parse_html(s):
    # KSF 요인 제목: 각 .kc 의 첫 <b><span class="en">제목</span>
    titles = []
    for kc in re.findall(r'<div class="kc">(.*?)</div>\s*</div>', s, re.S):
        m = re.search(r'<b>\s*<span class="en">(.*?)</span>', kc, re.S)
        if m:
            titles.append(strip_tags(m.group(1)))
    # 파이: <div class="pieblock"> 단위로 split. lg-item 은 파이에만 등장(다른 곳 없음).
    glob, kor = [], []
    for chunk in s.split('<div class="pieblock">')[1:]:
        tm = re.search(r'pie-title[^>]*>\s*<span class="en">(.*?)</span>', chunk, re.S)
        title = strip_tags(tm.group(1)) if tm else ""
        pairs = []
        for it in re.findall(r'<div class="lg-item">(.*?)</div>', chunk, re.S):
            nm = re.search(r'</span>\s*(.*?)\s*<b>\s*~?\s*([\d.]+)\s*%', it, re.S)
            if nm:
                pairs.append((strip_tags(nm.group(1)), float(nm.group(2))))
        tl = title.lower()
        if "korea" in tl or "한국" in title:
            kor = pairs
        elif glob:
            kor = kor or pairs
        else:
            glob = pairs
    return titles, glob, kor


def _to_trillion(num_s, unit):
    num = float(num_s.replace(",", ""))
    return num if unit.lower() in ("t", "trillion") else num / 1000.0   # B → T


def parse_size_cagr(s):
    """section#size 에서 총 시장규모(trillion_usd)·CAGR·기준연도 추출. 실패 시 (None, "")."""
    sec = re.search(r'<section id="size">(.*?)</section>', s, re.S)
    block = sec.group(1) if sec else s
    trillion, label, year = None, "", ""
    # 1) colchart 기준연도(첫 col-val) — 모든 리포트가 공통으로 그리는 시장규모 시계열(가장 일관적)
    cols = re.findall(r'col-val">\s*~?\$?\s*([\d.,]+)\s*(trillion|billion|[TB])', block, re.I)
    if cols:
        trillion = _to_trillion(cols[0][0], cols[0][1]); label = "$" + cols[0][0] + cols[0][1].upper()[0]
        ym = re.search(r'col-lab">\s*(\d{4})', block); year = ym.group(1) if ym else ""
    if trillion is None:                               # 2) h2 영문 $figure
        h2en = re.search(r'<h2>.*?<span class="en">(.*?)</span>', block, re.S)
        en = strip_tags(h2en.group(1)) if h2en else ""
        m = re.search(r'(?:US)?\$\s*([\d.,]+)\s*(trillion|billion|[BT])\b', en, re.I) \
            or re.search(r'([\d.,]+)\s*(trillion|billion)\b', en, re.I)
        if m:
            trillion = _to_trillion(m.group(1), m.group(2)); label = m.group(0).strip()
    if trillion is None:                               # 3) 한국어 폴백: X조/억 달러
        h2ko = re.search(r'<h2>.*?<span class="ko">(.*?)</span>', block, re.S)
        ko = strip_tags(h2ko.group(1)) if h2ko else ""
        mk, ma = re.search(r'([\d.,]+)\s*조\s*달러', ko), re.search(r'([\d.,]+)\s*억\s*달러', ko)
        if mk:
            trillion = float(mk.group(1).replace(",", "")); label = mk.group(0).strip()
        elif ma:
            trillion = float(ma.group(1).replace(",", "")) / 10000.0; label = ma.group(0).strip()
    # CAGR: .cagr-badge 의 <span class="n">~13%</span>
    cm = re.search(r'cagr-badge.*?<span class="n">\s*(.*?)\s*</span>', block, re.S)
    cagr = strip_tags(cm.group(1)) if cm else ""
    market = {"label": label, "trillion_usd": round(trillion, 4), "year": year} if trillion else None
    return market, cagr


def main():
    reports = json.load(open(os.path.join(ROOT, "reports.json"), encoding="utf-8"))
    latest = {}
    for e in reports:                                  # gics별 최신 날짜만
        if e["gics"] not in latest or e["date"] > latest[e["gics"]]["date"]:
            latest[e["gics"]] = e

    data = {}
    if os.path.exists(os.path.join(ROOT, "game_data.json")):
        try:
            loaded = json.load(open(os.path.join(ROOT, "game_data.json"), encoding="utf-8"))
            if isinstance(loaded, dict):
                data = loaded                          # 기존 위에 병합(파싱 실패한 날 보존)
        except Exception:
            data = {}

    ok = 0
    for gics, e in latest.items():
        path = os.path.join(ROOT, e["file"])
        if not os.path.exists(path):
            continue
        raw = open(path, encoding="utf-8").read()
        titles, glob, kor = parse_html(raw)
        if len(titles) < 3 and not glob:
            continue                                   # 정보 부족 → 건너뜀(기존 유지)
        market, cagr = parse_size_cagr(raw)
        data[gics] = {
            "gics": gics,
            "industry_en": e.get("industry_en", ""),
            "industry_ko": e.get("industry_ko", ""),
            "sector": e.get("sector", ""),
            "global_company": e.get("global_company", ""),
            "korea_company": e.get("korea_company", ""),
            "headline_ko": e.get("headline_ko", ""),
            "ksf_weights": ksf_weights(titles),
            "global_firms": firms(glob),
            "korea_firms": firms(kor),
            "cagr": cagr,
        }
        if market:
            data[gics]["market"] = market
        ok += 1

    with open(os.path.join(ROOT, "game_data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
    print(f"game_data.json: {ok}개 파싱 성공, 총 {len(data)}개 산업")


if __name__ == "__main__":
    main()
