You are running headless inside a GitHub Actions runner, in a fresh checkout of the
repo `dshseungwon/daily-industry-report` (cwd = repo root). No human is present.
Execute autonomously. Do NOT git commit or push: a later workflow step does that.

ONE-OFF MAINTENANCE JOB, two goals:

(A) KOREAN REWRITE of every report dated BEFORE 2026-06-10 (the folders
reports/<date>/ where <date> < 2026-06-10; the 2026-06-10 reports are ALREADY in the
new register — do not retranslate them). The current Korean in old reports is
translationese. For each old report, REWRITE every <span class="ko"> from its
<span class="en"> twin as a top-tier executive secretary briefing the chairman:
- 합쇼체 보고체: "~로 파악됩니다", "~한 바 있습니다", "~할 것으로 보입니다",
  "시사점을 말씀드리면 ~라는 점입니다". 영어 문장 구조를 버리고 한국어 호흡으로 재구성
  (문장 분할, 연결어 "실제로/다만/앞서/이에 따라" 추가 자유).
- 번역체 금지: "~에 의해", "~되어지다" 류 직역투, 어색한 영어 명사구 직역 금지.
- 짧은 라벨/제목/차트 라벨/KPI 제목은 간결한 명사형(예: "Executive summary"→"핵심 보고",
  "Bull · upside"→"낙관 시나리오", "KPIs to watch"→"주시할 지표"). "Why it matters:"→"시사점:".
- 용어집: market share→시장점유율, value chain→가치사슬, moat→해자, KSF→핵심성공요인,
  CAGR→연평균 성장률(CAGR), profit pool→이익 풀, backlog→수주잔고, occupancy→입주율,
  net interest income→순이자이익, fee income→비이자수익.
- 단위 변환 반드시 검산: $X billion = X×10억 달러($35.71B→357억 1,000만 달러),
  $X trillion = X조 달러, €1,085B→1조 850억 유로(1,085억 아님), ₩61.1T→61.1조 원,
  X percentage points→X%포인트. 헷갈리면 원문 표기 유지가 오역보다 낫다.
- 한국 기업은 한국어 정식 명칭, 해외 기업은 통용 한글 표기(널리 쓰일 때만), 약어형
  사명·기관(SLB, UPS, ZF, FDA, CMS)은 영문 유지. 수치/연도/날짜/%는 EN과 정확히 일치.

- 제목·라벨은 멋부린 헤드라인 금지, 표준 용어로: "승부를 가르는 조건"→"핵심 성공 요인", "두 플레이어, 각자의 전략"→"주요 기업 · 전략 분석", "규정집"→"규제·정책", "뉴스 흐름"→"최근 시장 동향", "계기판"→"주시할 지표", "향후 몇 년, 세 갈래 경로"→"시나리오: 낙관·기본·비관". 비유·장식어 금지, 비서가 임원에게 보고하듯 평이하게.
- HTML 엔티티(&amp; 등)는 그대로 유지. ko 스팬 안에 태그를 새로 넣지 말 것.
Recommended mechanics per report: extract unique EN span strings to JSON, write the
Korean array, inject by matching the en-span text (normalize whitespace), exactly as a
script — do NOT hand-edit spans one by one in the HTML. Use parallel subagents, one
per dated folder, to stay within the time limit.

(B) MARKET-CAP BACKFILL for ALL reports (every dated folder INCLUDING 2026-06-10).
In section 11 (PLAYERS · strategy analysis) each of the two player blocks has stat
callouts (class="stat"). ADD one more stat to each player block, matching the existing
stat markup exactly, bilingual:
- EN label "Market cap", KO label "시가총액".
- Value: current market cap with as-of month, e.g. EN "$348B (Jun 2026)" /
  KO "3,480억 달러(2026년 6월)"; Korean companies in ₩조 원 (e.g. "₩11.9T (May 2026)" /
  "11.9조 원(2026년 5월)").
- If the company is UNLISTED (e.g. Bosch=private, Osstem Implant=delisted 2023,
  LH Dongtan REIT=pre-IPO, IKEA, Mars, state-owned entities…): EN "Private (unlisted)" /
  KO "비상장". Do NOT invent a number.
- RESEARCH each company's CURRENT market cap with web search (June 2026 values,
  stockanalysis.com / companiesmarketcap.com / recent news are fine sources). One
  lookup per unique company; reuse across reports where the same company appears.
- Do not add a duplicate if a market-cap stat already exists in that block.

(C) reports.json: for every entry dated before 2026-06-10, REWRITE headline_ko in the
same briefing register (keep headline_en and all other fields unchanged). Keep raw
ampersands (&) in JSON strings.

(D) VERIFY before finishing (mandatory):
1. Every modified file: equal counts of <span class="en"> and <span class="ko">.
2. EN/KO numeric-consistency gate over ALL reports — run and fix every real mismatch
   (years, %, converted currency magnitudes must be correct; representation-only
   differences like "about a quarter"→"약 25%" may be accepted):

python3 - <<'PY'
import re, glob
bad = 0
for f in glob.glob('reports/*/industry-report_*.html'):
    s = open(f, encoding='utf-8').read()
    for e, k in re.findall(r'<span class="en">(.*?)</span><span class="ko">(.*?)</span>', s, re.S):
        if not re.search(r'[가-힣]', k): continue
        ye = set(m.group(0) for m in re.finditer(r'(?<!\d)(?:19|20)\d{2}(?!\d)', e))
        yk = set(m.group(0) for m in re.finditer(r'(?<!\d)(?:19|20)\d{2}(?!\d)', k))
        pe = sorted(re.findall(r'\d+(?:\.\d+)?(?=%)', e)); pk = sorted(re.findall(r'\d+(?:\.\d+)?(?=%|％)', k))
        if (pe != pk and not set(pe) <= set(pk)) or not ye <= yk:
            print(f, '|', e[:70]); bad += 1
print('mismatches:', bad)
PY

3. Every report has a market-cap stat in BOTH player blocks (grep '시가총액' count == 2
   per file; for proxy/unlisted players the label still appears with 비상장).
4. Spot-recompute 10 of the currency conversions you wrote.
5. Run `node build_index.js` (reports.json changed) and confirm it succeeds.

Finish by printing: number of reports retranslated, number of market-cap stats added
(listed vs 비상장), and any numeric fixes made.
