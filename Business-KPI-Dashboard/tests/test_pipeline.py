"""
Quality checks for the data pipeline (Phase 10).
Run from the project root after the analysis scripts:
    python tests/test_pipeline.py
Exits with an error if any check fails.
"""

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# SHA-256 of the file downloaded from https://edvyro.in/datasets/customer_churn_sample.csv
OFFICIAL_SHA256 = "1d5048cad41e8abbefd5fab04cc7dd6579234a292a8f59f85d7d072f37fabdce"

# Values worked out by hand from the 15 rows (see documentation/methodology.md, section 5).
HAND_CALCULATED = {
    "total_customers": 15,
    "churned_customers": 7,
    "active_customers": 8,
    "churn_rate_pct": 7 / 15 * 100,
    "retention_rate_pct": 8 / 15 * 100,
    "monthly_revenue": 7 * 49.99 + 4 * 79.99 + 4 * 149.99,
    "revenue_at_risk": 5 * 49.99 + 2 * 79.99,
    "avg_tenure_months": 282 / 15,
}

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def main():
    raw = ROOT / "data" / "original_dataset.csv"
    clean = ROOT / "data" / "cleaned_dataset.csv"
    out = ROOT / "analysis" / "outputs"

    check("original dataset is the unmodified EdVyro file",
          hashlib.sha256(raw.read_bytes()).hexdigest() == OFFICIAL_SHA256)

    with raw.open(newline="") as f:
        raw_rows = list(csv.DictReader(f))
    with clean.open(newline="") as f:
        clean_rows = list(csv.DictReader(f))

    check("cleaned dataset keeps all 15 rows", len(clean_rows) == len(raw_rows) == 15, f"{len(clean_rows)} rows")
    check("cleaned dataset keeps every original column",
          set(raw_rows[0]) <= set(clean_rows[0]))
    check("original values unchanged in cleaned data",
          all(abs(float(r[c]) - float(c2[c])) < 1e-9 if c in ("MonthlyCharges", "TotalCharges", "Age", "TenureMonths", "SupportTickets")
              else r[c].strip() == c2[c]
              for r, c2 in zip(raw_rows, clean_rows) for c in raw_rows[0]))
    check("every TotalChargesCheck is OK", all(r["TotalChargesCheck"] == "OK" for r in clean_rows))
    check("ChurnFlag matches Churn", all((r["Churn"] == "Yes") == (r["ChurnFlag"] == "1") for r in clean_rows))

    log = json.loads((out / "data_quality_log.json").read_text())
    check("all data-quality validation checks passed", log["validation"]["all_checks_passed"])

    kpis = json.loads((out / "kpi_results.json").read_text())
    k = kpis["kpis"]
    for key, expected in HAND_CALCULATED.items():
        check(f"KPI {key} equals hand calculation", abs(k[key] - expected) < 1e-9, f"{k[key]} vs {expected}")
    check("independent csv-module cross-check matched",
          all(v["match"] for v in kpis["independent_cross_check"].values()))
    check("churn rate + retention rate = 100%", abs(k["churn_rate_pct"] + k["retention_rate_pct"] - 100) < 1e-9)
    check("retained revenue + revenue at risk = monthly revenue",
          abs(k["retained_monthly_revenue"] + k["revenue_at_risk"] - k["monthly_revenue"]) < 1e-9)

    for dim in ("ContractType", "TenureGroup", "PaymentMethod"):
        seg = kpis["segments"][dim]
        check(f"{dim} segments add up to 15 customers", sum(s["Customers"] for s in seg) == 15)
        check(f"{dim} revenue at risk adds up to total",
              abs(sum(s["RevenueAtRisk"] for s in seg) - k["revenue_at_risk"]) < 1e-9)

    expectations = json.loads((out / "filter_expectations.json").read_text())
    check("300 filter combinations generated", len(expectations) == 4 * 5 * 5 * 3, f"{len(expectations)}")

    data_js = (ROOT / "dashboard" / "data.js").read_text()
    payload = json.loads(data_js.split("window.EDVYRO_DATA = ", 1)[1].rstrip().rstrip(";"))
    check("dashboard data.js has the same 15 customers as cleaned data",
          [r["CustomerID"] for r in payload["rows"]] == [r["CustomerID"] for r in clean_rows])

    width = max(len(n) for n, _, _ in results)
    for name, ok, detail in results:
        print(f"[{'PASS' if ok else 'FAIL'}] {name.ljust(width)} {detail if not ok else ''}")
    failed = [n for n, ok, _ in results if not ok]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
