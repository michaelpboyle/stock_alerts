"""
Price Data Sources
yfinance, 12Data, Finnhub, Alpha Vantage, EODHD
"""

import logging
logger = logging.getLogger(__name__)
## logger = logging.getLogger("data_sources")

import time
import requests
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from typing import Optional
from stock_alerts.config import Config


# -----------------------------
# YAHOO FINANCE
# -----------------------------
def get_current_price_YF(symbol: str) -> Optional[float]:
    logger.info(f"[YF] Fetching price for {symbol}")

    for attempt in range(3):
        try:
            ticker = yf.Ticker(symbol)

            # Step 1: Market state
            market_state = None
            try:
                info = ticker.info
                market_state = info.get("marketState", None)
                logger.info(f"[YF] market_state={market_state}")
            except Exception:
                info = {}
                logger.warning(f"[YF] Could not read .info for {symbol}")

            # Step 2: fast_info (only when market active)
            if market_state in ("REGULAR", "PRE", "POST"):
                try:
                    fi = ticker.fast_info
                    price = fi.get("last_price")
                    if price is not None:
                        logger.info(f"[YF] Used fast_info last_price for {symbol}")
                        return float(price)
                except Exception:
                    logger.warning(f"[YF] fast_info failed for {symbol}")

            # Step 3: .info fallback
            try:
                if info:
                    if "regularMarketPrice" in info:
                        logger.info(f"[YF] Used info regularMarketPrice for {symbol}")
                        return float(info["regularMarketPrice"])
                    if "currentPrice" in info:
                        logger.info(f"[YF] Used info currentPrice for {symbol}")
                        return float(info["currentPrice"])
            except Exception:
                logger.warning(f"[YF] .info fallback failed for {symbol}")

            # Step 4: history() fallback
            try:
                hist = ticker.history(period="1d", interval="1m")
                if not hist.empty:
                    logger.info(f"[YF] Used history 1m Close for {symbol}")
                    return float(hist["Close"].iloc[-1])
            except Exception:
                logger.warning(f"[YF] history() failed for {symbol}")

        except Exception as e:
            logger.error(f"[YF] Exception for {symbol}: {e}")
            time.sleep(1)

    logger.error(f"[YF] Could not retrieve price for {symbol}")
    return None


# -----------------------------
# FINNHUB
# -----------------------------
def get_current_price_finnhub(symbol: str) -> Optional[float]:
    logger.info(f"[Finnhub] Fetching price for {symbol}")

    api_key = Config.FINNHUB_API_KEY
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        price = data.get("c")
        if isinstance(price, (int, float)) and price > 0:
            logger.info(f"[Finnhub] Price={price} for {symbol}")
            return float(price)

        logger.warning(f"[Finnhub] No usable price in response for {symbol}")
        return None

    except Exception as e:
        logger.error(f"[Finnhub] Exception for {symbol}: {e}")
        return None


# -----------------------------
# 12DATA
# -----------------------------
def get_current_price_12data(symbol: str) -> Optional[float]:
    logger.info(f"[12Data] Fetching price for {symbol}")

    api_key = Config.TWELVEDATA_API_KEY
    url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={api_key}"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        price = data.get("price")
        if isinstance(price, (int, float, str)):
            try:
                price_f = float(price)
                logger.info(f"[12Data] Price={price_f} for {symbol}")
                return price_f
            except ValueError:
                pass

        logger.warning(f"[12Data] No usable price in response for {symbol}")
        return None

    except Exception as e:
        logger.error(f"[12Data] Exception for {symbol}: {e}")
        return None


# -----------------------------
# EODHD
# -----------------------------
def get_current_price_EODHD(symbol):
    logger.info(f"[EODHD] Fetching price for {symbol}")

    api_key = Config.EODHD_API_KEY
    url = f"https://eodhd.com/api/real-time/{symbol}?api_token={api_key}&fmt=json"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if isinstance(data, dict) and 'close' in data:
            price = float(data['close'])
            logger.info(f"[EODHD] Price={price} for {symbol}")
            return price

        if isinstance(data, list) and len(data) > 0 and 'close' in data[0]:
            price = float(data[0]['close'])
            logger.info(f"[EODHD] Price={price} for {symbol}")
            return price

        logger.warning(f"[EODHD] No usable price in response for {symbol}")

    except Exception as e:
        logger.error(f"[EODHD] Exception for {symbol}: {e}")

    return None


# -----------------------------
# ALPHA VANTAGE
# -----------------------------
def get_current_price_AV(symbol: str) -> Optional[float]:
    logger.info(f"[AV] Fetching price for {symbol}")

    api_key = Config.ALPHA_VANTAGE_API_KEY
    ts = TimeSeries(key=api_key, output_format='pandas')

    try:
        data, meta = ts.get_quote_endpoint(symbol)
        if not data.empty:
            price = float(data["05. price"].iloc[0])
            logger.info(f"[AV] Price={price} for {symbol}")
            return price

        logger.warning(f"[AV] Empty response for {symbol}")

    except Exception as e:
        logger.error(f"[AV] Exception for {symbol}: {e}")

    return None

