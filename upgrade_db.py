import sqlite3
from database import DB_PATH

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Add calories column if not exists
cursor.execute(
    """
ALTER TABLE WorkoutLog
ADD COLUMN calories REAL;
"""
)

conn.commit()
conn.close()

print("WorkoutLog updated: calories column added.")
