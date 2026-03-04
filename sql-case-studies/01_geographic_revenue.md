
# Case Study 1: Where Is the Revenue Coming From?
## Geographic Revenue Analysis

---

## The Business Question

Chinook operates as a digital media store selling music tracks and albums globally. 
Before making any decisions about where to invest in marketing or customer acquisition, 
leadership needs to understand the geographic landscape of our revenue.

**The core question:** Which geographic markets should Chinook prioritize for growth 
and customer acquisition — and are we over-investing in markets where we're already saturated?

This is not just a "show me a ranked list" request. The goal is to understand:
- Where is revenue concentrated?
- Which markets have high revenue but low customer counts (high value per customer)?
- How dependent is the business on any single market?

---

## The Prompt I Gave the AI

Rather than asking vaguely for "revenue by country," I used a structured prompt framework 
to ensure the AI had everything it needed to return something useful the first time.

---

**🧠 Persona**
> Act as a senior data analyst who writes clean, well-commented SQL for business stakeholders — not just code that runs, but code that can be read and maintained by others.

**🎯 Task**
> Write a SQL query that returns total revenue by country, number of unique customers per country, and average revenue per customer — sorted by total revenue descending.

**📋 Context**
> I'm working in the Chinook SQLite database. The relevant tables are Invoice (columns: InvoiceId, CustomerId, BillingCountry, Total) and Customer (column: CustomerId). Every invoice is tied to a customer via CustomerId.

**🚧 Constraints**
> - This is SQLite — do not use FORMAT(), TOP, or ISNULL. Use PRINTF(), LIMIT, and COALESCE instead.
> - Use INNER JOIN, not LEFT JOIN — I only want countries where purchases actually occurred.
> - Do not use reserved words like `avg` or `total` as aliases.

**📐 Format**
> Return a single clean SELECT statement. Use clear column aliases. Format all currency columns with PRINTF('$%.2f', ...). Add brief inline comments explaining key decisions.

**📎 References**
> Follow the same CTE structure and alias style used in standard business intelligence reporting — readable top-to-bottom, with each logical step named.

**👥 Audience**
> The output will be reviewed by a non-technical marketing director. Column names should be self-explanatory. No raw decimals. No cryptic aliases.

**✅ Evaluate**
> I'll check the first draft for: correct join type, no SQLite-incompatible functions, readable aliases, formatted currency, and whether the output actually answers the business question — not just runs without errors.

---

## How This Prompt Was Built

My first instinct was a one-liner:

> *"Using the Chinook database, write me a SQL query that shows revenue by country, 
> number of customers, and average spend. Sort by revenue descending."*

That would return something, but not something presentable — raw decimals, weak aliases, 
no comments, no awareness of SQLite's limitations. So before writing my actual prompt, 
I asked the AI for a reusable prompt framework for technical tasks. It returned the 
eight-part structure (Persona, Task, Context, Constraints, Format, References, Audience, 
Evaluate) that I used to rebuild my request from scratch.

The before/after speaks for itself — same underlying ask, completely different quality 
of output.

---

## The AI's Raw Output

To demonstrate why prompt structure matters, I ran two versions of the same request.

**First — a generic, unstructured prompt:**
> *"Write me a SQL query that shows revenue by country, number of customers, 
> and average spend. Sort by revenue descending."*

The AI returned this:
```sql
SELECT BillingCountry, 
       SUM(Total) as total, 
       COUNT(DISTINCT CustomerId) as customers, 
       SUM(Total)/COUNT(DISTINCT CustomerId) as avg
FROM Invoice
GROUP BY BillingCountry
ORDER BY total DESC;
```

**The output looked like this:**

| BillingCountry | total | customers | avg |
|----------------|-------|-----------|-----|
| USA | 523.0600000000003 | 13 | 40.23538... |
| Canada | 303.9599999999999 | 8 | 37.99499... |
| France | 195.09999999999994 | 5 | 39.01999... |
| Brazil | 190.09999999999997 | 5 | 38.01999... |

It runs. It's directionally correct. But it would never go in front of a marketing 
director as-is — raw floating point decimals, no ranking, no percentage of total, 
no comments, and a reserved word (`avg`) used as an alias.

---

**Then — using my structured prompt framework:**

