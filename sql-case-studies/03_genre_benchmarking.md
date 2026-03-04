
# Case Study 3: What's Selling and What Isn't?
## Genre & Track Performance Benchmarking

---

## The Business Question

Chinook's catalog spans multiple genres — from Rock and Metal to Jazz, Classical, 
and beyond. But not all genres are created equal. Some punch above their weight 
relative to the size of their catalog. Others have large track libraries that 
generate disproportionately little revenue.

Leadership needs to know which product categories deserve investment and which 
are underperforming — but "underperforming" only means something when you have 
a benchmark to compare against.

**The core question:** Which genres are over-performing or under-performing 
relative to the catalog average — and what does that tell us about where to 
focus product, marketing, and merchandising decisions?

This is not just a revenue ranking. The goal is to understand:
- Which genres generate the most total revenue?
- Which genres generate the most revenue per track sold — efficiency, not just volume?
- How does each genre compare against the global catalog average?
- Which genres are "above average", "average", or "below average" performers?

---

## The Prompt I Gave the AI

Using the structured prompt framework and context priming approach from the 
previous case studies, here is the prompt I built for this analysis.

By Case Study 3, my context prime reflects lessons from the first two — 
specifically the standing instructions around ranking and percentage-of-total 
columns. The V1 output should be closer to production-ready as a result.

---

**🧠 Persona**
> You are a senior data analyst working inside Chinook Digital Media. You write 
> clean, well-commented SQLite-compatible SQL for a marketing team. You follow 
> these standards in every query you write:
>
> - Always use CTEs (WITH ... AS) instead of nested subqueries
> - Always format currency with PRINTF('$%.2f', ...)
> - Always use COALESCE() to handle potential NULLs in formatted columns
> - Always use INNER JOIN unless a LEFT JOIN is explicitly required
> - Always add a formal comment header block at the top of every query
> - Never use reserved words as aliases (avg, total, count, etc.)
> - Never use SQLite-incompatible functions (no FORMAT(), TOP, ISNULL())
> - For any query that ranks or compares rows, always include:
>   1. An explicit ROW_NUMBER() ranking column as the first column
>   2. A percentage of total column showing each row's share of the relevant aggregate
>   Unless I explicitly tell you these are not needed.
>
> These are non-negotiable standards. Apply them to every query in this session 
> without being reminded.

**🎯 Task**
> Write a SQL query that benchmarks each genre's performance against the global 
> catalog average. For each genre, calculate total revenue, total tracks sold, 
> and average revenue per track sold. Then compare each genre against the global 
> average revenue per track and label it as 'Above Average', 'Average', or 
> 'Below Average'.

**📋 Context**
> I'm working in the Chinook SQLite database. The relevant tables are:
> - Genre (GenreId, Name)
> - Track (TrackId, GenreId)
> - InvoiceLine (InvoiceLineId, InvoiceId, TrackId, UnitPrice, Quantity)
>
> Every track belongs to one genre via GenreId. Every sale is recorded as a 
> line item in InvoiceLine. I want performance calculated at the genre level — 
> total revenue and total tracks sold across all invoices for each genre.

**🚧 Constraints**
> - Use CASE WHEN to create the performance label — not a subquery in the SELECT
> - The global average should be calculated once in its own CTE — not recalculated 
>   for every row using a correlated subquery
> - All standards listed in the Persona section apply

**📐 Format**
> Use three CTEs:
> - CTE 1: Calculate total revenue and tracks sold per genre
> - CTE 2: Calculate the global average revenue per track across all genres
> - CTE 3 or Final SELECT: Join the two, add the performance label, ranking, 
>   percentage of total revenue, and formatted currency columns
>
> Sort by total revenue descending.

**📎 References**
> Follow this exact CTE structure and commenting style for every query:
> - Each CTE should have a comment block above it explaining its purpose
> - The final SELECT should have a comment explaining what it produces
> - The header block at the top of the query should follow this format exactly:
>
> ```
> -- ============================================================
> -- Query    : [Query name]
> -- Database : Chinook (SQLite)
> -- Author   : Senior Data Analyst, Chinook Digital Media
> -- Purpose  : [What this query does]
> -- Audience : [Who will use this]
> -- Notes    : [Any important context]
> -- ============================================================
> ```
>
> Column aliases should use title case with spaces — "Total Revenue" not 
> "total_revenue". Raw numeric columns used for sorting or calculations 
> should be kept as unformatted intermediates in the CTEs and only 
> formatted with PRINTF() in the final SELECT.

