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
| Tue, Feb 18, 2026 | Neudesic, Tempe | Kyle Chalmers |
| 5:00 PM MST | Arizona Data Platform User Group | KC Labs AI |

---

| **YouTube** | **LinkedIn** | **GitHub Repo** | **KC Labs AI** | **AI Workshop** | **Morning Hike** |
| :---: | :---: | :---: | :---: | :---: | :---: |
| <img src="./qr_codes/youtube_qr.png" width="150" alt="YouTube QR"> | <img src="./qr_codes/linkedin_qr.png" width="150" alt="LinkedIn QR"> | <img src="./qr_codes/repo_qr.png" width="150" alt="GitHub QR"> | <img src="./qr_codes/kclabs_qr.png" width="150" alt="KC Labs QR"> | <img src="./qr_codes/aztechweek_workshop_qr.png" width="150" alt="Workshop QR"> | <img src="./qr_codes/aztechweek_hike_qr.png" width="150" alt="Hike QR"> |
| [Subscribe](https://www.youtube.com/channel/UCkRi29nXFxNBuPhjseoB6AQ) | [Connect](https://www.linkedin.com/in/kylechalmers/) | [Star](https://github.com/kyle-chalmers/azure-sql-patent-intelligence) | [Visit](https://kclabs.ai/) | [RSVP](https://partiful.com/e/VPy2EpNYQFppO6ZQA17n) | [RSVP](https://partiful.com/e/vMiPKyrTML8yf8Gnf618) |

YouTube (subscribe for more data + AI content): https://www.youtube.com/channel/UCkRi29nXFxNBuPhjseoB6AQ
LinkedIn: https://www.linkedin.com/in/kylechalmers/
This repo: https://github.com/kyle-chalmers/azure-sql-patent-intelligence
KC Labs AI: https://kclabs.ai/

AZ Tech Week 2026:
The Practical AI Playbook Workshop (Wed, Apr 8 - Scottsdale): https://partiful.com/e/VPy2EpNYQFppO6ZQA17n
Sat Morning Hike, Connect, & Coffee (Sat, Apr 11 - Phoenix): https://partiful.com/e/vMiPKyrTML8yf8Gnf618

</div>

---

## The Big Idea

> **One prompt. Nine pipeline steps. Under 15 minutes. What used to take half a day now happens in a single conversation — with ticket tracking, schema design, API ingestion, data loading, analysis, and visualization all handled by an AI agent using the tools you already know.**

Tonight we build a patent intelligence database for **Intel Corporation** (the #1 tech employer in Phoenix) using:

- **Claude Code** as the AI agent — orchestrating the entire workflow via MCP servers and CLI tools
- **Azure SQL Database** (free tier) as the data store, queried through `sqlcmd` and loaded with `pyodbc`
- **Azure DevOps Boards** (free tier) for real-world ticket-driven workflow — the pipeline opens a ticket and closes it when done
- **USPTO Patent API** (free) as the live data source
- **One structured prompt** that drives all 9 steps from ticket creation to ticket closure

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

## What This Takes Manually vs. With Claude Code

| Step | Manual | With Claude Code |
|:-----|:------:|:----------------:|
| Create & track ticket | 2-5 min | Part of the prompt |
| Design schema | 15-30 min | Included in prompt |
| Write CREATE TABLE DDL | 10-15 min | Generated + executed |
| Search USPTO API | 30+ min (read API docs, write code) | One function call |
| Write data loading script | 1-2 hours (pyodbc, MERGE, error handling) | Generated + executed |
| Write analytical queries | 30-60 min (OPENJSON syntax, CTEs) | Generated + executed |
| Create visualizations | 30-60 min (matplotlib boilerplate) | Generated + saved |
| Write executive summary | 20-30 min | Generated |
| **Total** | **3-5 hours** | **~12 minutes** |

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
