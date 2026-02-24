# Backup Commands

If Claude Code encounters issues during the demo, use these manual commands.

## 0. Create Azure DevOps Work Item

```bash
az boards work-item create \
  --title "Build AI & Data Patent Intelligence Pipeline" \
  --type Task \
  --description "Build patent intelligence pipeline: schema creation, USPTO API search, data loading, T-SQL analysis, and visualization." \
  --output table
```

Note the ID from the output for step 8.

## 1. Connect to Azure SQL

```bash
sqlcmd -S $AZURE_SQL_SERVER -d $AZURE_SQL_DATABASE -U $AZURE_SQL_USER -P $AZURE_SQL_PASSWORD -Q "SELECT name FROM sys.tables"
```

## 2. Create PATENTS Table

```bash
sqlcmd -S $AZURE_SQL_SERVER -d $AZURE_SQL_DATABASE -U $AZURE_SQL_USER -P $AZURE_SQL_PASSWORD -Q "
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PATENTS')
CREATE TABLE PATENTS (
    patent_number NVARCHAR(50) NOT NULL PRIMARY KEY,
    title NVARCHAR(500),
    abstract NVARCHAR(MAX),
    assignee NVARCHAR(300),
    inventors NVARCHAR(MAX),
    filing_date DATE,
    grant_date DATE,
    cpc_codes NVARCHAR(MAX),
    search_query NVARCHAR(200),
    category NVARCHAR(100),
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);
CREATE INDEX IX_PATENTS_ASSIGNEE ON PATENTS (assignee);
CREATE INDEX IX_PATENTS_FILING_DATE ON PATENTS (filing_date);
"
```

## 3. Search USPTO API (Python)

```bash
python3 -c "
from tools.patent_search import search_by_title
import json

results_ai = search_by_title('AI data processing', limit=17)
results_pred = search_by_title('predictive analytics', limit=17)
results_bi = search_by_title('business intelligence', limit=16)
all_results = results_ai + results_pred + results_bi

print(f'Found {len(all_results)} patents total')
print(f'  AI data processing: {len(results_ai)}')
print(f'  Predictive analytics: {len(results_pred)}')
print(f'  Business intelligence: {len(results_bi)}')
for p in all_results[:5]:
    print(f'  - {p[\"patent_number\"]}: {p[\"title\"][:60]}...')
"
```

## 4. Load Data (Python with pyodbc)

```bash
python3 -c "
import os, json, pyodbc
from dotenv import load_dotenv
from tools.patent_search import search_by_title

load_dotenv()
conn_str = (
    f'DRIVER={{ODBC Driver 18 for SQL Server}};'
    f'SERVER={os.getenv(\"AZURE_SQL_SERVER\")};'
    f'DATABASE={os.getenv(\"AZURE_SQL_DATABASE\")};'
    f'UID={os.getenv(\"AZURE_SQL_USER\")};'
    f'PWD={os.getenv(\"AZURE_SQL_PASSWORD\")};'
    f'Encrypt=yes;TrustServerCertificate=no;'
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Search three AI & data topics
topics = [
    ('AI data processing', 17),
    ('predictive analytics', 17),
    ('business intelligence', 16),
]
all_patents = []
for topic, limit in topics:
    results = search_by_title(topic, limit=limit)
    for p in results:
        p['search_query'] = topic
        p['category'] = 'title_search'
    all_patents.extend(results)

merge_sql = '''
MERGE INTO PATENTS AS target
USING (SELECT ? AS patent_number, ? AS title, ? AS abstract, ? AS assignee,
       ? AS inventors, ? AS filing_date, ? AS grant_date, ? AS cpc_codes,
       ? AS search_query, ? AS category) AS source
ON target.patent_number = source.patent_number
WHEN MATCHED THEN UPDATE SET title=source.title, abstract=source.abstract,
    assignee=source.assignee, inventors=source.inventors, filing_date=source.filing_date,
    grant_date=source.grant_date, cpc_codes=source.cpc_codes, updated_at=GETDATE()
WHEN NOT MATCHED THEN INSERT (patent_number, title, abstract, assignee, inventors,
    filing_date, grant_date, cpc_codes, search_query, category, created_at, updated_at)
VALUES (source.patent_number, source.title, source.abstract, source.assignee,
    source.inventors, source.filing_date, source.grant_date, source.cpc_codes,
    source.search_query, source.category, GETDATE(), GETDATE());
'''

for p in all_patents:
    cursor.execute(merge_sql, (
        p['patent_number'], p['title'], p.get('abstract', ''), p['assignee'],
        json.dumps(p.get('inventors', [])), p.get('filing_date'),
        p.get('grant_date'), json.dumps(p.get('cpc_codes', [])),
        p.get('search_query', ''), p.get('category', 'title_search')
    ))

conn.commit()
print(f'Loaded {len(all_patents)} patents')
conn.close()
"
```

