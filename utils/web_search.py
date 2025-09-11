# utils/web_search.py
from config.config import SERPAPI_KEY, GOOGLE_CSE_KEY, GOOGLE_CX
import requests

def serpapi_search(query: str, num_results: int = 3):
    if not SERPAPI_KEY:
        return {"error": "SERPAPI_KEY not set."}
    try:
        params = {"engine": "google", "q": query, "api_key": SERPAPI_KEY, "num": num_results}
        resp = requests.get("https://serpapi.com/search", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for r in data.get("organic_results", [])[:num_results]:
            snippet = r.get("snippet") or r.get("title")
            link = r.get("link")
            results.append({"title": r.get("title"), "snippet": snippet, "link": link})
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}

def google_cse_search(query: str, num_results: int = 3):
    if not (GOOGLE_CSE_KEY and GOOGLE_CX):
        return {"error": "GOOGLE_CSE_KEY or GOOGLE_CX not set."}
    try:
        params = {"key": GOOGLE_CSE_KEY, "cx": GOOGLE_CX, "q": query, "num": num_results}
        resp = requests.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for r in data.get("items", [])[:num_results]:
            snippet = r.get("snippet")
            link = r.get("link")
            title = r.get("title")
            results.append({"title": title, "snippet": snippet, "link": link})
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}

def web_search(query: str, num_results: int = 3):
    if SERPAPI_KEY:
        return serpapi_search(query, num_results=num_results)
    if GOOGLE_CSE_KEY and GOOGLE_CX:
        return google_cse_search(query, num_results=num_results)
    return {"error": "No web search API key configured. Set SERPAPI_KEY or GOOGLE_CSE_KEY+GOOGLE_CX in env."}
