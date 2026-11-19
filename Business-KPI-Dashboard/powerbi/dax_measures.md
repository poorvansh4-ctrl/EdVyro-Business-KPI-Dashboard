# DAX Measures — EdVyro Business KPI Dashboard

All measures live in the table **`Customers`** (the query created from [`power_query.m`](power_query.m)).

**How to add a measure (Power BI Desktop):** in the **Data** pane, right-click `Customers` → **New measure** → paste one block → press Enter. Repeat for each block. Then set the format shown under **Format** (Measure tools ribbon → Format).

> Tip: create an empty table for measures first (Home → Enter data → name it `_Measures` → Load), then right-click it → New measure. Measures will be grouped at the top of the Data pane. If you do this, every measure still refers to `Customers[...]` columns exactly as written below.

---

## 1. Customer counts

```DAX
Total Customers =
DISTINCTCOUNT ( Customers[CustomerID] )
```
Format: Whole number.

```DAX
Churned Customers =
VAR _total = [Total Customers]
VAR _churned =
    CALCULATE ( [Total Customers], KEEPFILTERS ( Customers[Churn] = "Yes" ) )
RETURN
    IF ( NOT ISBLANK ( _total ), _churned + 0 )
```
Format: Whole number.

```DAX
Active Customers =
VAR _total = [Total Customers]
VAR _active =
    CALCULATE ( [Total Customers], KEEPFILTERS ( Customers[Churn] = "No" ) )
RETURN
    IF ( NOT ISBLANK ( _total ), _active + 0 )
```
Format: Whole number.

**Why this pattern?** `KEEPFILTERS` makes the measure respect every slicer (including the Churn Status slicer). The `+ 0` shows **0** instead of *(Blank)* when a segment has customers but none churned — so *One Year* shows a churn rate of 0 %, not blank. The `IF (NOT ISBLANK …)` keeps segments with *no* customers hidden.

---

## 2. Rates

```DAX
Churn Rate % =
DIVIDE ( [Churned Customers], [Total Customers] )
```

```DAX
Retention Rate % =
DIVIDE ( [Active Customers], [Total Customers] )
```
Format: Percentage, 1 decimal place. `DIVIDE` returns blank instead of an error when the denominator is 0.

---

## 3. Revenue

```DAX
Monthly Revenue (MRR) =
SUM ( Customers[MonthlyCharges] )
```

```DAX
Lifetime Revenue =
SUM ( Customers[TotalCharges] )
```

```DAX
Revenue at Risk =
VAR _mrr = [Monthly Revenue (MRR)]
VAR _risk =
    CALCULATE ( [Monthly Revenue (MRR)], KEEPFILTERS ( Customers[Churn] = "Yes" ) )
RETURN
    IF ( NOT ISBLANK ( _mrr ), _risk + 0 )
```

```DAX
Revenue at Risk % =
DIVIDE ( [Revenue at Risk], [Monthly Revenue (MRR)] )
```

```DAX
Retained MRR =
[Monthly Revenue (MRR)] - [Revenue at Risk]
```

```DAX
Annualised Revenue at Risk =
[Revenue at Risk] * 12
```

```DAX
Share of Revenue at Risk % =
DIVIDE (
    [Revenue at Risk],
    CALCULATE ( [Revenue at Risk], ALLSELECTED ( Customers ) )
)
```

```DAX
ARPU =
DIVIDE ( [Monthly Revenue (MRR)], [Total Customers] )
```

```DAX
Avg Monthly Charge - Churned =
CALCULATE ( AVERAGE ( Customers[MonthlyCharges] ), KEEPFILTERS ( Customers[Churn] = "Yes" ) )
```

```DAX
Avg Monthly Charge - Active =
CALCULATE ( AVERAGE ( Customers[MonthlyCharges] ), KEEPFILTERS ( Customers[Churn] = "No" ) )
```
Format for all money measures: Currency → **₹ English (India)**, 2 decimal places. Percent measures: Percentage, 1 decimal.

**Revenue at Risk definition.** The dataset has no dates or future contract values, so "risk" is measured with the only recurring-revenue field available: the `MonthlyCharges` of customers whose `Churn = "Yes"`. It is the monthly recurring revenue tied to customers who left during the observation period — the amount the business loses each month unless those customers are won back. *Annualised Revenue at Risk* (× 12) is a simple projection that assumes no win-back and unchanged prices; label it as an estimate.

