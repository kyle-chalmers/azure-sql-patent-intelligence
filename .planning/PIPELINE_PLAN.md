# Pipeline Plan: AI & Data Patent Intelligence

## Steps
0. Create Ticket (Azure DevOps)
1. Connect & Discover (empty database)
2. Create Schema (PATENTS table + indexes)
3. Search USPTO (3 topics, 50 patents)
4. Load Data (MERGE upsert via pyodbc)
5. Analyze (4 T-SQL queries with OPENJSON)
5b. Backfill (all patents since 2022-11-30)
5c. Daily Sync (SYNC_LOG + incremental load)
5d. Deploy Azure Function (timer trigger)
6. Visualize (matplotlib charts)
7. Report (executive summary)
8. Close Ticket

## Status: Executing
