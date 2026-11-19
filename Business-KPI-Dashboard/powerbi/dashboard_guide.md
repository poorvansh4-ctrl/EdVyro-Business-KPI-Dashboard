# Power BI Build Guide — EdVyro Business KPI Dashboard

This guide walks you through building the 5-page dashboard in **Power BI Desktop**, click by click. It takes about 90–120 minutes the first time.

Files you will use from this project:

| File | What it is for |
|---|---|
| `data/original_dataset.csv` | The untouched EdVyro dataset (loaded by the Power Query script) |
| `data/cleaned_dataset.csv` | Ready-to-use cleaned data (shortcut option) |
| `powerbi/power_query.m` | Cleaning steps for Power Query |
| `powerbi/dax_measures.md` | Every KPI measure + the expected values to check against |
| `powerbi/edvyro_theme.json` | Colours and fonts (colour-blind-safe blue/orange) |
| `analysis/business_insights.md` | Text for insight boxes and page 5 |

---

## 0. Before you start — important for Mac users

- **Power BI Desktop runs only on Windows.** It is free (Microsoft Store → "Power BI Desktop"). If you only have a Mac, use a Windows PC (college lab, friend, cyber café) or a Windows virtual machine.
- **Publishing needs a Microsoft work or school account** (for example your college email). Personal Gmail/Outlook addresses cannot sign up for Power BI.
- **"Publish to web"** (a public link anyone can open) must be allowed by your organisation's admin. Many colleges turn it off.

If any of these block you, EdVyro also accepts **Looker Studio** or a **spreadsheet dashboard** (Google Sheets) — both work on a Mac with a Gmail account. See `documentation/submission_guide.md`.

---

## 1. Load and clean the data

### Option A (recommended) — Power Query cleaning script
1. Open Power BI Desktop → **Blank report**.
2. **Home → Get data → Blank query**. The Power Query Editor opens.
3. **Home → Advanced Editor**. Delete everything in the box.
4. Open `powerbi/power_query.m` in Notepad, copy all of it, paste it into the Advanced Editor.
5. Change the `SourcePath` line to the real location of `original_dataset.csv` on your PC. Tip: in File Explorer, Shift + right-click the file → **Copy as path**, then paste between the quotes (remove the extra quotes it adds).
6. Click **Done**. You should see 15 rows and 24 columns.
7. In **Query Settings** (right side), rename the query from `Query1` to **`Customers`**.
8. Scroll right to the `TotalChargesCheck` column — every row should say **OK**.
9. **Home → Close & Apply**.

### Option B (shortcut) — load the already-cleaned file
1. **Home → Get data → Text/CSV** → choose `data/cleaned_dataset.csv` → **Transform Data**.
2. Check the column types: `Age`, `TenureMonths`, `SupportTickets`, `ChurnFlag` and every `…Order` column = Whole number; `MonthlyCharges`, `TotalCharges`, `ExpectedTotalCharges` = Fixed decimal number.
3. Rename the query to **`Customers`** → **Close & Apply**.

Either way, the Applied Steps list is your evidence of the cleaning process — take a screenshot of it for your submission.

---

## 2. Prepare the model

Go to **Table view** (left toolbar, grid icon), select the `Customers` table.

**Sort categories in a logical order** (otherwise Power BI sorts alphabetically, e.g. "13-24" before "7-12"):

| Click this column… | Column tools → Sort by column → |
|---|---|
| `TenureGroup` | `TenureGroupOrder` |
| `ContractType` | `ContractOrder` |
| `AgeGroup` | `AgeGroupOrder` |
| `SupportTicketBand` | `SupportTicketBandOrder` |
| `TotalChargesBand` | `TotalChargesBandOrder` |

**Format money columns:** select `MonthlyCharges` → Column tools → Format: Currency → **₹ English (India)**. Repeat for `TotalCharges`.

**Stop Power BI summing IDs and ages:** select `Age` → Column tools → Summarization → **Don't summarize**. Do the same for `TenureMonths`, `SupportTickets` and every `…Order` column.

**Hide helper columns** (right-click → Hide in report view): every `…Order` column, `ExpectedTotalCharges`, `TotalChargesCheck`, `ChurnFlag`.

---

## 3. Apply the theme

**View → Themes (dropdown arrow) → Browse for themes** → choose `powerbi/edvyro_theme.json`.

Colour meaning used on every page (validated colour-blind-safe):
- **Blue `#2a78d6`** = Retained customers / retained revenue
- **Orange `#eb6834`** = Churned customers / revenue at risk