**👥 Audience**
> The output will be used by the product and marketing team to make decisions 
> about catalog investment, merchandising priority, and promotional spend 
> by genre. Column names should be immediately understandable to a 
> non-technical reader.

**✅ Evaluate**
> I'll check the first draft for: correct join logic across three tables, 
> global average calculated efficiently in its own CTE, performance labels 
> applied correctly via CASE WHEN, ranking and percentage of total included, 
> and whether the output actually answers the benchmarking question — not 
> just ranks genres by revenue.

---

## The AI's Raw Output

The V1 output was the strongest of the three case studies. Notable improvements 
without any feedback required:
- ROW_NUMBER() ranking included from the start — prompt library update working
- % of Total Revenue included from the start — prompt library update working
- Global average calculated correctly once in its own CTE — not recalculated per row
- Used `* 1.0` to force float division in SQLite — inferred without being told
- Used `ON 1 = 1` CROSS JOIN pattern with an inline comment explaining why
- Full comment header block applied correctly

The V1 query is saved below for reference. The evaluation follows.
```sql
WITH genre_stats AS (
    SELECT
        g.GenreId,
        g.Name                                          AS genre_name,
        SUM(il.UnitPrice * il.Quantity)                 AS total_revenue_raw,
        SUM(il.Quantity)                                AS total_tracks_sold
    FROM Genre g
    INNER JOIN Track t
        ON t.GenreId = g.GenreId
    INNER JOIN InvoiceLine il
        ON il.TrackId = t.TrackId
    GROUP BY
        g.GenreId,
        g.Name
),
global_avg AS (
    SELECT
        SUM(total_revenue_raw) * 1.0 / SUM(total_tracks_sold) AS avg_rev_per_track_global
    FROM genre_stats
),
genre_benchmarked AS (
    SELECT
        gs.genre_name,
        gs.total_revenue_raw,
        gs.total_tracks_sold,
        gs.total_revenue_raw * 1.0 / gs.total_tracks_sold  AS avg_rev_per_track_raw,
        ga.avg_rev_per_track_global,
        CASE
            WHEN (gs.total_revenue_raw * 1.0 / gs.total_tracks_sold)
                 > ga.avg_rev_per_track_global THEN 'Above Average'
            WHEN (gs.total_revenue_raw * 1.0 / gs.total_tracks_sold)
                 = ga.avg_rev_per_track_global THEN 'Average'
            ELSE                                    'Below Average'
        END                                                 AS performance_label
    FROM genre_stats gs
    INNER JOIN global_avg ga
        ON 1 = 1
)
SELECT
    ROW_NUMBER() OVER (ORDER BY total_revenue_raw DESC)         AS "Rank",
    genre_name                                                   AS "Genre",
    PRINTF('$%.2f', COALESCE(total_revenue_raw, 0))             AS "Total Revenue",
    total_tracks_sold                                            AS "Tracks Sold",
    PRINTF('$%.2f', COALESCE(avg_rev_per_track_raw, 0))         AS "Avg Revenue per Track",
    PRINTF('$%.2f', COALESCE(avg_rev_per_track_global, 0))      AS "Global Avg Revenue per Track",
    PRINTF('%.1f%%',
        COALESCE(total_revenue_raw, 0) * 100.0
        / SUM(total_revenue_raw) OVER ()
    )                                                            AS "% of Total Revenue",
    performance_label                                            AS "vs. Global Average"
FROM genre_benchmarked
ORDER BY
    total_revenue_raw DESC;
```

**V1 Query Results:**

