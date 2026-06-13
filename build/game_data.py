# -*- coding: utf-8 -*-
"""
game_data.py — 리포트 구조화 데이터(D 딕트) → 게임 시나리오용 깨끗한 game_data.json.

산업 패권(industry-hegemon) 게임이 쓰는 산업별 실데이터를 추출한다:
  - ksf_weights: 리포트의 KSF 요인들을 게임 4역량(tech/brand/scale/global)으로 분류·정규화
  - global_firms: pie_global(실제 글로벌 점유율)에서 'Others' 제외, 이름 정제
  - korea_firms:  pie_korea(실제 한국 점유율)에서 'Others' 제외, 이름 정제
  - market(최신 시장 규모)·cagr
HTML 파싱이 아니라 D 딕트(클린 소스)에서 뽑으므로 기업명에 국가·쓰레기가 안 섞인다.
기존 game_data.json(dict, gics 키)이 있으면 gics 단위로 '병합'(누적) — 매일 7개씩 커버리지가 는다.

실행: python3 build/game_data.py   (산출: 레포 루트 game_data.json, dict[gics])
파이프라인 연동: 일일 빌드(gen.py) 끝에서 자동 호출.
"""
import json, os, re, html

from reports_data import REPORTS

CAPS = ["tech", "brand", "scale", "global"]

# KSF 영문 요인명 → 게임 4역량 분류 키워드. CHECK_ORDER 순으로 가장 먼저 매칭되는 cap.
# (brand/scale/global을 tech보다 먼저 봐서, 'high-spec'·'performance' 같은 모호어가 tech로 쏠리는 것 완화)
CHECK_ORDER = ["brand", "scale", "global", "tech"]
KEYWORDS = {
    "brand":  ["brand", "premium", "high-spec", "marketing", "design", "loyalty", "trust", "reputation",
               "customer experience", "content", "franchise", "membership", "luxury"],
    "scale":  ["scale", "low-cost", "low cost", "cost", "manufactur", "capacity", "volume",
               "production", "pricing", "throughput", "yield", "operational", "utiliz", "fleet", "density",
               "efficiency", "efficient"],
    "global": ["global", "international", "distribution", "network", "geograph", "export",
               "supply chain", "supply-chain", "footprint", "reach", "regulat", "compliance",
               "diversif", "logistics", "channel", "access", "infra"],
    "tech":   ["r&d", "rnd", "research", "technolog", "innovat", "ai", "chip", "semiconductor",
               "software", "patent", "decarbon", "sustainab", "digital", "data", "automation",
               "engineering", "clinical", "ip", "spec", "performance", "advanced", "quality"],
}


def classify(factor_en: str) -> str:
    s = html.unescape(factor_en or "").lower()
    for cap in CHECK_ORDER:
        for kw in KEYWORDS[cap]:
            if kw in s:
                return cap
    return ""   # 미분류


def ksf_weights(ksf_list) -> dict:
    """KSF 요인들을 순위 가중(앞일수록 중요)으로 4역량에 누적·정규화."""
    raw = {c: 0.0 for c in CAPS}
    n = len(ksf_list) or 1
    for i, item in enumerate(ksf_list):
        en = item[0] if isinstance(item, (list, tuple)) else str(item)
        cap = classify(en)
        w = (n - i)            # 순위 가중: 1순위 = n, 마지막 = 1
        if cap:
            raw[cap] += w
    total = sum(raw.values())
    if total <= 0:
        return {c: 0.25 for c in CAPS}                 # 분류 실패 → 균등(게임에서 '준비중' 처리)
    return {c: round(raw[c] / total, 4) for c in CAPS}


def clean_name(raw: str):
    """'English한글' 분리. (en, ko) 반환. 게임 측에서도 방어하지만 여기서 1차 정제."""
    s = html.unescape((raw or "").strip())
    m = re.match(r"^([^가-힣]+?)\s*([가-힣].*)$", s)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return s, None


def firms_from_pie(pie):
    """pie [(name, share), ...] → [{name, ko?, share}] (Others 제외)."""
    out = []
    for entry in (pie or []):
        if not isinstance(entry, (list, tuple)) or len(entry) < 2:
            continue
        name, share = entry[0], entry[1]
        en, ko = clean_name(name)
        if not en or en.lower() in ("others", "other", "etc"):
            continue
        rec = {"name": en, "share": share}
        if ko:
            rec["ko"] = ko
        out.append(rec)
    return out


def latest_market(cols):
    """cols [(label, value_T, year)] → 최신(현재년 추정) 규모(조달러)와 연도 라벨."""
    if not cols:
        return None
    actual = [c for c in cols if not str(c[2]).endswith("E")]   # 'E'(추정) 아닌 최근 = 현재
    pick = actual[-1] if actual else cols[-1]
    return {"label": pick[0], "trillion_usd": pick[1], "year": str(pick[2])}


def build_entry(D: dict) -> dict:
    return {
        "gics": D.get("gics", ""),
        "industry_en": html.unescape(D.get("industry_en", "")),
        "industry_ko": D.get("industry_ko", ""),
        "sector": D.get("sector_en", ""),
        "sector_ko": D.get("sector_ko", ""),
        "global_company": html.unescape(D.get("global_company", "")),
        "korea_company": html.unescape(D.get("korea_company", "")),
        "headline_ko": D.get("headline_ko", ""),
        "ksf_weights": ksf_weights(D.get("ksf", [])),
        "global_firms": firms_from_pie(D.get("pie_global")),
        "korea_firms": firms_from_pie(D.get("pie_korea")),
        "market": latest_market(D.get("cols")),
        "cagr": D.get("cagr", ""),
    }


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_path = os.path.join(root, "game_data.json")

    data = {}
    if os.path.exists(out_path):                      # 기존 dict 위에 병합(누적). list(구버전)·깨진 파일이면 새로.
        try:
            with open(out_path, encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                data = loaded
        except Exception:
            data = {}

    added = 0
    for D in REPORTS:
        g = D.get("gics")
        if not g:
            continue
        data[g] = build_entry(D)
        added += 1

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
    print(f"game_data.json: {added}개 갱신, 총 {len(data)}개 산업 → {out_path}")


if __name__ == "__main__":
    main()
