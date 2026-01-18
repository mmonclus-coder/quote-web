import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor

def get_conn():
    dsn = os.environ["DATABASE_URL"]
    # Render Postgres commonly requires SSL. :contentReference[oaicite:2]{index=2}
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

            cur.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
              quote_no text primary key,
              created_at timestamptz not null default now(),
              rep text,
              work_order text,
              due_date text,
              submitted_on text,
              unit_price numeric,
              items_json jsonb not null,
              total numeric
            );
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

def save_quote(*, quote_no: str, rep: str, work_order: str, due_date: str, submitted_on: str,
              unit_price: float, items: list[dict], total: float) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO quotes (quote_no, rep, work_order, due_date, submitted_on, unit_price, items_json, total)
            VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb,%s)
            ON CONFLICT (quote_no) DO UPDATE SET
              rep = EXCLUDED.rep,
              work_order = EXCLUDED.work_order,
              due_date = EXCLUDED.due_date,
              submitted_on = EXCLUDED.submitted_on,
              unit_price = EXCLUDED.unit_price,
              items_json = EXCLUDED.items_json,
              total = EXCLUDED.total;
            """, (quote_no, rep, work_order, due_date, submitted_on, unit_price, json.dumps(items), total))
        conn.commit()

def load_quote(quote_no: str):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM quotes WHERE quote_no=%s", (quote_no,))
            return cur.fetchone()
