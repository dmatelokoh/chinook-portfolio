# Chinook Portfolio Expansion — Project Brief
## Python + Tableau Projects Building on the SQL Foundation
**Daniel Matel-Okoh | Days 31–93**

---

## The Big Picture

The SQL portfolio (Case Studies 1–3) answered foundational business questions 
about Chinook's geographic revenue, customer lifetime value, and genre 
performance. But every case study ended with unanswered questions that SQL 
alone couldn't address — time-series patterns, cross-market distributions, 
churn signals, and trend analysis.

The next phase answers those questions. The Python project picks up where the 
SQL left off. The Tableau dashboard synthesizes everything into a stakeholder-ready 
tool. The connective thread is simple: each phase of analysis surfaced questions 
the current tools couldn't answer, which motivated the next phase.

By Day 93, the portfolio tells one continuous story across three tools — not 
five disconnected projects.

---

## How I Learn

I learn best going slow — small steps, one concept at a time, with space to 
ask questions and update my notes before moving on. This is not a crash course. 
Every day should have a single clear focus. If something takes longer than 
expected, that's fine — understanding matters more than speed.

**Rules for every learning day:**
- One new concept per session. Don't stack multiple new ideas.
- After each concept, pause and write it down in my own words before continuing.
- If something doesn't make sense, stop and ask — don't push through confusion.
- Build every exercise on the Chinook database. No generic tutorial data.
- End each day by writing a short note: what I learned, what's still fuzzy, 
  what I want to try tomorrow.
- **Checkpoint:** At the end of each learning day, try one small exercise 
  applying the concept without step-by-step guidance. If you can't do it 
  independently, spend more time before moving on.
- **Commit your work.** At the end of each working day, save your progress 
  to git with a short message describing what you did (see Git Workflow below).

---

## Tools I'm Using

**VS Code** — for writing Python scripts and Jupyter notebooks. All coding 
happens here.

**Claude Chat** — for learning, Q&A, and iterative problem-solving. This is 
where I ask questions, get code explained, and work through concepts step by 
step. I paste my context prime at the start of each session.

**Claude Cowork** — for tasks that touch my actual project files. Cowork runs 
in the Claude Desktop app and has direct access to a folder on my computer. 
Instead of copy-pasting between Claude chat and my file system, I point Cowork 
at my project folder and let it read, create, and edit files directly.

**When to use Chat vs. Cowork:**
- **Chat** when I'm learning something new and want to go slow with explanations
- **Chat** when I want to understand *why* something works, not just get it done
- **Cowork** when I have a clear task that involves creating or editing actual 
  files in my project folder (generating data, creating notebooks, organizing 
  outputs)
- **Cowork** when I need Claude to read multiple files in my project at once 
  (like checking consistency across case studies during portfolio polish)

**On "Chat + Cowork" days (write-up days):** Use Chat to discuss findings, 
narrative structure, and business framing. Then switch to Cowork to write the 
actual markdown and code cells in the notebook. Chat is for thinking; Cowork 
is for editing files.

**Tableau Public** — for the capstone dashboard. Free, shareable via link. 
**Note:** All workbooks saved to Tableau Public are publicly visible. This is 
fine for portfolio work, but be aware before saving any in-progress work.

**Git + GitHub** — for version control and publishing your portfolio. You'll 
use git from Day 31 as a daily habit, not as a separate project to learn. 
The commands you need fit on one hand (see Git Workflow below).

**Usage limits:** This plan assumes a Claude Pro subscription. If you hit 
usage limits during a Cowork session, switch to Chat for the remainder of that 
day's work. If you're consistently hitting limits, consider upgrading to Max 
for the duration of the project.

---

## Git Workflow — Daily Habit, Not a Separate Project

Git tracks every change you make to your files. GitHub is where those changes 
live online so hiring managers can see your work. You don't need to learn git 
deeply — you need three commands and one daily habit.

**The three commands you'll use every day:**
```bash
git add .                          # Stage all changed files
git commit -m "Day 34: wrote assumptions.md"   # Save with a message
git push                           # Upload to GitHub
```

