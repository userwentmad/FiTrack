# fix_db.py
import sqlite3
import os

DB_PATH = os.path.join("data", "fitrack.db")  # use the correct path

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Match exactly what your app expects
c.execute(
    """
CREATE TABLE IF NOT EXISTS MessageHistory (
    msg_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date_sent TEXT,
    message_text TEXT,
    trigger_type TEXT
)
"""
)

conn.commit()
conn.close()

print("Table 'MessageHistory' created or already exists!")
