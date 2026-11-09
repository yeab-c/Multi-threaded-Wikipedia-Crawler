# Wikipedia Crawler

A multithreaded Wikipedia crawler that crawls pages starting from a given URL, stores words and links in a local SQLite database, and lets you search and rank pages by word frequency.

## Project Structure

```
crawler/
├── main.py       # CLI entry point
├── crawl.py      # Crawling logic (multithreaded)
├── fetcher.py    # HTTP fetching and HTML parsing
├── db.py         # SQLite database operations
└── config.py     # PageData dataclass
```

## Requirements

Install dependencies with:

```bash
pip install requests beautifulsoup4
```

## Usage

All commands are run through `main.py`.

### 1. Crawl a Wikipedia page

```bash
python main.py --crawl https://en.wikipedia.org/wiki/Dog
```

Crawls starting from the given URL (up to depth 2, 100 pages max) and saves everything to a local `Dog.sqlite` database.

### 2. Index word counts per page

```bash
python main.py --index Dog
```

Prints the total word count for each crawled page in the `Dog.sqlite` database.

### 3. Search for a word

```bash
python main.py --search Bark Dog
```

Finds pages containing the word `Bark` within the `Dog` crawl, ranked by score (`2 × word count + incoming links`).

### 4. Show most-linked pages

```bash
python main.py --top Dog
```

Prints the top 3 most linked-to pages in the `Dog` crawl.

## How It Works

1. **Fetching** — `fetcher.py` downloads Wikipedia pages using `requests` and parses them with `BeautifulSoup`, extracting paragraph text and internal Wikipedia links.
2. **Crawling** — `crawl.py` uses a thread pool (10 workers by default) with a work queue to crawl pages in parallel up to a configurable depth.
3. **Storage** — `db.py` saves pages and word counts to a SQLite database (`<PageTitle>.sqlite`). Pages are ranked using a simple score: `2 × word count + number of incoming links`.
