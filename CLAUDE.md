# Claude Code Instructions: Azure SQL Patent Intelligence

> IMPORTANT: Everything in this repo is public-facing, so do not place any sensitive info here and make sure to distinguish between what should be internal-facing info (e.g. secrets, PII, recording guides/scripts), and public-facing info (instructions, how-to guides, actual code utilized). If there is information that Claude Code needs across sessions but should not be published, put it in the `.internal/` folder which is ignored by git per the `.gitignore`.

## Project Overview

This is a demo repository for the **Arizona Data Platform User Group** meetup presentation showing how Claude Code integrates with Azure SQL Database to build an AI-powered patent intelligence pipeline.

**Audience**: ~34 Microsoft data professionals (DBAs, SQL Server devs, BI analysts)
**Demo Subject**: Intel Corporation patent analysis using USPTO API + Azure SQL Database

## Available Tools

### MCP Server: DBHub (Azure SQL)

- Use for schema discovery and quick queries (the "wow" moment for the audience)
- Tools available: `list_tables`, `describe_table`, `run_query`
- If MCP is unavailable, fall back to sqlcmd seamlessly

### CLI Tools

- **sqlcmd**: Connect to Azure SQL Database for DDL and analytical queries
  - Connection: `sqlcmd -S $AZURE_SQL_SERVER -d $AZURE_SQL_DATABASE -U $AZURE_SQL_USER -P $AZURE_SQL_PASSWORD`
  - CSV output: add `-s "," -W` flags
  - Single query: `-Q "SELECT ..."`
- **Python + pyodbc**: For data loading scripts with parameterized queries
  - Connection string uses `ODBC Driver 18 for SQL Server`
  - Always use parameterized queries (? placeholders) — never string interpolation
- **az boards** (Azure DevOps): Create and manage work items for ticket-driven workflows
  - Requires: `az extension add --name azure-devops` + `az login`
  - Set defaults: `az devops configure --defaults organization=https://dev.azure.com/kylechalmers project=microsoft-builds`
  - Create: `az boards work-item create --title "..." --type Task`
  - Close: `az boards work-item update --id <ID> --state Done --discussion "Summary"`

### Python Tools (in tools/ directory)

- **patent_search.py**: USPTO API wrapper with 3-tier fallback (USPTO ODP → Google Patents → Sample Data)
  - `search_by_assignee("Intel", limit=50)` — primary function for demo
  - `search_by_title("semiconductor", limit=50)` — keyword search
  - API key loaded from `.env` file (USPTO_API_KEY)
- **azure_sql_queries.py**: T-SQL query builders
  - `build_create_table_sql()` — DDL for PATENTS table with indexes
  - `build_upsert_query()` — Parameterized MERGE statement
  - `get_trends_query()` — Filing trends by year
  - `get_top_inventors_query()` — Uses CROSS APPLY OPENJSON
  - `get_cpc_breakdown_query()` — Uses CROSS APPLY OPENJSON

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

## Demo Flow

The demo follows 9 steps in a single prompt:

0. **Create Ticket** — Azure DevOps work item to track the pipeline build
1. **Connect & Discover** — Show empty database
2. **Create Schema** — DDL with indexes
3. **Search USPTO** — API call for Intel patents
4. **Load Data** — Python pyodbc with MERGE upserts
5. **Analyze** — T-SQL queries with OPENJSON
6. **Visualize** — matplotlib charts
7. **Report** — Markdown executive summary
8. **Close Ticket** — Update work item to Done with summary

## Intel CPC Codes Reference

| CPC Code | Technology Area |
| -------- | --------------- |
| H01L | Semiconductor devices (Intel's core) |
| G06F | Electric digital data processing |
| H04L | Digital information transmission |
| G06N | Computing arrangements - AI/ML |
