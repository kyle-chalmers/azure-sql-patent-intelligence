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
    "intel": [
        {
            "patent_number": "US20240389012A1",
            "title": "Method for Advanced Semiconductor Packaging with Through-Silicon Vias",
            "abstract": "A method for fabricating advanced semiconductor packages using through-silicon via technology for high-bandwidth interconnects.",
            "assignee": "Intel Corporation",
            "inventors": ["Ravi Mahajan", "Srinivas Pietambaram"],
            "filing_date": "2024-05-15",
            "grant_date": None,
            "cpc_codes": ["H01L23/498", "H01L25/0657"],
        },
        {
            "patent_number": "US20240356789A1",
            "title": "Energy-Efficient AI Compute Architecture with Dynamic Precision Scaling",
            "abstract": "A computing architecture that dynamically scales numerical precision based on workload requirements to optimize energy efficiency for AI inference.",
            "assignee": "Intel Corporation",
            "inventors": ["Naveen Mellempudi", "Dheevatsa Mudigere"],
            "filing_date": "2024-04-22",
            "grant_date": None,
            "cpc_codes": ["G06N3/063", "G06F7/544"],
        },
        {
            "patent_number": "US20240312456A1",
            "title": "Heterogeneous Chiplet Integration Using Embedded Multi-Die Bridge",
            "abstract": "A semiconductor device architecture using embedded multi-die interconnect bridge technology for heterogeneous chiplet integration.",
            "assignee": "Intel Corporation",
            "inventors": ["Wilfred Gomes", "Debendra Mallik"],
            "filing_date": "2024-03-18",
            "grant_date": None,
            "cpc_codes": ["H01L25/18", "H01L23/5385"],
        },
        {
            "patent_number": "US20240278901A1",
            "title": "Secure Enclave Processing for Confidential Computing in Cloud Environments",
            "abstract": "A method for providing hardware-based trusted execution environments for confidential computing workloads in multi-tenant cloud infrastructure.",
            "assignee": "Intel Corporation",
            "inventors": ["Anand Rajan", "Simon Johnson"],
            "filing_date": "2024-02-14",
            "grant_date": None,
            "cpc_codes": ["G06F21/53", "H04L9/3234"],
        },
        {
            "patent_number": "US20240245123A1",
            "title": "Photonic Integrated Circuit for Data Center Optical Interconnects",
            "abstract": "An integrated photonic circuit design for high-bandwidth, low-latency optical interconnects in data center environments.",
            "assignee": "Intel Corporation",
            "inventors": ["Robert Blum", "Haisheng Rong"],
            "filing_date": "2024-01-20",
            "grant_date": None,
            "cpc_codes": ["H04B10/25", "G02B6/12"],
        },
        {
            "patent_number": "US11934567B2",
            "title": "Neural Network Accelerator with Sparse Matrix Computation Engine",
            "abstract": "A hardware accelerator for neural network inference that exploits sparsity in weight matrices for improved throughput and energy efficiency.",
            "assignee": "Intel Corporation",
            "inventors": ["Eriko Nurvitadhi", "Ganesh Venkatesh"],
            "filing_date": "2023-08-10",
            "grant_date": "2024-03-19",
            "cpc_codes": ["G06N3/08", "G06F17/16"],
        },
        {
            "patent_number": "US11876543B2",
            "title": "Advanced EUV Lithography Process for Sub-3nm Node Fabrication",
            "abstract": "An extreme ultraviolet lithography process optimization for manufacturing semiconductor devices at sub-3 nanometer technology nodes.",
            "assignee": "Intel Corporation",
            "inventors": ["Todd Younkin", "Britt Turkot"],
            "filing_date": "2023-06-05",
            "grant_date": "2024-01-16",
            "cpc_codes": ["H01L21/027", "G03F7/70"],
        },
        {
            "patent_number": "US11789012B2",
            "title": "5G Network Slicing Optimization Using Reinforcement Learning",
            "abstract": "A system for optimizing 5G network slice allocation using reinforcement learning to maximize quality of service across diverse workloads.",
            "assignee": "Intel Corporation",
            "inventors": ["Rath Vannithamby", "Anthony Ngoc Tran"],
            "filing_date": "2023-04-12",
            "grant_date": "2023-10-17",
            "cpc_codes": ["H04L41/0893", "H04W28/024"],
        },
        {
            "patent_number": "US11723456B2",
            "title": "In-Memory Computing Architecture for Graph Analytics",
            "abstract": "A processing-in-memory architecture optimized for large-scale graph analytics workloads with near-data computation capabilities.",
            "assignee": "Intel Corporation",
            "inventors": ["Onur Mutlu", "Saugata Ghose"],
            "filing_date": "2023-02-28",
            "grant_date": "2023-08-08",
            "cpc_codes": ["G06F15/78", "G06F12/0246"],
        },
        {
            "patent_number": "US11654321B2",
            "title": "Quantum Error Correction Method for Superconducting Qubit Arrays",
            "abstract": "A quantum error correction technique for arrays of superconducting qubits enabling fault-tolerant quantum computation.",
            "assignee": "Intel Corporation",
            "inventors": ["James Clarke", "Anne Matsuura"],
            "filing_date": "2023-01-10",
            "grant_date": "2023-05-23",
            "cpc_codes": ["G06N10/70", "H10N60/12"],
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
    results = _search_uspto_odp(company, limit)
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


def search_by_title(keywords: str, limit: int = 50) -> list[dict]:
    """Search patents by title keywords.

    Args:
        keywords: Keywords to search in patent titles (e.g., "semiconductor")
        limit: Maximum number of results to return

    Returns:
        List of patent dictionaries
    """
    # Try USPTO ODP API first (primary source)
    results = _search_uspto_odp(keywords, limit)
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


def _search_uspto_odp(query: str, limit: int) -> list[dict]:
    """Search USPTO Open Data Portal API.

    Args:
        query: Search query (company name, keywords, or patent number)
        limit: Maximum results to return

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
