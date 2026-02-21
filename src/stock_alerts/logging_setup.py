import logging.config
from pathlib import Path

def setup_logging():
    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    LOG_DIR = PROJECT_ROOT / "logs"
    LOG_DIR.mkdir(exist_ok=True)

    LOG_FILE = LOG_DIR / "stock_alerts.log"
    CONFIG_FILE = PROJECT_ROOT / "logging.ini"

    logging.config.fileConfig(
        CONFIG_FILE,
        defaults={"log_file": str(LOG_FILE)},
        disable_existing_loggers=False
    )

