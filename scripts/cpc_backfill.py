"""Exhaustive patent collection by CPC (Cooperative Patent Classification) codes.

Collects AI & data patents by examiner-assigned CPC codes using the
USPTO ODP API. Uses monthly windows with pagination for thorough coverage.

Usage:
    python scripts/cpc_backfill.py

Requires: pyodbc, python-dotenv
"""

import json
import os
import sys
import time
from datetime import date, timedelta

import pyodbc
from dotenv import load_dotenv

# Add project root to path for tools/ imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from tools.patent_search import search_by_cpc
from tools.azure_sql_queries import build_upsert_query

# --- Configuration ---
DATE_FROM = "2025-01-01"
DATE_TO = date.today().isoformat()
MAX_PAGES_PER_WINDOW = 20  # 20 pages x 25 results = 500 max per window
API_PAGE_SIZE = 25  # empirical max per page
SLEEP_BETWEEN_CALLS = 0.5  # seconds
CATEGORY = "cpc_collection"

# CPC codes ordered by AI-specificity (highest priority first).
# G06F sub-codes omitted — Lucene can't reliably query them due to
# space-separated format in the API. G06F patents are still captured
# when cross-classified with these 5 codes (very common for AI patents).
CPC_CODES = {
    "G06N": "AI/ML computing — neural networks, machine learning",
    "G06Q": "Business data processing / BI systems",
    "G06V": "Image/video recognition",
    "G10L": "Speech analysis and recognition",
    "G16H": "Healthcare informatics / AI in medicine",
}


def generate_monthly_windows(start_date: str, end_date: str) -> list[tuple[str, str]]:
    """Generate (month_start, month_end) tuples covering the date range."""
    windows = []
    d = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    while d <= end:
        month_start = d.replace(day=1)
        if d.month == 12:
            month_end = date(d.year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(d.year, d.month + 1, 1) - timedelta(days=1)
        if month_end > end:
            month_end = end
        windows.append((month_start.isoformat(), month_end.isoformat()))
        # Advance to next month
        if d.month == 12:
            d = date(d.year + 1, 1, 1)
        else:
            d = date(d.year, d.month + 1, 1)

    return windows


def get_connection() -> pyodbc.Connection:
    """Connect to Azure SQL Database."""
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={os.environ['AZURE_SQL_SERVER']};"
        f"DATABASE={os.environ['AZURE_SQL_DATABASE']};"
        f"UID={os.environ['AZURE_SQL_USER']};"
        f"PWD={os.environ['AZURE_SQL_PASSWORD']};"
        "Connection Timeout=120;"
    )


def collect_cpc_window(cpc_code: str, month_start: str, month_end: str) -> list[dict]:
    """Collect all patents for one CPC code in one month window."""
    all_results = []
    seen_ids = set()

    for page in range(MAX_PAGES_PER_WINDOW):
        offset = page * API_PAGE_SIZE
        try:
            results = search_by_cpc(
                cpc_code,
                limit=100,
                filing_date_from=month_start,
                filing_date_to=month_end,
                start=offset,
            )
        except Exception as e:
            print(f"    API error page {page}: {e}")
            break

        if not results:
            break

        for patent in results:
            pid = patent.get("patent_number", "")
            if pid and pid not in seen_ids:
                seen_ids.add(pid)
                all_results.append(patent)

        if len(results) < API_PAGE_SIZE:
            break  # Last page

        time.sleep(SLEEP_BETWEEN_CALLS)

    return all_results


def main():
    conn = get_connection()
    cursor = conn.cursor()
    merge_sql = build_upsert_query()
    windows = generate_monthly_windows(DATE_FROM, DATE_TO)

    print(f"CPC Backfill: {len(windows)} monthly windows x {len(CPC_CODES)} codes")
    print(f"Date range: {DATE_FROM} to {DATE_TO}\n")

    grand_total = 0
    global_seen = set()  # Dedup across all CPC codes
    cpc_counts = {}

    for cpc_code, description in CPC_CODES.items():
        cpc_total = 0
        print(f"{'='*60}")
        print(f"CPC {cpc_code}: {description}")
        print(f"{'='*60}")

        for month_start, month_end in windows:
            patents = collect_cpc_window(cpc_code, month_start, month_end)

            loaded = 0
            for p in patents:
                pid = p.get("patent_number", "")
                if not pid:
                    continue

                global_seen.add(pid)

                params = (
                    pid,
                    p.get("title", ""),
                    p.get("abstract", ""),
                    p.get("assignee", ""),
                    json.dumps(p.get("inventors", [])),
                    p.get("filing_date") or None,
                    p.get("grant_date") or None,
                    json.dumps(p.get("cpc_codes", [])),
                    f"CPC:{cpc_code}",
                    CATEGORY,
                )
                try:
                    cursor.execute(merge_sql, params)
                    loaded += 1
                except Exception as e:
                    print(f"    MERGE error {pid}: {e}")

            conn.commit()
            cpc_total += loaded
            if loaded > 0:
                print(f"  {month_start[:7]}: {loaded} patents")

        grand_total += cpc_total
        cpc_counts[cpc_code] = cpc_total
        print(f"  Subtotal: {cpc_total}\n")

    # Log to SYNC_LOG
    cursor.execute(
        "INSERT INTO SYNC_LOG (filing_date_from, filing_date_to, "
        "patents_loaded, search_topics, sync_status) "
        "VALUES (?, ?, ?, ?, ?)",
        (DATE_FROM, DATE_TO, grand_total,
         ", ".join(f"CPC:{c}" for c in CPC_CODES), "completed"),
    )
    conn.commit()

    # Final summary
    cursor.execute("SELECT COUNT(*) FROM PATENTS")
    total_in_db = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    print(f"{'='*60}")
    print(f"CPC Collection Complete")
    print(f"{'='*60}")
    print(f"  Unique patents seen: {len(global_seen)}")
    print(f"  Total MERGE operations: {grand_total}")
    for code, count in cpc_counts.items():
        print(f"    CPC:{code}: {count}")
    print(f"  Total patents in DB: {total_in_db}")


if __name__ == "__main__":
    main()