---

## 4. Tenure and engagement

```DAX
Average Tenure (Months) =
AVERAGE ( Customers[TenureMonths] )
```

```DAX
Avg Tenure - Churned =
CALCULATE ( AVERAGE ( Customers[TenureMonths] ), KEEPFILTERS ( Customers[Churn] = "Yes" ) )
```

```DAX
Avg Tenure - Active =
CALCULATE ( AVERAGE ( Customers[TenureMonths] ), KEEPFILTERS ( Customers[Churn] = "No" ) )
```

```DAX
Avg Support Tickets =
AVERAGE ( Customers[SupportTickets] )
```
Format: Decimal number, 1 decimal place.

---

## 5. Dynamic text (for the overview and insight text boxes)

```DAX
Customer Health Summary =
IF (
    ISBLANK ( [Total Customers] ),
    "No customers match the current filters.",
    "Of " & FORMAT ( [Total Customers], "0" ) & " customers in view, "
        & FORMAT ( [Churned Customers], "0" ) & " churned ("
        & FORMAT ( [Churn Rate %], "0.0%" ) & ") and "
        & FORMAT ( [Active Customers], "0" ) & " are active. Revenue at risk is ₹"
        & FORMAT ( [Revenue at Risk], "#,0.00" ) & " per month ("
        & FORMAT ( [Revenue at Risk %], "0.0%" ) & " of monthly revenue)."
)
```
Use it in a **Card (new)** or **Multi-row card** visual so the sentence updates with the slicers.

---

## 6. Check measures (for testing — hide them from report view)

```DAX
Check - Churned via Flag =
SUM ( Customers[ChurnFlag] )
```
Must always equal `[Churned Customers]`.

```DAX
Check - Rates Total =
[Churn Rate %] + [Retention Rate %]
```
Must always be 100 % (when any customer is in view).

```DAX
Check - Revenue Split =
[Retained MRR] + [Revenue at Risk] - [Monthly Revenue (MRR)]
```
Must always be 0.

---

## 7. Expected results — compare your cards with these

These numbers come from [`analysis/kpi_calculations.py`](../analysis/kpi_calculations.py) and were cross-checked by a second, pandas-free calculation on the original CSV.

**No filters applied**

| Measure | Expected value |
|---|---|
| Total Customers | 15 |
| Churned Customers | 7 |
| Active Customers | 8 |
| Churn Rate % | 46.7 % |
| Retention Rate % | 53.3 % |
| Monthly Revenue (MRR) | ₹1,269.85 |
| Lifetime Revenue | ₹31,327.18 |
| Revenue at Risk | ₹409.93 |
| Revenue at Risk % | 32.3 % |
| Retained MRR | ₹859.92 |
| Annualised Revenue at Risk | ₹4,919.16 |
| ARPU | ₹84.66 |
| Average Tenure (Months) | 18.8 |
| Avg Tenure - Churned / Active | 7.0 / 29.1 |
| Avg Monthly Charge - Churned / Active | ₹58.56 / ₹107.49 |
| Avg Support Tickets | 2.5 |

**With one slicer applied** (spot checks)

| Slicer selection | Customers | Churned | Churn Rate | MRR | Revenue at Risk |
|---|---|---|---|---|---|
| Contract = Month-to-Month | 7 | 7 | 100.0 % | ₹409.93 | ₹409.93 |
| Contract = One Year | 4 | 0 | 0.0 % | ₹259.96 | ₹0.00 |
| Contract = Two Year | 4 | 0 | 0.0 % | ₹599.96 | ₹0.00 |
| Tenure = 0-6 months | 4 | 4 | 100.0 % | ₹199.96 | ₹199.96 |
| Tenure = 13-24 months | 5 | 1 | 20.0 % | ₹339.95 | ₹79.99 |
| Payment = UPI | 4 | 3 | 75.0 % | ₹199.96 | ₹149.97 |
| Payment = Credit Card | 6 | 2 | 33.3 % | ₹629.94 | ₹99.98 |
| Churn Status = Retained | 8 | 0 | 0.0 % | ₹859.92 | ₹0.00 |

All 300 slicer combinations are listed in [`analysis/outputs/filter_expectations.json`](../analysis/outputs/filter_expectations.json).
