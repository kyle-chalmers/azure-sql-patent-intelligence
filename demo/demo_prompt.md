# Demo Prompts

## Pre-Demo: Wake the Database (run 10 min before, NOT on stage)

```
Run a quick sqlcmd query against our Azure SQL database to wake it up: SELECT GETDATE()
```

## Pre-Demo: Verify Setup (run 5 min before, NOT on stage)

```
Verify our setup: 1) Check the USPTO API key is configured, 2) Test sqlcmd can connect to Azure SQL, 3) Confirm pyodbc is installed. Just run quick checks for each.
```

## On Stage: /clear first

Run `/clear` to start with a clean conversation.

---

## Prompt 1: The Main Demo (paste this during the presentation)

```
I need to build a patent intelligence database for Intel Corporation — the largest
tech employer here in Phoenix. Let's use our Azure SQL Database and the USPTO patent API.

Here's what I need you to do:

1. CONNECT & DISCOVER: Show me what tables currently exist in our Azure SQL Database
   (should be empty — we're building from scratch).

2. CREATE SCHEMA: Create a PATENTS table optimized for T-SQL with columns for
   patent_number (PK), title, abstract, assignee, inventors (JSON as NVARCHAR(MAX)),
   filing_date, grant_date, cpc_codes (JSON as NVARCHAR(MAX)), search_query, category,
   and timestamps. Add indexes on assignee and filing_date.

3. SEARCH USPTO: Use the patent search tools in tools/ to find Intel Corporation patents.
   Search by assignee "Intel" with a limit of 50.

4. LOAD DATA: Write a Python script using pyodbc to load those patent results into
   our Azure SQL table. Use parameterized MERGE statements for upsert logic. Execute it.

5. ANALYZE: Run T-SQL analytical queries:
   - How many patents did we load and what's the date range?
   - What are the filing trends by year?
   - Who are Intel's most prolific inventors?
   - What technology categories (CPC codes) do they focus on?
   Use OPENJSON to parse the JSON arrays.

6. VISUALIZE: Create matplotlib charts showing filing trends by year and top technology
   categories. Save as PNG files.

7. REPORT: Generate a markdown executive summary of Intel's patent portfolio.

The patent search tools are in the tools/ directory. The Azure SQL connection details
are in the .env file. Let's build this entire pipeline right now.
```

---

## Prompt 2: Audience Participation (optional, use during Q&A if time allows)

```
The audience wants to see [COMPANY NAME]. Search the USPTO for their patents using
search_by_assignee("[COMPANY NAME]", limit=20), load the results into our PATENTS table,
and give me a quick summary of what they're patenting.
```

---

## Prompt 3: Quick Follow-Up Analysis (optional, if demo finishes early)

```
Compare Intel's patent activity to [COMPANY NAME]'s. Run a query showing both companies'
filing trends side by side, and create a comparison chart.
```
