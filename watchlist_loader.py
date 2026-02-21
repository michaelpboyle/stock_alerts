#!/usr/bin/env python3
"""
Bulk Watchlist Loader - Hardcoded symbols → SQLite watchlist table
"""

import sqlite3
from pathlib import Path
import logging

# === LOGGING SETUP ===
LOG_FILE = Path(__file__).resolve().parent / "stock_alerts.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] watchlist_loader: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("watchlist_loader")

# === DB PATH ===
PROJECT_ROOT = Path(__file__).resolve().parent
DB_FILE = PROJECT_ROOT / "stock_alerts.db"

# === HARDCODED WATCHLIST ===
WATCHLIST = [
    ("SLV", 78.0, None),
    ("HOOD", 81.0, None),
    ("CRCL", 67.3, None),
    ("IONQ", 38.0, None),
    ("RBLX", 67.0, None),
]


def init_db():
    """Ensure the watchlist table exists."""
    logger.info(f"Initializing DB at {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS watchlist (
                       symbol TEXT,
                       active INTEGER DEFAULT 1,
                       above REAL,
                       below REAL,
                       created_at DATETIME DEFAULT (datetime('now', 'localtime')),
                       updated_at DATETIME DEFAULT (datetime('now', 'localtime')),
                       PRIMARY KEY (symbol, active))''')

    conn.commit()
    conn.close()
    logger.info("DB initialized successfully")


def load_watchlist_bulk():
    """Bulk insert/replace watchlist with transaction safety."""
    init_db()

    logger.info(f"Loading {len(WATCHLIST)} symbols into {DB_FILE}")

    conn = sqlite3.connect(DB_FILE)
    conn.execute("BEGIN TRANSACTION")

    try:
        logger.info("Deactivating existing active watchlist entries")
        conn.execute("DELETE FROM watchlist WHERE active = 0")
        conn.execute("UPDATE watchlist SET active = 0 WHERE active = 1")

        logger.info("Inserting new watchlist entries")
        conn.executemany("""
            INSERT OR REPLACE INTO watchlist (symbol, above, below)
            VALUES (?, ?, ?)
        """, WATCHLIST)

        conn.commit()
        logger.info("Watchlist loaded successfully")

    except Exception as e:
        conn.rollback()
        logger.exception(f"Error loading watchlist: {e}")
        return False

    finally:
        conn.close()

    # Verification
    conn = sqlite3.connect(DB_FILE)
    count = conn.execute("SELECT COUNT(*) FROM watchlist WHERE active=1").fetchone()[0]
    conn.close()

    logger.info(f"Verified: {count} active symbols in watchlist")
    return True


if __name__ == "__main__":
    if load_watchlist_bulk():
        logger.info("Watchlist ready for market monitoring")
    else:
        logger.error("Watchlist load failed — check DB path and schema")

