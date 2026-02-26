"""Patent data wrapper using USPTO Open Data Portal API.

Primary source: USPTO ODP API (api.uspto.gov) - requires API key
Fallback: Google Patents API (rate-limited, no key required)

API key should be set in environment variable USPTO_API_KEY or .env file.

IMPORTANT - USPTO API Search Query Behavior:
============================================
The USPTO API uses OR matching by default for multi-word queries:
  - "smart lock" matches "smart" OR "lock" -> 69,449 results (mostly irrelevant)
  - '"smart lock"' (quoted) matches exact phrase -> 201 results (all relevant)

For precise searches, use these techniques:
  1. QUOTED PHRASES: Wrap multi-word terms in double quotes
     - search_by_title('"smart lock"')  -> exact phrase match
     - search_by_title('"electronic deadbolt"')

  2. BOOLEAN OPERATORS: Use AND, OR, NOT
     - search_by_title('smart AND lock AND door')  -> all terms required
     - search_by_title('lock NOT automotive')  -> exclude terms

  3. CPC CODE SEARCHES: For highest precision, use search_by_cpc()
     - search_by_cpc("E05B47")  -> electronic locks specifically
     - CPC codes eliminate keyword ambiguity entirely
"""
import json
import os
import urllib.parse
import urllib.request
from typing import Optional


# USPTO Open Data Portal API
USPTO_ODP_API = "https://api.uspto.gov/api/v1/patent/applications/search"

# Google Patents API (fallback)
GOOGLE_PATENTS_API = "https://patents.google.com/xhr/query"


def _get_api_key() -> Optional[str]:
    """Get USPTO API key from environment or .env file.

    Returns:
        API key string or None if not found
    """
    # Check environment variable first
    api_key = os.environ.get("USPTO_API_KEY")
    if api_key:
        return api_key

    # Try loading from .env file
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("USPTO_API_KEY="):
                    return line.strip().split("=", 1)[1]

    return None


def search_by_assignee(company: str, limit: int = 50) -> list[dict]:
    """Search patents by assignee/company name.

    Args:
        company: Company name to search for (e.g., "Google", "Microsoft")
        limit: Maximum number of results to return

    Returns:
        List of patent dictionaries
    """
    # Try USPTO ODP API first (primary source)
    # Use field-specific query to search applicant name directly
    assignee_query = f'applicationMetaData.applicantBag.applicantNameText:"{company}"'
    results = _search_uspto_odp(assignee_query, limit)
    if results:
        return results

    # Fallback to Google Patents
    print(f"[USPTO API unavailable, trying Google Patents for '{company}']")
    query = f"assignee={company}"
    return _search_google_patents(query, limit)


def search_by_title(
    keywords: str,
    limit: int = 50,
    filing_date_from: Optional[str] = None,
    filing_date_to: Optional[str] = None,
    start: int = 0,
) -> list[dict]:
    """Search patents by title keywords with optional date-range filtering.

    Args:
        keywords: Keywords to search in patent titles (e.g., "AI data processing")
        limit: Maximum number of results to return
        filing_date_from: Start date for filing date filter (YYYY-MM-DD)
        filing_date_to: End date for filing date filter (YYYY-MM-DD)
        start: Offset for pagination (skip first N results)

    Returns:
        List of patent dictionaries
    """
    # Try USPTO ODP API first (primary source)
    # Use field-specific query to search invention title directly
    title_query = f'applicationMetaData.inventionTitle:({keywords})'
    if filing_date_from or filing_date_to:
        date_from = filing_date_from or "*"
        date_to = filing_date_to or "*"
        title_query += f' AND applicationMetaData.filingDate:[{date_from} TO {date_to}]'
    results = _search_uspto_odp(title_query, limit, start=start)
    if results:
        return results

    # Fallback to Google Patents
    print(f"[USPTO API unavailable, trying Google Patents for '{keywords}']")
    query = f"({keywords})"
    return _search_google_patents(query, limit)


def get_patent(patent_number: str) -> Optional[dict]:
    """Get single patent by publication number.

    Args:
        patent_number: Publication number (e.g., "US11934567B2")

    Returns:
        Patent dictionary or None if not found
    """
    # Try USPTO first
    results = _search_uspto_odp(patent_number, 1)
    if results:
        return results[0]

    # Fallback to Google Patents
    results = _search_google_patents(patent_number, 1)
    return results[0] if results else None


