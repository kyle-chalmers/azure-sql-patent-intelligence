-- QC Verification Queries for Patent Intelligence Pipeline
-- Run these in Azure Portal > SQL Query Editor to validate pipeline output

-- QC 1: Total patents, date range, assignee count
SELECT COUNT(*) AS total_patents,
       MIN(filing_date) AS earliest_filing,
       MAX(filing_date) AS latest_filing,
       COUNT(DISTINCT assignee) AS unique_assignees
FROM PATENTS;

-- QC 2: Patents by category (should show title_search, backfill, daily_sync)
SELECT category, COUNT(*) AS cnt
FROM PATENTS GROUP BY category ORDER BY cnt DESC;

-- QC 3: Patents by search topic
SELECT search_query, COUNT(*) AS cnt
FROM PATENTS GROUP BY search_query ORDER BY cnt DESC;

-- QC 4: Filing trends by month (granular view for backfill verification)
SELECT FORMAT(filing_date, 'yyyy-MM') AS filing_month, COUNT(*) AS cnt
FROM PATENTS WHERE filing_date IS NOT NULL
GROUP BY FORMAT(filing_date, 'yyyy-MM')
ORDER BY filing_month;

-- QC 5: Check for empty/null patent_numbers (should be 0)
SELECT COUNT(*) AS empty_ids FROM PATENTS
WHERE patent_number IS NULL OR patent_number = '';

-- QC 6: Check for duplicates (should be 0)
SELECT patent_number, COUNT(*) AS cnt
FROM PATENTS GROUP BY patent_number HAVING COUNT(*) > 1;

-- QC 7: SYNC_LOG history
SELECT * FROM SYNC_LOG ORDER BY sync_date DESC;

-- QC 8: Sample patents (spot-check titles and data quality)
SELECT TOP 10 patent_number, title, assignee, filing_date, search_query, category
FROM PATENTS ORDER BY filing_date DESC;
