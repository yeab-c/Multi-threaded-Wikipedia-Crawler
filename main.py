import argparse

def main():
    parser = argparse.ArgumentParser(description="A web crawler for wikipedia urls")
    
    # python main.py --crawl https://en.wikipedia.org/wiki/Dog
    parser.add_argument("--crawl", action = "store", metavar = "WIKIPEDIA LINK", 
                        help = "Crawls through the provided url") 
    # python main.py --index Dog
    parser.add_argument("--index", action = "store", metavar = "PAGE TITLE", 
                        help = "Counts the words on each page of a crawled wikipedia title")
    # python main.py --search Bark Dog
    parser.add_argument("--search", action = "store", nargs = 2, metavar = ("WORD", "PAGE_TITLE"),
                        help = "finds pages that consists the given WORD with PAGE_TITLE as its starting page")
    # python main.py --top Dog
    parser.add_argument("--top", action = "store", help = "Shows the linked to pages",
                        metavar = "PAGE TITLE" )

    args = parser.parse_args()

    
    if args.crawl:
        print("Working", args.crawl)

if __name__ == "__main__":
    main()


