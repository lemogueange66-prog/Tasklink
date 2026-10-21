import os, sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "tasklink.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def query(sql, args=(), one=False, commit=False):
    conn = get_db()
    cur = conn.execute(sql, args)
    if commit:
        conn.commit()
        result = cur.lastrowid
    else:
        rows = [dict(r) for r in cur.fetchall()]
        result = (rows[0] if rows else None) if one else rows
    conn.close()
    return result