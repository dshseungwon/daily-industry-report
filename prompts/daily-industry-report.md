You are running headless inside a GitHub Actions runner, in a fresh checkout of the
repo `dshseungwon/daily-industry-report` (current working directory = repo root).
No human is present. Execute autonomously, make reasonable choices, and note them in
your output. Do NOT ask questions. Do NOT git commit or git push: a later workflow
step does that. Your job is to leave the new/updated files in the working tree.

GOAL: Generate today's batch of SEVEN daily INDUSTRY-ANALYSIS reports for "The
Industry Brief", FACT-CHECK them, and update the landing page. Each report is a
single self-contained, mobile-first, interactive, BILINGUAL (English default +
Korean) HTML file whose MAIN body is a deep industry analysis; the two companies
(global #1, Korea #1) come afterward as a SECONDARY "players · strategy analysis"
section.

REPO LAYOUT (already exists):
- index.html, reports.json, build_index.js, .nojekyll at the repo root.
- Reports live in dated subfolders: reports/<YYYY-MM-DD>/.
- GitHub Pages serves from main/root, so committing is all that's needed to publish.

FAST PATH — reuse the template. Copy the NEWEST existing report (highest dated folder
under reports/, e.g. the most recent reports/<date>/industry-report_*.html) and reuse
its <style> and <script> VERBATIM, swapping only the body content. That template
already implements everything: English-default bilingual toggle; a CAGR badge +
vertical column chart with a ZOOMED baseline; global + Korea pie charts; a value chain
drawn as a NUMBERED ARROW-CONNECTED FLOW with a PROFIT-POOL bar; Five Forces chips; a
2x2 competitive-positioning SVG map; a KPI watchlist; bull/base/bear SCENARIO cards;
and per-company strategy blocks using a 4-step SCQA DIAGNOSIS (Situation, Complication,
Question, Answer) plus 1-3 tailored strategy tracks.

STEP 1 — Pick today's 7 GICS industries with COVERAGE-AWARE rotation. Sweep every
industry exactly once per lap, spread across sectors, tracking progress in rotation.json
so nothing is skipped or over-repeated. When a lap completes it starts the next lap; once
the 74 GICS Industries (Phase 1) are fully covered AND a subindustries.json file exists in
the repo root, it advances to Phase 2 (GICS Sub-Industries). Run:

python3 - <<'PY'
import json, os
from collections import OrderedDict
SECTOR={"10":"Energy","15":"Materials","20":"Industrials","25":"Consumer Discretionary","30":"Consumer Staples","35":"Health Care","40":"Financials","45":"Information Technology","50":"Communication Services","55":"Utilities","60":"Real Estate"}
L1=[("101010","Energy Equipment & Services"),("101020","Oil, Gas & Consumable Fuels"),("151010","Chemicals"),("151020","Construction Materials"),("151030","Containers & Packaging"),("151040","Metals & Mining"),("151050","Paper & Forest Products"),("201010","Aerospace & Defense"),("201020","Building Products"),("201030","Construction & Engineering"),("201040","Electrical Equipment"),("201050","Industrial Conglomerates"),("201060","Machinery"),("201070","Trading Companies & Distributors"),("202010","Commercial Services & Supplies"),("202020","Professional Services"),("203010","Air Freight & Logistics"),("203020","Passenger Airlines"),("203030","Marine Transportation"),("203040","Ground Transportation"),("203050","Transportation Infrastructure"),("251010","Automobile Components"),("251020","Automobiles"),("252010","Household Durables"),("252020","Leisure Products"),("252030","Textiles, Apparel & Luxury Goods"),("253010","Hotels, Restaurants & Leisure"),("253020","Diversified Consumer Services"),("255010","Distributors"),("255030","Broadline Retail"),("255040","Specialty Retail"),("301010","Consumer Staples Distribution & Retail"),("302010","Beverages"),("302020","Food Products"),("302030","Tobacco"),("303010","Household Products"),("303020","Personal Care Products"),("351010","Health Care Equipment & Supplies"),("351020","Health Care Providers & Services"),("351030","Health Care Technology"),("352010","Biotechnology"),("352020","Pharmaceuticals"),("352030","Life Sciences Tools & Services"),("401010","Banks"),("402010","Financial Services"),("402020","Consumer Finance"),("402030","Capital Markets"),("402040","Mortgage REITs"),("403010","Insurance"),("451020","IT Services"),("451030","Software"),("452010","Communications Equipment"),("452020","Technology Hardware, Storage & Peripherals"),("452030","Electronic Equipment, Instruments & Components"),("453010","Semiconductors & Semiconductor Equipment"),("501010","Diversified Telecommunication Services"),("501020","Wireless Telecommunication Services"),("502010","Media"),("502020","Entertainment"),("502030","Interactive Media & Services"),("551010","Electric Utilities"),("551020","Gas Utilities"),("551030","Multi-Utilities"),("551040","Water Utilities"),("551050","Independent Power and Renewable Electricity Producers"),("601010","Diversified REITs"),("601025","Industrial REITs"),("601030","Hotel & Resort REITs"),("601040","Office REITs"),("601050","Health Care REITs"),("601060","Residential REITs"),("601070","Retail REITs"),("601080","Specialized REITs"),("602010","Real Estate Management & Development")]
def load(p,d):
    try: return json.load(open(p))
    except Exception: return d
def universe(phase):
    if phase>=2 and os.path.exists("subindustries.json"):
        return [(str(c),n) for c,n in load("subindustries.json",[])]
    return L1
reps=load("reports.json",[])
state=load("rotation.json",None)
if state is None:
    covered=set(str(r.get("gics")) for r in reps if r.get("gics"))
    state={"phase":1,"covered":[c for c,_ in L1 if c in covered]}
phase=int(state.get("phase",1)); covered=set(state.get("covered",[]))
univ=universe(phase); uncovered=[(c,n) for c,n in univ if c not in covered]
if not uncovered:
    if phase==1 and os.path.exists("subindustries.json"): phase=2
    covered=set(); univ=universe(phase); uncovered=[(c,n) for c,n in univ]
def spread_pick(items, k):
    bysec=OrderedDict()
    for c,n in items: bysec.setdefault(SECTOR.get(c[:2],"?"),[]).append((c,n))
    out=[]; secs=list(bysec.keys()); i=0
    while len(out)<k and any(bysec[s] for s in secs):
        s=secs[i%len(secs)]
        if bysec[s]: out.append(bysec[s].pop(0))
        i+=1
    return out
pick=spread_pick(uncovered,7)
if len(pick)<7:  # lap nearly done -> top up from a fresh lap
    used=set(c for c,_ in pick)|covered
    pick+=spread_pick([(c,n) for c,n in universe(phase) if c not in used],7-len(pick))
for c,_ in pick: covered.add(c)
json.dump({"phase":phase,"covered":sorted(covered)}, open("rotation.json","w"), ensure_ascii=False)
for k,(c,n) in enumerate(pick): print(k+1, c, "|", n, "|", SECTOR.get(c[:2],"?"))
PY

This prints up to 7 `(k, gics_code, industry, sector)` rows and writes rotation.json (it is
committed with the reports in STEP 6). Use these as today's industries; the GICS code shown
is the report's code.

For EACH industry do STEPS 2-4.

STEP 2 — Research (web search; last 12 months; year-stamp every figure). DEEP industry
analysis: (a) definition & value chain; (b) market size & CAGR; (c) MARKET SHARE
globally AND in Korea, quantified; (d) Porter's Five Forces each rated High/Medium/Low
with a reason; (e) PESTEL + the LATEST legislation/regulation (name bills/rules with
dates); (f) Key Success Factors (4-6). Then 4-6 DATED recent issues with "why it
matters". Then the two players: GLOBAL #1 (largest worldwide by a stated metric) and
KOREA #1 (largest South Korean; if none meaningful, say so and name the closest proxy,
do not invent). Keep source URLs. Run the 7 industries' research in PARALLEL with
subagents (the Agent tool) to save time.

