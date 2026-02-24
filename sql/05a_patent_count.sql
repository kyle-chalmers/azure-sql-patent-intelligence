-- Summary stats: total patents, date range, unique assignees

SELECT
    COUNT(*) AS total_patents,
    MIN(filing_date) AS earliest_filing,
    MAX(filing_date) AS latest_filing,
    COUNT(DISTINCT assignee) AS unique_assignees
FROM PATENTS;
