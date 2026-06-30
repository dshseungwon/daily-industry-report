#!/usr/bin/env node
/*
 * build_index.js — regenerates index.html (bilingual landing) from reports.json.
 *
 * Each run publishes 7 GICS-industry reports per day; each report covers a global
 * #1 and a Korea #1. The landing groups cards by day (7 per day), shows both
 * leaders on each card, and has its own 한국어/English toggle (persisted, shared
 * key "dis-lang" so it matches the reports).
 *
 * reports.json entry shape:
 *   { date, gics, sector, set_index, industry_en, industry_ko,
 *     global_company, korea_company, file, headline_en, headline_ko, accent }
 *
 * Usage: node build_index.js [dir]   (dir defaults to this folder = Pages root)
 */
const fs = require("fs");
const path = require("path");

const ROOT = process.argv[2] || __dirname;
const PER_DAY = 7;
const INDUSTRIES = [
  "Energy Equipment & Services","Oil, Gas & Consumable Fuels","Chemicals",
  "Construction Materials","Containers & Packaging","Metals & Mining",
  "Paper & Forest Products","Aerospace & Defense","Building Products",
  "Construction & Engineering","Electrical Equipment","Industrial Conglomerates",
  "Machinery","Trading Companies & Distributors","Commercial Services & Supplies",
  "Professional Services","Air Freight & Logistics","Passenger Airlines",
  "Marine Transportation","Ground Transportation","Transportation Infrastructure",
  "Automobile Components","Automobiles","Household Durables","Leisure Products",
  "Textiles, Apparel & Luxury Goods","Hotels, Restaurants & Leisure",
  "Diversified Consumer Services","Distributors","Broadline Retail",
  "Specialty Retail","Consumer Staples Distribution & Retail","Beverages",
  "Food Products","Tobacco","Household Products","Personal Care Products",
  "Health Care Equipment & Supplies","Health Care Providers & Services",
  "Health Care Technology","Biotechnology","Pharmaceuticals",
  "Life Sciences Tools & Services","Banks","Financial Services","Consumer Finance",
  "Capital Markets","Mortgage REITs","Insurance","IT Services","Software",
  "Communications Equipment","Technology Hardware, Storage & Peripherals",
  "Electronic Equipment, Instruments & Components",
  "Semiconductors & Semiconductor Equipment",
  "Diversified Telecommunication Services","Wireless Telecommunication Services",
  "Media","Entertainment","Interactive Media & Services","Electric Utilities",
  "Gas Utilities","Multi-Utilities","Water Utilities",
  "Independent Power and Renewable Electricity Producers","Diversified REITs",
  "Industrial REITs","Hotel & Resort REITs","Office REITs","Health Care REITs",
  "Residential REITs","Retail REITs","Specialized REITs",
  "Real Estate Management & Development",
];
const N = INDUSTRIES.length;

function esc(s){return String(s==null?"":s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}
function fmtDate(iso){const [y,m,d]=iso.split("-").map(Number);
  const mon=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][m-1];return `${mon} ${d}, ${y}`;}
function fmtDateKo(iso){const [y,m,d]=iso.split("-").map(Number);return `${y}년 ${m}월 ${d}일`;}
function daysSinceEpoch(iso){return Math.round((new Date(iso+"T00:00:00Z")-new Date("2026-01-01T00:00:00Z"))/86400000);}

// load
let reports=[];
try{reports=JSON.parse(fs.readFileSync(path.join(ROOT,"reports.json"),"utf8"))||[];}catch(e){reports=[];}
reports=reports.filter(r=>r&&r.date&&r.file);
const specials=reports.filter(r=>r.special);
reports=reports.filter(r=>!r.special);

// group by date desc, set_index asc
const byDate={};
reports.forEach(r=>{(byDate[r.date]=byDate[r.date]||[]).push(r);});
const dates=Object.keys(byDate).sort((a,b)=>a<b?1:-1);
dates.forEach(d=>byDate[d].sort((a,b)=>(a.set_index||0)-(b.set_index||0)));

