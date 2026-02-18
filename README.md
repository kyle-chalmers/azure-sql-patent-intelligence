<div align="center">

# Claude Code + Azure SQL: AI-Powered Patent Intelligence

### Building a Complete Data Pipeline in One Conversation

[![Claude Code](https://img.shields.io/badge/Claude_Code-AI_Agent-blueviolet?style=for-the-badge&logo=anthropic)](https://claude.ai/download)
[![Azure SQL](https://img.shields.io/badge/Azure_SQL-Free_Tier-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)](https://aka.ms/azuresqlhub)
[![Python](https://img.shields.io/badge/Python-pyodbc-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![T-SQL](https://img.shields.io/badge/T--SQL-OPENJSON-CC2927?style=for-the-badge&logo=microsoftsqlserver&logoColor=white)](https://learn.microsoft.com/en-us/sql/t-sql/)
[![USPTO API](https://img.shields.io/badge/USPTO-Patent_API-darkblue?style=for-the-badge)](https://data.uspto.gov)

---

| **Date** | **Venue** | **Presenter** |
|:---:|:---:|:---:|
| Tue, Feb 18, 2026 | Neudesic, Tempe | Kyle Chalmers |
| 5:00 PM MST | Arizona Data Platform User Group | KC Labs AI |

---

| **LinkedIn** | **YouTube** | **GitHub Repo** |
|:---:|:---:|:---:|
| <img src="./qr_codes/linkedin_qr.png" width="150"> | <img src="./qr_codes/youtube_qr.png" width="150"> | <img src="./qr_codes/repo_qr.png" width="150"> |
| [Connect](https://www.linkedin.com/in/kylechalmers/) | [Subscribe](https://www.youtube.com/channel/UCkRi29nXFxNBuPhjseoB6AQ) | [Star](https://github.com/kyle-chalmers/azure-sql-patent-intelligence) |

</div>

---

## The Big Idea

> **What if AI could handle your entire data pipeline — from API ingestion to database loading to analysis — requiring you only to connect it to the right tools?**

Tonight we build a patent intelligence database for **Intel Corporation** (the #1 tech employer in Phoenix) using:
- **Claude Code** as the AI agent orchestrating everything
- **Azure SQL Database** (free tier) as the data store
- **USPTO Patent API** (free) as the data source
- **sqlcmd + pyodbc** as the tools Claude uses — the same tools you already know

---

## Session Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                    SESSION OVERVIEW (~25 min)                         │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────┐   ┌─────────────┐   ┌──────────────┐   ┌──────────┐  │
│  │  Intro   │──▶│   Context   │──▶│    Demo      │──▶│ Wrap-up  │  │
│  │ (2 min)  │   │  (3 min)    │   │  (12 min)    │   │ (3 min)  │  │
│  └──────────┘   └─────────────┘   └──────────────┘   └──────────┘  │
│                                                              │      │
│                  Show CLAUDE.md     Single prompt:            ▼      │
│                  + tools/           empty DB ──▶ full      Q&A      │
│                                     patent analysis                  │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Demo: One Prompt, Complete Pipeline

```
USPTO API ──▶ Python ──▶ Azure SQL ──▶ T-SQL Analysis ──▶ Visualizations
  (search)    (load)      (store)       (OPENJSON)         (matplotlib)
```

<details>
<summary><b>Demo Prompt</b> <sup>(click to expand)</sup></summary>

```text
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

</div>

---

## What This Takes Manually vs. With Claude Code

| Step | Manual | With Claude Code |
|:-----|:------:|:----------------:|
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
1. Go to: **https://data.uspto.gov/key/myapikey**
2. Sign in or create a free account (email verification)
3. Click "Generate API Key"
4. Copy the key and add to `.env` file

### Azure SQL Database (Free Tier)
1. Go to: **https://aka.ms/azuresqlhub** and click "Try for free"
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

### Scan to Connect

| **LinkedIn** | **YouTube** | **GitHub** |
|:---:|:---:|:---:|
| <img src="./qr_codes/linkedin_qr.png" width="150"> | <img src="./qr_codes/youtube_qr.png" width="150"> | <img src="./qr_codes/repo_qr.png" width="150"> |

---

*Thank you for attending! Questions? Find me after the session or connect on LinkedIn.*

<sub>Made with Claude Code</sub>

</div>
