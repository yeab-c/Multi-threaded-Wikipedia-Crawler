import requests
import bs4
import re

from urllib.parse import urljoin, urldefrag
from config import PageData



# Helper Functions

def is_valid_url(url):
    pattern = r"^https?://(?:[a-z]{2,3}|meta)\.(?:m\.)?wikipedia\.org/wiki/[^\s]+$"
    return bool(re.match(pattern, url, re.IGNORECASE))


def title(url):
    match = re.search(r"/([^/#?\s]+)(?:[#?]\S*)?$", url)
    if not match:
        return None
    return re.sub("_", " ", match.group(1))


# ------------------------------------------------------------------

HEADERS = {
        "User-Agent": "MyCrawlerBot/1.0 (contact: your-email@gmail.com) EducationalProject/Crawler"
        }


#Fetch function
def fetch(session: requests.Session, url: str, retries: int = 3) -> str:
    if not is_valid_url(url):
        raise ValueError(f"Invalid Wikipedia URL: '{url}'")

    for attempt in range(1, retries + 1):
        try:
            response = session.get(url, timeout=30)
        except (requests.ConnectTimeout, requests.ReadTimeout):
            if attempt == retries:
                raise
            time.sleep(2 * attempt)
            continue

        if response.status_code == 429:
            time.sleep(int(response.headers.get("Retry-After", 5)))
            continue

        response.raise_for_status()
        return response.text

    raise RuntimeError(f"Gave up on {url} after {retries} attempts")
def parse(html: str, url: str) -> PageData | None:
    soup = bs4.BeautifulSoup(html, "html.parser")

    first_p = None
    for p in soup.select("#mw-content-text p"):
        for sup in p.select("sup"):
            sup.decompose()
        if p.get_text(strip=True):
            first_p = p
            break

    if first_p is None:
        return None

    text = first_p.get_text(" ", strip=True)

    links = []
    for a in first_p.select("a[href]"):
        full_url, _ = urldefrag(urljoin(url, a["href"]))

        if not is_valid_url(full_url):
            continue
        if ":" in full_url.split("/wiki/", 1)[1]:
            continue
        if full_url == url:
            continue
        if full_url not in links:
            links.append(full_url)

   
    page = PageData(
            url = url,
            title = title(url),
            text = text,
            links = links
            )
    
    return page


#Test to check if it is working
def main():
    url = "https://en.wikipedia.org/wiki/Dog"
    
    with requests.Session() as session:
        session.headers.update(HEADERS)
        html = fetch(session, url)

    page = parse(html, url)
    if page is None:
        print("No Paragraph Found")
        return
   
   
    print(page.url)
    print(page.title)
    print(page.text)
    print(page.links)



if __name__ == "__main__":
    main()
