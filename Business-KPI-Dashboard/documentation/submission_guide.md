# Submission Guide — EdVyro Task 2

## 1. What EdVyro asks for

- **Deliverable:** a *published Power BI, Tableau, Looker Studio, or spreadsheet dashboard link*.
- **Submit:** *one public or view-only link*, with supporting files in the same repository, folder or project page "so one link is enough". Examples EdVyro gives: a GitHub repository, Google Drive folder, Figma file, YouTube video or portfolio page "that a reviewer can open without requesting access".

## 2. Your dashboard link (done)

**Google Sheets dashboard, view-only:**
<https://docs.google.com/spreadsheets/d/1i7BwdceJrBUXdqcdYteQnfCGl6LGgv06dqtX2r1riZY/edit?usp=sharing>

| Requirement | Status |
|---|---|
| Accepted platform | ✅ Spreadsheet dashboard (Google Sheets) |
| Public / view-only | ✅ Sharing is "Anyone with the link → Viewer" |
| Opens without signing in | ✅ Tested signed out on 19 Nov 2026 |
| Filters for contract, tenure, payment method (+ churn status) | ✅ 4 slicers; tested as a signed-out viewer |
| Churn rate, retention rate, revenue at risk, tenure KPIs | ✅ Scorecards + definitions on the Dashboard and Definitions tabs |
| Clear labels and accessible colours | ✅ Every chart titled, insight line under each, colour-blind-safe orange/blue |
| Same numbers as the verified analysis | ✅ KPI Check tab: 17/17 Match; `tests/test_spreadsheet_export.py`: 20/20 |

Details of every tab and check: [`spreadsheet/README.md`](../spreadsheet/README.md).

**Two quick things to do yourself (2 minutes):**
1. Open the link above in a **private/incognito window** and confirm you see the dashboard without signing in.
2. Optional: check the sharing setting yourself: open the sheet signed in → **Share** (top right) → under *General access* it should say **Anyone with the link · Viewer**. Don't change it to Editor.

---

## 3. Put everything in one public GitHub repository

The dashboard link alone meets the deliverable. EdVyro also asks for supporting files in one place, so a repository is the best single link to submit.

1. Create a free account at <https://github.com> (any email works).
2. Click **+ → New repository** → name it `Business-KPI-Dashboard` → **Public** → **Create repository**.
3. On the empty repository page click **uploading an existing file**. Drag in the *contents* of the `Business-KPI-Dashboard` folder (all sub-folders) → **Commit changes**.
4. Optional, to host the web dashboard for free: **Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: main, folder: / (root) → Save**. After 1–2 minutes it is live at `https://<your-username>.github.io/Business-KPI-Dashboard/dashboard/`. Paste that link into the README's "Live dashboards" table (pencil icon → edit → Commit).
5. Open the repository link in a private/incognito window to confirm it is public.

The README already shows the Google Sheets link at the top, so a reviewer who opens the repository finds the dashboard first.

## 4. What to paste in the EdVyro submission form

**Link:** your GitHub repository link (or, if you skip GitHub, the Google Sheets link above).

**Short explanation:**

> **Business KPI Dashboard — EdVyro Data Analytics Task 2.** Interactive Google Sheets dashboard (view-only link in the README; filters work without signing in) built on the official EdVyro customer churn sample (15 customers; 13 data-quality checks, all passed, no rows removed). KPIs: churn rate 46.7%, retention rate 53.3%, revenue at risk ₹409.93/month (32.3% of monthly revenue, defined as the monthly charges of churned customers), average tenure 18.8 months. Filters for contract type, tenure group, payment method and churn status update 8 KPI cards, 12 charts and 6 segment tables, with a written insight under every chart. Key finding: all 7 churned customers were on Month-to-Month contracts, in their first ~12 months and had 3+ support tickets; payment-method differences disappear within each contract type. Because these traits overlap in a 15-record sample, recommendations are framed as tests with named measurements. Every KPI is recalculated in the sheet and matched to the verified Python results (KPI Check tab), and the repository includes the Python pipeline, tests, a supplementary web dashboard, a Power BI build kit and a business report.

---

## 5. Final submission checklist

**Done:**
- [x] Official EdVyro dataset used unchanged (`data/original_dataset.csv`)
- [x] Cleaned dataset and cleaning log
- [x] KPIs defined and verified (hand calculation, independent recalculation, automated tests)
- [x] Google Sheets dashboard built: 4 filters, 8 KPI cards, 12 charts, 6 segment tables, Insights, KPI Check
- [x] View-only public link set and tested signed out, including using a filter
- [x] Google Sheet numbers checked against the verified Python results (20/20)
- [x] Backup downloads of the sheet (`spreadsheet/`: .xlsx, PDF, CSV, screenshots)
- [x] Business report (`documentation/final_report.pdf`), recommendations, methodology
- [x] Supplementary web dashboard and Power BI build kit

**You need to do:**
- [ ] Open the Google Sheets link in a private/incognito window (section 2)
- [ ] Create the public GitHub repository and upload this folder (section 3)
- [ ] Submit the repository link with the explanation from section 4 on EdVyro
- [ ] Check your EdVyro dashboard later for review feedback (submission is not approval)

---

## 6. Alternatives (only if you need them)

**Power BI.** Needs Power BI Desktop (Windows only) and a work or school Microsoft account; personal Gmail/Outlook addresses cannot sign up. Follow `powerbi/dashboard_guide.md`, which covers publishing in §13.

**Looker Studio** (free with Gmail, runs in the browser):
1. Data source: **Google Sheets** connector → this spreadsheet → `Customers` tab.
2. Calculated fields: Total Customers `COUNT_DISTINCT(CustomerID)`; Churned `SUM(Churned)`; Churn Rate `SUM(Churned) / COUNT_DISTINCT(CustomerID)`; Retention Rate `1 - SUM(Churned) / COUNT_DISTINCT(CustomerID)`; Revenue at Risk `SUM(\`Revenue at risk\`)`; Average Tenure `AVG(TenureMonths)`; ARPU `SUM(MonthlyCharges) / COUNT_DISTINCT(CustomerID)`.
3. Add **Drop-down list** controls for `ContractType`, `TenureGroup`, `PaymentMethod`, `ChurnStatus` and make them report-level.
4. **Share → Manage access → Anyone on the internet with the link can view**.
