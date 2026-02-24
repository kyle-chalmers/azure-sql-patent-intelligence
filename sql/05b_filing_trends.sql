-- Filing trends: patents per year

SELECT
    YEAR(filing_date) AS filing_year,
    COUNT(*) AS patent_count
FROM PATENTS
WHERE filing_date IS NOT NULL
GROUP BY YEAR(filing_date)
ORDER BY filing_year;
