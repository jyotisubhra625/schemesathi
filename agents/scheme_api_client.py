"""
Live Government Scheme API Client for SchemeSaathi.
Fetches real-time welfare scheme data over HTTP API with automatic local caching fallback.
"""
import requests
import json
import os
from typing import List, Dict, Any, Optional

API_ENDPOINT = "https://api.myscheme.gov.in/api/v1/schemes/search"

def fetch_live_schemes(state: Optional[str] = None, occupation: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches schemes live over HTTP from government scheme endpoint.
    Falls back gracefully to local verified schemes registry if API is unavailable/rate-limited.
    """
    try:
        headers = {
            "User-Agent": "SchemeSaathi-Agentic-Assistant/1.0",
            "Accept": "application/json"
        }
        params = {}
        if state and state.lower() != "all":
            params["state"] = state
        if occupation:
            params["occupation"] = occupation

        # Fast HTTP GET call with 2.5s timeout
        res = requests.get(API_ENDPOINT, params=params, headers=headers, timeout=2.5)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"[SchemeAPI] Successfully fetched {len(data)} live schemes from API.")
                return data
            elif isinstance(data, dict) and "data" in data and len(data["data"]) > 0:
                print(f"[SchemeAPI] Successfully fetched {len(data['data'])} live schemes from API.")
                return data["data"]
    except Exception as e:
        print(f"[SchemeAPI] Info: Live API endpoint unreachable/timeout ({e}). Using verified scheme registry.")

    # Always return verified scheme dataset
    local_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "schemes.json")
    with open(local_path, "r", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    schemes = fetch_live_schemes(state="Odisha", occupation="farmer")
    print(f"Loaded {len(schemes)} schemes.")
