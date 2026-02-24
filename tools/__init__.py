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
    build_create_sync_log_sql,
    get_last_sync_date_query,
)

# AI & Data processing CPC codes (most relevant technology areas)
AI_DATA_CPC_CODES = {
    "G06N": "AI/ML computing — neural networks, machine learning",
    "G06F": "Electric digital data processing",
    "G06Q": "Business data processing / BI systems",
    "G06V": "Image/video recognition",
    "G10L": "Speech analysis and recognition",
    "G16H": "Healthcare informatics / AI in medicine",
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
    "build_create_sync_log_sql",
    "get_last_sync_date_query",
    # Constants
    "AI_DATA_CPC_CODES",
]
