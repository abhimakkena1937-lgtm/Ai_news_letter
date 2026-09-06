import os
from datetime import datetime, timezone

import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing")


def get_connection():
    return psycopg.connect(DATABASE_URL)


def init_db():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subscribers (
                    id SERIAL PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TEXT NOT NULL
                )
            """)

        conn.commit()


def add_subscriber(email: str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute("""
                    INSERT INTO subscribers
                    (email, status, created_at)
                    VALUES (%s, %s, %s)
                """, (
                    email,
                    "active",
                    datetime.now(timezone.utc).isoformat()
                ))

                conn.commit()
                return True

            except psycopg.errors.UniqueViolation:
                conn.rollback()
                return False


def get_active_subscribers():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT email
                FROM subscribers
                WHERE status = 'active'
            """)

            return [row[0] for row in cursor.fetchall()]


def unsubscribe(email: str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE subscribers
                SET status = 'unsubscribed'
                WHERE email = %s
            """, (email,))

        conn.commit()


init_db()