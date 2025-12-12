import sqlite3
from database import DB_PATH

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT * FROM WorkoutLog ORDER BY date ASC")
rows = cursor.fetchall()

for r in rows:
    print(r)

conn.close()
