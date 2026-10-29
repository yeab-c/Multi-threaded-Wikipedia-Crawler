import asyncio
import httpx
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

#Fetch function
async def fetch(url: str) -> str:

    headers = {
        "User-Agent": "MyCrawlerBot/1.0 (contact: your-email@gmail.com) EducationalProject/Crawler"
    }
    
    valid = is_valid_url(url)
    if not valid:
        raise ValueError(f"Invalid Wikipedia URL: '{url}'")

    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.get(url)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 5))
            print(f"Rate limited. Waiting {retry_after} seconds...")
            await asyncio.sleep(retry_after)
            return await fetch(url)

        return response.text

async def parse(url: str) -> PageData:
    html = await fetch(url)
    soup = bs4.BeautifulSoup(html, "html.parser")

    first_p = None
    for p in soup.select("#mw-content-text p"):
        for sup in p.select("sup"):
            sup.decompose()
        if p.get_text(strip=True):
            first_p = p
            break

    if first_p is None:
        print("No paragraph found")
        return

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
async def main():
    url = "https://en.wikipedia.org/wiki/Dog"
    page = await parse(url)
   
   
    print(page.url)
    print(page.title)
    print(page.text)
    print(page.links)




asyncio.run(main())
