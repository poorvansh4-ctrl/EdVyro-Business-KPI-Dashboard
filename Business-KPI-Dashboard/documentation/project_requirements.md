# Project Requirements Checklist

Verified on 19 November 2026 from EdVyro's public pages (no sign-in needed):
- Task guide: <https://edvyro.in/datasets/task-kits/data-analytics-task-2>
- Checklist: <https://edvyro.in/datasets/task-kits/data-analytics-task-2.md>
- Data guide: "Customer Churn Analysis Guide" in <https://edvyro.in/datasets/source-materials/task-source-library.html>
- Curriculum: <https://edvyro.in/internships/data-analytics> · Project guide: <https://edvyro.in/guides/data-analytics-project-guide>

Status key: ✅ done and verified · 🟡 prepared, needs a manual step from you · ⬜ not started

## A. Official EdVyro Task 2 passing checklist

| # | Requirement (EdVyro wording) | Status | Evidence |
|---|---|---|---|
| A1 | Define churn rate, retention rate, revenue at risk, and tenure KPIs | ✅ | `documentation/methodology.md` §3, `powerbi/dax_measures.md`, dashboard overview "How the KPIs are calculated" |
| A2 | Create filters for contract, tenure, and payment method | ✅ | Google Sheets: 4 slicers (contract, tenure group, payment method, churn status), tested as a signed-out viewer; web dashboard filter bar tested on all 300 combinations |
| A3 | Use appropriate charts with clear labels and accessible colours | ✅ | 12 titled Google Sheets charts with data labels; colour-blind-validated orange/blue pair (CVD ΔE 24.7 light / 26.8 dark) used in every dashboard |
| A4 | Put the work and a short explanation in one public or view-only link | 🟡 | Dashboard link is public (view-only). Explanation text ready in `submission_guide.md` §4. You still create the GitHub repository and submit (needs your accounts) |
| A5 | Deliverable: published Power BI, Tableau, Looker Studio, or spreadsheet dashboard link | ✅ | Google Sheets dashboard, view-only: <https://docs.google.com/spreadsheets/d/1i7BwdceJrBUXdqcdYteQnfCGl6LGgv06dqtX2r1riZY/edit?usp=sharing>. (No Power BI .pbix exists; the Power BI kit is optional extra evidence) |
| A6 | Optional upgrade: a written insight beside every major visual | ✅ | Google Sheets: insight subtitle under every chart; web dashboard: dynamic insight line under every chart |

## B. Guidance from the EdVyro project guide and data guide

| # | Guidance | Status | Evidence |
|---|---|---|---|
| B1 | Define each KPI before charting it; churn rate needs a denominator and scope | ✅ | Scope stated on dashboard and in methodology §3 |
| B2 | Check that a contract filter changes calculations consistently | ✅ | `tests/test_dashboard_metrics.js` (3,467 checks); spot checks in `dax_measures.md` §7 |
| B3 | Keep a small manual calculation to compare with the dashboard | ✅ | `methodology.md` §5 and `tests/test_pipeline.py` |
| B4 | Identify missing, duplicate, impossible and extreme values; keep a cleaning log; don't silently delete rows | ✅ | `documentation/data_cleaning.md`, `analysis/outputs/data_quality_log.json` |
| B5 | Separate descriptive findings from predictions; don't imply causation from correlation | ✅ | Caveats in insights, report §8–9, dashboard insight page |
| B6 | Recommendation names audience, decision, supporting metric, uncertainty, next measurement | ✅ | `documentation/recommendations.md` |
| B7 | Don't claim revenue saved from a classroom dataset | ✅ | No savings claimed; annual figure labelled "estimate" |
| B8 | Test the link in a signed-out browser before submitting | ✅ | Google Sheets link opened signed out and a filter used as a viewer (screenshots in `spreadsheet/screenshots/`). Repeat once yourself, and test the GitHub link after you create it |
| B9 | Share only material you have permission to publish; no private data | ✅ | Dataset is EdVyro's synthetic sample; no personal data added |

## C. Your project brief (12 phases)

| Phase | Status | Notes |
|---|---|---|
| 1 Research official resources | ✅ | All 4 named resources found publicly (see top of this file) |
| 2 Dataset discovery & validation | ✅ | Official dataset used; 13 quality checks, all passed |
| 3 KPI calculations | ✅ | 9 required KPIs + extras; cross-checked 3 ways |
| 4 Segmentation | ✅ | 9 dimensions; confounding check by contract × payment |
| 5 Published BI dashboard | ✅ Google Sheets · 🟡 Power BI | Google Sheets dashboard published view-only (accepted platform). Power BI: full specification, DAX, Power Query, theme; needs Power BI Desktop on Windows if you want it too |
| 6 Interactivity (4 filters) | ✅ | Google Sheets slicers tested as a signed-out viewer; web filters tested on all 300 combinations; Power BI synced slicers specified |
| 7 Power BI implementation files | ✅ | `power_query.m`, `dax_measures.md`, `edvyro_theme.json`, `dashboard_guide.md` |
| 8 Web dashboard (Chart.js) | ✅ | `dashboard/` — 5 pages, 12 charts, 4 filters, table views, light/dark, phone layout |
| 9 Project folder structure | ✅ | Matches the requested layout, plus `tests/` and `analysis/outputs/` |
| 10 Testing & QA | ✅ | 26 pipeline checks + 3,467 web-dashboard checks + 20 Google Sheets checks + signed-out browser tests |
| 11 Final business report | ✅ | `documentation/final_report.md` and `.pdf` (11 sections) |
| 12 EdVyro submission | 🟡 | Dashboard link published and tested. Remaining: create the GitHub repository and submit (needs your accounts); see `submission_guide.md` |
