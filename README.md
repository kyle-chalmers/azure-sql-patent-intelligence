<div align="center">

# Claude Code + Azure SQL: AI-Powered Patent Intelligence

### From Zero to Full Data Pipeline — Faster Than You Thought Possible

[![Claude Code](https://img.shields.io/badge/Claude_Code-AI_Agent-blueviolet?style=for-the-badge&logo=anthropic)](https://claude.ai/download)
[![Azure SQL](https://img.shields.io/badge/Azure_SQL-Free_Tier-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)](https://aka.ms/azuresqlhub)
[![Python](https://img.shields.io/badge/Python-pyodbc-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![T-SQL](https://img.shields.io/badge/T--SQL-OPENJSON-CC2927?style=for-the-badge&logo=microsoftsqlserver&logoColor=white)](https://learn.microsoft.com/en-us/sql/t-sql/)
[![USPTO API](https://img.shields.io/badge/USPTO-Patent_API-darkblue?style=for-the-badge)](https://data.uspto.gov)
[![Azure DevOps](https://img.shields.io/badge/Azure_DevOps-Boards-0078D7?style=for-the-badge&logo=azuredevops&logoColor=white)](https://dev.azure.com)

---

| **Date** | **Venue** | **Presenter** |
| :---: | :---: | :---: |
| Tue, Feb 18, 2026 | Virtual | Kyle Chalmers |
| 5:00 PM MST | Arizona Data Platform User Group | KC Labs AI |

---

| **YouTube** | **LinkedIn** | **GitHub Repo** | **KC Labs AI** | **AI Workshop** | **Morning Hike** |
| :---: | :---: | :---: | :---: | :---: | :---: |
| <img src="./qr_codes/youtube_qr.png" width="150" alt="YouTube QR"> | <img src="./qr_codes/linkedin_qr.png" width="150" alt="LinkedIn QR"> | <img src="./qr_codes/repo_qr.png" width="150" alt="GitHub QR"> | <img src="./qr_codes/kclabs_qr.png" width="150" alt="KC Labs QR"> | <img src="./qr_codes/aztechweek_workshop_qr.png" width="150" alt="Workshop QR"> | <img src="./qr_codes/aztechweek_hike_qr.png" width="150" alt="Hike QR"> |
| [Subscribe](https://www.youtube.com/channel/UCkRi29nXFxNBuPhjseoB6AQ) | [Connect](https://www.linkedin.com/in/kylechalmers/) | [Star](https://github.com/kyle-chalmers/azure-sql-patent-intelligence) | [Visit](https://kclabs.ai/) | [RSVP](https://partiful.com/e/VPy2EpNYQFppO6ZQA17n) | [RSVP](https://partiful.com/e/vMiPKyrTML8yf8Gnf618) |

- YouTube (subscribe for more data + AI content): https://www.youtube.com/channel/UCkRi29nXFxNBuPhjseoB6AQ
- LinkedIn: https://www.linkedin.com/in/kylechalmers/
- This repo: https://github.com/kyle-chalmers/azure-sql-patent-intelligence
- KC Labs AI: https://kclabs.ai/

AZ Tech Week 2026:
- The Practical AI Playbook Workshop (Wed, Apr 8 - Scottsdale): https://partiful.com/e/VPy2EpNYQFppO6ZQA17n
- Sat Morning Hike, Connect, & Coffee (Sat, Apr 11 - Phoenix): https://partiful.com/e/vMiPKyrTML8yf8Gnf618

</div>

---

## The Big Idea

> **Today with Claude Code and other AI coding tools, one well-designed prompt with the appropriate context can lead us to building a full data pipeline in one sitting. What used to take days now can happen over hours or even minutes in a single conversation, with ticket tracking, schema design, API ingestion, data loading, analysis, and visualization all handled by an AI agent using the tools available in your Microsoft data stack today.**

Tonight I will build a real patent intelligence database as if I was working for Intel Corporation (the #1 tech employer in Phoenix) using:

- **Claude Code** as the AI agent — orchestrating the entire workflow via different CLI/MCP tools
- **Azure SQL Database** (free tier) as the data store, queried through `sqlcmd` and loaded with `pyodbc`
- **Azure DevOps Boards** (free tier) for real-world ticket-driven workflow — the pipeline opens a ticket and closes it when done
- **USPTO Patent API** (free) as the live data source
- **One structured prompt** that drives all steps from ticket creation to ticket closure.

---

## Session Flow

```text
┌──────────────────────────────────────────────────────────────────────┐
│                    SESSION OVERVIEW (~25 min)                         │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────┐   ┌─────────────┐   ┌──────────────┐   ┌──────────┐  │
│  │  Intro   │──▶│   Context   │──▶│    Demo      │──▶│ Wrap-up  │  │
│  │ (2 min)  │   │  (3 min)    │   │  (12 min)    │   │ (3 min)  │  │
│  └──────────┘   └─────────────┘   └──────────────┘   └──────────┘  │
│                                                              │      │
│                  Show CLAUDE.md     DevOps Ticket ──▶        ▼      │
│                  + tools/           empty DB ──▶ full       Q&A     │
│                                     patent analysis                  │
│                                     ──▶ Close Ticket                 │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Prereqs Prompt for Claude Code

> After cloning this repo, open it in Claude Code and paste this prompt to install all dependencies:

<details>
<summary><b>Prereqs Prompt</b> <sup>(click to expand)</sup></summary>

```xml
<prereqs-request>
  <context>
    I just cloned the azure-sql-patent-intelligence repo and need to install all
    dependencies, configure my environment, and verify everything works before
    running the demo. My Azure SQL Database and USPTO API key should already be
    set up — I just need the local tooling wired together.
  </context>

  <rules>
    - Check what's already installed before installing — don't reinstall working tools
    - Never print or log credentials — use environment variables from .env only
    - If a step fails, explain what happened in one sentence and continue with the rest
    - At the end, print a single summary table showing what's ready and what needs attention
  </rules>

  <steps>
    <step name="env-file">
      If .env doesn't already exist, copy .env.example to .env.
      Print a checklist of which variables still need to be filled in (check for
      empty values). Don't print the actual values — just show which are set and
      which are missing.
    </step>

    <step name="python-deps">
      Install Python dependencies from requirements.txt:
      pyodbc, matplotlib, python-dotenv, pandas, qrcode.
      Run: pip install -r requirements.txt
      Verify with: python3 -c "import pyodbc, matplotlib, dotenv, pandas; print('OK')"
    </step>

    <step name="sqlcmd">
      Install sqlcmd for connecting to Azure SQL Database.
      macOS: brew install microsoft/mssql-release/mssql-tools18
      Linux: https://learn.microsoft.com/en-us/sql/linux/sql-server-linux-setup-tools
      Verify with: sqlcmd '-?'
    </step>

    <step name="azure-cli">
      Install Azure CLI if not present, then add the Azure DevOps extension.
      macOS: brew install azure-cli
      Then: az extension add --name azure-devops
      If already installed, skip. Verify with: az boards -h
      Note: User will need to run 'az login' and 'az devops configure --defaults
      organization=ORG project=PROJECT' themselves after this step.
    </step>

    <step name="test-azure-sql">
      If AZURE_SQL_SERVER is set in .env, test the connection:
      source .env && sqlcmd -S "$AZURE_SQL_SERVER" -d "$AZURE_SQL_DATABASE" \
        -U "$AZURE_SQL_USER" -P "$AZURE_SQL_PASSWORD" \
        -Q "SELECT DB_NAME() AS CurrentDB, SUSER_NAME() AS CurrentUser"
      If it fails with a firewall error, tell the user to add their IP in
      Azure Portal > SQL Server > Networking > Firewall rules.
    </step>

    <step name="verify-all">
      Print a summary table:
      - .env variables: which are set, which are empty
      - Python packages: installed or missing
      - sqlcmd: available or not
      - Azure CLI + DevOps extension: available or not
      - Azure SQL connection: connected or failed (with reason)
      - USPTO API key: valid or missing
    </step>
  </steps>
</prereqs-request>
```

</details>

---

## Demo: One Prompt, Complete Pipeline

```text
DevOps ──▶ USPTO API ──▶ Python ──▶ Azure SQL ──▶ T-SQL Analysis ──▶ Visualizations ──▶ DevOps
(ticket)    (search)     (load)      (store)       (OPENJSON)         (matplotlib)     (close)
```

<details>
<summary><b>Demo Prompt</b> <sup>(click to expand)</sup></summary>

```xml
<pipeline-request>
  <context>
    I need to build a patent intelligence database for Intel Corporation — the largest
    tech employer here in Phoenix. Let's use our Azure SQL Database and the USPTO patent API.
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
      Use az boards to create a Task titled "Build Intel Patent Intelligence Pipeline".
    </step>

    <step name="connect-discover">
      Show me what tables currently exist in our Azure SQL Database
      (should be empty — we're building from scratch).
    </step>

    <step name="create-schema">
      Create a PATENTS table optimized for T-SQL with columns for
      patent_number (PK), title, abstract, assignee, inventors (JSON as NVARCHAR(MAX)),
      filing_date, grant_date, cpc_codes (JSON as NVARCHAR(MAX)), search_query, category,
      and timestamps. Add indexes on assignee and filing_date.
    </step>

    <step name="search-uspto">
      Use the patent search tools in tools/ to find Intel Corporation patents.
      Search by assignee "Intel" with a limit of 50.
    </step>

    <step name="load-data">
      Write a Python script using pyodbc to load those patent results into
      our Azure SQL table. Use parameterized MERGE statements for upsert logic. Execute it.
    </step>

    <step name="analyze">
      Run T-SQL analytical queries:
      - How many patents did we load and what's the date range?
      - What are the filing trends by year?
      - Who are Intel's most prolific inventors?
      - What technology categories (CPC codes) do they focus on?
      Use OPENJSON to parse the JSON arrays.
    </step>

    <step name="visualize">
      Create matplotlib charts showing filing trends by year and top technology
      categories. Save as PNG files.
    </step>

    <step name="report">
      Generate a markdown executive summary of Intel's patent portfolio.
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

</details>

---

## Intel CPC Codes Reference

**CPC (Cooperative Patent Classification)** is the global system used by the USPTO and European Patent Office to categorize patents by technology area. Every patent is tagged with one or more CPC codes — think of them as the "genre tags" for inventions. Analyzing CPC codes reveals where a company is investing its R&D.

These are the CPC codes you'll see most often in Intel's patent portfolio:

| CPC Code | Technology Area | Description |
|:--------:|:----------------|:------------|
| H01L | Semiconductor Devices | Intel's core — chip fabrication, packaging |
| G06F | Digital Data Processing | CPU architecture, computing systems |
| H04L | Digital Transmission | Networking, 5G, data center interconnects |
| G06N | AI/ML Computing | Neural networks, quantum computing |

---

## Key Tools Demonstrated

<div align="center">

| Tool | Purpose | Command |
|:----:|:--------|:--------|
| ![Claude](https://img.shields.io/badge/-Claude_Code-blueviolet?style=flat-square) | AI agent orchestrating the pipeline | `claude` |
| ![Azure SQL](https://img.shields.io/badge/-Azure_SQL-0078D4?style=flat-square) | Database (free tier) | `sqlcmd -S server -d db -Q "..."` |
| ![Python](https://img.shields.io/badge/-pyodbc-3776AB?style=flat-square) | Data loading with MERGE upserts | `python3 load_patents.py` |
| ![USPTO](https://img.shields.io/badge/-USPTO_API-darkblue?style=flat-square) | Patent data source (free) | `X-API-KEY` header |
| ![T-SQL](https://img.shields.io/badge/-T--SQL-CC2927?style=flat-square) | Analysis with OPENJSON | `CROSS APPLY OPENJSON(...)` |
| ![Azure DevOps](https://img.shields.io/badge/-Azure_DevOps-0078D7?style=flat-square) | Ticket-driven workflow | `az boards work-item create/update` |

</div>

---

## What Changes When an AI Agent Runs the Pipeline

The value isn't just speed — it's that one person can build something they wouldn't have attempted alone.

Manually, each step requires you to context-switch between docs, languages, and tools. With Claude Code, your job shifts from **writing code** to **reviewing code** — you describe intent and verify results.

| Step | What you do manually | What you do with Claude Code |
|:-----|:---------------------|:-----------------------------|
| Track the work | Open Azure DevOps, create a work item, fill in fields | Described in the prompt — created automatically |
| Design schema | Decide column types, JSON storage strategy, indexing | Review the generated DDL, approve or adjust |
| Search USPTO API | Read API docs, get a key, write HTTP requests, parse JSON | Describe what you want ("Intel patents") — agent calls the API |
| Load data into SQL | Write pyodbc script, handle connections, build MERGE statements | Review the generated script, watch it execute, verify row counts |
| Analyze with T-SQL | Look up OPENJSON syntax, write CTEs, iterate on queries | Ask questions in plain English, review the SQL and results |
| Visualize results | Write matplotlib boilerplate, format axes, save figures | Describe the charts you want, review the output |
| Summarize findings | Write a report from scratch based on query results | Review the generated summary, edit for tone |

**The honest version:** I could not have built this pipeline without Claude Code — not because I can't write T-SQL or Python, but because I wouldn't have sat down and wired together the USPTO API, pyodbc MERGE statements, OPENJSON analytics, matplotlib charts, and Azure DevOps tickets in one sitting. The breadth of tools and syntax across a pipeline like this is the real barrier, and that's exactly what an AI agent absorbs for you.

---

## Cost Breakdown

| Component | Cost |
|:----------|:----:|
| Azure SQL Database free tier | $0/month (lifetime, 100K vCore-seconds, 32 GB) |
| USPTO Patent API | $0 (free API key) |
| Claude Code (Pro plan) | $20/month (or $100/month for Max) |
| Azure DevOps Boards free tier | $0 (up to 5 users) |
| sqlcmd + pyodbc | $0 (open source) |
| **Total** | **$20-100/month** |

---

## Takeaways

<table>
<tr>
<td width="33%" align="center">

### 1. AI Works WITH Your Stack

No special plugins. Claude Code uses `sqlcmd` and `pyodbc` — the same tools you already know. It connects TO your Azure SQL, not around it.

</td>
<td width="33%" align="center">

### 2. One Prompt, Complete Pipeline

From empty database to executive report in a single conversation. API ingestion, schema creation, data loading, analysis, and visualization.

</td>
<td width="33%" align="center">

### 3. Context Engineering is the Skill

The CLAUDE.md file teaches the AI your tools, patterns, and standards. That's the real investment — everything else flows from it.

</td>
</tr>
</table>

---

## Prerequisites

### USPTO API Key (Required)

1. Go to: **<https://data.uspto.gov/key/myapikey>**
2. Sign in or create a free account (email verification)
3. Click "Generate API Key"
4. Copy the key and add to `.env` file

### Azure SQL Database (Free Tier)

> **Detailed walkthrough**: See **[docs/AZURE_SQL_SETUP.md](docs/AZURE_SQL_SETUP.md)** for step-by-step instructions with screenshots.

1. Go to: **<https://aka.ms/azuresqlhub>** and click "Try for free"
2. Create a logical server with SQL authentication
3. Create database: `PatentIntelligence` (select "None" for data source)
4. Add your client IP to the firewall rules

### Local Tools

```bash
# Install sqlcmd (macOS)
brew install sqlcmd

# Install Python dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Azure DevOps Boards (Ticket Workflow)

1. Go to: **<https://dev.azure.com>** and create or use an existing organization
2. Create a project for tracking demo work items
3. Install the CLI:

```bash
# Install Azure CLI (macOS)
brew install azure-cli

# Add Azure DevOps extension
az extension add --name azure-devops

# Login and configure defaults
az login
az devops configure --defaults organization=https://dev.azure.com/kylechalmers project=microsoft-builds
```

### Verify Setup

```bash
# Test USPTO API
python3 -c "from tools.patent_search import _get_api_key; print('OK' if _get_api_key() else 'MISSING')"

# Test Azure SQL
sqlcmd -S yourserver.database.windows.net -d PatentIntelligence -U sqladmin -P 'YourPass' -Q "SELECT 1 AS connected"

# Test pyodbc
python3 -c "import pyodbc; print('OK')"
```

---

## Get Started

<div align="center">

| | Resource | Link |
|:--:|:---------|:-----|
| 🤖 | **Claude Code** | [claude.ai/download](https://claude.ai/download) |
| ☁️ | **Azure SQL Free Tier** | [aka.ms/azuresqlhub](https://aka.ms/azuresqlhub) |
| 📊 | **USPTO Patent API** | [data.uspto.gov/key/myapikey](https://data.uspto.gov/key/myapikey) |
| 💻 | **This Repository** | [github.com/kyle-chalmers/azure-sql-patent-intelligence](https://github.com/kyle-chalmers/azure-sql-patent-intelligence) |

</div>

---

<div align="center">

## More From KC Labs AI

</div>

<details>
<summary><b>Video Tutorials</b> <sup>(click to expand)</sup></summary>

| Video | Description | |
|:------|:------------|:---:|
| **FUTURE PROOF Your Data Career with this Claude Code Deep Dive** | Complete guide to Claude Code for data teams | [Watch](https://www.youtube.com/watch?v=g4g4yBcBNuE) |
| **UPDATE to settings.json Chapter** | Settings.json updates from the Deep Dive | [Watch](https://youtu.be/WKt28ytMl3c) |
| **The AI Integration Every Data Professional Needs** | Using Claude Code with Snowflake | [Watch](https://www.youtube.com/watch?v=q1y7M5mZkkE) |
| **Claude Code Makes Databricks Easy** | Jobs, notebooks, SQL & Unity Catalog | [Watch](https://www.youtube.com/watch?v=5_q7j-k8DbM) |
| **Integrate Claude in Your Jira Workflow** | Jira/Confluence integration guide | [Watch](https://www.youtube.com/watch?v=WRvgMzYaIVo) |
| **Skip S3 and Athena in the AWS Console** | CLI + Claude Code for AWS data lakes | [Watch](https://www.youtube.com/watch?v=kCUTStWwErg) |
| **Use AI to Build Better Data Infrastructure** | Context Engineering with PRP Framework | [Watch](https://youtu.be/DUK39XqEVm0) |

</details>

---

<div align="center">

## Upcoming: AZ Tech Week 2026

| Event | Date | Details |
|:------|:-----|:--------|
| **The Practical AI Playbook Workshop** | Wed, Apr 8 | Hands-on AI tools workshop at 1951@SkySong, Scottsdale |
| **Sat. Morning Hike, Connect, & Coffee** | Sat, Apr 11 | Casual networking hike at Phoenix Mountain Preserve |

</div>

---

<div align="center">

### Scan to Connect

| **YouTube** | **LinkedIn** | **GitHub** | **KC Labs AI** |
| :---: | :---: | :---: | :---: |
| <img src="./qr_codes/youtube_qr.png" width="150" alt="YouTube QR"> | <img src="./qr_codes/linkedin_qr.png" width="150" alt="LinkedIn QR"> | <img src="./qr_codes/repo_qr.png" width="150" alt="GitHub QR"> | <img src="./qr_codes/kclabs_qr.png" width="150" alt="KC Labs QR"> |

YouTube (subscribe for more data + AI content): https://www.youtube.com/channel/UCkRi29nXFxNBuPhjseoB6AQ
LinkedIn: https://www.linkedin.com/in/kylechalmers/
This repo: https://github.com/kyle-chalmers/azure-sql-patent-intelligence
KC Labs AI: https://kclabs.ai/

AZ Tech Week 2026:
The Practical AI Playbook Workshop (Wed, Apr 8 - Scottsdale): https://partiful.com/e/VPy2EpNYQFppO6ZQA17n
Sat Morning Hike, Connect, & Coffee (Sat, Apr 11 - Phoenix): https://partiful.com/e/vMiPKyrTML8yf8Gnf618

---

*Thank you for attending! Questions? Find me after the session or connect on LinkedIn.*

<sub>Made with Claude Code</sub>

</div>
