# Business Insights — EdVyro Customer Churn (Task 2)

**Scope.** 15 synthetic customers from the official EdVyro file `customer_churn_sample.csv`, one observation period. Amounts are fictional INR (₹) per the EdVyro *Customer Churn Analysis Guide*. Every number below is produced by [`kpi_calculations.py`](kpi_calculations.py) and stored in [`outputs/kpi_results.json`](outputs/kpi_results.json).

**Decision question (from the EdVyro data guide):** *Which customer groups should a fictional subscription team contact first to reduce avoidable churn?*

> **Read this first — the most important caveat.** In this sample the risk traits overlap almost completely. The 7 churned customers are exactly the 7 Month-to-Month customers, and they are also the customers with tenure of 2–14 months and 3–6 support tickets. With 15 records it is **not possible to say which trait matters most**, and none of these findings proves cause. They describe who left, not why.

---

## 1. Headline KPIs

| KPI | Value |
|---|---|
| Total customers | 15 |
| Churned / Active | 7 / 8 |
| Churn rate | **46.7 %** |
| Retention rate | **53.3 %** |
| Monthly revenue (MRR) | ₹1,269.85 |
| Revenue at risk (monthly) | **₹409.93** = 32.3 % of MRR |
| Annualised revenue at risk (estimate, × 12) | ₹4,919.16 |
| ARPU (MRR ÷ customers) | ₹84.66 |
| Average tenure — all / churned / active | 18.8 / 7.0 / 29.1 months |

## 2. Key findings

1. **Nearly half the customers left.** 7 of 15 churned (46.7 %). By revenue the loss is smaller — 32.3 % of MRR — because churned customers paid less per month on average (₹58.56 vs ₹107.49 for active customers).
2. **Contract type separates churners from non-churners completely.** Month-to-Month: 7 of 7 churned (100 %). One Year: 0 of 4. Two Year: 0 of 4. All ₹409.93 of revenue at risk comes from Month-to-Month customers.
3. **Churn is concentrated in the first year.** Every customer with 12 months' tenure or less churned (6 of 6); 13–24 months: 1 of 5 (20 %); 25+ months: 0 of 4. Customers up to 12 months account for ₹329.94 (80.5 %) of revenue at risk.
4. **High support contact goes with churn.** Every customer with 4+ tickets churned (5 of 5); 2–3 tickets: 2 of 4 (50 %); 0–1 tickets: 0 of 6. Churned customers averaged 4.3 tickets vs 1.0 for active customers, and no active customer has more than 2.
5. **Payment-method differences are explained by contract mix.** Raw churn rates look very different — Debit Card 100 % (2/2), UPI 75 % (3/4), Credit Card 33.3 % (2/6), Bank Transfer 0 % (0/3) — but inside Month-to-Month *every* payment method churned at 100 %, and no Bank Transfer customer is on Month-to-Month. Payment method should not be treated as a driver.
6. **Plan differences are also explained by contract mix.** Basic 71.4 % churn (5/7), Pro 50 % (2/4), Enterprise 0 % (0/4). But the 2 Basic and 2 Pro customers on One Year contracts all stayed, and all 4 Enterprise customers are on Two Year contracts.

## 3. High-risk segments (descriptive, this sample only)

| Segment | Customers | Churn rate | Revenue at risk | Share of revenue at risk |
|---|---|---|---|---|
| Contract: Month-to-Month | 7 | 100 % | ₹409.93 | 100 % |
| Tenure: 0–12 months | 6 | 100 % | ₹329.94 | 80.5 % |
| Support tickets: 4+ | 5 | 100 % | ₹279.95 | 68.3 % |
| Plan: Basic | 7 | 71.4 % | ₹249.95 | 61.0 % |
| Payment: UPI | 4 | 75 % | ₹149.97 | 36.6 % |

These rows overlap — they are mostly the same customers seen from different angles. Shares therefore add up to more than 100 %.

**Best-retained segments:** One Year and Two Year contracts (8 customers, 0 % churn, ₹859.92 = 67.7 % of MRR), tenure 25+ months, Enterprise plan, Bank Transfer, 0–1 support tickets.

## 4. Revenue risk observations

- ₹409.93 of monthly recurring revenue is attached to customers who churned — 32.3 % of the ₹1,269.85 MRR. If none are won back, that is about ₹4,919 a year (simple × 12 estimate, assumes unchanged prices).
- 61.0 % of the revenue at risk comes from the Basic plan (₹249.95) and 39.0 % from Pro (₹159.98). Enterprise contributes none.
- By lifetime revenue, churned customers had paid ₹3,109.51 — only 9.9 % of total lifetime revenue (₹31,327.18) — because they left early.
- Revenue is concentrated in long contracts: Two Year customers alone hold ₹599.96 (47.2 %) of MRR with 0 % churn.

