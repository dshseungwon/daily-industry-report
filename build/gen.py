# -*- coding: utf-8 -*-
import json, os

OUT = os.path.dirname(os.path.abspath(__file__))
DATE = "2026-06-08"
tpl = open(os.path.join(OUT, "_template.html"), encoding="utf-8").read()

# Extract verbatim head styles (both <style> blocks) and the script block
HEAD = tpl[tpl.index("<style>"):tpl.index("</head>")]
SCRIPT = tpl[tpl.index("<script>"):tpl.index("</body>")]

PAL = ["#0e2a47", "#117aca", "#ffb81c", "#5aa9e6", "#c9d4e3"]
PAL_KR = ["#0047a0", "#117aca", "#ffb81c", "#5aa9e6", "#c9d4e3"]

def bz(en, ko):
    return f'<span class="en">{en}</span><span class="ko">{ko}</span>'

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def heights(vals):
    lo, hi = min(vals), max(vals)
    if hi == lo:
        return [72 for _ in vals]
    return [round(44 + (v - lo) / (hi - lo) * 56) for v in vals]

def pie(slices, kr=False):
    pal = PAL_KR if kr else PAL
    segs, legend, cum = [], [], 0.0
    for i, (name, pct) in enumerate(slices):
        c = pal[i] if i < len(pal) else "#c9d4e3"
        segs.append(f"{c} {cum:.0f}% {cum+pct:.0f}%")
        cum += pct
        legend.append(f'<div class="lg-item"><span class="lg-dot" style="background:{c}"></span>{esc(name)}<b>~{pct:g}%</b></div>')
    return ("background:conic-gradient(" + ",".join(segs) + ")", "".join(legend))

def chips(items):
    out = []
    for go, en, ko in items:
        out.append(f'<button class="chip" data-go="{go}">{bz(en,ko)}</button>')
    return "".join(out)

def value_chain(steps):
    parts = []
    for i, (en, ko, den, dko) in enumerate(steps, 1):
        parts.append(f'<div class="vc-step"><span class="vc-n">{i}</span><b>{bz(en,ko)}</b><span class="d">{bz(den,dko)}</span></div>')
        if i < len(steps):
            parts.append('<div class="vc-arrow" aria-hidden="true">&#10148;</div>')
    return '<div class="vchain">' + "".join(parts) + "</div>"

def profit_pool(rows):
    out = []
    LV = {"hi": ("High", "높음"), "med": ("Medium", "중간"), "lo": ("Low", "낮음")}
    for en, ko, lv in rows:
        e, k = LV[lv]
        out.append(f'<div class="pool-row"><span class="pn">{bz(en,ko)}</span><span class="ptrack"><span class="pfill {lv}"></span></span><span class="pv {lv}">{bz(e,k)}</span></div>')
    return '<div class="pool">' + "".join(out) + "</div>"

def colchart(cols):
    vals = [c[1] for c in cols]
    hs = heights(vals)
    out = []
    for (disp, _v, lab), h in zip(cols, hs):
        out.append(f'<div class="col"><div class="col-val">{esc(disp)}</div><div class="col-bar" data-h="{h}"></div><div class="col-lab">{esc(lab)}</div></div>')
    return '<div class="colchart">' + "".join(out) + "</div>"

def forces(items):
    LV = {"hi": ("High", "높음"), "med": ("Medium", "중간"), "lo": ("Low", "낮음")}
    out = []
    for en, ko, lv, ren, rko in items:
        e, k = LV[lv]
        out.append(f'<div class="force"><div class="force-top"><b>{bz(en,ko)}</b><span class="rate {lv}">{bz(e,k)}</span></div><p>{bz(ren,rko)}</p></div>')
    return '<div class="forces reveal">' + "".join(out) + "</div>"