STEP 3 — KOREAN: TWO-PASS, never inline. Translationese is the #1 quality complaint;
the fix is to never translate sentence-by-sentence while looking at English.
PASS 1 (here): build each report ENGLISH-ONLY — every <span class="ko"> temporarily
holds the IDENTICAL English text as its <span class="en"> twin (equal span counts
guaranteed by construction).
PASS 2 (runs AFTER the STEP 6a/6b fact-check corrections, so corrected English is the
source): for each report, a dedicated subagent extracts the unique EN strings and
REWRITES each one in Korean as a top-tier executive secretary briefing the chairman.
Korean rewrite rules (give these to the rewrite subagents verbatim):
- 합쇼체 보고체: "~로 파악됩니다", "~한 바 있습니다", "~할 것으로 보입니다",
  "시사점을 말씀드리면 ~라는 점입니다". 문장 구조는 영어를 버리고 한국어 호흡으로
  재구성(문장 분할, 연결어 "실제로/다만/앞서/이에 따라" 추가 자유).
- 번역체 금지: "~에 의해", "~되어지다", "면세 입국", "재경로화" 같은 직역 명사구 금지.
- 짧은 라벨/제목/차트 라벨/KPI 제목은 간결한 명사형(예: "Executive summary"→"핵심 보고",
  "Bull · upside"→"낙관 시나리오", "KPIs to watch"→"주시할 지표"). "Why it matters:"→"시사점:".
