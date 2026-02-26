"""Generate patent analysis charts from Azure SQL data.

Connects to Azure SQL Database, runs analytical queries, and produces
matplotlib charts saved to the output/ directory.

Usage:
    python output/generate_charts.py

Requires: matplotlib, pyodbc, python-dotenv
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pyodbc
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")


def get_connection() -> pyodbc.Connection:
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={os.environ['AZURE_SQL_SERVER']};"
        f"DATABASE={os.environ['AZURE_SQL_DATABASE']};"
        f"UID={os.environ['AZURE_SQL_USER']};"
        f"PWD={os.environ['AZURE_SQL_PASSWORD']};"
        "Connection Timeout=120;"
    )


def generate_filing_trends(cursor):
    """Bar chart of patent filing counts by month."""
    cursor.execute("""
        SELECT FORMAT(filing_date, 'yyyy-MM') AS filing_month, COUNT(*) AS cnt
        FROM PATENTS WHERE filing_date IS NOT NULL
        GROUP BY FORMAT(filing_date, 'yyyy-MM')
        ORDER BY filing_month
    """)
    rows = cursor.fetchall()
    months = [r[0] for r in rows]
    counts = [r[1] for r in rows]

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(months, counts, color="#2563eb", edgecolor="white")
    ax.set_xlabel("Filing Month", fontsize=12)
    ax.set_ylabel("Patent Count", fontsize=12)
    ax.set_title("AI & Data Patent Filing Trends (2025-2026)", fontsize=14, fontweight="bold")
    plt.xticks(rotation=45, ha="right")
    for bar, count in zip(bars, counts):
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + 1,
            str(count),
            ha="center",
            va="bottom",
            fontsize=9,
        )
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "filing_trends.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


def generate_cpc_breakdown(cursor):
    """Horizontal bar chart of top 10 CPC technology categories."""
    cursor.execute("""
        SELECT TOP 10 LEFT(cpc.value, 4) AS cpc_group, COUNT(*) AS patent_count
        FROM PATENTS CROSS APPLY OPENJSON(cpc_codes) AS cpc
        GROUP BY LEFT(cpc.value, 4)
        ORDER BY patent_count DESC
    """)
    rows = cursor.fetchall()
    cpc_labels = [r[0] for r in rows]
    cpc_counts = [r[1] for r in rows]

    # CPC code descriptions for readability
    cpc_desc = {
        "G06F": "Digital Data Processing",
        "G06N": "AI/ML Computing",
        "H04L": "Digital Transmission",
        "H04N": "Image Communication",
        "G06Q": "Business Data Processing",
        "G06T": "Image Processing",
        "A61B": "Medical Diagnostics",
        "G06V": "Image Recognition",
        "H04W": "Wireless Networks",
        "G16H": "Healthcare Informatics",
    }
    labels = [f"{c}\n{cpc_desc.get(c, '')}" for c in cpc_labels]

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = plt.cm.Set3(range(len(cpc_labels)))
    bars = ax.barh(labels[::-1], cpc_counts[::-1], color=colors[::-1], edgecolor="white")
    ax.set_xlabel("Patent Count", fontsize=12)
    ax.set_title("Top 10 Technology Categories (CPC Codes)", fontsize=14, fontweight="bold")
    for bar, count in zip(bars, cpc_counts[::-1]):
        ax.text(
            bar.get_width() + 5,
            bar.get_y() + bar.get_height() / 2.0,
            str(count),
            ha="left",
            va="center",
            fontsize=9,
        )
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "cpc_breakdown.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


if __name__ == "__main__":
    conn = get_connection()
    cursor = conn.cursor()

    generate_filing_trends(cursor)
    generate_cpc_breakdown(cursor)

    cursor.close()
    conn.close()
    print("Done.")
