from __future__ import annotations

import json
import sqlite3

DB_PATH = "orion.db"


def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS flags (key TEXT PRIMARY KEY, payload TEXT NOT NULL)"
    )
    con.commit()
    con.close()


def upsert_flag(key: str, payload: dict):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO flags(key,payload) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET payload=excluded.payload",
        (key, json.dumps(payload)),
    )
    con.commit()
    con.close()


def get_flag(key: str) -> dict | None:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT payload FROM flags WHERE key=?", (key,))
    row = cur.fetchone()
    con.close()
    if not row:
        return None
    return json.loads(row[0])
