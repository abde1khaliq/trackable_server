import requests
from bs4 import BeautifulSoup

def parse_html(url: str, class_name: str) -> str | None:
    """
    Fetches the page and returns the text content of the first element
    matching the given tag and class.
    Example: parse_html(url, "price_color")
    """
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    element = soup.find(class_=class_name)
    return element.get_text(strip=True) if element else None