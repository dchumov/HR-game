import sqlite3
import json

DB_PATH = "game.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS players (
            user_id     INTEGER PRIMARY KEY,
            scene       TEXT    DEFAULT 'ep1_intro',
            logic       INTEGER DEFAULT 0,
            empathy     INTEGER DEFAULT 0,
            authority   INTEGER DEFAULT 0,
            crystals    INTEGER DEFAULT 30,
            flags       TEXT    DEFAULT '[]'
        )
    """)
    conn.commit()
    conn.close()


def _row_to_dict(row):
    if not row:
        return None
    return {
        "user_id":   row[0],
        "scene":     row[1],
        "logic":     row[2],
        "empathy":   row[3],
        "authority": row[4],
        "crystals":  row[5],
        "flags":     json.loads(row[6]),
    }


def get_player(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return _row_to_dict(row)


def create_player(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO players (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()
    return get_player(user_id)


def update_player(user_id: int, **kwargs):
    if "flags" in kwargs and isinstance(kwargs["flags"], list):
        kwargs["flags"] = json.dumps(kwargs["flags"])
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [user_id]
    c.execute(f"UPDATE players SET {sets} WHERE user_id=?", vals)
    conn.commit()
    conn.close()


def reset_player(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE players
        SET scene='ep1_intro', logic=0, empathy=0, authority=0, crystals=30, flags='[]'
        WHERE user_id=?
    """, (user_id,))
    conn.commit()
    conn.close()
    return get_player(user_id)
