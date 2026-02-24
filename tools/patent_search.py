"""Patent data wrapper using USPTO Open Data Portal API.

Primary source: USPTO ODP API (api.uspto.gov) - requires API key
Fallback: Google Patents API (rate-limited, no key required)
Last resort: Sample data for demos

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

# Sample data for demo when APIs are unavailable
SAMPLE_PATENTS = {
    "ai data processing": [
        {
            "patent_number": "US20240401234A1",
            "title": "Distributed AI Data Processing Pipeline with Adaptive Resource Allocation",
            "abstract": "A distributed data processing system that uses machine learning to dynamically allocate computing resources across processing nodes based on workload characteristics.",
            "assignee": "Google LLC",
            "inventors": ["Jeff Dean", "Sanjay Ghemawat"],
            "filing_date": "2024-06-12",
            "grant_date": None,
            "cpc_codes": ["G06N3/08", "G06F9/5083"],
        },
        {
            "patent_number": "US20240378901A1",
            "title": "Real-Time AI Data Transformation Engine for Streaming Analytics",
            "abstract": "An AI-powered data transformation engine that processes streaming data in real time, applying learned patterns to cleanse, enrich, and route data to downstream systems.",
            "assignee": "IBM Corporation",
            "inventors": ["Ruchir Puri", "Mukesh Khare"],
            "filing_date": "2024-05-03",
            "grant_date": None,
            "cpc_codes": ["G06F16/2458", "G06N20/00"],
        },
        {
            "patent_number": "US11987654B2",
            "title": "Automated Data Quality Assessment Using Neural Network Classification",
            "abstract": "A system for automatically assessing data quality in large-scale datasets using neural network classifiers trained on historical data quality patterns.",
            "assignee": "Amazon Technologies Inc",
            "inventors": ["Swami Sivasubramanian", "Peter Skomoroch"],
            "filing_date": "2023-11-20",
            "grant_date": "2024-05-14",
            "cpc_codes": ["G06N3/04", "G06F16/215"],
        },
        {
            "patent_number": "US11876234B2",
            "title": "Federated Learning Framework for Privacy-Preserving Data Processing",
            "abstract": "A federated learning system that enables AI model training across distributed data sources without centralizing sensitive data.",
            "assignee": "Microsoft Technology Licensing LLC",
            "inventors": ["Brendan McMahan", "Keith Bonawitz"],
            "filing_date": "2023-08-15",
            "grant_date": "2024-01-23",
            "cpc_codes": ["G06N3/098", "G06F21/6245"],
        },
    ],
    "predictive analytics": [
        {
            "patent_number": "US20240389567A1",
            "title": "Predictive Analytics Engine with Explainable AI for Business Forecasting",
            "abstract": "A predictive analytics system that generates business forecasts with built-in explainability features, allowing users to understand the reasoning behind each prediction.",
            "assignee": "Salesforce Inc",
            "inventors": ["Richard Socher", "Caiming Xiong"],
            "filing_date": "2024-04-28",
            "grant_date": None,
            "cpc_codes": ["G06Q10/04", "G06N3/08"],
        },
        {
            "patent_number": "US11923456B2",
            "title": "Time-Series Anomaly Detection Using Transformer-Based Predictive Models",
            "abstract": "A transformer-based architecture for detecting anomalies in time-series data by learning temporal patterns and predicting expected value distributions.",
            "assignee": "SAS Institute Inc",
            "inventors": ["Oliver Schabenberger", "Xin Yan"],
            "filing_date": "2023-10-05",
            "grant_date": "2024-03-12",
            "cpc_codes": ["G06N3/0455", "G06F18/2433"],
        },
        {
            "patent_number": "US11845678B2",
            "title": "Predictive Maintenance System Using Multi-Sensor Fusion and Deep Learning",
            "abstract": "A predictive maintenance platform that fuses data from multiple IoT sensors and applies deep learning models to predict equipment failures before they occur.",
            "assignee": "Microsoft Technology Licensing LLC",
            "inventors": ["Joseph Sirosh", "Wee Hyong Tok"],
            "filing_date": "2023-07-18",
            "grant_date": "2023-12-19",
            "cpc_codes": ["G06N3/08", "G05B23/0283"],
        },
    ],
    "business intelligence": [
        {
            "patent_number": "US20240367890A1",
            "title": "Natural Language Query Interface for Business Intelligence Dashboards",
            "abstract": "A natural language processing system that converts plain English questions into optimized SQL queries for business intelligence dashboards and data visualization tools.",
            "assignee": "Tableau Software LLC",
            "inventors": ["Andrew Beers", "Jock Mackinlay"],
            "filing_date": "2024-05-10",
            "grant_date": None,
            "cpc_codes": ["G06Q10/10", "G06F16/242"],
        },
        {
            "patent_number": "US11912345B2",
            "title": "Automated Insight Generation from Enterprise Data Warehouses",
            "abstract": "An AI system that automatically discovers and surfaces actionable insights from enterprise data warehouses by analyzing statistical patterns across business metrics.",
            "assignee": "SAP SE",
            "inventors": ["Juergen Mueller", "Thomas Saueressig"],
            "filing_date": "2023-09-22",
            "grant_date": "2024-02-27",
            "cpc_codes": ["G06Q10/06", "G06N20/00"],
        },
        {
            "patent_number": "US11834567B2",
            "title": "Semantic Layer for Unified Business Intelligence Across Heterogeneous Data Sources",
            "abstract": "A semantic layer technology that provides a unified business view across heterogeneous data sources, enabling consistent metrics and dimensions for BI reporting.",
            "assignee": "Oracle International Corporation",
            "inventors": ["Juan Loaiza", "Andrew Mendelsohn"],
            "filing_date": "2023-06-30",
            "grant_date": "2023-12-05",
            "cpc_codes": ["G06Q10/10", "G06F16/25"],
        },
    ],
    "assa abloy": [
        {
            "patent_number": "US20250001234A1",
            "title": "Multi-factor authentication door access control system",
            "abstract": "A door access control system that combines biometric verification with mobile credentials...",
            "assignee": "Example Corp Global Solutions AB",
            "inventors": ["Erik Lindqvist", "Anna Svensson"],
            "filing_date": "2025-09-03",
            "grant_date": None,
            "cpc_codes": ["E05B47/00", "G07C9/00"],
        },
        {
            "patent_number": "US20250005678A1",
            "title": "Beacon circuit for use with electronic locks",
            "abstract": "An electronic lock system with integrated beacon circuitry for proximity detection...",
            "assignee": "Example Corp AB",
            "inventors": ["Johan Berg"],
            "filing_date": "2025-08-07",
            "grant_date": None,
            "cpc_codes": ["E05B47/00", "H04W4/80"],
        },
    ],
}


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
        company: Company name to search for (e.g., "Intel", "Microsoft")
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
    results = _search_google_patents(query, limit)
    if results:
        return results

    # Last resort: sample data for demos
    results = _get_sample_data(company.lower(), limit)
    return results


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
    results = _search_google_patents(query, limit)
    if results:
        return results

    # Last resort: sample data for demos
    results = _get_sample_data(keywords.lower(), limit)
    return results


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


def _get_sample_data(key: str, limit: int) -> list[dict]:
    """Get sample data for demos when APIs are unavailable.

    Args:
        key: Search key (company name or keywords)
        limit: Maximum results

    Returns:
        List of sample patent dictionaries
    """
    for sample_key, patents in SAMPLE_PATENTS.items():
        if sample_key in key or key in sample_key:
            print(f"[Using sample data for '{key}' - APIs unavailable]")
            return patents[:limit]
    return []


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
