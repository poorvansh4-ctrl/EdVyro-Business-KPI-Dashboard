/*
 * Checks that the web dashboard calculates exactly what Python calculates.
 *   1. KPIs for all 300 filter combinations vs analysis/outputs/filter_expectations.json
 *   2. Segment tables vs analysis/outputs/kpi_results.json
 * Run from the project root (after the two Python scripts):
 *   node tests/test_dashboard_metrics.js
 */
"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "..");
const metrics = require(path.join(ROOT, "dashboard", "metrics.js"));

const sandbox = { window: {} };
vm.runInNewContext(fs.readFileSync(path.join(ROOT, "dashboard", "data.js"), "utf8"), sandbox);
const rows = sandbox.window.EDVYRO_DATA.rows;

const expectations = JSON.parse(fs.readFileSync(path.join(ROOT, "analysis", "outputs", "filter_expectations.json"), "utf8"));
const kpiResults = JSON.parse(fs.readFileSync(path.join(ROOT, "analysis", "outputs", "kpi_results.json"), "utf8"));

const TOLERANCE = 1e-9;
let checks = 0;
const failures = [];

function same(a, b) {
  if (a === null || b === null) return a === b;
  return Math.abs(a - b) <= TOLERANCE;
}

function expectEqual(label, actual, expected) {
  checks += 1;
  if (!same(actual, expected)) failures.push(`${label}: dashboard=${actual} python=${expected}`);
}

// 1. Every filter combination
let nonEmpty = 0;
for (const testCase of expectations) {
  const k = metrics.computeKpis(metrics.filterRows(rows, testCase.filters));
  if (k.total_customers > 0) nonEmpty += 1;
  const label = Object.values(testCase.filters).join(" | ");
  for (const [key, expected] of Object.entries(testCase.kpis)) {
    expectEqual(`${label} :: ${key}`, k[key], expected);
  }
}

// 2. Segment tables (unfiltered)
const SEGMENT_FIELDS = {
  ContractType: "ContractOrder",
  TenureGroup: "TenureGroupOrder",
  PaymentMethod: null,
  SubscriptionType: "MonthlyCharges",
  SupportTicketBand: "SupportTicketBandOrder",
  AgeGroup: "AgeGroupOrder",
};
const columnMap = {
  customers: "Customers", churned: "Churned", churnRate: "ChurnRatePct", mrr: "MonthlyRevenue",
  revenueAtRisk: "RevenueAtRisk", shareOfRevenueAtRisk: "ShareOfRevenueAtRiskPct", avgTenure: "AvgTenureMonths", arpu: "ARPU",
};
for (const [field, order] of Object.entries(SEGMENT_FIELDS)) {
  const pythonRows = Object.fromEntries(kpiResults.segments[field].map((r) => [r.Segment, r]));
  const jsTable = metrics.segmentTable(rows, field, order);
  expectEqual(`${field} :: segment count`, jsTable.length, Object.keys(pythonRows).length);
  for (const seg of jsTable) {
    for (const [jsKey, pyKey] of Object.entries(columnMap)) {
      expectEqual(`${field}=${seg.segment} :: ${jsKey}`, seg[jsKey], pythonRows[seg.segment][pyKey]);
    }
  }
}

// 3. Sort order sanity: tenure groups must come out in business order
const tenureOrder = metrics.options(rows, "TenureGroup", "TenureGroupOrder").join(", ");
checks += 1;
if (tenureOrder !== "0-6 months, 7-12 months, 13-24 months, 25+ months") failures.push(`tenure order: ${tenureOrder}`);

console.log(`Filter combinations tested: ${expectations.length} (${nonEmpty} non-empty)`);
console.log(`Checks run: ${checks}`);
if (failures.length) {
  console.log(`FAILED: ${failures.length}`);
  failures.slice(0, 20).forEach((f) => console.log("  " + f));
  process.exit(1);
}
console.log("ALL CHECKS PASSED - dashboard maths matches Python");