function card(r){
  const accent=/^#?[0-9a-fA-F]{6}$/.test(r.accent||"")?(r.accent[0]==="#"?r.accent:"#"+r.accent):"#117aca";
  const search=esc(((r.industry_en||"")+" "+(r.industry_ko||"")+" "+(r.global_company||"")+" "+(r.korea_company||"")).toLowerCase());
  const href=r.file&&r.file!=="#"?esc(r.file):null;
  const inner=`
      <div class="card-top">
        <span class="gics">${r.special?"SPECIAL REPORT":"GICS "+esc(r.gics||"")}</span>
        <span class="sector">${esc(r.sector||"")}</span>
      </div>
      <h3 class="ind"><span class="en">${esc(r.industry_en)}</span><span class="ko">${esc(r.industry_ko)}</span></h3>
      <div class="leaders">
        <div class="ld"><span class="ldtag glo"><span class="en">Global</span><span class="ko">글로벌</span></span><b>${esc(r.global_company)}</b></div>
        <div class="ld"><span class="ldtag kor"><span class="en">Korea</span><span class="ko">한국</span></span><b>${esc(r.korea_company)}</b></div>
      </div>
      <p class="head"><span class="en">${esc(r.headline_en||"")}</span><span class="ko">${esc(r.headline_ko||"")}</span></p>
      <span class="go">${href?'<span class="en">Read report &rarr;</span><span class="ko">리포트 보기 &rarr;</span>':'<span class="en">Sample</span><span class="ko">샘플</span>'}</span>`;
  return href
    ? `<a class="rcard reveal" href="${href}" style="--accent:${accent}" data-search="${search}">${inner}</a>`
    : `<div class="rcard sample reveal" style="--accent:${accent}" data-search="${search}">${inner}</div>`;
}

function dayHtml(d){
  const cards=byDate[d].map(card).join("\n");
  return `
    <section class="day">
      <div class="day-head">
        <span class="day-date"><span class="en">${esc(fmtDate(d))}</span><span class="ko">${esc(fmtDateKo(d))}</span></span>
        <span class="day-meta">${byDate[d].length} <span class="en">reports</span><span class="ko">개</span></span>
      </div>
      <div class="grid">
${cards}
      </div>
    </section>`;
}
const isPhase1=r=>/^\d{6}$/.test(String(r.gics||""));
const legDate=d=>byDate[d].every(isPhase1);
const curDates=dates.filter(d=>!legDate(d));
const legDates=dates.filter(d=>legDate(d));
const daySections=curDates.map(dayHtml).join("\n");
const legacySections=legDates.map(dayHtml).join("\n");
const legCount=legDates.reduce((a,d)=>a+byDate[d].length,0);
const specialHtml = specials.length ? `
    <section class="day special-sec">
      <div class="day-head">
        <span class="day-date"><span class="en">Special Reports</span><span class="ko">스페셜 리포트</span></span>
        <span class="day-meta">${specials.length} <span class="en">special</span><span class="ko">개</span></span>
      </div>
      <div class="grid">
${specials.map(card).join("\n")}
      </div>
    </section>` : "";
const legacyHtml = legacySections ? `
    <div style="margin:24px 0 4px;text-align:center;">
      <button id="legacy-toggle" aria-expanded="false" style="background:#fff;border:1px solid var(--line);border-radius:999px;padding:10px 18px;font-size:13.5px;font-weight:700;color:var(--ink);box-shadow:var(--shadow);cursor:pointer;">
        <span class="en">Earlier industry-level reports</span><span class="ko">이전 산업 단위 리포트</span>
        <span style="color:var(--mute);font-weight:800;"> · ${legCount}</span>
        <span id="lt-chev" style="display:inline-block;transition:transform .25s;">&#9662;</span>
      </button>
    </div>
    <div id="legacy" hidden>
      <p class="empty" style="margin:6px 0 2px;"><span class="en">These analyse the broader GICS industry (Phase 1). The daily series now drills into GICS sub-industries.</span><span class="ko">아래는 상위 GICS 산업 단위(Phase 1) 분석입니다. 현재 데일리 시리즈는 GICS 세부산업으로 더 깊이 들어가고 있습니다.</span></p>
${legacySections}
    </div>` : "";