| Rank | Genre | Total Revenue | Tracks Sold | Avg Rev/Track | Global Avg | % of Total | vs. Global Avg |
|------|-------|---------------|-------------|---------------|------------|------------|----------------|
| 1 | Rock | $826.65 | 835 | $0.99 | $1.04 | 35.5% | Below Average |
| 2 | Latin | $382.14 | 386 | $0.99 | $1.04 | 16.4% | Below Average |
| 3 | Metal | $261.36 | 264 | $0.99 | $1.04 | 11.2% | Below Average |
| 4 | Alternative & Punk | $241.56 | 244 | $0.99 | $1.04 | 10.4% | Below Average |
| 5 | TV Shows | $93.53 | 47 | $1.99 | $1.04 | 4.0% | Above Average |
| 6 | Jazz | $79.20 | 80 | $0.99 | $1.04 | 3.4% | Below Average |
| 7 | Blues | $60.39 | 61 | $0.99 | $1.04 | 2.6% | Below Average |
| 8 | Drama | $57.71 | 29 | $1.99 | $1.04 | 2.5% | Above Average |
| 9 | R&B/Soul | $40.59 | 41 | $0.99 | $1.04 | 1.7% | Below Average |
| 10 | Classical | $40.59 | 41 | $0.99 | $1.04 | 1.7% | Below Average |
| 11 | Sci Fi & Fantasy | $39.80 | 20 | $1.99 | $1.04 | 1.7% | Above Average |
| 12 | Reggae | $29.70 | 30 | $0.99 | $1.04 | 1.3% | Below Average |
| 13 | Pop | $27.72 | 28 | $0.99 | $1.04 | 1.2% | Below Average |
| 14 | Soundtrack | $19.80 | 20 | $0.99 | $1.04 | 0.9% | Below Average |
| 15 | Comedy | $17.91 | 9 | $1.99 | $1.04 | 0.8% | Above Average |
| 16 | Hip Hop/Rap | $16.83 | 17 | $0.99 | $1.04 | 0.7% | Below Average |
| 17 | Bossa Nova | $14.85 | 15 | $0.99 | $1.04 | 0.6% | Below Average |
| 18 | Alternative | $13.86 | 14 | $0.99 | $1.04 | 0.6% | Below Average |
| 19 | World | $12.87 | 13 | $0.99 | $1.04 | 0.6% | Below Average |
| 20 | Science Fiction | $11.94 | 6 | $1.99 | $1.04 | 0.5% | Above Average |
| 21 | Heavy Metal | $11.88 | 12 | $0.99 | $1.04 | 0.5% | Below Average |
| 22 | Electronica/Dance | $11.88 | 12 | $0.99 | $1.04 | 0.5% | Below Average |
| 23 | Easy Listening | $9.90 | 10 | $0.99 | $1.04 | 0.4% | Below Average |
| 24 | Rock And Roll | $5.94 | 6 | $0.99 | $1.04 | 0.3% | Below Average |

---

## My Critical Evaluation

The V1 output was structurally clean — the prompt library updates eliminated the 
ranking and percentage issues that required feedback in the previous two case 
studies. But after reviewing the results, I had four substantive issues to address.

**1. The "vs. Global Average" metric is misleading**

This is the most important issue — and it's one the AI couldn't have caught because 
it requires product domain knowledge to recognize.

Looking at the output, the pattern is immediately obvious: every $0.99 track is 
labeled "Below Average" and every $1.99 TV show or movie is labeled "Above Average." 
The performance label isn't measuring genre popularity, catalog efficiency, or 
customer demand — it's measuring price point. Music tracks are priced at $0.99. 
Video content is priced at $1.99. The global average lands at $1.04 — just above 
the $0.99 music floor — which means almost every music genre automatically fails 
the benchmark regardless of how well it actually sells.

A good report shouldn't have meaningless columns. Each metric should provide 
actionable context for leadership to make informed decisions. This one doesn't.

The better metric is **revenue per unique track in the catalog** — how much revenue 
each available track is generating on average. This measures catalog efficiency: 
a genre with 500 tracks generating $826 has very different economics than a genre 
with 10 tracks generating $826. The first has a deep catalog that's modestly 
utilized. The second has a tight catalog that's working extremely hard.

I replaced the "vs. Global Average" column with a catalog efficiency metric: 
revenue divided by the number of unique tracks available in that genre — not 
tracks sold, but tracks that exist in the catalog. This required adding a fourth 
CTE to count unique tracks per genre from the Track table.

**2. Column order is not intuitive**

The "vs. Global Average" column appeared at the far right — separated from the 
"Avg Revenue per Track" column it's commenting on. In a report, comparative 
context should sit immediately next to the metric it references. I moved the 
performance label to appear directly after "Avg Revenue per Track" so the reader's 
eye naturally flows: here's the number, here's what it means.

**3. No total row**

The output has no summary row showing total revenue and total percentage across 
all genres. Adding a total row serves two purposes: it gives leadership an instant 
sanity check that percentages sum to 100%, and it shows the full revenue picture 
at a glance. I added this using a UNION ALL pattern at the bottom of the final 
SELECT.

**4. Rock and Roll anomaly — flagged for investigation**

Rock is our #1 genre with $826.65 in revenue and 835 tracks sold. Rock And Roll 
sits at #24 with just $5.94 and 6 tracks sold. In most music catalogs, Rock and 
Roll is the parent genre of Rock — not a separate category. This could indicate 
a catalog tagging issue where a small number of tracks are labeled "Rock And Roll" 
instead of "Rock." Worth flagging to the product team before presenting this report.

