# Implementation Plan: Azure SQL Patent Intelligence Demo

## Implementation Progress

| Step | Status | Notes |
|------|--------|-------|
| 1. Create repo structure | [x] Done | Directory created with all subdirectories |
| 2. USPTO API key setup | [x] Done | .env.example created with instructions |
| 3. Test USPTO API | [ ] Pending | Requires Kyle's API key in .env |
| 4. Azure SQL setup | [ ] Pending | Requires Azure portal setup by Kyle |
| 5. Configure MCP + CLI | [ ] Pending | Requires live Azure SQL connection |
| 6. Create code files | [x] Done | patent_search.py, azure_sql_queries.py, __init__.py |
| 7. Create demo prompt | [x] Done | demo/demo_prompt.md + backup_commands.md |
| 8. Create README.md | [x] Done | Full audience-facing documentation |
| 9. Create PRESENTATION_GUIDE.md | [x] Done | .internal/PRESENTATION_GUIDE.md |
| 10. Presentation flow | [x] Done | Documented in presentation guide |
| 11. Additional elements | [x] Done | Cost table, security Q&A, manual comparison |
| 12. End-to-end verification | [ ] Pending | Requires live API + DB connections |

---

## Remaining Steps (Require Kyle's Action)

### Step 3: Test USPTO API
Once `.env` is configured with a real API key:
```bash
python3 -c "from tools.patent_search import search_by_assignee; results = search_by_assignee('Intel Corporation', limit=5); print(f'Found {len(results)} patents')"
```

### Step 4: Azure SQL Database Setup
1. Go to https://aka.ms/azuresqlhub -> "Try for free"
2. Create logical server with SQL authentication (sqladmin)
3. Create database: PatentIntelligence
4. Configure firewall: Add client IP + Allow Azure services
5. Test: `sqlcmd -S server -d PatentIntelligence -U sqladmin -P pass -Q "SELECT 1"`

### Step 5: Configure DBHub MCP
```bash
claude mcp add dbhub -- npx -y @bytebase/dbhub \
  --transport stdio \
  --dsn "sqlserver://sqladmin:YourPass@yourserver.database.windows.net:1433/PatentIntelligence?encrypt=true"
```

### Step 12: End-to-End Verification
Run the full demo prompt in Claude Code and verify all 7 steps complete successfully.

---

## QR Codes Needed
Generate QR codes for:
- LinkedIn: https://www.linkedin.com/in/kylechalmers/
- YouTube: https://www.youtube.com/channel/UCkRi29nXFxNBuPhjseoB6AQ
- GitHub repo: https://github.com/kyle-chalmers/azure-sql-patent-intelligence

Save as PNG files in `qr_codes/` directory.
