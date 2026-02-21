#!/usr/bin/env python3
import sqlite3
from typing import List, Dict, Optional, Any
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

def load_watchlist(db_file: str) -> List[Dict[str, Any]]:
    """Load active symbols/thresholds from SQLite watchlist table."""
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("""
        SELECT symbol, above, below, active, created_at, updated_at 
        FROM watchlist 
        WHERE active=1
    """)
    rows = c.fetchall()
    conn.close()
    
    watchlist = []
    for row in rows:
        watchlist.append({
            "symbol": row[0],
            "above": row[1],
            "below": row[2],
            "active": row[3],
            "created_at": row[4],
            "updated_at": row[5]
        })
    return watchlist

def print_watchlist_summary(watchlist: List[Dict[str, Any]]):
    print(f"📋 Loaded {len(watchlist)} active symbols:")
    for item in watchlist:
        above_str = f"${item['above']:.1f}" if item['above'] else "None"
        below_str = f"${item['below']:.1f}" if item['below'] else "None"
        print(f"  {item['symbol']}: above={above_str}, below={below_str}")