After applying the Persona, Task, Context, Constraints, Format, References, Audience, 
and Evaluate framework, the AI returned a materially better first draft:
```sql
-- ============================================================
-- Revenue Summary by Country
-- Source: Chinook SQLite Database
-- Purpose: Help marketing understand revenue and customer
--          concentration across geographic markets
-- ============================================================

WITH country_metrics AS (
    SELECT
        i.BillingCountry                            AS country,
        SUM(i.Total)                                AS revenue_raw,
        COUNT(DISTINCT c.CustomerId)                AS unique_customers,
        SUM(i.Total) / COUNT(DISTINCT c.CustomerId) AS avg_revenue_raw
    FROM Invoice AS i
        INNER JOIN Customer AS c
            ON i.CustomerId = c.CustomerId
    GROUP BY i.BillingCountry
)

SELECT
    country                                             AS "Country",
    PRINTF('$%.2f', COALESCE(revenue_raw, 0))          AS "Total Revenue",
    unique_customers                                    AS "Unique Customers",
    PRINTF('$%.2f', COALESCE(avg_revenue_raw, 0))      AS "Avg Revenue per Customer"
FROM country_metrics
ORDER BY revenue_raw DESC;
```

This is a meaningful step up. The CTE is clean, the join logic is correct, currency 
is formatted, and the comments explain the decisions. The difference wasn't the AI 
getting smarter — it was the quality of the input I gave it.

But after running this and reviewing the output, I still had notes.

---

## My Critical Evaluation

The structured prompt produced a solid first draft — but "solid" still wasn't "done." 
This is the part of the AI workflow that I think gets undervalued: the human review pass.

Here's exactly what I flagged:

**1. No ranking column**
The output sorts by revenue descending, but there's no explicit rank number. In a 
report, a reader should be able to instantly see "USA is #1, Canada is #2" without 
counting rows manually. I added ROW_NUMBER() OVER (ORDER BY revenue DESC).

**2. No percentage of total revenue**
Raw revenue numbers tell me who's biggest, but not how concentrated the business is. 
If the USA represents 22% of total revenue, that's a very different strategic 
conversation than if it represents 60%. The AI didn't calculate this because I didn't 
explicitly ask for it — a reminder that AI answers the question you ask, not the 
question you should have asked.

**3. No global revenue benchmark**
To calculate percentage of total, I needed a second CTE capturing the grand total 
revenue across all countries. The AI's version had no mechanism for this — adding it 
required restructuring the query with an additional CTE and a CROSS JOIN pattern.

**4. Floating point noise**
Values like `523.0600000000003` are a SQLite artifact. PRINTF('$%.2f') fixes the 
display, and the AI applied it correctly — but only because I specified it explicitly 
in my prompt. Without that constraint, it wouldn't have been there.

**5. No comment header block**
The AI added inline comments, which was good. But there was no formal header block 
identifying the case study, business question, skills used, and author. That's a 
professional standard for any query that lives in a shared repo.

**6. No total orders column**
I wanted to see not just how many unique customers each country has, but how many 
total orders they placed. Orders-per-customer is a loyalty signal — a country with 
5 customers and 35 orders is behaving very differently from one with 5 customers 
and 6 orders. I added COUNT(i.InvoiceId) AS total_orders.

**The bottom line:** The structured prompt got me to a strong 65% in a fraction of 
the time it would have taken me to write from scratch. The remaining 35% — the ranking, 
the percentage of total, the global benchmark CTE, the total orders column, the header 
block — came from knowing what a marketing director actually needs to see. The AI 
couldn't have added those without being told.

---

## Iterative Prompting — From V1 to V2

After completing my evaluation, I reformatted my notes as a structured feedback prompt 
and fed them back to the AI — letting it incorporate my changes while preserving 
everything it already got right.

**The feedback prompt I sent:**

