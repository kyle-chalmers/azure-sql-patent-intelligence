
SELECT TOP 10
    inventor.value AS inventor_name,
    COUNT(*) AS patent_count
FROM PATENTS
CROSS APPLY OPENJSON(inventors) AS inventor
GROUP BY inventor.value
ORDER BY patent_count DESC;
