
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
