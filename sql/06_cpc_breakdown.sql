
SELECT TOP 10
    LEFT(cpc.value, 4) AS cpc_group,
    COUNT(*) AS patent_count
FROM PATENTS
CROSS APPLY OPENJSON(cpc_codes) AS cpc
GROUP BY LEFT(cpc.value, 4)
ORDER BY patent_count DESC;
