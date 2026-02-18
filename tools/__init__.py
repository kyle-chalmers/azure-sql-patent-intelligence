"""Azure SQL Patent Intelligence tools.

This module exports the public API for patent search, Azure SQL query builders,
and analysis workflow functions.
"""

from tools.patent_search import (
    search_by_assignee,
    search_by_title,
    get_patent,
    SAMPLE_PATENTS,
)

from tools.azure_sql_queries import (
    build_create_table_sql,
    build_upsert_query,
    get_trends_query,
    get_top_inventors_query,
    get_cpc_breakdown_query,
)

# Intel Corporation CPC codes (most relevant technology areas)
INTEL_CPC_CODES = {
    "H01L": "Semiconductor devices (Intel's core)",
    "G06F": "Electric digital data processing",
    "H04L": "Digital information transmission",
    "G06N": "Computing arrangements - AI/ML",
}

__all__ = [
    # Patent search functions
    "search_by_assignee",
    "search_by_title",
    "get_patent",
    "SAMPLE_PATENTS",
    # Azure SQL query builders
    "build_create_table_sql",
    "build_upsert_query",
    "get_trends_query",
    "get_top_inventors_query",
    "get_cpc_breakdown_query",
    # Constants
    "INTEL_CPC_CODES",
]