## 5. Retention opportunities

- **Early-life Month-to-Month customers** are where all observed losses happened. Any intervention aimed at the first 12 months of a Month-to-Month subscription addresses 100 % of observed revenue at risk.
- **Active watch list.** The two active customers with the most support contact (2 tickets each — the highest among active customers) are CUST-1006 (One Year, 18 months, Basic, UPI, ₹49.99) and CUST-1009 (One Year, 15 months, Pro, Credit Card, ₹79.99). Together they hold ₹129.98 of MRR (15.1 % of retained MRR). This is a descriptive filter, not a prediction that they will leave.
- **Long-contract customers are stable** in this sample and hold two-thirds of MRR; protecting their renewal is a lower-effort way to safeguard revenue.

## 6. Recommendations

Each follows the EdVyro data-guide rule: name the **audience, decision, supporting metric, uncertainty and next measurement**.

| # | Audience | Decision | Supporting metric | Uncertainty | Next measurement |
|---|---|---|---|---|---|
| 1 | Retention / marketing team | Pilot an offer that moves new Month-to-Month customers to a One Year plan (e.g. a discounted first year). | Month-to-Month churn 100 % (7/7) vs 0 % (0/8) on longer contracts; 100 % of revenue at risk. | Customers who choose longer contracts may simply be more committed (self-selection). Converting someone may not change their behaviour. 15 records. | Churn rate of customers given the offer vs a comparison group not given it, over the next 3 months. |
| 2 | Customer success | Run structured onboarding check-ins at months 1, 3, 6 and 12 for every new customer. | 6/6 customers with ≤ 12 months' tenure churned; 80.5 % of revenue at risk. | Tenure overlaps fully with contract type here; check-ins may help only Month-to-Month customers. | Churn rate by tenure band for the next sign-up cohort, with and without check-ins. |
| 3 | Support lead | Flag any customer who reaches 3 tickets in 90 days for senior review and a root-cause call. | 4+ tickets: 5/5 churned; churners averaged 4.3 tickets vs 1.0; no active customer exceeds 2. | Tickets may be a symptom of a problem rather than its cause; the data has no ticket reasons. | Churn rate and ticket-resolution time for flagged customers; start recording ticket category. |
| 4 | Account managers | Proactively check in with CUST-1006 and CUST-1009 before their One Year terms renew. | Highest ticket count among active customers (2 each); ₹129.98 MRR (15.1 % of retained MRR). | No renewal dates in the data; 2 tickets is not evidence they will leave. | Renewal outcome of these two accounts; ticket count trend. |
| 5 | Product / pricing team | Review what Basic and Pro customers on Month-to-Month get in their first months; test a plan-fit conversation at sign-up. | Basic 71.4 % churn and 61.0 % of revenue at risk; Enterprise 0 %. | Plan is confounded with contract (all Enterprise are Two Year; Basic/Pro on One Year all stayed). | Churn by plan *within* the same contract type once more data is available. |
| 6 | Analytics / data team | Before scaling any programme, collect sign-up and churn dates, renewal dates and ticket reasons, and re-run this dashboard on a full customer extract. | Current sample is 15 records with fully overlapping risk traits. | Findings may not hold in a larger population. | Re-calculated churn rate per segment with confidence intervals on the larger dataset. |

## 7. Limitations

- **Small sample.** 15 customers; one customer changes a segment's churn rate by 14–50 percentage points.
- **No time dimension.** No sign-up or churn dates, so churn cannot be expressed per month and trends cannot be shown.
- **Overlapping traits.** Contract, tenure, tickets, plan and age move together; the data cannot separate their effects.
- **Correlation, not causation.** Nothing here shows that changing a customer's contract, plan or payment method would change their behaviour.
- **Synthetic data.** EdVyro supplies fictional records for training; do not draw conclusions about real customers.

---

## Text for Power BI page 5 (copy into text boxes)

**Key findings**
- 7 of 15 customers churned (46.7 %); ₹409.93 of monthly revenue (32.3 %) is at risk.
- All 7 churned customers were on Month-to-Month contracts; One Year and Two Year had 0 % churn.
- Every customer with 12 months' tenure or less churned (6/6).
- Every customer with 4+ support tickets churned (5/5); active customers have at most 2.
- Payment-method and plan differences disappear inside each contract type.

**Caution:** these traits describe the same 7 customers. The data shows who left, not why.

**Recommendations**
1. Pilot a One Year upgrade offer for new Month-to-Month customers.
2. Onboarding check-ins at months 1, 3, 6 and 12.
3. Escalate any customer reaching 3 support tickets in 90 days.
4. Check in with CUST-1006 and CUST-1009 before renewal.
5. Review the Basic/Pro first-months experience.
6. Collect dates and ticket reasons; re-test on a larger dataset.
