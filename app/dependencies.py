from psycopg.rows import dict_row
from app.db import pool


def get_db():
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            yield cur
