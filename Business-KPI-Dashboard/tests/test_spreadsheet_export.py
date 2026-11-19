"""
Checks the Google Sheets dashboard against the verified Python results, using two
downloads of the unfiltered Google Sheet:
  spreadsheet/Customer_Churn_KPI_Dashboard.xlsx  (File > Download > Microsoft Excel)
  spreadsheet/dashboard_tab_export.csv           (Dashboard tab, File > Download > CSV)
It compares:
  1. every KPI on the KPI Check tab with analysis/outputs/kpi_results.json
  2. every cell of the five segment tables on the Dashboard tab with
     analysis/outputs/segment_summary.csv (the .xlsx keeps pivot tables as definitions
     without values, so their displayed values are read from the CSV download)
  3. the 15 customer rows with data/original_dataset.csv
Run from the project root:
    python tests/test_spreadsheet_export.py
Needs openpyxl (pip install openpyxl).
"""

import csv
import json
import warnings
from pathlib import Path

import openpyxl

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / "spreadsheet" / "Customer_Churn_KPI_Dashboard.xlsx"
DASHBOARD_CSV = ROOT / "spreadsheet" / "dashboard_tab_export.csv"

KPI_ROWS = {  # KPI Check row -> key in kpi_results.json (rates stored as fractions in the sheet)
    5: ("total_customers", 1), 6: ("churned_customers", 1), 7: ("active_customers", 1),
    8: ("churn_rate_pct", 100), 9: ("retention_rate_pct", 100), 10: ("monthly_revenue", 1),
    11: ("revenue_at_risk", 1), 12: ("revenue_at_risk_pct", 100), 13: ("annualised_revenue_at_risk", 1),
    14: ("retained_monthly_revenue", 1), 15: ("lifetime_revenue", 1), 16: ("avg_tenure_months", 1),
    17: ("avg_tenure_churned", 1), 18: ("avg_tenure_active", 1), 19: ("arpu", 1),
    20: ("avg_monthly_charge_churned", 1), 21: ("avg_monthly_charge_active", 1),
}
# Segment-table header label in the Dashboard CSV -> segment dimension
PIVOTS = {"ContractType", "TenureGroup", "PaymentMethod", "SubscriptionType", "SupportTicketBand"}
# CSV column index -> (segment_summary.csv column, allowed difference from display rounding)
PIVOT_COLUMNS = {2: ("Customers", 0), 3: ("Churned", 0), 4: ("Active", 0), 5: ("ChurnRatePct", 0.05),
                 6: ("MonthlyRevenue", 0.005), 7: ("RevenueAtRisk", 0.005), 9: ("ARPU", 0.005), 10: ("AvgTenureMonths", 0.05)}


def number(text):
    return float(text.replace("₹", "").replace(",", "").replace("%", ""))

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def main():
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    kpis = json.loads((ROOT / "analysis" / "outputs" / "kpi_results.json").read_text())["kpis"]

    kc = wb["KPI Check"]
    for row, (key, scale) in KPI_ROWS.items():
        sheet_value = kc.cell(row=row, column=2).value * scale
        check(f"KPI Check: {kc.cell(row=row, column=1).value}", abs(sheet_value - kpis[key]) < 1e-6,
              f"sheet {sheet_value} vs python {kpis[key]}")

    segments = {(r["Dimension"], r["Segment"]): r for r in csv.DictReader(open(ROOT / "analysis" / "outputs" / "segment_summary.csv"))}
    with open(DASHBOARD_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    cells, seen, dim = 0, set(), None
    for r in rows:
        label = r[1] if len(r) > 1 else ""
        if label in PIVOTS:
            dim = label
            seen.add(dim)
            continue
        if not label or len(r) < 11 or not r[2]:  # any row without a customer count ends the table
            dim = None
            continue
        if dim:
            expected = segments[(dim, label)]
            for col, (key, tol) in PIVOT_COLUMNS.items():
                cells += 1
                if abs(number(r[col]) - float(expected[key])) > tol + 1e-9:
                    check(f"Dashboard {dim}={label} {key}", False, f"sheet {r[col]} vs python {expected[key]}")
    check("Dashboard has all five segment tables", seen == PIVOTS, f"found {sorted(seen)}")
    expected_cells = sum(1 for k in segments if k[0] in PIVOTS) * len(PIVOT_COLUMNS)
    check(f"Dashboard segment tables match Python ({cells} cells)",
          cells == expected_cells and all(ok for n, ok, _ in results if n.startswith("Dashboard ")),
          f"checked {cells} of {expected_cells} cells")

    with open(ROOT / "data" / "original_dataset.csv", newline="") as f:
        original = {r["CustomerID"]: r for r in csv.DictReader(f)}
    cust = wb["Customers"]
    headers = [c.value for c in cust[1]][:11]
    same = True
    for r in cust.iter_rows(min_row=2, max_row=16, values_only=True):
        source = original[r[0]]
        for h, v in zip(headers, r[:11]):
            same &= (abs(float(source[h]) - float(v)) < 1e-9) if isinstance(v, (int, float)) else (source[h] == v)
    check("Customers tab holds the 15 official rows unchanged", same and cust.max_row >= 16)

    width = max(len(n) for n, _, _ in results)
    for name, ok, detail in results:
        print(f"[{'PASS' if ok else 'FAIL'}] {name.ljust(width)} {'' if ok else detail}")
    failed = [n for n, ok, _ in results if not ok]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
