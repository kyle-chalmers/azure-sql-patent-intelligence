# Backup Commands

If Claude Code encounters issues during the demo, use these manual commands.

## 0. Create Azure DevOps Work Item

```bash
az boards work-item create \
  --title "Build Intel Patent Intelligence Pipeline" \
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
from tools.patent_search import search_by_assignee
import json
results = search_by_assignee('Intel Corporation', limit=50)
print(f'Found {len(results)} patents')
for p in results[:5]:
    print(f'  - {p[\"patent_number\"]}: {p[\"title\"][:60]}...')
"
```

## 4. Load Data (Python with pyodbc)

```bash
python3 -c "
import os, json, pyodbc
from dotenv import load_dotenv
from tools.patent_search import search_by_assignee

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

patents = search_by_assignee('Intel Corporation', limit=50)
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

for p in patents:
    cursor.execute(merge_sql, (
        p['patent_number'], p['title'], p.get('abstract', ''), p['assignee'],
        json.dumps(p.get('inventors', [])), p.get('filing_date'),
        p.get('grant_date'), json.dumps(p.get('cpc_codes', [])),
        'Intel Corporation', 'assignee_search'
    ))

conn.commit()
print(f'Loaded {len(patents)} patents')
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

## 8. Close Azure DevOps Work Item

```bash
# Replace <ID> with the work item ID from step 0
az boards work-item update \
  --id <ID> \
  --state Done \
  --discussion "Pipeline complete: PATENTS table created with indexes, Intel patents loaded via MERGE upserts, analysis run with OPENJSON, matplotlib visualizations generated, executive summary produced." \
  --output table
```

## 9. Cleanup (after demo)

```bash
sqlcmd -S $AZURE_SQL_SERVER -d $AZURE_SQL_DATABASE -U $AZURE_SQL_USER -P $AZURE_SQL_PASSWORD -Q "DROP TABLE IF EXISTS PATENTS;"
```
