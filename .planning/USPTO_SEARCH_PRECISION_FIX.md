# Fix: USPTO API Search Narrowed to Field-Specific Queries

**Status: COMPLETED** (2026-02-18)

## Context

The `search_by_assignee()` function returned irrelevant results (X-ray fluoroscopy, light-emitting devices) when searching for "Google LLC". Root cause: `_search_uspto_odp()` passed the company name as a generic keyword query (`q=Google LLC`), which the USPTO API treats as `Google OR LLC` across ALL fields — returning millions of results.

## Problem

**Before** (`search_by_assignee` line ~203):
```python
results = _search_uspto_odp(company, limit)  # "Google LLC" → matches ANY field
```

Result: `q=Google+LLC` → millions of results (keyword OR match across all fields)

## Fix Applied

### `search_by_assignee()` — uses nested `applicantNameText` field
```python
assignee_query = f'applicationMetaData.applicantBag.applicantNameText:"{company}"'
results = _search_uspto_odp(assignee_query, limit)
```

Result: `q=applicationMetaData.applicantBag.applicantNameText%3A%22Google+LLC%22` → targeted results (all Google LLC patents)

**Note:** The USPTO ODP API requires fully-qualified nested field paths (e.g., `applicationMetaData.applicantBag.applicantNameText`), not short-form names (e.g., `applicantNameText`). Short-form returns 404. This was discovered during implementation — the original plan assumed Lucene short-form syntax would work.

### `search_by_title()` — uses nested `inventionTitle` field
```python
title_query = f'applicationMetaData.inventionTitle:({keywords})'
results = _search_uspto_odp(title_query, limit)
```

### `_search_uspto_odp()` — unchanged
It just passes whatever query string it receives as the `q` parameter.

## Files Modified

- `azure-sql-patent-intelligence/tools/patent_search.py`
- `agent-building-example/tools/patent_search.py`
- `azure-sql-patent-intelligence/.env` — added `USPTO_API_KEY` (already gitignored)
- `azure-sql-patent-intelligence/.planning/PLAN.md` — renamed to `REPO_SETUP_PROGRESS.md`

## Verification Results

All tests passed against the live USPTO ODP API:

| Test | Result |
|------|--------|
| `search_by_assignee('Google LLC', limit=5)` | Targeted results, all 5 returned show `Google LLC` as assignee |
| `search_by_assignee('Microsoft', limit=3)` | 54,797 total, returns `Microsoft Technology Licensing, LLC` patents |
| `search_by_assignee('IBM', limit=3)` | Returns `International Business Machines Corporation` patents |
| `search_by_title('AI data processing', limit=3)` | Returns patents with AI data processing in title |
