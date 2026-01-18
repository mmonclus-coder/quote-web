import os
import psycopg2

def get_conn():
    # Provided by Render once we attach Postgres
    dsn = os.environ["DATABASE_URL"]
    return psycopg2.connect(dsn, sslmode="require")

def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS quote_counter (
              id integer primary key,
              last_quote_no integer not null
            );
            """)
            cur.execute("""
            INSERT INTO quote_counter (id, last_quote_no)
            VALUES (1, 0)
            ON CONFLICT (id) DO NOTHING;
            """)
        conn.commit()

def next_quote_no() -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            UPDATE quote_counter
            SET last_quote_no = last_quote_no + 1
            WHERE id = 1
            RETURNING last_quote_no;
            """)
            (n,) = cur.fetchone()
        conn.commit()
        return int(n)
