import sqlite3

from pathlib import Path


def create_tables(name:str) -> None:
    conn = sqlite3.connect(f'{name}.sqlite', isolation_level = None)
    conn.execute("PRAGMA foreign_keys = ON;")
    # Pages Table
    conn.execute('''
    CREATE TABLE IF NOT EXISTS pages (
        page_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        parent_page_id INTEGER DEFAULT 0,
        depth INTEGER DEFAULT 0
    );
    ''')
    # Text Table
    conn.execute('''
    CREATE TABLE IF NOT EXISTS text (
        text_id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT NOT NULL,
        FOREIGN KEY (page_id) REFERENCES pages (page_id),
        count INTEGER NOT NULL
    );
    ''')

    conn.close()


