"""Load Intel patents into Azure SQL Database using MERGE upserts."""
import json
import os
import pyodbc
from dotenv import load_dotenv
from tools.patent_search import search_by_assignee
from tools.azure_sql_queries import build_upsert_query

load_dotenv()

# Connect to Azure SQL
conn = pyodbc.connect(
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={os.environ['AZURE_SQL_SERVER']};"
    f"DATABASE={os.environ['AZURE_SQL_DATABASE']};"
    f"UID={os.environ['AZURE_SQL_USER']};"
    f"PWD={os.environ['AZURE_SQL_PASSWORD']}"
)
cursor = conn.cursor()
print("Connected to Azure SQL Database")

# Search for Intel patents
print("\nSearching USPTO for Intel patents...")
patents = search_by_assignee("Intel", limit=50)
print(f"Found {len(patents)} patents to load")

# Get the MERGE upsert query
upsert_sql = build_upsert_query()

# Load each patent
loaded = 0
for i, patent in enumerate(patents, 1):
    params = (
        patent.get("patent_number", ""),
        patent.get("title", ""),
        patent.get("abstract", ""),
        patent.get("assignee", ""),
        json.dumps(patent.get("inventors", [])),
        patent.get("filing_date") or None,
        patent.get("grant_date") or None,
        json.dumps(patent.get("cpc_codes", [])),
        "Intel",  # search_query
        "semiconductor",  # category
    )
    try:
        cursor.execute(upsert_sql, params)
        loaded += 1
        print(f"  [{i}/{len(patents)}] {patent.get('patent_number', 'N/A')} - {patent.get('title', 'N/A')[:60]}")
    except Exception as e:
        print(f"  [{i}/{len(patents)}] ERROR: {e}")

conn.commit()
cursor.close()
conn.close()

print(f"\nDone! Loaded {loaded}/{len(patents)} patents into PATENTS table.")
