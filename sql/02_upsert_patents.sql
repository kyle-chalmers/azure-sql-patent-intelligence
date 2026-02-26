
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