// up next: next day's 7-industry set after the most recent published day
let upHtml="";
if(dates.length){
  const nextDay=new Date(new Date(dates[0]+"T00:00:00Z").getTime()+86400000).toISOString().slice(0,10);
  // Lane rotation: split the 74 industries into 7 contiguous lanes and pick one
  // from each lane per day, so every day spans 7 different sectors.
  const dy=daysSinceEpoch(nextDay), items=[];
  for(let l=0;l<PER_DAY;l++){
    const s=Math.floor(l*N/PER_DAY), e=Math.floor((l+1)*N/PER_DAY), len=e-s;
    items.push(INDUSTRIES[s+(((dy%len)+len)%len)]);
  }
  upHtml=`
    <section class="day">
      <div class="day-head">
        <span class="day-date"><span class="en">Up next · ${esc(fmtDate(nextDay))}</span><span class="ko">다음 회차 · ${esc(fmtDateKo(nextDay))}</span></span>
      </div>
      <div class="up-grid">
${items.map(i=>`        <div class="up">${esc(i)}</div>`).join("\n")}
      </div>
    </section>`;
}

const totalReports=reports.length+specials.length, totalDays=dates.length;
const lastUpdEn=dates.length?fmtDate(dates[0]):"", lastUpdKo=dates.length?fmtDateKo(dates[0]):"";

