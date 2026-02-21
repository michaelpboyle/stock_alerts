#!/usr/bin/env python3
"""
Stock Alerts Main Engine
Checks prices and sends notifications
"""

import sys
import time
from datetime import datetime
import logging

from stock_alerts.logging_setup import setup_logging
from stock_alerts.telegram import send_alert
from stock_alerts.db import DatabaseManager
from stock_alerts.config import load_config, DB_FILE
from stock_alerts import data_sources, watchlist

logger = logging.getLogger(__name__)


def check_alerts(DATA_SRC, WATCH_LIST, db, get_price_func):
    load_config()

    logger.info(f"{DATA_SRC.upper()} + Telegram + SQLite Alerts - {datetime.now().strftime('%H:%M:%S')}")

    alerts_triggered = 0

    for item in WATCH_LIST:
        sym = item["symbol"]
        above = item.get("above")
        below = item.get("below")

        price = get_price_func(sym)
        time.sleep(5)

        if price is None:
            logger.warning(f"Could not retrieve price for {sym}")
            continue

        logger.info(f"Checking {sym} price: {price}")

        # ABOVE
        if above is not None and price >= above:
            if db.already_alerted_today(DATA_SRC, sym, above, "above"):
                logger.info(f"{sym}: already alerted today (above)")
            else:
                msg = f"🚨 {DATA_SRC.upper()}: *{sym} ABOVE*\n💰 ${price:.2f}\n📈 > ${above:.2f}"
                if send_alert(msg):
                    db.log_alert(DATA_SRC, sym, above, "above", price)
                    alerts_triggered += 1

        # BELOW
        if below is not None and price <= below:
            if db.already_alerted_today(DATA_SRC, sym, below, "below"):
                logger.info(f"{sym}: already alerted today (below)")
            else:
                msg = f"🚨 {DATA_SRC.upper()}: *{sym} BELOW*\n💰 ${price:.2f}\n📉 < ${below:.2f}"
                if send_alert(msg):
                    db.log_alert(DATA_SRC, sym, below, "below", price)
                    alerts_triggered += 1

    logger.info(f"Complete. {alerts_triggered} new alerts sent.")


def main():
    setup_logging()

    # Parse data source argument
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python main.py <data_source>")

    DATA_SRC = sys.argv[1]

    # Initialize DB
    db = DatabaseManager(db_path=DB_FILE, data_src=DATA_SRC)

    # Select price function dynamically
    func_name = f"get_current_price_{DATA_SRC}"
    get_price_func = getattr(data_sources, func_name)

    # Load watchlist
    WATCH_LIST = watchlist.load_watchlist(DB_FILE)

    logger.info("")
    logger.info("📋 Loaded %d active symbols:", len(WATCH_LIST))

    for item in WATCH_LIST:
        symbol = item["symbol"]
        above = item.get("above")
        below = item.get("below")
        logger.info("  %s: above=$%s, below=%s", symbol, above, below)

    logger.info("")

    # Run alerts
    check_alerts(DATA_SRC, WATCH_LIST, db, get_price_func)


if __name__ == "__main__":
    main()

