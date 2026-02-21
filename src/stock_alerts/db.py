"""
Stock Alerts Database Manager
Handles alerts, and notifications
"""

import logging
logger = logging.getLogger(__name__)

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from contextlib import contextmanager
from datetime import date, datetime   # <-- Needed imports

class DatabaseManager:
    def __init__(self, db_path, data_src):
        self.db_path = Path(db_path)
        self.data_src = data_src
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager for safe DB connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Dict-like rows
            yield conn
        except sqlite3.Error as e:
            print(f"DB Error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def _init_db(self):
        """Create tables if they don't exist"""
        logger.info("Initializing database and ensuring tables exist")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts
                (source TEXT, symbol TEXT, threshold REAL, direction TEXT,
                 alerted_date DATE, alerted_time TEXT, price REAL,
                 PRIMARY KEY(source, symbol, threshold, direction, alerted_date))
            ''')
            
            conn.commit()


    def already_alerted_today(self, source, symbol, threshold, direction):
        logger.info(f"Checking if already alerted today: {source}, {symbol}, {threshold}, {direction}")

        today = date.today().isoformat()

        query = """
            SELECT 1 FROM alerts
            WHERE source=? AND symbol=? AND threshold=? AND direction=? AND alerted_date=?
        """

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (self.data_src, symbol, threshold, direction, today))
            result = cursor.fetchone()
            return result is not None


    def log_alert(self, source, symbol, threshold, direction, price):
        logger.info(f"Logging alert: {source}, {symbol}, {threshold}, {direction}, price={price}")

        today = date.today().isoformat()
        now = datetime.now().strftime("%H:%M:%S")

        query = """
            INSERT OR IGNORE INTO alerts
            (source, symbol, threshold, direction, alerted_date, alerted_time, price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (self.data_src, symbol, threshold, direction, today, now, price))
            conn.commit()

