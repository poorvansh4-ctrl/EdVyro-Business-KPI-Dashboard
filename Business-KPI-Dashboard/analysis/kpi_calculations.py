"""
EdVyro Data Analytics - Task 2: Business KPI Dashboard
Step 2 of the pipeline: KPI calculations, segmentation and validation.

Input : data/cleaned_dataset.csv  (created by analysis/data_analysis.py)
Output: analysis/outputs/kpi_results.json          - headline KPIs, segment tables, findings
        analysis/outputs/segment_summary.csv       - every segment table in one long table
        analysis/outputs/filter_expectations.json  - KPIs for every dashboard filter combination
        dashboard/data.js                          - cleaned rows for the web dashboard

Run from the project root (after data_analysis.py):
    python analysis/kpi_calculations.py

KPI definitions (dataset scope = all 15 customers in the supplied observation period):
    Total Customers        = count of distinct CustomerID
    Churned Customers      = customers with Churn = "Yes"
    Active Customers       = customers with Churn = "No"
    Churn Rate %           = Churned / Total x 100
    Retention Rate %       = Active / Total x 100
    Monthly Revenue (MRR)  = sum of MonthlyCharges for all customers
    Lifetime Revenue       = sum of TotalCharges for all customers
    Revenue at Risk        = sum of MonthlyCharges for churned customers
                             (monthly recurring revenue attached to customers who left)
    Revenue at Risk %      = Revenue at Risk / MRR x 100
    Average Tenure         = mean of TenureMonths
    ARPU                   = MRR / Total Customers
"""

import csv
import itertools
import json
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CLEAN_PATH = ROOT / "data" / "cleaned_dataset.csv"
RAW_PATH = ROOT / "data" / "original_dataset.csv"
OUT_DIR = ROOT / "analysis" / "outputs"
DATA_JS_PATH = ROOT / "dashboard" / "data.js"

# Dimension -> column used to sort its segments in a business-friendly order.
DIMENSIONS = {
    "ContractType": "ContractOrder",
    "TenureGroup": "TenureGroupOrder",
    "PaymentMethod": None,
    "SubscriptionType": "MonthlyCharges",
    "SupportTicketBand": "SupportTicketBandOrder",
    "AgeGroup": "AgeGroupOrder",
    "TotalChargesBand": "TotalChargesBandOrder",
    "Gender": None,
    "ChurnStatus": None,
}
# The four dashboard filters required by the EdVyro checklist (+ churn status).
FILTER_COLUMNS = ["ContractType", "TenureGroup", "PaymentMethod", "ChurnStatus"]
DASHBOARD_FIELDS = [
    "CustomerID", "Gender", "Age", "AgeGroup", "TenureMonths", "TenureGroup", "TenureGroupOrder",
    "SubscriptionType", "MonthlyCharges", "TotalCharges", "TotalChargesBand", "TotalChargesBandOrder",
    "ContractType", "ContractOrder", "SupportTickets", "SupportTicketBand", "SupportTicketBandOrder",
    "PaymentMethod", "Churn", "ChurnFlag", "ChurnStatus",
]


def pct(part, whole):
    return None if whole == 0 else part / whole * 100


def compute_kpis(df: pd.DataFrame) -> dict:
    total = int(df["CustomerID"].nunique())
    churned = int(df["ChurnFlag"].sum())
    active = total - churned
    mrr = float(df["MonthlyCharges"].sum())
    at_risk = float(df.loc[df["ChurnFlag"] == 1, "MonthlyCharges"].sum())
    return {
        "total_customers": total,
        "churned_customers": churned,
        "active_customers": active,
        "churn_rate_pct": pct(churned, total),
        "retention_rate_pct": pct(active, total),
        "monthly_revenue": mrr,
        "retained_monthly_revenue": mrr - at_risk,
        "lifetime_revenue": float(df["TotalCharges"].sum()),
        "revenue_at_risk": at_risk,
        "revenue_at_risk_pct": pct(at_risk, mrr),
        "annualised_revenue_at_risk": at_risk * 12,
        "avg_tenure_months": float(df["TenureMonths"].mean()) if total else None,
        "avg_tenure_churned": float(df.loc[df["ChurnFlag"] == 1, "TenureMonths"].mean()) if churned else None,
        "avg_tenure_active": float(df.loc[df["ChurnFlag"] == 0, "TenureMonths"].mean()) if active else None,
        "arpu": mrr / total if total else None,
        "avg_monthly_charge_churned": float(df.loc[df["ChurnFlag"] == 1, "MonthlyCharges"].mean()) if churned else None,
        "avg_monthly_charge_active": float(df.loc[df["ChurnFlag"] == 0, "MonthlyCharges"].mean()) if active else None,
        "avg_support_tickets": float(df["SupportTickets"].mean()) if total else None,
    }