> *"The query you returned was a strong first draft, but I have specific feedback I need 
> you to incorporate. Please update the query with the following changes:*
>
> *1. **Add a ranking column** — Use ROW_NUMBER() OVER (ORDER BY revenue DESC) to add 
> an explicit rank number as the first column.*
>
> *2. **Add percentage of total revenue** — Add a column showing each country's revenue 
> as a percentage of total global revenue, rounded to 2 decimal places using ROUND(..., 2).*
>
> *3. **Add a global revenue benchmark CTE** — Add a second CTE that captures grand total 
> revenue using SUM(Total), then use a CROSS JOIN to make that value available in the 
> final SELECT.*
>
> *4. **Add a total orders column** — Use COUNT(InvoiceId) to capture every order placed 
> per country, including repeat purchases. Place it immediately after Unique Customers so 
> readers can compare headcount vs. order volume directly.*
>
> *5. **Confirm currency formatting is applied to all money columns** — Use PRINTF('$%.2f') 
> on every column that contains a dollar amount.*
>
> *6. **Add a formal comment header block** at the top of the query in this exact format:*
> ```
> -- ============================================
> -- Case Study 1: Geographic Revenue Analysis
> -- Business Question: [question here]
> -- Skills: [list skills used]
> -- Author: Daniel Matel-Okoh
> -- AI Partner: Claude / Gemini
> -- ============================================
> ```
> *Do not change anything else about the query structure — keep the existing CTE, 
> join logic, aliases, and inline comments exactly as they are."*

---

**The V2 Query — AI Output After Prompt Chaining:**
```sql
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
        SUM(i.Total)                                            AS revenue_raw,
        COUNT(DISTINCT i.CustomerId)                            AS unique_customer_count,
        COUNT(i.InvoiceId)                                      AS total_orders,
        SUM(i.Total) / COUNT(DISTINCT i.CustomerId)             AS avg_revenue_per_customer_raw
    FROM Invoice AS i
        INNER JOIN Customer AS c
            ON i.CustomerId = c.CustomerId
    GROUP BY
        i.BillingCountry
),
global_totals AS (
    SELECT
        SUM(Total) AS global_revenue_raw
    FROM Invoice
)
SELECT
    ROW_NUMBER() OVER (ORDER BY cm.revenue_raw DESC)              AS "Rank",
    cm.country                                                    AS "Country",
    PRINTF('$%.2f', COALESCE(cm.revenue_raw, 0))                  AS "Total Revenue",
    cm.unique_customer_count                                      AS "Unique Customers",
    cm.total_orders                                               AS "Total Orders",
    PRINTF('$%.2f', COALESCE(cm.avg_revenue_per_customer_raw, 0)) AS "Avg Revenue Per Customer",
    ROUND((cm.revenue_raw / gt.global_revenue_raw) * 100.0, 2)   AS "% of Global Revenue"
FROM
    country_metrics AS cm
    CROSS JOIN global_totals AS gt
ORDER BY
    cm.revenue_raw DESC;
```

**What the prompt chaining achieved:**

| | V1 (Initial AI Output) | V2 (After Prompt Chaining) |
|---|---|---|
| Ranking column | ❌ | ✅ ROW_NUMBER() |
| % of global revenue | ❌ | ✅ ROUND(..., 2) |
| Global benchmark CTE | ❌ | ✅ CROSS JOIN pattern |
| Total orders column | ❌ | ✅ COUNT(InvoiceId) |
| Float division fix (100.0) | ❌ | ✅ AI inferred this edge case |
| Comment header block | ❌ | ✅ Full header |
| Currency formatting | ✅ | ✅ |
| Correct join type | ✅ | ✅ |
| Inline comments | ✅ | ✅ |

One thing worth noting: the AI added `100.0` instead of `100` in the percentage 
calculation to force float division in SQLite — an edge case I didn't explicitly 
specify, but that my feedback prompt gave it enough context to reason through. 
That's the compounding value of precise prompting.

---

**V2 Query Results:**

