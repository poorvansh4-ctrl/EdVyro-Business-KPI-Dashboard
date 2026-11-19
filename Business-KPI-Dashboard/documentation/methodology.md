# Methodology

## 1. Sources

| Resource (as named in the EdVyro task) | Where it was found | Public? |
|---|---|---|
| Step-by-step task guide | <https://edvyro.in/datasets/task-kits/data-analytics-task-2> | Yes |
| Starter checklist | <https://edvyro.in/datasets/task-kits/data-analytics-task-2.md> | Yes |
| Customer churn data guide | "Customer Churn Analysis Guide", Analytics section of <https://edvyro.in/datasets/source-materials/task-source-library.html> | Yes |
| Customer churn dataset (CSV) | <https://edvyro.in/datasets/customer_churn_sample.csv> | Yes |
| Programme project guide (extra context) | <https://edvyro.in/guides/data-analytics-project-guide> | Yes |

All five were downloaded on 19 November 2026 without signing in. **The official dataset was used; no alternative dataset was needed.**

## 2. Pipeline

```
data/original_dataset.csv            (never edited)
   │  analysis/data_analysis.py      profile → validate → clean
   ▼
data/cleaned_dataset.csv  +  analysis/outputs/data_quality_log.json
   │  analysis/kpi_calculations.py   KPIs, segments, findings, cross-check
   ▼
analysis/outputs/kpi_results.json, segment_summary.csv, filter_expectations.json, dashboard/data.js
   │  analysis/report_charts.py      static charts for the report
   ▼
documentation/images/*.png
```

Checks: `tests/test_pipeline.py` (26 checks) and `tests/test_dashboard_metrics.js` (3,467 checks).

## 3. KPI definitions

Scope for every KPI: the customers currently in view (all 15 customers when no filter is applied), in the single observation period covered by the file. One row = one customer (IDs were verified unique).

| KPI | Formula | Unfiltered value |
|---|---|---|
| Total Customers | count of distinct `CustomerID` | 15 |
| Churned Customers | customers with `Churn = Yes` | 7 |
| Active Customers | customers with `Churn = No` | 8 |
| Churn Rate | Churned ÷ Total × 100 | 46.67 % |
| Retention Rate | Active ÷ Total × 100 | 53.33 % |
| Monthly Revenue (MRR) | Σ `MonthlyCharges` (all customers) | ₹1,269.85 |
| Lifetime Revenue | Σ `TotalCharges` (all customers) | ₹31,327.18 |
| **Revenue at Risk** | Σ `MonthlyCharges` where `Churn = Yes` | ₹409.93 |
| Revenue at Risk % | Revenue at Risk ÷ MRR × 100 | 32.28 % |
| Annualised Revenue at Risk (estimate) | Revenue at Risk × 12 | ₹4,919.16 |
| Average Tenure | mean `TenureMonths` | 18.8 months |
| ARPU | MRR ÷ Total Customers | ₹84.66 |

### Why Revenue at Risk is defined this way
The data has no dates, renewal values or predicted probabilities, so a forward-looking "probability × value" measure is not possible without inventing numbers. The only recurring-revenue field is `MonthlyCharges`. Revenue at Risk is therefore the **monthly recurring revenue attached to customers who churned during the observation period** — the amount lost each month unless those customers are won back. The ×12 annual figure is clearly labelled as an estimate that assumes no win-back and unchanged prices. `TotalCharges` is not used for risk because it is revenue already received.

### Why Churn Rate uses the whole dataset as the denominator
The file is a single snapshot with no time column, so a monthly churn rate cannot be calculated. The rate is "share of customers in this dataset who left during the observation period", as the EdVyro guide's definition of `churned` describes.

## 4. Segmentation method

Segments use existing columns or simple, documented bands (see `data_cleaning.md` §3): contract type, tenure group, payment method, plan, support-ticket band, age group, lifetime-charge band, gender, churn status. For each segment the same KPI formulas are applied to the customers in that segment. "Share of revenue at risk" = segment revenue at risk ÷ total revenue at risk in view.