- 용어집: market share→시장점유율, value chain→가치사슬, moat→해자, KSF→핵심성공요인,
  CAGR→연평균 성장률(CAGR), profit pool→이익 풀, backlog→수주잔고, occupancy→입주율.
- 단위 변환은 반드시 검산: $X billion = X×10억 달러($35.71B→357억 1,000만 달러),
  $X trillion = X조 달러, €1,085B→1조 850억 유로(1,085 billion = 1조 850억; 1,085억이 아님),
  ₩61.1T→61.1조 원, X percentage points→X%포인트. 헷갈리면 원문 표기 유지가 오역보다 낫다.
- 한국 기업은 한국어 정식 명칭, 해외 기업은 통용 한글 표기(널리 쓰일 때만), 약어형
  사명·기관(SLB, UPS, ZF, FDA, CMS)은 영문 유지. 수치/연도/날짜/%는 EN과 정확히 일치.
After PASS 2, run the EN/KO NUMERIC-CONSISTENCY GATE on every file and fix all real
mismatches before finishing (false positives like "about a quarter"→"약 25%" may be
accepted; absolute rule: years, %, and converted currency magnitudes must be correct):

python3 - <<'PY'
import re, glob, sys
bad_total = 0
for f in glob.glob('reports/*/industry-report_*.html'):
    s = open(f, encoding='utf-8').read()
    for e, k in re.findall(r'<span class="en">(.*?)</span><span class="ko">(.*?)</span>', s, re.S):
        if not re.search(r'[가-힣]', k): continue
        ye = set(m.group(0) for m in re.finditer(r'(?<!\d)(?:19|20)\d{2}(?!\d)', e))
        yk = set(m.group(0) for m in re.finditer(r'(?<!\d)(?:19|20)\d{2}(?!\d)', k))
        pe = sorted(re.findall(r'\d+(?:\.\d+)?(?=%)', e)); pk = sorted(re.findall(r'\d+(?:\.\d+)?(?=%|％)', k))
        if (pe != pk and not set(pe) <= set(pk)) or not ye <= yk:
            print(f, '|', e[:70]); bad_total += 1
print('mismatches:', bad_total)
PY


STYLE — PLAIN, STANDARD, NO HEADLINE FLOURISHES (applies to BOTH English and Korean,
section titles AND prose). This is the #1 quality rule. Write like a competent
secretary briefing an executive: plain, specific, useful. Never reach for a clever or
"impressive" phrase.
- Use these EXACT standard section labels, nothing creative:
  Executive summary / 핵심 요약 · Definition & value chain / 정의와 가치사슬 ·
  Market size & growth / 시장 규모와 성장 · Market share / 시장점유율 ·
  Competitive positioning / 경쟁 포지셔닝 · Porter's Five Forces / 포터의 5가지 경쟁요인 ·
  Regulation & policy / 규제·정책 · Key Success Factors / 핵심 성공 요인 ·
  Recent market events / 최근 시장 동향 · Players · strategy analysis / 주요 기업 · 전략 분석 ·
  KPIs to watch / 주시할 지표 · Scenarios: bull, base, bear / 시나리오: 낙관·기본·비관 ·
  Risks & outlook / 리스크와 전망.
