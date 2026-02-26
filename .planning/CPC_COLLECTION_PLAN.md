# CPC Code Patent Collection Plan

## Context

The database has patents collected via keyword title searches, which are imprecise. CPC (Cooperative Patent Classification) codes are assigned by patent examiners and provide precise technology classification. This plan adds CPC-based collection for exhaustive coverage.

## CPC Codes

| Code | Description |
|------|-------------|
| G06N | AI/ML computing — neural networks, machine learning |
| G06Q | Business data processing / BI systems |
| G06V | Image/video recognition |
| G10L | Speech analysis and recognition |
| G16H | Healthcare informatics / AI in medicine |

G06F sub-codes were tested but the USPTO API cannot reliably query them (space-separated format in Lucene). G06F patents are still captured via cross-classification with these 5 codes.

## API Query Format

The USPTO ODP API field path for CPC is: `applicationMetaData.cpcClassificationBag:{code}*`

CPC entries in the API are stored as strings like `'G06N  20/20'` with variable spacing.

## Strategy

- 14 monthly windows (Jan 2025 - Feb 2026) x 5 CPC codes
- Paginate up to 20 pages (500 patents) per window
- API returns max 25 per page
- Dedup by patent_number across all CPC codes
- MERGE upsert with `category='cpc_collection'`, `search_query='CPC:{code}'`
- 0.5s sleep between API calls

## Script

`scripts/cpc_backfill.py` — standalone execution script.

## QC

`sql/09_cpc_collection_qc.sql` — verification queries for Azure Portal.
