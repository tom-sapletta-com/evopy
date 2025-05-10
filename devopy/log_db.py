import sqlite3
import threading
import time
from datetime import datetime

DB_PATH = "devopy_logs.sqlite3"

class LogDB:
    _lock = threading.Lock()

    @staticmethod
    def init_db():
        with LogDB._lock:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                source TEXT,
                level TEXT,
                message TEXT,
                request TEXT,
                response TEXT,
                error TEXT
            )''')
            conn.commit()
            conn.close()

    @staticmethod
    def log(source, level, message, request=None, response=None, error=None):
        with LogDB._lock:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('''INSERT INTO logs (timestamp, source, level, message, request, response, error)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (datetime.utcnow().isoformat(), source, level, message, request, response, error))
            conn.commit()
            conn.close()

    @staticmethod
    def fetch_recent(limit=100):
        with LogDB._lock:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('SELECT * FROM logs ORDER BY id DESC LIMIT ?', (limit,))
            rows = c.fetchall()
            conn.close()
            return rows

# Inicjalizacja bazy przy imporcie
LogDB.init_db()
