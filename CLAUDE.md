# Claude Code Instructions: Azure SQL Patent Intelligence

> IMPORTANT: Everything in this repo is public-facing, so do not place any sensitive info here and make sure to distinguish between what should be internal-facing info (e.g. secrets, PII, recording guides/scripts), and public-facing info (instructions, how-to guides, actual code utilized). If there is information that Claude Code needs across sessions but should not be published, put it in the `.internal/` folder which is ignored by git per the `.gitignore`.

## Project Overview

This is a demo repository for a **KC Labs AI YouTube video** showing how Claude Code integrates with Azure SQL Database to build an AI-powered patent intelligence pipeline.

**Audience**: YouTube viewers — data professionals, AI practitioners, and developers
**Demo Subject**: AI & data processing patent analysis using USPTO API + Azure SQL Database

> **Claude Code**: If `.internal/OWNER_CONFIG.md` exists, read it at the start of each session and use those concrete values (org URLs, resource names, emails) for all commands. This avoids resolving `$ENV_VAR` references or guessing placeholder values.
>
> **Viewers cloning this repo**: Create your own `.internal/OWNER_CONFIG.md` with your personal values (DevOps org, Function App name, resource group, email). See the format in CLAUDE.md's Available Tools section. Then update `.env` with your credentials (see `.env.example`). The pipeline tools, prompts, and SQL patterns all work out of the box.

## Available Tools

### MCP Server: DBHub (Azure SQL)

- Use for schema discovery and quick queries (the "wow" moment for the audience)
- Tools available: `list_tables`, `describe_table`, `run_query`
- If MCP is unavailable, fall back to sqlcmd seamlessly

### CLI Tools

When calling the cli tools, there may be a pause period of 30 seconds while it wakes back up.

- **sqlcmd**: Connect to Azure SQL Database for DDL and analytical queries
  - Connection: `sqlcmd -S $AZURE_SQL_SERVER -d $AZURE_SQL_DATABASE -U $AZURE_SQL_USER -P $AZURE_SQL_PASSWORD`
  - Login timeout (for free-tier wake-up): add `-l 60` flag
  - CSV output: add `-s "," -W` flags
  - Single query: `-Q "SELECT ..."`
  - Load environment first: `source .env` before running sqlcmd commands
- **Python + pyodbc**: For data loading scripts with parameterized queries
  - Connection string uses `ODBC Driver 18 for SQL Server`
  - Always use parameterized queries (? placeholders) — never string interpolation
  - Load `.env` with `python-dotenv`: `from dotenv import load_dotenv; load_dotenv()`
  - pyodbc connect: `pyodbc.connect(f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={db};UID={user};PWD={pwd}")`
- **az boards** (Azure DevOps): Create and manage work items for ticket-driven workflows
  - Always include `--org "$AZURE_DEVOPS_ORG" --project "$AZURE_DEVOPS_PROJECT"` on every command
  - Create: `az boards work-item create --title "..." --type Task --org "$AZURE_DEVOPS_ORG" --project "$AZURE_DEVOPS_PROJECT"`
  - Transition to Doing (when work starts): `az boards work-item update --id <ID> --state "Doing" --org "$AZURE_DEVOPS_ORG"`
  - Transition to Done (when work completes): `az boards work-item update --id <ID> --state "Done" --org "$AZURE_DEVOPS_ORG"`
  - Add comment: `az boards work-item update --id <ID> --discussion "Summary" --org "$AZURE_DEVOPS_ORG"`
  - Delete: `az boards work-item delete --id <ID> --yes --org "$AZURE_DEVOPS_ORG" --project "$AZURE_DEVOPS_PROJECT"`
  - State lifecycle: `To Do` → `Doing` (start of work) → `Done` (completion)

### Azure Functions (Daily Sync Automation)