**The bottom line:** The prompt library updates from Cases 1 and 2 eliminated two 
recurring structural issues before V1 was even written. The remaining issues required 
product domain knowledge — specifically understanding that track pricing creates a 
misleading benchmark — and a presentation judgment call about column order. That's 
the human layer: knowing not just whether the query runs, but whether the output 
actually means something to the person reading it.

---

## Iterative Prompting — From V1 to V2

I reformatted my evaluation notes as a structured feedback prompt and fed them 
back to the AI.

**The feedback prompt I sent:**

> *"The query you returned was strong, but I have three specific changes I need 
> you to incorporate:*
>
> *1. **Replace the 'vs. Global Average' performance label with a catalog efficiency 
> metric.** The current label is misleading because it's driven entirely by price 
> point ($0.99 music vs. $1.99 video), not by actual genre performance. Replace it 
> with a new metric: revenue per unique track in the catalog — how much revenue each 
> available track in that genre is generating on average.*
>
> *To calculate this, add a new CTE that counts the number of unique tracks per 
> genre from the Track table (not from InvoiceLine — I want catalog depth, not 
> tracks sold). Then add a column in the final SELECT that divides total revenue 
> by unique tracks in catalog. Label the column "Revenue per Catalog Track" and 
> format it with PRINTF('$%.2f').*
>
> *Remove the existing 'vs. Global Average' performance label column entirely — 
> it is being replaced by "Revenue per Catalog Track". Keep the "Global Avg Revenue 
> per Track" column as a trending KPI.*
>
> *2. **Add a total row** at the bottom of the output showing:*
> - *'TOTAL' as the Genre label*
> - *Sum of all Total Revenue (formatted)*
> - *Sum of all Tracks Sold*
> - *'—' for Avg Revenue per Track and Revenue per Catalog Track columns*
> - *'100.0%' for % of Total Revenue*
> - *'—' for Global Avg Revenue per Track*
>
> *Use a UNION ALL pattern to append the total row to the main query.*
>
> *3. **Update the comment header block** to reflect these changes — update the 
> Purpose field to mention catalog efficiency as the new benchmark metric, and add 
> a note explaining that Global Avg Revenue per Track serves as a trending KPI.*
>
> *Keep everything else exactly as it is — CTE structure, join logic, ranking, 
> formatting, and inline comments."*

---

**A note on prompt precision — what this iteration taught me:**

My first version of this feedback prompt said "Keep the global average revenue 
per track column and the existing performance label" — which contradicted my 
instruction to replace the performance label. The AI did exactly what I told it: 
it added the new catalog efficiency column but kept the old performance label too, 
because I hadn't explicitly said to remove it.

This is a prompt precision lesson worth documenting: **AI executes instructions 
literally.** If you want something removed, you have to say so explicitly. Assuming 
the AI will infer that a replacement means a removal is one of the most common 
sources of unexpected output. I caught the contradiction, updated the feedback 
prompt to explicitly state "Remove the existing 'vs. Global Average' performance 
label column entirely", and the column was cleanly dropped on the next iteration.

The corrected feedback prompt above reflects the final version I sent.

---

**The V2 Query — AI Output After Prompt Chaining:**
```sql
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
--            Global Avg Revenue per Track serves as a trending KPI —
--            a rising figure over time indicates growing AOV across
--            the catalog, driven by either higher-priced content
--            adoption or a shift in catalog mix toward premium genres.
-- ============================================================

WITH genre_stats AS (
    SELECT
        g.GenreId,
        g.Name                                      AS genre_name,
        SUM(il.UnitPrice * il.Quantity)             AS total_revenue_raw,
        SUM(il.Quantity)                            AS total_tracks_sold
    FROM Genre g
    INNER JOIN Track t
        ON t.GenreId = g.GenreId
    INNER JOIN InvoiceLine il
        ON il.TrackId = t.TrackId
    GROUP BY
        g.GenreId,
        g.Name
),
global_avg AS (
    SELECT
        SUM(total_revenue_raw) * 1.0
            / SUM(total_tracks_sold)                AS avg_rev_per_track_global
    FROM genre_stats
),
catalog_depth AS (
    SELECT
        GenreId,
        COUNT(TrackId)                              AS unique_tracks_in_catalog
    FROM Track
    GROUP BY
        GenreId
),
genre_benchmarked AS (
    SELECT
        gs.genre_name,
        gs.total_revenue_raw,
        gs.total_tracks_sold,
        gs.total_revenue_raw * 1.0
            / gs.total_tracks_sold                  AS avg_rev_per_track_raw,
        ga.avg_rev_per_track_global,
        gs.total_revenue_raw * 1.0
            / cd.unique_tracks_in_catalog           AS rev_per_catalog_track_raw
    FROM genre_stats gs
    INNER JOIN global_avg ga
        ON 1 = 1
    INNER JOIN catalog_depth cd
        ON cd.GenreId = gs.GenreId
)
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
            / SUM(total_revenue_raw) OVER ()
        )                                                           AS "% of Total Revenue",
        PRINTF('$%.2f', COALESCE(rev_per_catalog_track_raw, 0))    AS "Revenue per Catalog Track",
        1                                                           AS _sort_grp,
        total_revenue_raw                                           AS _sort_rev
    FROM genre_benchmarked

    UNION ALL

    SELECT
        NULL,
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
```