def accordion(items):
    out = []
    for badge, ten, tko, wen, wko in items:
        out.append(f'<div class="ac"><div class="ac-head" tabindex="0" role="button" aria-expanded="false"><span class="ac-badge">{esc(badge)}</span><span class="ac-title">{bz(ten,tko)}</span></div><div class="ac-body"><p class="why">{bz(wen,wko)}</p></div></div>')
    return '<div class="acc" data-accordion>' + "".join(out) + "</div>"

def ksf(items):
    out = []
    for i, (en, ko, den, dko) in enumerate(items, 1):
        out.append(f'<div class="kc"><span class="kn">{i}</span><div><b>{bz(en,ko)}</b><p>{bz(den,dko)}</p></div></div>')
    return '<div class="ksf reveal">' + "".join(out) + "</div>"

def stats(items):
    out = []
    for n, en, ko in items:
        out.append(f'<div class="stat"><div class="n">{esc(n)}</div><div class="l">{bz(en,ko)}</div></div>')
    return '<div class="stats">' + "".join(out) + "</div>"

def scqa(d):
    f = esc(d["formula"])
    return (
        '<div class="scqa">'
        f'<div class="scqa-row s"><span class="scqa-k">S</span><div class="scqa-bd"><span class="scqa-lab">{bz("Situation · biggest problem","상황 · 핵심 문제")}</span><p>{bz(*d["s"])}</p></div></div>'
        f'<div class="scqa-row c"><span class="scqa-k">C</span><div class="scqa-bd"><span class="scqa-lab">{bz("Complication · root cause","원인 · 근본 이유")}</span><p>{bz(*d["c"])}</p><div class="formula">{f}</div></div></div>'
        f'<div class="scqa-row q"><span class="scqa-k">Q</span><div class="scqa-bd"><span class="scqa-lab">{bz("Question · hypothesis","질문 · 가설적 접근")}</span><p>{bz(*d["q"])}</p></div></div>'
        f'<div class="scqa-row a"><span class="scqa-k">A</span><div class="scqa-bd"><span class="scqa-lab">{bz("Answer · direction","해결 · 방향")}</span><p>{bz(*d["a"])}</p></div></div>'
        '</div>'
    )

def tree(d):
    branches = []
    for j, b in enumerate(d["branches"]):
        lever = j == len(d["branches"]) - 1
        if lever:
            leaf = f'<div class="leaf lever"><span class="lever-tag">{bz("Lever","레버")}</span>{bz(b[2],b[3])}</div>'
        else:
            leaf = f'<div class="leaf">{bz(b[2],b[3])}</div>'
        branches.append(f'<div class="branch"><b>{bz(b[0],b[1])}</b>{leaf}</div>')
    return (
        '<div class="tree">'
        f'<div class="root">{bz(*d["root"])}</div>'
        '<div class="branches">' + "".join(branches) + "</div>"
        f'<p class="tree-cap">{bz("MECE issue tree — branches are mutually exclusive; the gold leaf is the binding lever.","MECE 이슈트리 — 가지는 상호배타적이며, 금색 잎이 핵심 레버입니다.")}</p>'
        '</div>'
        f'<p class="scqa-cap">{bz("SCQA narrative above; the issue tree below decomposes the cause (C) into MECE branches, gold = the binding lever.","위는 SCQA 흐름이고, 아래 이슈트리는 원인(C)을 MECE 가지로 분해합니다. 금색이 핵심 레버입니다.")}</p>'
    )

def tracks(items):
    n = len(items)
    cls = ["t1", "t2", "t3"]
    out = []
    for i, (tten, ttko, tnen, tnko, pen, pko) in enumerate(items):
        out.append(f'<div class="track {cls[i]}"><div class="tt">{bz(tten,ttko)}</div><div class="tn">{bz(tnen,tnko)}</div><p>{bz(pen,pko)}</p></div>')
    return f'<div class="track-grid n{n}">' + "".join(out) + "</div>"

