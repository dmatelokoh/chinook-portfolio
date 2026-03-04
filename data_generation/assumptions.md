# Synthetic Data Expansion — Assumptions & Design Decisions

**Author:** Daniel Matel-Okoh
**Date:** March 2026
**Purpose:** Document every decision made before writing `generate_synthetic_data.py`.
All choices below are informed by the Phase 0 Target Parameters in the project brief.

---

## 1. Preservation Rules

The original Chinook database is treated as immutable. Every record in every table
is copied into `chinook_expanded.db` exactly as-is before any synthetic data is added.

- **Original customers (CustomerIds 1–59):** Unchanged. Referred to as the "legacy cohort."
- **Original invoices (InvoiceIds 1–412):** Unchanged.
- **Original invoice lines (InvoiceLineIds 1–2,240):** Unchanged.
- **Track, Genre, Album, Artist, MediaType, Playlist, PlaylistTrack:** Copied verbatim.
  No new tracks, genres, albums, or artists are created.
- **Track.UnitPrice:** Never modified. Only two values exist ($0.99 and $1.99) and they
  stay exactly as they are. Price evolution applies only to InvoiceLine.UnitPrice
  (see Section 8).

---

## 2. ID Ranges

New synthetic records start above the original max IDs to guarantee no collisions.

| Table        | Original Max ID | Synthetic IDs Start At |
|--------------|----------------:|----------------------:|
| Customer     |              59 |                    60 |
| Invoice      |             412 |                   413 |
| InvoiceLine  |           2,240 |                 2,241 |

IDs are assigned sequentially with no gaps.

---

## 3. Target Scale

| Metric            | Original | Target (Expanded)    |
|-------------------|----------|----------------------|
| Customers         |       59 | ~5,000 total         |
| Invoices          |      412 | ~50,000+             |
| Invoice lines     |    2,240 | ~200,000+            |
| Date range        | 2021-01 to 2025-12 | 2019-01 to 2025-12 (7 years) |

**New synthetic customers:** ~4,941 (bringing total to ~5,000).

**Date range rationale:** Extending backward to 2019 gives 7 full years. The original
data runs 2021–2025; synthetic customers can have join dates starting as early as
2019-01-01. This provides enough time depth for cohort analysis and trend detection.

---

## 4. Customer Generation

### 4a. Country Distribution

Weighted toward existing major markets, with a long tail of smaller countries.
The distribution is modeled on the original Chinook proportions, amplified slightly
for the US and other large markets to feel realistic for a digital music store.

| Country          | Approx. Weight | Expected Customers |
|------------------|---------------:|-------------------:|
| USA              |          22.0% |            ~1,085  |
| Canada           |          10.0% |              ~495  |
| Brazil           |           8.5% |              ~420  |
| France           |           8.0% |              ~395  |
| Germany          |           7.0% |              ~345  |
| United Kingdom   |           6.0% |              ~295  |
| Portugal         |           3.5% |              ~175  |
| Czech Republic   |           3.0% |              ~150  |
| India            |           3.0% |              ~150  |
| Australia        |           2.5% |              ~125  |
| Argentina        |           2.0% |              ~100  |
| Spain            |           2.0% |              ~100  |
| Italy            |           2.0% |              ~100  |
| Netherlands      |           1.5% |               ~75  |
| Chile            |           1.5% |               ~75  |
| Poland           |           1.5% |               ~75  |
| Ireland          |           1.5% |               ~75  |
| Sweden           |           1.5% |               ~75  |
| Belgium          |           1.5% |               ~75  |
| Norway           |           1.5% |               ~75  |
| Finland          |           1.0% |               ~50  |
| Denmark          |           1.0% |               ~50  |
| Austria          |           1.0% |               ~50  |
| Hungary          |           1.0% |               ~50  |
| (Others — 4-5 additional countries) | ~2.0% | ~100 |

"Others" includes countries like Mexico, Japan, South Africa, and Colombia to add
geographic variety without overcomplicating the distribution.

### 4b. Customer Names

Generated using the `faker` library with locale matching the customer's country
(e.g., `faker.Faker('pt_BR')` for Brazil). This produces culturally appropriate
first and last names.

### 4c. Customer Tenure (Join Dates)

Each customer's "join date" is the date of their first invoice. Join dates are
distributed across the full 7-year window with a slight forward skew — more
customers join in later years, reflecting a growing platform.