**The daily habit:** At the end of each working day, run those three commands 
in Terminal from your project folder. The commit message should be one sentence 
describing what you did. That's it. No branches, no pull requests, no merge 
conflicts.

**What this gives you:**
- A public GitHub profile with 90+ commits showing daily, consistent progress
- Backup of your work — if your laptop dies, everything is on GitHub
- Evidence that you built the portfolio incrementally, not all at once
- A signal to hiring managers that you work the way data teams work

**Rules:**
- Commit at the end of every working day, even if the day's work is incomplete
- Push to GitHub at least once per week (or after finishing each deliverable)
- Commit messages should be short and specific: "Day 41: data validation 
  checklist — all 10 checks passing" not "updated files"
- Never commit the database file (`chinook_expanded.db`) — it's too large 
  for GitHub. The `.gitignore` file handles this automatically. Instead, 
  your README explains how to regenerate it from the generation script.

---

## Cowork Setup (Do This on Day 31)

1. Download or update the Claude Desktop app from claude.com/download
2. Open the app and click the "Cowork" tab at the top
3. Create a project folder on your computer: `~/Documents/chinook-portfolio/`
4. In Cowork settings, grant Claude access to this folder only — nothing else
5. Inside that folder, create a file called `INSTRUCTIONS.md` with your 
   coding standards and project context (use the context prime as a starting 
   point — Cowork will read this file automatically)
6. Also create a `SESSION_LOG.md` file — update this at the end of every 
   Cowork session with: what was completed, what's in progress, what's next. 
   This helps Cowork pick up where you left off if a session is interrupted.
7. Test it: ask Cowork to "Read the files in this folder and tell me what 
   you see." Make sure it can access your existing SQL case study files.

**Important Cowork notes:**
- Cowork has no memory between sessions — it starts fresh every time. 
  That's why INSTRUCTIONS.md and SESSION_LOG.md matter: Cowork reads them 
  at the start of each task.
- The Claude Desktop app must stay open while Cowork is working.
- Start with read access to your project folder. Only grant write access 
  when you're ready for Cowork to create or edit files.
- Cowork burns through usage limits faster than chat. Use it for real 
  tasks, not for learning and Q&A.
- **Update INSTRUCTIONS.md** at each phase transition: entering Phase 0 
  (data generation), Phase 1 (Python analysis), Phase 2 (Tableau), and 
  Portfolio Polish. Update the "What I'm building right now" option at the 
  start of each deliverable block.
- **If a Cowork session is interrupted** (usage limits, crash, etc.): update 
  SESSION_LOG.md with where you stopped, then start a new session. Cowork 
  will read the log and pick up from there.

---

## Phase 0: Setup + Synthetic Data Expansion (Days 31–42)

### Why

The original Chinook database has 59 customers and $2,328 in total revenue. 
That's too small to support meaningful statistical analysis, realistic 
segmentation, or time-series work. Before starting the Python project, build 
a synthetic expansion that preserves all original data while adding enough 
volume for real analytics.

### Target Scale

- ~5,000 customers (original 59 preserved as "legacy cohort")
- ~50,000+ invoices spanning 5–7 years
- ~200,000+ invoice lines
- All original tracks, genres, albums, and artists preserved

### What the Synthetic Data Must Include

**Realistic geographic distribution.** Weight customer creation toward 
existing markets (US, Canada, France, Brazil, Germany) but include long-tail 
countries. Not uniform — the US should have significantly more customers 
than Denmark.

**Time depth with seasonality.** Invoice dates should span multiple years 
with observable patterns — holiday spending spikes (Nov–Dec), summer dips, 
and a general upward trend in transaction volume over time.

**Variable purchase frequency.** Most customers buy 3–8 times, a small 
percentage buy 15+, and some buy once and never return.

**Customer tenure variation.** Different start dates — some joined in year 1, 
some joined last quarter.

**Price evolution.** Price changes apply to `InvoiceLine.UnitPrice` only — 
the `Track.UnitPrice` column remains unchanged to preserve compatibility with 
the original SQL portfolio. Tracks that were $0.99 in earlier years might be 
$1.29 or $1.49 in later invoice lines. Video content can move from $1.99 to 
$2.49.