Power BI assigns colours alphabetically, so "Churned" may come out blue. Whenever a visual uses `ChurnStatus` in the legend: **Format → Visual → Columns/Bars → Colors** → set *Churned* = `#eb6834`, *Retained* = `#2a78d6`.

---

## 4. Create the measures

Follow `powerbi/dax_measures.md` sections 1–6. When you are done, build a quick test: add a **Card** with `Total Customers` — it must show **15**. Add `Churn Rate %` — it must show **46.7%**. Delete the test cards afterwards.

---

## 5. Pages and canvas

1. Click the empty canvas → **Format page → Canvas settings** → Type **16:9** (1280 × 720).
2. Create 5 pages (the **+** at the bottom) and rename them (double-click the tab):
   1. `Executive Overview`
   2. `Churn Analysis`
   3. `Revenue Analysis`
   4. `Customer Segmentation`
   5. `Business Insights`

**Layout grid used on every page** (set exact positions in **Format → General → Properties → Size and position**):

```
y = 16   ┌ Page title (text box) ────────────────────────────────────────────┐   h = 48
y = 72   [Contract type ▾] [Tenure group ▾] [Payment method ▾] [Churn status ▾]   h = 56
y = 144  ┌──────────────── content area (x 24 → 1256, y 144 → 704) ──────────────┐
y = 704  └──────────────────────────────────────────────────────────────────────┘
```
Slicers: width 296, x = 24 / 336 / 648 / 960. Gap between visuals: 16 px.

---

## 6. Filters (slicers) — build once, sync to every page

On the **Executive Overview** page:

1. Click an empty spot → **Visualizations → Slicer**. Drag `ContractType` into **Field**.
2. **Format → Visual → Slicer settings → Options → Style: Dropdown**. Turn **Selection → "Select all" option: On**, keep **Single select: Off** (Ctrl + click picks several).
3. **Format → General → Title** → text: `Contract type`.
4. Position: x 24, y 72, w 296, h 56.
5. Repeat for:
   - `TenureGroup` → title `Tenure group` → x 336
   - `PaymentMethod` → title `Payment method` → x 648
   - `ChurnStatus` → title `Churn status` → x 960
6. **View → Sync slicers.** Select each slicer in turn and tick both boxes (**Sync** and **Visible**) for all 5 pages. Now one selection filters every page.
7. Optional: add a **Clear all slicers** button: **Insert → Buttons → Clear all slicers**, place it in the page title row at the right.

Note for reviewers: choosing *Churn status = Churned* makes Churn Rate 100 % by definition — that slicer is for exploring the churned or retained group, not for reading the rate.

---

## 7. Page 1 — Executive Overview

**Title text box** (x 24, y 16, w 900, h 48): `Customer health — executive overview` (20 pt, Segoe UI Semibold). Second line, 11 pt grey: `EdVyro sample · 15 customers · amounts in ₹ (fictional)`.

**Primary KPI cards** — Visualizations → **Card** (or *Card (new)*), y 144, h 112, w 296:

| x | Field | Card title |
|---|---|---|
| 24 | `Total Customers` | Total customers |
| 336 | `Churn Rate %` | Churn rate |
| 648 | `Retention Rate %` | Retention rate |
| 960 | `Revenue at Risk` | Revenue at risk (monthly) |

Card formatting: Callout value 28 pt; Category label off; turn the visual **Title on** with the text above. Expected (no filters): 15 / 46.7% / 53.3% / ₹409.93.

**Secondary cards** — y 272, h 72, w 296: `Monthly Revenue (MRR)` (x 24), `ARPU` (x 336), `Average Tenure (Months)` (x 648), `Active Customers` (x 960).

**Customer split** — Visualizations → **100% stacked bar chart** (x 24, y 360, w 400, h 150)
- Y-axis: *(leave empty)*; X-axis: `Total Customers`; Legend: `ChurnStatus`
- Data labels: On (shows 46.7 % / 53.3 %). Legend: On, top. Title: `Customer split — churned vs retained`.

**Health summary** — **Card (new)** or **Multi-row card** (x 24, y 526, w 400, h 178) with `Customer Health Summary` (wrap text on). The sentence updates with the slicers.

**Churn rate by contract type** — **Clustered bar chart** (x 440, y 360, w 400, h 344)
- Y-axis: `ContractType`; X-axis: `Churn Rate %`
- Bar colour: orange `#eb6834`. Data labels: On. X-axis: Off (labels carry the values). Gridlines: Off.
- Title: `Churn rate by contract type`. Subtitle (Format → General → Title → Subtitle): `All churn in this sample came from Month-to-Month contracts.`

