-- ============================================
-- Case Study 1: Geographic Revenue Analysis
-- Business Question: Which countries generate the most revenue,
--                   how many unique customers does each have,
--                   and what share of global revenue do they represent?
-- Skills: CTEs, Window Functions, Aggregate Functions,
--         CROSS JOIN, PRINTF formatting, ROUND, ROW_NUMBER
-- Author: Daniel Matel-Okoh
-- AI Partner: Claude
-- ============================================

WITH country_metrics AS (
    SELECT
        i.BillingCountry                                        AS country,
        -- Count every invoice line to get gross revenue per country
        SUM(i.Total)                                            AS revenue_raw,
        -- DISTINCT ensures we count customers once, even if they
        -- placed multiple orders (which is common in this dataset)
        COUNT(DISTINCT i.CustomerId)                            AS unique_customer_count,
        -- COUNT(InvoiceId) captures every order placed, including
        -- repeat purchases by the same customer — intentionally NOT distinct
        COUNT(i.InvoiceId)                                      AS total_orders,
        -- Divide total revenue by unique buyers — not by invoice count —
        -- so the average reflects spend per person, not per transaction
        SUM(i.Total) / COUNT(DISTINCT i.CustomerId)             AS avg_revenue_per_customer_raw
    FROM Invoice AS i
        -- INNER JOIN: intentionally excludes any customer record that
        -- has never generated an invoice (no ghost rows in the output)
        INNER JOIN Customer AS c
            ON i.CustomerId = c.CustomerId
    GROUP BY
        i.BillingCountry
),
global_totals AS (
    -- Isolated CTE so the grand total is calculated once and reused cleanly.
    -- CROSS JOIN below makes this single value available on every row
    -- without distorting the GROUP BY in country_metrics.
    SELECT
        SUM(Total) AS global_revenue_raw
    FROM Invoice
)
SELECT
    -- Explicit rank makes the #1 market immediately obvious to any reader
    ROW_NUMBER() OVER (ORDER BY cm.revenue_raw DESC)              AS "Rank",
    cm.country                                                    AS "Country",
    -- PRINTF formats raw float as a readable dollar amount.
    -- COALESCE guards against any unexpected NULLs (e.g. data gaps),
    -- defaulting to 0 so the report never surfaces a blank cell.
    PRINTF('$%.2f', COALESCE(cm.revenue_raw, 0))                  AS "Total Revenue",
    cm.unique_customer_count                                      AS "Unique Customers",
    -- Placed immediately after Unique Customers so readers can directly
    -- compare headcount vs. order volume — a natural loyalty signal
    cm.total_orders                                               AS "Total Orders",
    PRINTF('$%.2f', COALESCE(cm.avg_revenue_per_customer_raw, 0)) AS "Avg Revenue Per Customer",
    -- Percentage share: each country's slice of the global pie.
    -- Multiplied by 100.0 (not 100) to force float division in SQLite,
    -- then ROUND to 2 decimal places for a clean, readable percentage.
    ROUND((cm.revenue_raw / gt.global_revenue_raw) * 100.0, 2)   AS "% of Global Revenue"
FROM
    country_metrics AS cm
    -- CROSS JOIN is intentional: global_totals is a single-row scalar.
    -- This pattern attaches the grand total to every country row
    -- without aggregating or collapsing the result set.
    CROSS JOIN global_totals AS gt
-- Highest-revenue markets appear first — most useful view for
-- the marketing team prioritising budget allocation decisions
ORDER BY
    cm.revenue_raw DESC;