---

**What the prompt chaining achieved:**

| | V1 (Initial AI Output) | V2 (After Prompt Chaining) |
|---|---|---|
| Ranking column | ✅ | ✅ |
| % of Total Revenue | ✅ | ✅ |
| Catalog efficiency metric | ❌ | ✅ Revenue per Catalog Track |
| Meaningful performance label | ❌ | ✅ Replaced price-driven label |
| Column order — label next to metric | ❌ | ✅ |
| Total row | ❌ | ✅ UNION ALL pattern |
| Global avg as trending KPI | ❌ | ✅ Documented in header |
| Correct join logic | ✅ | ✅ |
| Float division fix (* 1.0) | ✅ | ✅ |
| Inline comments | ✅ | ✅ |

*Note: Final query results including Opera appear in the Verification Pass section below.*

---

## Verification Pass — AI Self-Check + Meta-Prompting

I ran the same structured verification pass before accepting these results.

**The verification prompt I sent:**

> *"Please verify the V2 query output is mathematically correct. Run the 
> following checks:*
>
> *1. **Spot-check the % of Total Revenue column** — Sum all 24 genre percentages 
> and confirm they add up to approximately 100%.*
>
> *2. **Verify the global revenue total** — The TOTAL row shows $2,328.60. 
> Cross-check this against the sum of all 24 individual genre revenue figures. 
> Do they match?*
>
> *3. **Check the Revenue per Catalog Track calculation for one genre** — For 
> Sci Fi & Fantasy: divide Total Revenue ($39.80) by the number of unique tracks 
> in the catalog for that genre. Show your work and confirm it matches the $1.53 
> shown.*
>
> *4. **Verify the Tracks Sold total** — The TOTAL row shows 2,240 tracks sold. 
> Sum all 24 individual genre track counts and confirm they match.*
>
> *5. **Flag any anomalies** — Are there any genres where the Revenue per Catalog 
> Track, Tracks Sold, or Total Revenue looks inconsistent or surprising?*
>
> *6. **Meta-check** — Beyond these five checks, what other verification methods 
> would you recommend specifically for a genre benchmarking query that uses 
> catalog depth as a metric?"*

---

**Verification Results:**

**✅ Check 1 — Percentages sum to 100%**
All 24 genre percentages sum to exactly 100.0%. No rounding drift. All rows 
account for the full total.

**✅ Check 2 — Genre revenues sum to TOTAL row**
Running sum across all 24 genres = $2,328.60. Matches the TOTAL row exactly. 
No genres dropped or double-counted.

**✅ Check 3 — Sci Fi & Fantasy Revenue per Catalog Track**
$39.80 ÷ $1.53 = 26.01 → 26 unique catalog tracks.
Reverse check: $39.80 ÷ 26 = $1.530769... → formats to $1.53. Confirmed correct.

This genre ranks #11 by total revenue but #1 by catalog efficiency — its small, 
tight catalog is generating more revenue per available track than any other genre 
in the database. That's the insight the original "vs. Global Average" label 
completely missed.

**✅ Check 4 — Tracks Sold total**
Sum of all 24 genre track counts = 2,240. Matches the TOTAL row exactly.

**⚠️ Check 5 — Anomalies flagged**

**Bossa Nova — perfect sell-through:**
$14.85 ÷ $0.99 = exactly 15 catalog tracks. Tracks Sold is also 15. Every single 
track in the Bossa Nova catalog sold at least once — the only genre in the dataset 
where Revenue per Catalog Track equals Avg Revenue per Track. Worth confirming 
against raw data before presenting to leadership.

