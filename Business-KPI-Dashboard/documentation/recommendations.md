# Recommendations

**Decision question (EdVyro Customer Churn Analysis Guide):** *Which customer groups should a fictional subscription team contact first to reduce avoidable churn?*

**Short answer:** customers in the **first 12 months of a Month-to-Month plan**, especially those who have raised **3 or more support tickets**. In this sample that group contains every churned customer and all ₹409.93 of monthly revenue at risk.

Each recommendation below names the **audience, decision, supporting metric, uncertainty and next measurement**, as the EdVyro data guide requires. No revenue "saved" is claimed: the data cannot show what an intervention would achieve.

---

### 1. Pilot a One Year upgrade offer for new Month-to-Month customers — *priority: high*
- **Audience:** retention / marketing team
- **Decision:** offer new Month-to-Month customers a reason to move to a One Year plan (e.g. a first-year discount), as a controlled pilot.
- **Supporting metric:** Month-to-Month churn 100 % (7 of 7) vs 0 % (0 of 8) on One Year and Two Year; Month-to-Month holds 100 % of revenue at risk (₹409.93/month).
- **Uncertainty:** customers who choose longer contracts may simply be more committed. Moving someone to a longer contract may not change their behaviour. Based on 15 records.
- **Next measurement:** churn rate of customers who received the offer vs a comparison group who did not, after 3 months.

### 2. Structured onboarding for the first 12 months — *priority: high*
- **Audience:** customer success
- **Decision:** scheduled check-ins at months 1, 3, 6 and 12 for every new customer.
- **Supporting metric:** all 6 customers with ≤ 12 months' tenure churned; they carry ₹329.94 (80.5 %) of revenue at risk. Churned customers averaged 7.0 months' tenure vs 29.1 for active ones.
- **Uncertainty:** in this sample tenure and contract type overlap completely, so check-ins may only matter for Month-to-Month customers.
- **Next measurement:** churn rate by tenure band for the next sign-up cohort, with vs without check-ins.

### 3. Escalate customers who reach 3 support tickets — *priority: high*
- **Audience:** support team lead
- **Decision:** flag any customer with 3 tickets in 90 days for senior review and a root-cause call.
- **Supporting metric:** all 5 customers with 4+ tickets churned (₹279.95 at risk, 68.3 %); churned customers averaged 4.3 tickets vs 1.0; no active customer has more than 2. Every churned customer had at least 3.
- **Uncertainty:** tickets may be a symptom of a deeper problem rather than its cause; the data has no ticket reasons.
- **Next measurement:** churn rate and resolution time for flagged customers; start recording ticket category.

### 4. Check in with the two most-contacted active customers — *priority: medium*
- **Audience:** account managers
- **Decision:** contact CUST-1006 (One Year, 18 months, Basic, ₹49.99) and CUST-1009 (One Year, 15 months, Pro, ₹79.99) before their contracts renew.
- **Supporting metric:** 2 tickets each — the highest among active customers; together ₹129.98 MRR (15.1 % of retained revenue).
- **Uncertainty:** no renewal dates in the data; 2 tickets is not evidence they will leave. This is a descriptive filter, not a prediction.
- **Next measurement:** renewal outcome for both accounts.

### 5. Review the Basic and Pro first-months experience — *priority: medium*
- **Audience:** product / pricing team
- **Decision:** review what Basic and Pro Month-to-Month customers receive early on; test a plan-fit conversation at sign-up.
- **Supporting metric:** Basic churn 71.4 % (5 of 7) and 61.0 % of revenue at risk; Pro 50 % (2 of 4); Enterprise 0 %.
- **Uncertainty:** plan is confounded with contract — all Enterprise customers are on Two Year contracts, and Basic/Pro customers on One Year contracts all stayed.
- **Next measurement:** churn by plan *within the same contract type* once more data exists.

### 6. Close the data gaps before scaling any programme — *priority: foundation*
- **Audience:** analytics / data team
- **Decision:** add sign-up date, churn date, renewal date and ticket reason to the customer extract; re-run this pipeline and dashboard on the full customer base.
- **Supporting metric:** the current sample has 15 records and fully overlapping risk traits, so the separate effect of each trait cannot be measured.
- **Uncertainty:** the patterns above may not hold in a larger population.
- **Next measurement:** segment churn rates with confidence intervals on the larger dataset; monthly churn trend.

---

## What *not* to do
- **Do not target payment methods.** Debit Card (100 %) and UPI (75 %) look risky, but inside Month-to-Month every method churned at 100 % and no Bank Transfer customer is on Month-to-Month. Changing how people pay is unlikely to matter on this evidence.
- **Do not target by age or gender.** Younger customers churned more, but age overlaps with contract and tenure; gender shows only a small difference (50.0 % vs 42.9 %) on 7–8 customers each.

## KPIs to track after acting
Churn rate and revenue at risk by contract type and tenure group (both on the dashboard), share of new customers on One Year or longer, average tickets per customer in the first 90 days, and renewal rate of One Year contracts.
