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

STEP 1 — Pick today's 7 GICS industries with the LANE rotation (one per lane -> 7
different list positions; do NOT use a consecutive day*7 block). Compute today's date in Korea time
with `TZ=Asia/Seoul date +%F` and run:

python3 - <<'PY'
from datetime import date, datetime
from zoneinfo import ZoneInfo
industries = ["Energy Equipment & Services","Oil, Gas & Consumable Fuels","Chemicals","Construction Materials","Containers & Packaging","Metals & Mining","Paper & Forest Products","Aerospace & Defense","Building Products","Construction & Engineering","Electrical Equipment","Industrial Conglomerates","Machinery","Trading Companies & Distributors","Commercial Services & Supplies","Professional Services","Air Freight & Logistics","Passenger Airlines","Marine Transportation","Ground Transportation","Transportation Infrastructure","Automobile Components","Automobiles","Household Durables","Leisure Products","Textiles, Apparel & Luxury Goods","Hotels, Restaurants & Leisure","Diversified Consumer Services","Distributors","Broadline Retail","Specialty Retail","Consumer Staples Distribution & Retail","Beverages","Food Products","Tobacco","Household Products","Personal Care Products","Health Care Equipment & Supplies","Health Care Providers & Services","Health Care Technology","Biotechnology","Pharmaceuticals","Life Sciences Tools & Services","Banks","Financial Services","Consumer Finance","Capital Markets","Mortgage REITs","Insurance","IT Services","Software","Communications Equipment","Technology Hardware, Storage & Peripherals","Electronic Equipment, Instruments & Components","Semiconductors & Semiconductor Equipment","Diversified Telecommunication Services","Wireless Telecommunication Services","Media","Entertainment","Interactive Media & Services","Electric Utilities","Gas Utilities","Multi-Utilities","Water Utilities","Independent Power and Renewable Electricity Producers","Diversified REITs","Industrial REITs","Hotel & Resort REITs","Office REITs","Health Care REITs","Residential REITs","Retail REITs","Specialized REITs","Real Estate Management & Development"]
N=len(industries); PER=7; day=(datetime.now(ZoneInfo("Asia/Seoul")).date()-date(2026,1,1)).days
for l in range(PER):
    s=(l*N)//PER; e=((l+1)*N)//PER; i=s+(day%(e-s)); print(l+1, i, "|", industries[i])
PY

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
toggle + section chips, reveal-on-scroll, prefers-reduced-motion. Keep two sections
MECE: "Macro forces & the latest RULES" = laws/bills/regulations ONLY (dated);
"What's moving the industry now" = market/competitive events ONLY (earnings, deals,
demand, prices). No item may appear in both.

Structure (analysis dominant; players secondary): (1) Header — brand "The Industry
Brief", industry, date, "GICS day-set k of 7", GICS sector + code; (2) Executive summary (≤3 sentences, the single most important points only); (3) Definition & value chain (numbered arrow flow + profit-pool bar); (4)
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