**Genre purchase patterns.** A customer who buys Rock is more likely to also 
buy Metal and Alternative & Punk than Bossa Nova.

**Customer churn.** Some customers stop purchasing entirely after a period of 
activity.

### Target Parameters (refine these in assumptions.md on Day 37)

These are starting points — adjust during planning, but document every change:
- **Genre affinity strength:** A customer's primary genre should represent 
  40–60% of their purchases. Secondary genres 20–30%. Remaining genres make 
  up the rest.
- **Churn rate:** 15–25% of customers should have no purchases in the most 
  recent 12 months of the data.
- **Rock revenue share:** Approximately 30–40% of total revenue in the 
  expanded data, consistent with the SQL Case Study 3 finding (~35.5%). The 
  genre rank order (Rock > Latin > Metal > Alternative, etc.) should be 
  approximately preserved. Exact percentages will shift with scale, but if 
  Rock drops below Latin, the SQL case study narrative breaks.
- **ID ranges:** New CustomerIds start above `MAX(CustomerId)` from the 
  original data. Same for InvoiceId and InvoiceLineId. Never overwrite or 
  duplicate original IDs.
- **Foreign key integrity:** Every `Invoice.CustomerId` must reference an 
  existing `Customer.CustomerId`. Every `InvoiceLine.InvoiceId` must reference 
  an existing `Invoice.InvoiceId`. Every `InvoiceLine.TrackId` must reference 
  an existing `Track.TrackId`.

### Day-by-Day Breakdown

| Day | Focus | What I'm Doing | Tool |
|-----|-------|----------------|------|
| 31 | Environment setup + git init | Install VS Code and the Python extension. Install Python from python.org/downloads (not Homebrew — avoids PATH issues on Mac). Verify by running `python3 --version` in Terminal. Install packages: `pip3 install pandas numpy matplotlib seaborn faker`. Create project folder `~/Documents/chinook-portfolio/`. **Git:** Run `git --version` to confirm git is installed. Run `git init` in the project folder. Create `.gitignore` (see below). Copy SQL case study files into the project folder. First commit: `git commit -m "Day 31: initial project structure + SQL case studies"`. | VS Code + Terminal |
| 32 | Cowork setup + GitHub | Download Claude Desktop app. Set up Cowork with project folder access. Create `INSTRUCTIONS.md` and `SESSION_LOG.md`. Test Cowork can read files. Write and run a test script: `import sqlite3; conn = sqlite3.connect('chinook.db'); print(conn.execute('SELECT COUNT(*) FROM Customer').fetchone())`. Confirm it prints `(59,)`. **Git:** Create a GitHub account (if needed). Create a new repository called `chinook-portfolio`. Connect and push: `git remote add origin https://github.com/[username]/chinook-portfolio.git && git push -u origin main`. | VS Code + Cowork + Terminal |
| 33 | Learn: sqlite3 + pandas basics | Connect to Chinook from Python. Run one simple query. Load results into a pandas DataFrame. Just those three things. **Checkpoint:** Without looking at examples, write a query that loads the Genre table into a DataFrame and prints it. | Chat (learning) |
| 34 | Learn: pandas exploration | Use `.head()`, `.describe()`, `.shape()`, `.value_counts()` to explore the original Chinook tables. Write down what I notice. **Checkpoint:** Use `.value_counts()` to find the top 5 countries by number of customers. | Chat (learning) |
| 35 | Learn: Python scripting basics | Learn `for` loops, defining functions with `def`, and the `random` module (`random.choice`, `random.choices` with weights, `random.gauss`). Exercise: write a function that generates a random customer record (name, country, join date) using weighted random selection for country. | Chat (learning) |
| 36 | Learn: Writing to SQLite + datetime | Learn `INSERT` statements from Python, `DataFrame.to_sql()`, and `datetime.timedelta` for generating date ranges. Learn the `faker` library for realistic name generation. Exercise: insert 10 generated customer records into a test database and verify they appear. | Chat (learning) |
| 37 | Plan the synthetic data | Write `assumptions.md` — document every decision about distributions, seasonality, churn rates, pricing, genre affinity. Use the Target Parameters above as starting points. No code yet. Just the plan. | Chat (planning) |
| 38 | Build: customer generation | Write the script that generates new customers with realistic country distribution and tenure variation. Test it. Check the output. | Cowork (file creation) |
| 39 | Build: invoice generation | Generate invoices with seasonality, variable frequency, and customer-level purchase patterns. Link each invoice to a valid CustomerId. | Cowork (file creation) |
| 40 | Build: invoice line generation | Generate invoice lines with genre affinity, price evolution, and valid TrackIds. Link each line to a valid InvoiceId. Calculate and set `Invoice.Total` as the sum of its lines. | Cowork (file creation) |
| 41 | Verify + finalize | Run the generation script end-to-end. Execute the **Data Validation Checklist** (below). Fix any issues. Export `chinook_expanded.db`. **Git:** Commit and push: `git commit -m "Day 41: synthetic data generation complete — all validation checks passing" && git push`. | Cowork (verification) |
| 42 | Buffer | Catch up on data generation if anything ran long. If not needed, run additional spot checks or rest. | — |

