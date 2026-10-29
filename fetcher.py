import asyncio
import httpx
import bs4
import re


# Helper Functions

def is_valid_url(url):
    pattern = r"^https?://(?:[a-z]{2,3}|meta)\.(?:m\.)?wikipedia\.org/wiki/[^\s]+$"
    return bool(re.match(pattern, url, re.IGNORECASE))

# ------------------------------------------------------------------

#Fetch function
async def fetch(url):

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
async def main():
    url = "https://en.wikipedia.org/wiki/Dog"
    html = await fetch(url)
    print(len(html))
    print(html)




asyncio.run(main())