**"What this page shows" text box** (x 856, y 360, w 400, h 344):
```
Customer health at a glance
• 7 of 15 customers churned (46.7 %).
• ₹409.93 of ₹1,269.85 monthly revenue (32.3 %) belongs to churned customers.
• Churned customers stayed 7.0 months on average vs 29.1 for active ones.
• Every churned customer was on a Month-to-Month contract.
Use the filters above to explore any segment.
```

---

## 8. Page 2 — Churn Analysis

Four charts in a 2 × 2 grid, each w 608, h 272. Put the written insight in each chart's **Subtitle** (this meets EdVyro's optional upgrade "add a written insight beside every major visual").

| Position (x, y) | Visual | Fields | Title / subtitle |
|---|---|---|---|
| 24, 144 | **Stacked bar chart** | Y: `ContractType` · X: `Total Customers` · Legend: `ChurnStatus` (Churned orange, Retained blue) | *Churned vs retained customers by contract* / "7 of 7 Month-to-Month customers churned; 0 of 8 on longer contracts." |
| 648, 144 | **Clustered bar chart** | Y: `ContractType` · X: `Churn Rate %` (orange) | *Churn rate by contract type* / "Month-to-Month 100 %, One Year 0 %, Two Year 0 %." |
| 24, 432 | **Clustered column chart** | X: `TenureGroup` · Y: `Churn Rate %` (orange) | *Churn rate by tenure group* / "All 6 customers in their first 12 months churned; none past 24 months." |
| 648, 432 | **Clustered bar chart** | Y: `PaymentMethod` · X: `Churn Rate %` (orange). Sort: `Churn Rate %` descending (… → Sort axis) | *Churn rate by payment method* / "Differences reflect contract mix: inside Month-to-Month every method churned 100 %." |

For every chart: Data labels **On**, value axis **Off**, gridlines **Off**, bar/column **Spacing → Inner padding 40 %** (keeps bars thin).

**Tooltip check:** hover a bar — it should show the churn rate. To add counts to the tooltip, drag `Total Customers` and `Churned Customers` into the **Tooltips** well.

---

## 9. Page 3 — Revenue Analysis

**Cards** (y 144, h 96, w 296): `Monthly Revenue (MRR)` (x 24), `Revenue at Risk` (x 336), `Revenue at Risk %` (x 648), `ARPU` (x 960).
Expected: ₹1,269.85 / ₹409.93 / 32.3 % / ₹84.66.

| Position (x, y, w, h) | Visual | Fields | Title / subtitle |
|---|---|---|---|
| 24, 256, 608, 216 | **Stacked bar chart** | Y: `ContractType` · X: `Retained MRR` **and** `Revenue at Risk` (two measures). Colours: Retained MRR blue, Revenue at Risk orange | *Revenue by contract type — retained vs at risk* / "All ₹409.93 at risk sits in Month-to-Month; Two Year holds ₹599.96 (47 % of MRR)." |
| 648, 256, 608, 216 | **Stacked column chart** | X: `SubscriptionType` · Y: `Total Customers` · Legend: `ChurnStatus` | *Monthly charges: customers per price plan* / "Basic ₹49.99, Pro ₹79.99, Enterprise ₹149.99. Churned customers paid ₹58.56/month on average vs ₹107.49 for active." |
| 24, 488, 608, 216 | **Clustered column chart** | X: `TenureGroup` · Y: `Revenue at Risk` (orange) | *Revenue at risk by tenure group* / "₹329.94 (80.5 %) of revenue at risk is from customers in their first 12 months." |
| 648, 488, 608, 216 | **Clustered bar chart** | Y: `ContractType` · X: `ARPU` (blue) | *Average revenue per customer by contract* / "Two Year customers pay ₹149.99/month on average; Month-to-Month ₹58.56." |

Optional: add a small card with `Annualised Revenue at Risk` titled *"Annual revenue at risk (estimate: monthly × 12)"*.

---

## 10. Page 4 — Customer Segmentation

**Segment matrix** — Visualizations → **Matrix** (x 24, y 144, w 800, h 272)
- Rows: `ContractType`, then `TenureGroup` (use the ⤓ expand icon to drill down)
- Values: `Total Customers`, `Churned Customers`, `Churn Rate %`, `Monthly Revenue (MRR)`, `Revenue at Risk`, `Share of Revenue at Risk %`
- Conditional formatting: `Churn Rate %` → **Data bars** (positive bar colour orange). `Revenue at Risk` → Data bars orange.
- Title: *Segment table — contract and tenure*.

