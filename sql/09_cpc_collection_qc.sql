-- QC Queries for CPC Code Patent Collection
-- Run these in Azure Portal > SQL Query Editor to verify CPC backfill

-- QC 1: Count by CPC search code
SELECT search_query, COUNT(*) AS cnt
FROM PATENTS
WHERE category = 'cpc_collection'
GROUP BY search_query
ORDER BY cnt DESC;

-- QC 2: Total by category (keyword vs CPC)
SELECT category, COUNT(*) AS cnt
FROM PATENTS
GROUP BY category
ORDER BY cnt DESC;

-- QC 3: CPC code distribution within collected patents
SELECT TOP 15
    LEFT(cpc.value, 4) AS cpc_group,
    COUNT(*) AS patent_count
FROM PATENTS
CROSS APPLY OPENJSON(cpc_codes) AS cpc
WHERE category = 'cpc_collection'
GROUP BY LEFT(cpc.value, 4)
ORDER BY patent_count DESC;

-- QC 4: Monthly filing trends for CPC-collected patents
SELECT FORMAT(filing_date, 'yyyy-MM') AS filing_month, COUNT(*) AS cnt
FROM PATENTS
WHERE category = 'cpc_collection' AND filing_date IS NOT NULL
GROUP BY FORMAT(filing_date, 'yyyy-MM')
ORDER BY filing_month;

-- QC 5: Sample CPC-collected patents
SELECT TOP 10 patent_number, title, assignee, filing_date, search_query
FROM PATENTS
WHERE category = 'cpc_collection'
ORDER BY filing_date DESC;