### .gitignore File (Create on Day 31)

```
# Database files (too large for GitHub — regenerate from script)
*.db

# Python cache
__pycache__/
*.pyc

# Jupyter notebook checkpoints
.ipynb_checkpoints/

# OS files
.DS_Store
Thumbs.db

# Tableau workbook backups
*.twbx~
```

### Data Validation Checklist (Day 41)

Run these checks before moving to Phase 1. All must pass:
1. `SELECT COUNT(*) FROM Customer` returns approximately 5,000
2. `SELECT COUNT(*) FROM Customer WHERE CustomerId <= 59` returns exactly 59 
   (original customers preserved)
3. `SELECT COUNT(*) FROM Invoice` returns approximately 50,000+
4. `SELECT COUNT(*) FROM InvoiceLine` returns approximately 200,000+
5. Every `InvoiceLine.TrackId` exists in the Track table: 
   `SELECT COUNT(*) FROM InvoiceLine WHERE TrackId NOT IN (SELECT TrackId FROM Track)` returns 0
6. Every `Invoice.CustomerId` exists in the Customer table: 
   `SELECT COUNT(*) FROM Invoice WHERE CustomerId NOT IN (SELECT CustomerId FROM Customer)` returns 0
7. Nov–Dec monthly invoice counts are visibly higher than Jun–Jul: 
   `SELECT strftime('%m', InvoiceDate) AS month, COUNT(*) FROM Invoice GROUP BY 1 ORDER BY 1`
8. Rock revenue share is between 30% and 40% of total revenue
9. `Track.UnitPrice` values are unchanged from the original database
10. No duplicate or overlapping IDs between original and synthetic records

### Fallback Plan

If data generation is not working after Day 42, don't stay stuck:
- **Option 1:** Simplify the dataset. Drop genre affinity and price evolution. 
  Generate customers + invoices + invoice lines with volume and seasonality 
  only. These two features are "nice to have" — the core analyses can work 
  without them.
- **Option 2:** Use Claude Chat to generate the entire script. Walk through 
  each section for understanding, then run it in VS Code. This is slower for 
  learning but gets the data built.
- **Option 3:** Ask Claude to generate the data directly in a Cowork session 
  (Cowork can run the script and iterate on fixes in real time).

### Deliverables

- `chinook_expanded.db` — the expanded SQLite database (excluded from GitHub 
  via `.gitignore` — README explains how to regenerate from script)
- `data_generation/generate_synthetic_data.py` — the generation script
- `data_generation/assumptions.md` — documented assumptions

### Portfolio Note

Label the expanded data transparently in the README: *"The original Chinook 
database was too small for meaningful statistical analysis. I built a synthetic 
expansion preserving all original data while adding [X] customers and [Y] 
transactions with realistic seasonality, churn, and price variation. The 
database is excluded from this repository due to file size — run 
`python data_generation/generate_synthetic_data.py` to regenerate it."*

---

## Phase 1: Python Project (Days 43–66)

