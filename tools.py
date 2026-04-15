from __future__ import annotations

import re
from urllib.parse import urlparse

from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from rich import print

load_dotenv()

# Groq (and other providers) reject tool calls with malformed URLs; keep extraction strict.
_URL_PATTERN = re.compile(r"https?://[^\s\)\]>'\"]+", re.IGNORECASE)


def extract_http_urls(text: str, *, max_urls: int = 12) -> list[str]:
    """Return unique http(s) URLs from text in order of first appearance."""
    if not text:
        return []
    seen: set[str] = set()
    out: list[str] = []
    for raw in _URL_PATTERN.findall(text):
        u = raw.rstrip(".,;:!?)]}'\"")
        parsed = urlparse(u)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            continue
        if u not in seen:
            seen.add(u)
            out.append(u)
        if len(out) >= max_urls:
            break
    return out

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query : str) -> str:
    """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets."""
    results = tavily.search(query=query,max_results=5)

    out = []

    for r in results['results']:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        )
    
    return "\n----\n".join(out)

@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"