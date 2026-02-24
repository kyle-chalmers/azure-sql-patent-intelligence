# Claude Code + Azure SQL: Build a Complete Data Pipeline in One Prompt

## Script Outline (Video Production Format)

---

HOOK INTRO (90-120 seconds)

First 5 Seconds (High energy, direct to camera)

- "What if I told you that a single prompt could build an entire data pipeline, from an empty database to an executive report, with ticket tracking, API ingestion, analysis, and visualizations?"

- Quick flash of [the finished pipeline output: charts, SQL results, executive summary on screen] as you say: "That's exactly what we're building today."

6-10 Seconds (Set expectations)

- "In this video, I'm going to build a patent intelligence database from scratch using Claude Code and Azure SQL. We'll pull real patent data from the USPTO API, load it, analyze it with T-SQL, backfill three years of historical data, and set up a daily sync process. All of it driven by AI."

Rest of Intro (Build credibility and preview)

- "I'm Kyle, and on this channel I build real data workflows with AI tools so you can see exactly what works and what doesn't."

- Your angle: I built this pipeline originally for a live meetup demo, and the audience reaction convinced me to record the full walkthrough. The biggest takeaway from that session was that the tool works because the context is right, not because the AI is magic.

- Preview the structure:
  - First, I'll show you how I set up the context that makes this possible: the CLAUDE.md file and the tools directory
  - Second, we'll run the full pipeline live: ticket creation, schema design, USPTO API search, data loading, T-SQL analysis, and visualization
  - Third, we'll take it further with a historical backfill of all AI patents since ChatGPT launched, and then set up a daily sync so this pipeline keeps itself current

- "By the end, you'll have a template you can copy for any API-to-database pipeline. Let's get into it."

---

DEFINITIONS

- **CLAUDE.md**: A markdown file that gives Claude Code all the context it needs about your project: what tools are available, how to connect to databases, what conventions to follow. Think of it as the instruction manual for your AI agent.
- **MERGE (T-SQL)**: An upsert statement. If the record exists, update it. If it doesn't, insert it. This makes data loading idempotent, so you can run it multiple times without duplicating data.
- **OPENJSON**: A T-SQL function that lets you query inside JSON strings stored in NVARCHAR columns. Azure SQL doesn't have a native JSON type, so this is how you parse JSON arrays for analysis.
- **CPC Codes**: Cooperative Patent Classification. Every patent is tagged with codes describing its technology area. G06N is AI/ML, G06F is data processing, G06Q is business intelligence. Think of them as genre tags for inventions.

---

SECTION 1: The Context That Makes It Work (3-4 minutes)

Setup

- Before we touch the database, I want to show you the two things that actually make this demo possible. The code Claude writes is a result of the context we give it.
- [Screen: Open the project folder in terminal, show the file structure]

The CLAUDE.md File

- [Screen: Open CLAUDE.md in editor, scroll through it slowly]
- This file tells Claude Code everything about the project: what database we're connecting to, what CLI tools are available, the T-SQL conventions to follow, and the exact steps of the pipeline.
- Point out the key sections:
  - Available tools: sqlcmd connection string, pyodbc patterns, az boards commands
  - T-SQL conventions: JSON stored as NVARCHAR(MAX), CROSS APPLY OPENJSON for parsing, MERGE must end with semicolon
  - Demo flow: the numbered steps Claude will follow
- "The biggest lesson, as it has been in my other videos, is that the tool did it because I gave it the right context. A clear description of what I wanted, the constraints I was working with, and enough structure for it to reason through the problem."

The Tools Directory

- [Screen: Show tools/ directory, briefly open patent_search.py and azure_sql_queries.py]
- patent_search.py: Handles the USPTO API with a 3-tier fallback. If the API is down, it tries Google Patents, then falls back to sample data. That way the demo always works.
- azure_sql_queries.py: T-SQL query builders. CREATE TABLE, MERGE upsert, filing trends, top inventors, CPC breakdown. All parameterized, all reusable.
- "These aren't complex. Each file is one responsibility, one purpose. No abstractions, no frameworks. Just functions that return SQL strings and API results."

- [Personal anecdote opportunity: Talk about why you wrote the tools this way. Maybe mention the meetup where the API went down and the fallback saved the demo.]

Section Transition

- That's the setup. The AI agent knows what tools it has, how to connect, and what conventions to follow.
- "Now let's actually run the pipeline and watch Claude Code build this thing from nothing."

---

SECTION 2: The Live Pipeline Build (8-10 minutes)

Setup

- This is the core of the video. One prompt, and Claude Code handles everything from ticket creation to analysis.
- [Screen: Claude Code terminal, clean session after /clear]

Paste the Prompt

- [Screen: Paste the pipeline-request XML prompt into Claude Code]
- Walk through what the prompt asks for: create a DevOps ticket, connect to the empty database, build the schema, search three AI topics on the USPTO API, load the data, run analysis queries, create charts, write a report, close the ticket.
- "This is it. One structured prompt. Let's see what happens."

Step 0: Create the DevOps Ticket

- [Screen: Claude Code runs az boards command, ticket created]
- Claude creates an Azure DevOps work item: "Build AI & Data Patent Intelligence Pipeline"
- "We track everything. If this were a real project, you'd see this ticket in your sprint board. The pipeline opens it at the start and closes it at the end."

Step 1: Connect and Discover

- [Screen: sqlcmd query runs, shows empty database]
- "The free tier auto-pauses after inactivity, so the first connection might take 30 seconds. Claude knows this because we told it in the CLAUDE.md, so it uses a 60-second timeout."
- Database is empty. No tables. That's our starting point.

Step 2: Create Schema

