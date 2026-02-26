"""Azure Function: Daily Patent Sync

Timer-triggered function that runs daily at 7:31 AM UTC (12:31 AM MST).
Searches USPTO API for new patents since the last sync and loads them
into Azure SQL Database using MERGE upsert.

Environment variables (configure in Function App > Application Settings):
    USPTO_API_KEY, AZURE_SQL_SERVER, AZURE_SQL_DATABASE,
    AZURE_SQL_USER, AZURE_SQL_PASSWORD
"""

import json
import logging
import os
from datetime import date

import azure.functions as func
import pyodbc

from shared.patent_search import search_by_title
from shared.azure_sql_queries import (
    build_upsert_query,
    get_last_sync_date_query,
)

app = func.FunctionApp()

SEARCH_TOPICS = [
    "AI data processing",
    "predictive analytics",
    "business intelligence",
]


def _get_connection() -> pyodbc.Connection:
    """Connect to Azure SQL using ODBC Driver 17 (Azure Function runtime)."""
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.environ['AZURE_SQL_SERVER']};"
        f"DATABASE={os.environ['AZURE_SQL_DATABASE']};"
        f"UID={os.environ['AZURE_SQL_USER']};"
        f"PWD={os.environ['AZURE_SQL_PASSWORD']}"
    )


@app.timer_trigger(schedule="0 31 7 * * *", arg_name="timer", run_on_startup=False)
def daily_patent_sync(timer: func.TimerRequest) -> None:
    """Daily patent sync: search USPTO for new patents and load into Azure SQL."""
    logging.info("Starting daily patent sync")

    conn = _get_connection()
    cursor = conn.cursor()

    # Determine date range: last sync date -> today
    cursor.execute(get_last_sync_date_query())
    row = cursor.fetchone()
    if row and row.last_sync_date:
        from_date = str(row.last_sync_date)
    else:
        from_date = "2022-11-30"

    to_date = date.today().isoformat()
    logging.info(f"Sync range: {from_date} to {to_date}")

    merge_sql = build_upsert_query()
    total_loaded = 0

    for topic in SEARCH_TOPICS:
        results = search_by_title(
            topic,
            limit=100,
            filing_date_from=from_date,
            filing_date_to=to_date,
        )

        count = 0
        for p in results:
            try:
                params = (
                    p.get("patent_number", ""),
                    p.get("title", ""),
                    p.get("abstract", ""),
                    p.get("assignee", ""),
                    json.dumps(p.get("inventors", [])),
                    p.get("filing_date") or None,
                    p.get("grant_date") or None,
                    json.dumps(p.get("cpc_codes", [])),
                    topic,
                    "daily_sync",
                )
                cursor.execute(merge_sql, params)
                count += 1
            except Exception as e:
                logging.error(f"Error loading {p.get('patent_number', '?')}: {e}")

        logging.info(f"  {topic}: {count} patents")
        total_loaded += count

    conn.commit()

    # Log the sync
    cursor.execute(
        "INSERT INTO SYNC_LOG (filing_date_from, filing_date_to, patents_loaded, search_topics) "
        "VALUES (?, ?, ?, ?)",
        (from_date, to_date, total_loaded, ", ".join(SEARCH_TOPICS)),
    )
    conn.commit()

    cursor.close()
    conn.close()

    logging.info(f"Daily sync complete: {total_loaded} patents loaded")
