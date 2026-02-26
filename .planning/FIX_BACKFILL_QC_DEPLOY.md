# Plan: Fix Backfill, QC, and Deploy Azure Function

## Context

The initial pipeline execution completed Steps 0-8, but three issues remain:

1. **Backfill failed silently** — The `_format_uspto_patent` function uses `earliestPublicationNumber` as the patent PK, but this field is **empty for most patent applications** that haven't been published yet. Raw API inspection confirmed all 25 results had `patent_number=''`, causing everything to collapse to a single row on MERGE upsert. The database has only 44 patents instead of hundreds.

2. **Azure Function not deployed** — The `azure_function/` code is built but the resource group doesn't exist and `func` CLI isn't installed.

3. **No QC guidance** — User needs Azure Portal links, SQL queries, and instructions to verify the pipeline output.

### Root Cause (Verified)

Raw API dump of `applicationMetaData` keys revealed:

- `earliestPublicationNumber` — inside `applicationMetaData`, **often empty** for pending applications
- `applicationNumberText` — at the **top level** of the response (NOT inside `applicationMetaData`), e.g. `'19255999'` — **always present and unique**

The `_format_uspto_patent(app)` function receives the full `app` dict but only looks inside `app["applicationMetaData"]` for the ID. It never checks `app["applicationNumberText"]`.

### Backfill Scope (Jan 1, 2025 -> today)

Tested API volume per topic for 2025:

- `"AI data processing"`: 14,103 total (broad, many irrelevant)
- `"predictive analytics"`: 302-394 total (focused)
- `"business intelligence"`: 1,320 total (moderate)

API returns max 25 results per page. With pagination, a reasonable backfill covers ~500-1000 unique patents across all 3 topics. Monthly windows + pagination will ensure thorough coverage.

---

## Part 1: Fix `patent_search.py` — Reliable Unique ID

### File: `tools/patent_search.py`

**Change 1**: `_format_uspto_patent` (line 199) — use `applicationNumberText` as fallback ID

Current (broken):

```python
def _format_uspto_patent(app: dict) -> Optional[dict]:
    meta = app.get("applicationMetaData", {})
    ...
    return {
        "patent_number": meta.get("earliestPublicationNumber", ""),
        ...
    }
```

Fixed:

```python
def _format_uspto_patent(app: dict) -> Optional[dict]:
    meta = app.get("applicationMetaData", {})
    ...
    # Use publication number if available, fall back to application number
    patent_id = meta.get("earliestPublicationNumber", "")
    if not patent_id:
        patent_id = app.get("applicationNumberText", "")
    ...
    return {
        "patent_number": patent_id,
        ...
    }
```

**Change 2**: `_search_uspto_odp` (line 141) — skip results with no usable ID

After the `_format_uspto_patent` call (line 177), add a guard:

```python
patent = _format_uspto_patent(app)
if patent and patent.get("patent_number"):  # Skip if no usable ID
    results.append(patent)
```

**Change 3**: Copy fixed file to `azure_function/shared/patent_search.py`

---

## Part 2: Historical Backfill (Jan 1, 2025 -> today)

### Strategy: Monthly Windows with Pagination

Break the date range into monthly chunks to work around the 25-per-page API limit and get broader coverage. For each month x topic:

1. Call `search_by_title(topic, limit=100, filing_date_from=month_start, filing_date_to=month_end, start=0)`
2. If 25 results returned (page full), paginate: increment `start` by 25, fetch next page
3. Continue until fewer than 25 returned or 5 pages reached (125 patents per month/topic cap to avoid runaway)
4. Dedup by `patent_number` in Python before MERGE upsert
5. Tag `category='backfill'`
6. Commit after each month, print running totals

### Expected Volume

~14 months x 3 topics x ~25-100 per window = **500-1500 unique patents** after dedup. This is well within Azure SQL free-tier capacity and should take ~5-10 minutes of API calls.

### Post-Backfill

- Update SYNC_LOG with the backfill run
- Re-run the 4 analytical queries to refresh results
- Regenerate matplotlib charts with richer data
- Print new summary stats

---

## Part 3: Provision & Deploy Azure Function

### 3a: Install Azure Functions Core Tools

```bash
brew install azure-functions-core-tools@4
```

### 3b: Provision Azure Resources

```bash
# 1. Create resource group (use same region as SQL server)
az group create --name <resource-group> --location <region>

# 2. Create storage account
az storage account create \
  --resource-group <resource-group> \
  --name <storage-account> \
  --location <region> --sku Standard_LRS

# 3. Create Function App (Python 3.10, Consumption plan)
az functionapp create \
  --resource-group <resource-group> \
  --consumption-plan-location <region> \
  --runtime python --runtime-version 3.10 \
  --functions-version 4 \
  --name <function-app-name> \
  --storage-account <storage-account>
```