def segment_table(df: pd.DataFrame, dimension: str, order_col) -> pd.DataFrame:
    total_at_risk = df.loc[df["ChurnFlag"] == 1, "MonthlyCharges"].sum()
    total_mrr = df["MonthlyCharges"].sum()
    rows = []
    for segment, g in df.groupby(dimension, sort=False):
        k = compute_kpis(g)
        rows.append({
            "Dimension": dimension,
            "Segment": segment,
            "SortKey": g[order_col].iloc[0] if order_col else segment,
            "Customers": k["total_customers"],
            "Churned": k["churned_customers"],
            "Active": k["active_customers"],
            "ChurnRatePct": k["churn_rate_pct"],
            "RetentionRatePct": k["retention_rate_pct"],
            "MonthlyRevenue": k["monthly_revenue"],
            "ShareOfMonthlyRevenuePct": pct(k["monthly_revenue"], total_mrr),
            "RevenueAtRisk": k["revenue_at_risk"],
            "ShareOfRevenueAtRiskPct": pct(k["revenue_at_risk"], total_at_risk),
            "LifetimeRevenue": k["lifetime_revenue"],
            "AvgTenureMonths": k["avg_tenure_months"],
            "ARPU": k["arpu"],
            "AvgSupportTickets": k["avg_support_tickets"],
        })
    table = pd.DataFrame(rows)
    if order_col is None:  # unordered categories: largest churn rate first, then size
        table = table.sort_values(["ChurnRatePct", "Customers"], ascending=[False, False])
    else:
        table = table.sort_values("SortKey")
    return table.drop(columns="SortKey").reset_index(drop=True)


def ties(table: pd.DataFrame, column: str, largest=True) -> dict:
    target = table[column].max() if largest else table[column].min()
    winners = table[table[column] == target]
    return {"segments": winners["Segment"].tolist(), "value": float(target),
            "customers": int(winners["Customers"].sum())}


def findings(df: pd.DataFrame, tables: dict) -> dict:
    out = {}
    for dim in ["ContractType", "TenureGroup", "PaymentMethod", "SubscriptionType", "SupportTicketBand", "AgeGroup"]:
        t = tables[dim]
        out[dim] = {
            "highest_churn": ties(t, "ChurnRatePct", largest=True),
            "best_retention": ties(t, "RetentionRatePct", largest=True),
            "largest_revenue_at_risk": ties(t, "RevenueAtRisk", largest=True),
        }
    # Is the payment-method pattern explained by contract mix? Churn rate per contract x payment cell.
    cross = (df.groupby(["ContractType", "PaymentMethod"])
               .agg(Customers=("CustomerID", "count"), Churned=("ChurnFlag", "sum"))
               .reset_index())
    cross["ChurnRatePct"] = cross["Churned"] / cross["Customers"] * 100
    out["contract_x_payment"] = cross.to_dict(orient="records")
    # Churners vs active customers on observed attributes (descriptive only).
    out["churned_profile"] = {
        "support_tickets_range": [int(df.loc[df.ChurnFlag == 1, "SupportTickets"].min()),
                                  int(df.loc[df.ChurnFlag == 1, "SupportTickets"].max())],
        "active_support_tickets_range": [int(df.loc[df.ChurnFlag == 0, "SupportTickets"].min()),
                                         int(df.loc[df.ChurnFlag == 0, "SupportTickets"].max())],
        "tenure_range": [int(df.loc[df.ChurnFlag == 1, "TenureMonths"].min()),
                         int(df.loc[df.ChurnFlag == 1, "TenureMonths"].max())],
        "active_tenure_range": [int(df.loc[df.ChurnFlag == 0, "TenureMonths"].min()),
                                int(df.loc[df.ChurnFlag == 0, "TenureMonths"].max())],
        "contracts": sorted(df.loc[df.ChurnFlag == 1, "ContractType"].unique().tolist()),
    }
    # Active customers with the most support contact - a descriptive watch list, not a prediction.
    active = df[df.ChurnFlag == 0]
    watch = active[active["SupportTickets"] == active["SupportTickets"].max()]
    out["active_watch_list"] = watch[["CustomerID", "ContractType", "TenureMonths", "SupportTickets",
                                      "SubscriptionType", "PaymentMethod", "MonthlyCharges"]].to_dict(orient="records")
    return out


def independent_check(kpis: dict) -> dict:
    """Recompute the core KPIs from the ORIGINAL file with the csv module only (no pandas, no cleaning code)."""
    with RAW_PATH.open(newline="") as f:
        rows = list(csv.DictReader(f))
    total = len({r["CustomerID"].strip() for r in rows})
    churned = sum(1 for r in rows if r["Churn"].strip() == "Yes")
    mrr = sum(float(r["MonthlyCharges"]) for r in rows)
    at_risk = sum(float(r["MonthlyCharges"]) for r in rows if r["Churn"].strip() == "Yes")
    manual = {
        "total_customers": total,
        "churned_customers": churned,
        "active_customers": total - churned,
        "churn_rate_pct": churned / total * 100,
        "retention_rate_pct": (total - churned) / total * 100,
        "monthly_revenue": mrr,
        "lifetime_revenue": sum(float(r["TotalCharges"]) for r in rows),
        "revenue_at_risk": at_risk,
        "revenue_at_risk_pct": at_risk / mrr * 100,
        "avg_tenure_months": sum(int(r["TenureMonths"]) for r in rows) / total,
        "arpu": mrr / total,
    }
    result = {}
    for key, value in manual.items():
        match = abs(value - kpis[key]) < 1e-9
        result[key] = {"pandas": kpis[key], "manual": value, "match": match}
    assert all(v["match"] for v in result.values()), f"KPI cross-check failed: {result}"
    return result