**Alternative vs. Alternative & Punk — catalog tagging flag:**
Alternative & Punk is #4 with $241.56 revenue while Alternative is #18 with 
$13.86. These may represent an inconsistent tagging convention in the source 
data rather than two genuinely distinct genre segments. If consolidated, the 
combined genre would rank solidly in the top 3.

**Rock vs. Rock And Roll — same issue:**
Rock is #1 with $826.65 revenue. Rock And Roll is #24 with $5.94. In most music 
catalogs, Rock And Roll is the parent genre of Rock, not a separate category. 
Worth flagging to the product team as a potential catalog organization issue.

---

**🔬 Check 6 — Meta-Verification: Where the Real Discovery Happened**

The AI surfaced several additional checks specific to genre benchmarking queries 
that use catalog depth. One of them caught a real error.

The AI recommended running this silent exclusion check:
```sql
SELECT g.Name, COUNT(t.TrackId) AS catalog_tracks
FROM Genre g
INNER JOIN Track t ON t.GenreId = g.GenreId
LEFT JOIN InvoiceLine il ON il.TrackId = t.TrackId
GROUP BY g.Name
HAVING SUM(il.Quantity) IS NULL;
```

**Result:**

| Name | catalog_tracks |
|------|---------------|
| Opera | 1 |

**The silent exclusion check caught a real gap.** Opera has 1 track in the catalog 
and zero sales. Because the original query used INNER JOIN all the way through 
Genre → Track → InvoiceLine, Opera was being silently dropped from the output 
entirely — never appearing in the benchmark, never appearing in the TOTAL row.

This created two specific problems:

1. **The TOTAL row understated catalog scope.** The query reported against 24 
   genres, but Chinook actually carries 25. Any framing like "across our full 
   catalog" would have been technically incorrect.

2. **Revenue per Catalog Track was slightly inflated.** Opera's unsold track 
   wasn't in any denominator, so the metric was only measuring genres that had 
   already proven commercial viability — it couldn't surface Opera-style problems 
   by design.

**The fix decision — Option A vs. Option B:**

The AI presented two options:
- **Option A:** Keep the INNER JOIN, add a comment noting that zero-sales genres 
  are excluded. Clean and defensible.
- **Option B:** Change the InvoiceLine JOIN to LEFT JOIN, use NULLIF and COALESCE 
  to handle zero-sales rows, and let Opera appear at the bottom with $0.00 values.

I chose **Option B.** For a report designed to inform catalog investment decisions, 
a genre sitting at $0.00 revenue with 1 catalog track is precisely the kind of 
finding that should surface — not be silently excluded. Dead catalog inventory is 
actionable information.

**The final aesthetic fix:**

After implementing Option B, I noticed the TOTAL row was showing NULL in the Rank 
column instead of a placeholder. A small thing — but attention to detail matters 
in a stakeholder report. I updated the UNION ALL total row to use `'—'` instead 
of NULL, which cleaned up the output.

---

**Final Query Results — 25 Genres + TOTAL:**

| Rank | Genre | Total Revenue | Tracks Sold | Avg Rev/Track | Global Avg | % of Total | Rev/Catalog Track |
|------|-------|---------------|-------------|---------------|------------|------------|-------------------|
| 1 | Rock | $826.65 | 835 | $0.99 | $1.04 | 35.5% | $0.64 |
| 2 | Latin | $382.14 | 386 | $0.99 | $1.04 | 16.4% | $0.66 |
| 3 | Metal | $261.36 | 264 | $0.99 | $1.04 | 11.2% | $0.70 |
| 4 | Alternative & Punk | $241.56 | 244 | $0.99 | $1.04 | 10.4% | $0.73 |
| 5 | TV Shows | $93.53 | 47 | $1.99 | $1.04 | 4.0% | $1.01 |
| 6 | Jazz | $79.20 | 80 | $0.99 | $1.04 | 3.4% | $0.61 |
| 7 | Blues | $60.39 | 61 | $0.99 | $1.04 | 2.6% | $0.75 |
| 8 | Drama | $57.71 | 29 | $1.99 | $1.04 | 2.5% | $0.90 |
| 9 | R&B/Soul | $40.59 | 41 | $0.99 | $1.04 | 1.7% | $0.67 |
| 10 | Classical | $40.59 | 41 | $0.99 | $1.04 | 1.7% | $0.55 |
| 11 | Sci Fi & Fantasy | $39.80 | 20 | $1.99 | $1.04 | 1.7% | $1.53 |
| 12 | Reggae | $29.70 | 30 | $0.99 | $1.04 | 1.3% | $0.51 |
| 13 | Pop | $27.72 | 28 | $0.99 | $1.04 | 1.2% | $0.58 |
| 14 | Soundtrack | $19.80 | 20 | $0.99 | $1.04 | 0.9% | $0.46 |
| 15 | Comedy | $17.91 | 9 | $1.99 | $1.04 | 0.8% | $1.05 |
| 16 | Hip Hop/Rap | $16.83 | 17 | $0.99 | $1.04 | 0.7% | $0.48 |
| 17 | Bossa Nova | $14.85 | 15 | $0.99 | $1.04 | 0.6% | $0.99 |
| 18 | Alternative | $13.86 | 14 | $0.99 | $1.04 | 0.6% | $0.35 |
| 19 | World | $12.87 | 13 | $0.99 | $1.04 | 0.6% | $0.46 |
| 20 | Science Fiction | $11.94 | 6 | $1.99 | $1.04 | 0.5% | $0.92 |
| 21 | Heavy Metal | $11.88 | 12 | $0.99 | $1.04 | 0.5% | $0.42 |
| 22 | Electronica/Dance | $11.88 | 12 | $0.99 | $1.04 | 0.5% | $0.40 |
| 23 | Easy Listening | $9.90 | 10 | $0.99 | $1.04 | 0.4% | $0.41 |
| 24 | Rock And Roll | $5.94 | 6 | $0.99 | $1.04 | 0.3% | $0.49 |
| 25 | Opera | $0.00 | 0 | $0.00 | $1.04 | 0.0% | $0.00 |
| — | TOTAL | $2,328.60 | 2,240 | — | — | 100.0% | — |

