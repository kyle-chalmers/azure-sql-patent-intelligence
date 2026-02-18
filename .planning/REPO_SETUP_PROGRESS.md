# Implementation Progress: Azure SQL Patent Intelligence Demo

## Status

| Step | Status | Notes |
|------|--------|-------|
| 1. Create repo structure | Done | All directories, tools, configs |
| 2. USPTO API key setup | Done | Key in `.env` (30 chars, working) |
| 3. Test USPTO API | Done | `search_by_assignee('Intel', limit=5)` returns 5 patents from 57K+ results |
| 4. Azure SQL setup | **Pending** | Requires Azure portal setup by Kyle |
| 5. Configure MCP + CLI | **Pending** | Requires live Azure SQL connection |
| 6. Create code files | Done | patent_search.py (3-tier fallback), azure_sql_queries.py |
| 7. Create demo prompt | Done | XML format with `<pipeline-request>`, `<rules>`, `<steps>` tags |
| 8. Create README.md | Done | Full audience-facing docs, QR codes, AZ Tech Week events |
| 9. CLAUDE.md context engineering | Done | Operating Principles, T-SQL conventions, tool docs |
| 10. Presentation guide | Done | `.internal/PRESENTATION_GUIDE.md` |
| 11. QR codes | Done | 6 QR codes: YouTube, LinkedIn, GitHub, KC Labs, Workshop, Hike |
| 12. Azure DevOps integration | Done | `az boards` commands in CLAUDE.md, steps 0+8 in prompt |
| 13. End-to-end dry run | **Pending** | Requires live Azure SQL + DevOps connections |

---

## Remaining Steps

### Step 4: Azure SQL Database Setup

1. Go to <https://aka.ms/azuresqlhub> -> "Try for free"
2. Create logical server with SQL authentication (sqladmin)
3. Create database: `PatentIntelligence`
4. Configure firewall: Add client IP + Allow Azure services
5. Add credentials to `.env`:

```
AZURE_SQL_SERVER=yourserver.database.windows.net
AZURE_SQL_DATABASE=PatentIntelligence
AZURE_SQL_USER=sqladmin
AZURE_SQL_PASSWORD=yourpassword
```

6. Test connection:

```bash
sqlcmd -S $AZURE_SQL_SERVER -d $AZURE_SQL_DATABASE -U $AZURE_SQL_USER -P $AZURE_SQL_PASSWORD -Q "SELECT 1 AS connected"
```

### Step 5: Configure DBHub MCP

```bash
claude mcp add dbhub -- npx -y @bytebase/dbhub \
  --transport stdio \
  --dsn "sqlserver://sqladmin:YourPass@yourserver.database.windows.net:1433/PatentIntelligence?encrypt=true"
```

### Step 13: End-to-End Dry Run

1. Run the pre-demo wake-up and verify prompts
2. Paste the full XML demo prompt and run all 9 steps
3. Confirm: ticket created, table built, patents loaded, analysis complete, charts saved, ticket closed
