"""
EdVyro Data Analytics - Task 2: Business KPI Dashboard
Step 1 of the pipeline: data inspection, data-quality checks and cleaning.

Input : data/original_dataset.csv   (official EdVyro customer_churn_sample.csv, never modified)
Output: data/cleaned_dataset.csv
        analysis/outputs/data_quality_log.json

Run from the project root:
    python analysis/data_analysis.py
"""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "data" / "original_dataset.csv"
CLEAN_PATH = ROOT / "data" / "cleaned_dataset.csv"
OUT_DIR = ROOT / "analysis" / "outputs"

EXPECTED_COLUMNS = [
    "CustomerID", "Gender", "Age", "TenureMonths", "SubscriptionType",
    "MonthlyCharges", "TotalCharges", "ContractType", "SupportTickets",
    "PaymentMethod", "Churn",
]
TEXT_COLUMNS = ["CustomerID", "Gender", "SubscriptionType", "ContractType", "PaymentMethod", "Churn"]
INT_COLUMNS = ["Age", "TenureMonths", "SupportTickets"]
MONEY_COLUMNS = ["MonthlyCharges", "TotalCharges"]
NUMERIC_COLUMNS = INT_COLUMNS + MONEY_COLUMNS

# Allowed values for categorical fields (taken from the supplied file, checked below).
ALLOWED_VALUES = {
    "Gender": {"Female", "Male"},
    "SubscriptionType": {"Basic", "Pro", "Enterprise"},
    "ContractType": {"Month-to-Month", "One Year", "Two Year"},
    "PaymentMethod": {"Credit Card", "Debit Card", "Bank Transfer", "UPI"},
    "Churn": {"Yes", "No"},
}

# Plausibility ranges for numeric fields (business rules, not statistical outliers).
VALID_RANGES = {
    "Age": (18, 100),
    "TenureMonths": (0, 120),
    "SupportTickets": (0, 100),
    "MonthlyCharges": (0.01, 10_000),
    "TotalCharges": (0, 1_000_000),
}

# Derived segment definitions. Labels sort correctly when paired with the *Order column.
TENURE_BINS = [(0, 6, "0-6 months"), (7, 12, "7-12 months"), (13, 24, "13-24 months"), (25, 10_000, "25+ months")]
AGE_BINS = [(18, 29, "18-29"), (30, 44, "30-44"), (45, 200, "45+")]
TICKET_BINS = [(0, 1, "Low (0-1)"), (2, 3, "Medium (2-3)"), (4, 10_000, "High (4+)")]
TOTAL_CHARGE_BINS = [(0, 999.99, "Under 1000"), (1000, 2999.99, "1000-2999"), (3000, 10_000_000, "3000+")]
CONTRACT_ORDER = {"Month-to-Month": 1, "One Year": 2, "Two Year": 3}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assign_band(value, bins):
    """Return (label, order) for the first inclusive range that contains value."""
    for order, (low, high, label) in enumerate(bins, start=1):
        if low <= value <= high:
            return label, order
    return None, None


def iqr_outliers(series: pd.Series) -> dict:
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    flagged = series[(series < low) | (series > high)]
    return {
        "q1": round(float(q1), 2), "q3": round(float(q3), 2), "iqr": round(float(iqr), 2),
        "lower_fence": round(float(low), 2), "upper_fence": round(float(high), 2),
        "outlier_count": int(flagged.size), "outlier_values": [float(v) for v in flagged],
    }


