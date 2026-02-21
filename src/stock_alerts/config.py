"""
Stock Alerts Configuration
Centralized API keys from environment variables
"""

import os
from pathlib import Path
from typing import Optional

# PROJECT ROOT (one level above src)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Absolute path to the SQLite DB
DB_FILE = PROJECT_ROOT / "stock_alerts.db"

class Config:
    # API Keys (all from environment variables)
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    TWELVEDATA_API_KEY: str = os.getenv("TWELVEDATA_API_KEY", "")
    EODHD_API_KEY: str = os.getenv("EODHD_API_KEY", "")
    FINNHUB_API_KEY: str = os.getenv("FINNHUB_API_KEY", "")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # Database
    DB_PATH: str = "stock_alerts.db"
    
    # Settings
    CHECK_INTERVAL_MINUTES: int = 5
    PRICE_CHANGE_THRESHOLD: float = 2.0
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required config"""
        required = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
        missing = [key for key in required if not getattr(cls, key)]
        
        if missing:
            print(f"❌ Missing required config: {missing}")
            print("Set these environment variables:")
            print("export TELEGRAM_BOT_TOKEN='your_bot_token'")
            print("export TELEGRAM_CHAT_ID='your_chat_id'")
            return False
        
        return True

# Environment setup helper
def load_config():
    """Load and validate config"""
    if not Config.validate():
        print("⚠️  Fix config before running!")
        exit(1)
    print("✅ Config loaded successfully!")

