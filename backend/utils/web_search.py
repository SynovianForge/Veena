'''# utils/web_search.py
from ddgs import DDGS
import requests
from html import unescape

def simple_search(query, max_results=5):
    """Lightweight search with DuckDuckGo's new ddgs API."""
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results, region="wt-wt", safesearch="off", timelimit="d"):
                results.append({
                    "title": unescape(r.get("title", "")),
                    "snippet": unescape(r.get("body", "")),
                    "link": r.get("href", "")
                })
    except Exception as e:
        return [{"title": "Search error", "snippet": str(e), "link": ""}]

    # Fallback: Bing News RSS (very crude)
    if not results:
        try:
            resp = requests.get("https://www.bing.com/news/search?q=" + query.replace(" ", "+"), timeout=5)
            if resp.ok:
                text = resp.text
                start = text.find("<title>")
                snippet = text[start:start+400] if start != -1 else text[:400]
                results = [{"title": "Bing News Fallback", "snippet": snippet, "link": "https://bing.com/news"}]
        except Exception:
            results = [{"title": "No results", "snippet": "Could not reach fallback source", "link": ""}]

    return results'''
