# build/ — manual report generator (reference)

These scripts are the deterministic generator used to hand-build one day's batch
of 7 reports (the 2026-06-08 set is included as a worked example).

- `gen.py` — assembles each report's HTML from `_template.html` (style/script reused
  verbatim) plus a per-industry data dict; also writes `today.json` (landing entries).
- `r1.py … r7.py` — the 7 per-industry data dicts for the example day.
- `reports_data.py` — collects r1…r7 into the list `gen.py` consumes.
- `_template.html` — a recent report whose `<style>`/`<script>` are reused.

Run locally with: `python3 build/gen.py` (writes the 7 HTML files + today.json).

NOTE: the daily GitHub Action does NOT use these scripts. It runs Claude Code with
`prompts/daily-industry-report.md`, which regenerates the batch by copying the newest
report as a template. These files are kept for reference / manual rebuilds.