---

**Overall Verdict: Numbers are mathematically consistent and defendable — 
and the verification pass made the query meaningfully better.**

The math was correct from the start. But the silent exclusion check surfaced a 
real data completeness issue that no amount of arithmetic checking would have 
caught. Opera wasn't a calculation error — it was a design gap. The meta-prompt 
found it. The human made the call on how to fix it. That's the workflow working 
exactly as intended.

---

## The Business Insight

### Rock Is the Business — Treat It That Way

Rock represents 35.5% of total revenue. In power law terms, this is exactly 
what you'd expect — a small number of categories driving a disproportionate 
share of output. The strategic response isn't to diversify away from Rock. 
It's to go deeper.

The questions I'd want answered before the next planning cycle:

- **Which markets are driving Rock revenue?** Case Study 1 showed the USA 
  is our largest market overall — but is that true specifically for Rock, or 
  are there surprise markets where Rock over-indexes?
- **Who are our top Rock artists and top Rock buyers?** Do we have a customer 
  buyer persona for the ideal Rock customer — demographics, purchase patterns, 
  AOV? Both for current customers and potential acquisition targets?
- **Are there emerging Rock artists not yet in our catalog?** Catalog gaps in 
  our #1 revenue genre are a direct revenue leak.
- **What is Rock's YoY growth trend?** A genre representing 35.5% of revenue 
  that is growing is a very different strategic conversation than one that is 
  flat or declining. One, three, and five year trend lines would significantly 
  change how aggressively we invest in catalog expansion and marketing support 
  for this genre.

The concentration is healthy as long as it's growing. If Rock's share is 
declining, the 73.5% top-4 concentration becomes a risk conversation — not 
just a success story.

---

### The Top 4 Concentration — Healthy or Risky?

Rock, Latin, Metal, and Alternative & Punk represent 73.5% of total revenue 
combined. Whether that's healthy or risky depends entirely on trend direction.

If those four genres are growing year-over-year, concentration is a feature — 
it tells us where to focus resources and where the market is rewarding us. If 
they're flat or declining, 73.5% in four categories with no strong second tier 
emerging is a vulnerability. The remaining 21 genres represent only 26.5% of 
revenue combined — not enough of a cushion if the top 4 soften.

This is the strongest argument for building out the YoY analysis as a follow-up 
query. One, five, and ten year trend lines across all genres would transform this 
snapshot into a strategic roadmap.

---

### Sci Fi & Fantasy — The Hidden Opportunity

Sci Fi & Fantasy ranks #11 by total revenue but #1 by catalog efficiency at 
$1.53 per catalog track. Before drawing conclusions, that number needs context 
— video content is priced at $1.99 vs. $0.99 for music, so the comparison isn't 
perfectly apples-to-apples.

But even when compared only against other video genres, Sci Fi & Fantasy stands 
out. TV Shows generates $1.01 per catalog track. Drama generates $0.90. Comedy 
generates $1.05. Sci Fi & Fantasy at $1.53 is a significant outlier even within 
its own pricing tier.

