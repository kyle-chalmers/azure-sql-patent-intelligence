"""Azure SQL (T-SQL) query builders for patent data.

This module provides functions to generate T-SQL queries for:
- Creating the PATENTS table with proper indexes
- Upserting patent records using MERGE
- Analyzing filing trends, inventors, and CPC codes
- JSON handling via OPENJSON and CROSS APPLY

Key T-SQL adaptations from Snowflake:
    Snowflake VARIANT     -> NVARCHAR(MAX) (JSON as string)
    PARSE_JSON()          -> N/A (store as string, query with OPENJSON())
    ILIKE                 -> LIKE (Azure SQL default collation is case-insensitive)
    CURRENT_TIMESTAMP()   -> GETDATE()
    LIMIT N               -> TOP N
    TIMESTAMP             -> DATETIME2
"""
import json


def build_create_table_sql() -> str:
    """Generate T-SQL CREATE TABLE statement for PATENTS table.

    Returns:
        T-SQL DDL string with table creation and index statements
    """
    return """
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PATENTS')
CREATE TABLE PATENTS (
    patent_number NVARCHAR(50) NOT NULL PRIMARY KEY,
    title NVARCHAR(500),
    abstract NVARCHAR(MAX),
    assignee NVARCHAR(300),
    inventors NVARCHAR(MAX),       -- JSON array stored as string
    filing_date DATE,
    grant_date DATE,
    cpc_codes NVARCHAR(MAX),       -- JSON array stored as string
    search_query NVARCHAR(200),
    category NVARCHAR(100),
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);

-- Indexes for common query patterns
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_PATENTS_ASSIGNEE')
    CREATE INDEX IX_PATENTS_ASSIGNEE ON PATENTS (assignee);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_PATENTS_FILING_DATE')
    CREATE INDEX IX_PATENTS_FILING_DATE ON PATENTS (filing_date);
"""


def build_upsert_query() -> str:
    """Generate T-SQL MERGE template for upserting patent records.

    This returns a parameterized MERGE statement for use with pyodbc.
    Parameters are passed via ? placeholders.

    Returns:
        T-SQL MERGE statement with parameter placeholders
    """
    return """
MERGE INTO PATENTS AS target
USING (SELECT
    ? AS patent_number,
    ? AS title,
    ? AS abstract,
    ? AS assignee,
    ? AS inventors,
    ? AS filing_date,
    ? AS grant_date,
    ? AS cpc_codes,
    ? AS search_query,
    ? AS category
) AS source
ON target.patent_number = source.patent_number
WHEN MATCHED THEN UPDATE SET
    title = source.title,
    abstract = source.abstract,
    assignee = source.assignee,
    inventors = source.inventors,
    filing_date = source.filing_date,
    grant_date = source.grant_date,
    cpc_codes = source.cpc_codes,
    search_query = source.search_query,
    category = source.category,
    updated_at = GETDATE()
WHEN NOT MATCHED THEN INSERT (
    patent_number, title, abstract, assignee, inventors,
    filing_date, grant_date, cpc_codes, search_query, category,
    created_at, updated_at
) VALUES (
    source.patent_number, source.title, source.abstract, source.assignee,
    source.inventors, source.filing_date, source.grant_date, source.cpc_codes,
    source.search_query, source.category, GETDATE(), GETDATE()
);
"""


def get_patent_count_query() -> str:
    """Query to get total patent count and date range.

    Returns:
        T-SQL query string
    """
    return """
SELECT
    COUNT(*) AS total_patents,
    MIN(filing_date) AS earliest_filing,
    MAX(filing_date) AS latest_filing,
    COUNT(DISTINCT assignee) AS unique_assignees
FROM PATENTS;
"""


def get_trends_query() -> str:
    """Query for patent filing trends by year.

    Returns:
        T-SQL query string
    """
    return """
SELECT
    YEAR(filing_date) AS filing_year,
    COUNT(*) AS patent_count
FROM PATENTS
WHERE filing_date IS NOT NULL
GROUP BY YEAR(filing_date)
ORDER BY filing_year;
"""


def get_top_inventors_query(top_n: int = 10) -> str:
    """Query for most prolific inventors using OPENJSON to parse JSON array.

    Args:
        top_n: Number of top inventors to return

    Returns:
        T-SQL query string using CROSS APPLY OPENJSON
    """
    return f"""
SELECT TOP {top_n}
    inventor.value AS inventor_name,
    COUNT(*) AS patent_count
FROM PATENTS
CROSS APPLY OPENJSON(inventors) AS inventor
GROUP BY inventor.value
ORDER BY patent_count DESC;
"""


def get_cpc_breakdown_query(top_n: int = 10) -> str:
    """Query for technology category breakdown using OPENJSON.

    Args:
        top_n: Number of top CPC codes to return

    Returns:
        T-SQL query string using CROSS APPLY OPENJSON
    """
    return f"""
SELECT TOP {top_n}
    LEFT(cpc.value, 4) AS cpc_group,
    COUNT(*) AS patent_count
FROM PATENTS
CROSS APPLY OPENJSON(cpc_codes) AS cpc
GROUP BY LEFT(cpc.value, 4)
ORDER BY patent_count DESC;
"""


def get_assignee_comparison_query() -> str:
    """Query to compare patent activity across assignees.

    Returns:
        T-SQL query string
    """
    return """
SELECT
    assignee,
    COUNT(*) AS total_patents,
    MIN(filing_date) AS earliest_filing,
    MAX(filing_date) AS latest_filing,
    COUNT(DISTINCT YEAR(filing_date)) AS active_years
FROM PATENTS
GROUP BY assignee
ORDER BY total_patents DESC;
"""