- **Function App**: `patent-sync-func` (Consumption plan, Python 3.10) — replace with your own Function App name
- **Resource Group**: `patent-intelligence-rg` — replace with your own resource group
- **Built during demo**: The `azure_function/` directory is created from scratch by Claude Code during the live demo (not pre-built)
- **What to build**: `function_app.py` (timer-triggered), `host.json`, `requirements.txt` (azure-functions, pyodbc), and a `shared/` subdirectory with copies of `patent_search.py` and `azure_sql_queries.py`
- **Schedule**: `0 0 7 * * *` (daily at 7:00 AM UTC / midnight MST)
- **Deploy**: `cd azure_function && func azure functionapp publish <your-function-app> --python`
- **View logs**: `func azure functionapp logstream <your-function-app>`
- **Manual trigger**: `az functionapp function invoke --name <your-function-app> --resource-group <your-rg> --function-name daily_patent_sync`
- **Important**: Uses `ODBC Driver 17` (not 18) — the Python 3.10 Consumption plan image ships with Driver 17
- **Setup**: See Prerequisites in README.md for creating the Function App and configuring Application Settings

### Python Tools (in tools/ directory)

- **patent_search.py**: USPTO API wrapper with 3-tier fallback (USPTO ODP → Google Patents → Sample Data)
  - `search_by_title("AI data processing", limit=17)` — primary function for demo
  - `search_by_title("predictive analytics", limit=17)` — second topic
  - `search_by_title("business intelligence", limit=16)` — third topic
  - All 50 patents merge into the same PATENTS table for cross-topic analysis
  - Supports `filing_date_from` / `filing_date_to` params for date-range filtering
  - Supports `start` param for pagination (API returns max 100 per request)
  - API key loaded from `.env` file (USPTO_API_KEY)
- **azure_sql_queries.py**: T-SQL query builders
  - `build_create_table_sql()` — DDL for PATENTS table with indexes
  - `build_upsert_query()` — Parameterized MERGE statement
  - `get_trends_query()` — Filing trends by year
  - `get_top_inventors_query()` — Uses CROSS APPLY OPENJSON
  - `get_cpc_breakdown_query()` — Uses CROSS APPLY OPENJSON
  - `build_create_sync_log_sql()` — DDL for SYNC_LOG table
  - `get_last_sync_date_query()` — Last successful sync date for daily sync

## T-SQL Conventions for This Project

### JSON Handling

- Store JSON arrays as `NVARCHAR(MAX)` (not Snowflake VARIANT)
- Parse with `CROSS APPLY OPENJSON(column_name)` for arrays
- Use `JSON_VALUE(column, '$.key')` for scalar values

### Key T-SQL Patterns

```sql
-- Parse JSON array (inventors, cpc_codes)
SELECT inventor.value FROM PATENTS CROSS APPLY OPENJSON(inventors) AS inventor

-- MERGE upsert (must end with semicolon!)
MERGE INTO PATENTS AS target USING (...) AS source ON ... WHEN MATCHED THEN UPDATE ... WHEN NOT MATCHED THEN INSERT ...;

-- Top N results
SELECT TOP 10 ... FROM ... ORDER BY ...

-- Current timestamp
GETDATE()
```

### Things to Remember

- T-SQL MERGE statements MUST end with a semicolon
- Use `NVARCHAR` not `VARCHAR` for Unicode support
- Azure SQL default collation is case-insensitive (no need for ILIKE)
- Use `DATETIME2` instead of `TIMESTAMP` for date/time columns

## Environment Configuration

Connection details are in `.env` file (gitignored). Template at `.env.example`.

Required variables:

- `USPTO_API_KEY` — Free from <https://data.uspto.gov/key/myapikey>
- `AZURE_SQL_SERVER` — yourserver.database.windows.net
- `AZURE_SQL_DATABASE` — PatentIntelligence
- `AZURE_SQL_USER` — sqladmin
- `AZURE_SQL_PASSWORD` — your password
- `AZURE_DEVOPS_ORG` — <https://dev.azure.com/kylechalmers>
- `AZURE_DEVOPS_PROJECT` — microsoft-builds

