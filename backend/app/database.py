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

        existing_spaces = conn.execute("SELECT COUNT(*) AS count FROM spaces").fetchone()["count"]
        if existing_spaces == 0:
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

        existing_orders = conn.execute("SELECT COUNT(*) AS count FROM parking_orders").fetchone()["count"]
        if existing_orders == 0:
            conn.executemany(
                """
                INSERT INTO parking_orders (plate_number, space_code, entry_time, exit_time, duration_hours, amount, status)
                VALUES (?, ?, ?, ?, ?, ?, 'paid')
                """,
                [
                    ("京A00001", "A-002", "2026-06-12T08:30", "2026-06-12T10:15", 1.75, 8.0),
                    ("京A00002", "A-003", "2026-06-12T09:00", "2026-06-12T09:10", 0.17, 0.0),
                    ("京A00003", "B-001", "2026-06-12T10:00", "2026-06-12T12:30", 2.5, 16.0),
                    ("京A00004", "C-002", "2026-06-12T14:00", "2026-06-12T18:45", 4.75, 32.0),
                    ("京A00005", "C-003", "2026-06-12T17:00", "2026-06-12T17:12", 0.2, 0.0),
                    ("京A00006", "A-002", "2026-06-12T18:00", "2026-06-12T20:30", 2.5, 16.0),
                    ("京A00007", "A-003", "2026-06-12T19:00", "2026-06-12T21:15", 2.25, 16.0),
                    ("京A00008", "B-001", "2026-06-12T20:00", "2026-06-12T22:00", 2.0, 16.0),
                    ("京A00009", "A-002", "2026-06-13T07:45", "2026-06-13T09:30", 1.75, 8.0),
                    ("京A00010", "B-001", "2026-06-13T08:30", "2026-06-13T08:42", 0.2, 0.0),
                    ("京A00011", "C-002", "2026-06-13T09:00", "2026-06-13T11:30", 2.5, 16.0),
                    ("京A00012", "A-003", "2026-06-13T10:00", "2026-06-13T14:15", 4.25, 24.0),
                    ("京A00013", "C-003", "2026-06-13T13:00", "2026-06-13T15:45", 2.75, 16.0),
                    ("京A00014", "B-001", "2026-06-13T16:00", "2026-06-13T16:10", 0.17, 0.0),
                    ("京A00015", "A-002", "2026-06-13T17:30", "2026-06-13T20:00", 2.5, 16.0),
                    ("京A00016", "C-002", "2026-06-13T18:00", "2026-06-13T21:30", 3.5, 24.0),
                    ("京A00017", "A-003", "2026-06-13T19:00", "2026-06-13T22:15", 3.25, 24.0),
                    ("京A00018", "B-001", "2026-06-13T20:00", "2026-06-13T23:30", 3.5, 24.0),
                    ("京A00019", "C-003", "2026-06-13T21:00", "2026-06-13T23:00", 2.0, 16.0),
                    ("京A00020", "A-002", "2026-06-14T08:00", "2026-06-14T09:45", 1.75, 8.0),
                    ("京A00021", "A-003", "2026-06-14T09:30", "2026-06-14T12:00", 2.5, 16.0),
                    ("京A00022", "B-001", "2026-06-14T10:00", "2026-06-14T10:12", 0.2, 0.0),
                    ("京A00023", "C-002", "2026-06-14T11:00", "2026-06-14T13:30", 2.5, 16.0),
                    ("京A00024", "C-003", "2026-06-14T14:00", "2026-06-14T16:15", 2.25, 16.0),
                    ("京A00025", "A-002", "2026-06-14T15:30", "2026-06-14T15:40", 0.17, 0.0),
                    ("京A00026", "B-001", "2026-06-14T17:00", "2026-06-14T19:45", 2.75, 16.0),
                ],
            )