| Period     | Approx. % of New Customers |
|------------|---------------------------:|
| 2019       |                        8%  |
| 2020       |                       10%  |
| 2021       |                       13%  |
| 2022       |                       16%  |
| 2023       |                       19%  |
| 2024       |                       20%  |
| 2025       |                       14%  |

2025 is lower because customers joining late in 2025 would have very few invoices,
so the script biases toward earlier join dates where there's room for purchase history.

---

## 5. Invoice Generation

### 5a. Purchase Frequency

Each customer is assigned a "purchase intensity" drawn from a gamma distribution,
which naturally produces the desired shape: most customers buy a moderate number
of times, a few buy heavily, and some buy rarely.

| Frequency Tier     | Invoices per Customer | Approx. % of Customers |
|--------------------|-----------------------|-----------------------:|
| One-and-done       | 1                     |                   10%  |
| Low frequency      | 2–4                   |                   30%  |
| Moderate frequency | 5–10                  |                   40%  |
| High frequency     | 11–20                 |                   15%  |
| Power buyers       | 21+                   |                    5%  |

**Implementation:** Draw from `Gamma(shape=2.5, scale=3.5)`, round to integer,
clip to [1, 35]. This gives a median around 7–8 purchases per customer and a
long right tail.

### 5b. Invoice Timing

Invoices are spaced across a customer's active period (from join date to either
their churn date or the end of the data).

- **Inter-purchase intervals:** Drawn from a log-normal distribution
  (`mean=3.5, sigma=0.6` in log-space), producing intervals centered around
  30–40 days with variance. Some gaps are a few days; some are several months.
- **Day-of-month:** Uniformly random (1–28 to avoid month-length issues).

### 5c. Seasonality

Monthly purchase probability is scaled by a seasonality multiplier applied to
the likelihood of a purchase occurring in that month:

| Month | Multiplier | Rationale                        |
|-------|------------|----------------------------------|
| Jan   |       0.95 | Post-holiday dip                 |
| Feb   |       0.85 | Low season                       |
| Mar   |       0.90 | Slight recovery                  |
| Apr   |       0.90 | Baseline                         |
| May   |       0.95 | Baseline                         |
| Jun   |       0.80 | Summer dip begins                |
| Jul   |       0.75 | Deepest summer dip               |
| Aug   |       0.80 | Summer dip continues             |
| Sep   |       0.90 | Back-to-school recovery          |
| Oct   |       1.00 | Building toward holidays         |
| Nov   |       1.25 | Black Friday / holiday shopping  |
| Dec   |       1.35 | Christmas / year-end peak        |

**Implementation:** When generating each invoice date, accept/reject based on
the month's multiplier relative to the maximum (1.35). This means ~100% of
December dates are kept and ~56% of July dates are kept, creating visible
seasonality without deterministic patterns.

### 5d. Year-over-Year Growth

A gentle volume multiplier increases transaction density over time:

| Year | Volume Multiplier |
|------|------------------:|
| 2019 |              0.70 |
| 2020 |              0.80 |
| 2021 |              0.90 |
| 2022 |              1.00 |
| 2023 |              1.05 |
| 2024 |              1.10 |
| 2025 |              1.10 |

This ensures the time series shows a visible upward trend without making
early years look empty.

---

## 6. Invoice Line Generation

### 6a. Lines per Invoice

The number of line items per invoice is drawn from a distribution matching
the original data's range (1–14 lines, average ~5.4):

- Drawn from `Poisson(lambda=4.5)` + 1 (minimum 1 line), capped at 14.
- This produces a mean around 5.5 lines per invoice, consistent with the original.

### 6b. Track Selection and Genre Affinity

Each customer is assigned a **genre affinity profile** at creation time:

1. **Primary genre:** Selected via weighted random choice (weights proportional
   to original genre revenue shares — see Section 7). Represents 40–60% of the
   customer's purchases.
2. **Secondary genre:** Selected from genres adjacent to the primary (see
   affinity matrix in Section 7). Represents 20–30% of purchases.
3. **Remaining genres:** All other purchases are drawn from the full track catalog
   with a mild bias toward popular genres. Represents 15–35% of purchases.

**Track selection within a genre:** When a genre is chosen for a line item,
a track is selected uniformly at random from all tracks in that genre.

