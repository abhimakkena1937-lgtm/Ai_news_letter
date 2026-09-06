import sqlite3
from datetime import datetime


DB_NAME = "subscribers.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_subscriber(email: str):

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO subscribers
            (email, status, created_at)
            VALUES (?, ?, ?)
            """,
            (
                email,
                "active",
                datetime.utcnow().isoformat()
            )
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


def get_active_subscribers():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT email
        FROM subscribers
        WHERE status = 'active'
        """
    )

    subscribers = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()

    return subscribers


def unsubscribe(email: str):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE subscribers
        SET status = 'unsubscribed'
        WHERE email = ?
        """,
        (email,)
    )

    conn.commit()
    conn.close()