## 5. Analytical Queries

### Patent Count and Date Range
```bash
sqlcmd -S $AZURE_SQL_SERVER -d $AZURE_SQL_DATABASE -U $AZURE_SQL_USER -P $AZURE_SQL_PASSWORD -Q "
SELECT COUNT(*) AS total_patents, MIN(filing_date) AS earliest, MAX(filing_date) AS latest
FROM PATENTS;
"
```

### Filing Trends by Year
```bash
sqlcmd -S $AZURE_SQL_SERVER -d $AZURE_SQL_DATABASE -U $AZURE_SQL_USER -P $AZURE_SQL_PASSWORD -Q "
SELECT YEAR(filing_date) AS year, COUNT(*) AS patents
FROM PATENTS WHERE filing_date IS NOT NULL
GROUP BY YEAR(filing_date) ORDER BY year;
"
```

### Top Inventors (OPENJSON)
```bash
sqlcmd -S $AZURE_SQL_SERVER -d $AZURE_SQL_DATABASE -U $AZURE_SQL_USER -P $AZURE_SQL_PASSWORD -Q "
SELECT TOP 10 inventor.value AS inventor, COUNT(*) AS patents
FROM PATENTS CROSS APPLY OPENJSON(inventors) AS inventor
GROUP BY inventor.value ORDER BY patents DESC;
"
```

### CPC Code Breakdown (OPENJSON)
```bash
sqlcmd -S $AZURE_SQL_SERVER -d $AZURE_SQL_DATABASE -U $AZURE_SQL_USER -P $AZURE_SQL_PASSWORD -Q "
SELECT TOP 10 LEFT(cpc.value, 4) AS cpc_group, COUNT(*) AS patents
FROM PATENTS CROSS APPLY OPENJSON(cpc_codes) AS cpc
GROUP BY LEFT(cpc.value, 4) ORDER BY patents DESC;
"
```

## 5b. Backfill Patents Since ChatGPT Launch (Nov 30, 2022)

```bash
python3 -c "
import os, json, pyodbc
from dotenv import load_dotenv
from tools.patent_search import search_by_title

load_dotenv()
conn_str = (
    f'DRIVER={{ODBC Driver 18 for SQL Server}};'
    f'SERVER={os.getenv(\"AZURE_SQL_SERVER\")};'
    f'DATABASE={os.getenv(\"AZURE_SQL_DATABASE\")};'
    f'UID={os.getenv(\"AZURE_SQL_USER\")};'
    f'PWD={os.getenv(\"AZURE_SQL_PASSWORD\")};'
    f'Encrypt=yes;TrustServerCertificate=no;'
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

topics = ['AI data processing', 'predictive analytics', 'business intelligence']
merge_sql = '''
MERGE INTO PATENTS AS target
USING (SELECT ? AS patent_number, ? AS title, ? AS abstract, ? AS assignee,
       ? AS inventors, ? AS filing_date, ? AS grant_date, ? AS cpc_codes,
       ? AS search_query, ? AS category) AS source
ON target.patent_number = source.patent_number
WHEN MATCHED THEN UPDATE SET title=source.title, abstract=source.abstract,
    assignee=source.assignee, inventors=source.inventors, filing_date=source.filing_date,
    grant_date=source.grant_date, cpc_codes=source.cpc_codes, updated_at=GETDATE()
WHEN NOT MATCHED THEN INSERT (patent_number, title, abstract, assignee, inventors,
    filing_date, grant_date, cpc_codes, search_query, category, created_at, updated_at)
VALUES (source.patent_number, source.title, source.abstract, source.assignee,
    source.inventors, source.filing_date, source.grant_date, source.cpc_codes,
    source.search_query, source.category, GETDATE(), GETDATE());
'''

total = 0
for topic in topics:
    offset = 0
    while True:
        batch = search_by_title(topic, limit=100, filing_date_from='2022-11-30', start=offset)
        if not batch:
            break
        for p in batch:
            cursor.execute(merge_sql, (
                p['patent_number'], p['title'], p.get('abstract', ''), p['assignee'],
                json.dumps(p.get('inventors', [])), p.get('filing_date'),
                p.get('grant_date'), json.dumps(p.get('cpc_codes', [])),
                topic, 'backfill'
            ))
        total += len(batch)
        offset += len(batch)
        if len(batch) < 100:
            break
    conn.commit()

print(f'Backfill complete: {total} patents loaded since 2022-11-30')
conn.close()
"
```

## 5c. Daily Sync — Create SYNC_LOG Table and Run Sync

```bash
# Create SYNC_LOG table
sqlcmd -S $AZURE_SQL_SERVER -d $AZURE_SQL_DATABASE -U $AZURE_SQL_USER -P $AZURE_SQL_PASSWORD -Q "
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'SYNC_LOG')
CREATE TABLE SYNC_LOG (
    sync_id INT IDENTITY(1,1) PRIMARY KEY,
    sync_date DATETIME2 DEFAULT GETDATE(),
    filing_date_from DATE,
    filing_date_to DATE,
    patents_loaded INT,
    search_topics NVARCHAR(500),
    sync_status NVARCHAR(50) DEFAULT 'completed'
);
"
```