### Project Title

**"Chinook Purchase Behavior & Market Analysis"**

### Connective Thread to SQL Portfolio

| SQL Case Study | Unanswered Question | Python Deliverable |
|----------------|--------------------|--------------------|
| CS1 (Geographic) | Is Rock revenue concentrated in the US or distributed? | Cross-market genre analysis |
| CS2 (CLV) | Are purchase dates clustered? Is the uniform frequency a real pattern? | Purchase timing & frequency analysis |
| CS2 (CLV) | Is Puja Srivastava a new customer or a disengaged one? | Customer cohort & tenure analysis |
| CS3 (Genre) | What's the YoY trend for Rock's 35.5% revenue share? | Genre revenue trend analysis |
| CS3 (Genre) | Is Sci Fi & Fantasy's catalog efficiency improving over time? | Catalog efficiency trends |

### Notebook Template

Every Python notebook should follow this structure for consistency:
1. **Business Question** — markdown cell connecting this analysis to the SQL 
   case study it extends. What question are we answering and why?
2. **Setup** — import libraries, connect to database, load data
3. **Analysis sections** — each with: a markdown intro explaining the approach, 
   code cells, visualizations, and a markdown "Finding" cell stating what the 
   data shows
4. **Summary & Recommendations** — markdown cell with business framing. Not 
   just "what the data shows" but "what a marketing team should do about it"
5. **Methodology Note** — brief description of how AI was used in this 
   analysis: what was delegated, what was verified manually, what was revised
6. **Next Steps** — what this analysis suggests exploring next (connects 
   forward to subsequent deliverables or the Tableau dashboard)

### Deliverable 1: Purchase Timing & Frequency Analysis (Days 49–53)

**Question:** Is the purchase frequency pattern organic, seasonal, promotional, 
or a data artifact?

**Scope:**
- Pull invoice dates by customer, calculate inter-purchase intervals
- Plot purchase frequency distributions (histogram)
- Purchase date scatter plot — plot all invoice dates on a timeline; visually 
  inspect for clustering around specific months or days; calculate % of annual 
  revenue in Q4 vs. other quarters
- Monthly revenue time series — plot monthly revenue over time to visually 
  identify seasonal patterns (formal statistical decomposition is out of scope; 
  visual inspection with trend lines is sufficient)
- Cohort analysis — group customers by first purchase quarter, compare 
  retention and average spend across cohorts; do newer customers behave 
  differently from legacy ones?

**Skills demonstrated:** pandas datetime operations, groupby, merge, 
matplotlib/seaborn visualization, descriptive statistics

### Deliverable 2: Cross-Market Genre Analysis (Days 54–57)

**Question:** Does Rock dominate everywhere, or are there markets where other 
genres over-index?

**Scope:**
- Genre revenue by country — pivot table
- Concentration ratios — what % of each country's revenue comes from its 
  top genre?
- Genre co-purchase matrix — for each genre, count how many customers who 
  purchased Genre A also purchased Genre B; visualize as a heatmap (this is 
  a simple co-occurrence count, not a full association rules / market basket 
  analysis)
- Heatmap visualization — genre × country revenue matrix

**Skills demonstrated:** pivot tables, merge operations, cross-tabulation, 
heatmap visualization

### Deliverable 3: Genre Revenue Trends & Catalog Efficiency Over Time (Days 58–62)

**Question:** Is Rock's 35.5% share growing or declining?

**Scope:**
- Monthly and yearly revenue by genre — line charts showing trend direction
- Market share over time — is Rock's share stable, growing, or eroding?
- Catalog efficiency trends — revenue per catalog track by genre over time
- Cohort retention by genre affinity — define each customer's primary genre 
  as their most-purchased genre; compare retention curves across the top 5 
  genres (what % of Rock-primary customers are still active after 6 months 
  vs. Metal-primary customers?)

**Skills demonstrated:** time-series analysis, rolling averages, trend 
visualization, cohort analysis

### Day-by-Day Breakdown

