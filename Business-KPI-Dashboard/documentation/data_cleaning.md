# Data Cleaning Log

**Input:** `data/original_dataset.csv` — the official EdVyro file downloaded from <https://edvyro.in/datasets/customer_churn_sample.csv> on 19 November 2026.
SHA-256 `1d5048ca…7fabdce` (checked by `tests/test_pipeline.py` so any accidental edit is caught).

**Output:** `data/cleaned_dataset.csv` (15 rows × 24 columns) — produced by `analysis/data_analysis.py`. The same steps are repeated in Power BI by `powerbi/power_query.m`.

**Full machine log:** `analysis/outputs/data_quality_log.json`

---

## 1. What the raw file contains

| Column | Type (validated) | Values in the file |
|---|---|---|
| `CustomerID` | text | CUST-1001 … CUST-1015, all match pattern `CUST-####` |
| `Gender` | text | Female 8, Male 7 |
| `Age` | whole number | 23 – 60 |
| `TenureMonths` | whole number | 2 – 48 |
| `SubscriptionType` | text | Basic 7, Pro 4, Enterprise 4 |
| `MonthlyCharges` | decimal (₹) | 49.99 (Basic), 79.99 (Pro), 149.99 (Enterprise) |
| `TotalCharges` | decimal (₹) | 99.98 – 7,199.52 |
| `ContractType` | text | Month-to-Month 7, One Year 4, Two Year 4 |
| `SupportTickets` | whole number | 0 – 6 (EdVyro guide: count in the previous 90 days) |
| `PaymentMethod` | text | Credit Card 6, UPI 4, Bank Transfer 3, Debit Card 2 |
| `Churn` | text | No 8, Yes 7 |

15 rows, 11 columns — matches the expected structure.

> **Field-name note.** The EdVyro *Customer Churn Analysis Guide* describes fields named `customer_id`, `tenure_months`, `monthly_charge`, `support_tickets`, `contract_type` (Monthly / quarterly / annual) and `churned`. The CSV actually supplied uses different names and contract labels (see table above). This project follows the CSV exactly as supplied and uses the guide only for meanings (e.g. charges are fictional INR; tickets cover 90 days).

## 2. Quality checks and results

| Check | Rule | Result | Rows affected |
|---|---|---|---|
| Missing values | empty or NA cell in any column | none found | 0 |
| Blank / whitespace-only text | stripped value is "" | none found | 0 |
| Leading / trailing spaces | value ≠ trimmed value | none found | 0 |
| Duplicate rows | identical rows | none found | 0 |
| Duplicate customer IDs | `CustomerID` repeated | none found | 0 |
| ID format | matches `CUST-` + 4 digits | all valid | 0 |
| Numeric parsing | every numeric column converts without error | all valid | 0 |
| Whole numbers | Age, TenureMonths, SupportTickets have no decimals | all valid | 0 |
| Allowed categories | each text column only uses known values | all valid | 0 |
| Plausible ranges | Age 18–100, tenure 0–120, tickets 0–100, charges > 0 | all valid | 0 |
| Revenue consistency | `TotalCharges` = `MonthlyCharges` × `TenureMonths` (± ₹0.01) | all 15 match exactly | 0 |
| Price consistency | each plan has exactly one monthly price | all valid | 0 |
| Statistical outliers | 1.5 × IQR rule on each numeric column | none flagged | 0 |

**Conclusion:** the supplied file is already clean. No row was removed, no value was changed, nothing was imputed and no outlier was capped. This is reported rather than hidden, as the EdVyro guide asks ("do not silently delete inconvenient rows").

### Outlier fences (1.5 × IQR)

| Column | Q1 | Q3 | Lower fence | Upper fence | Outliers |
|---|---|---|---|---|---|
| Age | 30 | 47 | 4.5 | 72.5 | 0 |
| TenureMonths | 7 | 27 | −23 | 57 | 0 |
| SupportTickets | 1 | 4 | −3.5 | 8.5 | 0 |
| MonthlyCharges | 49.99 | 114.99 | −47.51 | 212.49 | 0 |
| TotalCharges | 449.91 | 3,209.73 | −3,689.82 | 7,349.46 | 0 |

## 3. Cleaning actions taken

1. **Trimmed** spaces on every text field (defensive step; 0 cells changed).
2. **Set data types:** `Age`, `TenureMonths`, `SupportTickets` → integer; `MonthlyCharges`, `TotalCharges` → 2-decimal number.
3. **Added analysis columns** (original 11 columns are kept unchanged):

| New column | Rule | Why |
|---|---|---|
| `ChurnFlag` | 1 if `Churn = Yes`, else 0 | lets KPIs be summed |
| `ChurnStatus` | "Churned" / "Retained" | readable label for the Churn Status filter |
| `TenureGroup` (+ `TenureGroupOrder`) | 0-6, 7-12, 13-24, 25+ months | tenure filter and segmentation |
| `AgeGroup` (+ order) | 18-29, 30-44, 45+ | extra segmentation |
| `SupportTicketBand` (+ order) | Low (0-1), Medium (2-3), High (4+) | support-contact segmentation |
| `TotalChargesBand` (+ order) | Under 1000, 1000-2999, 3000+ | lifetime-value segmentation |
| `ContractOrder` | Month-to-Month 1, One Year 2, Two Year 3 | logical sort order in charts |
| `ExpectedTotalCharges`, `TotalChargesCheck` | MonthlyCharges × TenureMonths, OK / Mismatch | evidence for the consistency check |

**Why these tenure bands?** They follow common subscription milestones (first 6 months, first year, second year, beyond) and each band contains at least 2 customers. Band edges are inclusive: a customer with exactly 12 months is in 7-12.

## 4. Validation after cleaning (all passed)

- Row count unchanged (15 → 15).
- Customer IDs unique.
- No missing values in any of the 24 columns.
- Categories valid; numeric ranges valid.
- Every `TotalChargesCheck` = OK.
- One price per subscription plan.
- `ChurnFlag` agrees with `Churn` on every row.
- Every row received a tenure group.

## 5. Summary statistics (cleaned data)

| Column | Mean | Median | Std dev | Min | Max |
|---|---|---|---|---|---|
| Age | 39.07 | 38 | 11.39 | 23 | 60 |
| TenureMonths | 18.80 | 15 | 14.33 | 2 | 48 |
| SupportTickets | 2.53 | 2 | 1.92 | 0 | 6 |
| MonthlyCharges (₹) | 84.66 | 79.99 | 42.74 | 49.99 | 149.99 |
| TotalCharges (₹) | 2,088.48 | 1,099.78 | 2,407.37 | 99.98 | 7,199.52 |

**Mean by churn status**

| Column | Churned (7) | Retained (8) |
|---|---|---|
| Age | 30.43 | 46.62 |
| TenureMonths | 7.00 | 29.12 |
| SupportTickets | 4.29 | 1.00 |
| MonthlyCharges (₹) | 58.56 | 107.49 |
| TotalCharges (₹) | 444.22 | 3,527.21 |

`TotalCharges` is right-skewed (skew 1.21): a few long-tenure Enterprise customers have much higher lifetime charges, which is why its median (₹1,099.78) is far below its mean.
