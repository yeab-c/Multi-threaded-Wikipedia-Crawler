import argparse

from fetcher import is_valid_url
from crawl import crawl
from db import connect, words_per_page, rank_words, most_linked_pages

def main():
    parser = argparse.ArgumentParser(description="A web crawler for wikipedia urls")
    
    # python main.py --crawl https://en.wikipedia.org/wiki/Dog
    parser.add_argument("--crawl", action = "store", metavar = "WIKIPEDIA_LINK", 
                        help = "Crawls through the provided url") 
    # python main.py --index Dog
    parser.add_argument("--index", action = "store", metavar = "PAGE_TITLE", 
                        help = "Counts the words on each page of a crawled wikipedia title")
    # python main.py --search Bark Dog
    parser.add_argument("--search", action = "store", nargs = 2, metavar = ("WORD", "PAGE_TITLE"),
                        help = "finds pages that consists the given WORD with PAGE_TITLE as its starting page")
    # python main.py --top Dog
    parser.add_argument("--top", action = "store", help = "Shows the linked to pages",
                        metavar = "PAGE_TITLE" )

    args = parser.parse_args()

    
    if args.crawl:
        if is_valid_url(args.crawl):
            crawl(args.crawl)
        else:
            raise ValueError("Invalid URL")

    if args.index:
        conn = connect(args.index)
        words_per_page(conn)
        conn.close()

    if args.search:
        word, main_page = args.search
        conn = connect(main_page)
        rank_words(conn, word)
        conn.close()

    if args.top:
        conn = connect(args.top)
        most_linked_pages(conn)
        conn.close()        

if __name__ == "__main__":
    main()