| Day | Focus | What I'm Doing | Tool |
|-----|-------|----------------|------|
| 43 | Learn: pandas groupby | Group Chinook data by country. Calculate sums, means, counts. One operation at a time. **Checkpoint:** Without looking at examples, write a groupby that shows total revenue per genre, sorted descending. | Chat |
| 44 | Learn: pandas merge | Merge two DataFrames (like Customer + Invoice). Understand left, right, inner joins in pandas. **Checkpoint:** Merge Customer, Invoice, and InvoiceLine into one DataFrame. Check row count to confirm the join type is correct. | Chat |
| 45 | Learn: pandas pivot tables | Create a pivot table of genre revenue by country. Just the table — no visualization yet. **Checkpoint:** Create a pivot showing average invoice total by country and year. | Chat |
| 46 | Learn: matplotlib basics | Make one bar chart. Learn figure, axes, title, labels. Style it so it doesn't look like default matplotlib. **Checkpoint:** Make a horizontal bar chart of the top 10 genres by revenue, with axis labels and a title. | Chat |
| 47 | Learn: seaborn, datetime, rolling averages | Make one heatmap. Parse dates with pandas. Extract month and year from InvoiceDate. Learn `.rolling()` — calculate the 3-month rolling average of monthly revenue. **Checkpoint:** Plot monthly revenue as a line chart with a 3-month rolling average overlaid. | Chat |
| 48 | Learn: Jupyter notebooks + cohort analysis | Create a new Jupyter notebook in VS Code (learn how cells work — code vs. markdown, how to run cells, how to use markdown headers). Then work through a guided cohort analysis exercise: identify each customer's first purchase quarter, assign to cohorts, calculate how many customers in each cohort purchased again in the next quarter. Display as a table. | Chat |
| 49 | Build: Deliverable 1 (part 1) | Pull invoice dates, calculate inter-purchase intervals. Plot frequency histogram. | Cowork |
| 50 | Build: Deliverable 1 (part 2) | Purchase date scatter plot. Monthly revenue time series with trend line. | Cowork |
| 51 | Build: Deliverable 1 (part 3) | Cohort analysis — group customers by first purchase quarter. Build retention table. Compare cohort behavior. | Cowork |
| 52 | Write: Deliverable 1 | Write up findings in the notebook following the Notebook Template. Connect back to Case Study 2. Export key figures. Use Chat to discuss narrative, then Cowork to edit the notebook. | Chat + Cowork |
| 53 | Review: Deliverable 1 | Review the notebook end-to-end. Does it tell a clear story? Fix anything unclear. Update AI collaboration log. **Git:** `git commit -m "Day 53: Deliverable 1 complete — purchase behavior analysis" && git push` | Chat |
| 54 | Build: Deliverable 2 (part 1) | Genre × country pivot table. Calculate concentration ratios by market. | Cowork |
| 55 | Build: Deliverable 2 (part 2) | Genre co-purchase matrix. Heatmap visualization. | Cowork |
| 56 | Write: Deliverable 2 | Write up findings following the Notebook Template. Connect back to Case Studies 1 and 3. Use Chat to discuss narrative, then Cowork to edit. | Chat + Cowork |
| 57 | Review: Deliverable 2 | Review end-to-end. Fix anything unclear. Update AI collaboration log. **Git:** `git commit -m "Day 57: Deliverable 2 complete — cross-market genre analysis" && git push` | Chat |
| 58 | Build: Deliverable 3 (part 1) | Monthly genre revenue trends. Market share over time. | Cowork |
| 59 | Build: Deliverable 3 (part 2) | Catalog efficiency trends. Churn analysis by genre affinity. | Cowork |
| 60 | Build: Deliverable 3 (part 3) | Rolling averages. Multi-axis plotting (secondary y-axis for market share %). | Cowork |
| 61 | Write: Deliverable 3 | Write up findings following the Notebook Template. Connect back to Case Study 3. Use Chat to discuss narrative, then Cowork to edit. | Chat + Cowork |
| 62 | Review: Deliverable 3 | Review end-to-end. Update AI collaboration log. **Git:** `git commit -m "Day 62: Deliverable 3 complete — genre trends analysis" && git push` | Chat |
| 63 | Buffer day | Catch up on anything that ran long. Or rest. | — |
| 64 | Python project cleanup | Clean up all three notebooks. Consistent headers, comments, figure labels. Ensure all notebooks follow the Notebook Template. | Cowork |
| 65 | Python README | Write the Python project README with connections to SQL case studies. | Chat |
| 66 | Export Tableau-ready data | Export key tables from `chinook_expanded.db` as CSV files into a `tableau-data/` folder. At minimum: (1) a flattened invoice-line-level file joining Customer, Invoice, InvoiceLine, Track, Genre, and Album; (2) a customer summary table with CLV, first purchase date, last purchase date, and primary genre; (3) a monthly revenue summary by genre and country. Test that the CSVs load correctly in a spreadsheet. **Git:** `git commit -m "Day 66: Python phase complete + Tableau data exports" && git push` | Cowork |