- [Screen: Claude shows the CREATE TABLE DDL, then executes it]
- PATENTS table with patent_number as primary key, JSON columns as NVARCHAR(MAX), indexes on assignee and filing_date.
- "Notice DATETIME2 instead of TIMESTAMP, NVARCHAR instead of VARCHAR. These are Azure SQL conventions, and Claude follows them because we specified them in the context file."

Step 3: Search the USPTO API

- [Screen: Claude makes three search_by_title calls]
- Three topics, 50 patents total:
  - "AI data processing" (17 patents)
  - "predictive analytics" (17 patents)
  - "business intelligence" (16 patents)
- "This is the pivot from the original demo. Instead of searching one company, we're searching across the entire patent ecosystem for AI and data topics. The results come from Google, IBM, Amazon, Salesforce, Microsoft, Oracle, and others."

Step 4: Load Data

- [Screen: Claude writes and runs the Python load script with pyodbc]
- MERGE upserts: if the patent already exists, update it. If it's new, insert it.
- "Every patent gets tagged with which search topic found it. That lets us do cross-topic analysis later."

Step 5: Analyze

- [Screen: Claude writes SQL queries, saves to sql/ directory, runs them]
- Walk through each query briefly:
  - Patent count and date range
  - Filing trends by year (YEAR(filing_date), GROUP BY)
  - Top inventors (CROSS APPLY OPENJSON on the inventors JSON array)
  - CPC code breakdown (CROSS APPLY OPENJSON on cpc_codes, LEFT() for grouping)
- "That OPENJSON syntax is the T-SQL equivalent of Snowflake's LATERAL FLATTEN or Postgres's jsonb_array_elements. If you're a SQL Server person, this is your JSON Swiss Army knife."

Step 6: Visualize

- [Screen: matplotlib charts appear: filing trends bar chart, CPC code horizontal bar chart]
- Quick pause on each chart. Point out anything interesting in the data.

Step 7: Report and Close

- [Screen: Markdown executive summary, then DevOps ticket updated to Done]
- Claude generates a summary, closes the ticket with a comment.
- "From empty database to closed ticket. That's the pipeline."

- Key insight: Your job shifts from writing code to reviewing code. You describe intent, Claude handles execution, and you verify the results.

Section Transition

- "We've got 50 patents loaded and analyzed. But 50 patents isn't a real dataset. Let's go bigger."

---

SECTION 3: Backfill and Daily Sync (5-7 minutes)

Setup

- The initial load was a proof of concept. Now we're going to backfill every AI and data processing patent filed since November 30, 2022, the day ChatGPT went public. Then we'll set up a sync process so the database stays current.
- [Screen: Claude Code, continuing in the same session]

The Backfill

- [Screen: Claude runs the backfill step, fetching patents in batches]
- date-range filtering on the USPTO API: filing_date_from=2022-11-30
- Pagination: the API returns max 100 per request, so Claude loops through batches
- Every batch gets MERGE upserted. Idempotent. You can run it twice and nothing breaks.
- [Screen: Show the running count as batches load]
- "This is where the date-range params we added to search_by_title pay off. Without them, you can only grab the most recent results. With them, you can pull the full history."

- [Personal anecdote opportunity: Talk about why you chose the ChatGPT launch date as the cutoff. Maybe comment on the explosion of AI patent filings since late 2022.]

The SYNC_LOG Table

- [Screen: Claude creates SYNC_LOG table]
- Six columns: sync_id, sync_date, filing_date_from, filing_date_to, patents_loaded, search_topics, sync_status
- "This is the metadata table that turns a one-off script into a repeatable process. Every time the sync runs, it logs what date range it covered and how many patents it loaded."

The Daily Sync Script

- [Screen: Claude writes and runs the sync script]
- Step 1: Query SYNC_LOG for the last successful sync date
- Step 2: Search USPTO for patents filed after that date
- Step 3: MERGE upsert the results
- Step 4: Write a new row to SYNC_LOG
- "If you wanted to automate this, you'd wrap this script in an Azure Function or a cron job. The logic is already here. You just need a trigger."

- Key insight: The difference between a demo and a production pipeline is about three things: historical backfill, incremental loading, and a sync log. We just added all three.

What the Data Looks Like Now

- [Screen: Run a few queries showing the full dataset: total patents, filing trends across years, top assignees]
- Compare the 50-patent initial load to the full backfill. Way more interesting patterns.
- Point out which companies are filing the most AI patents, which CPC codes dominate, any trends worth calling out.

Section Transition

- "Let's wrap this up with what you should take away from this."

---

WRAP-UP (60-90 seconds)

Recap the Key Takeaways

- Here's my take on what we just built and why it matters.

- The pipeline itself is useful, but the real lesson is the pattern. Give an AI agent the right context, the right tools, and a clear set of instructions, and it can wire together things you wouldn't normally sit down and build in one session. USPTO API calls, pyodbc MERGE statements, OPENJSON analytics, matplotlib charts, DevOps ticket tracking. The breadth is the hard part, and that's what the AI absorbs for you.

- Now you may ask yourself, all this information is great, but what should we do about it?
  - Clone the repo. The link is in the description. Everything you saw, the CLAUDE.md, the tools, the prompts, it's all there.
  - Set up your own Azure SQL free tier database. It costs nothing and it won't expire.
  - Try the prereqs prompt to get your local environment wired up, then run the demo prompt yourself.
  - Adapt it. Swap out the USPTO API for whatever data source you work with. The pattern is the same: search, load, analyze, visualize, report.

Closing

- "If this was helpful, drop a like and subscribe for more data and AI content. I put out videos showing how these tools actually work in real workflows, not the hype version, the real version."
- "As always, thanks so much and I will talk to you next time."
