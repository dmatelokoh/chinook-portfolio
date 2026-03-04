-- ============================================================
-- Query    : Customer Lifetime Value & Segmentation — V2
-- Database : Chinook (SQLite)
-- Author   : Senior Data Analyst, Chinook Digital Media
-- Purpose  : Calculate total lifetime spend, purchase count,
--            and average order value per customer, then assign
--            each customer to a value tier (Platinum / Gold /
--            Silver / Bronze) based on explicit spend thresholds.
--            Includes each customer's % contribution to total
--            company revenue and a global rank by lifetime spend.
-- Audience : Marketing team — segment-specific retention campaigns
-- Changes  : V2 — Added ROW_NUMBER() rank, recalibrated tier
--            thresholds, added pct_of_total_revenue via CROSS JOIN
--            against a global revenue CTE, title-cased all aliases,
--            and appended a standalone tier summary query.
-- Notes    : Spend is aggregated at the customer level by summing
--            InvoiceLine unit prices × quantities. Tier thresholds
--            are business-defined, not mathematical quartiles.
-- ============================================================

WITH customer_metrics AS (
    SELECT
        c.CustomerId,
        c.FirstName,
        c.LastName,
        c.Country,
        SUM(il.UnitPrice * il.Quantity)                             AS lifetime_spend,
        COUNT(DISTINCT i.InvoiceId)                                 AS purchase_count,
        SUM(il.UnitPrice * il.Quantity) / NULLIF(COUNT(DISTINCT i.InvoiceId), 0)
                                                                    AS avg_order_value
    FROM       Customer     c
    INNER JOIN Invoice      i   ON i.CustomerId   = c.CustomerId
    INNER JOIN InvoiceLine  il  ON il.InvoiceId   = i.InvoiceId
    GROUP BY
        c.CustomerId,
        c.FirstName,
        c.LastName,
        c.Country
),
customer_segments AS (
    SELECT
        CustomerId,
        FirstName,
        LastName,
        Country,
        lifetime_spend,
        purchase_count,
        avg_order_value,
        CASE
            WHEN lifetime_spend >= 45.00 THEN 'Platinum'
            WHEN lifetime_spend >= 40.00 THEN 'Gold'
            WHEN lifetime_spend >= 37.62 THEN 'Silver'
            ELSE                              'Bronze'
        END AS value_tier
    FROM customer_metrics
),
global_revenue AS (
    SELECT
        SUM(lifetime_spend) AS total_revenue
    FROM customer_metrics
)
SELECT
    ROW_NUMBER() OVER (ORDER BY cs.lifetime_spend DESC)             AS "Rank",
    cs.FirstName || ' ' || cs.LastName                             AS "Customer Name",
    cs.Country                                                      AS "Country",
    COALESCE(PRINTF('$%.2f', cs.lifetime_spend),  'N/A')           AS "Total Lifetime Spend",
    cs.purchase_count                                               AS "Number of Purchases",
    COALESCE(PRINTF('$%.2f', cs.avg_order_value), 'N/A')           AS "Avg Order Value",
    ROUND(
        cs.lifetime_spend / NULLIF(gr.total_revenue, 0) * 100,
        2
    )                                                               AS "Pct of Total Revenue",
    cs.value_tier                                                   AS "Value Tier"
FROM       customer_segments cs
CROSS JOIN global_revenue    gr
ORDER BY cs.lifetime_spend DESC;


-- ============================================================
-- Tier Summary Query (Standalone)
-- ============================================================
WITH customer_metrics AS (
    SELECT
        c.CustomerId,
        SUM(il.UnitPrice * il.Quantity) AS lifetime_spend
    FROM       Customer     c
    INNER JOIN Invoice      i   ON i.CustomerId   = c.CustomerId
    INNER JOIN InvoiceLine  il  ON il.InvoiceId   = i.InvoiceId
    GROUP BY c.CustomerId
),
customer_segments AS (
    SELECT
        CustomerId,
        lifetime_spend,
        CASE
            WHEN lifetime_spend >= 45.00 THEN 'Platinum'
            WHEN lifetime_spend >= 40.00 THEN 'Gold'
            WHEN lifetime_spend >= 37.62 THEN 'Silver'
            ELSE                              'Bronze'
        END AS value_tier
    FROM customer_metrics
),
global_revenue AS (
    SELECT SUM(lifetime_spend) AS total_revenue
    FROM customer_metrics
)
SELECT
    cs.value_tier                                                   AS "Value Tier",
    COUNT(cs.CustomerId)                                            AS "Number of Customers",
    COALESCE(PRINTF('$%.2f', SUM(cs.lifetime_spend)), 'N/A')       AS "Total Tier Revenue",
    ROUND(
        SUM(cs.lifetime_spend) / NULLIF(gr.total_revenue, 0) * 100,
        2
    )                                                               AS "Pct of Total Revenue"
FROM       customer_segments cs
CROSS JOIN global_revenue    gr
GROUP BY cs.value_tier, gr.total_revenue
ORDER BY SUM(cs.lifetime_spend) DESC;
