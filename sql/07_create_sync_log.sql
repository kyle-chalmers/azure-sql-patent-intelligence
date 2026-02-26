
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'SYNC_LOG')
CREATE TABLE SYNC_LOG (
    sync_id INT IDENTITY(1,1) PRIMARY KEY,
    sync_date DATETIME2 DEFAULT GETDATE(),
    filing_date_from DATE,
    filing_date_to DATE,
    patents_loaded INT,
    search_topics NVARCHAR(500),
    sync_status NVARCHAR(50) DEFAULT 'completed'
);