| Rank | Country | Total Revenue | Unique Customers | Total Orders | Avg Rev/Customer | % of Global Revenue |
|------|---------|---------------|------------------|--------------|------------------|---------------------|
| 1 | USA | $523.06 | 13 | 91 | $40.24 | 22.46% |
| 2 | Canada | $303.96 | 8 | 56 | $37.99 | 13.05% |
| 3 | France | $195.10 | 5 | 35 | $39.02 | 8.38% |
| 4 | Brazil | $190.10 | 5 | 35 | $38.02 | 8.16% |
| 5 | Germany | $156.48 | 4 | 28 | $39.12 | 6.72% |
| 6 | United Kingdom | $112.86 | 3 | 21 | $37.62 | 4.85% |
| 7 | Czech Republic | $90.24 | 2 | 14 | $45.12 | 3.88% |
| 8 | Portugal | $77.24 | 2 | 14 | $38.62 | 3.32% |
| 9 | India | $75.26 | 2 | 13 | $37.63 | 3.23% |
| 10 | Chile | $46.62 | 1 | 7 | $46.62 | 2.00% |
| 11 | Hungary | $45.62 | 1 | 7 | $45.62 | 1.96% |
| 12 | Ireland | $45.62 | 1 | 7 | $45.62 | 1.96% |
| 13 | Austria | $42.62 | 1 | 7 | $42.62 | 1.83% |
| 14 | Finland | $41.62 | 1 | 7 | $41.62 | 1.79% |
| 15 | Netherlands | $40.62 | 1 | 7 | $40.62 | 1.74% |
| 16 | Norway | $39.62 | 1 | 7 | $39.62 | 1.70% |
| 17 | Sweden | $38.62 | 1 | 7 | $38.62 | 1.66% |
| 18 | Argentina | $37.62 | 1 | 7 | $37.62 | 1.62% |
| 19 | Australia | $37.62 | 1 | 7 | $37.62 | 1.62% |
| 20 | Belgium | $37.62 | 1 | 7 | $37.62 | 1.62% |
| 21 | Denmark | $37.62 | 1 | 7 | $37.62 | 1.62% |
| 22 | Italy | $37.62 | 1 | 7 | $37.62 | 1.62% |
| 23 | Poland | $37.62 | 1 | 7 | $37.62 | 1.62% |
| 24 | Spain | $37.62 | 1 | 7 | $37.62 | 1.62% |

---

## Verification Pass — AI Self-Check + Meta-Prompting

Before drawing any business conclusions from this data, I ran a structured verification 
pass. Rather than just trusting the output, I prompted the AI to check its own work 
against the raw numbers.

I also added a sixth question that applies meta-prompting to quality control:

> *"Beyond the five checks above, what other verification methods would you recommend 
> to ensure this query output is accurate and trustworthy? Think about this from the 
> perspective of a senior data analyst who needs to defend these numbers to a leadership team."*

Asking the AI to reason about *how* to verify — not just *whether* the numbers are correct 
— surfaces checks I might not have thought to run myself.

---

**Verification Results:**

**✅ Check 1 — Percentages sum to ~100%**
All 24 country percentages sum to 100.03%. The 0.03% gap comes from independently 
rounding each row to 2 decimal places — display artifact, not a data error.

**✅ Check 2 — Global revenue back-calculation**
Back-calculating from USA's percentage: $523.06 ÷ 0.2246 = $2,328.84. The known Chinook 
Invoice total is $2,328.60. The $0.24 variance is entirely explained by rounding the 
percentage to 2 decimal places. Mathematically consistent.

**✅ Check 3 — USA average revenue per customer**
$523.06 ÷ 13 customers = $40.2354... → formatted to $40.24. Exact match confirmed.

**✅ Check 4 — Row count completeness**
Output has 24 rows. Chinook has customers from 24 countries with completed invoices. 
The INNER JOIN correctly excluded registered customers with no purchase history without 
silently dropping any active market.

**⚠️ Check 5 — Anomaly scan**
Chile ($46.62), Czech Republic ($45.12), and Hungary ($45.62) show average revenue 
per customer 14–18% above the global average of $39.47. These are not data errors — 
they are small-sample effects. Each of those countries has only 1–2 customers, so a 
single high-value invoice moves the average significantly. No real anomalies detected.

---

**🔬 Check 6 — Meta-Verification: What Else Should We Check?**

The AI's response to the meta-prompt surfaced six additional checks a senior analyst 
would run before presenting to leadership. Two are worth highlighting:

**Duplicate invoice guard:**
> Run `SELECT InvoiceId, COUNT(*) FROM Invoice GROUP BY InvoiceId HAVING COUNT(*) > 1`
>
> If any InvoiceId appears more than once, SUM(Total) is silently inflated. This is 
> the most common revenue inflation bug in aggregation queries.

**NULL billing country audit:**
> Run `SELECT COUNT(*) FROM Invoice WHERE BillingCountry IS NULL`
>
> Any invoices with a NULL country are excluded from all country rows AND from the 
> global total CTE — meaning percentages could sum to less than 100% and the grand 
> total would be understated silently.