### 3c: Configure Application Settings

```bash
source .env && az functionapp config appsettings set \
  --resource-group <resource-group> \
  --name <function-app-name> \
  --settings \
    USPTO_API_KEY="$USPTO_API_KEY" \
    AZURE_SQL_SERVER="$AZURE_SQL_SERVER" \
    AZURE_SQL_DATABASE="$AZURE_SQL_DATABASE" \
    AZURE_SQL_USER="$AZURE_SQL_USER" \
    AZURE_SQL_PASSWORD="$AZURE_SQL_PASSWORD"
```

### 3d: Deploy

```bash
cd azure_function && func azure functionapp publish <function-app-name> --python
```

### 3e: Verify

```bash
# Check function registered
az functionapp function show --name <function-app-name> \
  --resource-group <resource-group> \
  --function-name daily_patent_sync --output table

# Stream logs
func azure functionapp logstream <function-app-name>
```

Note: ODBC Driver 17 is used in the Function code (not 18) — the Consumption plan Python 3.10 image ships with Driver 17.

---

## Part 4: QC — Queries and Verification Guide

### QC SQL Queries (run in Azure Portal Query Editor)

```sql
-- QC 1: Total patents, date range, assignee count
SELECT COUNT(*) AS total_patents,
       MIN(filing_date) AS earliest_filing,
       MAX(filing_date) AS latest_filing,
       COUNT(DISTINCT assignee) AS unique_assignees
FROM PATENTS;

-- QC 2: Patents by category (should show title_search, backfill, daily_sync)
SELECT category, COUNT(*) AS cnt
FROM PATENTS GROUP BY category ORDER BY cnt DESC;

-- QC 3: Patents by search topic
SELECT search_query, COUNT(*) AS cnt
FROM PATENTS GROUP BY search_query ORDER BY cnt DESC;

-- QC 4: Filing trends by month (granular view for backfill verification)
SELECT FORMAT(filing_date, 'yyyy-MM') AS filing_month, COUNT(*) AS cnt
FROM PATENTS WHERE filing_date IS NOT NULL
GROUP BY FORMAT(filing_date, 'yyyy-MM')
ORDER BY filing_month;

-- QC 5: Check for empty/null patent_numbers (should be 0)
SELECT COUNT(*) AS empty_ids FROM PATENTS
WHERE patent_number IS NULL OR patent_number = '';

-- QC 6: Check for duplicates (should be 0)
SELECT patent_number, COUNT(*) AS cnt
FROM PATENTS GROUP BY patent_number HAVING COUNT(*) > 1;

-- QC 7: SYNC_LOG history
SELECT * FROM SYNC_LOG ORDER BY sync_date DESC;

-- QC 8: Sample patents (spot-check titles and data quality)
SELECT TOP 10 patent_number, title, assignee, filing_date, search_query, category
FROM PATENTS ORDER BY filing_date DESC;
```

### What to Check in the UI

1. **Azure Portal > SQL Query Editor**: Log in with sqladmin credentials, run QC queries above
   - Verify `total_patents` is in the hundreds (not 44)
   - Verify `earliest_filing` is in early 2025
   - Verify `empty_ids` = 0 and no duplicates
   - Check `filing_month` distribution — should have entries for every month in 2025
2. **Azure DevOps**: Open Board, confirm pipeline work item is in "Done" column
3. **Function App** (after deploy): Monitor tab > Invocations, or use logstream

---

## Execution Order

1. **Output QC links + queries FIRST** (Part 4) — so user can verify current state in the portal while remaining steps execute
2. **Fix `patent_search.py`** — unique ID fallback (Part 1)
3. **Backfill** — monthly windows with pagination, Jan 2025 -> today (Part 2)
4. **Re-run analytics** — refresh queries, charts, summary (reuse existing sql/ files)
5. **Provision & deploy Function App** — az CLI commands (Part 3)
6. **Output updated QC results** — post-backfill verification

---

## Files Modified

| File | Change |
| ---- | ------ |
| `tools/patent_search.py` | Add `applicationNumberText` fallback for patent_number |
| `azure_function/shared/patent_search.py` | Mirror the same fix |
| `sql/08_qc_queries.sql` | New — QC verification queries |
| `output/filing_trends.png` | Regenerated with backfill data |
| `output/cpc_breakdown.png` | Regenerated with backfill data |

---

## Verification

- After Part 1: Run `search_by_title("predictive analytics", limit=5, filing_date_from="2025-03-01")` and confirm all results have non-empty `patent_number`
- After Part 2: `SELECT COUNT(*) FROM PATENTS` should be in the hundreds; `SELECT COUNT(*) WHERE patent_number = ''` should be 0
- After Part 3: `az functionapp function show` returns the function details
- After Part 4: Provide all links and queries; user runs QC in portal
