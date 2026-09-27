import os
import time

import psycopg
from psycopg.rows import dict_row

from domain import judge

DSN = os.environ.get("DATABASE_URL", "postgresql://app:app@localhost:54395/spectrum")

# 领取后判定前的处理耗时，让「领取中」在队列里可被观察到（交班快照会冻结这一状态）
PROCESS_SECONDS = 0.8


def connect():
    return psycopg.connect(DSN, row_factory=dict_row)


def claim_one(conn):
    row = conn.execute(
        """
        SELECT id FROM jobs
        WHERE status='pending'
        ORDER BY id
        FOR UPDATE SKIP LOCKED
        LIMIT 1
        """
    ).fetchone()
    if not row:
        return None
    conn.execute("UPDATE jobs SET status='claimed' WHERE id=%s", (row["id"],))
    conn.commit()
    return row["id"]


def complete_one(conn):
    row = conn.execute(
        """
        SELECT id, nominal_nm, measured_nm FROM jobs
        WHERE status='claimed'
        ORDER BY id
        FOR UPDATE SKIP LOCKED
        LIMIT 1
        """
    ).fetchone()
    if not row:
        return None
    verdict, reason = judge(row["nominal_nm"], row["measured_nm"])
    conn.execute(
        "UPDATE jobs SET status='done', verdict=%s, reason=%s WHERE id=%s",
        (verdict, reason, row["id"]),
    )
    conn.commit()
    return row["id"]


def main():
    while True:
        try:
            with connect() as conn:
                claim_one(conn)
            time.sleep(PROCESS_SECONDS)
            with connect() as conn:
                complete_one(conn)
        except Exception as exc:
            print("worker err", exc, flush=True)
        time.sleep(0.4)


if __name__ == "__main__":
    main()