def profile(raw: pd.DataFrame) -> dict:
    """Profile the raw file exactly as supplied (all columns read as text first)."""
    log = {"source_file": RAW_PATH.name, "source_sha256": sha256(RAW_PATH)}
    log["rows"], log["columns"] = int(raw.shape[0]), int(raw.shape[1])
    log["column_names"] = list(raw.columns)
    log["columns_match_expected"] = list(raw.columns) == EXPECTED_COLUMNS

    stripped = raw.apply(lambda s: s.str.strip())
    log["missing_values"] = {c: int(raw[c].isna().sum()) for c in raw.columns}
    log["blank_strings"] = {c: int((stripped[c] == "").sum()) for c in raw.columns}
    log["cells_with_extra_whitespace"] = {c: int((raw[c].notna() & (raw[c] != stripped[c])).sum()) for c in raw.columns}
    log["duplicate_rows"] = int(raw.duplicated().sum())
    log["duplicate_customer_ids"] = int(raw["CustomerID"].duplicated().sum())
    log["customer_id_pattern_ok"] = bool(stripped["CustomerID"].str.fullmatch(r"CUST-\d{4}").all())

    # Type validation: every numeric column must parse without coercion failures.
    type_checks = {}
    for c in NUMERIC_COLUMNS:
        parsed = pd.to_numeric(stripped[c], errors="coerce")
        type_checks[c] = {
            "unparseable_values": int(parsed.isna().sum() - raw[c].isna().sum()),
            "non_integer_values": int((parsed % 1 != 0).sum()) if c in INT_COLUMNS else None,
        }
    log["type_checks"] = type_checks

    log["unexpected_category_values"] = {
        c: sorted(set(stripped[c].dropna()) - allowed) for c, allowed in ALLOWED_VALUES.items()
    }
    log["category_counts"] = {c: stripped[c].value_counts().to_dict() for c in ALLOWED_VALUES}
    return log


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.apply(lambda s: s.str.strip())
    for c in INT_COLUMNS:
        df[c] = pd.to_numeric(df[c]).astype("int64")
    for c in MONEY_COLUMNS:
        df[c] = pd.to_numeric(df[c]).astype("float64").round(2)

    # Derived analysis fields (original columns are kept unchanged).
    df["ChurnFlag"] = (df["Churn"] == "Yes").astype("int64")
    df["ChurnStatus"] = np.where(df["ChurnFlag"] == 1, "Churned", "Retained")
    df["TenureGroup"], df["TenureGroupOrder"] = zip(*df["TenureMonths"].map(lambda v: assign_band(v, TENURE_BINS)))
    df["AgeGroup"], df["AgeGroupOrder"] = zip(*df["Age"].map(lambda v: assign_band(v, AGE_BINS)))
    df["SupportTicketBand"], df["SupportTicketBandOrder"] = zip(*df["SupportTickets"].map(lambda v: assign_band(v, TICKET_BINS)))
    df["TotalChargesBand"], df["TotalChargesBandOrder"] = zip(*df["TotalCharges"].map(lambda v: assign_band(v, TOTAL_CHARGE_BINS)))
    df["ContractOrder"] = df["ContractType"].map(CONTRACT_ORDER).astype("int64")
    df["ExpectedTotalCharges"] = (df["MonthlyCharges"] * df["TenureMonths"]).round(2)
    df["TotalChargesCheck"] = np.where((df["TotalCharges"] - df["ExpectedTotalCharges"]).abs() <= 0.01, "OK", "Mismatch")
    return df


def validate(raw: pd.DataFrame, df: pd.DataFrame) -> dict:
    """Rule checks on the cleaned data. Every check must be True for the run to pass."""
    range_violations = {
        c: int(((df[c] < low) | (df[c] > high)).sum()) for c, (low, high) in VALID_RANGES.items()
    }
    price_per_plan = df.groupby("SubscriptionType")["MonthlyCharges"].nunique().to_dict()
    checks = {
        "row_count_unchanged": len(df) == len(raw),
        "customer_ids_unique": df["CustomerID"].is_unique,
        "no_missing_values": int(df.isna().sum().sum()) == 0,
        "categories_valid": all(set(df[c]) <= allowed for c, allowed in ALLOWED_VALUES.items()),
        "numeric_ranges_valid": sum(range_violations.values()) == 0,
        "total_charges_equal_monthly_x_tenure": bool((df["TotalChargesCheck"] == "OK").all()),
        "one_price_per_subscription_type": all(v == 1 for v in price_per_plan.values()),
        "churn_flag_matches_churn": bool(((df["Churn"] == "Yes") == (df["ChurnFlag"] == 1)).all()),
        "every_row_has_tenure_group": bool(df["TenureGroup"].notna().all()),
    }
    return {
        "checks": checks,
        "all_checks_passed": all(checks.values()),
        "range_violations": range_violations,
        "monthly_price_by_subscription_type": df.groupby("SubscriptionType")["MonthlyCharges"].first().to_dict(),
        "total_charges_mismatches": int((df["TotalChargesCheck"] != "OK").sum()),
    }