**Contract × payment matrix** — **Matrix** (x 840, y 144, w 416, h 272)
- Rows: `ContractType` · Columns: `PaymentMethod` · Values: `Churn Rate %`, `Total Customers`
- Title: *Churn rate: contract × payment method* / Subtitle: "Read across a row: within each contract, payment method makes no difference."

**Segment bars** — three **100% stacked bar charts** (y 432, w 400, h 272), each with Legend = `ChurnStatus`, X = `Total Customers`, data labels on:

| x | Y-axis | Title / subtitle |
|---|---|---|
| 24 | `TenureGroup` | *Tenure segmentation* / "Churn falls from 100 % (≤ 12 months) to 0 % (25+ months)." |
| 440 | `PaymentMethod` | *Payment method segmentation* / "Bank Transfer 0 %, Debit Card 100 % — driven by which contracts use each method." |
| 856 | `SupportTicketBand` | *Customer churn by support contact* / "All 5 customers with 4+ tickets churned; none with 0–1." |

---

## 11. Page 5 — Business Insights

Use text boxes (**Insert → Text box**). Copy the text from the *"Text for Power BI page 5"* section at the bottom of `analysis/business_insights.md`.

| Position (x, y, w, h) | Text box heading | Content |
|---|---|---|
| 24, 144, 608, 272 | **Key findings** | 5 findings + the caution line |
| 24, 432, 608, 272 | **High-risk segments & revenue risk** | Month-to-Month (7 customers, 100 %, ₹409.93); first 12 months (6, 100 %, ₹329.94); 4+ tickets (5, 100 %, ₹279.95); Basic plan (7, 71.4 %, ₹249.95). |
| 648, 144, 608, 272 | **Recommendations** | Recommendations 1–6 |
| 648, 432, 608, 160 | **Retention opportunities** | Early-life Month-to-Month customers; watch list CUST-1006 and CUST-1009 (₹129.98 MRR); long contracts hold 67.7 % of MRR. |
| 648, 608, 608, 96 | **Limitations** | 15 synthetic records · no dates · overlapping traits · correlation, not causation. |

Text boxes are static: they describe the full dataset and do not change with slicers. Say so in a small grey note at the bottom of the page: *"Insights describe all 15 customers; filters on this page do not change the text."*

---

## 12. Test before publishing (Phase 10 checklist)

Compare each item with the expected values in `powerbi/dax_measures.md` §7.

- [ ] No filters: 15 customers, 46.7 % churn, 53.3 % retention, ₹409.93 revenue at risk.
- [ ] Contract = One Year → churn rate shows **0.0 %** (not blank), revenue at risk **₹0.00**.
- [ ] Payment = UPI → 4 customers, 75.0 %, ₹149.97.
- [ ] Tenure = 13-24 months → 5 customers, 20.0 %, ₹79.99.
- [ ] Slicer choice on page 1 is still selected when you open page 3 (sync works).
- [ ] Tenure groups appear in order 0-6, 7-12, 13-24, 25+ (sort-by-column works).
- [ ] Every chart has a title; colours are Churned = orange, Retained = blue on every page.
- [ ] Add a card with `Check - Rates Total` → shows 100 %; `Check - Revenue Split` → shows 0. Delete afterwards.

---

## 13. Publish and get a view-only link

1. **File → Save as** → `EdVyro_Business_KPI_Dashboard.pbix` (save it in the `powerbi/` folder).
2. **Home → Publish** → sign in with your work/school account → choose **My workspace**.
3. Click **Open '…' in Power BI** when it finishes (opens app.powerbi.com).
4. In the report: **File → Embed report → Publish to web (public)** → **Create embed code** → **Publish**.
5. Copy the **"Link you can send in email"**. This is your dashboard link.
6. **Test it:** open a private/incognito browser window, paste the link, and confirm the report loads and the slicers work without signing in.

> **Privacy:** Publish to web makes the report public on the internet. That is fine for this fictional dataset — never do it with real customer data.

**If "Publish to web" is greyed out or disabled by your admin:**
- Ask your college IT admin to allow it, **or**
- Use an accepted alternative platform (Looker Studio or Google Sheets) — see `documentation/submission_guide.md`, **and**
- Still upload the `.pbix`, a PDF export (**File → Export → Export to PDF**) and page screenshots to your GitHub repository so the reviewer can see the Power BI work.

---

## 14. Export evidence for your submission

- **File → Export → Export to PDF** → save as `powerbi/EdVyro_Business_KPI_Dashboard.pdf`.
- Screenshot each page (Windows: `Win + Shift + S`) → save into `documentation/screenshots/` as `page1_overview.png` … `page5_insights.png`.
- Screenshot the Power Query **Applied Steps** and the measures list.
