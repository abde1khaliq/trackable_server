import requests
from bs4 import BeautifulSoup

def parse_html(url: str, class_name: str) -> str | None:
    """
    Fetches the page and returns the text content of the first element
    matching the given class or classes.
    Supports both single and multiple classes.
    Example: parse_html(url, "price_color")
             parse_html(url, "style-scope yt-formatted-string")
    """
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")

    classes = class_name.split()
    element = soup.find(class_=classes)

    return element.get_text(strip=True) if element else None
