#!/bin/bash
# StockAlerts.bash - Universal launcher for Desktop/Pi

if [ -z "$1" ]; then
    echo "Usage: $0 <source>"
    exit 1
fi
SRC="$1"
case "$SRC" in
    finnhub|12data|YF|AV|EODHD)
        echo "SRC = $SRC"
        ;;
    *)
        echo "❌ Unknown source: $SRC"
        echo "Valid sources: finnhub, 12data, yf, av, eodhd"
        exit 1
        ;;
esac

set -e  # Exit on any error
echo "🚀 Stock Alerts Launcher - $(date)"

HOSTNAME_NOW="$(hostname)"

# Adjust these to your actual hostnames
case "$HOSTNAME_NOW" in
    raspberrypi)
        PLATFORM="pi"
        echo "✅ Detected Raspberry Pi (hostname: $HOSTNAME_NOW)"
        PYTHON_CMD="PYTHON_CMD="/home/michaelpb/.venvs/stock_alerts_env/bin/python3"
        SCRIPT_PATH="/home/michaelpb/stock_alerts/main.py"
        LOG_PATH="/home/michaelpb/stock_alerts/StockAlerts.log"
        export PYTHONPATH="/home/michaelpb/stock_alerts/src"
        ;;
    *)  ## michael-HP-ENVY-Laptop-17-ch0xxx
        PLATFORM="desktop"
        echo "✅ Detected Desktop (hostname: $HOSTNAME_NOW)"
        PYTHON_CMD="/home/michael/anaconda3/envs/stock_alerts-env/bin/python3"
        SCRIPT_PATH="/home/michael/PythonAnacProjects/stock_alerts/main.py"
        LOG_PATH="/home/michael/PythonAnacProjects/stock_alerts/StockAlerts.log"
        export PYTHONPATH="/home/michael/PythonAnacProjects/stock_alerts/src"
        ;;
esac


# Verify script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Python script not found: $SCRIPT_PATH"
    exit 1
fi

# Verify Python exists (best-effort)
if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
    echo "❌ Python not found: $PYTHON_CMD"
    exit 1
fi

# Set your credentials
stock_alerts_config() {
    export TELEGRAM_BOT_TOKEN="PUT_YOUR_TOKEN_HERE"
    export TELEGRAM_CHAT_ID="PUT_CHAT_ID_HERE"
    export TWELVEDATA_API_KEY="PUT_YOUR_API_KEY_HERE"
    export ALPHA_VANTAGE_API_KEY="PUT_YOUR_API_KEY_HERE"
    export EODHD_API_KEY="PUT_YOUR_API_KEY_HERE"
    export FINNHUB_API_KEY="PUT_YOUR_API_KEY_HERE"
}
stock_alerts_config  # <- UNcomment this line to activate

echo "📱 Running $PLATFORM script: $SCRIPT_PATH"
echo "🐍 Using Python: $PYTHON_CMD"

cd "$(dirname "$SCRIPT_PATH")"
echo "----- $(date) -----" >> "$LOG_PATH"
echo "" >> "$LOG_PATH"
"$PYTHON_CMD" "$SCRIPT_PATH" "$SRC" >> "$LOG_PATH" 2>&1

echo "Launcher finished at $(date)" >> "$LOG_PATH"

