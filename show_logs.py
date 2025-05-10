import sqlite3
import sys

DB_PATH = sys.argv[1] if len(sys.argv) > 1 else "devopy_logs.sqlite3"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT id, timestamp, level, message, error FROM logs ORDER BY id DESC LIMIT 20;")
for row in c.fetchall():
    print(f"[{row[0]}] {row[1]} | {row[2]} | {row[3]} | {row[4]}")
conn.close()