def filter_expectations(df: pd.DataFrame) -> list:
    """KPIs for every combination of the dashboard filters (used by tests/test_dashboard.mjs)."""
    options = {c: ["All"] + sorted(df[c].unique().tolist()) for c in FILTER_COLUMNS}
    cases = []
    for combo in itertools.product(*options.values()):
        selection = dict(zip(FILTER_COLUMNS, combo))
        mask = pd.Series(True, index=df.index)
        for col, val in selection.items():
            if val != "All":
                mask &= df[col] == val
        k = compute_kpis(df[mask])
        cases.append({"filters": selection, "kpis": {key: k[key] for key in [
            "total_customers", "churned_customers", "active_customers", "churn_rate_pct",
            "retention_rate_pct", "monthly_revenue", "revenue_at_risk", "revenue_at_risk_pct",
            "avg_tenure_months", "arpu", "lifetime_revenue"]}})
    return cases


def write_data_js(df: pd.DataFrame) -> None:
    records = df[DASHBOARD_FIELDS].to_dict(orient="records")
    payload = {
        "source": "EdVyro customer_churn_sample.csv (official Task-2 dataset), cleaned by analysis/data_analysis.py",
        "currency": "INR",
        "generated": date.today().isoformat(),
        "rows": records,
    }
    DATA_JS_PATH.write_text(
        "// Generated by analysis/kpi_calculations.py - do not edit by hand.\n"
        f"window.EDVYRO_DATA = {json.dumps(payload, indent=1)};\n"
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(CLEAN_PATH)

    kpis = compute_kpis(df)
    cross_check = independent_check(kpis)
    tables = {dim: segment_table(df, dim, order) for dim, order in DIMENSIONS.items()}
    result = {
        "dataset": {"file": CLEAN_PATH.name, "rows": int(len(df)), "currency": "INR (per EdVyro data guide)"},
        "kpis": kpis,
        "independent_cross_check": cross_check,
        "segments": {dim: t.to_dict(orient="records") for dim, t in tables.items()},
        "findings": findings(df, tables),
    }
    (OUT_DIR / "kpi_results.json").write_text(json.dumps(result, indent=2))
    pd.concat(tables.values()).round(2).to_csv(OUT_DIR / "segment_summary.csv", index=False)
    cases = filter_expectations(df)
    (OUT_DIR / "filter_expectations.json").write_text(json.dumps(cases, indent=1))
    write_data_js(df)

    print("HEADLINE KPIs")
    print(f"  Total customers ........ {kpis['total_customers']}")
    print(f"  Churned / Active ....... {kpis['churned_customers']} / {kpis['active_customers']}")
    print(f"  Churn rate ............. {kpis['churn_rate_pct']:.2f}%")
    print(f"  Retention rate ......... {kpis['retention_rate_pct']:.2f}%")
    print(f"  Monthly revenue (MRR) .. {kpis['monthly_revenue']:,.2f}")
    print(f"  Lifetime revenue ....... {kpis['lifetime_revenue']:,.2f}")
    print(f"  Revenue at risk ........ {kpis['revenue_at_risk']:,.2f} ({kpis['revenue_at_risk_pct']:.2f}% of MRR)")
    print(f"  Avg tenure (all/churned/active) {kpis['avg_tenure_months']:.2f} / "
          f"{kpis['avg_tenure_churned']:.2f} / {kpis['avg_tenure_active']:.2f} months")
    print(f"  ARPU ................... {kpis['arpu']:,.2f}")
    print(f"Independent csv-module cross-check: {sum(v['match'] for v in cross_check.values())}/{len(cross_check)} KPIs match")
    cols = ["Segment", "Customers", "Churned", "ChurnRatePct", "MonthlyRevenue", "RevenueAtRisk",
            "ShareOfRevenueAtRiskPct", "AvgTenureMonths"]
    for dim, t in tables.items():
        if dim == "ChurnStatus":
            continue
        print(f"\n{dim}\n{t[cols].round(2).to_string(index=False)}")
    print(f"\nFilter combinations written: {len(cases)} -> analysis/outputs/filter_expectations.json")
    print(f"Dashboard data written: {DATA_JS_PATH.relative_to(ROOT)} ({len(df)} rows)")


if __name__ == "__main__":
    main()
