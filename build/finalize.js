// One-time finalize when the sub-industry lap completes: keep one (latest) report
// per GICS code, delete superseded report HTML, rebuild the landing, and drop a
// .rotation-complete marker so the daily job stops publishing afterwards.
const fs = require('fs');
const { execSync } = require('child_process');

let r = JSON.parse(fs.readFileSync('reports.json', 'utf8'));
const by = {};
for (const x of r) {
  const k = String(x.gics);
  if (!by[k] || x.date > by[k].date) by[k] = x;
}
const keep = Object.values(by);
const keepFiles = new Set(keep.map(x => x.file));

// remove orphaned report HTML (only under reports/, never touches magazine/)
function walk(d) {
  for (const f of fs.readdirSync(d, { withFileTypes: true })) {
    const p = d + '/' + f.name;
    if (f.isDirectory()) walk(p);
    else if (p.endsWith('.html') && !keepFiles.has(p)) { fs.unlinkSync(p); console.log('removed', p); }
  }
}
if (fs.existsSync('reports')) walk('reports');

keep.sort((a, b) => b.date.localeCompare(a.date) || String(a.gics).localeCompare(String(b.gics)));
fs.writeFileSync('reports.json', JSON.stringify(keep, null, 2) + '\n');
execSync('node build_index.js', { stdio: 'inherit' });
fs.writeFileSync('.rotation-complete', new Date().toISOString() + '\n');
console.log('finalize complete. unique reports kept:', keep.length);