```bash
# Run daily sync
python3 -c "
import os, json, pyodbc
from datetime import date
from dotenv import load_dotenv
from tools.patent_search import search_by_title

load_dotenv()
conn_str = (
    f'DRIVER={{ODBC Driver 18 for SQL Server}};'
    f'SERVER={os.getenv(\"AZURE_SQL_SERVER\")};'
    f'DATABASE={os.getenv(\"AZURE_SQL_DATABASE\")};'
    f'UID={os.getenv(\"AZURE_SQL_USER\")};'
    f'PWD={os.getenv(\"AZURE_SQL_PASSWORD\")};'
    f'Encrypt=yes;TrustServerCertificate=no;'
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Get last sync date
cursor.execute('''
    SELECT TOP 1 filing_date_to FROM SYNC_LOG
    WHERE sync_status = \'completed\' ORDER BY sync_date DESC
''')
row = cursor.fetchone()
last_date = str(row[0]) if row else '2022-11-30'
today = str(date.today())

topics = ['AI data processing', 'predictive analytics', 'business intelligence']
merge_sql = '''
MERGE INTO PATENTS AS target
USING (SELECT ? AS patent_number, ? AS title, ? AS abstract, ? AS assignee,
       ? AS inventors, ? AS filing_date, ? AS grant_date, ? AS cpc_codes,
       ? AS search_query, ? AS category) AS source
ON target.patent_number = source.patent_number
WHEN MATCHED THEN UPDATE SET title=source.title, abstract=source.abstract,
    assignee=source.assignee, inventors=source.inventors, filing_date=source.filing_date,
    grant_date=source.grant_date, cpc_codes=source.cpc_codes, updated_at=GETDATE()
WHEN NOT MATCHED THEN INSERT (patent_number, title, abstract, assignee, inventors,
    filing_date, grant_date, cpc_codes, search_query, category, created_at, updated_at)
VALUES (source.patent_number, source.title, source.abstract, source.assignee,
    source.inventors, source.filing_date, source.grant_date, source.cpc_codes,
    source.search_query, source.category, GETDATE(), GETDATE());
'''

total = 0
for topic in topics:
    results = search_by_title(topic, limit=100, filing_date_from=last_date, filing_date_to=today)
    for p in results:
        cursor.execute(merge_sql, (
            p['patent_number'], p['title'], p.get('abstract', ''), p['assignee'],
            json.dumps(p.get('inventors', [])), p.get('filing_date'),
            p.get('grant_date'), json.dumps(p.get('cpc_codes', [])),
            topic, 'daily_sync'
        ))
    total += len(results)

conn.commit()
cursor.execute('''
    INSERT INTO SYNC_LOG (filing_date_from, filing_date_to, patents_loaded, search_topics)
    VALUES (?, ?, ?, ?)
''', (last_date, today, total, ', '.join(topics)))
conn.commit()
print(f'Daily sync complete: {total} patents loaded ({last_date} to {today})')
conn.close()
"
```

## 5d. Create & Deploy Azure Function

> The `azure_function/` directory is built from scratch by Claude Code during the live demo.
> If you need to create it manually, it should contain: `function_app.py` (timer trigger),
> `host.json`, `requirements.txt`, and `shared/` (with `patent_search.py` and `azure_sql_queries.py`).

```bash
# Deploy the daily sync function to Azure
cd azure_function && func azure functionapp publish patent-sync-func --python
```

```bash
# Verify the function is registered
az functionapp function show \
  --name patent-sync-func \
  --resource-group patent-intelligence-rg \
  --function-name daily_patent_sync \
  --output table
```

```bash
# (Optional) Manually trigger the function to test
az functionapp function invoke \
  --name patent-sync-func \
  --resource-group patent-intelligence-rg \
  --function-name daily_patent_sync
```

```bash
# (Optional) Stream live logs
func azure functionapp logstream patent-sync-func
```

## 8. Close Azure DevOps Work Item

```bash
# Replace <ID> with the work item ID from step 0
az boards work-item update \
  --id <ID> \
  --state Done \
  --discussion "Pipeline complete: PATENTS table created with indexes, AI & data patents loaded via MERGE upserts across 3 topics, analysis run with OPENJSON, matplotlib visualizations generated, executive summary produced." \
  --output table
```

## 9. Cleanup (after demo)

```bash
sqlcmd -S $AZURE_SQL_SERVER -d $AZURE_SQL_DATABASE -U $AZURE_SQL_USER -P $AZURE_SQL_PASSWORD -Q "DROP TABLE IF EXISTS PATENTS;"
```