def summarise(df: pd.DataFrame) -> dict:
    numeric = df[NUMERIC_COLUMNS].describe().T.round(2)
    stats = {c: numeric.loc[c].to_dict() for c in NUMERIC_COLUMNS}
    for c in NUMERIC_COLUMNS:
        stats[c]["median"] = round(float(df[c].median()), 2)
        stats[c]["skew"] = round(float(df[c].skew()), 3)
    by_churn = df.groupby("Churn")[NUMERIC_COLUMNS].mean().round(2)
    return {
        "numeric_summary": stats,
        "iqr_outliers": {c: iqr_outliers(df[c]) for c in NUMERIC_COLUMNS},
        "mean_by_churn": {c: by_churn[c].to_dict() for c in NUMERIC_COLUMNS},
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(RAW_PATH, dtype=str, keep_default_na=False, na_values=[""])

    log = {"profile": profile(raw)}
    df = clean(raw)
    log["validation"] = validate(raw, df)
    log["statistics"] = summarise(df)
    log["cleaning_actions"] = [
        "Trimmed leading/trailing whitespace on every text field (cells affected listed in profile).",
        "Cast Age, TenureMonths, SupportTickets to integer; MonthlyCharges, TotalCharges to 2-dp decimal.",
        "Added ChurnFlag (1 = Yes, 0 = No) and ChurnStatus (Churned / Retained).",
        "Added TenureGroup, AgeGroup, SupportTicketBand, TotalChargesBand (+ sort-order columns).",
        "Added ContractOrder so contract types sort Month-to-Month > One Year > Two Year.",
        "Added ExpectedTotalCharges and TotalChargesCheck (MonthlyCharges x TenureMonths, tolerance 0.01).",
        "No rows removed, no values imputed, no outliers capped.",
    ]
    log["cleaned_rows"], log["cleaned_columns"] = int(df.shape[0]), int(df.shape[1])

    df.to_csv(CLEAN_PATH, index=False, float_format="%.2f")
    (OUT_DIR / "data_quality_log.json").write_text(json.dumps(log, indent=2, default=str))
    assert sha256(RAW_PATH) == log["profile"]["source_sha256"], "original dataset changed during run"

    p, v = log["profile"], log["validation"]
    print(f"Original: {p['rows']} rows x {p['columns']} columns | columns as expected: {p['columns_match_expected']}")
    print(f"Missing cells: {sum(p['missing_values'].values())} | blank strings: {sum(p['blank_strings'].values())} | "
          f"whitespace cells: {sum(p['cells_with_extra_whitespace'].values())}")
    print(f"Duplicate rows: {p['duplicate_rows']} | duplicate CustomerIDs: {p['duplicate_customer_ids']} | "
          f"ID pattern OK: {p['customer_id_pattern_ok']}")
    print(f"Unexpected category values: {p['unexpected_category_values']}")
    print("IQR outliers:", {c: o["outlier_count"] for c, o in log["statistics"]["iqr_outliers"].items()})
    for name, ok in v["checks"].items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print(f"Cleaned: {df.shape[0]} rows x {df.shape[1]} columns -> {CLEAN_PATH.relative_to(ROOT)}")
    if not v["all_checks_passed"]:
        raise SystemExit("Validation failed - see analysis/outputs/data_quality_log.json")


if __name__ == "__main__":
    main()
