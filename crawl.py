import queue
import threading
import re
from collections import Counter

import requests

from fetcher import HEADERS, fetch, parse, title
from db import add_page, add_words, connect, create_tables, get_page_id


work_q = queue.Queue()
result_q = queue.Queue()


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+(?:[-'][a-z0-9]+)*", text.lower())


def drain(work_q: queue.Queue) -> int:
    removed = 0
    while True:
        try:
            work_q.get_nowait()
            removed += 1
        except queue.Empty:
            return removed

def worker(session):
    while True:
        item = work_q.get()
        if item is None:
            return
        url, depth = item

        try:
            page = parse(fetch(session, url), url)
        except Exception as e:
            print(f"Failed {url}: {e}")
            page = None

        result_q.put((url, depth, page))

def crawl(start_url: str, max_depth: int = 2, max_crawled: int = 100,
          max_urls: int = 50, workers: int = 10) -> None:
    visited = {start_url}
    pending = 1
    crawled = 0
    stopping = False

    conn = connect(title(start_url))
    create_tables(conn)
    add_page(conn, title(start_url), start_url, 0, incoming=0)
    work_q.put((start_url, 0))

    with requests.Session() as session:
        session.headers.update(HEADERS)
        threads = [threading.Thread(target=worker, args=(session,), daemon=True)
                   for _ in range(workers)]
        for t in threads:
            t.start()

        while pending > 0:
            url, depth, page = result_q.get()
            pending -= 1
            if page is None:
                continue

            crawled += 1
            print(f"[{crawled}] depth {depth}: {page.title}")
            add_words(conn, url, Counter(words(page.text)))

            for link in page.links:
                add_page(conn, title(link), link, depth + 1)   # counts the link
                if stopping or depth >= max_depth or link in visited or len(visited) >= max_urls:
                    continue
                visited.add(link)
                pending += 1
                work_q.put((link, depth + 1))

            if not stopping and crawled >= max_crawled:
                stopping = True
                pending -= drain(work_q)

        for _ in threads:
            work_q.put(None)
        for t in threads:
            t.join()
     
    conn.close()


if __name__ == "__main__":
    crawl("https://en.wikipedia.org/wiki/Dog", max_depth=1)







        