const html=`<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Industry Brief · 데일리 GICS 산업 분석</title>
<style>
  :root{--navy:#0e2a47;--blue:#117aca;--gold:#ffb81c;--ink:#13314f;--mute:#5b6b8c;
    --line:#e6ebf4;--bg:#eef2f7;--card:#fff;--accent:#117aca;--krred:#c8102e;--krblue:#0047a0;
    --radius:16px;--shadow:0 8px 24px rgba(14,42,71,.10);}
  *{box-sizing:border-box;}
  html{scroll-behavior:smooth;}
  body{margin:0;background:var(--bg);color:var(--ink);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;
    line-height:1.55;-webkit-font-smoothing:antialiased;-webkit-text-size-adjust:100%;}
  a{text-decoration:none;color:inherit;}
  .wrap{max-width:1040px;margin:0 auto;padding:0 16px;}
  body.lang-ko .en{display:none;}
  body.lang-en .ko{display:none;}
  .topbar{position:sticky;top:0;z-index:50;background:rgba(14,42,71,.97);backdrop-filter:blur(8px);border-bottom:1px solid #21426b;}
  .topbar .row{display:flex;align-items:center;gap:10px;max-width:1040px;margin:0 auto;padding:9px 14px;}
  .brand{color:#fff;font-weight:800;font-size:15px;}
  .brand span.g{color:var(--gold);}
  #lang{margin-left:auto;background:var(--gold);color:var(--navy);border:none;border-radius:999px;padding:7px 14px;font-size:13px;font-weight:800;cursor:pointer;}
  .hero{background:linear-gradient(160deg,#123a61,#0e2a47 62%);color:#fff;border-radius:0 0 26px 26px;padding:32px 0 28px;border-left:8px solid var(--gold);}
  .eyebrow{color:var(--gold);font-weight:700;letter-spacing:2px;font-size:12px;text-transform:uppercase;margin:0 0 12px;}
  .hero h1{font-size:clamp(27px,7vw,42px);margin:0 0 8px;font-weight:800;letter-spacing:-.5px;line-height:1.08;}
  .hero .sub{font-size:clamp(14px,3.8vw,18px);color:#cfe2f5;margin:0 0 16px;}
  .meta{display:flex;flex-wrap:wrap;gap:8px;}
  .mpill{background:rgba(255,255,255,.10);border:1px solid rgba(207,226,245,.25);border-radius:999px;padding:6px 13px;font-size:13px;color:#eaf3fb;}
  .mpill b{color:var(--gold);}
  .search-wrap{margin:16px 0 2px;}
  #search{width:100%;padding:13px 16px;border:1px solid var(--line);border-radius:999px;font-size:15px;background:#fff;color:var(--ink);box-shadow:var(--shadow);}
  #search:focus{outline:2px solid var(--blue);}
  .day{padding:22px 0 2px;}
  .day-head{display:flex;align-items:baseline;gap:12px;margin:0 0 13px;border-bottom:1px solid var(--line);padding-bottom:8px;}
  .day-date{font-size:clamp(17px,4.6vw,21px);font-weight:800;letter-spacing:-.3px;}
  .day-meta{color:var(--mute);font-size:13px;font-weight:600;}
  .grid{display:grid;grid-template-columns:1fr;gap:13px;}
  .rcard{display:block;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:17px;box-shadow:var(--shadow);border-top:5px solid var(--accent);transition:transform .15s,box-shadow .15s;}
  a.rcard:hover{transform:translateY(-3px);box-shadow:0 14px 30px rgba(14,42,71,.16);}
  .rcard.sample{opacity:.82;border-style:dashed;}
  .card-top{display:flex;justify-content:space-between;gap:8px;margin-bottom:7px;}
  .gics{background:var(--accent);color:#fff;font-weight:700;font-size:11.5px;padding:3px 10px;border-radius:999px;}
  .sector{color:var(--mute);font-size:11.5px;font-weight:600;align-self:center;}
  .ind{font-size:clamp(17px,4.6vw,20px);margin:2px 0 9px;font-weight:800;letter-spacing:-.3px;}
  .leaders{display:flex;flex-direction:column;gap:5px;margin-bottom:9px;}
  .ld{font-size:13.5px;color:var(--ink);display:flex;align-items:center;gap:8px;}
  .ld b{font-weight:700;}
  .ldtag{flex:none;font-size:10.5px;font-weight:800;letter-spacing:.5px;text-transform:uppercase;color:#fff;border-radius:6px;padding:2px 7px;}
  .ldtag.glo{background:var(--navy);}
  .ldtag.kor{background:var(--krred);}
  .head{font-size:13.5px;color:var(--mute);margin:0 0 11px;}
  .go{font-weight:700;color:var(--accent);font-size:13.5px;}
  .rcard.sample .go{color:var(--mute);}
  .up-grid{display:grid;grid-template-columns:1fr;gap:8px;}
  .up{background:#fff;border:1px dashed #c5d3e6;border-radius:11px;padding:10px 14px;font-size:13.5px;color:var(--ink);}
  .reveal{opacity:0;transform:translateY(14px);transition:opacity .5s,transform .5s;}
  .reveal.in{opacity:1;transform:none;}
  .empty{color:var(--mute);font-size:15px;padding:8px 2px;}
  footer{background:var(--navy);color:#9fb6d2;margin-top:28px;padding:20px 0 30px;font-size:13px;border-radius:26px 26px 0 0;}
  .disclaim{color:#7188a8;font-size:12px;margin-top:6px;}
  @media(min-width:640px){.grid{grid-template-columns:1fr 1fr;}.up-grid{grid-template-columns:1fr 1fr;}}
  @media(min-width:980px){.grid{grid-template-columns:1fr 1fr 1fr;}.up-grid{grid-template-columns:repeat(4,1fr);}}
  @media(prefers-reduced-motion:reduce){html{scroll-behavior:auto;}.reveal{opacity:1;transform:none;transition:none;}.rcard{transition:none;}}
</style>
</head>
<body class="lang-ko">
  <div class="topbar"><div class="row">
    <div class="brand">The Industry Brief</div>
    <button id="lang" aria-label="Toggle language"><span class="en">한국어</span><span class="ko">EN</span></button>
  </div></div>

  <div class="hero"><div class="wrap">
    <p class="eyebrow"><span class="en">Daily GICS industry analysis</span><span class="ko">데일리 GICS 산업 분석</span></p>
    <h1>The Industry Brief</h1>
    <p class="sub"><span class="en">A daily GICS industry, decoded with strategy frameworks — its structure, forces and regulation, plus the global and Korean leaders and a strategy for each.</span><span class="ko">매일 GICS 산업 하나를 전략 프레임워크로 분석해 드립니다. 산업 구조·경쟁요인·규제와 함께, 글로벌·한국 1위 기업의 전략까지 정리해 드립니다.</span></p>
    <div class="meta">
      <span class="mpill"><b>${totalReports}</b> <span class="en">reports</span><span class="ko">개 리포트</span></span>
      <span class="mpill"><b>${totalDays}</b> <span class="en">day(s)</span><span class="ko">일치</span></span>
      <span class="mpill"><span class="en">Updated</span><span class="ko">업데이트</span> <b><span class="en">${esc(lastUpdEn)}</span><span class="ko">${esc(lastUpdKo)}</span></b></span>
      <span class="mpill"><span class="en">74-industry GICS rotation</span><span class="ko">74개 GICS 산업 순환</span></span>
    </div>
    <div class="search-wrap"><input id="search" type="search" placeholder="Search industry or company… · 산업·기업 검색" aria-label="Search"></div>
  </div></div>

  <div class="wrap" id="content">
${specialHtml}
${daySections || '    <p class="empty"><span class="en">No reports yet. The first batch publishes after the next scheduled run.</span><span class="ko">아직 리포트가 없습니다. 다음 예약 실행 후 첫 묶음이 게시됩니다.</span></p>'}
    <p class="empty" id="noresult" style="display:none"><span class="en">No matches.</span><span class="ko">검색 결과가 없습니다.</span></p>
${upHtml}
${legacyHtml}
  </div>

  <footer><div class="wrap">
    The Industry Brief · <span class="en">auto-generated landing page.</span><span class="ko">자동 생성 랜딩 페이지.</span>
    <div class="disclaim"><span class="en">Informational only, not investment advice. Generated ${esc(lastUpdEn)}.</span><span class="ko">정보 제공용이며 투자 자문이 아닙니다. ${esc(lastUpdKo)} 생성.</span></div>
  </div></footer>

  <script>
    var KEY='dis-lang';
    function setLang(l){document.body.classList.toggle('lang-ko',l==='ko');document.body.classList.toggle('lang-en',l==='en');document.documentElement.lang=l;try{localStorage.setItem(KEY,l);}catch(e){}}
    var saved=null;try{saved=localStorage.getItem(KEY);}catch(e){}setLang(saved==='en'?'en':'ko'); // default Korean; remembers selection
    var b=document.getElementById('lang');
    if(b)b.addEventListener('click',function(){setLang(document.body.classList.contains('lang-ko')?'en':'ko');});
    var q=document.getElementById('search'),nores=document.getElementById('noresult');
    if(q)q.addEventListener('input',function(){
      var t=q.value.trim().toLowerCase(),cards=document.querySelectorAll('.rcard'),shown=0;
      cards.forEach(function(c){var m=!t||(c.getAttribute('data-search')||'').indexOf(t)>-1;c.style.display=m?'':'none';if(m)shown++;});
      nores.style.display=(cards.length&&shown===0)?'':'none';
    });
    var lt=document.getElementById('legacy-toggle'),lg=document.getElementById('legacy'),ch=document.getElementById('lt-chev');
    if(lt&&lg)lt.addEventListener('click',function(){var h=lg.hasAttribute('hidden');if(h){lg.removeAttribute('hidden');lt.setAttribute('aria-expanded','true');if(ch)ch.style.transform='rotate(180deg)';lg.querySelectorAll('.reveal').forEach(function(e){e.classList.add('in');});}else{lg.setAttribute('hidden','');lt.setAttribute('aria-expanded','false');if(ch)ch.style.transform='';}});
    var reduce=window.matchMedia('(prefers-reduced-motion:reduce)').matches;
    if(reduce||!('IntersectionObserver'in window)){document.querySelectorAll('.reveal').forEach(function(e){e.classList.add('in');});}
    else{var io=new IntersectionObserver(function(en){en.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target);}});},{threshold:.08});
      document.querySelectorAll('.reveal').forEach(function(e){io.observe(e);});}
  </script>
</body>
</html>`;

fs.writeFileSync(path.join(ROOT,"index.html"),html);
console.log(`index.html rebuilt: ${totalReports} report(s) across ${totalDays} day(s).`);