def aplans(items):
    out = []
    for ten, tko, fen, fko, toen, toko in items:
        out.append(
            f'<div class="ap"><div class="apt">{bz(ten,tko)}</div><div class="ap-flow">'
            f'<div class="ap-from"><small>{bz("From","현재")}</small>{bz(fen,fko)}</div>'
            f'<div class="ap-arrow">&#8594;</div>'
            f'<div class="ap-to"><small>{bz("To","목표")}</small>{bz(toen,toko)}</div>'
            '</div></div>'
        )
    return '<div class="ap-grid">' + "".join(out) + "</div>"

def leader(side, tag_en, tag_ko, name, flag, blurb_en, blurb_ko, st, dh_en, dh_ko, sc, root_en, root_ko, tr, ap):
    style = ' style="margin-top:14px"' if side == "kr" else ""
    return (
        f'<div class="{side}"{style}>'
        f'<div class="leader-band"><span class="flagdot">{flag}</span><div><div class="tag">{bz(tag_en,tag_ko)}</div><h3>{esc(name)}</h3></div></div>'
        '<div class="leader-wrap reveal">'
        f'<p class="mute" style="margin-top:0">{bz(blurb_en,blurb_ko)}</p>'
        + stats(st)
        + f'<div class="diag"><div class="dh">{bz(dh_en,dh_ko)}</div>'
        + scqa(sc)
        + f'<div class="subh" style="margin:14px 0 0">{bz("Issue tree · root-cause decomposition","이슈트리 · 원인 분해")}</div>'
        + tree({"root": (root_en, root_ko), "branches": sc["branches"]})
        + '</div>'
        + tracks(tr)
        + f'<div class="subh">{bz("Action plans","액션 플랜")}</div>'
        + aplans(ap)
        + '</div></div>'
    )

def posmap(points, xen, xko, yen, yko, ten, tko):
    # points: list of (cx,cy,r,color,label) ; first navy, second krred, rest grey
    circ = []
    for cx, cy, r, color, label in points:
        circ.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}"/><text x="{cx}" y="{cy-9}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#13314f">{esc(label)}</text>')
    return (
        '<div class="posmap reveal"><svg viewBox="0 0 340 290" xmlns="http://www.w3.org/2000/svg" role="img">'
        '<rect x="60" y="18" width="262" height="214" fill="#f7fafd" stroke="#e6ebf4" stroke-width="1.5" rx="8"/>'
        '<line x1="60" y1="125" x2="322" y2="125" stroke="#dbe3ef" stroke-width="1" stroke-dasharray="4 4"/>'
        '<line x1="191" y1="18" x2="191" y2="232" stroke="#dbe3ef" stroke-width="1" stroke-dasharray="4 4"/>'
        + "".join(circ)
        + f'<text x="191" y="254" text-anchor="middle" font-size="11" font-weight="800" fill="#5b6b8c" class="en">{esc(xen)} &#8594;</text>'
        + f'<text x="191" y="254" text-anchor="middle" font-size="11" font-weight="800" fill="#5b6b8c" class="ko">{esc(xko)} &#8594;</text>'
        + f'<text x="14" y="125" text-anchor="middle" font-size="11" font-weight="800" fill="#5b6b8c" transform="rotate(-90 14 125)" class="en">{esc(yen)} &#8594;</text>'
        + f'<text x="14" y="125" text-anchor="middle" font-size="11" font-weight="800" fill="#5b6b8c" transform="rotate(-90 14 125)" class="ko">{esc(yko)} &#8594;</text>'
        + '</svg>'
        + f'<div class="pos-legend"><span class="pl-i"><span class="pl-d" style="background:var(--navy)"></span>{bz("Global #1","글로벌 1위")}</span><span class="pl-i"><span class="pl-d" style="background:var(--krred)"></span>{bz("Korea #1","한국 1위")}</span><span class="pl-i"><span class="pl-d" style="background:#9fb1c9"></span>{bz("Peers","경쟁사")}</span></div>'
        + f'<p class="cap">{bz(ten,tko)}</p></div>'
    )

