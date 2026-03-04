-- ============================================================
-- Query    : Genre Performance Benchmark vs. Global Average
-- Database : Chinook (SQLite)
-- Author   : Senior Data Analyst, Chinook Digital Media
-- Purpose  : Benchmarks each genre's revenue and sales performance
--            against the global average revenue per track sold, and
--            evaluates catalog efficiency via revenue per unique track
--            in the genre's catalog, to guide catalog investment,
--            merchandising priority, and promotional spend decisions.
-- Audience : Product and Marketing Team
-- Notes    : Revenue is derived from InvoiceLine (UnitPrice * Quantity).
--            Global average is computed across all genres combined,
--            not as a simple average of per-genre averages.
--            Catalog depth is sourced from the Track table (not
--            InvoiceLine) to reflect available inventory, not units sold.
--            Genres with zero sales (e.g. Opera) are intentionally
--            included with $0.00 revenue to surface dead catalog
--            inventory for catalog investment decisions. Division
--            columns use NULLIF to prevent divide-by-zero errors
--            on zero-sales genres, resolving to $0.00 via COALESCE.
-- ============================================================


-- ============================================================
-- CTE 1: genre_stats
-- Aggregates total revenue and total tracks sold for each genre
-- by joining Genre → Track → InvoiceLine.
-- InvoiceLine uses a LEFT JOIN so genres with zero sales are
-- retained in the result rather than silently dropped. COALESCE
-- wraps both aggregates to convert NULL (no sales) to 0.
-- GenreId is retained here to support the catalog_depth join downstream.
-- Raw numeric values are kept unformatted for downstream calculations.
-- ============================================================
WITH genre_stats AS (
    SELECT
        g.GenreId,
        g.Name                                          AS genre_name,
        COALESCE(SUM(il.UnitPrice * il.Quantity), 0)    AS total_revenue_raw,
        COALESCE(SUM(il.Quantity), 0)                   AS total_tracks_sold
    FROM Genre g
    INNER JOIN Track t
        ON t.GenreId = g.GenreId
    LEFT JOIN InvoiceLine il
        ON il.TrackId = t.TrackId
    GROUP BY
        g.GenreId,
        g.Name
),

-- ============================================================
-- CTE 2: global_avg
-- Calculates the global average revenue per track sold once,
-- across all genres combined, to serve as the benchmark baseline.
-- Dividing total revenue by total tracks sold (not averaging
-- per-genre averages) ensures accuracy across unequal genre sizes.
-- Zero-sales genres contribute 0 to both the numerator and
-- denominator, leaving the global average unaffected.
-- ============================================================
global_avg AS (
    SELECT
        SUM(total_revenue_raw) * 1.0
            / NULLIF(SUM(total_tracks_sold), 0)     AS avg_rev_per_track_global
    FROM genre_stats
),

-- ============================================================
-- CTE 3: catalog_depth
-- Counts the number of unique tracks available per genre directly
-- from the Track table. This reflects catalog inventory depth —
-- how many tracks Chinook carries in each genre — independent of
-- whether those tracks have ever been sold. Used to compute the
-- catalog efficiency metric: revenue earned per available track.
-- ============================================================
catalog_depth AS (
    SELECT
        GenreId,
        COUNT(TrackId)                              AS unique_tracks_in_catalog
    FROM Track
    GROUP BY
        GenreId
),

-- ============================================================
-- CTE 4: genre_benchmarked
-- Joins genre_stats, global_avg, and catalog_depth to produce
-- one row per genre with all intermediate metrics needed for the
-- final output: per-track sold average and catalog efficiency ratio.
-- NULLIF guards both division columns against zero-sales genres —
-- the resulting NULL resolves cleanly to $0.00 via COALESCE in
-- the final SELECT.
-- ============================================================
genre_benchmarked AS (
    SELECT
        gs.genre_name,
        gs.total_revenue_raw,
        gs.total_tracks_sold,
        gs.total_revenue_raw * 1.0
            / NULLIF(gs.total_tracks_sold, 0)           AS avg_rev_per_track_raw,
        ga.avg_rev_per_track_global,
        gs.total_revenue_raw * 1.0
            / NULLIF(cd.unique_tracks_in_catalog, 0)    AS rev_per_catalog_track_raw
    FROM genre_stats gs
    INNER JOIN global_avg ga
        ON 1 = 1  -- Cross-join pattern: global_avg is a single-row scalar CTE
    INNER JOIN catalog_depth cd
        ON cd.GenreId = gs.GenreId
)

-- ============================================================
-- Final SELECT
-- Produces the genre benchmark report with ranking, formatted
-- currency columns, percentage share of total revenue, global
-- average benchmark, and revenue per catalog track to surface
-- catalog productivity independent of sales volume.
-- Zero-sales genres appear at the bottom of the ranking with
-- $0.00 values, making dead catalog inventory explicitly visible.
-- A UNION ALL total row is appended at the bottom.
-- _sort_grp and _sort_rev are ordering helpers consumed by the
-- outer ORDER BY and excluded from the visible output columns.
-- ============================================================
SELECT
    "Rank",
    "Genre",
    "Total Revenue",
    "Tracks Sold",
    "Avg Revenue per Track",
    "Global Avg Revenue per Track",
    "% of Total Revenue",
    "Revenue per Catalog Track"
FROM (

    -- Detail rows: one row per genre, ranked by total revenue
    SELECT
        ROW_NUMBER() OVER (
            ORDER BY total_revenue_raw DESC
        )                                                           AS "Rank",
        genre_name                                                  AS "Genre",
        PRINTF('$%.2f', COALESCE(total_revenue_raw, 0))            AS "Total Revenue",
        total_tracks_sold                                           AS "Tracks Sold",
        PRINTF('$%.2f', COALESCE(avg_rev_per_track_raw, 0))        AS "Avg Revenue per Track",
        PRINTF('$%.2f', COALESCE(avg_rev_per_track_global, 0))     AS "Global Avg Revenue per Track",
        PRINTF('%.1f%%',
            COALESCE(total_revenue_raw, 0) * 100.0
            / NULLIF(SUM(total_revenue_raw) OVER (), 0)
        )                                                           AS "% of Total Revenue",
        PRINTF('$%.2f', COALESCE(rev_per_catalog_track_raw, 0))    AS "Revenue per Catalog Track",
        1                                                           AS _sort_grp,
        total_revenue_raw                                           AS _sort_rev
    FROM genre_benchmarked

    UNION ALL

    -- Total row: cross-genre sums appended below all detail rows
    SELECT
        '—',
        'TOTAL',
        PRINTF('$%.2f', SUM(total_revenue_raw)),
        SUM(total_tracks_sold),
        '—',
        '—',
        '100.0%',
        '—',
        2,
        0
    FROM genre_benchmarked

)
ORDER BY
    _sort_grp,
    _sort_rev DESC;