**Confounding check.** Because churn might be explained by more than one column, churn rate was cross-tabulated by contract type × payment method and checked by plan within contract:

| Contract | Bank Transfer | Credit Card | Debit Card | UPI |
|---|---|---|---|---|
| Month-to-Month | – | 100 % (2) | 100 % (2) | 100 % (3) |
| One Year | 0 % (2) | 0 % (1) | – | 0 % (1) |
| Two Year | 0 % (1) | 0 % (3) | – | – |

Within each contract type churn does not vary by payment method. Likewise, Basic and Pro customers on One Year contracts all stayed, and all Enterprise customers are on Two Year contracts. Tenure also overlaps fully: every Month-to-Month customer has 2–14 months' tenure and every other customer 15–48. The report therefore treats contract, tenure, tickets, plan and payment method as overlapping descriptions of the same 7 churned customers, and makes no causal claim.

## 5. Validation

1. **Hand calculation** (in `tests/test_pipeline.py`):
   - Churned: CUST-1001, 1003, 1005, 1007, 1010, 1012, 1014 → 7; churn rate 7/15 = 46.67 %.
   - MRR = 7 × 49.99 + 4 × 79.99 + 4 × 149.99 = 349.93 + 319.96 + 599.96 = ₹1,269.85.
   - Revenue at risk = 5 Basic × 49.99 + 2 Pro × 79.99 = 249.95 + 159.98 = ₹409.93.
   - Average tenure = 282 ÷ 15 = 18.8 months.
2. **Independent recomputation**: `kpi_calculations.py` recalculates 11 KPIs from the *original* CSV with Python's `csv` module (no pandas, no cleaning code) and stops if any differ.
3. **Additivity checks**: segment customers sum to 15; segment revenue at risk sums to ₹409.93; churn + retention = 100 %; retained + at-risk revenue = MRR.
4. **Dashboard consistency**: `tests/test_dashboard_metrics.js` runs the web dashboard's own calculation code for all 300 combinations of the four filters (4 contract × 5 tenure × 5 payment × 3 status options, including "All") and compares 11 KPIs each with Python, plus every segment table — 3,467 checks, 0 differences.
5. **Browser test**: the web dashboard was opened in a browser; filters, tabs, table views, empty state (0 customers), light and dark mode and a 375 px phone width were checked with no console errors.
6. **Power BI**: `powerbi/dax_measures.md` §7 lists the values each card must show, with and without filters, so the Power BI build can be checked against the same numbers.
7. **Google Sheets dashboard**: the KPI Check tab recalculates 17 KPIs with sheet formulas and compares them with the Python values (17/17 Match). `tests/test_spreadsheet_export.py` re-checks those KPIs, all 136 segment-table cells and the 15 data rows from the downloaded sheet (20/20). The view-only link was opened signed out and a slicer was used as a viewer (Payment method = UPI); every card, chart and table showed the verified UPI values.

**Rounding.** Values are stored unrounded and rounded only for display (1 decimal for rates and tenure, 2 for money). Python's formatter rounds halves to even, so the active customers' average tenure of exactly 29.125 months appears as 29.12 in Python logs and 29.13 in Excel/Power BI; the dashboards show 29.1.

## 6. Tools

Google Sheets (formulas, pivot tables, slicers, charts) · Python 3 (pandas, numpy, matplotlib, openpyxl) · Node.js (tests) · HTML/CSS/JavaScript with Chart.js 4.4.1 · Power BI Desktop (build guide, DAX, Power Query M, theme).

## 7. Limitations

- 15 synthetic records: a single customer moves a segment's churn rate by 14–50 percentage points.
- No dates: no trend, cohort or time-to-churn analysis is possible.
- Overlapping attributes: effects of contract, tenure, tickets, plan and age cannot be separated.
- Descriptive only: no predictive model or causal inference was attempted (Task 3 of the EdVyro track covers risk scoring).