I ran both checks against the Chinook database. No duplicate invoices. No NULL billing 
countries. The data is clean.

---

**Overall Verdict: Numbers are mathematically consistent and defendable.**

The meta-prompting addition was particularly valuable: the duplicate invoice check and 
NULL audit are exactly the kind of defensive checks that separate a junior analyst 
("the query ran") from a senior analyst ("the query ran and I can prove the numbers are right").

---

## The Business Insight

### The Top-Line Story: Three Markets Drive the Business

The USA (22.46%), Canada (13.05%), and France (8.38%) are the only markets above 8% 
of global revenue — together they account for nearly 44% of total revenue from 24 
countries. Every other market is under 9% individually. For a marketing team allocating 
budget, that's a clear signal: these three markets are where the business lives.

But "biggest" and "best opportunity" are not the same thing. The strategic question 
for each market is different.

---

### USA — Monetize Deeper, Not Wider

The USA is the dominant market by every metric: most customers (13), most orders (91), 
highest total revenue ($523.06). But the average revenue per customer ($40.24) is 
actually below the global average for mid-size markets like Czech Republic ($45.12) 
and Chile ($46.62). That's a flag.

In digital marketing terms, this is a classic penetration vs. monetization problem. 
We have the audience. We're not maximizing yield from it. Before spending another 
dollar on US customer acquisition, I'd want to answer two questions:

1. **What's the genre distribution of US purchases?** If 80% of US revenue comes from 
   2-3 genres, that's the 80/20 signal — and it tells us exactly where to focus 
   merchandising, recommendations, and promotional spend.
2. **Can we apply US genre insights to Canada?** The two markets share significant 
   cultural and demographic overlap. If Rock and Alternative dominate in the US, 
   there's a reasonable hypothesis that the same push in Canada — our #2 market — 
   could lift revenue per customer there too. This is the kind of cross-market 
   insight that makes regional marketing efficient.

The next logical analysis from this query is a US-specific genre breakdown — which 
is exactly what Case Study 3 addresses.

---

### Czech Republic — A Small Market Worth Watching

With only 2 customers, the Czech Republic has the highest average revenue per customer 
($45.12) of any multi-customer market. Sample size is too small to draw conclusions — 
but in a digital marketing context, this is the kind of signal you put on a watchlist, 
not in a press release.

If Czech Republic customer counts grow and the AOV holds, this becomes a high-value 
emerging market worth targeted acquisition investment. If it was one high-spending 
customer pulling the average up, that's a different conversation — one about retention 
and whale protection, not acquisition.

---

### The Missing Metric: Orders-to-Customer Ratio

One column I'd add in the next iteration is the percentage of total orders coming 
from unique customers — essentially an orders-per-customer ratio by country. 
The current data shows us *that* the USA has 91 orders from 13 customers (7.0 
orders/customer) and France has 35 orders from 5 customers (7.0 orders/customer) 
— but we can't see this directly without calculating it manually.

This metric matters because a country with a disproportionately high orders-per-customer 
ratio likely has "whale" customers — individuals driving outsized purchase volume. 
Whales deserve different treatment than average customers: early access, loyalty 
perks, direct relationship management. Identifying them is a retention priority, 
not just a reporting curiosity.

A follow-up query calculating `total_orders / unique_customers` per country and 
flagging any market more than 1 standard deviation above the mean would surface 
these markets immediately.

---

### Revenue Concentration Is a Vulnerability

The top 3 markets (USA, Canada, France) represent 44% of revenue. The bottom 15 
markets — each with a single customer — collectively represent about 25%. That's 
15 markets where one customer churning means that market goes to $0.

In marketing portfolio terms, this is dangerous concentration. A competitor entering 
the US market aggressively, a licensing change in North America, or even a single 
large US customer churning would have outsized impact on the business. A healthy 
revenue portfolio looks more like the bottom of this table — many small contributors 
— not the top.

The strategic recommendation isn't to abandon the US. It's to deliberately invest 
in growing the mid-tier markets (Germany, UK, Brazil) where there are already 
multiple customers and a foundation to build on — reducing dependency on any single 
geography over time.
