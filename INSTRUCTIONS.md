# Project Instructions for Cowork
Read this file at the start of every task. Also read SESSION_LOG.md for current progress.

**Who I am:**
I'm Daniel Matel-Okoh, a digital marketing professional with 8 years of 
experience (customer acquisition, retention, campaign optimization, CLV, ROAS, 
funnel analysis) transitioning into data analytics. I'm building a portfolio 
that demonstrates SQL, Python, and Tableau skills applied to real business 
problems.

**How I learn:**
I learn best going slow — one concept at a time, with space to ask questions 
and write things down before moving on. When teaching me something new:
- Introduce one idea at a time. Don't stack multiple new concepts.
- After explaining something, pause and ask if I want to try it before 
  moving to the next thing.
- Use the Chinook database for every example — no abstract or generic data.
- If I ask "why does this work?" give me the real explanation, not a 
  simplified version I'll have to unlearn later.
- If I'm about to make a mistake or miss something, say so directly.
- Don't assume I know Python terminology. If you use a term like "method" 
  or "argument" or "iterable," briefly explain what it means the first 
  time it comes up.

**What I've already built:**
A SQL analytics portfolio with three case studies on the Chinook SQLite database:
- Case Study 1: Geographic revenue analysis (CTEs, ROW_NUMBER, CROSS JOIN)
- Case Study 2: Customer lifetime value segmentation (CASE WHEN tiering, 
  PERCENT_RANK, multi-table JOINs)
- Case Study 3: Genre benchmarking with catalog efficiency (UNION ALL, 
  LEFT JOIN, benchmarking CTEs)

Each case study identified unanswered questions that require Python and 
Tableau to answer. The current project phase is building those answers.

**The database:**
I'm working with an expanded version of the Chinook SQLite database 
(`chinook_expanded.db`). It preserves all original Chinook data and adds 
synthetic records for analytical depth:
- ~5,000 total customers across 24+ countries
- The original 59 customers are preserved exactly as-is (CustomerIds 1–59) 
  and are referred to as the "legacy cohort" in the analysis. All original 
  invoices and invoice lines are unchanged. New synthetic records start above 
  the original max IDs.
- ~50,000+ invoices spanning 5–7 years
- ~200,000+ invoice lines
- Realistic seasonality (holiday spikes, summer dips)
- Variable purchase frequency (not uniform)
- Customer tenure variation (different start dates)
- Modest price evolution over time (in InvoiceLine.UnitPrice only — 
  Track.UnitPrice is unchanged from the original)
- Genre affinity patterns (customers have genre preferences — primary 
  genre = 40–60% of purchases)
- Customer churn (~15–25% of customers inactive in the final 12 months)
- Rock revenue share preserved at approximately 30–40% to maintain 
  consistency with SQL Case Study 3 findings

The original Chinook schema is unchanged:
- Customer (CustomerId, FirstName, LastName, Country)
- Invoice (InvoiceId, CustomerId, InvoiceDate, BillingCountry, Total)
- InvoiceLine (InvoiceLineId, InvoiceId, TrackId, UnitPrice, Quantity)
- Track (TrackId, Name, AlbumId, GenreId, UnitPrice)
- Genre (GenreId, Name)
- Album, Artist, MediaType, Playlist, PlaylistTrack (unchanged)

**My environment:**
- Mac (Python installed from python.org)
- Python in VS Code (Jupyter notebooks for analysis, .py files for scripts)
- Tableau Public for dashboards (data source: CSV files exported from the 
  database, stored in `tableau-data/` — Tableau Public cannot connect to 
  SQLite directly)
- SQLite for the database
- Libraries I'm using: pandas, numpy, matplotlib, seaborn, sqlite3 (built 
  into Python — no installation needed), faker
- Git for version control, GitHub for hosting the portfolio repository
- I'm learning Python — explain concepts clearly but don't over-simplify. 
  If I ask for code, make it readable and well-commented.

**My tools — Chat vs. Cowork:**
- I use **Claude Chat** (this session) for learning, Q&A, and working 
  through concepts step by step
- I use **Claude Cowork** for tasks that touch my actual project files — 
  creating notebooks, generating data, editing files, and multi-file 
  review during portfolio polish
- If a task would be better handled in Cowork (because it involves creating 
  or editing files), tell me and I'll switch
- On **"Chat + Cowork" days** (write-up days): I use Chat to discuss 
  findings and narrative framing, then switch to Cowork to write the 
  actual cells in the notebook

**My coding standards (carry these across all sessions):**
- Always add comments explaining *why*, not just *what*
- Use clear, descriptive variable names (not single letters)
- Structure notebooks with markdown headers separating each analysis step
- When writing SQL inside Python, use the same CTE + formatting conventions 
  from my SQL portfolio (CTEs over subqueries, PRINTF for currency in SQLite, 
  COALESCE for NULLs)
- All visualizations should have: title, axis labels, source note, and a 
  clean style (no default matplotlib grey background)
- When presenting findings, frame them through a marketing/business lens — 
  I'm not just describing what the data shows, I'm explaining what a 
  marketing team should do about it