### 6c. Invoice Total

`Invoice.Total` is calculated as the sum of `(UnitPrice * Quantity)` across all
its invoice lines. This is computed after all lines are generated, not set independently.

### 6d. Quantity

All invoice lines have `Quantity = 1`. This matches the original data where
every single invoice line has Quantity = 1.

---

## 7. Genre Distribution and Affinity

### 7a. Target Genre Revenue Shares

The expanded data must preserve the original rank order. Rock must remain the
top genre at 30–40% of total revenue.

| Genre               | Original Share | Target Share (Expanded) |
|---------------------|---------------:|------------------------:|
| Rock                |         35.5%  |               32–36%    |
| Latin               |         16.4%  |               14–17%    |
| Metal               |         11.2%  |               10–12%    |
| Alternative & Punk  |         10.4%  |                9–11%    |
| TV Shows            |          4.0%  |                3–5%     |
| Jazz                |          3.4%  |                3–4%     |
| Blues               |          2.8%  |                2–4%     |
| Drama               |          2.4%  |                2–3%     |
| R&B/Soul            |          2.2%  |                2–3%     |
| Electronica/Dance   |          1.5%  |                1–2%     |
| (Remaining 15)      |         10.2%  |                8–12%    |

**Implementation:** Genre weights for primary genre assignment are set
proportional to these target shares, with Rock weighted slightly above its
natural share to compensate for dilution from random track picks.

### 7b. Genre Affinity Matrix (Simplified)

When selecting a secondary genre, use these adjacency groups:

| Primary Genre       | Likely Secondary Genres                    |
|---------------------|--------------------------------------------|
| Rock                | Metal, Alternative & Punk, Blues            |
| Metal               | Rock, Alternative & Punk                   |
| Alternative & Punk  | Rock, Metal, Pop                           |
| Latin               | Pop, R&B/Soul, Reggae, World               |
| Jazz                | Blues, Bossa Nova, R&B/Soul                 |
| Blues                | Rock, Jazz, R&B/Soul                       |
| Pop                 | Rock, R&B/Soul, Latin, Electronica/Dance   |
| R&B/Soul            | Pop, Jazz, Hip Hop/Rap, Latin              |
| TV Shows            | Drama, Sci Fi & Fantasy, Comedy            |
| Drama               | TV Shows, Sci Fi & Fantasy                 |
| Classical           | Soundtrack, Jazz, Easy Listening           |
| Electronica/Dance   | Pop, Alternative & Punk, Hip Hop/Rap       |
| (Others)            | Draw from any genre proportionally          |

**Thin-catalog exclusion rule:** Any genre with fewer than 10 tracks is excluded
from all secondary genre assignments. At the invoice volumes being generated,
a secondary genre with a tiny catalog would produce implausible track concentration
(e.g., one track accounting for a disproportionate share of genre revenue).

Applying this rule to the current catalog:

| Genre | Tracks | Excluded from affinity matrix? |
|-------|-------:|-------------------------------|
| Opera |      1 | Yes — only 1 track            |
| (All others) | 12+ | No — catalog depth is sufficient |

**Opera specifically:** Removed from Classical's secondary list and not referenced
anywhere else in the affinity matrix. The one Opera track will still appear
organically in the ~15–35% random-draw portion of any customer's purchases, but
at a rate consistent with its catalog size rather than as a targeted secondary pick.

**Bossa Nova (16 tracks):** Above the threshold. Left in the Jazz adjacency group
as a conscious choice — the Jazz/Bossa Nova adjacency is musically accurate, and
16 tracks is enough catalog depth at these volumes. Worth monitoring in validation
if genre-level track concentration analysis is run later.

---

## 8. Price Evolution

Price changes apply **only to InvoiceLine.UnitPrice**. Track.UnitPrice is never
modified.

The concept: as years pass, the store raises prices slightly on the same tracks.
A track listed at $0.99 in the Track table might appear in an InvoiceLine at
$1.29 in later years.

| Year  | Audio Track Price | Video/TV Price |
|-------|------------------:|---------------:|
| 2019  |            $0.99  |         $1.99  |
| 2020  |            $0.99  |         $1.99  |
| 2021  |            $0.99  |         $1.99  |
| 2022  |            $1.09  |         $2.19  |
| 2023  |            $1.19  |         $2.29  |
| 2024  |            $1.29  |         $2.39  |
| 2025  |            $1.49  |         $2.49  |

