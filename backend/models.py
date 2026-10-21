from database import get_db

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL, phone TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE, city TEXT NOT NULL, password TEXT NOT NULL,
    bio TEXT DEFAULT '', skills TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
    title TEXT NOT NULL, category TEXT, description TEXT, price INTEGER, city TEXT,
    kind TEXT DEFAULT 'service'
);
CREATE TABLE IF NOT EXISTS missions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
    title TEXT NOT NULL, description TEXT, budget INTEGER, city TEXT,
    status TEXT DEFAULT 'open', worker_id INTEGER
);
CREATE TABLE IF NOT EXISTS portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
    filename TEXT NOT NULL, kind TEXT NOT NULL, caption TEXT DEFAULT '',
    created TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT, mission_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL, UNIQUE (mission_id, user_id)
);
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT, mission_id INTEGER NOT NULL UNIQUE,
    reviewer_id INTEGER NOT NULL, worker_id INTEGER NOT NULL,
    rating INTEGER NOT NULL, comment TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT, reporter_id INTEGER NOT NULL,
    reported_id INTEGER NOT NULL, reason TEXT NOT NULL,
    created TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT, sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL, content TEXT NOT NULL,
    created TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

def init_db():
    conn = get_db()
    conn.executescript(SCHEMA)
    columns = [r[1] for r in conn.execute("PRAGMA table_info(services)")]
    if "kind" not in columns:  # old database: add the new column
        conn.execute("ALTER TABLE services ADD COLUMN kind TEXT DEFAULT 'service'")
    conn.commit()
    conn.close()