from contextlib import contextmanager
from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "parking.db"


@contextmanager
def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def rows_to_dicts(rows):
    return [dict(row) for row in rows]


def init_db():
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS spaces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                area TEXT NOT NULL,
                status TEXT NOT NULL,
                plate_number TEXT,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS monthly_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                holder_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                plate_number TEXT NOT NULL UNIQUE,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                fee REAL NOT NULL,
                status TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS parking_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate_number TEXT NOT NULL,
                space_code TEXT NOT NULL,
                entry_time TEXT NOT NULL,
                exit_time TEXT,
                duration_hours REAL,
                amount REAL,
                status TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                buyer_name TEXT NOT NULL,
                tax_number TEXT,
                email TEXT NOT NULL,
                amount REAL NOT NULL,
                issued_at TEXT NOT NULL,
                invoice_no TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL
            );
            """
        )

        existing = conn.execute("SELECT COUNT(*) AS count FROM spaces").fetchone()["count"]
        if existing == 0:
            conn.executemany(
                """
                INSERT INTO spaces (code, area, status, plate_number, updated_at)
                VALUES (?, ?, ?, ?, datetime('now', 'localtime'))
                """,
                [
                    ("A-001", "A区", "occupied", "沪A12345"),
                    ("A-002", "A区", "free", None),
                    ("A-003", "A区", "reserved", None),
                    ("B-001", "B区", "free", None),
                    ("B-002", "B区", "occupied", "浙B88K21"),
                    ("C-001", "C区", "maintenance", None),
                    ("C-002", "C区", "free", None),
                    ("C-003", "C区", "free", None),
                ],
            )
