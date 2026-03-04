
--

Day 32 — Cowork Setup + Database Connection Test
What I did

Downloaded the original Chinook SQLite database from GitHub (lerocha/chinook-database)
Renamed Chinook_Sqlite.db to chinook.db and placed it in the project folder
Ran a Python test script from Terminal: connected to chinook.db with sqlite3 and confirmed SELECT COUNT(*) FROM Customer returns (59,)
Tested Cowork: confirmed it can read the project folder, sees the full directory structure, and automatically reads INSTRUCTIONS.md and SESSION_LOG.md for context

What I learned

Python's built-in sqlite3 library connects to a database file with one line: sqlite3.connect('chinook.db')
.fetchone() returns a single row as a tuple — that's why the output is (59,) instead of just 59
Cowork reads INSTRUCTIONS.md and SESSION_LOG.md at the start of every session, so keeping those files updated is how you give it context between sessions

What's still fuzzy

Nothing — today was straightforward setup and verification.

Tomorrow (Day 33)

Learn sqlite3 + pandas basics: connect to Chinook from Python, run a query, load results into a pandas DataFrame
Checkpoint: load the Genre table into a DataFrame and print it without looking at examples

--

Day 31 — Environment Setup + Git Init
What I did

Installed Python 3.14.3 (upgraded from macOS default 3.9.6) and confirmed pip 25.3
Installed project packages: pandas, numpy, matplotlib, seaborn, faker
Created ~/Documents/chinook-portfolio/ with full folder structure: sql-case-studies, python-analysis, data_generation, tableau-data, ai-collaboration
Copied SQL case study files (.md writeups + .sql queries) into the new structure and removed the duplicate source folder
Initialized git, renamed branch to main, created .gitignore
Created GitHub repo (dmatelokoh/chinook-portfolio), generated personal access token, pushed to GitHub

What I learned

Git user name is a display label on commits — it's separate from my GitHub username. The email is what actually links commits to my GitHub profile.
GitHub no longer accepts passwords for pushes — you need a personal access token with repo scope.
The daily git workflow is three commands: git add ., git commit -m "message", git push

What's still fuzzy

Nothing major — today was all setup. Haven't written any Python yet.

Tomorrow (Day 32)

Set up Cowork with project folder access
Write and run a test script connecting Python to the Chinook SQLite database
Confirm SELECT COUNT(*) FROM Customer returns 59