That gap signals one of two things: either the catalog is very tight and highly 
curated, or customer demand for this genre significantly exceeds the current 
catalog depth. Either way, it's an opportunity worth investigating with the same 
framework applied to Rock — top titles, top buyers, geographic performance, and 
catalog gaps. If we can identify what's driving the efficiency and replicate it 
through targeted catalog expansion, this genre could move from #11 to a much 
higher revenue rank without requiring new customers.

---

### Video Content Investment — Get the COGS First

TV Shows, Drama, Comedy, Sci Fi & Fantasy, and Science Fiction all price at 
$1.99 — double the music track price. Their catalog efficiency figures are 
stronger than most music genres as a result. On the surface, this looks like 
a clear argument for investing more in video content.

But the surface is misleading without cost data. Video content licensing and 
acquisition costs are fundamentally different from music track costs. Before 
making any catalog investment decision in video, we need the COGS breakdown — 
what does it cost to license a TV Show episode vs. a music track? The higher 
price point only justifies more investment if the margin holds up. A genre 
generating $1.53 per catalog track at 20% margin is worth less than a genre 
generating $0.99 per catalog track at 70% margin.

This is the one question this dataset cannot answer on its own. It's also the 
right question to bring to a leadership conversation.

---

### Opera — Cost-Benefit Before Any Decision

Opera has 1 track in the catalog and zero sales. The instinct might be to remove 
it immediately — but the right first step is a cost analysis. What does it 
actually cost Chinook to carry this track? Licensing fees, catalog maintenance, 
storage overhead?

If the cost is negligible, there's no urgency to remove it — it's not hurting 
anything and removing it creates a small administrative task for no real gain. 
If there's a meaningful ongoing cost attached to it, that changes the calculus 
entirely. Zero revenue against any non-trivial cost is a straightforward 
cut decision.

The broader implication: Opera surfaced because the verification pass caught it 
as a silent exclusion. Without that check, we would have presented a 24-genre 
report to leadership and never known a 25th genre existed in the catalog. This 
is the practical value of a verification workflow — it doesn't just catch math 
errors, it catches completeness gaps that shape the entire framing of the analysis.

---

### Alternative — Catalog Pruning Conversation

Alternative ranks #18 with the worst catalog efficiency in the dataset at $0.35 
per catalog track. With approximately 40 tracks in the catalog and only 14 ever 
sold, the implied sell-through rate is around 35% — significantly below genres 
like Bossa Nova (100%) and Blues (~84%).

The question worth asking is whether the unsold Alternative tracks are genuinely 
unpopular or simply underpromoted. Before pruning the catalog, I'd want to know 
how much merchandising support these tracks have received. If they've never been 
featured in a recommendation engine, a promotional email, or a curated playlist, 
low sell-through isn't a signal of low demand — it's a signal of low visibility.

If they have been promoted and still aren't selling, then a targeted catalog 
reduction makes sense. Remove the bottom-performing titles, consolidate the 
Alternative and Alternative & Punk catalogs into a single genre label, and 
redirect the freed catalog capacity toward genres with proven demand.

---

### Bossa Nova — A Diversity Signal

Every single track in the Bossa Nova catalog has sold at least once. 100% 
sell-through across 15 tracks is a meaningful signal — it tells us there's 
a genuine, engaged audience for this genre even though it represents only 0.6% 
of total revenue.

This doesn't necessarily mean we should expand the Bossa Nova catalog 
aggressively. It means the current catalog is well-matched to existing demand. 
Before expanding, I'd want to understand whether demand exceeds supply — are 
customers searching for Bossa Nova content and not finding it? — or whether 
the current 15 tracks represent the natural ceiling for this genre's audience.

At a minimum, Bossa Nova is a good example of healthy genre diversity: a small, 
well-curated catalog serving a specific audience efficiently. That's a model 
worth applying to other underperforming genres before investing in catalog 
expansion.

---

### The YoY Dimension — What This Report Can't Tell Us Alone

Almost every insight in this report would be significantly sharpened by 
year-over-year trend data. Is Rock's 35.5% share growing or declining? Is 
Sci Fi & Fantasy's catalog efficiency improving as the catalog expands? Is 
the Global Avg Revenue per Track — our KPI for catalog-wide AOV — trending 
upward?

A one, five, and ten year trend analysis across all genres would transform 
this snapshot into a strategic planning tool. The current report answers 
"where are we now." The YoY analysis answers "where are we going" — and 
that's the question leadership actually makes budget decisions on.
