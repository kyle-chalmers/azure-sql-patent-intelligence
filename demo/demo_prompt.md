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

```xml
<pipeline-request>
  <context>
    I need to build a patent intelligence database for AI and data processing patents —
    covering AI data processing, predictive analytics, and business intelligence.
    Let's use our Azure SQL Database and the USPTO patent API.
  </context>

  <rules>
    - Announce each step before executing it (e.g., "Step 3: Searching USPTO...")
    - Show every SQL query and its results inline — the audience needs to see what's happening
    - Keep all output concise: tables over paragraphs, top 10 over full dumps
    - One script per task — no unnecessary helper files or abstractions
    - Confirm success at each step with a brief summary before moving to the next
    - Save charts to the output/ directory and confirm file paths
  </rules>

  <steps>
    <step name="create-ticket">
      Create an Azure DevOps work item to track this pipeline build.
      Use az boards to create a Task titled "Build AI & Data Patent Intelligence Pipeline".
    </step>

    <step name="connect-discover">
      Connect to our Azure SQL Database and show me what tables currently exist
      (should be empty — we're building from scratch). Note: the free tier
      auto-pauses after inactivity — the first query may take ~30 seconds to
      wake the database up. Use a 60-second login timeout (-l 60) and if the
      first attempt fails, wait a moment and retry once.
    </step>

    <step name="create-schema">
      Create a PATENTS table optimized for T-SQL with columns for
      patent_number (PK), title, abstract, assignee, inventors (JSON as NVARCHAR(MAX)),
      filing_date, grant_date, cpc_codes (JSON as NVARCHAR(MAX)), search_query, category,
      and timestamps. Add indexes on assignee and filing_date.
    </step>

    <step name="search-uspto">
      Use the patent search tools in tools/ to search three AI & data topics:
      search_by_title("AI data processing", limit=17),
      search_by_title("predictive analytics", limit=17),
      search_by_title("business intelligence", limit=16).
      Merge all results into one list (50 patents total).
    </step>

    <step name="load-data">
      Write a Python script using pyodbc to load those patent results into
      our Azure SQL table. Use parameterized MERGE statements for upsert logic. Execute it.
    </step>

    <step name="backfill">
      Backfill all AI data processing, predictive analytics, and business intelligence patents
      filed since November 30, 2022 (when ChatGPT launched). Use date-range filtering on the
      USPTO API to pull patents in batches, loading each batch into the PATENTS table with MERGE
      upserts. Track total patents loaded and date range covered.
    </step>

    <step name="daily-sync">
      Set up a daily sync process that loads only net-new patents since the last run.
      Create a SYNC_LOG table to track the last successful sync date and patent count.
      Write a Python script that queries the USPTO API for patents filed after the last
      sync date, loads them via MERGE upserts, and updates the sync log.
    </step>

    <step name="deploy-function">
      Create an Azure Function to run the daily sync automatically. Build the
      azure_function/ directory from scratch with function_app.py, host.json,
      and requirements.txt. The function should:
        - Use a timer trigger with schedule "0 0 7 * * *" (daily at 7 AM UTC)
        - Reuse the same patent search and MERGE upsert logic from the earlier steps
        - Use ODBC Driver 17 (not 18 — the Consumption plan image ships with Driver 17)
        - Copy the patent_search.py and azure_sql_queries.py into a shared/ subdirectory
          so the function can import them
      Then deploy live:
        cd azure_function && func azure functionapp publish patent-sync-func --python
      After deployment, confirm the function is registered using:
        az functionapp function show --name patent-sync-func --resource-group patent-intelligence-rg --function-name daily_patent_sync
      This turns the manual sync into a serverless job that runs every morning at 7 AM UTC.
    </step>

    <step name="analyze">
      Write T-SQL analytical queries and save each one to the sql/ directory
      as a numbered .sql file before executing it. The audience will copy these
      into the Azure Portal Query Editor to validate results visually.

      Queries to write and run:
      1. Summary stats — total patents loaded, earliest/latest filing dates,
         unique assignees (save as sql/03_patent_count.sql)
      2. Filing trends — patent count by year, ordered chronologically
         (save as sql/04_filing_trends.sql)
      3. Top inventors — parse the inventors JSON array using CROSS APPLY
         OPENJSON, group by inventor name, top 10 (save as sql/05_top_inventors.sql)
      4. Technology categories — parse cpc_codes JSON array using CROSS APPLY
         OPENJSON, group by first 4 characters of CPC code, top 10
         (save as sql/06_cpc_breakdown.sql)
    </step>

    <step name="visualize">
      Create matplotlib charts from the query results and save as PNG files
      to the output/ directory:
      1. Filing trends by year (bar or line chart)
      2. Top technology categories by CPC code (horizontal bar chart)
    </step>

    <step name="report">
      Generate a markdown executive summary of the AI & data patent landscape.
    </step>

    <step name="close-ticket">
      Update the Azure DevOps work item to "Done". Add a discussion comment
      summarizing what was built: table created, patents loaded, analysis complete.
    </step>
  </steps>

  <resources>
    The patent search tools are in the tools/ directory. The Azure SQL connection details
    are in the .env file. Let's build this entire pipeline right now.
  </resources>
</pipeline-request>
```

---

## Prompt 2: Audience Participation (optional, use during Q&A if time allows)

```xml
<follow-up>
  The viewer wants to explore [TOPIC]. Search the USPTO for patents using
  search_by_title("[TOPIC]", limit=20), load the results into our PATENTS table,
  and give me a quick summary of what's being patented in that area.
</follow-up>
```

---

## Prompt 3: Quick Follow-Up Analysis (optional, if demo finishes early)

```xml
<follow-up>
  Compare patent activity across our three topics: AI data processing, predictive analytics,
  and business intelligence. Run a query showing filing trends by topic side by side,
  and create a comparison chart.
</follow-up>
```