def _search_uspto_odp(query: str, limit: int, start: int = 0) -> list[dict]:
    """Search USPTO Open Data Portal API.

    Args:
        query: Search query (company name, keywords, or patent number)
        limit: Maximum results to return
        start: Offset for pagination (skip first N results)

    Returns:
        List of patent dictionaries, empty list on failure
    """
    api_key = _get_api_key()
    if not api_key:
        print("[No USPTO_API_KEY found - set in environment or .env file]")
        return []

    params = {
        "q": query,
        "rows": min(limit, 100),
        "start": start,
    }

    url = f"{USPTO_ODP_API}?{urllib.parse.urlencode(params)}"

    headers = {
        "X-API-KEY": api_key,
        "Accept": "application/json",
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())

        results = []
        for app in data.get("patentFileWrapperDataBag", []):
            patent = _format_uspto_patent(app)
            if patent:
                results.append(patent)
                if len(results) >= limit:
                    break

        if results:
            print(f"[USPTO ODP: Found {data.get('count', 0)} total, returning {len(results)}]")

        return results

    except urllib.error.HTTPError as e:
        if e.code == 401 or e.code == 403:
            print(f"[USPTO API authentication failed (HTTP {e.code}) - check API key]")
        else:
            print(f"[USPTO API error: HTTP {e.code}]")
        return []
    except Exception as e:
        print(f"[USPTO API error: {e}]")
        return []


def _format_uspto_patent(app: dict) -> Optional[dict]:
    """Convert USPTO ODP result to standardized dict for storage.

    Args:
        app: Application data from USPTO ODP API

    Returns:
        Standardized patent dictionary or None if invalid
    """
    meta = app.get("applicationMetaData", {})
    if not meta:
        return None

    # Extract applicant/assignee
    applicants = meta.get("applicantBag", [])
    assignee = ""
    if applicants:
        assignee = applicants[0].get("applicantNameText", "")

    # Extract inventors
    inventors = []
    for inv in meta.get("inventorBag", []):
        name = inv.get("inventorNameText", "")
        if name:
            inventors.append(name)

    # Format dates (remove time component)
    filing_date = meta.get("filingDate", "")
    if filing_date and "T" in filing_date:
        filing_date = filing_date.split("T")[0]

    # Extract CPC codes if available
    cpc_codes = []
    for cpc in meta.get("cpcClassificationBag", []):
        if isinstance(cpc, dict) and cpc.get("cpcClassificationText"):
            cpc_codes.append(cpc["cpcClassificationText"])
        elif isinstance(cpc, str):
            cpc_codes.append(cpc)

    return {
        "patent_number": meta.get("earliestPublicationNumber", ""),
        "title": meta.get("inventionTitle", ""),
        "abstract": "",  # ODP search doesn't include abstract
        "assignee": assignee,
        "inventors": inventors,
        "filing_date": filing_date,
        "grant_date": None,  # Would need separate lookup
        "cpc_codes": cpc_codes,
        "status_code": meta.get("applicationStatusCode"),
    }



def _search_google_patents(query: str, limit: int) -> list[dict]:
    """Search Google Patents API (fallback).

    Args:
        query: Search query string
        limit: Maximum results to return

    Returns:
        List of patent dictionaries
    """
    params = {
        "url": query,
        "num": min(limit, 100),
        "exp": "",
        "output": "json"
    }

    url = f"{GOOGLE_PATENTS_API}?{urllib.parse.urlencode(params)}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://patents.google.com/",
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())

        results = []
        clusters = data.get("results", {}).get("cluster", [])
        for cluster in clusters:
            for item in cluster.get("result", []):
                patent = item.get("patent", {})
                results.append(_format_google_patent(patent))
                if len(results) >= limit:
                    return results

        return results

    except urllib.error.HTTPError as e:
        if e.code == 503 or e.code == 429:
            print(f"[Google Patents rate limited (HTTP {e.code})]")
        else:
            print(f"[Google Patents error: HTTP {e.code}]")
        return []
    except Exception as e:
        print(f"[Google Patents error: {e}]")
        return []


def _format_google_patent(patent: dict) -> dict:
    """Convert Google Patents result to standardized dict.

    Args:
        patent: Patent dictionary from Google Patents API

    Returns:
        Standardized patent dictionary
    """
    assignee = patent.get("assignee", "")
    if assignee:
        assignee = assignee.replace("<b>", "").replace("</b>", "")

    return {
        "patent_number": patent.get("publication_number", ""),
        "title": patent.get("title", "").strip(),
        "abstract": patent.get("snippet", "").replace("&hellip;", "..."),
        "assignee": assignee,
        "inventors": [patent.get("inventor", "")] if patent.get("inventor") else [],
        "filing_date": patent.get("filing_date"),
        "grant_date": patent.get("grant_date"),
        "cpc_codes": [],
    }