def kpis(items):
    out = []
    for ten, tko, ven, vko, wen, wko in items:
        out.append(f'<div class="kpi"><div class="kt">{bz(ten,tko)}</div><div class="kv">{bz(ven,vko)}</div><div class="kw">{bz(wen,wko)}</div></div>')
    return '<div class="kpis reveal">' + "".join(out) + "</div>"

def scenarios(b):
    return (
        '<div class="scen reveal">'
        f'<div class="sc bull"><div class="sh">{bz("Bull · upside","낙관")}</div><div class="sd">{bz(*b["bull"][0])}</div><p>{bz(*b["bull"][1])}</p></div>'
        f'<div class="sc base"><div class="sh">{bz("Base · central","기본")}</div><div class="sd">{bz(*b["base"][0])}</div><p>{bz(*b["base"][1])}</p></div>'
        f'<div class="sc bear"><div class="sh">{bz("Bear · downside","비관")}</div><div class="sd">{bz(*b["bear"][0])}</div><p>{bz(*b["bear"][1])}</p></div>'
        '</div>'
    )

def risks(items):
    return '<ul class="tight">' + "".join(f'<li>{bz(en,ko)}</li>' for en, ko in items) + "</ul>"

def sources(items):
    return "".join(f'<li><a href="{esc(u)}">{esc(t)}</a></li>' for t, u in items)