- The one-line sub-headline under each label is a PLAIN factual finding (specific and
  useful), never a magazine headline, metaphor, or slogan.
- Executive summary: AT MOST 3 sentences, the single most important points only.
- Every strategy/action line must be concrete and self-explanatory to a reader with no
  extra context. No cryptic shorthand (bad: "동탄을 일정대로 완수"; good: "동탄 헬스케어 리츠를
  예정대로 상장·가동합니다").
- BANNED — real examples of what NOT to write (EN or KO):
  "A trillion-dollar asset pool, a coming wave of demand" / "1조 달러에 육박하는 자산 풀, 다가오는 수요의 파도";
  "Global giants race ahead, Korea at the starting line" / "글로벌은 거인 독주, 한국은 아직 출발선";
  "What it takes to win" / "승부를 가르는 조건" (use Key Success Factors / 핵심 성공 요인);
  "The two players, each with its OWN strategy" / "두 플레이어, 각자의 전략" (use the standard label above);
  "Keep the deal machine running" / "딜 머신을 계속 돌린다" (write plainly, e.g. "M&A로 성장을 이어갑니다");
  "Three ways the next few years could break" / "향후 몇 년, 세 갈래 시나리오".

STEP 4 — Build ONE bilingual .html per industry (NO external dependencies). Every
string as <span class="en">…</span><span class="ko">…</span>; ENGLISH DEFAULT
(<html lang="en">, <body class="lang-en">, script calls setLang('en')). Market size =
vertical COLUMN chart with a zoomed baseline (note the zoom honestly in the caption);
market share = two PIE charts (CSS conic-gradient, global + Korea, each summing to
100%, with legends). Mobile-first, card-based, accordions, sticky top bar with language
toggle + section chips (the top bar MUST also start with a .nav-home gold pill link, href="../../index.html", labelled All/전체, that returns to the landing index), reveal-on-scroll, prefers-reduced-motion. Keep two sections
MECE: "Macro forces & the latest RULES" = laws/bills/regulations ONLY (dated);
"What's moving the industry now" = market/competitive events ONLY (earnings, deals,
demand, prices). No item may appear in both.

Structure (analysis dominant; players secondary): (1) Header — brand "The Industry
Brief", industry, date, "GICS day-set k of 7", and the GICS taxonomy breadcrumb (STEP 4A); (2) Executive summary (≤3 sentences, the single most important points only); (3) Definition & value chain (numbered arrow flow + profit-pool bar — EACH stage must show its INDICATIVE SHARE of the industry profit pool as a percentage: the .pv label reads ~NN%, the shares sum to ~100% across the listed stages, the bar width is proportional to that share, and the hi/med/lo class only tints colour by magnitude; do NOT use a generic High/Medium/Low word as the value); (4)
Market size & growth (CAGR badge + zoomed column chart); (5) Market share (global +
Korea pies summing to 100%); (6) Competitive positioning (2x2 SVG with Global #1 navy,
Korea #1 red, 2-3 peers = 4 plotted points, one-line takeaway); (7) Porter's Five
Forces (rated); (8) Macro forces & the latest RULES (laws only, dated); (9) Key Success
Factors (6 cards); (10) What's moving the industry now (market events only, dated);
(11) PLAYERS · strategy analysis — Global #1 then Korea #1, EACH with stat callouts that
MUST include a MARKET CAP stat ("Market cap"/"시가총액", current value with as-of month,
e.g. "$348B (Jun 2026)" / "3,480억 달러(2026년 6월)"; if the company is unlisted write
"Private (unlisted)"/"비상장" — e.g. Bosch, delisted Osstem Implant), plus an
SCQA diagnosis (S = biggest problem, C = root cause WITH a driver-decomposition formula
line, Q = hypothesis-framed question, A = answer that maps to the tracks), 1-3 tailored
strategy tracks, and 3 action-plan cards (현재->목표 / From->To); (12) KPIs to watch
(3-4 leading indicators with latest reading + "what to watch"); (13) Scenarios
(bull/base/bear, each with swing variable + outcome); (14) Risks & outlook; (15)
Sources footer. Filename:
industry-report_<YYYY-MM-DD>_<GICScode>_<IndustrySlug>.html. Save all 7 into
reports/<YYYY-MM-DD>/ (create the folder).

STEP 4A — GICS TAXONOMY BREADCRUMB (REQUIRED in the hero of EVERY report). The
template you copy already contains the CSS (<style id="gics-tax-css">) and a
<div class="gics-tax"> breadcrumb in the hero. KEEP the CSS verbatim and REPLACE the
breadcrumb items for today's code. Render the FULL GICS path as labeled items separated
by the chevron span, with ONLY the current level marked class="gt-i cur":
- Phase 1 (6-digit industry code): 3 levels — Sector (code[:2]) > Industry Group
  (code[:4]) > Industry (code[:6], CURRENT).
- Phase 2 (8-digit sub-industry code): 4 levels — Sector (code[:2]) > Industry Group
  (code[:4]) > Industry (code[:6]) > Sub-Industry (code[:8], CURRENT). The parent
  Industry name (code[:6]) comes from the L1 list in STEP 1; the Sub-Industry name
  (code, name) from subindustries.json.
Each item HTML (bilingual; add " cur" to class only for the current level):
<span class="gt-i cur"><span class="gt-c">CODE</span><span class="gt-n"><span class="en">EN</span><span class="ko">KO</span></span><span class="gt-l"><span class="en">LEVEL_EN</span><span class="ko">LEVEL_KO</span></span></span>
Lead with <span class="gt-h"><span class="en">GICS</span><span class="ko">GICS 분류</span></span>
and put <span class="gt-a" aria-hidden="true">&#8250;</span> between items. Level labels:
Sector/섹터, Industry Group/산업군, Industry/산업, Sub-Industry/세부산업. The old
"GICS · sector · code" pill is REPLACED by this breadcrumb (keep the date and Players pills).
SECTOR (code[:2]) EN|KO: 10 Energy|에너지; 15 Materials|소재; 20 Industrials|산업재;
25 Consumer Discretionary|경기소비재; 30 Consumer Staples|필수소비재; 35 Health Care|헬스케어;
40 Financials|금융; 45 Information Technology|정보기술; 50 Communication Services|커뮤니케이션 서비스;
55 Utilities|유틸리티; 60 Real Estate|부동산.
INDUSTRY GROUP (code[:4]) EN|KO: 1010 Energy|에너지; 1510 Materials|소재; 2010 Capital Goods|자본재;
2020 Commercial & Professional Services|상업·전문 서비스; 2030 Transportation|운송;
2510 Automobiles & Components|자동차·부품; 2520 Consumer Durables & Apparel|내구소비재·의류;
2530 Consumer Services|소비자 서비스; 2550 Consumer Discretionary Distribution & Retail|경기소비재 유통·소매;
3010 Consumer Staples Distribution & Retail|필수소비재 유통·소매; 3020 Food, Beverage & Tobacco|식품·음료·담배;
3030 Household & Personal Products|가정·개인 용품; 3510 Health Care Equipment & Services|헬스케어 장비·서비스;
3520 Pharmaceuticals, Biotechnology & Life Sciences|제약·바이오·생명과학; 4010 Banks|은행;
4020 Financial Services|금융 서비스; 4030 Insurance|보험; 4510 Software & Services|소프트웨어·서비스;
4520 Technology Hardware & Equipment|기술 하드웨어·장비; 4530 Semiconductors & Semiconductor Equipment|반도체·반도체 장비;
5010 Telecommunication Services|통신 서비스; 5020 Media & Entertainment|미디어·엔터테인먼트; 5510 Utilities|유틸리티;
6010 Equity Real Estate Investment Trusts (REITs)|리츠(REITs); 6020 Real Estate Management & Development|부동산 관리·개발.

STEP 5 — Build the 7 landing entries: for each industry an object {date, gics, sector,
set_index, industry_en, industry_ko, global_company, korea_company, file, headline_en,
headline_ko (~습니다체), accent}. The "file" field MUST be
"reports/<YYYY-MM-DD>/industry-report_<YYYY-MM-DD>_<GICScode>_<IndustrySlug>.html".
Use raw ampersands (&) in JSON strings, not &amp;.

STEP 6 — VERIFY BEFORE FINISHING (mandatory). GOLDEN RULE: any report HTML that you
created or changed must pass a FRESH verification before this run ends.
(a) FACT-CHECK: for each of the 7 reports, dispatch an INDEPENDENT verification (fresh
web search, do NOT reuse the original research) rating each KEY claim ✓ Confirmed /
⚠ Roughly right / ✗ Wrong-or-unsupported: the GLOBAL #1 and KOREA #1 identity, each
player's headline financials AND current market cap (±10% tolerance; "비상장" claims
must be verified too), market-size figures and CAGR, market-share percentages,
and every dated regulation/recent-issue. Run the 7 in PARALLEL (one subagent each).
(b) CORRECT every ✗ and every stale/meaningfully-off ⚠ in the HTML, keeping EN and KO
numbers IDENTICAL. Where a number is genuinely scope-dependent, keep it but label it
"indicative/approx" and make the caption honest.
(c) INTEGRITY GATE: confirm each file has equal <span class="en"> and <span class="ko">
counts; exactly 2 pie charts summing to 100%; 5 Five-Forces items; 6 KSF cards; 2
leader/strategy blocks; a value-chain flow + profit-pool bar; a 2x2 SVG with 4 plotted
points; 2 SCQA diagnoses (S/C/Q/A each appear twice); a KPI watchlist (3-4 cards); 3
scenario cards; a market-cap stat in BOTH player blocks; equal en/ko span counts AFTER
the Korean rewrite pass; and that the regulation and news sections share NO duplicate
item. Fix any failure. Order of operations within this run: STEP 4 (English build) →
STEP 6a/6b (fact-check + corrections, English) → STEP 3 PASS 2 (Korean rewrite) →
numeric-consistency gate → STEP 6c integrity gate → STEP 7.

STEP 7 — Merge today's 7 objects into reports.json (it holds all history; do not drop
existing entries; if an entry for today's file already exists, overwrite it), then run
`node build_index.js` to rebuild index.html. Do NOT commit or push — the workflow does
that. Finish by printing a short summary: today's 7 GICS industries, each one's global
#1 and Korea #1, and any figures corrected during STEP 6.

STEP 8 — WRITE THE MORNING DIGEST (a later workflow step emails it; do NOT commit it).
After the 7 reports and reports.json/index.html are done, write TWO files at the repo
ROOT:

1) `digest.html` — a self-contained, INLINE-STYLED (email-safe) HTML body, KOREAN-
   primary in polite 합쇼체 (this is a personal morning brief the owner actually reads).
   Write the Korean natively in the same secretary-briefing register as the reports (번역체 금지). Mobile-friendly, max-width ~600px, INLINE css only (no <style> blocks, no external
   assets, no <script>; mail clients strip them). Structure, in this order:
   - Header line: "The Industry Brief · 오늘의 다이제스트 · <YYYY-MM-DD>" with a link to
     the landing page https://dshseungwon.github.io/daily-industry-report/ .
   - "오늘의 픽" card FIRST: pick the SINGLE most interesting/important of today's 7
     (one short clause on why it is the pick), then a 3-LINE summary (exactly 3 sentences)
     of what is moving and why it matters today, then a prominent link
     "전체 리포트 보기 →" to that report's live URL.
   - "오늘의 7개 산업" list: each of the 7 on ONE line —
     산업명(국문) (English) · 글로벌 1위 / 한국 1위 · 한 줄 takeaway —
     and make each line a link to its own live report URL.
   - Live URLs are exactly
     https://dshseungwon.github.io/daily-industry-report/reports/<YYYY-MM-DD>/<filename>
     using the precise filenames you created in reports/<YYYY-MM-DD>/.
   Keep it scannable: the whole email should be readable in under a minute. No em-dash
   characters anywhere; use commas, periods, or parentheses.

2) `digest_subject.txt` — exactly ONE line, the email subject, e.g.
   "오늘의 픽: <산업명(국문)> · The Industry Brief <YYYY-MM-DD>". No trailing newline-only
   second line.

These two files are git-ignored on purpose; leave them in the working tree and do NOT
commit them. Then finish by printing the short run summary as described in STEP 7.
