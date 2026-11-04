import sqlite3

## Helper Function
def connect(name: str) -> sqlite3.Connection:
    conn = sqlite3.connect(f"{name}.sqlite")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def get_page_id(conn: sqlite3.Connection, url: str) -> int | None:
    with conn:
        row = conn.execute(
            "SELECT page_id FROM pages WHERE url = ?", (url,)
        ).fetchone()
    return row[0] if row else None

def find_word(conn: sqlite3.Connection, word: str, limit: int = 10) -> list[tuple]:
    with conn:
        return conn.execute(
            """
            SELECT p.title, p.url, w.count, p.incoming_links,
                   2 * w.count + p.incoming_links AS score
            FROM words w
            JOIN pages p ON p.page_id = w.page_id
            WHERE w.word = ?
            ORDER BY score DESC
            LIMIT ?
            """,
            (word.lower().strip(), limit),
        ).fetchall()  
# =========================================================================

def create_tables(conn: sqlite3.Connection) -> None:
    with conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS pages (
            page_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title   TEXT NOT NULL,
            url     TEXT NOT NULL UNIQUE,
            depth   INTEGER NOT NULL DEFAULT 0,
            incoming_links INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS words (
            page_id INTEGER NOT NULL REFERENCES pages (page_id),
            word    TEXT    NOT NULL,
            count   INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (page_id, word)
        );

        CREATE INDEX IF NOT EXISTS idx_words_word ON words (word);
        """)


def add_page(
    conn: sqlite3.Connection,
    title: str,
    url: str,
    depth: int,
    incoming: int = 1,
) -> None:
    with conn:
        conn.execute(
            """
            INSERT INTO pages (title, url, depth, incoming_links)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE
                SET incoming_links = incoming_links + 1
            """,
            (title, url, depth, incoming),
        )

def add_words(conn: sqlite3.Connection, url: str, counts: dict[str, int]) -> None:
    page_id = get_page_id(conn, url)
    if not page_id:
        raise ValueError(f"Page not saved yet: {url}")

    rows = [(page_id, word, n) for word, n in counts.items()]
    with conn:
        conn.executemany(
            """
            INSERT INTO words (page_id, word, count)
            VALUES (?, ?, ?)
            ON CONFLICT(page_id, word) DO UPDATE
                SET count = excluded.count
            """,
            rows,
        )

def rank_words(conn: sqlite3.Connection, word: str) -> None:
    results = find_word(conn, word)
    if not results:
        print(f'Can\'t find "{word}"')
        return

    print(f'Pages ranked for "{word}" (2 x word count + pages linking to it)')
    print("=" * 20)
    for idx, (title, url, count, links, score) in enumerate(results, 1):
        print(f"{idx}. {title}, score {score}")
        print(f"   {url}")
