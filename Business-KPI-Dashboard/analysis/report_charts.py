"""
EdVyro Data Analytics - Task 2: Business KPI Dashboard
Step 3 of the pipeline: static chart images for the report and README.

Input : analysis/outputs/kpi_results.json  (created by kpi_calculations.py)
Output: documentation/images/*.png

Run from the project root (after kpi_calculations.py):
    python analysis/report_charts.py
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "analysis" / "outputs" / "kpi_results.json"
IMG_DIR = ROOT / "documentation" / "images"

# Same validated colours as the dashboards (colour-blind-safe blue/orange pair).
RETAINED, CHURNED = "#2a78d6", "#eb6834"
INK, INK_2, MUTED, LINE, SURFACE = "#111827", "#455064", "#667085", "#e2e6ec", "#ffffff"

plt.rcParams.update({
    "font.family": ["Helvetica Neue", "Arial", "DejaVu Sans"],
    "font.size": 10,
    "axes.edgecolor": LINE,
    "axes.labelcolor": INK_2,
    "xtick.color": INK_2,
    "ytick.color": INK_2,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})


def segments(results, dimension):
    return results["segments"][dimension]


def finish(ax, title, subtitle):
    ax.set_title(title, loc="left", fontsize=12, fontweight="bold", color=INK, pad=22)
    ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=9, color=INK_2)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


def rate_bars(results, dimension, title, subtitle, filename, horizontal=True, sort=False):
    rows = segments(results, dimension)
    if sort:
        rows = sorted(rows, key=lambda r: (-r["ChurnRatePct"], -r["Customers"]))
    labels = [r["Segment"] for r in rows]
    values = [r["ChurnRatePct"] for r in rows]
    counts = [f"{r['Churned']} of {r['Customers']}" for r in rows]
    fig, ax = plt.subplots(figsize=(6.4, 0.55 * len(rows) + 1.6 if horizontal else 3.4))
    if horizontal:
        positions = range(len(rows))[::-1]
        ax.barh(list(positions), values, height=0.5, color=CHURNED)
        ax.set_yticks(list(positions), labels)
        for y, v, c in zip(positions, values, counts):
            ax.text(v + 1.5, y, f"{v:.1f}%  ({c})", va="center", fontsize=9, color=INK_2)
        ax.set_xlim(0, 125)
        ax.xaxis.set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_color(LINE)
    else:
        ax.bar(labels, values, width=0.45, color=CHURNED)
        for x, v, c in zip(range(len(rows)), values, counts):
            ax.text(x, v + 3, f"{v:.1f}%\n({c})", ha="center", fontsize=9, color=INK_2)
        ax.set_ylim(0, 125)
        ax.yaxis.set_visible(False)
        ax.spines["left"].set_visible(False)
    finish(ax, title, subtitle)
    fig.tight_layout()
    fig.savefig(IMG_DIR / filename, dpi=200)
    plt.close(fig)


def revenue_by_contract(results):
    rows = segments(results, "ContractType")
    labels = [r["Segment"] for r in rows][::-1]
    at_risk = [r["RevenueAtRisk"] for r in rows][::-1]
    retained = [r["MonthlyRevenue"] - r["RevenueAtRisk"] for r in rows][::-1]
    fig, ax = plt.subplots(figsize=(6.4, 3.3))
    ax.barh(labels, at_risk, height=0.5, color=CHURNED, label="Revenue at risk", edgecolor=SURFACE, linewidth=1)
    ax.barh(labels, retained, left=at_risk, height=0.5, color=RETAINED, label="Retained revenue", edgecolor=SURFACE, linewidth=1)
    for y, (a, r) in enumerate(zip(at_risk, retained)):
        note = "  (all at risk)" if a and not r else (f"  (₹{a:,.2f} at risk)" if a else "")
        ax.text(a + r + 8, y, f"₹{a + r:,.2f}{note}", va="center", fontsize=9, color=INK_2)
    ax.set_xlim(0, 900)
    ax.xaxis.set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_color(LINE)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=2, frameon=False, fontsize=9)
    finish(ax, "Monthly revenue by contract type", "All ₹409.93 of revenue at risk is on Month-to-Month contracts")
    fig.tight_layout()
    fig.savefig(IMG_DIR / "revenue_by_contract.png", dpi=200)
    plt.close(fig)


def status_split(results, dimension, title, subtitle, filename):
    rows = segments(results, dimension)
    labels = [r["Segment"] for r in rows][::-1]
    churned = [r["ChurnRatePct"] for r in rows][::-1]
    retained = [100 - v for v in churned]
    fig, ax = plt.subplots(figsize=(6.4, 0.55 * len(rows) + 1.6))
    ax.barh(labels, churned, height=0.5, color=CHURNED, label="Churned", edgecolor=SURFACE, linewidth=1)
    ax.barh(labels, retained, left=churned, height=0.5, color=RETAINED, label="Retained", edgecolor=SURFACE, linewidth=1)
    for y, (c, r) in enumerate(zip(churned, retained)):
        if c >= 12:
            ax.text(c / 2, y, f"{c:.0f}%", ha="center", va="center", fontsize=9, color=INK)
        if r >= 12:
            ax.text(c + r / 2, y, f"{r:.0f}%", ha="center", va="center", fontsize=9, color=SURFACE)
    ax.set_xlim(0, 100)
    ax.xaxis.set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_color(LINE)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=2, frameon=False, fontsize=9)
    finish(ax, title, subtitle)
    fig.tight_layout()
    fig.savefig(IMG_DIR / filename, dpi=200)
    plt.close(fig)


def main():
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    results = json.loads(RESULTS.read_text())
    rate_bars(results, "ContractType", "Churn rate by contract type",
              "Every churned customer was on a Month-to-Month contract", "churn_by_contract.png")
    rate_bars(results, "TenureGroup", "Churn rate by tenure group",
              "All customers in their first 12 months churned", "churn_by_tenure.png", horizontal=False)
    rate_bars(results, "PaymentMethod", "Churn rate by payment method",
              "Differences follow contract mix (see report section 6)", "churn_by_payment.png", sort=True)
    revenue_by_contract(results)
    status_split(results, "SupportTicketBand", "Churned vs retained by support tickets (90 days)",
                 "All 5 customers with 4+ tickets churned; none with 0-1", "churn_by_tickets.png")
    print("Charts written:", ", ".join(sorted(p.name for p in IMG_DIR.glob("*.png"))))


if __name__ == "__main__":
    main()
