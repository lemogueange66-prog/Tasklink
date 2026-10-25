from database import get_db

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL, phone TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE, city TEXT NOT NULL, password TEXT NOT NULL,
    bio TEXT DEFAULT '', skills TEXT DEFAULT '', profile_photo TEXT DEFAULT '',
    lat REAL, lng REAL, location_label TEXT DEFAULT '', share_location INTEGER DEFAULT 0
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
    id INTEGER PRIMARY KEY AUTOINCREMENT, mission_id INTEGER,
    reviewer_id INTEGER NOT NULL, worker_id INTEGER NOT NULL,
    rating INTEGER NOT NULL, comment TEXT DEFAULT '',
    created TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT, reporter_id INTEGER NOT NULL,
    reported_id INTEGER NOT NULL, reason TEXT NOT NULL,
    created TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT, sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL, content TEXT NOT NULL,
    created TEXT DEFAULT CURRENT_TIMESTAMP, is_read INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_services_user ON services(user_id);
CREATE INDEX IF NOT EXISTS idx_missions_user ON missions(user_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_user ON portfolio(user_id);
CREATE INDEX IF NOT EXISTS idx_reviews_worker ON reviews(worker_id);
CREATE INDEX IF NOT EXISTS idx_messages_users ON messages(sender_id, receiver_id);
"""

# Created after the upgrades below, because an old database must be rebuilt first.
# A mission review is unique per mission; a direct review is unique per (reviewer, provider).
LATE_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_reviews_worker ON reviews(worker_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_reviews_mission ON reviews(mission_id) WHERE mission_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_reviews_direct ON reviews(reviewer_id, worker_id) WHERE mission_id IS NULL;
CREATE INDEX IF NOT EXISTS idx_messages_unread ON messages(receiver_id, is_read);
"""

# Columns added after the first version: (table, column, definition)
UPGRADES = [
    ("users", "profile_photo", "TEXT DEFAULT ''"),
    ("services", "kind", "TEXT DEFAULT 'service'"),
    ("users", "lat", "REAL"),
    ("users", "lng", "REAL"),
    ("users", "location_label", "TEXT DEFAULT ''"),
    ("users", "share_location", "INTEGER DEFAULT 0"),
    ("messages", "is_read", "INTEGER DEFAULT 0"),
]


def upgrade_reviews(conn):
    """Old databases: reviews.mission_id was NOT NULL + UNIQUE, so a review could only follow a mission.
    Rebuild the table so a client can also review a provider directly (data is kept)."""
    cols = {r[1]: r for r in conn.execute("PRAGMA table_info(reviews)")}
    if "created" in cols and not cols["mission_id"][3]:
        return
    conn.executescript("""
        DROP TABLE IF EXISTS reviews_new;
        CREATE TABLE reviews_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT, mission_id INTEGER,
            reviewer_id INTEGER NOT NULL, worker_id INTEGER NOT NULL,
            rating INTEGER NOT NULL, comment TEXT DEFAULT '',
            created TEXT DEFAULT CURRENT_TIMESTAMP
        );
        INSERT INTO reviews_new (id, mission_id, reviewer_id, worker_id, rating, comment)
            SELECT id, mission_id, reviewer_id, worker_id, rating, comment FROM reviews;
        DROP TABLE reviews;
        ALTER TABLE reviews_new RENAME TO reviews;
    """)


def init_db():
    """Create missing tables and add missing columns to an older database."""
    conn = get_db()
    try:
        conn.executescript(SCHEMA)
        for table, column, definition in UPGRADES:
            existing = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]
            if column not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
                if (table, column) == ("messages", "is_read"):      # old messages count as already read
                    conn.execute("UPDATE messages SET is_read=1")
        upgrade_reviews(conn)
        conn.executescript(LATE_INDEXES)
        conn.commit()
    finally:
        conn.close()