### Python Project File Structure

```
chinook-portfolio/
├── .gitignore                 (excludes .db files, caches, OS files)
├── sql-case-studies/          (existing SQL work)
├── python-analysis/
│   ├── notebooks/
│   │   ├── 01_purchase_behavior.ipynb
│   │   ├── 02_cross_market_genre.ipynb
│   │   └── 03_genre_trends.ipynb
│   ├── output/
│   │   ├── figures/
│   │   └── summary_tables/
│   └── README.md
├── data_generation/
│   ├── generate_synthetic_data.py
│   └── assumptions.md
├── tableau-data/              (CSV exports for Tableau)
├── chinook_expanded.db        (excluded from GitHub — regenerate from script)
├── INSTRUCTIONS.md            (Cowork reads this)
├── SESSION_LOG.md             (Cowork session continuity)
└── README.md                  (master portfolio README)
```

---

## Phase 2: Tableau Dashboard (Days 67–93)

### Project Title

**"Chinook Executive Dashboard"**

### Important: Tableau Public Data Source

Tableau Public cannot connect to SQLite databases directly. The data was 
exported to CSV files on Day 66 (stored in `tableau-data/`). All Tableau 
work uses these CSVs as the data source. If you need additional data or 
different aggregations, go back to Python to export new CSVs.

### Dashboard Structure: 3 Interactive Views

**View 1 — Geographic Performance**
- Country revenue map, top markets table, country-level genre mix drill-down
- Sources: CS1 + Python Deliverable 2

**View 2 — Customer Segmentation & Behavior**
- Tier distribution, CLV scatter plot, cohort retention curves
- Sources: CS2 + Python Deliverable 1

**View 3 — Genre Performance & Trends**
- Genre revenue ranking with catalog efficiency, trend lines, market share over time
- Sources: CS3 + Python Deliverable 3

### Day-by-Day Breakdown

