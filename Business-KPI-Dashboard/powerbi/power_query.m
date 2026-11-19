// EdVyro Business KPI Dashboard - Power Query (M) cleaning script
// Rebuilds data/cleaned_dataset.csv inside Power BI from the untouched original file,
// using the same rules as analysis/data_analysis.py.
//
// HOW TO USE (Power BI Desktop):
//   Home > Get data > Blank query > Advanced Editor > paste this whole file > Done.
//   Rename the query to: Customers
//   Change SourcePath below to the folder where you saved the project.

let
    // 1. Location of the ORIGINAL EdVyro file (never edited)
    SourcePath = "C:\Users\YourName\Documents\Business-KPI-Dashboard\data\original_dataset.csv",

    // 2. Read the CSV (UTF-8, comma separated, first row = headers)
    Source = Csv.Document(
        File.Contents(SourcePath),
        [Delimiter = ",", Columns = 11, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    // 3. Trim stray spaces from every text field (0 cells affected in the supplied file)
    TrimmedText = Table.TransformColumns(
        PromotedHeaders,
        {
            {"CustomerID", Text.Trim, type text},
            {"Gender", Text.Trim, type text},
            {"SubscriptionType", Text.Trim, type text},
            {"ContractType", Text.Trim, type text},
            {"PaymentMethod", Text.Trim, type text},
            {"Churn", Text.Trim, type text}
        }
    ),

    // 4. Set data types. "en-US" makes sure 49.99 is read as a decimal on every PC locale.
    ChangedTypes = Table.TransformColumnTypes(
        TrimmedText,
        {
            {"Age", Int64.Type},
            {"TenureMonths", Int64.Type},
            {"SupportTickets", Int64.Type},
            {"MonthlyCharges", Currency.Type},
            {"TotalCharges", Currency.Type}
        },
        "en-US"
    ),

    // 5. Churn helper columns
    AddedChurnFlag = Table.AddColumn(ChangedTypes, "ChurnFlag", each if [Churn] = "Yes" then 1 else 0, Int64.Type),
    AddedChurnStatus = Table.AddColumn(AddedChurnFlag, "ChurnStatus", each if [Churn] = "Yes" then "Churned" else "Retained", type text),

    // 6. Tenure groups (+ sort order so visuals show 0-6, 7-12, 13-24, 25+)
    AddedTenureGroup = Table.AddColumn(AddedChurnStatus, "TenureGroup", each
        if [TenureMonths] <= 6 then "0-6 months"
        else if [TenureMonths] <= 12 then "7-12 months"
        else if [TenureMonths] <= 24 then "13-24 months"
        else "25+ months", type text),
    AddedTenureGroupOrder = Table.AddColumn(AddedTenureGroup, "TenureGroupOrder", each
        if [TenureMonths] <= 6 then 1 else if [TenureMonths] <= 12 then 2 else if [TenureMonths] <= 24 then 3 else 4, Int64.Type),

    // 7. Age groups
    AddedAgeGroup = Table.AddColumn(AddedTenureGroupOrder, "AgeGroup", each
        if [Age] <= 29 then "18-29" else if [Age] <= 44 then "30-44" else "45+", type text),
    AddedAgeGroupOrder = Table.AddColumn(AddedAgeGroup, "AgeGroupOrder", each
        if [Age] <= 29 then 1 else if [Age] <= 44 then 2 else 3, Int64.Type),

    // 8. Support-ticket bands
    AddedTicketBand = Table.AddColumn(AddedAgeGroupOrder, "SupportTicketBand", each
        if [SupportTickets] <= 1 then "Low (0-1)" else if [SupportTickets] <= 3 then "Medium (2-3)" else "High (4+)", type text),
    AddedTicketBandOrder = Table.AddColumn(AddedTicketBand, "SupportTicketBandOrder", each
        if [SupportTickets] <= 1 then 1 else if [SupportTickets] <= 3 then 2 else 3, Int64.Type),

    // 9. Lifetime-value (TotalCharges) bands
    AddedChargesBand = Table.AddColumn(AddedTicketBandOrder, "TotalChargesBand", each
        if [TotalCharges] < 1000 then "Under 1000" else if [TotalCharges] < 3000 then "1000-2999" else "3000+", type text),
    AddedChargesBandOrder = Table.AddColumn(AddedChargesBand, "TotalChargesBandOrder", each
        if [TotalCharges] < 1000 then 1 else if [TotalCharges] < 3000 then 2 else 3, Int64.Type),

    // 10. Contract sort order (Month-to-Month, One Year, Two Year)
    AddedContractOrder = Table.AddColumn(AddedChargesBandOrder, "ContractOrder", each
        if [ContractType] = "Month-to-Month" then 1 else if [ContractType] = "One Year" then 2 else 3, Int64.Type),

    // 11. Validation: TotalCharges should equal MonthlyCharges x TenureMonths (all 15 rows = "OK")
    AddedExpectedTotal = Table.AddColumn(AddedContractOrder, "ExpectedTotalCharges", each [MonthlyCharges] * [TenureMonths], Currency.Type),
    AddedTotalCheck = Table.AddColumn(AddedExpectedTotal, "TotalChargesCheck", each
        if Number.Abs([TotalCharges] - [ExpectedTotalCharges]) <= 0.01 then "OK" else "Mismatch", type text)
in
    AddedTotalCheck