> **Note**: These same variables must be configured as Application Settings in the Azure Function App for the daily sync automation.

## Demo Flow

The demo follows 9 steps in a single prompt:

0. **Create Ticket** — Azure DevOps work item to track the pipeline build
1. **Connect & Discover** — Show empty database
2. **Create Schema** — DDL with indexes
3. **Search USPTO** — API calls for AI data processing, predictive analytics, and business intelligence patents
4. **Load Data** — Python pyodbc with MERGE upserts
5. **Analyze** — T-SQL queries with OPENJSON
5b. **Backfill** — All patents filed since Nov 30, 2022 (ChatGPT launch) via date-range API calls
5c. **Daily Sync** — SYNC_LOG table + script to load net-new patents since last sync
5d. **Deploy Function** — `func azure functionapp publish` to deploy daily sync as Azure Function
6. **Visualize** — matplotlib charts
7. **Report** — Markdown executive summary
8. **Close Ticket** — Update work item to Done with summary

## Operating Principles

How Claude Code should reason through tasks — applicable to any data pipeline project.

### Show Your Reasoning

- Announce intent before action — say what you're about to do and why
- Show the actual commands and queries being run — don't execute silently
- Print every T-SQL query as a formatted code block BEFORE executing it, so the presenter can copy-paste it into the Azure Portal Query Editor for visual validation
- All SQL queries are also saved in the `sql/` directory (numbered by step) for reference and portal use
- Explain design choices briefly (one sentence) so the audience understands *why*, not just *what*
- Calibrate depth to your audience — skip basics they already know, lean into domain-specific details
- Example: "Using NVARCHAR(MAX) for JSON columns because Azure SQL stores JSON as strings, not a native JSON type"

### Verify Your Work

- Validate the result of each step before moving to the next — don't assume success
- After creating a table, confirm it exists. After loading data, check the row count. After running queries, sanity-check the results.
- Design for re-runnability: use `IF NOT EXISTS` for DDL, idempotent operations (like MERGE) for data loading
- If results look wrong or empty, flag it immediately — don't silently continue to the next step

### Keep It Reviewable

- Every artifact (DDL, scripts, queries, charts) should be readable by a colleague in under 30 seconds
- Prefer structured output (tables, bullet points) over prose
- Limit result sets to what's meaningful — top 10-15 rows, not full dumps. Summarize raw data into readable form.
- One script per task — no helper files, utility modules, or abstractions for one-off operations
- KISS and YAGNI: build only what's needed now, don't over-engineer, comment only where the logic isn't obvious

### Handle Failures Gracefully

- When a tool fails, explain what happened in one sentence and try the known fallback
- Don't retry the same failing command endlessly — try once, explain, move on
- Prioritize the core workflow — if a non-critical step fails (e.g., ticket tracking), skip it and continue with the primary work

### Protect Sensitive Data

- Never print credentials, API keys, or passwords in terminal output
- Use environment variables for all secrets — never hardcode in scripts
- Reference `$ENV_VARS` in commands instead of literal values

### Track Work End-to-End

- Open a work item at the start to track what's being built. Capture the ID.
- Immediately transition it to `Doing` once work begins.
- Reference the ticket ID when announcing steps so progress is traceable throughout the pipeline
- Close the ticket (state → `Done`) with a summary comment when work is complete
- If ticket tracking is unavailable, note it and continue — don't block the core work

## AI & Data CPC Codes Reference

| CPC Code | Technology Area |
| -------- | --------------- |
| G06N | AI/ML computing — neural networks, machine learning |
| G06F | Electric digital data processing |
| G06Q | Business data processing / BI systems |
| G06V | Image/video recognition |
| G10L | Speech analysis and recognition |
| G16H | Healthcare informatics / AI in medicine |
