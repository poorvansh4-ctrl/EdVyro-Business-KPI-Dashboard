/*
 * KPI and segmentation maths for the web dashboard.
 * Pure functions only (no DOM), so the same file runs in the browser and in
 * tests/test_dashboard_metrics.js, which checks every result against Python.
 * Definitions match analysis/kpi_calculations.py.
 */
(function (root) {
  "use strict";

  const FILTER_FIELDS = ["ContractType", "TenureGroup", "PaymentMethod", "ChurnStatus"];

  function sum(rows, field) {
    return rows.reduce((total, r) => total + r[field], 0);
  }

  function mean(rows, field) {
    return rows.length ? sum(rows, field) / rows.length : null;
  }

  function pct(part, whole) {
    return whole === 0 ? null : (part / whole) * 100;
  }

  function computeKpis(rows) {
    const total = new Set(rows.map((r) => r.CustomerID)).size;
    const churnedRows = rows.filter((r) => r.ChurnFlag === 1);
    const activeRows = rows.filter((r) => r.ChurnFlag === 0);
    const churned = churnedRows.length;
    const mrr = sum(rows, "MonthlyCharges");
    const atRisk = sum(churnedRows, "MonthlyCharges");
    return {
      total_customers: total,
      churned_customers: churned,
      active_customers: total - churned,
      churn_rate_pct: pct(churned, total),
      retention_rate_pct: pct(total - churned, total),
      monthly_revenue: mrr,
      retained_monthly_revenue: mrr - atRisk,
      lifetime_revenue: sum(rows, "TotalCharges"),
      revenue_at_risk: atRisk,
      revenue_at_risk_pct: pct(atRisk, mrr),
      annualised_revenue_at_risk: atRisk * 12,
      avg_tenure_months: mean(rows, "TenureMonths"),
      avg_tenure_churned: mean(churnedRows, "TenureMonths"),
      avg_tenure_active: mean(activeRows, "TenureMonths"),
      arpu: total ? mrr / total : null,
      avg_monthly_charge_churned: mean(churnedRows, "MonthlyCharges"),
      avg_monthly_charge_active: mean(activeRows, "MonthlyCharges"),
      avg_support_tickets: mean(rows, "SupportTickets"),
    };
  }

  function filterRows(rows, filters) {
    return rows.filter((r) =>
      FILTER_FIELDS.every((f) => !filters[f] || filters[f] === "All" || r[f] === filters[f])
    );
  }

  // Distinct values of a field, ordered by an optional numeric sort field.
  function options(rows, field, orderField) {
    const seen = new Map();
    rows.forEach((r) => {
      if (!seen.has(r[field])) seen.set(r[field], orderField ? r[orderField] : r[field]);
    });
    return [...seen.entries()]
      .sort((a, b) => (a[1] < b[1] ? -1 : a[1] > b[1] ? 1 : 0))
      .map(([value]) => value);
  }

  // One row per segment of `field` with the same measures as the Python segment tables.
  function segmentTable(rows, field, orderField) {
    const totalAtRisk = sum(rows.filter((r) => r.ChurnFlag === 1), "MonthlyCharges");
    const totalMrr = sum(rows, "MonthlyCharges");
    return options(rows, field, orderField).map((segment) => {
      const k = computeKpis(rows.filter((r) => r[field] === segment));
      return {
        segment,
        customers: k.total_customers,
        churned: k.churned_customers,
        active: k.active_customers,
        churnRate: k.churn_rate_pct,
        retentionRate: k.retention_rate_pct,
        mrr: k.monthly_revenue,
        retainedMrr: k.retained_monthly_revenue,
        shareOfMrr: pct(k.monthly_revenue, totalMrr),
        revenueAtRisk: k.revenue_at_risk,
        shareOfRevenueAtRisk: pct(k.revenue_at_risk, totalAtRisk),
        avgTenure: k.avg_tenure_months,
        arpu: k.arpu,
        avgTickets: k.avg_support_tickets,
      };
    });
  }

  // Segments with the highest value of `key` (ties included). Null when nothing qualifies.
  function leaders(table, key) {
    const valid = table.filter((t) => t[key] !== null);
    if (!valid.length) return null;
    const top = Math.max(...valid.map((t) => t[key]));
    return { value: top, segments: valid.filter((t) => t[key] === top) };
  }

  const api = { FILTER_FIELDS, computeKpis, filterRows, options, segmentTable, leaders, pct };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = api;
  } else {
    root.EdvyroMetrics = api;
  }
})(typeof window !== "undefined" ? window : globalThis);