def build(d):
    gp, gl = pie(d["pie_global"])
    kp, kl = pie(d["pie_korea"], kr=True)
    body = f'''<div class="topbar">
  <div class="row">
    <div class="brand">The Industry Brief<span class="g"> ·</span> {bz(d["industry_en"], d["industry_ko"])}</div>
    <div class="chips">{chips([("overview","Overview","개요"),("chain","Value chain","가치사슬"),("share","Market share","시장점유율"),("positioning","Positioning","포지셔닝"),("forces","5 Forces","5 Forces"),("reg","Regulation","규제"),("ksf","KSF","핵심성공요인"),("players","Players","플레이어"),("scenarios","Scenarios","시나리오")])}</div>
    <button id="lang" aria-label="Toggle language"><span class="en">한국어</span><span class="ko">EN</span></button>
  </div>
</div>
<div class="hero">
  <div class="wrap">
    <p class="eyebrow">{bz(f"The Industry Brief · GICS day-set {d['set_index']} of 7", f"디 인더스트리 브리프 · 오늘의 7개 중 {d['set_index']}번째")}</p>
    <h1>{bz(d["industry_en"], d["industry_ko"])}</h1>
    <p class="sub">{bz("Industry analysis &amp; competitive structure","산업 분석과 경쟁 구조")}</p>
    <div class="pill-row">
      <span class="pill">GICS · {bz(d["sector_en"], d["sector_ko"])} · {d["gics"]}</span>
      <span class="pill">{DATE}</span>
      <span class="pill">{bz("Players","플레이어")}: {esc(d["global_company"])} · {esc(d["korea_company"])}</span>
    </div>
  </div>
</div>
<div class="wrap">
  <section id="overview">
    <div class="card summary reveal">
      <p class="kicker">{bz("Executive summary","핵심 요약")}</p>
      <p>{bz(d["exec_en"], d["exec_ko"])}</p>
    </div>
  </section>
  <section id="chain">
    <div class="card reveal">
      <p class="kicker">{bz("Definition &amp; value chain","정의와 가치사슬")}</p>
      <h2>{bz(*d["chain_h2"])}</h2>
      <p class="lead">{bz(*d["chain_lead"])}</p>
      {value_chain(d["chain"])}
      <div class="subh" style="margin-top:16px">{bz("Profit pool — where margin concentrates","수익풀 — 마진이 집중되는 곳")}</div>
      {profit_pool(d["pool"])}
      <p class="cap">{bz(*d["pool_cap"])}</p>
    </div>
  </section>
  <section id="size">
    <div class="card reveal">
      <p class="kicker">{bz("Market size &amp; growth","시장 규모와 성장")}</p>
      <h2>{bz(*d["size_h2"])}</h2>
      <div class="cagr-wrap"><span class="cagr-badge">{bz("CAGR","연평균 성장")}<span class="n">{esc(d["cagr"])}</span></span><span class="mute" style="font-size:12.5px">{bz(*d["cagr_note"])}</span></div>
      {colchart(d["cols"])}
      <p class="cap">{bz(*d["size_cap"])}</p>
    </div>
  </section>
  <section id="share">
    <div class="card reveal">
      <p class="kicker">{bz("Market share (MS) status","시장점유율(MS) 현황")}</p>
      <h2>{bz(*d["share_h2"])}</h2>
      <div class="pies">
        <div class="pieblock"><div class="pie-title">{bz(*d["pie_global_title"])}</div><div class="pie" style="{gp}"></div><div class="legend">{gl}</div></div>
        <div class="pieblock"><div class="pie-title">{bz(*d["pie_korea_title"])}</div><div class="pie" style="{kp}"></div><div class="legend">{kl}</div></div>
      </div>
      <p class="cap">{bz(*d["share_cap"])}</p>
    </div>
  </section>
  <section id="positioning">
    <p class="kicker">{bz("Competitive positioning","경쟁 포지셔닝")}</p>
    <h2>{bz("Where the leaders sit — a 2×2 map","리더들의 위치 — 2×2 맵")}</h2>
    {posmap(d["pos_points"], *d["pos_x"], *d["pos_y"], *d["pos_take"])}
  </section>
  <section id="forces">
    <p class="kicker">{bz("Porter's Five Forces","포터의 5가지 경쟁요인")}</p>
    <h2>{bz("Structural attractiveness","산업 구조의 매력도")}</h2>
    {forces(d["forces"])}
    <p class="cap">{bz(*d["forces_cap"])}</p>
  </section>
  <section id="reg">
    <p class="kicker">{bz("Macro forces &amp; the latest RULES","거시 환경과 최신 규칙")}</p>
    <h2>{bz("The rulebook: policy &amp; regulation","규칙: 정책과 규제")}</h2>
    <p class="mute">{bz(*d["reg_intro"])}</p>
    <p class="hint">{bz("This section = laws, bills and rules only (dated). Market events are in &#8220;Recent issues&#8221; below.","이 섹션은 법·법안·규칙만(시행일 표기)입니다. 시장 이벤트는 아래 &#8216;최근 이슈&#8217;에 있습니다.")}</p>
    {accordion(d["reg"])}
  </section>
  <section id="ksf">
    <p class="kicker">{bz("Key Success Factors","핵심성공요인(KSF)")}</p>
    <h2>{bz("What it takes to win","이 산업에서 이기는 조건")}</h2>
    {ksf(d["ksf"])}
  </section>
  <section id="news">
    <p class="kicker">{bz("What's moving the industry now","지금 산업을 움직이는 것")}</p>
    <h2>{bz("The newsflow: market &amp; competitive events","뉴스: 시장·경쟁 이벤트")}</h2>
    <p class="hint">{bz("This section = business/market events (earnings, deals, demand, prices) — not policy. Tap for why it matters.","이 섹션은 실적·거래·수요·가격 등 시장 이벤트입니다(정책 아님). 눌러서 의미를 확인하십시오.")}</p>
    {accordion(d["news"])}
  </section>
  <section id="players">
    <div class="divider"><span class="ln"></span><span class="tx">{bz("Players · strategy analysis","플레이어 · 전략 분석")}</span><span class="ln"></span></div>
    <h2>{bz("The two leaders, each with its OWN strategy","두 리더, 각자 다른 전략")}</h2>
    <p class="mute" style="margin-top:-4px">{bz("The industry view above is the main act. Below, each leader is diagnosed on its own terms: a MECE issue tree → strategy thrusts chosen for THAT company → action plans. The NUMBER of thrusts varies by situation.","위의 산업 분석이 본론입니다. 아래에서는 각 리더를 그 회사에 맞게 진단합니다: MECE 이슈트리 → 그 기업에 맞춰 고른 전략 축 → 액션 플랜. 전략 축의 개수는 상황에 따라 다릅니다.")}</p>
    {leader("gl","Global #1","글로벌 1위", d["global_company"], "🌐", *d["gl"])}
    {leader("kr","Korea #1","한국 1위", d["korea_company"], "🇰🇷", *d["kr"])}
  </section>
  <section id="kpi">
    <p class="kicker">{bz("KPIs to watch","주목할 지표")}</p>
    <h2>{bz("The dials that move this industry","이 산업을 움직이는 계기판")}</h2>
    <p class="hint">{bz("Leading indicators with the latest reading — track these to see the thesis play out.","최신 수치가 담긴 선행지표입니다. 이 흐름을 추적하면 전망을 검증할 수 있습니다.")}</p>
    {kpis(d["kpis"])}
  </section>
  <section id="scenarios">
    <p class="kicker">{bz("Scenarios — bull · base · bear","시나리오 — 낙관·기본·비관")}</p>
    <h2>{bz("Three ways the next few years could break","향후 몇 년이 갈릴 세 갈래")}</h2>
    {scenarios(d["scen"])}
  </section>
  <section id="risks">
    <div class="card reveal">
      <p class="kicker">{bz("Risks &amp; outlook","리스크 &amp; 전망")}</p>
      <h2>{bz("Where the industry is headed","산업은 어디로 가는가")}</h2>
      {risks(d["risks"])}
    </div>
  </section>
</div>
<footer>
  <div class="wrap">
    <h4>{bz("Sources","출처")}</h4>
    <ul style="list-style:none;padding:0;margin:0;">{sources(d["sources"])}</ul>
    <p class="disclaim">{bz(f"The Industry Brief · {d['industry_en']} (GICS {d['gics']}) · Generated June 8, 2026. Public sources, rounded; informational only, not investment advice.", f"디 인더스트리 브리프 · {d['industry_ko']}(GICS {d['gics']}) · 2026년 6월 8일 생성. 공개 자료 기준 반올림이며 정보 제공용으로 투자 자문이 아닙니다.")}</p>
  </div>
</footer>'''
    title = f'{d["industry_en"]} · {d["industry_ko"]} — The Industry Brief'
    html = (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<title>{esc(title)}</title>\n' + HEAD + '\n</head>\n<body class="lang-en">\n\n'
        + body + "\n\n" + SCRIPT + "\n</body>\n</html>\n"
    )
    fn = f'industry-report_{DATE}_{d["gics"]}_{d["slug"]}.html'
    open(os.path.join(OUT, fn), "w", encoding="utf-8").write(html)
    return fn

from reports_data import REPORTS  # noqa
landing = []
for d in REPORTS:
    fn = build(d)
    landing.append({
        "date": DATE, "gics": d["gics"], "sector": d["sector_en"], "set_index": d["set_index"],
        "industry_en": d["industry_en"], "industry_ko": d["industry_ko"],
        "global_company": d["global_company"], "korea_company": d["korea_company"],
        "file": f"reports/{DATE}/{fn}",
        "headline_en": d["headline_en"], "headline_ko": d["headline_ko"], "accent": d["accent"],
    })
    print("built", fn)

open("/sessions/gracious-magical-pascal/mnt/outputs/today.json", "w", encoding="utf-8").write(json.dumps(landing, ensure_ascii=False, indent=2))
print("wrote /sessions/gracious-magical-pascal/mnt/outputs/today.json with", len(landing), "entries")