| Day | Focus | What I'm Doing | Tool |
|-----|-------|----------------|------|
| 67 | Setup | Install Tableau Public. Import the CSV files from `tableau-data/`. Explore the data source pane — learn how to join multiple CSVs if needed. | Tableau |
| 68 | Learn: basic charts | Make one bar chart. Learn dimensions vs. measures, rows vs. columns. | Tableau + Chat |
| 69 | Learn: filters + colors | Add a country filter. Color-code by revenue. Learn the Marks card. | Tableau + Chat |
| 70 | Learn: calculated fields | Create one calculated field (e.g., revenue per customer). | Tableau + Chat |
| 71 | Learn: maps | Build a country map with revenue shading. | Tableau + Chat |
| 72 | Build: View 1 (part 1) | Country revenue map + top markets table. | Tableau |
| 73 | Build: View 1 (part 2) | Add genre mix drill-down and concentration metrics. | Tableau |
| 74 | Review: View 1 | Does it answer the Case Study 1 questions? Polish formatting. | Tableau + Chat |
| 75 | Learn: parameters, actions, LOD expressions | Learn how dashboard actions work (click a country → filter another sheet). Learn FIXED LOD expressions — build a simple example: calculate each customer's first purchase date using `{FIXED [CustomerId] : MIN([InvoiceDate])}`, then use it as a dimension. | Tableau + Chat |
| 76 | Build: View 2 (part 1) | Tier distribution and CLV scatter plot. | Tableau |
| 77 | Build: View 2 (part 2) | Cohort retention curves (using the FIXED LOD for first purchase date). | Tableau |
| 78 | Review: View 2 | Does it answer the Case Study 2 questions? Polish formatting. | Tableau + Chat |
| 79 | Learn: date-based analysis | Learn continuous vs. discrete dates. Build a simple trend line. | Tableau + Chat |
| 80 | Build: View 3 (part 1) | Genre revenue ranking with catalog efficiency. | Tableau |
| 81 | Build: View 3 (part 2) | Revenue trends by genre. Market share stacked area chart. | Tableau |
| 82 | Review: View 3 | Does it answer the Case Study 3 questions? Polish formatting. | Tableau + Chat |
| 83 | Buffer day | Catch up on anything that ran long. If not needed, watch a Tableau dashboard design best-practices video. | — |
| 84 | Dashboard assembly | Combine three views into one dashboard. Add cross-filtering interactivity. | Tableau |
| 85 | Dashboard polish | Formatting, colors, fonts, consistent style. Mobile layout. | Tableau |
| 86 | Publish | Publish to Tableau Public. Test sharing links. Update AI collaboration log with Tableau phase examples. **Git:** `git commit -m "Day 86: Tableau dashboard published" && git push` | Tableau |
| 87 | Buffer day | Catch up or rest. | — |
| 88 | Portfolio polish: SQL files | Re-read all SQL case studies. Flag anything inconsistent with the expanded data findings. | Cowork |
| 89 | Portfolio polish: Python files | Re-read all notebooks. Consistent headers, labels, voice. Verify all notebooks follow the Notebook Template. | Cowork |
| 90 | Portfolio polish: README + connections | Update master README to link all pieces in progression (see structure below). Write connective summaries between phases. Add Tableau Public link. Add note about how to regenerate the database. This may take two days — if so, use Day 91 as overflow. | Cowork + Chat |
| 91 | Portfolio polish: final read | Read the entire portfolio top to bottom as a hiring manager would. Fix anything that breaks the narrative flow. | Cowork |
| 92 | Buffer day | Final fixes. **Git:** Final commit and push: `git commit -m "Day 92: portfolio complete" && git push` | — |
| 93 | Done. | — | — |

---

## Portfolio Polish — Final README Structure

The master README must include at minimum:
- A portfolio summary (who you are, what this demonstrates)
- A progression table linking all phases
- One-paragraph descriptions of each project with links to the relevant files
- A note on the synthetic data expansion and why it was necessary
- Instructions for regenerating the database (`python data_generation/generate_synthetic_data.py`)
- A link to the live Tableau Public dashboard
- A note on AI collaboration methodology

```
## Portfolio Progression

| Phase | Tool | Project | What It Answers |
|-------|------|---------|-----------------|
| 1 | SQL | Case Studies 1–3 | Where is revenue? Who are our best customers? What's selling? |
| 2 | Python | Purchase Behavior & Market Analysis | When do customers buy? Where do genres over-index? What's trending? |
| 3 | Tableau | Executive Dashboard | How does it all come together for a decision-maker? |
```

> *"Each phase of analysis surfaced questions the current tools couldn't 
> answer, which motivated the next phase — from SQL foundations, to Python 
> for behavioral and trend analysis, to Tableau for stakeholder-ready 
> visualization."*

---

## Success Criteria

By Day 93, the portfolio should demonstrate:

- **SQL:** Query design, business logic, data verification (already done)
- **Python:** Data generation, manipulation, statistical analysis, visualization
- **Tableau:** Interactive dashboards, stakeholder-ready presentation
- **Business thinking:** Every analysis connects to a decision a marketing 
  team would actually make
- **AI collaboration:** Documented, transparent, judgment-driven workflow — 
  maintained throughout all three phases with representative examples in 
  each deliverable's methodology note
- **Technical workflow:** Version-controlled with git, hosted on GitHub, 
  reproducible (database can be regenerated from script)
- **Progression:** One continuous story, not disconnected projects
