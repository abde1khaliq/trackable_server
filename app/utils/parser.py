import requests
from bs4 import BeautifulSoup

def parse_html(url: str, selector: str) -> str | None:
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, "html.parser")

    try:
        element = soup.select_one(selector)
    except Exception:
        # covers malformed selector syntax, e.g. user typo'd the CSS
        return None

    return element.get_text(strip=True) if element else None