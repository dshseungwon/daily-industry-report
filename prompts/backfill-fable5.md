Headless GitHub Actions runner, fresh checkout of dshseungwon/daily-industry-report
(cwd = repo root). No human is present. Execute autonomously. Do NOT git commit or push
(a later workflow step does that).

The TARGET DATE is in the environment variable TARGET_DATE (format YYYY-MM-DD).
Your job: REGENERATE the 7 reports for TARGET_DATE ONLY, fully rebuilt from scratch on
the model you are running, and OVERWRITE the existing files for that date in place.

STEP 1 - Compute TARGET_DATE's 7 GICS industries with the LANE rotation (one per lane,
7 different sectors; do NOT use a consecutive day*7 block). Read the date from the
TARGET_DATE env var (do not use today's date):

python3 - <<'PYROT'
import os
from datetime import date
TARGET=os.environ["TARGET_DATE"]
industries=["Energy Equipment & Services","Oil, Gas & Consumable Fuels","Chemicals","Construction Materials","Containers & Packaging","Metals & Mining","Paper & Forest Products","Aerospace & Defense","Building Products","Construction & Engineering","Electrical Equipment","Industrial Conglomerates","Machinery","Trading Companies & Distributors","Commercial Services & Supplies","Professional Services","Air Freight & Logistics","Passenger Airlines","Marine Transportation","Ground Transportation","Transportation Infrastructure","Automobile Components","Automobiles","Household Durables","Leisure Products","Textiles, Apparel & Luxury Goods","Hotels, Restaurants & Leisure","Diversified Consumer Services","Distributors","Broadline Retail","Specialty Retail","Consumer Staples Distribution & Retail","Beverages","Food Products","Tobacco","Household Products","Personal Care Products","Health Care Equipment & Supplies","Health Care Providers & Services","Health Care Technology","Biotechnology","Pharmaceuticals","Life Sciences Tools & Services","Banks","Financial Services","Consumer Finance","Capital Markets","Mortgage REITs","Insurance","IT Services","Software","Communications Equipment","Technology Hardware, Storage & Peripherals","Electronic Equipment, Instruments & Components","Semiconductors & Semiconductor Equipment","Diversified Telecommunication Services","Wireless Telecommunication Services","Media","Entertainment","Interactive Media & Services","Electric Utilities","Gas Utilities","Multi-Utilities","Water Utilities","Independent Power and Renewable Electricity Producers","Diversified REITs","Industrial REITs","Hotel & Resort REITs","Office REITs","Health Care REITs","Residential REITs","Retail REITs","Specialized REITs","Real Estate Management & Development"]
y,mo,d=map(int,TARGET.split("-")); day=(date(y,mo,d)-date(2026,1,1)).days
N=len(industries); PER=7
for l in range(PER):
    s=(l*N)//PER; e=((l+1)*N)//PER; i=s+(day%(e-s)); print(l+1, i, "|", industries[i])
PYROT

STEP 2 - For EACH of the 7 industries, BUILD the bilingual report following the build
spec in prompts/daily-industry-report.md EXACTLY. That means everything it specifies:
the same section structure and order; vertical COLUMN chart for market size; two PIE
charts (CSS conic-gradient) for market share; competitive 2x2 SVG; Porter Five Forces
with rating chips; Key Success Factors; SCQA diagnosis + strategy tracks + From->To
action plans per player; market-cap stat in BOTH player blocks; KPI watchlist; bull/
base/bear scenarios; the PLAIN-LANGUAGE STYLE rules (standard section labels, executive
summary AT MOST 3 sentences, NO headline flourishes, NO translationese); ENGLISH default
bilingual toggle; and the two-pass Korean in the polite executive-briefing register.
Research current data with web search and year-stamp every figure. Then run the fact-
check + corrections and ALL integrity / numeric-consistency gates from that spec. Run
the 7 industries in PARALLEL with subagents (the Agent tool) to fit the time budget.

STEP 3 - OVERWRITE the existing files in reports/<TARGET_DATE>/ with the new content,
keeping the SAME filenames: industry-report_<TARGET_DATE>_<GICScode>_<IndustrySlug>.html
(the GICS code + slug for each industry are fixed by the rotation, so the filenames
match what already exists). Do NOT modify reports.json or index.html. Do NOT commit.
Finish by printing the 7 industries you regenerated for TARGET_DATE.
