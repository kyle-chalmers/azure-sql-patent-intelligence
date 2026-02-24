"""Generate visualization charts from patent analysis data."""
import pyodbc
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()

conn = pyodbc.connect(
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={os.environ['AZURE_SQL_SERVER']};"
    f"DATABASE={os.environ['AZURE_SQL_DATABASE']};"
    f"UID={os.environ['AZURE_SQL_USER']};"
    f"PWD={os.environ['AZURE_SQL_PASSWORD']}"
)
cursor = conn.cursor()

# --- Chart 1: Filing Trends by Year ---
cursor.execute("""
SELECT YEAR(filing_date) AS filing_year, COUNT(*) AS patent_count
FROM PATENTS WHERE filing_date IS NOT NULL
GROUP BY YEAR(filing_date) ORDER BY filing_year
""")
rows = cursor.fetchall()
years = [str(r[0]) for r in rows]
counts = [r[1] for r in rows]

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(years, counts, color='#0071C5', edgecolor='white')
ax.set_xlabel('Filing Year', fontsize=12)
ax.set_ylabel('Number of Patents', fontsize=12)
ax.set_title('Intel Corporation — Patent Filing Trends by Year', fontsize=14, fontweight='bold')
for bar, count in zip(bars, counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, str(count),
            ha='center', va='bottom', fontweight='bold', fontsize=11)
ax.set_ylim(0, max(counts) * 1.15)
plt.tight_layout()
plt.savefig('output/filing_trends.png', dpi=150, bbox_inches='tight')
print('Saved: output/filing_trends.png')
plt.close()

# --- Chart 2: CPC Breakdown (Horizontal Bar) ---
cursor.execute("""
SELECT TOP 10 LEFT(cpc.value, 4) AS cpc_group, COUNT(*) AS patent_count
FROM PATENTS CROSS APPLY OPENJSON(cpc_codes) AS cpc
GROUP BY LEFT(cpc.value, 4) ORDER BY patent_count DESC
""")
rows = cursor.fetchall()
cpc_groups = [r[0] for r in rows]
cpc_counts = [r[1] for r in rows]

cpc_labels = {
    "H01L": "Semiconductor Devices",
    "G06F": "Digital Data Processing",
    "H04L": "Digital Transmission",
    "G06N": "AI/ML Computing",
    "H10D": "Semiconductor (Next-Gen)",
    "H04W": "Wireless Communication",
    "G11C": "Information Storage",
    "G06T": "Image Processing",
    "G06Q": "Business Data Processing",
    "H04J": "Multiplex Communication",
    "H04B": "Transmission Systems",
}
labels = [f"{g} — {cpc_labels.get(g, g)}" for g in cpc_groups]

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(labels[::-1], cpc_counts[::-1], color='#0071C5', edgecolor='white')
ax.set_xlabel('Number of Patents', fontsize=12)
ax.set_title('Intel Corporation — Technology Focus Areas (CPC Codes)', fontsize=14, fontweight='bold')
for bar, count in zip(bars, cpc_counts[::-1]):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2, str(count),
            ha='left', va='center', fontweight='bold', fontsize=10)
ax.set_xlim(0, max(cpc_counts) * 1.15)
plt.tight_layout()
plt.savefig('output/cpc_breakdown.png', dpi=150, bbox_inches='tight')
print('Saved: output/cpc_breakdown.png')
plt.close()

cursor.close()
conn.close()
print("Charts generated successfully!")