**Audio vs. video distinction:** Tracks with `Track.UnitPrice = 0.99` are audio;
tracks with `Track.UnitPrice = 1.99` are video/TV content. The price evolution
table above applies based on this original price tier.

**Note:** Original invoice lines (InvoiceLineIds 1–2,240) are untouched. Their
UnitPrices remain exactly as recorded, even if they would be "wrong" under this
evolution schedule. Only newly generated invoice lines use the evolved prices.

---

## 9. Customer Churn

**Target:** 15–25% of all customers should have no purchases in the most recent
12 months of data (January 2025 – December 2025).

### Implementation

Each customer is assigned a churn probability at creation time:

- **70% of customers** are "active" — they can purchase throughout the entire
  date range and have no forced churn.
- **20% of customers** are "at-risk" — they have a 50% chance of churning at a
  randomly selected point during their active period, after which no more invoices
  are generated.
- **10% of customers** are "short-lived" — they churn within 6–18 months of
  their join date.

The combined effect should produce an overall churn rate of ~20% (within the
15–25% target). "One-and-done" customers (Section 5a) naturally contribute to
the churned pool as well.

**Churn definition for validation:** A customer is "churned" if their most recent
invoice date is before 2025-01-01.

---

## 10. Foreign Key Integrity

Every foreign key relationship must be valid in the expanded database:

- `Invoice.CustomerId` → must exist in `Customer.CustomerId`
- `InvoiceLine.InvoiceId` → must exist in `Invoice.InvoiceId`
- `InvoiceLine.TrackId` → must exist in `Track.TrackId`
- `Invoice.BillingCountry` → matches the customer's `Country` field

No orphaned records. The generation script validates these constraints before
writing to the database.

---

## 11. Other Fields

### Customer Table

| Field       | Value                                                  |
|-------------|--------------------------------------------------------|
| FirstName   | faker-generated, locale-appropriate                    |
| LastName    | faker-generated, locale-appropriate                    |
| Company     | NULL (optional — ~20% of customers get a company name) |
| Address     | faker-generated                                        |
| City        | faker-generated, locale-appropriate                    |
| State       | faker-generated where applicable (US, Canada, Brazil)  |
| PostalCode  | faker-generated                                        |
| Phone       | faker-generated                                        |
| Fax         | NULL (deprecated field)                                |
| Email       | faker-generated                                        |
| SupportRepId| Randomly assigned from existing employee IDs (3, 4, 5) |

### Invoice Table

| Field          | Value                                            |
|----------------|--------------------------------------------------|
| BillingAddress | Same as customer's Address                       |
| BillingCity    | Same as customer's City                          |
| BillingState   | Same as customer's State                         |
| BillingPostalCode | Same as customer's PostalCode                 |
| BillingCountry | Same as customer's Country                       |
| Total          | Computed sum of invoice lines (UnitPrice * Qty)  |

---

## 12. Random Seed

The generation script uses `random.seed(42)` and `np.random.seed(42)` at the
start for reproducibility. Running the script twice produces identical output.

---

## 13. Validation Checklist (from Project Brief)

Before the data is accepted, all 10 checks must pass:

1. Total customers ≈ 5,000
2. Original 59 customers preserved (CustomerIds 1–59)
3. Total invoices ≈ 50,000+
4. Total invoice lines ≈ 200,000+
5. All InvoiceLine.TrackId values exist in Track table
6. All Invoice.CustomerId values exist in Customer table
7. Nov–Dec invoice counts visibly higher than Jun–Jul
8. Rock revenue share between 30% and 40%
9. Track.UnitPrice values unchanged from original
10. No duplicate or overlapping IDs between original and synthetic

---

## 14. What Is NOT Included

To keep the scope manageable, the following are explicitly out of scope:

- **No new tracks, albums, artists, or genres.** Synthetic data only adds
  customers, invoices, and invoice lines referencing existing tracks.
- **No playlist modifications.** The Playlist and PlaylistTrack tables are
  copied as-is.
- **No employee changes.** The Employee table is copied as-is.
- **No geographic migration.** A customer's country never changes.
- **No refunds or negative transactions.** All invoices represent purchases.
- **No promotional pricing or discounts.** Price evolution is the only
  price variation mechanism.
