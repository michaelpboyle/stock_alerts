"""
Telegram Notifications
"""

import logging
logger = logging.getLogger(__name__)

import requests
from stock_alerts.config import Config

def send_alert(message: str):
    """Send alert to Telegram"""
    logger.info("Sending Telegram alert")

    if not Config.TELEGRAM_BOT_TOKEN or not Config.TELEGRAM_CHAT_ID:
        logger.error("Telegram config missing — cannot send alert")
        return
    
    try:
        url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": Config.TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        logger.info(f"Sending Telegram alert: {message}")
        response = requests.post(url, data=payload)
        
        if response.status_code == 200:
            logger.info("Telegram alert sent successfully")
            return True
        else:
            logger.error(f"Telegram API error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        logger.exception(f"Telegram request failed: {e}")
        return False