- Each notebook follows the Notebook Template: Business Question → Setup → 
  Analysis Sections (each with intro, code, visualization, finding) → 
  Summary & Recommendations → Methodology Note (how AI was used) → 
  Next Steps

**What I'm building right now:**

[CURRENT PHASE: Option A — Setup + Data Generation]

(Keep all options below for reference. Update the line above when switching phases.)

**Option A — Setup + Data Generation (Days 31–42):**
I'm setting up my environment and building the synthetic data expansion 
script. The goal is to generate realistic customer, invoice, and invoice line 
data that preserves all original Chinook records and adds volume with realistic 
distributions, seasonality, churn, and genre affinity. Key constraints: price 
evolution applies to InvoiceLine.UnitPrice only (Track.UnitPrice stays 
unchanged), all foreign keys must be valid, new IDs start above the original 
max, and Rock revenue share should stay approximately 30–40%. The generation 
script should be well-documented and the assumptions should be explicitly 
stated in `assumptions.md`.

**Option B — Learning Python Fundamentals (Days 33–36, 43–48):**
I'm in the learning phase. I'm working through one concept at a time using 
the Chinook database. Topics include: sqlite3 + pandas basics, pandas 
exploration, Python scripting (loops, functions, random), writing to SQLite, 
datetime, groupby, merge, pivot tables, matplotlib, seaborn, rolling 
averages, and cohort analysis patterns. Go slow. One concept per exchange. 
Let me try things and ask questions before introducing the next idea. Don't 
give me a wall of code — give me one small piece, let me understand it, 
then build.

**Option C — Python Analysis: Purchase Behavior (Days 49–53):**
I'm building the purchase timing and frequency analysis. This answers the 
question raised in SQL Case Study 2: is the purchase frequency pattern 
organic, seasonal, or a data artifact? Deliverables: inter-purchase interval 
analysis, purchase date scatter plot (visual clustering inspection, not 
K-means), monthly revenue time series with trend line, cohort retention 
analysis.

**Option D — Python Analysis: Cross-Market Genre (Days 54–57):**
I'm building the cross-market genre analysis. This answers the question 
raised in SQL Case Studies 1 and 3: does Rock dominate everywhere, or are 
there markets where other genres over-index? Deliverables: genre × country 
pivot table, concentration ratios, genre co-purchase matrix (simple 
co-occurrence counts visualized as heatmap — not full market basket 
analysis), heatmap.

**Option E — Python Analysis: Genre Trends (Days 58–62):**
I'm building the genre revenue trend analysis. This answers the question 
raised in SQL Case Study 3: is Rock's 35.5% share growing or declining? 
Deliverables: monthly/yearly genre revenue trends, market share over time, 
catalog efficiency trends, cohort retention by genre affinity (define primary 
genre as most-purchased genre, compare retention curves for top 5 genres).

**Option F — Tableau Data Export (Day 66):**
I'm exporting data from `chinook_expanded.db` to CSV files for use in 
Tableau Public (which cannot connect to SQLite directly). Exporting: a 
flattened invoice-line-level file, a customer summary table, and a monthly 
revenue summary by genre and country. Files go in `tableau-data/`.

**Option G — Tableau Dashboard (Days 67–86):**
I'm building the Chinook Executive Dashboard in Tableau Public. Data source 
is the CSV files in `tableau-data/` (not the SQLite database — Tableau Public 
can't connect to SQLite). Three views: Geographic Performance (from CS1 + 
Python cross-market analysis), Customer Segmentation & Behavior (from CS2 + 
Python purchase behavior analysis), and Genre Performance & Trends (from CS3 + 
Python genre trends). Key Tableau concepts I need: dimensions vs. measures, 
filters, calculated fields, maps, parameters, dashboard actions, LOD 
expressions (especially FIXED for cohort assignment), continuous vs. discrete 
dates. Go slow on Tableau concepts — one feature at a time.

**Option H — Portfolio Polish (Days 88–92):**
I'm finalizing the portfolio. Updating the README to link all pieces in a 
clear progression, writing connective summaries, cleaning up code and 
notebooks, and ensuring consistent voice and formatting across all write-ups. 
Also verifying that the AI collaboration methodology notes are present in 
every deliverable. Final git push to make the GitHub repository complete.

---

**How I work with AI:**
- I use a structured prompt framework: Persona, Task, Context, Constraints, 
  Format, References, Audience, Evaluate
- I evaluate every output critically before accepting it
- I iterate with specific, numbered feedback — not vague "make it better"
- I verify outputs and use meta-prompts to surface checks I might not think of
- If something looks wrong, tell me — don't silently produce output that 
  looks correct but isn't

**What good output looks like from you:**
- Code that runs, is well-commented, and teaches me something
- Explanations that connect to business decisions, not just technical facts
- When I ask for analysis, structure the response as: finding → so what → 
  what to do next
- Flag tradeoffs explicitly — if there are two ways to do something, tell 
  me the pros and cons of each
- If I'm about to make a mistake or miss something, say so directly
- **When I'm learning:** go slow. One concept. One example. Let me try it. 
  Then the next one.
